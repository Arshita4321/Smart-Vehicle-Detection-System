import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class TrafficAnalytics:
    def __init__(self):
        self.history = []
        self.unique_vehicles = set()
        
    def add_frame_data(self, frame_id, detections, status, fps, inference_time):
        """Adds analytics data for a single frame, storing granular data."""
        vehicle_count = len(detections)
        avg_conf = sum(d['confidence'] for d in detections) / vehicle_count if vehicle_count > 0 else 0
        
        # Count classes for this frame
        class_counts = {'car': 0, 'truck': 0, 'bus': 0, 'motorcycle': 0}
        for d in detections:
            cls = d['class']
            if cls in class_counts:
                class_counts[cls] += 1
            if 'track_id' in d and d['track_id'] is not None:
                self.unique_vehicles.add(d['track_id'])
                
        self.history.append({
            'Frame': frame_id,
            'Vehicle Count': vehicle_count,
            'Avg Confidence': avg_conf,
            'Status': status,
            'FPS': fps,
            'Inference Time': inference_time,
            'Cars': class_counts['car'],
            'Trucks': class_counts['truck'],
            'Buses': class_counts['bus'],
            'Motorcycles': class_counts['motorcycle']
        })
        
    def get_trend_chart(self):
        """Generates a smoothed area chart for vehicle count trend."""
        if not self.history:
            return None
            
        df = pd.DataFrame(self.history)
        
        # Smoothed moving average for a cleaner look
        df['Smoothed Count'] = df['Vehicle Count'].rolling(window=max(1, len(df)//20), min_periods=1).mean()
        
        fig = px.area(df, x='Frame', y='Smoothed Count', 
                      title='Traffic Density Trend',
                      color_discrete_sequence=['rgba(67, 160, 71, 0.6)'])
                      
        fig.add_trace(go.Scatter(x=df['Frame'], y=df['Vehicle Count'], 
                                 mode='lines', opacity=0.3, name='Raw Count', line=dict(color='gray')))
                                 
        fig.update_layout(
            xaxis_title="Frame Number",
            yaxis_title="Vehicles",
            template="plotly_dark", # Modern dark template
            margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        return fig
        
    def get_class_distribution_chart(self):
        """Generates a donut chart for vehicle class distribution."""
        if not self.history:
            return None
            
        df = pd.DataFrame(self.history)
        totals = {
            'Cars': df['Cars'].sum(),
            'Trucks': df['Trucks'].sum(),
            'Buses': df['Buses'].sum(),
            'Bikes': df['Motorcycles'].sum()
        }
        
        # Filter out 0 counts
        labels = [k for k, v in totals.items() if v > 0]
        values = [v for v in totals.values() if v > 0]
        
        if not values:
            return None
            
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
        fig.update_layout(
            title="Vehicle Class Distribution",
            template="plotly_dark",
            margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        return fig

    def get_summary_metrics(self):
        if not self.history:
            return 0, 0, 0
        df = pd.DataFrame(self.history)
        avg_fps = df['FPS'].mean()
        avg_inf = df['Inference Time'].mean()
        return avg_fps, avg_inf, len(self.unique_vehicles)

    def get_csv(self):
        """Returns the history data as a CSV string."""
        if not self.history:
            return ""
        return pd.DataFrame(self.history).to_csv(index=False)
        
    def reset(self):
        self.history = []
        self.unique_vehicles = set()
