def generate_insights(analytics):
    """
    Analyzes the current traffic data and historical trends to generate human-readable insights.
    Returns a list of dicts with 'icon' and 'message'.
    """
    insights = []
    
    # 1. Traffic behavior insight
    behavior = analytics.get_traffic_behavior()
    if behavior == "Increasing":
        insights.append({"icon": "📈", "message": "Traffic volume is increasing rapidly. Possible congestion ahead."})
    elif behavior == "Decreasing":
        insights.append({"icon": "📉", "message": "Traffic volume is decreasing. Flow is clearing up."})
    else:
        insights.append({"icon": "➡️", "message": "Traffic volume is stable."})
        
    # 2. Confidence stability insight
    stability = analytics.get_confidence_stability()
    if stability == "Fluctuating":
        insights.append({"icon": "⚠️", "message": "Detection confidence is unstable. Consider adjusting camera angle or threshold."})
    else:
        insights.append({"icon": "✅", "message": "System performing consistently with high confidence."})
        
    # 3. Class specific insights
    df = analytics.get_dataframe()
    if len(df) > 0:
        latest = df.iloc[-1]
        heavy_vehicles = latest.get('Trucks', 0) + latest.get('Buses', 0)
        if heavy_vehicles > 2:
            insights.append({"icon": "🚛", "message": f"High number of heavy vehicles ({heavy_vehicles}) detected in current frame."})
            
    return insights
