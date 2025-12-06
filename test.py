import cv2
import serial
import time
import math
import numpy as np
import easyocr
import re
import threading
import queue
import os
from ultralytics import YOLO
from collections import defaultdict, deque
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# --- CONFIGURATION ---
SPEED_LIMIT_PIXELS = 50
OCR_INTERVAL = 0.5 
SMOOTHING_WINDOW = 6    
MIN_MOVE_DISTANCE = 3   
MAX_PHYSICAL_SPEED = 2000

# --- SUPABASE CONFIGURATION ---
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
SPEED_BUMP_ID = os.getenv('SPEED_BUMP_ID', '')  # UUID of the speed bump to update

# Initialize Supabase client
supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Supabase: {e}")
        supabase = None
else:
    print("Warning: Supabase credentials not found. Set SUPABASE_URL and SUPABASE_KEY environment variables.") 

# --- SETUP ---
# try:
#     arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)
#     time.sleep(2)
# except:
#     arduino = None

model = YOLO("yolov8n.pt") 
print("Initializing OCR Engine...")
reader = easyocr.Reader(['en'], gpu=True) 

# --- THREADING ---
ocr_queue = queue.Queue()
# Format: { track_id: (text, confidence, box_coordinates) }
plate_data = {} 
last_ocr_time = {}

speed_buffers = defaultdict(lambda: deque(maxlen=SMOOTHING_WINDOW))
track_history = {}
# Track cars that have passed (to avoid double counting)
passed_cars = set()  # Set of track_ids that have been counted
car_count = 0  # Total count of cars that have passed
CAR_EXIT_THRESHOLD = 2.0  # Seconds after a car disappears before counting it as passed
last_seen_time = {}  # Track when each car was last seen 

def ocr_worker():
    while True:
        try:
            # We need the track_id and the crop AND the offset (x1, y1) to map it back
            track_id, car_crop, offset_x, offset_y = ocr_queue.get(timeout=1) 
        except queue.Empty:
            continue

        try:
            # detail=1 gives us [ [box_coords], text, confidence ]
            results = reader.readtext(car_crop, detail=1)
            
            for (bbox, text, prob) in results:
                clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
                
                # Filter for likely plate text (e.g., > 3 chars, mostly uppercase)
                if len(clean_text) > 3 and prob > 0.4:
                    
                    # Convert OCR box points to Main Frame coordinates
                    # bbox is [[tl_x, tl_y], [tr_x, tr_y], [br_x, br_y], [bl_x, bl_y]]
                    (tl, tr, br, bl) = bbox
                    
                    # Map back to main image: Global X = Offset X + Local X
                    plate_x1 = int(tl[0]) + offset_x
                    plate_y1 = int(tl[1]) + offset_y
                    plate_x2 = int(br[0]) + offset_x
                    plate_y2 = int(br[1]) + offset_y
                    
                    # Store data safely
                    # We prioritize MAI plates if found
                    is_mai = "MAI" in clean_text
                    
                    # If we haven't found a plate yet, OR if this one is an Emergency plate
                    current_data = plate_data.get(track_id)
                    
                    if current_data is None or is_mai or (prob > current_data[1] and "MAI" not in current_data[0]):
                        plate_data[track_id] = (clean_text, prob, (plate_x1, plate_y1, plate_x2, plate_y2))
                        
                    if is_mai: break # Stop searching this crop if we found the target
                        
        except Exception as e:
            print(f"OCR Error: {e}")
        
        ocr_queue.task_done()

worker_thread = threading.Thread(target=ocr_worker, daemon=True)
worker_thread.start()

# --- MAIN LOOP ---
cap = cv2.VideoCapture(0)
ret, sample_frame = cap.read()
h_frame, w_frame = sample_frame.shape[:2]

print("System Started. Now highlighting detected plates!")

# Function to update Supabase with car count
def update_supabase_count(count: int):
    if supabase and SPEED_BUMP_ID:
        try:
            current_time = datetime.now(timezone.utc).isoformat()
            result = supabase.table('speed_bumps').update({
                'car_count': count,
                'last_updated': current_time
            }).eq('id', SPEED_BUMP_ID).execute()
            print(f"Updated Supabase: car_count = {count}")
        except Exception as e:
            print(f"Error updating Supabase: {e}")

# Load initial car count from Supabase
if supabase and SPEED_BUMP_ID:
    try:
        result = supabase.table('speed_bumps').select('car_count').eq('id', SPEED_BUMP_ID).execute()
        if result.data and len(result.data) > 0:
            car_count = result.data[0].get('car_count', 0)
            print(f"Loaded initial car count from Supabase: {car_count}")
    except Exception as e:
        print(f"Error loading initial count from Supabase: {e}")

while True:
    ret, frame = cap.read()
    if not ret: break
    
    current_time = time.time()
    results = model.track(frame, persist=True, classes=[2,3,5,7], verbose=False)
    
    display_frame = frame.copy()
    highest_speed_in_frame = 0 
    emergency_vehicle_detected = False
    avg_speed=0

    # Check for cars that have exited (not seen recently)
    current_track_ids = set()
    if results[0].boxes.id is not None:
        current_track_ids = set(results[0].boxes.id.int().cpu().tolist())
    
    # Mark all current cars as seen
    for track_id in current_track_ids:
        last_seen_time[track_id] = current_time
    
    # Check for cars that have exited (not seen for CAR_EXIT_THRESHOLD seconds)
    exited_cars = []
    for track_id, last_seen in list(last_seen_time.items()):
        if track_id not in current_track_ids:
            if current_time - last_seen > CAR_EXIT_THRESHOLD:
                if track_id not in passed_cars:
                    # Calculate the car's average speed before cleaning up
                    car_avg_speed = 0
                    if track_id in speed_buffers and len(speed_buffers[track_id]) > 0:
                        car_avg_speed = sum(speed_buffers[track_id]) / len(speed_buffers[track_id])
                    
                    # Only count and update if the car exceeded the speed limit
                    if car_avg_speed > SPEED_LIMIT_PIXELS:
                        exited_cars.append(track_id)
                        passed_cars.add(track_id)
                        car_count += 1
                        print(f"Car {track_id} passed at {int(car_avg_speed)} px/s (exceeded limit)! Total count: {car_count}")
                        # Update Supabase immediately when a speeding car passes
                        update_supabase_count(car_count)
                    else:
                        # Mark as passed but don't count it
                        passed_cars.add(track_id)
                        print(f"Car {track_id} passed at {int(car_avg_speed)} px/s (within limit) - not counted")
                
                # Clean up tracking data for exited cars
                if track_id in track_history:
                    del track_history[track_id]
                if track_id in speed_buffers:
                    del speed_buffers[track_id]
                if track_id in last_ocr_time:
                    del last_ocr_time[track_id]
                if track_id in plate_data:
                    del plate_data[track_id]
                del last_seen_time[track_id]
    
    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xywh.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        
        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box
            center_x, center_y = float(x), float(y)
            
            # --- 1. STABILIZED SPEED LOGIC ---
            if track_id in track_history:
                prev_x, prev_y, prev_time = track_history[track_id]
                dist = math.sqrt((center_x - prev_x)**2 + (center_y - prev_y)**2)
                time_diff = current_time - prev_time
                if dist < MIN_MOVE_DISTANCE: dist = 0
                if time_diff > 0:
                    raw_speed = dist / time_diff
                    if raw_speed < MAX_PHYSICAL_SPEED:
                        speed_buffers[track_id].append(raw_speed)
            
            avg_speed = sum(speed_buffers[track_id]) / len(speed_buffers[track_id]) if len(speed_buffers[track_id]) > 0 else 0
            track_history[track_id] = (center_x, center_y, current_time)
            if avg_speed > highest_speed_in_frame: highest_speed_in_frame = avg_speed

            # --- 2. OCR DISPATCHER ---
            # Crop logic
            if current_time - last_ocr_time.get(track_id, 0) > OCR_INTERVAL:
                x1 = int(max(0, x - w/2))
                y1 = int(max(0, y - h/2))
                x2 = int(min(w_frame, x + w/2))
                y2 = int(min(h_frame, y + h/2))
                car_crop = frame[y1:y2, x1:x2]
                
                if car_crop.size > 0:
                    # Pass x1, y1 (Offsets) so the thread can calculate global coordinates
                    ocr_queue.put((track_id, car_crop.copy(), x1, y1))
                    last_ocr_time[track_id] = current_time

            # --- 3. VISUALIZATION ---
            # Get Plate Data for this car
            p_text, p_conf, p_box = plate_data.get(track_id, ("Scanning...", 0, None))
            
            is_mai = "MAI" in p_text
            if is_mai: emergency_vehicle_detected = True

            # Determine Colors
            if is_mai:
                main_color = (0, 255, 0) # Green (Emergency)
            elif avg_speed > SPEED_LIMIT_PIXELS:
                main_color = (0, 0, 255) # Red (Speeding)
            else:
                main_color = (255, 255, 0) # Cyan (Safe)

            # Draw Vehicle Box
            cv2.rectangle(display_frame, 
                          (int(x - w/2), int(y - h/2)), 
                          (int(x + w/2), int(y + h/2)), main_color, 2)
            
            # Draw Data Label (Speed)
            cv2.putText(display_frame, f"ID:{track_id} {int(avg_speed)} px/s", 
                        (int(x - w/2), int(y - h/2) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, main_color, 2)

            # Draw LICENSE PLATE Box (If found)
            if p_box is not None:
                px1, py1, px2, py2 = p_box
                # Draw a tight box around the text text
                cv2.rectangle(display_frame, (px1, py1), (px2, py2), (255, 0, 255), 2)
                # Draw the text background for readability
                cv2.rectangle(display_frame, (px1, py1 - 20), (px2, py1), (255, 0, 255), -1)
                cv2.putText(display_frame, p_text, (px1, py1 - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # --- ACTUATOR LOGIC ---
    if emergency_vehicle_detected:
        # if arduino: arduino.write(b'L')
        status, color = "EMERGENCY! BUMP LOWERED", (0, 255, 0)
    elif highest_speed_in_frame > SPEED_LIMIT_PIXELS:
        # if arduino: arduino.write(b'R')
        status, color = "SPEEDING! BUMP RAISED", (0, 0, 255)
    else:
        # if arduino: arduino.write(b'L')
        status, color = "SAFE SPEED", (255, 255, 0)
     # 1. Prepare the command
    command_str = ""
    
    if emergency_vehicle_detected:
        # HACK: Tell C++ speed is 0. 
        # Result: Controller sees "Under Limit" -> Green Light + Flat Bumper.
        command_str = "S:0\n"
        status_msg = "EMERGENCY! CLEARING PATH"
        status_color = (0, 255, 0)
        
    else:
        # Send the actual detected speed
        # We assume 10 pixels/sec roughly equals 1 km/h for the demo scale
        # You might need to tune this divisor (e.g., avg_speed / 5)
        simulated_kmh = int(avg_speed / 10) 
        command_str = f"S:{simulated_kmh}\n"
        
        # Update HUD based on what we *think* the C++ will do
        # (The actual decision happens on the ESP32 now!)
        if simulated_kmh > 50: # Assuming 50 is the hard limit
            status_msg = f"SPEEDING ({simulated_kmh} km/h)"
            status_color = (0, 0, 255)
        else:
            status_msg = f"SAFE ({simulated_kmh} km/h)"
            status_color = (255, 255, 0)

    # 2. Send to ESP32
    # if arduino:
    #     try:
    #         # .encode() converts string to bytes
    #         arduino.write(command_str.encode()) 
    #         print(f"Sent to ESP32: {command_str.strip()}")
    #     except Exception as e:
    #         print(f"Serial Error: {e}")
    #     # HUD
    cv2.putText(display_frame, f"STATUS: {status}", (20, h_frame - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(display_frame, f"CARS PASSED: {car_count}", (20, h_frame - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow('Actibump Plate Detector', display_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()