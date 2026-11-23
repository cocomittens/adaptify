import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Emotion

EMOTIONS = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'shame', 'surprise']


class Command(BaseCommand):
    help = 'Add sample emotion history to the local database so the dashboard has data to show.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=120)
        parser.add_argument('--days', type=int, default=30)

    def handle(self, *args, **options):
        now = timezone.now()
        Emotion.objects.bulk_create([
            Emotion(
                user_id='demo',
                emotion=random.choice(EMOTIONS),
                confidence=round(random.uniform(0.35, 0.95), 3),
                created_at=now - timedelta(minutes=random.randint(0, options['days'] * 24 * 60)),
            )
            for _ in range(options['count'])
        ])
        self.stdout.write(self.style.SUCCESS(f"Added {options['count']} sample emotions."))
