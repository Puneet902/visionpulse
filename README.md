# 🛡️ VisionPlus – Real-time Security & Surveillance  

VisionPlus is an AI-powered real-time security and surveillance system designed for **weapon detection, face recognition, and automated alerting**.  
It processes CCTV and live camera feeds, detects threats, and instantly generates alerts with snapshots.  
The system also logs alerts in a PostgreSQL database and sends automated reports to admins via email.  
 <img width="858" height="469" alt="dashboard2" src="https://github.com/user-attachments/assets/9ecea7d6-464c-4b77-9840-111c53511e9f" />


---

## ✨ Key Features  
- 🔫 **Weapon Detection** – Real-time detection using YOLOv8  
- 👤 **Face Recognition** – DeepFace for recognizing and verifying individuals  
- 🚗 **Vehicle Detection** – Detects vehicles from CCTV/live streams  
- 📹 **Live Monitoring Dashboard** – Streamlit-based real-time monitoring  
- 🔌 **Backend Integration** – FastAPI for external alert/report services  
- 🗃️ **Database Logging** – PostgreSQL storage with snapshot support  
- 📧 **Email Notifications** – Sends automated reports to registered admins  

---

## ⚙️ Requirements  
- Python 3.8+  
- Install dependencies:  
```bash
pip install -r requirements.txt
```

---

## 📥 Model Download (`lightingbest.pt`)  
VisionPlus uses a custom YOLOv8 model for weapon detection.  

👉 [Download lightingbest.pt](https://drive.google.com/file/d/1u0_bmAhAPG8uuJ1HShgofo7-1z4gga3X/view)  

Save the file in the project folder.  

---

## ▶️ How to Run  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/Puneet902/visionpulse.git
cd visionpulse
```

### 2️⃣ Install Dependencies  
```bash
pip install -r requirements.txt
```

### 3️⃣ Launch Streamlit Dashboard  
```bash
streamlit run app.py
```
Opens the **real-time monitoring dashboard**.  

### 4️⃣ Start FastAPI Backend  
```bash
uvicorn main:app --reload
```
Runs backend services at: `http://127.0.0.1:8000`  

---

## 🗃️ Database Setup (PostgreSQL)  

### Create Database  
```sql
CREATE DATABASE vision_alerts;
```

### Create Alerts Table  
```sql
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    object_type TEXT,
    camera_id TEXT,
    image_path TEXT
);
```

### Create Users Table  
```sql
CREATE TABLE email_user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    report_path TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Update Credentials  
In `app.py` and `main.py`:  
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
Upload known faces in the **Face Registration tab** of the dashboard.  
Stored inside `registered_faces/`.  

---

## 📜 Alerts Log  
View full detection history (with timestamps, object type, and camera ID) under the **Alerts Log** tab in the dashboard.  
<img width="900" height="469" alt="alerts" src="https://github.com/user-attachments/assets/06527525-ddd4-4dd4-80e0-73029c506feb" />


---

## 🛠️ Notes  
- Keep `lightingbest.pt` in the same folder as `app.py`.  
- Face detection works best with clear frontal images.  

---

## 📌 Tech Stack  
- **AI/ML:** YOLOv8, DeepFace, OpenCV  
- **Frontend:** Streamlit  
- **Backend:** FastAPI  
- **Database:** PostgreSQL  
- **Language:** Python  
