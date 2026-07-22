import cv2
from ultralytics import YOLO

# Load YOLOv8 model (using the small version for speed)
model = YOLO('yolov8n.pt')

# COCO dataset class IDs for vehicles
VEHICLE_CLASSES = [2, 3, 5, 7]  # 2: car, 3: motorcycle, 5: bus, 7: truck

def detect_vehicles(image, conf_threshold=0.5):
    \"\"\"
    Detects vehicles in the image using YOLOv8.
    \"\"\"
    # Run YOLOv8 inference
    results = model(image, conf=conf_threshold, classes=VEHICLE_CLASSES, verbose=False)
    
    detections = []
    annotated_image = image.copy()
    
    # Check if we have results and process them
    if len(results) > 0:
        result = results[0]
        boxes = result.boxes
        
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            class_name = model.names[cls]
            
            detections.append({
                'class': class_name,
                'confidence': conf,
                'bbox': [x1, y1, x2, y2]
            })
            
            # Draw bounding box and label
            label = f\"{class_name}: {conf:.2f}\"
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_image, label, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
    return annotated_image, detections
