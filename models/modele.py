from deepface import DeepFace

# This will download FaceNet512 model into your .deepface folder
model = DeepFace.build_model("Facenet512")
print("Downloaded model!")

