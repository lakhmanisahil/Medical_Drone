from django.shortcuts import render, redirect
from os import path, system

from django.views.decorators import gzip
from django.http import StreamingHttpResponse

from Aeropulse.scripts.oximeter_module import *
import csv

# import sys
OXIMETER = OximeterModule()
OXIMETER.start_camera()


# Create your views here.
def home(request):
    
    # try:
    #     if not OXIMETER.cap.isOpened():
    #         OXIMETER.start_camera()
    # except:
    #         OXIMETER.start_camera()

    return render(request, 'base.html', {})

def symptoms(request):
    Fracture =  "Fracture" in request.GET
    Injury = "Injury" in request.GET
    JointDislocation = "JointDislocation" in request.GET
    Swelling = "Swelling" in request.GET
    Wound = "Wound" in request.GET
    Fine = "Fine" in request.GET

    # timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("symptoms.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Fracture", "Injury", "JointDislocation", "Swelling", "Wound", "Fine"])
        writer.writerow([Fracture, Injury, JointDislocation, Swelling, Wound, Fine])
    print(f"Reading saved")
    
    return home(request)

def oximeter(request):
    # system(r"python Aeropulse/scripts/oximeter.py")
    threading.Thread(target=OXIMETER.capture_and_process(), args=()).start()
    
    print("Oximeter is clicked")
    return redirect("home")

def thermometer(request):
    print("Thermometer is clicked")
    return redirect("home")

# def cancel(request):
#     print("Cancel is clicked")
#     return redirect("home")

def depart(request):
    OXIMETER.stop_camera()
    system(r'''ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{base_mode: 0, custom_mode: 'RTL'}"''')
    print("Depart is clicked")
    return redirect("home")

@gzip.gzip_page
def camera(request): # A page at /camera which is basically a pic of current frame
    try:
        return StreamingHttpResponse(gen(OXIMETER), content_type="multipart/x-mixed-replace;boundary=frame")
    except:  # This is bad!
        pass