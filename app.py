import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
import tempfile

from preprocessing import preprocess_image, pil_to_cv2, cv2_to_pil
from detection import detect_vehicles
from rules import analyze_traffic
from analytics import TrafficAnalytics

# Page Config
st.set_page_config(page_title=\"Smart Vehicle Detection\", page_icon=\"🚗\", layout=\"wide\")

# Initialize Analytics in session state
if 'analytics' not in st.session_state:
    st.session_state.analytics = TrafficAnalytics()
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0

def reset_session():
    st.session_state.analytics.reset()
    st.session_state.frame_count = 0

# UI Header
st.title(\"🚗 Smart Vehicle Detection with Rule-Based Traffic Analysis\")
st.markdown(\"\"\"
This application detects vehicles (cars, trucks, buses, bikes) in images or videos, 
analyzes the traffic conditions using simple rule-based logic, and presents real-time analytics.
\"\"\")

# Sidebar Controls
st.sidebar.header(\"⚙️ Settings\")
conf_threshold = st.sidebar.slider(\"Confidence Threshold\", 0.1, 1.0, 0.5, 0.05)
apply_blur = st.sidebar.toggle(\"Apply Gaussian Blur (Preprocessing)\", value=False)

if st.sidebar.button(\"🔄 Reset Session\"):
    reset_session()
    st.sidebar.success(\"Session Reset Successfully!\")

st.sidebar.markdown(\"---_{}_---\")
st.sidebar.markdown(\"**Supported Formats:** .jpg, .jpeg, .png, .mp4\")

# Main Layout
col1, col2 = st.columns([2, 1])

# File Uploader
uploaded_file = st.file_uploader(\"Upload an Image or Video\", type=['jpg', 'jpeg', 'png', 'mp4'])

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    with col1:
        st.subheader(\"Output Visualization\")
        output_placeholder = st.empty()
        
    with col2:
        st.subheader(\"Real-Time Metrics\")
        metrics_placeholder = st.empty()
        trend_placeholder = st.empty()
        
    if file_type in ['jpg', 'jpeg', 'png']:
        # Process Image
        image = Image.open(uploaded_file)
        cv2_img = pil_to_cv2(image)
        
        start_time = time.time()
        
        # Preprocess
        processed_img = preprocess_image(cv2_img, apply_blur)
        
        # Detect
        annotated_img, detections = detect_vehicles(processed_img, conf_threshold)
        
        # Analyze
        status, color, avg_conf = analyze_traffic(detections)
        vehicle_count = len(detections)
        
        inference_time = time.time() - start_time
        
        # Update Analytics
        st.session_state.frame_count += 1
        st.session_state.analytics.add_frame_data(
            st.session_state.frame_count, vehicle_count, avg_conf, status
        )
        
        # Display Output
        output_placeholder.image(cv2_to_pil(annotated_img), use_container_width=True)
        
        with metrics_placeholder.container():
            st.metric(\"Vehicles Detected\", vehicle_count)
            st.metric(\"Avg Confidence\", f\"{avg_conf:.2f}\")
            st.markdown(f\"**Traffic Status:** <span style='color:{color}; font-weight:bold;'>{status}</span>\", unsafe_allow_html=True)
            st.caption(f\"Inference Time: {inference_time:.3f}s\")
            
        with trend_placeholder.container():
            chart = st.session_state.analytics.get_trend_chart()
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                
    elif file_type == 'mp4':
        # Process Video
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        
        cap = cv2.VideoCapture(tfile.name)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            start_time = time.time()
            
            # Preprocess
            processed_img = preprocess_image(frame, apply_blur)
            
            # Detect
            annotated_img, detections = detect_vehicles(processed_img, conf_threshold)
            
            # Analyze
            status, color, avg_conf = analyze_traffic(detections)
            vehicle_count = len(detections)
            
            inference_time = time.time() - start_time
            fps = 1.0 / inference_time if inference_time > 0 else 0
            
            # Update Analytics
            st.session_state.frame_count += 1
            st.session_state.analytics.add_frame_data(
                st.session_state.frame_count, vehicle_count, avg_conf, status
            )
            
            # Display Output
            rgb_frame = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
            output_placeholder.image(rgb_frame, channels=\"RGB\", use_container_width=True)
            
            with metrics_placeholder.container():
                st.metric(\"Vehicles Detected\", vehicle_count)
                st.metric(\"Avg Confidence\", f\"{avg_conf:.2f}\")
                st.markdown(f\"**Traffic Status:** <span style='color:{color}; font-weight:bold;'>{status}</span>\", unsafe_allow_html=True)
                st.caption(f\"FPS: {fps:.1f} | Inference Time: {inference_time:.3f}s\")
                
            with trend_placeholder.container():
                chart = st.session_state.analytics.get_trend_chart()
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
                    
            # Small sleep to prevent UI freezing
            time.sleep(0.01)
            
        cap.release()
else:
    st.info(\"Please upload an image or video to start the analysis.\")
