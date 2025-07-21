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

# Ensure alert_images directory exists
os.makedirs("alert_images", exist_ok=True)

# PostgreSQL connection function
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="vision_alerts",
        user="postgres",
        password="Muralik@902"
    )

# Upload endpoint
@app.post("/upload_alert/")
async def upload_alert(
    timestamp: str = Form(...),
    object_type: str = Form(...),
    camera_id: str = Form(...),
    image: UploadFile = None
):
    folder = os.path.join("alert_images", camera_id)
    os.makedirs(folder, exist_ok=True)

    file_path = None
    if image:
        filename = f"{timestamp}_{object_type}.jpg"
        file_path = os.path.join(folder, filename)
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
