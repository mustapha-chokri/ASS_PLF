import sqlite3
import os

# Path to database
DB_PATH = 'app/association.db'

# Open connection to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Verifying database structure...")

# Check if the table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Database tables:")
for table in tables:
    print(f"- {table[0]}")

# Check membership_applications table structure
cursor.execute("PRAGMA table_info(membership_applications)")
columns = cursor.fetchall()
print("\nMembership Applications table columns:")
for column in columns:
    print(f"- {column[1]} ({column[2]}){' PRIMARY KEY' if column[5] == 1 else ''}{' NOT NULL' if column[3] == 1 else ''}")

# Check if there are any existing records
cursor.execute("SELECT COUNT(*) FROM membership_applications")
count = cursor.fetchone()[0]
print(f"\nTotal records in membership_applications: {count}")

# Close connection
conn.close()
print("\nVerification complete.") 