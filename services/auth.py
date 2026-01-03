import re
from database import database as db
from utils.validators import validate_username, validate_password, validate_nickname
from psycopg2 import sql, errors
import psycopg2
from utils.error_printer import print_error_message
import traceback
from models.models import Account
from typing import Callable

def login(username, password):
    try:
        db.login(username, password)
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                pass
                #cur.execute("SELECT * FROM Accounts WHERE username = %s", (username,))
        return True
    except db.DatabaseAuthError:
        raise
    except Exception:
        raise

def register(username, password, nickname) -> bool:
    if not username:
        raise ValueError("사용자 이름을 입력해 주세요.")
    if not password:
        raise ValueError("비밀번호를 입력해 주세요.")
    if not nickname:
        raise ValueError("닉네임을 입력해 주세요.")
    if not validate_username(username):
        raise ValueError("사용자 이름 형식이 올바르지 않습니다.")
    if not validate_password(password):
        raise ValueError("비밀번호 형식이 올바르지 않습니다.")
    if not validate_nickname(nickname):
        raise ValueError("닉네임 형식이 올바르지 않습니다.")
    try:
        conn = db.auth_access()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM Accounts WHERE username = %s", (username,))
                if cur.fetchone():
                    return False
                cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", ("player",))
                if cur.fetchone() is None:
                    raise ValueError("player 역할이 데이터베이스에 존재하지 않습니다.")
                cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
                exists = cur.fetchone()
                if not exists:
                    cur.execute(
                        sql.SQL("CREATE USER {} WITH PASSWORD %s")
                        .format(sql.Identifier(username)),
                        (password,)
                    )
                else:
                    return False
                cur.execute(
                    sql.SQL('GRANT player TO {}')
                    .format(sql.Identifier(username))
                )
                cur.execute(
                    """
                    INSERT INTO Accounts (username, nickname, created_at)
                    VALUES (%s, %s, NOW())
                    RETURNING user_ID
                    """,
                    (username, nickname)
                )
                new_user_id = cur.fetchone()[0]
        return True
    except errors.UniqueViolation:
        raise ValueError("이미 존재하는 사용자입니다.")
    except psycopg2.Error as e:
        print_error_message(e)
        traceback.print_exc()
        raise e
    except Exception:
        raise

def get_user_info():
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT username, nickname, created_at
                    FROM account_data
                    WHERE username = %s
                    """,
                    (db.session.get("username"),)
                )
                user_info = cur.fetchone()
                if user_info is None:
                    return None
                cur.execute("""
                    SELECT r.rolname
                    FROM pg_roles r
                    JOIN pg_auth_members m ON r.oid = m.roleid
                    JOIN pg_roles u ON u.oid = m.member
                    WHERE u.rolname = %s;
                """, (db.session.get("username"),))
                roles = cur.fetchall()
                if user_info is None:
                    return None
                print([r[0] for r in roles])

                return Account(
                    user_info[0],
                    user_info[1],
                    user_info[2],
                    [r[0] for r in roles]
                )

    except Exception:
        raise

def get_users_list(search_username: str, search_nickname: str,
                   key: Callable[[Account], int | tuple] = lambda x: x.created_at, in_reverse:bool = False):
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        a.user_ID,
                        a.username,
                        a.nickname,
                        a.created_at,
                        r.rolname AS user_role
                    FROM Accounts a
                    LEFT JOIN pg_roles u ON u.rolname = a.username
                    LEFT JOIN pg_auth_members m ON m.member = u.oid
                    LEFT JOIN pg_roles r ON r.oid = m.roleid
                    WHERE a.username LIKE %s
                        AND a.nickname LIKE %s
                    ORDER BY a.user_ID;
                    """, (f"%{search_username or ''}%",
                          f"%{search_nickname or ''}%")
                )
                rows = cur.fetchall()
                if rows is None:
                    raise ValueError("user_info가 None을 반환햇습니다. 이럴 리가 없는데?")

                accounts: dict[int, Account] = {}
                for row in rows:
                    user_ID, username, nickname, created_at, user_role = row
                    if user_ID not in accounts:
                        accounts[user_ID] = Account(
                            username = username, 
                            nickname = nickname,
                            created_at = created_at,
                            role = []
                        )
                        
                    accounts[user_ID].role.append(user_role)
                if key == None:
                    return reversed(accounts.values()) if not in_reverse else accounts.values()
                return sorted(accounts.values(), key=key, reverse=in_reverse)

    except Exception:
        raise

def update_nickname(username: str, new_nickname:str):
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE Accounts
                    SET nickname = %s
                    WHERE username = %s 
                    """, (new_nickname, username)
                )
    except Exception:
        raise