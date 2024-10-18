from django.urls import path
from Aeropulse import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', views.home, name='home'),
    path('symptoms/', views.symptoms, name='symptoms'),
    path('oximeter/', views.oximeter, name='oximeter'),
    path('thermometer/', views.thermometer, name='thermometer'),
    path('depart/', views.depart, name='depart'),
]
urlpatterns += staticfiles_urlpatterns()
