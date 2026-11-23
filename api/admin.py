from django.contrib import admin

from .models import Emotion


@admin.register(Emotion)
class EmotionAdmin(admin.ModelAdmin):
    list_display = ('emotion', 'confidence', 'user_id', 'created_at')
    list_filter = ('emotion',)
