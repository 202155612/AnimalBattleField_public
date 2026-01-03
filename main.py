import os
import threading
import webbrowser
import getpass
import secrets

from flask import Flask
from flask_session import Session

import psycopg2
from psycopg2 import sql, errors


def prompt_with_default(prompt, default):
    s = input(f"{prompt} ({default}): ").strip()
    return s if s else default

def ensure_login_roles(cur, guest_user, guest_password, register_user, register_password):
    def create_login(role_name, role_password):
        cur.execute(
            sql.SQL(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = {role_literal}) THEN
                        CREATE ROLE {role_identifier} LOGIN PASSWORD {role_password};
                    END IF;
                END
                $$;
                """
            ).format(
                role_literal=sql.Literal(role_name),
                role_identifier=sql.Identifier(role_name),
                role_password=sql.Literal(role_password),
            )
        )

    def grant_guest(role_name):
        cur.execute(
            sql.SQL("GRANT guest TO {role};").format(role=sql.Identifier(role_name))
        )

    def grant_register_privileges(role_name):
        cur.execute(
            sql.SQL("GRANT INSERT ON Accounts TO {role};").format(
                role=sql.Identifier(role_name)
            )
        )
        cur.execute(
            sql.SQL("GRANT UPDATE ON Accounts TO {role};").format(
                role=sql.Identifier(role_name)
            )
        )
        cur.execute(
            sql.SQL("GRANT SELECT ON Accounts TO {role};").format(
                role=sql.Identifier(role_name)
            )
        )

    create_login(guest_user, guest_password)
    create_login(register_user, register_password)
    grant_guest(guest_user)
    grant_guest(register_user)
    grant_register_privileges(register_user)


def initialize_database(
    host,
    port,
    admin_user,
    admin_password,
    db_name,
    guest_user,
    guest_password,
    register_user,
    register_password,
):
    sql_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "initial_SQL")

    sql_files = [
        "initial_table.sql",
        "initial_role.sql",
        "initial_data.sql",
        "initial_view.sql",
        "initial_view_role.sql",
    ]

    conn = None
    try:
        print(f"\n새 DB '{db_name}'에 접속해서 초기 SQL 스크립트를 실행합니다.\n")
        conn = psycopg2.connect(
            dbname=db_name,
            user=admin_user,
            password=admin_password,
            host=host,
            port=port,
        )
        conn.autocommit = True
        cur = conn.cursor()

        for filename in sql_files:
            path = os.path.join(sql_dir, filename)
            if not os.path.exists(path):
                print(f"경고: {path} 파일이 존재하지 않아 건너뜁니다.")
                continue

            print(f"{filename} 실행 중...")
            with open(path, "r", encoding="utf-8") as f:
                sql_text = f.read()
            cur.execute(sql_text)
            print(f"{filename} 실행 완료.")

        ensure_login_roles(
            cur,
            guest_user=guest_user,
            guest_password=guest_password,
            register_user=register_user,
            register_password=register_password,
        )

        print("\n초기 SQL 스크립트 실행을 모두 완료했습니다.\n")

    finally:
        if conn is not None:
            conn.close()


def create_database(
    host,
    port,
    admin_user,
    admin_password,
    base_db,
    new_db,
    guest_user,
    guest_password,
    register_user,
    register_password,
):
    print(f"\n기존 DB '{base_db}'에 접속해서 새 DB '{new_db}'를 생성합니다.\n")
    conn = None
    created = False

    try:
        conn = psycopg2.connect(
            dbname=base_db,
            user=admin_user,
            password=admin_password,
            host=host,
            port=port,
        )
        conn.autocommit = True
        cur = conn.cursor()

        try:
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_db))
            )
            created = True
            print(f"데이터베이스 '{new_db}' 생성 완료.\n")
        except errors.DuplicateDatabase:
            print(f"데이터베이스 '{new_db}'가 이미 존재합니다.\n")
            raise

        try:
            initialize_database(
                host=host,
                port=port,
                admin_user=admin_user,
                admin_password=admin_password,
                db_name=new_db,
                guest_user=guest_user,
                guest_password=guest_password,
                register_user=register_user,
                register_password=register_password,
            )
        except Exception as e:
            print(f"초기 SQL 스크립트 실행 중 오류 발생: {e}\n")
            if created:
                print(f"초기화 실패로 인해 DB '{new_db}'를 삭제합니다.\n")
                cur.execute(
                    sql.SQL("DROP DATABASE {}").format(sql.Identifier(new_db))
                )
                print(f"DB '{new_db}' 삭제 완료.\n")
            raise

    except Exception as e:
        print(f"데이터베이스 생성/초기화 중 오류 발생: {e}\n")
        raise

    finally:
        if conn is not None:
            conn.close()


def ensure_config_file():
    if not os.path.exists("config.py"):
        print("\nconfig.py 파일이 없습니다. 생성을 시작합니다.\n")

        HOST = prompt_with_default("데이터베이스 호스트", "localhost")
        PORT = prompt_with_default("데이터베이스 포트", "5432")
        guest_user = prompt_with_default("게스트 계정 사용자명", "guestuser")
        guest_password = getpass.getpass("게스트 계정 비밀번호 (guestPassword): ").strip()
        guest_password = guest_password if guest_password else "guestPassword"

        register_user = prompt_with_default("회원가입 계정 사용자명", "registeruser")
        register_password = getpass.getpass("회원가입 계정 비밀번호 (registerpassword): ").strip()
        register_password = register_password if register_password else "registerpassword"
        ADMIN_USER = prompt_with_default("데이터베이스 슈퍼 유저명", "postgres")
        ADMIN_PASSWORD = getpass.getpass("데이터베이스 비밀번호: ").strip()
        APP_DB = prompt_with_default(
            "새로 생성할 애플리케이션 데이터베이스 이름", "animal_battlefield"
        )
        BASE_DB = prompt_with_default("기존 데이터베이스 이름", "postgres")

        create_database(
            host=HOST,
            port=PORT,
            admin_user=ADMIN_USER,
            admin_password=ADMIN_PASSWORD,
            base_db=BASE_DB,
            new_db=APP_DB,
            guest_user=guest_user,
            guest_password=guest_password,
            register_user=register_user,
            register_password=register_password,
        )
        
        secret_key = getpass.getpass(
            "플라스크 SECRET_KEY (미입력 시 자동 생성): "
        ).strip()
        secret_key = secret_key if secret_key else secrets.token_hex(24)

        default_config = f'''
DB = "{APP_DB}"
PORT = "{PORT}"
HOST = "{HOST}"
ADMIN_USER = "{ADMIN_USER}"
ADMIN_PASSWORD = "{ADMIN_PASSWORD}"

GUEST_USER = "{guest_user}"
GUEST_PASSWORD = "{guest_password}"
REGISTER_USER = "{register_user}"
REGISTER_PASSWORD = "{register_password}"
SECRET_KEY = "{secret_key}"
'''

        with open("config.py", "w", encoding="utf-8") as f:
            f.write(default_config)

        print("\nconfig.py 생성 완료.\n")


def create_app():
    import config

    from views.home_view import bp as home_bp
    from views.auth_view import bp as auth_bp
    from views.account_view import bp as account_bp
    from views.card_list_view import bp as card_list_bp
    from views.deck_list_view import bp as deck_list_bp
    from views.deck_view import bp as deck_bp
    from views.battle_view import bp as battle_bp
    from views.card_patch_view import bp as card_patch_bp
    from views.replay_view import bp as replay_bp
    from views.replay_list_view import bp as replay_list_bp
    from views.admin_view import bp as admin_bp
    from views.card_stat_list_view import bp as card_stat_list_bp
    from views.card_stat_view import bp as card_stat_bp

    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    Session(app)

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(card_list_bp)
    app.register_blueprint(deck_list_bp)
    app.register_blueprint(deck_bp)
    app.register_blueprint(card_patch_bp)
    app.register_blueprint(battle_bp)
    app.register_blueprint(replay_bp)
    app.register_blueprint(replay_list_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(card_stat_list_bp)
    app.register_blueprint(card_stat_bp)

    return app


def main():
    try:
        ensure_config_file()
        app = create_app()
        threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
        app.run(debug=False, use_reloader=False)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
