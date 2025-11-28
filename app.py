import sqlite3
from flask import Flask, request, jsonify, render_template
from deepface import DeepFace
import os
from werkzeug.utils import secure_filename
import time

# ===================== Flask Setup =====================
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["DATABASE_IMAGES"] = "criminal_images"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["DATABASE_IMAGES"], exist_ok=True)

DB_PATH = os.path.join("db", "criminals.db")


# ===================== Helper Functions =====================
def get_all_criminals():
    """Fetch all criminals from SQLite DB"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows dict-like access
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM criminals")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_criminal(data):
    """Insert a new criminal record into SQLite DB"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO criminals (name, age, gender, crimes, status, last_known_address, release_date, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['name'],
        data['age'],
        data['gender'],
        data['crimes'],
        data['status'],
        data['address'],
        data['release_date'],
        data['image_path']
    ))
    conn.commit()
    conn.close()

# ===================== Home Route =====================
@app.route('/')
def home():
    return render_template("index.html")

# ===================== IDENTIFICATION API =====================
@app.route('/identify', methods=['POST'])
def identify():
    try:
        if 'image' not in request.files:
            return jsonify({"status": "No image provided"}), 400

        image = request.files['image']
        filename = secure_filename(image.filename)
        filepath = os.path.abspath(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        image.save(filepath)

        print(f"[*] Identifying image saved at: {filepath}")

        best_match = None
        max_confidence = -1
        start_time = time.time()

        criminals = get_all_criminals()  # Fetch from SQLite

        for criminal in criminals:
            stored_image = os.path.abspath(criminal["image_path"])
            try:
                result = DeepFace.verify(
                    img1_path=filepath,
                    img2_path=stored_image,
                    model_name="Facenet",
                    enforce_detection=False
                )
                print(f"Comparing with {stored_image}: {result}")

                if result["verified"] and result["distance"] < 0.4:
                    confidence = (1 - result["distance"]) * 100
                    if confidence > max_confidence:
                        max_confidence = confidence
                        best_match = criminal

            except Exception as e:
                print(f"Error comparing: {e}")
                continue

        if best_match:
            response_time = time.time() - start_time
            return jsonify({
                "status": "Match Found",
                "message": f"""Person Identified
Name: {best_match['name']}
Age: {best_match['age']}
Gender: {best_match['gender']}
Crimes: {best_match['crimes']}
Status: {best_match['status']}
Address: {best_match['last_known_address']}
Release Date: {best_match['release_date']}
Confidence: {max_confidence:.2f}%
Processing Time: {response_time:.2f}s"""
            })
        else:
            return jsonify({"status": "No Match Found", "message": "No criminal records matched."})

    except Exception as e:
        print(f"Identify error: {e}")
        return jsonify({"status": "Error", "message": str(e)})

# ===================== UPDATE CRIMINAL RECORD API =====================
@app.route('/update', methods=['POST'])
def update_criminal():
    try:
        if 'image' not in request.files:
            return jsonify({"status": "No image provided"}), 400

        image = request.files['image']
        filename = secure_filename(image.filename)
        save_path = os.path.abspath(os.path.join(app.config["DATABASE_IMAGES"], filename))
        image.save(save_path)

        data = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "gender": request.form.get("gender"),
            "crimes": request.form.get("crimes"),
            "status": request.form.get("status"),
            "address": request.form.get("address"),
            "release_date": request.form.get("releaseDate"),
            "image_path": save_path
        }

        if not all(data.values()):
            return jsonify({"status": "Missing Data", "message": "Fill all fields"}), 400

        add_criminal(data)

        return jsonify({"status": "Success", "message": f"Criminal record for {data['name']} added successfully!"})

    except Exception as e:
        print(f"Update error: {e}")
        return jsonify({"status": "Error", "message": str(e)})

# ===================== Run App =====================
if __name__ == "__main__":
    app.run(debug=True)
