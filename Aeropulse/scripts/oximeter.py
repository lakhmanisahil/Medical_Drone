import cv2
import pytesseract
import datetime
import csv
import os

# Set up Tesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path if needed

# Initialize camera
cap = cv2.VideoCapture(0)  # Change the index if you have multiple cameras

# Initialize CSV file for readings
readings_csv = "readings.csv"

# Check if CSV file exists; if not, create it and write headers
if not os.path.isfile(readings_csv):
    with open(readings_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "SpO2 Reading (%)", "PR Reading (bpm)"])

def save_reading_to_csv(spo2, pr):
    """Function to save SpO2 and PR readings to the CSV file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(readings_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, spo2, pr])
    print(f"Reading saved: SpO2={spo2}%, PR={pr} bpm at {timestamp}")

def detect_readings(frame):
    """Detect and extract SpO2 and PR readings from oximeter."""
    
    # Convert the frame to grayscale and threshold it
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY)
    cv2.imshow("ROI", thresholded) 

    # Define ROI for oximeter
    x, y, w, h = 200, 200, 200, 100  # Adjust for oximeter display
    roi = thresholded[y:y+h, x:x+w]
    
    # Extract text from the ROI using Tesseract
    device_text = pytesseract.image_to_string(roi, config='--psm 6')
    print(f"Extracted Text (oximeter): {device_text}")

    # Initialize readings
    spo2, pr = None, None

    # Process oximeter text to separate SpO2 and PR readings
    readings = ''.join(filter(str.isdigit, device_text))  # Keep only digits
    if len(readings) >= 4:  # Ensure we have enough digits
        spo2 = int(readings[:2])  # First two digits for SpO2
        pr = int(readings[2:4])   # Next two digits for PR

    return spo2, pr

# Reading counter
reading_count = 0
max_readings = 20  # Stop after 20 readings

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame from camera. Exiting...")
        break

    # Define ROI for oximeter
    oximeter_x, oximeter_y, oximeter_w, oximeter_h = 200, 200, 200, 100

    # Draw boundary for the ROI
    cv2.rectangle(frame, (oximeter_x, oximeter_y), (oximeter_x + oximeter_w, oximeter_y + oximeter_h), (0, 255, 0), 2)
    cv2.putText(frame, "Oximeter Reading", (oximeter_x - 20, oximeter_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.imshow("Device Reading Capture", frame)

    # Detect readings and save to CSV
    spo2_reading, pr_reading = detect_readings(frame)
    if spo2_reading is not None and pr_reading is not None:
        save_reading_to_csv(spo2_reading, pr_reading)
        reading_count += 1
        print(f"Reading {reading_count}/{max_readings} captured and stored.")
        
        # Stop after 20 readings
        if reading_count >= max_readings:
            print("Max readings reached. Exiting...")
            break

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
