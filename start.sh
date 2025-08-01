#!/bin/bash
# Run FastAPI in the background
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Run Streamlit on Railway default port 8080
streamlit run app.py --server.port 8080 --server.enableCORS false
