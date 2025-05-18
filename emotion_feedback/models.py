from django.db import models
from django.conf import settings
from accounts.models import Product

class FeedbackSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.session_id}"

class EmotionFeedback(models.Model):
    session = models.ForeignKey(FeedbackSession, on_delete=models.CASCADE)
    emotion = models.CharField(max_length=50)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.emotion} ({self.confidence:.2f}%)"

class UserFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(FeedbackSession, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    emotion = models.CharField(max_length=50, null=True, blank=True)
    emotion_image = models.CharField(max_length=255, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username} - Rating: {self.rating}"

class EmotionImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='emotion_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Emotion image from {self.user.username if self.user else 'Anonymous'} at {self.created_at}"
