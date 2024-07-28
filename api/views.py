from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .util.supabase_client import supabase
from datetime import datetime
import os
import pickle

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'text_emotion_detection/models', 'emotion_classifier_pipe_lr.pkl')

with open(MODEL_PATH, 'rb') as file:
    model = pickle.load(file)

@login_required
def detect_emotion_text(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        emotion = model.predict([text])[0]
        confidence = model.predict_proba([text]).max()

        supabase.from_('Emotions').insert([{ 'emotion': emotion, 'confidence': confidence, 'created_at': datetime.now().isoformat() }]).execute()
        return JsonResponse({'emotion': emotion, 'confidence': confidence})