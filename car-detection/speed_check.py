import cv2
import dlib
import time
import math
import serial
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables from .env file
load_dotenv()

# --- SUPABASE CONFIGURATION ---
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
SPEED_BUMP_ID = os.getenv('SPEED_BUMP_ID', '')  # UUID of the speed bump to update

supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Supabase: {e}")
        supabase = None
else:
    print("Warning: Supabase credentials not found. Set SUPABASE_URL and SUPABASE_KEY.")

# --- ARDUINO CONFIGURATION ---
ARDUINO_PORT = "COM3"
ARDUINO_BAUDRATE = 115200
try:
    # Attempt to connect to Arduino
    arduino = serial.Serial(port=ARDUINO_PORT, baudrate=ARDUINO_BAUDRATE, timeout=.1)
    time.sleep(2)  # Wait for Arduino to reset
    print(f"Arduino connected on {ARDUINO_PORT}")
except Exception as e:
    print(f"Warning: Could not connect to Arduino on {ARDUINO_PORT}: {e}")
    arduino = None

# --- SPEED LIMIT CONFIGURATION ---
SPEED_LIMIT_KMH = 35  # Speed limit in km/h

# --- HEALTH DECREASE TRIGGER POINT ---
HEALTH_CHECK_Y_POSITION = 400  # Y-coordinate where health check occurs (adjust based on your video)

# --- VIDEO CONFIGURATION ---
carCascade = cv2.CascadeClassifier('myhaar.xml')  # make sure this exists
video = cv2.VideoCapture('car3.mp4')  # or 0 for webcam

WIDTH = 1280
HEIGHT = 720
video.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

# --- HEALTH (from Supabase) ---
bumper_health = 10000  # Default health (0-10000)
if supabase and SPEED_BUMP_ID:
    try:
        result = supabase.table('speed_bumps').select('health').eq('id', SPEED_BUMP_ID).execute()
        if result.data and len(result.data) > 0:
            bumper_health = int(result.data[0].get('health', 10000))
            print(f"Loaded initial health from Supabase: {bumper_health}")
    except Exception as e:
        print(f"Error loading initial data from Supabase: {e}")


# --- UTILS ---

def get_status_from_health(health: int) -> str:
    """Determine status based on health: Good >= 7000, Damaged 3000-7000, Critical < 3000"""
    if health >= 7000:
        return 'Good'
    elif health >= 3000:
        return 'Damaged'
    else:
        return 'Critical'


def update_supabase_health(health: int):
    """Update health and status in Supabase based on health value"""
    if not supabase:
        print("[SUPABASE] Warning: Supabase client not initialized, cannot update health")
        return
    if not SPEED_BUMP_ID:
        print("[SUPABASE] Warning: SPEED_BUMP_ID not set, cannot update health")
        return

    # Ensure health stays within 0-10000 range
    health = max(0, min(10000, health))
    
    # Determine status based on health
    new_status = get_status_from_health(health)

    try:
        current_time = datetime.now(timezone.utc).isoformat()
        print(f"[SUPABASE] Updating health: health={health}, status={new_status}, time={current_time}")
        result = supabase.table('speed_bumps').update({
            'health': health,
            'status': new_status,
            'last_updated': current_time
        }).eq('id', SPEED_BUMP_ID).execute()

        if result.data:
            print(f"[SUPABASE] Successfully updated: health={health}, status={new_status}")
        else:
            print(f"[SUPABASE] Update returned no data. Check speed_bump_id='{SPEED_BUMP_ID}'.")
    except Exception as e:
        print(f"[SUPABASE] Error updating health: {e}")
        import traceback
        traceback.print_exc()


def send_arduino_command(command: str):
    """Send command to Arduino (here we send speed as text with newline)."""
    if arduino:
        try:
            arduino.write(command.encode())
            print(f"[ARDUINO] Sent: {command.strip()}")
        except Exception as e:
            print(f"[ARDUINO] Error sending: {e}")
    else:
        print(f"[ARDUINO] Not connected, would have sent: {command.strip()}")


def estimate_speed_fast(prev_loc, curr_loc, dt: float) -> float:
    """
    Estimate speed based on movement between two bounding boxes and time delta.
    prev_loc, curr_loc = [x, y, w, h]
    dt = time between frames (seconds)
    """
    (x1, y1, w1, h1) = prev_loc
    (x2, y2, w2, h2) = curr_loc

    # Euclidean distance in pixels (using center-to-center distance)
    center_x1 = x1 + w1 / 2
    center_y1 = y1 + h1 / 2
    center_x2 = x2 + w2 / 2
    center_y2 = y2 + h2 / 2
    
    d_pixels = math.sqrt((center_x2 - center_x1) ** 2 + (center_y2 - center_y1) ** 2)

    if dt <= 0:
        return 0.0

    # pixels → meters (This value is critical for speed calculation)
    # Lower this value to increase detected speeds.
    PIXELS_PER_METER = 35.0
    d_meters = d_pixels / PIXELS_PER_METER

    speed_m_per_s = d_meters / dt
    speed_kmh = speed_m_per_s * 3.6
    return speed_kmh


# --- MAIN TRACKING LOGIC ---

def trackMultipleObjects():
    global bumper_health

    frameCounter = 0

    carTracker: dict[int, dlib.correlation_tracker] = {}
    carLocationPrev: dict[int, list] = {}   # previous bbox per car
    carLastTime: dict[int, float] = {}      # last timestamp per car
    carSpeed: dict[int, float | None] = {}  # smoothed speed per car
    health_decreased_cars: set[int] = set() # cars that already caused health decrease

    currentCarID = 0

    last_arduino_command = None
    last_command_time = 0

    while True:
        start_time = time.time()

        rc, image = video.read()
        if not rc or image is None:
            print("Video finished or cannot read frame.")
            break

        image = cv2.resize(image, (WIDTH, HEIGHT))
        resultImage = image.copy()
        frameCounter += 1

        # Draw health check line
        cv2.line(resultImage, (0, HEALTH_CHECK_Y_POSITION), (WIDTH, HEALTH_CHECK_Y_POSITION), (255, 0, 255), 2)

        # --- UPDATE EXISTING TRACKERS ---
        cars_to_delete = []
        for carID, tracker in carTracker.items():
            trackingQuality = tracker.update(image)
            if trackingQuality < 7:
                cars_to_delete.append(carID)

        for carID in cars_to_delete:
            print(f"[TRACKER] Removing carID {carID}")
            carTracker.pop(carID, None)
            carLocationPrev.pop(carID, None)
            carLastTime.pop(carID, None)
            carSpeed.pop(carID, None)
            # Remove from health set too
            health_decreased_cars.discard(carID) 

        # --- DETECTION EVERY N FRAMES ---
        if frameCounter % 5 == 0:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))

            for (_x, _y, _w, _h) in cars:
                x, y, w, h = int(_x), int(_y), int(_w), int(_h)

                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h

                matchCarID = None

                # Try to match detected bbox with existing trackers
                for carID, tracker in carTracker.items():
                    pos = tracker.get_position()
                    t_x = int(pos.left())
                    t_y = int(pos.top())
                    t_w = int(pos.width())
                    t_h = int(pos.height())

                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h

                    # Simple overlap/center check
                    if (
                        t_x <= x_bar <= t_x + t_w and
                        t_y <= y_bar <= t_y + t_h and
                        x <= t_x_bar <= x + w and
                        y <= t_y_bar <= y + h
                    ):
                        matchCarID = carID
                        break

                if matchCarID is None:
                    print(f"[TRACKER] Creating new tracker {currentCarID}")
                    tracker = dlib.correlation_tracker()
                    # Initialize tracker with the detected bounding box
                    tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
                    carTracker[currentCarID] = tracker
                    carLocationPrev[currentCarID] = [x, y, w, h]
                    carLastTime[currentCarID] = time.time()
                    carSpeed[currentCarID] = None
                    currentCarID += 1

        # --- SPEED, HEALTH & DRAWING ---
        highest_speeding_speed = 0.0 # Tracks the max speed ONLY IF it exceeds the limit
        has_speeding_car = False

        for carID, tracker in carTracker.items():
            pos = tracker.get_position()
            t_x = int(pos.left())
            t_y = int(pos.top())
            t_w = int(pos.width())
            t_h = int(pos.height())

            curr_loc = [t_x, t_y, t_w, t_h]
            now = time.time()

            # Calculate speed if we have a previous location
            if carID in carLocationPrev and carID in carLastTime:
                dt = now - carLastTime[carID]
                if dt > 0.01:  # avoid division by near-zero
                    instant_speed = estimate_speed_fast(carLocationPrev[carID], curr_loc, dt)

                    # Smooth speed
                    if carSpeed[carID] is None:
                        carSpeed[carID] = instant_speed
                    else:
                        alpha = 0.7  # 70% previous, 30% new
                        carSpeed[carID] = alpha * carSpeed[carID] + (1 - alpha) * instant_speed

                    carLocationPrev[carID] = curr_loc
                    carLastTime[carID] = now

            speed_val = carSpeed.get(carID, None)

            # Color based on speed
            if speed_val is None:
                rect_color = (255, 255, 0)  # yellow - unknown yet
                text_color = (255, 255, 255)
            elif speed_val > SPEED_LIMIT_KMH:
                rect_color = (0, 0, 255)  # red
                text_color = (0, 0, 255)
                has_speeding_car = True
                
                # Update highest speeding speed
                if speed_val > highest_speeding_speed:
                    highest_speeding_speed = speed_val

                # Check if car has crossed the health check line and hasn't decreased health yet
                car_center_y = t_y + t_h // 2
                if car_center_y >= HEALTH_CHECK_Y_POSITION and carID not in health_decreased_cars:
                    health_decreased_cars.add(carID)
                    
                    # Damage calculation: use original simple damage
                    original_damage = (speed_val/10)**2
                    
                    bumper_health -= original_damage
                    bumper_health = max(0, bumper_health)
                    print(f"[HEALTH] Car {carID} at {int(speed_val)} km/h caused {original_damage:.2f} damage. New health: {int(bumper_health)}")
                    update_supabase_health(bumper_health)
            else:
                rect_color = (0, 255, 0)  # green
                text_color = (0, 255, 0)

            # Draw bbox
            cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rect_color, 3)

            # Show speed text
            if speed_val is not None:
                cv2.putText(
                    resultImage,
                    f"{int(speed_val)} km/h",
                    (t_x, max(t_y - 5, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    text_color,
                    2
                )

        # --- ARDUINO COMMANDS (THROTTLED) ---
        current_time_sec = time.time()
        if has_speeding_car and highest_speeding_speed > 0:
            new_command = f"{int(highest_speeding_speed)}"
            send_arduino_command(new_command)
            last_arduino_command = new_command
            last_command_time = current_time_sec
        else:
            # reset, so next speeding event will send again
            last_arduino_command = None

        # --- UI OVERLAYS ---
        cv2.putText(
            resultImage,
            f"Speed Limit: {SPEED_LIMIT_KMH} km/h",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        cv2.putText(
            resultImage,
            f"Health: {int(bumper_health)} ({get_status_from_health(int(bumper_health))})",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        end_time = time.time()
        fps = 1.0 / (end_time - start_time) if end_time > start_time else 0
        cv2.putText(
            resultImage,
            f"FPS: {int(fps)}",
            (WIDTH - 150, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.imshow('result', resultImage)

        # ESC to quit
        if cv2.waitKey(1) & 0xFF == 27:
            break

    video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    trackMultipleObjects()