import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Emotion

# Relative frequencies, so the sample data isn't a flat line across emotions.
EMOTION_WEIGHTS = {
    'joy': 26, 'neutral': 22, 'sadness': 14, 'anger': 11,
    'fear': 9, 'surprise': 8, 'disgust': 5, 'shame': 5,
}


class Command(BaseCommand):
    help = 'Add sample emotion history to the local database so the dashboard has data to show.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=120)
        parser.add_argument('--days', type=int, default=30)
        parser.add_argument('--clear', action='store_true', help='Delete existing local emotions first.')

    def handle(self, *args, **options):
        if options['clear']:
            Emotion.objects.all().delete()
        now = timezone.now()
        emotions = random.choices(
            list(EMOTION_WEIGHTS), weights=EMOTION_WEIGHTS.values(), k=options['count']
        )
        Emotion.objects.bulk_create([
            Emotion(
                user_id='demo',
                emotion=emotion,
                confidence=round(random.triangular(0.35, 0.98, 0.75), 3),
                created_at=now - timedelta(minutes=random.randint(0, options['days'] * 24 * 60)),
            )
            for emotion in emotions
        ])
        self.stdout.write(self.style.SUCCESS(f"Added {options['count']} sample emotions."))
