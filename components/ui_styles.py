import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        /* Dark Theme Base - Professional Data Product Look */
        .stApp {
            background-color: #121212;
            color: #E5E7EB;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* Hide Streamlit default branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Layout styling */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1440px;
        }

        /* Titles */
        .main-header {
            font-size: 2rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            margin-bottom: 4px;
            color: #F9FAFB;
        }
        .sub-header {
            font-size: 1rem;
            font-weight: 400;
            color: #9CA3AF;
            margin-top: 0px;
            margin-bottom: 24px;
        }
        hr {
            margin-top: 8px;
            margin-bottom: 24px;
            border-color: #374151;
        }

        /* Custom Metric Cards */
        .metric-card {
            background: #1F2937;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            text-align: left;
            transition: border-color 0.15s ease;
        }
        .metric-card:hover {
            border-color: #4B5563;
        }
        .metric-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #9CA3AF;
            margin-bottom: 4px;
            font-weight: 600;
        }
        .metric-value {
            font-size: 2.25rem;
            font-weight: 400;
            color: #F3F4F6;
            line-height: 1.2;
        }
        
        /* Traffic Badges */
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .badge-green { background-color: rgba(16, 185, 129, 0.1); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.2); }
        .badge-red { background-color: rgba(239, 68, 68, 0.1); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.2); }
        .badge-yellow { background-color: rgba(245, 158, 11, 0.1); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.2); }
        
        /* Insights Panel */
        .insights-panel {
            background: #1F2937;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 24px;
            margin-top: 16px;
        }
        .insight-item {
            display: flex;
            align-items: center;
            background: #111827;
            padding: 14px 16px;
            border-radius: 6px;
            margin-bottom: 12px;
            font-size: 0.95rem;
            color: #D1D5DB;
            border-left: 3px solid #6366F1;
        }
        .insight-item:last-child {
            margin-bottom: 0;
        }
        .insight-icon {
            margin-right: 14px;
            font-size: 1.1rem;
        }
        
        /* Streamlit overrides */
        .stButton>button {
            border-radius: 6px;
            font-weight: 500;
            border: 1px solid #4B5563;
            background: #1F2937;
            color: #E5E7EB;
        }
        .stButton>button:hover {
            border-color: #6B7280;
            color: #FFFFFF;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 48px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 0;
            color: #9CA3AF;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            color: #F9FAFB !important;
            border-bottom-color: #6366F1 !important;
        }
    </style>
    """, unsafe_allow_html=True)
