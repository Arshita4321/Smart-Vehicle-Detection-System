import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        uploaded_file = st.file_uploader("📂 Input Source", type=['jpg', 'jpeg', 'png', 'mp4'])
        
        st.markdown("---")
        st.markdown("**Detection Settings**")
        conf_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.05)
        
        st.markdown("**Interactive Toggles**")
        draw_boxes = st.toggle("👁️ Show Bounding Boxes", value=True)
        use_tracking = st.toggle("🎯 Unique Vehicle Tracking", value=True)
        
        st.markdown("**Filters**")
        selected_classes = st.multiselect("Filter Vehicle Types", 
                                        ['car', 'truck', 'bus', 'motorcycle'],
                                        default=['car', 'truck', 'bus', 'motorcycle'])
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            play = st.button("▶️ Play/Resume", use_container_width=True)
        with col2:
            pause = st.button("⏸️ Pause", use_container_width=True)
            
        if play:
            st.session_state.is_playing = True
        if pause:
            st.session_state.is_playing = False
            
        st.markdown("---")
        reset_btn = st.button("🔄 Reset Analytics Session", use_container_width=True)
        
    return uploaded_file, conf_threshold, draw_boxes, use_tracking, selected_classes, reset_btn
