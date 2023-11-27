import cv2
import multiprocessing
from ultralytics import YOLO
from send_email import send
import supervision as sv
import torch
import numpy as np



device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print(device)
#n,s,m,l,x
model = YOLO('yolov8m.pt')
model.to(device)

def capture_and_display(camera_source, window_name,restructed_area):
    cap = cv2.VideoCapture(camera_source)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    zone = sv.PolygonZone(polygon=restructed_area, frame_resolution_wh=(frame_width,frame_height))
    zone_annotator = sv.PolygonZoneAnnotator(zone=zone, color=sv.Color.white(), thickness=6, text_thickness=6, text_scale=4)
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=1,
        text_scale=0.5
    )
    check=False
    #cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        print(f"Camera {camera_source} not found.")
        return
    while True:
        ret, frame = cap.read()    
        if not ret:
            break
        results = model(frame,classes=[15,16,2,7,0,5,3], conf=0.4)[0]
        detections = sv.Detections.from_yolov8(results)
        labels = [
            f"{model.model.names[class_id]} {confidence:0.2f}"
            for _, _,confidence, class_id, _
            in detections
        ]

        frame = box_annotator.annotate(
            scene=frame, 
            detections=detections,
            labels=labels
        )

        zone.trigger(detections=detections)

        if any(zone.trigger(detections=detections)):
            if check==False:
              inner_process = multiprocessing.Process(target=send(results.boxes.cls))
              inner_process.start()
              check=True
        else :
            check=False
        
        frame=zone_annotator.annotate(scene=frame)
        cv2.imshow(window_name, frame)     
        

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow(window_name)

if __name__ == "__main__":
    file_path = 'information.txt'  # Replace with the path to your text file
    processes = [] 
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 3:
                numbers = np.array([int(part) for part in parts[2:]])
                restructed_area = numbers.reshape(-1, 2)
            window_name = parts[1]
            source=parts[0]
            #restructed_area=np.array([[int(words[2]), int(words[3])],[int(words[4]), int(words[5])],[int(words[6]), int(words[7])],[int(words[8]), int(words[9])],[int(words[10]), int(words[11])],[int(words[12]), int(words[13])]])                                                                                                                                                                   
            process = multiprocessing.Process(target=capture_and_display, args=(source, window_name,restructed_area))
            processes.append(process)
            process.start()

    for process in processes:
        process.join()
