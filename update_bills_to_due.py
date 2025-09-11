# update_bills_to_due.py
from app.web_api.core.database import SessionLocal, Bill

def main():
    db = SessionLocal()
    try:
        updated = db.query(Bill).filter(Bill.status == "PAID").update({Bill.status: "DUE"})
        db.commit()
        print(f"Updated {updated} bills to DUE.")
    finally:
        db.close()

if __name__ == "__main__":
    main()

