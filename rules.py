def analyze_traffic(detections):
    \"\"\"
    Applies rule-based logic to determine traffic status based on detections.
    \"\"\"
    vehicle_count = len(detections)
    
    if vehicle_count == 0:
        return \"No Traffic\", \"red\", 0.0
        
    avg_confidence = sum(d['confidence'] for d in detections) / vehicle_count
    
    if avg_confidence < 0.5:
        status = \"Low Confidence Detection\"
        color = \"orange\"
    elif vehicle_count > 5:
        status = \"High Traffic\"
        color = \"red\"
    else:
        status = \"Normal Traffic\"
        color = \"green\"
        
    return status, color, avg_confidence
