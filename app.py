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
st.set_page_config(page_title="AI Traffic Insights", page_icon="🚥", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Premium SaaS UI ---
st.markdown("""
<style>
    /* Dark Theme Base */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Hide Streamlit default branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Layout styling */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Titles */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 0px;
        color: #E2E8F0;
    }
    .sub-header {
        font-size: 1rem;
        font-weight: 400;
        color: #94A3B8;
        margin-top: -5px;
        margin-bottom: 25px;
    }
    hr {
        margin-top: 10px;
        margin-bottom: 20px;
        border-color: #334155;
    }

    /* Custom Metric Cards */
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    
    /* Traffic Badges */
    .badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-green { background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.2); }
    .badge-red { background-color: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.2); }
    .badge-yellow { background-color: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.2); }
    
    /* Insights Panel */
    .insights-panel {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
    .insight-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 12px;
        font-size: 0.95rem;
        color: #CBD5E1;
    }
    .insight-icon {
        margin-right: 10px;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# State Init
if 'analytics' not in st.session_state:
    st.session_state.analytics = TrafficAnalytics()
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0

def reset_session():
    st.session_state.analytics.reset()
    st.session_state.frame_count = 0

# --- Top Header ---
st.markdown('<div class="main-header">Smart Vehicle Detection & Traffic Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Real-time object detection and intelligent traffic assessment dashboard</div>', unsafe_allow_html=True)
st.markdown('<hr/>', unsafe_allow_html=True)

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    uploaded_file = st.file_uploader("📂 Input Source", type=['jpg', 'jpeg', 'png', 'mp4'])
    
    st.markdown("---")
    
    st.markdown("**Detection Settings**")
    conf_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.05)
    
    draw_boxes = st.toggle("👁️ Show Bounding Boxes", value=True)
    use_tracking = st.toggle("🎯 Unique Vehicle Tracking", value=True)
    apply_blur = st.toggle("🌫️ Apply Noise Reduction", value=False)
    
    st.markdown("---")
    if st.button("🔄 Reset Analytics Session", use_container_width=True):
        reset_session()
        st.success("Session reset.")

# --- Tabs ---
tab_dash, tab_analytics, tab_settings = st.tabs(["🎛️ Live Dashboard", "📈 Deep Analytics", "⚙️ Settings & Export"])

# Placeholders in Dashboard Tab
with tab_dash:
    dash_col1, dash_col2 = st.columns([1.5, 1], gap="large")
    
    with dash_col1:
        st.markdown("<h4 style='color: #E2E8F0; margin-bottom: 15px;'>Live Vision Output</h4>", unsafe_allow_html=True)
        # Using a styled container for video
        st.markdown("<div style='border: 1px solid #334155; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>", unsafe_allow_html=True)
        output_placeholder = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with dash_col2:
        st.markdown("<h4 style='color: #E2E8F0; margin-bottom: 15px;'>Key Metrics</h4>", unsafe_allow_html=True)
        
        status_placeholder = st.empty()
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Metric Cards
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            vehicles_metric_placeholder = st.empty()
            fps_metric_placeholder = st.empty()
        with m_col2:
            conf_metric_placeholder = st.empty()
            inf_metric_placeholder = st.empty()
            
        insights_placeholder = st.empty()

# Placeholders in Analytics Tab
with tab_analytics:
    st.markdown("### Historical Traffic Trends")
    trend_placeholder = st.empty()
    
    st.markdown("---")
    st.markdown("### Vehicle Class Distribution")
    dist_placeholder = st.empty()

# Placeholders in Settings Tab
with tab_settings:
    st.markdown("### 📥 Data Export")
    st.write("Download the granular frame-by-frame data collected during this session.")
    download_placeholder = st.empty()


# --- Processing Loop ---
if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    def update_ui(frame_img, v_count, avg_conf, stat, stat_color, fps, inf_time):
        """Helper to update dynamic UI components smoothly"""
        # Video feed
        output_placeholder.image(frame_img, use_container_width=True)
        
        # Traffic Status Badge
        badge_class = "badge-green" if stat_color == "green" else ("badge-red" if stat_color == "red" else "badge-yellow")
        status_html = f"""
        <div style="background: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 20px; display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #94A3B8; font-weight: 600; text-transform: uppercase; font-size: 0.9rem;">Traffic Status</span>
            <span class="badge {badge_class}">{stat}</span>
        </div>
        """
        status_placeholder.markdown(status_html, unsafe_allow_html=True)
        
        # Metrics
        vehicles_metric_placeholder.markdown(f'<div class="metric-card"><div class="metric-label">Vehicles in Frame</div><div class="metric-value" style="color: #60A5FA;">{v_count}</div></div><br/>', unsafe_allow_html=True)
        conf_metric_placeholder.markdown(f'<div class="metric-card"><div class="metric-label">Avg Confidence</div><div class="metric-value">{avg_conf:.2f}</div></div><br/>', unsafe_allow_html=True)
        fps_metric_placeholder.markdown(f'<div class="metric-card"><div class="metric-label">Live FPS</div><div class="metric-value" style="color: #A78BFA;">{fps:.1f}</div></div>', unsafe_allow_html=True)
        inf_metric_placeholder.markdown(f'<div class="metric-card"><div class="metric-label">Inference Time</div><div class="metric-value">{inf_time*1000:.1f} ms</div></div>', unsafe_allow_html=True)
        
        # Insights
        insight_msg1 = "High vehicle density. Possible congestion ahead." if stat_color == "red" else "Traffic is flowing smoothly."
        insight_msg2 = f"Currently tracking {st.session_state.analytics.get_summary_metrics()[2]} unique vehicles." if use_tracking else f"{v_count} vehicles detected in current view."
        
        insights_html = f"""
        <div class="insights-panel">
            <h5 style="color: #F8FAFC; margin-top: 0; margin-bottom: 15px;">🤖 AI Insights</h5>
            <div class="insight-item"><span class="insight-icon">🚦</span> <span>{insight_msg1}</span></div>
            <div class="insight-item"><span class="insight-icon">🔍</span> <span>{insight_msg2}</span></div>
        </div>
        """
        insights_placeholder.markdown(insights_html, unsafe_allow_html=True)
        
    if file_type in ['jpg', 'jpeg', 'png']:
        # Image Processing
        image = Image.open(uploaded_file)
        cv2_img = pil_to_cv2(image)
        start_time = time.time()
        
        processed_img = preprocess_image(cv2_img, apply_blur)
        annotated_img, detections = detect_vehicles(processed_img, conf_threshold, use_tracking=False, draw_boxes=draw_boxes)
        status, color, avg_conf = analyze_traffic(detections)
        vehicle_count = len(detections)
        inference_time = time.time() - start_time
        
        st.session_state.frame_count += 1
        st.session_state.analytics.add_frame_data(
            st.session_state.frame_count, detections, status, 0, inference_time
        )
        
        update_ui(cv2_to_pil(annotated_img), vehicle_count, avg_conf, status, color, 0, inference_time)
        
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
            annotated_img, detections = detect_vehicles(processed_img, conf_threshold, use_tracking=use_tracking, draw_boxes=draw_boxes)
            status, color, avg_conf = analyze_traffic(detections)
            vehicle_count = len(detections)
            
            inference_time = time.time() - start_time
            fps = 1.0 / inference_time if inference_time > 0 else 0
            
            st.session_state.frame_count += 1
            st.session_state.analytics.add_frame_data(
                st.session_state.frame_count, detections, status, fps, inference_time
            )
            
            rgb_frame = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
            update_ui(rgb_frame, vehicle_count, avg_conf, status, color, fps, inference_time)
            
            # Update Charts periodically
            if st.session_state.frame_count % 5 == 0:
                trend_chart = st.session_state.analytics.get_trend_chart()
                if trend_chart:
                    trend_placeholder.plotly_chart(trend_chart, use_container_width=True, key=f"trend_{st.session_state.frame_count}")
                    
                dist_chart = st.session_state.analytics.get_class_distribution_chart()
                if dist_chart:
                    dist_placeholder.plotly_chart(dist_chart, use_container_width=True, key=f"dist_{st.session_state.frame_count}")
                    
            time.sleep(0.01)
        cap.release()
        
    # Post Processing Updates
    trend_chart = st.session_state.analytics.get_trend_chart()
    if trend_chart:
        trend_placeholder.plotly_chart(trend_chart, use_container_width=True)
        
    dist_chart = st.session_state.analytics.get_class_distribution_chart()
    if dist_chart:
        dist_placeholder.plotly_chart(dist_chart, use_container_width=True)
        
    csv = st.session_state.analytics.get_csv()
    if csv:
        download_placeholder.download_button(
            label="📄 Download Analytics CSV",
            data=csv,
            file_name="traffic_analytics_report.csv",
            mime="text/csv",
            use_container_width=True
        )
else:
    with tab_dash:
        st.info("👈 Please upload an image or video from the sidebar to initialize the dashboard.")
