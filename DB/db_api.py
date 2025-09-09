import sqlite3
from datetime import datetime

ALLOWED_STATUSES = {"PENDING", "PAID", "FAILED", "CANCELED"}

def _validate_cnp(cnp: str) -> None:
    if not (isinstance(cnp, str) and cnp.isdigit() and len(cnp) == 13):
        raise ValueError("Invalid CNP: must be a 13-digit numeric string.")

def _validate_datetime(dt_str: str) -> None:
    try:
        datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        raise ValueError("Invalid DateTime: use 'YYYY-MM-DD HH:MM:SS'.")

def _validate_currency(cur: str) -> None:
    if not (isinstance(cur, str) and len(cur) == 3 and cur.isalpha() and cur.isupper()):
        raise ValueError("Invalid Currency: use a 3-letter uppercase ISO code (e.g., 'RON').")

def DB_API_add_payee(
    conn: sqlite3.Connection,
    cnp: str,
    amount: float,
    currency: str,
    dt_str: str,
    status: str,
    receiver: str,
    invoice_nr: str,
) -> int:
    """
    Insert a new row into Payee (CNP, Sum, Currency, DateTime, Status, Receiver, Invoice_nr).

    Returns:
        int: the newly inserted Payee.ID
    Raises:
        ValueError: on validation or database errors
    """
    try:
        # --- Validate inputs against schema expectations ---
        _validate_cnp(cnp)
        if not (isinstance(amount, (int, float)) and amount >= 0):
            raise ValueError("Invalid Sum: amount must be a non-negative number.")
        _validate_currency(currency)
        _validate_datetime(dt_str)

        status = status.upper().strip()
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid Status: must be one of {sorted(ALLOWED_STATUSES)}.")

        if not receiver or not receiver.strip():
            raise ValueError("Invalid Receiver: must be a non-empty string.")
        if not invoice_nr or not invoice_nr.strip():
            raise ValueError("Invalid Invoice_nr: must be a non-empty string.")

        cur = conn.cursor()

        # --- Check that the payer exists (CNP present in Payer) ---
        cur.execute("SELECT 1 FROM Payer WHERE CNP = ? LIMIT 1;", (cnp,))
        if not cur.fetchone():
            raise ValueError("CNP not found in Payer; cannot create Payee row.")

        # --- Guard against duplicate invoice for the same CNP (business rule) ---
        cur.execute(
            "SELECT 1 FROM Payee WHERE CNP = ? AND Invoice_nr = ? LIMIT 1;",
            (cnp, invoice_nr),
        )
        if cur.fetchone():
            raise ValueError("Duplicate invoice for this CNP: (CNP, Invoice_nr) must be unique in practice.")

        # --- Insert the new payee record ---
        cur.execute(
            """
            INSERT INTO Payee (CNP, Sum, Currency, DateTime, Status, Receiver, Invoice_nr)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (cnp, float(amount), currency, dt_str, status, receiver.strip(), invoice_nr.strip()),
        )
        conn.commit()
        return cur.lastrowid

    except sqlite3.Error as e:
        try:
            conn.rollback()
        except Exception:
            pass
        raise ValueError(f"Database error during Payee insertion: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {e}")
