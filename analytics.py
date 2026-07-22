import pandas as pd
import plotly.express as px

class TrafficAnalytics:
    def __init__(self):
        self.history = []
        
    def add_frame_data(self, frame_id, vehicle_count, avg_confidence, status):
        """Adds analytics data for a single frame."""
        self.history.append({
            'Frame': frame_id,
            'Vehicle Count': vehicle_count,
            'Avg Confidence': avg_confidence,
            'Status': status
        })
        
    def get_trend_chart(self):
        """Generates a plotly chart for vehicle count trend."""
        if not self.history:
            return None
            
        df = pd.DataFrame(self.history)
        
        fig = px.line(df, x='Frame', y='Vehicle Count', 
                      title='Traffic Trend Over Time',
                      markers=True,
                      color_discrete_sequence=['#1f77b4'])
                      
        fig.update_layout(
            xaxis_title="Frame Number",
            yaxis_title="Number of Vehicles",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
        
    def reset(self):
        """Resets the analytics history."""
        self.history = []
