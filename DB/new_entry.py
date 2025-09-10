import sqlite3
from db_api import DB_API_add_payee


def DB_API_connect_to_db(db_path: str) -> sqlite3.Connection:
    """
    Connects to an existing SQLite database.

    Parameters:
        db_path (str): Path to the SQLite database file (e.g. "payments.db").

    Returns:
        sqlite3.Connection: The database connection object.
    """
    try:
        conn = sqlite3.connect(db_path)
        print(f"Connected to database: {db_path}")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection failed: {e}")
        return None


def export_payee_table(conn: sqlite3.Connection, file_path: str = "payee_export.txt") -> None:
    """
    Export the entire Payee table into a text file.

    Parameters:
        conn (sqlite3.Connection): Active SQLite connection
        file_path (str): Path to the output text file
    """
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Payee;")
        rows = cur.fetchall()

        col_names = [desc[0] for desc in cur.description]

        with open(file_path, "w", encoding="utf-8") as f:
            # Write header
            f.write("\t".join(col_names) + "\n")
            # Write rows
            for row in rows:
                f.write("\t".join(str(val) if val is not None else "" for val in row) + "\n")

        print(f"Payee table exported to {file_path}")

    except Exception as e:
        print(f"Failed to export Payee table: {e}")


# --- Main flow ---
#--- new entry into DB ---
conn = DB_API_connect_to_db("payments.db")

try:
    new_id = DB_API_add_payee(
        conn=conn,
        cnp="1960101223344",           # must exist in Payer
        amount=999.50,
        currency="RON",
        dt_str="2025-09-09 10:15:00",
        status="PENDING",
        receiver="SC Exemplu SRL",
        invoice_nr="INV-2008",
    )
    print("Inserted Payee.ID =", new_id)

    # Export Payee table after insertion
    export_payee_table(conn, "C:\Endava\EndevLocal\Hackathon_DavaX\Hackathon_DavaX\database\payee_export.txt")

except ValueError as err:
    print("Error:", err)
finally:
    if conn:
        conn.close()
