import json

from django.test import TestCase

from .models import Emotion


class DetectEmotionTextTests(TestCase):
    def post(self, payload):
        return self.client.post('/api/text/', json.dumps(payload), content_type='application/json')

    def test_returns_emotion_and_probabilities_and_saves(self):
        response = self.post({'text': "I can't believe they cancelled my flight again. I'm furious."})
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['emotion'], 'anger')
        self.assertAlmostEqual(sum(body['probabilities'].values()), 1.0, places=5)
        self.assertEqual(body['confidence'], body['probabilities']['anger'])
        self.assertEqual(Emotion.objects.count(), 1)

    def test_save_false_does_not_record(self):
        response = self.post({'text': 'what a wonderful day', 'save': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Emotion.objects.count(), 0)

    def test_rejects_missing_text(self):
        self.assertEqual(self.post({}).status_code, 400)
        self.assertEqual(self.post({'text': '   '}).status_code, 400)

    def test_lists_saved_emotions(self):
        self.post({'text': 'what a wonderful day'})
        rows = self.client.get('/api/text/').json()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['emotion'], 'joy')
