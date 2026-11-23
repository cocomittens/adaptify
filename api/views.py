from django.http import JsonResponse, HttpResponseBadRequest
from .models import Emotion
from .util.supabase_client import supabase
from django.utils import timezone
import os
from decouple import config
from django.views.decorators.csrf import csrf_exempt
import joblib
import json

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'text_emotion/models', 'emotion_classifier_pipe_lr.pkl')
DEMO_USER_ID = config('DEMO_USER_ID', default='demo')

with open(MODEL_PATH, 'rb') as file:
    model = joblib.load(file)

def predict_emotions(text):
    results = model.predict([text])
    return str(results[0])

def get_prediction_proba(text):
    results = model.predict_proba([text])
    return float(results.max())

def save_emotion(emotion, confidence):
    row = {'user_id': DEMO_USER_ID, 'emotion': emotion, 'confidence': confidence, 'created_at': timezone.now().isoformat()}
    if supabase:
        supabase.from_('Emotions').insert([row]).execute()
    else:
        Emotion.objects.create(**row)

def list_emotions():
    if supabase:
        return supabase.from_('Emotions').select('*').execute().data
    return list(Emotion.objects.values('id', 'user_id', 'emotion', 'confidence', 'created_at'))

@csrf_exempt
def detect_emotion_text(request):
    if request.method == 'POST':
        try:
            text = json.loads(request.body.decode('utf-8')).get('text')
        except (ValueError, AttributeError):
            text = None
        if not isinstance(text, str) or not text.strip():
            return HttpResponseBadRequest('Request body must be JSON with a non-empty "text" string')

        emotion = predict_emotions(text)
        confidence = get_prediction_proba(text)

        save_emotion(emotion, confidence)
        return JsonResponse({'emotion': emotion, 'confidence': confidence})
    elif request.method == 'GET':
        return JsonResponse(list_emotions(), safe=False)
    else:
        return HttpResponseBadRequest("Only GET and POST methods are allowed")
