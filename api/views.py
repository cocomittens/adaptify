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

def predict_probabilities(text):
    """Probability of each emotion for the text, as {emotion: probability}."""
    results = model.predict_proba([text])[0]
    return {str(emotion): float(p) for emotion, p in zip(model.classes_, results)}

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
            data = json.loads(request.body.decode('utf-8'))
            text = data.get('text')
        except (ValueError, AttributeError):
            data, text = {}, None
        if not isinstance(text, str) or not text.strip():
            return HttpResponseBadRequest('Request body must be JSON with a non-empty "text" string')

        probabilities = predict_probabilities(text)
        emotion = max(probabilities, key=probabilities.get)
        confidence = probabilities[emotion]

        # "save": false analyzes without recording, e.g. for previews while typing.
        if data.get('save', True):
            save_emotion(emotion, confidence)
        return JsonResponse({'emotion': emotion, 'confidence': confidence, 'probabilities': probabilities})
    elif request.method == 'GET':
        return JsonResponse(list_emotions(), safe=False)
    else:
        return HttpResponseBadRequest("Only GET and POST methods are allowed")
