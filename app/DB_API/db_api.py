import sqlite3


def DB_API_check_user(conn: sqlite3.Connection, cnp: str) -> int:
    """
    Check if a user with the given CNP exists in the USER table.

    Parameters:
        conn (sqlite3.Connection): Active SQLite connection object
        cnp (str): CNP string (13 characters long)

    Returns:
        int: 1 if the user exists, 0 if the user does not exist
    Raises:
        ValueError: if the CNP is invalid or a database error occurs
    """
    try:
        # Validate CNP format
        if not (cnp.isdigit() and len(cnp) == 13):
            raise ValueError("Invalid CNP: must be a 13-digit numeric string.")

        cur = conn.cursor()
        cur.execute("SELECT 1 FROM Payer WHERE CNP = ? LIMIT 1;", (cnp,))
        result = cur.fetchone()

        if result:
            return 1  # Exists
        else:
            return 0  # Does not exist

    except sqlite3.Error as e:
        # Database-specific error
        raise ValueError(f"Database error: {e}")
    except Exception as e:
        # Any other unexpected error
        raise ValueError(f"Unexpected error: {e}")


def DB_API_connect_to_db(db_path: str) -> sqlite3.Connection:
    """
    Connects to an existing SQLite database.
    
    Parameters:
        db_path (str): Path to the SQLite database file (e.g. "payments.db").
    
    Returns:
        sqlite3.Connection: The database connection object.
    """
    try:
        # Establish connection to the database
        conn = sqlite3.connect(db_path)
        print(f"Connected to database: {db_path}")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection failed: {e}")
        return None
    
