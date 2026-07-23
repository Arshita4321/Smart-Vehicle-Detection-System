import streamlit as st

def render_insights_panel(insights_list):
    if not insights_list:
        return
        
    html = '<div class="insights-panel">'
    html += '<h4 style="color: #F8FAFC; margin-top: 0; margin-bottom: 20px; font-weight: 700;">🧠 Intelligence Engine</h4>'
    
    for item in insights_list:
        html += f'<div class="insight-item"><span class="insight-icon">{item["icon"]}</span><span>{item["message"]}</span></div>'
    
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
