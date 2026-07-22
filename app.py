import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
import tempfile
import base64

from preprocessing import preprocess_image, pil_to_cv2, cv2_to_pil
from detection import detect_vehicles
from rules import analyze_traffic
from analytics import TrafficAnalytics

# Page Config
st.set_page_config(page_title="AI Traffic Dashboard", page_icon="🚦", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Premium UI ---
st.markdown("""
<style>
    /* Main Theme Overrides */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Card Styling */
    div.css-1r6slb0, div.css-12oz5g7 {
        background-color: #1E2130;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Metrics Highlighting */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #4A90E2 !important;
    }
    
    /* Title styling */
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.5rem;
        background: -webkit-linear-gradient(45deg, #4A90E2, #50E3C2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #A0AEC0;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Analytics in session state
if 'analytics' not in st.session_state:
    st.session_state.analytics = TrafficAnalytics()
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0

def reset_session():
    st.session_state.analytics.reset()
    st.session_state.frame_count = 0

# Header
st.markdown('<h1 class="main-title">🚦 Smart Traffic Analytics Engine</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Real-time vehicle detection, tracking, and rule-based insights powered by YOLOv8.</p>', unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    conf_threshold = st.slider("Detection Confidence", 0.1, 1.0, 0.5, 0.05, 
                               help="Lower values detect more objects but may increase false positives.")
    
    use_tracking = st.toggle("Enable Vehicle Tracking (Unique IDs)", value=True,
                             help="Assigns unique IDs to track vehicles across frames.")
    
    apply_blur = st.toggle("Apply Noise Reduction (Blur)", value=False)

    st.divider()
    
    if st.button("🔄 Reset Analytics Session", use_container_width=True):
        reset_session()
        st.success("Session reset.")
        
    # File Uploader
    st.subheader("📁 Input Source")
    uploaded_file = st.file_uploader("Upload Image or Video", type=['jpg', 'jpeg', 'png', 'mp4'])

# --- Main Dashboard Layout ---
tab1, tab2 = st.tabs(["📺 Live Dashboard", "📊 Evaluation & Reports"])

with tab1:
    col1, col2 = st.columns([2, 1.2], gap="large")
    
    with col1:
        st.markdown("### 🎥 Vision Output")
        output_placeholder = st.empty()
        
    with col2:
        st.markdown("### 📈 Live Metrics")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            metric_vehicles = st.empty()
        with m_col2:
            metric_status = st.empty()
            
        st.markdown("---")
        st.markdown("### 📉 Traffic Trend")
        trend_placeholder = st.empty()

with tab2:
    st.markdown("### 📊 Performance & Evaluation Metrics")
    eval_col1, eval_col2, eval_col3 = st.columns(3)
    
    with eval_col1:
        eval_fps = st.empty()
    with eval_col2:
        eval_unique = st.empty()
    with eval_col3:
        eval_inf = st.empty()
        
    st.markdown("---")
    dist_placeholder = st.empty()
    
    st.markdown("---")
    st.markdown("### 📥 Export Data")
    download_placeholder = st.empty()

# --- Processing Logic ---
if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type in ['jpg', 'jpeg', 'png']:
        # Single Image Processing
        image = Image.open(uploaded_file)
        cv2_img = pil_to_cv2(image)
        
        start_time = time.time()
        
        processed_img = preprocess_image(cv2_img, apply_blur)
        annotated_img, detections = detect_vehicles(processed_img, conf_threshold, use_tracking=False)
        status, color, avg_conf = analyze_traffic(detections)
        vehicle_count = len(detections)
        
        inference_time = time.time() - start_time
        
        st.session_state.frame_count += 1
        st.session_state.analytics.add_frame_data(
            st.session_state.frame_count, detections, status, 0, inference_time
        )
        
        output_placeholder.image(cv2_to_pil(annotated_img), use_container_width=True)
        
        metric_vehicles.metric("Vehicles Detected", vehicle_count)
        metric_status.markdown(f"<div style='padding: 10px; border-radius: 5px; background-color: {color}; color: white; text-align: center; font-weight: bold; font-size: 1.2rem;'>{status}</div>", unsafe_allow_html=True)
        
    elif file_type == 'mp4':
        # Video Processing
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            start_time = time.time()
            
            processed_img = preprocess_image(frame, apply_blur)
            annotated_img, detections = detect_vehicles(processed_img, conf_threshold, use_tracking=use_tracking)
            status, color, avg_conf = analyze_traffic(detections)
            vehicle_count = len(detections)
            
            inference_time = time.time() - start_time
            fps = 1.0 / inference_time if inference_time > 0 else 0
            
            st.session_state.frame_count += 1
            st.session_state.analytics.add_frame_data(
                st.session_state.frame_count, detections, status, fps, inference_time
            )
            
            # --- Update UI Elements ---
            rgb_frame = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
            output_placeholder.image(rgb_frame, channels="RGB", use_container_width=True)
            
            metric_vehicles.metric("Vehicles in Frame", vehicle_count)
            # Use nicer hex colors for the status box
            bg_color = "#4CAF50" if color == "green" else "#FF9800" if color == "orange" else "#F44336"
            metric_status.markdown(f"<div style='padding: 15px; border-radius: 8px; background-color: {bg_color}; color: white; text-align: center; font-weight: bold; font-size: 1.1rem;'>{status}</div>", unsafe_allow_html=True)
            
            # Charts
            if st.session_state.frame_count % 3 == 0:  # Update charts every 3 frames for performance
                trend_chart = st.session_state.analytics.get_trend_chart()
                if trend_chart:
                    trend_placeholder.plotly_chart(trend_chart, use_container_width=True, key=f"trend_{st.session_state.frame_count}")
                    
                dist_chart = st.session_state.analytics.get_class_distribution_chart()
                if dist_chart:
                    dist_placeholder.plotly_chart(dist_chart, use_container_width=True, key=f"dist_{st.session_state.frame_count}")
                    
                # Eval Metrics
                a_fps, a_inf, unq = st.session_state.analytics.get_summary_metrics()
                eval_fps.metric("Average FPS", f"{a_fps:.1f}")
                eval_unique.metric("Total Unique Vehicles (Tracked)", unq if use_tracking else "N/A")
                eval_inf.metric("Avg Inference Time", f"{a_inf*1000:.1f} ms")
                
            time.sleep(0.01)
            
        cap.release()
        
    # --- Final Update after processing finishes ---
    trend_chart = st.session_state.analytics.get_trend_chart()
    if trend_chart:
        trend_placeholder.plotly_chart(trend_chart, use_container_width=True)
        
    dist_chart = st.session_state.analytics.get_class_distribution_chart()
    if dist_chart:
        dist_placeholder.plotly_chart(dist_chart, use_container_width=True)
        
    a_fps, a_inf, unq = st.session_state.analytics.get_summary_metrics()
    eval_fps.metric("Average FPS", f"{a_fps:.1f}")
    eval_unique.metric("Total Unique Vehicles (Tracked)", unq if use_tracking else "N/A")
    eval_inf.metric("Avg Inference Time", f"{a_inf*1000:.1f} ms")
    
    csv = st.session_state.analytics.get_csv()
    if csv:
        download_placeholder.download_button(
            label="📄 Download Analytics CSV",
            data=csv,
            file_name="traffic_analytics_report.csv",
            mime="text/csv"
        )
else:
    with tab1:
        st.info("👈 Please upload an image or video from the sidebar to start the analysis.")
