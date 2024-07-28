from django.urls import path
from .views import detect_emotion

urlpatterns = [
    path('text/', detect_emotion, name='detect_emotion'),
]