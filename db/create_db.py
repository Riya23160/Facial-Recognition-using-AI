import sqlite3
import os

# Paths
DB_FOLDER = "db"
DB_PATH = os.path.join(DB_FOLDER, "criminals.db")
IMAGES_FOLDER = os.path.join(os.path.dirname(DB_FOLDER), "criminal_images")  # ../criminal_images

# Ensure folders exist
os.makedirs(DB_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)  # Your images should already be here

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create table with image_path
cursor.execute("""
CREATE TABLE IF NOT EXISTS criminals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    crimes TEXT,
    status TEXT,
    last_known_address TEXT,
    release_date TEXT,
    image_path TEXT
)
""")

# Clear existing data
cursor.execute("DELETE FROM criminals")

# Insert sample criminals with correct image paths
cursor.execute("""
INSERT INTO criminals (name, age, gender, crimes, status, last_known_address, release_date, image_path)
VALUES
('sachin kumar', 21, 'Male', 'Robbery', 'Out on bail', 'Clement Town, Dehradun, Uttarakhand', NULL, ?),
('siddhi tuli', 20, 'Female', 'Fraud, Identity Theft', 'In jail', 'Model Town, Haridwar, Uttarakhand', NULL, ?),
('shashwat singh kushwah', 22, 'Male', 'Murder, Smuggling', 'Released', 'Puram, Haldwani, Uttarakhand', '2024-09-15', ?)
""", (
    os.path.join(IMAGES_FOLDER, "sachin_kumar.jpg"),
    os.path.join(IMAGES_FOLDER, "siddhi_tuli.jpg"),
    os.path.join(IMAGES_FOLDER, "shashwat_singh_kushwah.jpg")
))

conn.commit()
conn.close()

print("Database created successfully with image paths pointing to the separate 'criminal_images' folder!")
