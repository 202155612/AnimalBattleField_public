def print_error_message(error: Exception):
    import psycopg2
    print("=== psycopg2 오류 발생 ===")
    if isinstance(error, psycopg2.Error):
        print("type:", type(error))
        print("pgcode:", error.pgcode)
        print("diag.sqlstate:", getattr(error.diag, "sqlstate", None))
        print("diag.message_primary:", getattr(error.diag, "message_primary", None))
    print("raw message:", str(error))