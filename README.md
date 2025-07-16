# 🛡 visionplus Real-time Security & Surveillance

This is a real-time AI security & surveillance app built with:

* YOLO (vehicle + weapon detection)
* DeepFace (face recognition)
* Streamlit live dashboard
* YouTube or webcam video sources
* Alerts & activity logging

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
2. Click **Download** and save `lightingbest.pt` in the same directory as your Streamlit app.

---

## ▶ How to Run

1. Clone this repo:

   ```bash
   git clone https://github.com/yourusername/yourrepo.git
   cd yourrepo
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Make sure `lightingbest.pt` is in the project folder.

4. Run the app:

   ```bash
   streamlit run your_script_name.py
   ```

---

## 👤 Face Registration

Use the **Face Registration** tab to upload known faces.
Images will be saved in `registered_faces/`.

---

## 🚨 Full Alerts Log

Check all security alerts and detection history in the **Full Alerts Log** tab.

---

## ⚡ Notes

* `lightingbest.pt` must be in the same folder or the app won’t detect weapons.
* Tested with YOLOv8 + DeepFace (SFace model).
* Supports webcam or live YouTube streams.
