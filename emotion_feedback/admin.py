from django.contrib import admin
from .models import UserFeedback, EmotionFeedback, FeedbackSession, EmotionImage

admin.site.register(UserFeedback)
admin.site.register(EmotionFeedback)
admin.site.register(FeedbackSession)
admin.site.register(EmotionImage)