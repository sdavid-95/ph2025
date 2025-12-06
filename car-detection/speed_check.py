import cv2
import dlib
import time
import threading
import math
import serial
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

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

# --- ARDUINO CONFIGURATION ---
# ARDUINO_PORT = os.getenv('ARDUINO_PORT', 'COM3')  # Change to your Arduino port
# ARDUINO_BAUDRATE = 115200
# try:
#     arduino = serial.Serial(port=ARDUINO_PORT, baudrate=ARDUINO_BAUDRATE, timeout=.1)
#     time.sleep(2)
#     print(f"Arduino connected on {ARDUINO_PORT}")
# except Exception as e:
#     print(f"Warning: Could not connect to Arduino on {ARDUINO_PORT}: {e}")
#     arduino = None

# --- SPEED LIMIT CONFIGURATION ---
SPEED_LIMIT_KMH = 55  # Speed limit in km/h

carCascade = cv2.CascadeClassifier('myhaar.xml')
video = cv2.VideoCapture('cars2.mp4')

WIDTH = 1280
HEIGHT = 720


def estimateSpeed(location1, location2):
    d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
    # ppm = location2[2] / carWidth
    ppm = 14
    d_meters = d_pixels / ppm
    #print("d_pixels=" + str(d_pixels), "d_meters=" + str(d_meters))
    fps = 18
    speed = d_meters * fps * 3.6
    return speed


# Function to update Supabase with car count
def update_supabase_count(count: int):
    if not supabase:
        print("[SUPABASE] Warning: Supabase client not initialized, cannot update count")
        return
    if not SPEED_BUMP_ID:
        print("[SUPABASE] Warning: SPEED_BUMP_ID not set, cannot update count")
        return
    
    try:
        current_time = datetime.now(timezone.utc).isoformat()
        print(f"[SUPABASE] Attempting to update: car_count = {count}, time = {current_time}")
        result = supabase.table('speed_bumps').update({
            'car_count': count,
            'last_updated': current_time
        }).eq('id', SPEED_BUMP_ID).execute()
        
        if result.data:
            print(f"[SUPABASE] Successfully updated: car_count = {count}")
        else:
            print(f"[SUPABASE] Update returned no data. Check if speed_bump_id '{SPEED_BUMP_ID}' exists.")
    except Exception as e:
        print(f"[SUPABASE] Error updating Supabase: {e}")
        import traceback
        traceback.print_exc()


# Function to send command to Arduino
def send_arduino_command(command: str):
    """Send command to Arduino: 'R' = Raise, 'S' = Safe, 'E' = Emergency"""
    # Arduino connection is commented out, so this function does nothing
    # if arduino:
    #     try:
    #         arduino.write(command.encode())
    #         print(f"Sent to Arduino: {command}")
    #     except Exception as e:
    #         print(f"Error sending to Arduino: {e}")
    pass


# Load initial car count from Supabase
car_count = 0  # Total count of speeding cars
if supabase and SPEED_BUMP_ID:
    try:
        result = supabase.table('speed_bumps').select('car_count').eq('id', SPEED_BUMP_ID).execute()
        if result.data and len(result.data) > 0:
            car_count = result.data[0].get('car_count', 0)
            print(f"Loaded initial car count from Supabase: {car_count}")
    except Exception as e:
        print(f"Error loading initial count from Supabase: {e}")

# Track last Arduino command to avoid spamming
COMMAND_THROTTLE = 1.0  # Minimum seconds between Arduino commands

def trackMultipleObjects():
    global car_count  # Access global car_count variable
    
    rectangleColor = (0, 255, 0)
    frameCounter = 0
    currentCarID = 0
    fps = 0
    
    carTracker = {}
    carNumbers = {}
    carLocation1 = {}
    carLocation2 = {}
    speed = [None] * 1000
    passed_cars = set()  # Track cars that have been counted
    car_exit_threshold = 30  # Frames after car disappears before counting
    car_exit_counter = {}  # Track frames since car was last seen
    last_arduino_command_local = None  # Track last command sent to Arduino (local to function)
    last_command_time_local = 0  # Track when last command was sent (local to function)
    speeding_cars_seen = set()  # Track cars that have been seen speeding (to ensure they get counted)
    
    # Write output to video file
    out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (WIDTH,HEIGHT))

    while True:
        start_time = time.time()
        rc, image = video.read()
        if type(image) == type(None):
            break
        
        image = cv2.resize(image, (WIDTH, HEIGHT))
        resultImage = image.copy()
        
        frameCounter = frameCounter + 1
        
        carIDtoDelete = []

        for carID in carTracker.keys():
            trackingQuality = carTracker[carID].update(image)
            
            if trackingQuality < 7:
                carIDtoDelete.append(carID)
                
        # Clean up cars that are being removed from tracker
        # Note: Speeding cars are already counted when first detected, so we just mark them as passed
        for carID in carIDtoDelete:
            # Mark as passed (already counted if it was speeding)
            if carID not in passed_cars:
                passed_cars.add(carID)
                if speed[carID] is not None:
                    if speed[carID] > SPEED_LIMIT_KMH:
                        print(f"[TRACKER REMOVAL] Car {carID} removed (was already counted as speeding at {int(speed[carID])} km/h)")
                    else:
                        print(f"[TRACKER REMOVAL] Car {carID} removed at {int(speed[carID])} km/h (within limit - not counted)")
                else:
                    print(f"[TRACKER REMOVAL] Car {carID} removed but speed was never calculated (speed=None)")
            else:
                print(f"[TRACKER REMOVAL] Car {carID} removed (already counted)")
            
            print ('Removing carID ' + str(carID) + ' from list of trackers.')
            print ('Removing carID ' + str(carID) + ' previous location.')
            print ('Removing carID ' + str(carID) + ' current location.')
            carTracker.pop(carID, None)
            carLocation1.pop(carID, None)
            carLocation2.pop(carID, None)
            # Clean up exit counter
            if carID in car_exit_counter:
                car_exit_counter.pop(carID, None)
        
        if not (frameCounter % 10):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))
            
            for (_x, _y, _w, _h) in cars:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)
            
                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h
                
                matchCarID = None
            
                for carID in carTracker.keys():
                    trackedPosition = carTracker[carID].get_position()
                    
                    t_x = int(trackedPosition.left())
                    t_y = int(trackedPosition.top())
                    t_w = int(trackedPosition.width())
                    t_h = int(trackedPosition.height())
                    
                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h
                
                    if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
                        matchCarID = carID
                
                if matchCarID is None:
                    print ('Creating new tracker ' + str(currentCarID))
                    
                    tracker = dlib.correlation_tracker()
                    tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
                    carTracker[currentCarID] = tracker
                    carLocation1[currentCarID] = [x, y, w, h]

                    currentCarID = currentCarID + 1
        
        #cv2.line(resultImage,(0,480),(1280,480),(255,0,0),5)


        # Track currently visible cars
        current_car_ids = set(carTracker.keys())
        
        # Initialize exit counter for all currently tracked cars
        for carID in current_car_ids:
            if carID not in car_exit_counter:
                car_exit_counter[carID] = 0
        
        # Update exit counters and check for exited cars
        # Check all cars that were previously tracked (including those in exit_counter)
        all_previous_cars = set(car_exit_counter.keys())
        
        for carID in list(all_previous_cars):
            if carID in current_car_ids:
                # Car is still visible, reset counter
                car_exit_counter[carID] = 0
            else:
                # Car not visible, increment counter
                car_exit_counter[carID] = car_exit_counter.get(carID, 0) + 1
                
                # If car has been gone long enough, just mark it as passed
                # Note: Speeding cars are already counted when first detected, so we just clean up
                if car_exit_counter[carID] > car_exit_threshold and carID not in passed_cars:
                    # Mark as passed (already counted if it was speeding when detected)
                    passed_cars.add(carID)
                    if speed[carID] is not None:
                        if speed[carID] > SPEED_LIMIT_KMH:
                            print(f"[EXIT COUNTER] Car {carID} exited (was already counted as speeding at {int(speed[carID])} km/h)")
                        else:
                            print(f"[EXIT COUNTER] Car {carID} exited at {int(speed[carID])} km/h (within limit - not counted)")
                    else:
                        print(f"[EXIT COUNTER] Car {carID} exited but speed was never calculated (speed=None)")
                    # Clean up
                    if carID in car_exit_counter:
                        del car_exit_counter[carID]
        
        # Track highest speed in current frame for Arduino commands
        highest_speed = 0
        has_speeding_car = False
        
        for carID in carTracker.keys():
            trackedPosition = carTracker[carID].get_position()
                    
            t_x = int(trackedPosition.left())
            t_y = int(trackedPosition.top())
            t_w = int(trackedPosition.width())
            t_h = int(trackedPosition.height())
            
            # Determine color based on speed
            if speed[carID] is not None:
                if speed[carID] > SPEED_LIMIT_KMH:
                    rectangleColor = (0, 0, 255)  # Red for speeding
                    has_speeding_car = True
                    if speed[carID] > highest_speed:
                        highest_speed = speed[carID]
                    # Count and update Supabase immediately when car is first detected speeding
                    if carID not in passed_cars:
                        passed_cars.add(carID)
                        car_count += 1
                        speeding_cars_seen.add(carID)
                        print(f"[SPEEDING DETECTED] Car {carID} is speeding at {int(speed[carID])} km/h! Total count: {car_count}")
                        # Update Supabase immediately when a speeding car is detected
                        update_supabase_count(car_count)
                else:
                    rectangleColor = (0, 255, 0)  # Green for safe
            else:
                rectangleColor = (255, 255, 0)  # Yellow for unknown
            
            cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 4)
            
            # speed estimation
            carLocation2[carID] = [t_x, t_y, t_w, t_h]
            
            # Initialize exit counter for new cars
            if carID not in car_exit_counter:
                car_exit_counter[carID] = 0
        
        end_time = time.time()
        
        if not (end_time == start_time):
            fps = 1.0/(end_time - start_time)
        
        #cv2.putText(resultImage, 'FPS: ' + str(int(fps)), (620, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)


        # Calculate speed for all tracked cars using carLocation1 and carLocation2
        # Note: carLocation1 uses the same carID as carTracker
        for carID in list(carLocation1.keys()): 
            if frameCounter % 1 == 0:
                if carID not in carLocation2:
                    continue
                    
                [x1, y1, w1, h1] = carLocation1[carID]
                [x2, y2, w2, h2] = carLocation2[carID]
        
                # print 'previous location: ' + str(carLocation1[carID]) + ', current location: ' + str(carLocation2[carID])
                carLocation1[carID] = [x2, y2, w2, h2]
        
                # print 'new previous location: ' + str(carLocation1[carID])
                if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                    if (speed[carID] == None or speed[carID] == 0) and y1 >= 275 and y1 <= 285:
                        calculated_speed = estimateSpeed([x1, y1, w1, h1], [x2, y2, w2, h2])
                        speed[carID] = calculated_speed
                        if calculated_speed > SPEED_LIMIT_KMH:
                            print(f"[SPEED CALC] Car {carID} calculated speed: {int(calculated_speed)} km/h (SPEEDING)")
                        else:
                            print(f"[SPEED CALC] Car {carID} calculated speed: {int(calculated_speed)} km/h (safe)")

                    #if y1 > 275 and y1 < 285:
                    if speed[carID] != None and y1 >= 180:
                        # Color text based on speed
                        text_color = (0, 0, 255) if speed[carID] > SPEED_LIMIT_KMH else (0, 255, 0)
                        cv2.putText(resultImage, str(int(speed[carID])) + " km/hr", (int(x1 + w1/2), int(y1-5)),cv2.FONT_HERSHEY_SIMPLEX, 0.75, text_color, 2)
                        
                    #print ('CarID ' + str(i) + ': speed is ' + str("%.2f" % round(speed[i], 0)) + ' km/h.\n')

                    #else:
                    #    cv2.putText(resultImage, "Far Object", (int(x1 + w1/2), int(y1)),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                        #print ('CarID ' + str(i) + ' Location1: ' + str(carLocation1[i]) + ' Location2: ' + str(carLocation2[i]) + ' speed is ' + str("%.2f" % round(speed[i], 0)) + ' km/h.\n')
        
        # Send commands to Arduino based on detected speeds (throttled)
        current_time_sec = time.time()
        new_command = 'R' if has_speeding_car else 'S'
        
        # Only send if command changed or enough time has passed
        if (new_command != last_arduino_command_local or 
            (current_time_sec - last_command_time_local) > COMMAND_THROTTLE):
            #send_arduino_command(new_command)
            last_arduino_command_local = new_command
            last_command_time_local = current_time_sec
        
        # Display car count on frame
        cv2.putText(resultImage, f"Speeding Cars Count: {car_count}", (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(resultImage, f"Speed Limit: {SPEED_LIMIT_KMH} km/h", (20, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('result', resultImage)
        # Write the frame into the file 'output.avi'
        #out.write(resultImage)


        if cv2.waitKey(33) == 27:
            break
    
    cv2.destroyAllWindows()


if __name__ == '__main__':
    trackMultipleObjects()
