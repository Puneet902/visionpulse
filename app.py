import streamlit as st
import psycopg2
import cv2
from ultralytics import YOLO
from datetime import datetime
import os
from deepface import DeepFace
import pandas as pd

st.set_page_config(page_title="OASIS Edge AI Unit", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #1e1e2f; color: #FAFAFA; font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3, h4 { color: #FAFAFA; }
    .stExpander { border-radius: 10px; border: 2px solid #3a3a50; background-color: #2a2a3d; }
    .stExpander[aria-expanded="true"] { border-color: #00C6A2; }
    .stButton>button { width: 100%; padding: 10px; font-weight: bold; background-color: #00C6A2; border: none; border-radius: 5px; color: white; }
    .stButton>button:hover { background-color: #00a98f; }
    .stFileUploader { background-color: #2a2a3d; border-radius: 10px; padding: 15px; border: 2px dashed #555; }
    .stTextInput>div>input { background-color: #2a2a3d; color: #FAFAFA; border: 1px solid #555; border-radius: 5px; padding: 8px; }
    .css-1aumxhk { background-color: #1e1e2f; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡 Real-time Security & Surveillance")

DB_PATH = "registered_faces"
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)
if not os.path.exists("snapshots"):
    os.makedirs("snapshots")

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="vision_alerts",
        user="postgres",
        password="Muralik@902"
    )

@st.cache_resource
def load_models():
    vehicle_model = YOLO("yolov8n.pt")
    weapon_model = YOLO("lightingbest.pt")
    return vehicle_model, weapon_model

vehicle_model, weapon_model = load_models()

if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "live_history" not in st.session_state:
    st.session_state.live_history = []
if "run_stream" not in st.session_state:
    st.session_state.run_stream = False

tab1, tab2, tab3 = st.tabs(["🔴 Live Detection", "👤 Face Registration", "🚨 Full Alerts Log"])

with tab1:
    st.header("📡 Live Monitoring (Vehicles + Weapons + Face Recognition)")
    col1, col2 = st.columns([3, 1])
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("⚠ Unable to access the camera.")
    else:
        start = col2.button("▶ Start Detection")
        stop = col2.button("⏹ Stop Detection")
        frame_placeholder = col1.empty()
        summary_placeholder = col2.empty()
        if start:
            st.session_state.run_stream = True
        if stop:
            st.session_state.run_stream = False
        last_threat_alert_time = {}
        while st.session_state.run_stream:
            ret, frame = cap.read()
            if not ret:
                break
            annotated_frame = frame.copy()
            results_weapon = weapon_model(frame, verbose=False, conf=0.2)
            for r in results_weapon:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    label = r.names[class_id].upper()
                    if label in ["GUN", "KNIFE"]:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        color = (0, 0, 255) if label == "GUN" else (0, 255, 255)
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(annotated_frame, f"!! {label} !!", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                        st.session_state.live_history.append({
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "object": f"THREAT: {label}"
                        })
                        now = datetime.now()
                        last_time = last_threat_alert_time.get(label, datetime.min)
                        if (now - last_time).total_seconds() > 10:
                            last_threat_alert_time[label] = now
                            _, buffer = cv2.imencode('.jpg', frame)
                            screenshot_path = f"snapshots/{label}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
                            with open(screenshot_path, "wb") as f:
                                f.write(buffer)
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO alerts (timestamp, object_type, camera_id, image_path) VALUES (%s, %s, %s, %s)",
                                (now.strftime("%Y-%m-%d %H:%M:%S"), label, "cam0", screenshot_path)
                            )
                            conn.commit()
                            cursor.close()
                            conn.close()

            results_vehicle = vehicle_model(frame, verbose=False, conf=0.3)
            for r in results_vehicle:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    label = r.names[class_id].lower()
                    if label in ["car", "bus", "truck", "motorcycle", "bicycle"]:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(annotated_frame, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        st.session_state.live_history.append({
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "object": label.title()
                        })

            try:
                result_df_list = DeepFace.find(
                    img_path=frame, db_path=DB_PATH, enforce_detection=False,
                    silent=True, model_name='SFace', detector_backend='opencv'
                )
                if result_df_list and not result_df_list[0].empty:
                    for _, row in result_df_list[0].iterrows():
                        identity = os.path.basename(row['identity']).split('.')[0]
                        st.session_state.live_history.append({
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "object": f"Face: {identity.title()}"
                        })
                        now = datetime.now()
                        _, buffer = cv2.imencode('.jpg', frame)
                        screenshot_path = f"snapshots/Face_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
                        with open(screenshot_path, "wb") as f:
                            f.write(buffer)
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO alerts (timestamp, object_type, camera_id, image_path) VALUES (%s, %s, %s, %s)",
                            (now.strftime("%Y-%m-%d %H:%M:%S"), f"Face: {identity.title()}", "cam0", screenshot_path)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
            except:
                pass

            frame_placeholder.image(annotated_frame, channels="BGR")
            with summary_placeholder.container():
                st.subheader("Recent Detections")
                if st.session_state.live_history:
                    df_summary = pd.DataFrame(st.session_state.live_history[-10:])
                    st.dataframe(df_summary.iloc[::-1], use_container_width=True, hide_index=True)
                else:
                    st.write("Awaiting detections...")
        cap.release()

with tab2:
    st.header("🧑‍💼 Register Known Individuals")
    name_input = st.text_input("Enter person's name:")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    if st.button("Register Face"):
        if name_input and uploaded_file:
            file_ext = os.path.splitext(uploaded_file.name)[1]
            file_path = os.path.join(DB_PATH, f"{name_input.lower()}{file_ext}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            st.success(f"✅ Registered {name_input}!")
    if st.button("🗑 Remove All Faces"):
        for file in os.listdir(DB_PATH):
            os.remove(os.path.join(DB_PATH, file))
        st.warning("🚫 All registered faces removed.")

with tab3:
    st.header("📜 Full Security & Activity Alerts Log")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, object_type, camera_id, image_path FROM alerts ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for timestamp, object_type, cam_id, img_path in rows:
        with st.expander(f"🚨 {object_type} at {timestamp} from {cam_id}"):
            if os.path.exists(img_path):
                st.image(img_path)
            else:
                st.warning("Image not found")
