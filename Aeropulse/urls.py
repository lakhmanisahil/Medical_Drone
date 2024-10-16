from django.urls import path
from Aeropulse import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', views.home, name='home'),
    path('symptoms/', views.symptoms, name='symptoms'),
    path('oximeter/', views.oximeter, name='symptoms'),
    path('thermometer/', views.thermometer, name='symptoms'),
]
urlpatterns += staticfiles_urlpatterns()
