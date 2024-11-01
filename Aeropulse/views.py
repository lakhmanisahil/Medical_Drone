from django.shortcuts import render
from os import path, system

from subprocess import run,PIPE
import sys


# Create your views here.
def home(request):
    return render(request, 'base.html', {})

def symptoms(request):
    Fracture =  "Fracture" in request.GET
    Injury = "Injury" in request.GET
    JointDislocation = "JointDislocation" in request.GET
    Swelling = "Swelling" in request.GET
    Wound = "Wound" in request.GET
    Fine = "Fine" in request.GET
    
    return home(request)

def oximeter(request):
    system(r"python Aeropulse/scripts/oximeter.py")
    print("Oximeter is clicked")
    return home(request)

def thermometer(request):
    print("Thermometer is clicked")
    return home(request)

def depart(request):
    print("Depart is clicked")
    return home(request)

