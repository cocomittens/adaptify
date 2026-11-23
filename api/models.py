from django.db import models


class Emotion(models.Model):
    """Local store for detected emotions, used when Supabase isn't configured."""
    user_id = models.CharField(max_length=64)
    emotion = models.CharField(max_length=32)
    confidence = models.FloatField()
    created_at = models.DateTimeField()

    class Meta:
        ordering = ['created_at']
