import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
import tempfile

from components.ui_styles import apply_custom_css
from components.sidebar import render_sidebar
from components.metrics import render_metrics, render_status_badge
from components.charts import render_charts
from components.insights import render_insights_panel

from core.preprocessing import preprocess_image, pil_to_cv2, cv2_to_pil
from core.detection import detect_vehicles
from core.rules import analyze_traffic
from core.analytics import TrafficAnalytics
from core.insights_engine import generate_insights

# Page Config
st.set_page_config(page_title="Traffic Intelligence", page_icon="🚥", layout="wide", initial_sidebar_state="expanded")
apply_custom_css()

# State Initialization
if 'analytics' not in st.session_state:
    st.session_state.analytics = TrafficAnalytics()
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'prev_vehicle_count' not in st.session_state:
    st.session_state.prev_vehicle_count = 0

def reset_session():
    st.session_state.analytics.reset()
    st.session_state.frame_count = 0
    st.session_state.prev_vehicle_count = 0

# Header
st.markdown('<div class="main-header">Smart Vehicle Detection & Traffic Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Real-time object detection and intelligent traffic assessment dashboard</div>', unsafe_allow_html=True)
st.markdown('<hr/>', unsafe_allow_html=True)

# Sidebar
uploaded_file, conf_threshold, draw_boxes, use_tracking, selected_classes, reset_btn = render_sidebar()

if reset_btn:
    reset_session()
    st.rerun()

# Layout Tabs
tab_live, tab_trends, tab_analysis = st.tabs(["🔴 Live Detection", "📈 Trends & Insights", "🔍 Deep Analysis"])

# Setup Placeholders
with tab_live:
    col_video, col_metrics = st.columns([1.5, 1], gap="large")
    with col_video:
        st.markdown("<h4 style='color: #F8FAFC; margin-bottom: 15px;'>Live Vision Output</h4>", unsafe_allow_html=True)
        video_placeholder = st.empty()
    with col_metrics:
        st.markdown("<h4 style='color: #F8FAFC; margin-bottom: 15px;'>Real-time Metrics</h4>", unsafe_allow_html=True)
        status_placeholder = st.empty()
        metrics_placeholder = st.empty()
        insights_placeholder = st.empty()

with tab_trends:
    st.markdown("### Traffic & Confidence Trends")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        trend_placeholder = st.empty()
    with t_col2:
        conf_placeholder = st.empty()
        
    st.markdown("---")
    st.markdown("### Vehicle Class Distribution")
    dist_placeholder = st.empty()

with tab_analysis:
    st.markdown("### Deep Analysis & Export")
    export_placeholder = st.empty()

# Processing Logic
if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    def process_frame(frame, apply_blur=False):
        start_time = time.time()
        processed_img = preprocess_image(frame, apply_blur)
        
        # Detect
        annotated_img, detections = detect_vehicles(processed_img, conf_threshold, use_tracking=use_tracking, draw_boxes=draw_boxes)
        
        # Filter by selected classes
        if selected_classes:
            detections = [d for d in detections if d['class'] in selected_classes]
            
        vehicle_count = len(detections)
        status, color, avg_conf = analyze_traffic(detections)
        
        inference_time = time.time() - start_time
        fps = 1.0 / inference_time if inference_time > 0 else 0
        
        # Update Analytics
        st.session_state.frame_count += 1
        st.session_state.analytics.add_frame_data(
            st.session_state.frame_count, detections, status, fps, inference_time
        )
        
        delta = vehicle_count - st.session_state.prev_vehicle_count
        st.session_state.prev_vehicle_count = vehicle_count
        
        # UI Updates
        rgb_frame = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB) if isinstance(frame, np.ndarray) else annotated_img
        
        # If it's a PIL image being processed directly, the color conversion logic might be slightly different 
        # but preprocess handles PIL/CV2. detect_vehicles returns BGR CV2 image.
        if isinstance(annotated_img, np.ndarray) and file_type in ['jpg', 'jpeg', 'png']:
             rgb_frame = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
             
        video_placeholder.image(rgb_frame, use_container_width=True)
        
        with status_placeholder.container():
            render_status_badge(status, color)
            
        with metrics_placeholder.container():
            render_metrics(vehicle_count, avg_conf, fps, inference_time, delta)
            
        # Insights Engine
        insights = generate_insights(st.session_state.analytics)
        with insights_placeholder.container():
            render_insights_panel(insights)
            
    if file_type in ['jpg', 'jpeg', 'png']:
        # Image
        image = Image.open(uploaded_file)
        cv2_img = pil_to_cv2(image)
        process_frame(cv2_img)
        
        # Render charts for image (single point)
        render_charts(st.session_state.analytics, trend_placeholder, conf_placeholder, dist_placeholder)
        
        csv = st.session_state.analytics.get_csv()
        if csv:
            export_placeholder.download_button("📄 Download Analytics CSV", data=csv, file_name="traffic_report.csv", mime="text/csv")
            
    elif file_type == 'mp4':
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
        
        if st.session_state.is_playing:
            while cap.isOpened() and st.session_state.is_playing:
                ret, frame = cap.read()
                if not ret:
                    st.session_state.is_playing = False
                    break
                
                process_frame(frame)
                
                if st.session_state.frame_count % 10 == 0:
                    render_charts(st.session_state.analytics, trend_placeholder, conf_placeholder, dist_placeholder)
                    
                time.sleep(0.01)
        else:
             # Just show static state
             if st.session_state.frame_count > 0:
                  render_charts(st.session_state.analytics, trend_placeholder, conf_placeholder, dist_placeholder)
                  
        cap.release()
        
        csv = st.session_state.analytics.get_csv()
        if csv:
            export_placeholder.download_button("📄 Download Analytics CSV", data=csv, file_name="traffic_report.csv", mime="text/csv")
            
else:
    st.info("👈 Please upload an image or video from the sidebar to initialize the dashboard.")
