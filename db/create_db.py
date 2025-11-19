import sqlite3

# Connect to database
conn = sqlite3.connect("criminals.db")
cursor = conn.cursor()

# Create table with new fields
cursor.execute("""
CREATE TABLE IF NOT EXISTS criminals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    crimes TEXT,
    status TEXT,
    last_known_address TEXT,
    release_date TEXT
)
""")

# Clear existing data (optional but helps accuracy during testing)
cursor.execute("DELETE FROM criminals")

# Add sample criminals with correct naming format
cursor.execute("""
INSERT INTO criminals (name, age, gender, crimes, status, last_known_address, release_date)
VALUES
('sachin kumar', 21, 'Male', 'Robbery', 'Out on bail', 'Clement Town, Dehradun, Uttarakhand', NULL),
('siddhi tuli', 20, 'Female', 'Fraud, Identity Theft', 'In jail', 'Model Town, Haridwar, Uttarakhand', NULL),
('shashwat singh kushwah', 22, 'Male', 'Murder, Smuggling', 'Released', 'Puram, Haldwani, Uttarakhand', '2024-09-15')
""")

conn.commit()
conn.close()

print("Database created with corrected names!")
