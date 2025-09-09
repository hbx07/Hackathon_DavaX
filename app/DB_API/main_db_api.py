from db_api import DB_API_connect_to_db, DB_API_check_user


def main():
    db_file = "DB\\payments.db"
    conn = DB_API_connect_to_db(db_file)

    if conn:
#        test_cnp = "1981234567890"  # Negative test
        test_cnp = "1960101223344"  # Positive test
        try:
#            cur = conn.cursor()
#            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
#            tables = cur.fetchall()
#            print("Tables:", tables)            
            result = DB_API_check_user(conn, test_cnp)
            if result == 1:
                print(f"CNP {test_cnp} exists in Payer table.")
            else:
                print(f"CNP {test_cnp} does not exist in Payer table.")
        except ValueError as e:
            print(f"Error: {e}")

        conn.close()


if __name__ == "__main__":
    main()

