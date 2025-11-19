from flask import Flask, request, jsonify, render_template
from deepface import DeepFace
import sqlite3
import os
import traceback

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "criminals.db")
CRIMINALS_IMAGES_PATH = os.path.join(BASE_DIR, "criminal_images")


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/identify", methods=["POST"])
def identify_person():
    try:
        if "image" not in request.files:
            return jsonify({"status":"error","message":"No image uploaded!"}), 400

        file = request.files.get("image")
        if not file or file.filename == "":
            return jsonify({"status":"error","message":"No file selected!"}), 400

        img_path = os.path.join(UPLOAD_FOLDER, file.filename.replace(" ", "_"))
        file.save(img_path)

        match_name = None
        confidence = 0

        for img_file in os.listdir(CRIMINALS_IMAGES_PATH):
            criminal_img_path = os.path.join(CRIMINALS_IMAGES_PATH, img_file)
            try:
                result = DeepFace.verify(img_path, criminal_img_path, model_name="Facenet512", enforce_detection=False)
                if result.get("verified") and result.get("confidence",0) > confidence:
                    confidence = result["confidence"]
                    match_name = img_file.split(".")[0].replace("_", " ").lower()
            except:
                continue

        if not match_name:
            os.remove(img_path)
            print("❌ No match found in database.")
            return jsonify({"status":"No Match Found","message":"No match found in criminal database."}), 200

        # Fetch from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, age, gender, crimes, status, last_known_address, release_date
            FROM criminals
            WHERE LOWER(name) = ?
        """, (match_name,))
        result = cursor.fetchone()
        conn.close()

        os.remove(img_path)  # Delete uploaded image

        if result:
            formatted_response = f"""
Person Identified
----------------------------
Name: {result[0].title()}
Age: {result[1]}
Gender: {result[2]}
Crimes: {result[3]}
Status: {result[4]}
Last Address: {result[5]}
Release Date: {result[6] if result[6] else "N/A"}
"""
            # Print nicely in terminal
            print("✅ Match found!")
            print(formatted_response)

            return jsonify({
                "status": "Match Found",
                "confidence": round(confidence,2),
                "message": formatted_response.strip()
            }), 200
        else:
            print("❌ No record in database for matched image.")
            return jsonify({"status":"No Match Found in Database","message":"No record in database for matched image."}), 200

    except Exception as e:
        try: os.remove(img_path)
        except: pass
        traceback.print_exc()
        return jsonify({"status":"error","message":str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
