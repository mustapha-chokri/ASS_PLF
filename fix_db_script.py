import sqlite3
from datetime import datetime

# Path to database
DB_PATH = 'app/association.db'

# Open connection to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Checking database structure...")
# Check if the table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='membership_applications'")
table_exists = cursor.fetchone()

if not table_exists:
    print("Table membership_applications does not exist. Creating it...")
    # Create the table with all required columns including application_token
    cursor.execute("""
    CREATE TABLE membership_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name VARCHAR(64) NOT NULL,
        last_name VARCHAR(64) NOT NULL,
        national_id VARCHAR(20),
        birth_date DATE,
        address VARCHAR(256),
        phone VARCHAR(15) NOT NULL,
        email VARCHAR(120),
        profession VARCHAR(64),
        application_date DATE NOT NULL,
        status VARCHAR(20) NOT NULL,
        notes TEXT,
        reviewed_by INTEGER,
        review_date DATETIME,
        application_token VARCHAR(64) UNIQUE
    )
    """)
    conn.commit()
    print("Table membership_applications created successfully.")
else:
    print("Table membership_applications exists. Checking for application_token column...")
    # Check if application_token column exists
    cursor.execute("PRAGMA table_info(membership_applications)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'application_token' not in columns:
        print("Adding application_token column...")
        cursor.execute("ALTER TABLE membership_applications ADD COLUMN application_token VARCHAR(64) UNIQUE")
        conn.commit()
        print("Column application_token added successfully.")
    else:
        print("Column application_token already exists.")

# Close connection
conn.close()
print("Database update completed.") 