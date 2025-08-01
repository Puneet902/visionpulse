from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import shutil
import psycopg2
import gdown

app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directory for alerts if it doesn't exist
os.makedirs("alert_images", exist_ok=True)

# ✅ Function to auto-download model if missing
def download_model_if_needed():
    model_path = "lightingbest.pt"
    if not os.path.exists(model_path):
        print("🔽 Downloading lightingbest.pt from Google Drive...")
        url = "https://drive.google.com/uc?id=1u0_bmAhAPG8uuJ1HShgofo7-1z4gga3X"
        gdown.download(url, output=model_path, quiet=False)
        print("✅ Download complete!")

# ✅ Run download function on startup
download_model_if_needed()

# ✅ Database connection helper
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="vision_alerts",
        user="postgres",
        password="Muralik@902"
    )

# 🚨 Endpoint to upload alert with optional image
@app.post("/upload_alert/")
async def upload_alert(
    timestamp: str = Form(...),
    object_type: str = Form(...),
    camera_id: str = Form(...),
    image: UploadFile = None
):
    folder = f"alert_images/{camera_id}"
    os.makedirs(folder, exist_ok=True)

    file_path = None
    if image:
        file_path = f"{folder}/{timestamp}_{object_type}.jpg"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO alerts (timestamp, object_type, camera_id, image_path) VALUES (%s, %s, %s, %s)",
        (timestamp, object_type, camera_id, file_path)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "success", "message": "Alert saved"}

# ✅ Endpoint to register a Firebase user
@app.post("/register_user/")
async def register_user(email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    try:
        cursor.execute(
            "INSERT INTO users (email) VALUES (%s) ON CONFLICT (email) DO NOTHING",
            (email,)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"status": "error", "message": str(e)}

    cursor.close()
    conn.close()
    return {"status": "success", "message": f"User {email} registered"}
