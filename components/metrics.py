import streamlit as st

def render_metrics(vehicles_count, avg_conf, fps, inference_time, delta=0):
    col1, col2 = st.columns(2)
    
    # Delta indicator - subtle text color
    delta_color = "#34d399" if delta > 0 else "#f87171" if delta < 0 else "#6b7280"
    delta_html = f"<div style='color: {delta_color}; font-size: 0.85rem; margin-top: 4px; font-weight: 500;'>{'+' if delta > 0 else ''}{delta} vs prev frame</div>" if delta != 0 else ""
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Vehicles in Frame</div>
            <div class="metric-value">{vehicles_count}</div>
            {delta_html}
        </div>
        <div style="height: 16px;"></div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">System FPS</div>
            <div class="metric-value">{fps:.1f}</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Average Confidence</div>
            <div class="metric-value">{avg_conf:.2f}</div>
        </div>
        <div style="height: 16px;"></div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Inference Latency</div>
            <div class="metric-value">{inference_time*1000:.1f} <span style="font-size: 1rem; color:#9ca3af; font-weight:400;">ms</span></div>
        </div>
        ''', unsafe_allow_html=True)

def render_status_badge(status, color_code):
    badge_class = "badge-green" if color_code == "green" else ("badge-red" if color_code == "red" else "badge-yellow")
    st.markdown(f'''
    <div style="background: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <span style="color: #d1d5db; font-weight: 500; font-size: 0.95rem; letter-spacing: 0.02em;">Real-time Traffic Status</span>
        <span class="badge {badge_class}">{status}</span>
    </div>
    ''', unsafe_allow_html=True)
