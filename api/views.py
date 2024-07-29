from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .util.supabase_client import supabase
from datetime import datetime
import os
from decouple import config
from django.views.decorators.csrf import csrf_exempt
import joblib
import json

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'text_emotion/models', 'emotion_classifier_pipe_lr.pkl')
DEMO_USER_ID = config('DEMO_USER_ID')

with open(MODEL_PATH, 'rb') as file:
    model = joblib.load(file)

def predict_emotions(text):
    results = model.predict([text])
    return results[0]

def get_prediction_proba(text):
    results = model.predict_proba([text])
    return results.max()

@csrf_exempt
def detect_emotion_text(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        text = data.get('text')

        emotion = predict_emotions(text)
        confidence = get_prediction_proba(text)

        supabase.from_('Emotions').insert([{ 'user_id': DEMO_USER_ID, 'emotion': emotion, 'confidence': confidence, 'created_at': datetime.now().isoformat() }]).execute()
        return JsonResponse({'emotion': emotion, 'confidence': confidence})
    elif request.method == 'GET':
        response = supabase.from_('Emotions').select('*').execute()
        return JsonResponse(response.data, safe=False)    
    else:
        return HttpResponseBadRequest("Only POST method is allowed")