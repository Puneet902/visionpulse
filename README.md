
# 🛡️ visionplus Real-time Security & Surveillance

A real-time AI-powered security & surveillance system built using:

* 🧠 YOLOv8 (vehicle + weapon detection)
* 👤 DeepFace (face recognition)
* 📹 Streamlit for live monitoring
* 🔌 FastAPI backend for external integrations
* 🗃️ PostgreSQL for alert logging
* 🎥 Webcam / YouTube video stream support

---

## 📦 Requirements

* Python 3.8+
* Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 📥 Download `lightingbest.pt`

This app uses a custom YOLO model for weapon detection.

👉 **Download manually from Google Drive:**

[Download lightingbest.pt](https://drive.google.com/file/d/1u0_bmAhAPG8uuJ1HShgofo7-1z4gga3X/view)

1. Click the link above.
2. Click **Download** and save `lightingbest.pt` in the project folder.

---

## ▶️ How to Run the App

### Step 1: Clone the Repository

```bash
git clone https://github.com/Puneet902/visionpulse.git
cd yourrepo
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Launch the Streamlit Frontend

```bash
streamlit run app.py
```

This will open the **dashboard UI** for detection and monitoring.

### Step 4: Launch FastAPI Backend

```bash
uvicorn main:app --reload
```

This will start the backend server at `http://127.0.0.1:8000`.

---

## 🧠 Features

* Live vehicle and weapon detection using YOLOv8
* Real-time face recognition with DeepFace
* Alerts auto-logged to PostgreSQL with snapshot images
* Register known users via face upload
* Upload alerts remotely using FastAPI

---

## 🗃️ PostgreSQL Database Setup

### 1️⃣ Create Database

```sql
CREATE DATABASE vision_alerts;
```

### 2️⃣ Create Alerts Table

```sql
CREATE TABLE IF NOT EXISTS public.alerts
(
    id integer NOT NULL DEFAULT nextval('alerts_id_seq'::regclass),
    "timestamp" timestamp without time zone,
    object_type text COLLATE pg_catalog."default",
    camera_id text COLLATE pg_catalog."default",
    image_path text COLLATE pg_catalog."default",
    CONSTRAINT alerts_pkey PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.alerts
    OWNER to postgres;
```

### 3️⃣ Create Users Table

```sql
CREATE TABLE email_user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    report_path TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


```

### 4️⃣ Update Credentials in Code

In `app.py` and `main.py`, update your PostgreSQL password:

```python
psycopg2.connect(
    host="localhost",
    database="vision_alerts",
    user="postgres",
    password="your_password_here"
)
```

---

## 🧑‍💼 Face Registration

Use the **Face Registration** tab in the dashboard to upload known faces.
They are stored in `registered_faces/`.

---

## 📜 Full Alerts Log

Navigate to the **Full Alerts Log** tab in Streamlit to see all past detections with timestamps, object type, and camera ID.

---

## 🛠️ Notes

* Keep `lightingbest.pt` in the same folder as the app.
* Face detection works best with frontal clear images.

---

