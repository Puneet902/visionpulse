from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import shutil
import psycopg2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("alert_images", exist_ok=True)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="vision_alerts",
        user="postgres",
        password="your_password_here"
    )

# 🚨 Route for uploading alerts
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

# ✅ Route to register Firebase user email into users table
@app.post("/register_user/")
async def register_user(email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure users table exists
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
