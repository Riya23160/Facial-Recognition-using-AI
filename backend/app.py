from flask import Flask, request, jsonify
from deepface import DeepFace
import sqlite3
import os

app = Flask(__name__)

# Folder to temporarily save uploaded images
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend folder
DB_PATH = os.path.join(BASE_DIR, "..", "db", "criminals.db")
CRIMINALS_IMAGES_PATH = os.path.join(BASE_DIR, "..", "criminal_images")


@app.route("/")
def home():
    return "Face Identification API Running!"


@app.route("/identify", methods=["POST"])
def identify_person():
    print("📨 Request received!")

    if "image" not in request.files:
        print("❌ No image file in request")
        return jsonify({"error": "No image uploaded!"}), 400

    file = request.files["image"]

    if file.filename == "":
        print("❌ Empty file name")
        return jsonify({"error": "No selected file!"}), 400

    # Save uploaded image in uploads folder
    img_path = os.path.join(UPLOAD_FOLDER, file.filename.replace(" ", "_"))
    file.save(img_path)
    print(f"📸 Image saved at: {img_path}")

    match_name = None
    confidence = 0

    try:
        print("🔍 Starting face comparison with images in criminal_images folder...")

        for img in os.listdir(CRIMINALS_IMAGES_PATH):
            criminal_img_path = os.path.join(CRIMINALS_IMAGES_PATH, img)
            print(f"🔍 Comparing with {img}...")

            result = DeepFace.verify(img_path, criminal_img_path, model_name="Facenet512", enforce_detection=False)

            print(f"✔ Verified: {result['verified']} | Confidence: {round(result['confidence'], 2)}")

            if result["verified"] and result["confidence"] > confidence:
                confidence = result["confidence"]
                match_name = img.split(".")[0].replace("_", " ").lower()

        # If no match found
        if not match_name:
            print("❌ No match found")
            os.remove(img_path)
            print("🗑️ Temporary file removed")
            return jsonify({"status": "No Match Found"}), 200

        print(f"🧠 Match: {match_name} | Confidence: {round(confidence, 2)}")

        # Fetch from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT name, age, gender, crimes, status, last_known_address, release_date FROM criminals WHERE LOWER(name) = ?", (match_name,))
        result = cursor.fetchone()
        conn.close()

        os.remove(img_path)  # Delete uploaded image
        print("🗑️ Temporary file removed")

        if result:
            formatted_response = f"""
Person Identified
----------------------------
Name: {result[0].replace('_', ' ').title()}
Age: {result[1]}
Gender: {result[2]}
Crimes: {result[3]}
Status: {result[4]}
Last Address: {result[5]}
Release Date: {result[6] if result[6] else "N/A"}
"""
            print("✅ Match Found!")
            print(formatted_response)

            return jsonify({
                "status": "Match Found",
                "confidence": round(confidence, 2),
                "message": formatted_response.strip()
            }), 200

        else:
            print("❌ No Match Found in Database")
            return jsonify({"status": "No Match Found in Database"}), 200

    except Exception as e:
        print(f"⚠️ Error occurred: {str(e)}")
        try:
            os.remove(img_path)
            print("🗑️ Temporary file removed due to error")
        except:
            pass
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
