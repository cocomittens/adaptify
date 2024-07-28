from django.shortcuts import render
from django.http import JsonResponse
import os
import pickle

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'emotion_detection', 'model.pkl')

with open(MODEL_PATH, 'rb') as file:
    model = pickle.load(file)

def detect_emotion(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        emotion = model.predict([text])[0]
        return JsonResponse({'emotion': emotion})