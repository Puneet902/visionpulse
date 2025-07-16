import streamlit as st
import cv2
from ultralytics import YOLO
from datetime import datetime
import os
from deepface import DeepFace
import yt_dlp
import pandas as pd

# --- Page Config and Styling ---
st.set_page_config(page_title="Real-time Security & Surveillance", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    h1, h2, h3 { color: #FFFFFF; }
    .stExpander { border-radius: 10px; border: 2px solid #4A4A4A; }
    .stExpander[aria-expanded="true"] { border-color: #4CAF50; }
    .threat-alert[aria-expanded="true"] { border-color: #e63946; }
    .stButton>button { width: 100%; border: 2px solid #4A4A4A; background-color: #262730; color: #FAFAFA; }
    .stButton>button:hover { border-color: #e63946; color: #e63946; }
    .stFileUploader { background-color: #262730; border-radius: 10px; padding: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡 Real-time Security & Surveillance")

# --- Registered Faces DB ---
DB_PATH = "registered_faces"
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

# --- Session State ---
if 'run_stream' not in st.session_state:
    st.session_state.run_stream = False
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'live_history' not in st.session_state:
    st.session_state.live_history = []

# --- Load YOLO Models ---
@st.cache_resource
def load_models():
    vehicle_model = YOLO("yolov8n.pt")
    weapon_model = YOLO("lightingbest.pt")
    return vehicle_model, weapon_model

vehicle_model, weapon_model = load_models()

# --- YouTube Stream Link Extractor ---
def get_direct_stream_link(youtube_url):
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True, 'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            stream_url = info_dict.get("url", None)
            return stream_url
    except Exception as e:
        st.error(f"❌ Error extracting stream link: {e}")
        return None

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["🔴 Live Detection", "👤 Face Registration", "🚨 Full Alerts Log"])

# --- 1️⃣ Live Detection ---
with tab1:
    st.header("Live Monitoring (Vehicles + Weapons + Face Recognition)")

    source_type = st.radio("Choose Video Source:", ["YouTube Live Stream", "Webcam"])
    stream_url = None

    if source_type == "YouTube Live Stream":
        youtube_url = st.text_input(
            "📺 Paste YouTube Live URL:",
            placeholder="https://www.youtube.com/watch?v=...",
            key="youtube_url_input"
        )
        if youtube_url:
            if "youtube.com/watch" in youtube_url:
                with st.spinner("Extracting stream link..."):
                    stream_url = get_direct_stream_link(youtube_url)
                if stream_url:
                    st.success(f"✅ Stream URL Ready!")
                else:
                    st.error("❌ Could not extract stream URL. Check if the video is public/live.")
            else:
                st.warning("⚠ Please provide a valid YouTube link.")
    elif source_type == "Webcam":
        stream_url = 0

    btn_col1, btn_col2 = st.columns(2)
    if btn_col1.button("▶ Start Stream"):
        if stream_url is not None:
            st.session_state.run_stream = True
        else:
            st.warning("Please provide a valid video source first.")
    if btn_col2.button("⏹ Stop Stream"):
        st.session_state.run_stream = False
        st.session_state.live_history = []

    frame_col, summary_col = st.columns([3, 1])
    frame_placeholder = frame_col.empty()
    summary_placeholder = summary_col.empty()

    if st.session_state.run_stream and stream_url is not None:
        cap = cv2.VideoCapture(stream_url)

        if not cap.isOpened():
            st.error("⚠ Unable to open video source.")
        else:
            last_threat_alert_time = {}

            while st.session_state.run_stream:
                ret, frame = cap.read()
                if not ret:
                    st.warning("⚠ Stream ended or could not read frame.")
                    st.session_state.run_stream = False
                    break

                annotated_frame = frame.copy()

                # --- VEHICLE DETECTION ---
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

                # --- WEAPON DETECTION ---
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
                                st.session_state.alerts.append({
                                    "time": now.strftime("%Y-%m-%d %H:%M:%S"),
                                    "event": f"{label} Detected",
                                    "screenshot": buffer.tobytes(),
                                    "type": "threat"
                                })
                                st.toast(f"🚨 {label} Detected!", icon="🚨")

                # --- FACE RECOGNITION (UPDATED LOGIC) ---
                try:
                    # DeepFace.find returns a list of dataframes. We check the first one.
                    result_df_list = DeepFace.find(
                        img_path=frame, db_path=DB_PATH, enforce_detection=False,
                        silent=True, model_name='SFace', detector_backend='opencv'
                    )
                    
                    # If the result list is not empty and its first dataframe is not empty, a known face was found
                    if result_df_list and not result_df_list[0].empty:
                        for _, row in result_df_list[0].iterrows():
                            # Get the name from the file path
                            identity = os.path.basename(row['identity']).split('.')[0]
                            
                            # Add KNOWN face to the detection history table
                            st.session_state.live_history.append({
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "object": f"Face: {identity.title()}"
                            })

                            # Check cooldown and create an ALERT for the known face
                            now = datetime.now()
                            last_time = last_threat_alert_time.get(identity, datetime.min)
                            if (now - last_time).total_seconds() > 10: # 10-second cooldown per person
                                last_threat_alert_time[identity] = now
                                _, buffer = cv2.imencode('.jpg', frame)
                                st.session_state.alerts.append({
                                    "time": now.strftime("%Y-%m-%d %H:%M:%S"),
                                    "event": f"Known Person: {identity.title()}",
                                    "screenshot": buffer.tobytes(),
                                    "type": "face"
                                })
                                st.toast(f"✅ Known Person Seen: {identity.title()}", icon="✅")
                    else:
                        # If no known face is found, add "Unknown Face" to the history table
                        st.session_state.live_history.append({
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "object": "Unknown Face"
                        })

                except Exception as e:
                    # If any error occurs during face detection (e.g., no face in frame), log it as Unknown
                    # and print the error to the console for debugging.
                    # print(f"DeepFace error: {e}") # Uncomment for debugging
                    st.session_state.live_history.append({
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "object": "Unknown Face"
                    })

                # --- Show annotated frame ---
                frame_placeholder.image(annotated_frame, channels="BGR")

                # --- Update real-time summary panel ---
                with summary_placeholder.container():
                    st.subheader("Recent Detections")
                    if st.session_state.live_history:
                        st.session_state.live_history = st.session_state.live_history[-10:]
                        df_summary = pd.DataFrame(st.session_state.live_history)
                        st.dataframe(df_summary.iloc[::-1], use_container_width=True, hide_index=True)
                    else:
                        st.write("Awaiting detections...")
                    
                    st.markdown("---")
                    
                    st.subheader("Live Security Alerts")
                    if not st.session_state.alerts:
                        st.info("No alerts recorded yet.")
                    else:
                        for alert in reversed(st.session_state.alerts):
                            expander_title = f"🚨 {alert['event']} at {alert['time']}"
                            with st.expander(expander_title):
                                st.image(alert['screenshot'], caption=f"Detection at {alert['time']}")
            cap.release()

    else:
        frame_placeholder.markdown("### Stream is stopped or no valid URL.")
        summary_placeholder.info("Start the stream to see live detections and alerts.")


# --- 2️⃣ Face Registration ---
with tab2:
    st.header("Register Known Individuals")
    st.info("Upload a clear photo. Name should have no spaces (e.g., 'john_doe').")
    col1, col2 = st.columns([1, 2])

    with col1:
        name_input = st.text_input("Enter person's name:", key="reg_name")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"], key="reg_file")

        if st.button("Register Face", disabled=(not name_input or not uploaded_file)):
            if ' ' in name_input:
                st.error("❌ Please remove spaces from the name.")
            else:
                try:
                    file_ext = os.path.splitext(uploaded_file.name)[1]
                    file_path = os.path.join(DB_PATH, f"{name_input.lower()}{file_ext}")
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    with st.spinner("Updating face database... This may take a moment."):
                        pkl_file = os.path.join(DB_PATH, "representations_sface.pkl")
                        if os.path.exists(pkl_file):
                            os.remove(pkl_file)
                        DeepFace.find(img_path=file_path, db_path=DB_PATH, enforce_detection=False,
                                      silent=True, model_name='SFace', detector_backend='opencv')
                    st.success(f"✅ Registered {name_input}!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: Could not process image. Ensure it contains a clear face. Details: {e}")

    with col2:
        st.subheader("Registered Individuals")
        image_files = [f for f in os.listdir(DB_PATH) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if not image_files:
            st.warning("No faces registered yet.")
        else:
            for file in image_files:
                file_path = os.path.join(DB_PATH, file)
                col_image, col_btn = st.columns([2, 1])
                with col_image:
                    st.image(file_path, caption=os.path.splitext(file)[0].title(), width=150)
                with col_btn:
                    if st.button(f"❌ Remove {file}", key=f"remove_{file}"):
                        os.remove(file_path)
                        pkl_file = os.path.join(DB_PATH, "representations_sface.pkl")
                        if os.path.exists(pkl_file):
                            os.remove(pkl_file)
                        st.success(f"✅ Removed {file}. Database will update on next registration or app restart.")
                        st.experimental_rerun()

# --- 3️⃣ Alerts Log ---
with tab3:
    st.header("Full Security & Activity Alerts Log")
    st.info("This tab shows all alerts recorded during the session. For live updates, see the panel in the 'Live Detection' tab.")
    if not st.session_state.alerts:
        st.info("No alerts have been recorded yet.")
    else:
        for alert in reversed(st.session_state.alerts):
            expander_title = f"🚨 {alert['event']} at {alert['time']}"
            with st.expander(expander_title):
                st.image(alert['screenshot'], caption=f"Detection at {alert['time']}")
