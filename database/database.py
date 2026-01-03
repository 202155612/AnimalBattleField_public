import psycopg2
from psycopg2 import errorcodes
from flask import session
import config
from config import (
    DB,
    HOST,
    PORT,
    REGISTER_USER,
    REGISTER_PASSWORD,
    GUEST_USER,
    GUEST_PASSWORD
)
from utils.error_printer import print_error_message

class DatabaseAuthError(Exception):
    pass

def access():
    try:
        db_user = session.get("username", GUEST_USER)
        db_pass = session.get("password", GUEST_PASSWORD)

        conn = psycopg2.connect(
            database=DB,
            user=db_user, 
            password=db_pass,
            host=HOST,
            port=PORT
        )
        return conn
    except psycopg2.Error as e:
        print_error_message(e)
        raise e
    
def auth_access():
    try:
        conn = psycopg2.connect(
            database=DB,
            user=REGISTER_USER, 
            password=REGISTER_PASSWORD,
            host=HOST,
            port=PORT
        )
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, current_database()")
            print("DB user, DB:", cur.fetchone())
        print("register conn 완료")
        return conn
    except psycopg2.Error as e:
        print_error_message(e)
        raise e
    
def login(username: str, password: str) -> bool:
    try:
        conn = psycopg2.connect(
            database=DB,
            user=username, 
            password=password,
            host=HOST,
            port=PORT,
        )
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM login_data WHERE username = %s;", (username,))
            user_id = cur.fetchone()
            if not user_id:
                raise DatabaseAuthError("DB 로그인에 성공했으나, 사용자 정보를 불러올 수 없습니다.")
        session["username"] = username
        session["password"] = password
        session["user_ID"] = user_id[0]
        conn.close()
    except psycopg2.Error as e:
        session.pop("username", None)
        session.pop("password", None)
        session.pop("user_ID", None)
        print_error_message(e)
        if "password authentication failed" in str(e):
            raise DatabaseAuthError(f"사용자 이름 또는 비밀번호가 틀렸습니다.") from e
        raise e
    return True



def logout():
    session.pop("username", None)
    session.pop("password", None)
    session.pop("user_ID", None)
    session.clear()
