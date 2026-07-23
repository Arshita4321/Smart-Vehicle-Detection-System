import cv2
from ultralytics import YOLO

# Load YOLOv8 model (using the small version for speed)
model = YOLO('yolov8n.pt')

# COCO dataset class IDs for vehicles
VEHICLE_CLASSES = [2, 3, 5, 7]  # 2: car, 3: motorcycle, 5: bus, 7: truck

def detect_vehicles(image, conf_threshold=0.5, use_tracking=False, draw_boxes=True):
    """
    Detects (and optionally tracks) vehicles in the image using YOLOv8.
    """
    if use_tracking:
        # persist=True ensures IDs are kept across frames
        results = model.track(image, conf=conf_threshold, classes=VEHICLE_CLASSES, persist=True, tracker="botsort.yaml", verbose=False)
    else:
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
            
            # Extract tracking ID if tracking is enabled and an ID was assigned
            track_id = None
            if use_tracking and box.id is not None:
                track_id = int(box.id[0])
                
            detections.append({
                'class': class_name,
                'confidence': conf,
                'bbox': [x1, y1, x2, y2],
                'track_id': track_id
            })
            
            if draw_boxes:
                # Draw bounding box and label
                label = f"{class_name} {track_id if track_id else ''}: {conf:.2f}"
                
                # Distinct colors for different classes
                color = (0, 255, 0)
                if class_name == 'car': color = (255, 50, 50)
                elif class_name == 'truck': color = (50, 50, 255)
                elif class_name == 'bus': color = (255, 255, 50)
                elif class_name == 'motorcycle': color = (255, 50, 255)
                
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(annotated_image, label, (x1, max(y1 - 10, 10)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        
    return annotated_image, detections
