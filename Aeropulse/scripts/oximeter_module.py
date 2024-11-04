# oximeter_module.py

import cv2
import pytesseract
import datetime
import csv
import os
import threading

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OximeterModule:

    def __init__(self, csv_filename="readings.csv"):
        
        self.cap = None
        self.csv_filename = csv_filename
        self.reading_count = 0
        self.max_readings = 20
        self._initialize_csv()

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
        if self.cap:
            self.cap.release()
        # cv2.destroyAllWindows()
        print("Camera stopped.")

    def save_reading_to_csv(self, spo2, pr):
        """Save SpO2 and PR readings to the CSV file with a timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, spo2, pr])
        print(f"Reading saved: SpO2={spo2}%, PR={pr} bpm at {timestamp}")

    def detect_readings(self, frame):
        """Detect and extract SpO2 and PR readings from oximeter display in a frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresholded = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY)
        # cv2.imshow("ROI", thresholded)

        x, y, w, h = 0, 0, 637, 480
        roi = thresholded[y:y+h, x:x+w]

        device_text = pytesseract.image_to_string(roi, config='--psm 6')
        print(f"Extracted Text (oximeter): {device_text}")

        readings = ''.join(filter(str.isdigit, device_text))
        spo2, pr = None, None
        if len(readings) >= 4:
            spo2 = int(readings[:2])
            pr = int(readings[2:4])

        return spo2, pr

    def capture_and_process(self):
        """Capture frames from the camera, detect readings, display them, and save to CSV."""
        if not self.cap:
            raise Exception("Camera has not been started.")

        while self.reading_count < self.max_readings:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame from camera. Exiting...")
                break

            # Draw rectangle around the oximeter display area
            oximeter_x, oximeter_y, oximeter_w, oximeter_h = 0, 0, 637, 480
            cv2.rectangle(frame, (oximeter_x, oximeter_y), (oximeter_x + oximeter_w, oximeter_y + oximeter_h), (0, 255, 0), 2)
            cv2.putText(frame, "Oximeter Reading", (oximeter_x - 20, oximeter_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Detect readings
            spo2_reading, pr_reading = self.detect_readings(frame)
            if spo2_reading is not None and pr_reading is not None:
                # Save the readings to CSV
                self.save_reading_to_csv(spo2_reading, pr_reading)
                self.reading_count += 1
                print(f"Reading {self.reading_count}/{self.max_readings} captured and stored.")
                
                # Display the readings on the frame
                cv2.putText(frame, f"SpO2: {spo2_reading}%", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"PR: {pr_reading} bpm", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Display the frame
            # cv2.imshow("Device Reading Capture", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exit key pressed.")
                break

        self.stop_camera()

def gen(camera): # generates frames in the format of http response, to stream to webpage
        
        while True:
            try:
                frame = camera.get_frame()
                yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            except:
                break