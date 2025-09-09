# main.py

from db_api import DB_API_Check_User

def main():
    # Example CNP values
    cnp_list = [
        "1981234567890",  # starts with '1'
        "2981234567890",  # starts with '2'
        "3981234567890"   # invalid
        "198123456789"   # invalid
    ]

    for cnp in cnp_list:
        try:
            result = DB_API_Check_User(cnp)
            print(f"CNP: {cnp} -> Result: {result}")
        except ValueError as e:
            print(f"CNP: {cnp} -> Error: {e}")

if __name__ == "__main__":
    main()
