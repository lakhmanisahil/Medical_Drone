# oximeter_module.py

import cv2
import pytesseract
import datetime
import csv
import os
import threading

import time
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OximeterModule:

    def __init__(self, capture_interval=0.5, max_readings=20):
        # Create a unique filename with a timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = f"readings_{timestamp}.csv"
        self.cap = None
        self.capture_interval = capture_interval
        self.max_readings = max_readings
        self.reading_count = 0
        self._initialize_csv()
        self.capturing = False

        # self.video = cv2.VideoCapture(0)

    # Start of section
        # This section is for streaming the video to the webpage

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        try:
            image = self.frame
            _, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()
        except:
            pass

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.cap.read()

    
    
    # end of section

    def _initialize_csv(self):
        """Initialize the CSV file with headers if it doesn't exist."""
        if not os.path.isfile(self.csv_filename):
            with open(self.csv_filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "SpO2 Reading (%)", "PR Reading (bpm)"])

    def start_camera(self):
        """Initialize the camera."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open camera")
        print("Camera started.")
        (self.grabbed, self.frame) = self.cap.read()
        threading.Thread(target=self.update, args=()).start()

    def stop_camera(self):
        """Release the camera and close any open windows."""
        if self.cap.isOpened():
            self.cap.release()
            cv2.destroyAllWindows()
        # cv2.destroyAllWindows()
        print("Camera stopped.")

    def save_reading_to_csv(self, spo2, pr, device_text):
        """Save SpO2 and PR readings to the CSV file with a timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, spo2, f"{pr:.3f}"])
        print(f"Reading saved: SpO2={spo2}%, PR={pr:.3f} bpm at {timestamp}")
        print(f"Extracted Text: {device_text}")

    def detect_readings(self, frame):
        """Detect and extract SpO2 and PR readings from oximeter display in a frame."""
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define color range for filtering light blue color
        lower_color = np.array([90, 50, 200])
        upper_color = np.array([130, 255, 255])
        mask = cv2.inRange(hsv_frame, lower_color, upper_color)

        filtered_frame = cv2.bitwise_and(frame, frame, mask=mask)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            roi = frame[y:y+h, x:x+w]
            device_text = pytesseract.image_to_string(roi, config='--psm 6')

            # Extract and format readings
            readings = ''.join(filter(lambda c: c.isdigit() or c == '.', device_text))
            if len(readings) >= 4:
                try:
                    spo2 = int(readings[:2])
                    pr = float(readings[2:])
                    return spo2, pr, device_text, filtered_frame
                except ValueError:
                    pass

        return None, None, "", filtered_frame

    def capture_and_process(self):
        """Capture frames from the camera, detect readings, and save to CSV."""
        if not self.cap.isOpened():
            print("Camera is not started. Please start the camera first.")
            return
        
        while self.reading_count < self.max_readings:
            if not self.cap.isOpened():
                break
            start_time = time.time()

            # cv2.imshow("Device Reading Capture", self.frame)
            spo2_reading, pr_reading, device_text, filtered_frame = self.detect_readings(self.frame)
            # cv2.imshow("Filtered Color", filtered_frame)

            if spo2_reading is not None and pr_reading is not None:
                self.save_reading_to_csv(spo2_reading, pr_reading, device_text)
                self.reading_count += 1
                print(f"Reading {self.reading_count}/{self.max_readings} captured and stored.")

                if self.reading_count >= self.max_readings:
                    print("Max readings reached. Exiting...")
                    break

            # elapsed_time = time.time() - start_time
            # if elapsed_time < self.capture_interval:
            #     time.sleep(self.capture_interval - elapsed_time)

            # Stop camera if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exit key pressed.")
                break
        
        # self.stop_camera()

def gen(camera): # generates frames in the format of http response, to stream to webpage
        
        while True:
            try:
                frame = camera.get_frame()
                yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            except:
                break