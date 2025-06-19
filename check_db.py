from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Get all tables
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
        print("Tables in database:", [r[0] for r in result])
        
        # Get cash_boxes table structure
        result = conn.execute(text("PRAGMA table_info(cash_boxes);")).fetchall()
        print("\nCash_boxes table structure:")
        for row in result:
            print(row) 