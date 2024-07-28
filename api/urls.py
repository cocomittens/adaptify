from django.urls import path
from .views import detect_emotion_text

urlpatterns = [
    path('text/', detect_emotion_text, name='detect_emotion_text'),
]