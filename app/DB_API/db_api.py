def DB_API_Check_User(cnp: str) -> int:
    """
    DB_API_Check_User function
    Parameter: cnp - 13 digit numeric string
    Return: 1 if it starts with '1', 0 if it starts with '2', otherwise raises ValueError
    """
    # Validate that input is a 13-digit number
    if not (cnp.isdigit() and len(cnp) == 13):
        raise ValueError("Invalid CNP: must be a 13-digit numeric string.")

    # Return 1 if CNP starts with '1'
    if cnp[0] == '1':
        return 1
    # Return 0 if CNP starts with '2'
    elif cnp[0] == '2':
        return 0
    else:
        # Raise error for unsupported starting digit
        raise ValueError("Invalid CNP: must start with '1' or '2'.")
