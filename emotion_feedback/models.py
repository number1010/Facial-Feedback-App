from django.db import models
from django.contrib.auth.models import User

class FeedbackSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.session_id}"

class EmotionFeedback(models.Model):
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('surprised', 'Surprised'),
        ('neutral', 'Neutral'),
        ('fearful', 'Fearful'),
        ('disgusted', 'Disgusted'),
    ]

    session = models.ForeignKey(FeedbackSession, on_delete=models.CASCADE)
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='emotions/', null=True, blank=True)

    def __str__(self):
        return f"{self.emotion} ({self.confidence:.2f})"

class UserFeedback(models.Model):
    session = models.ForeignKey(FeedbackSession, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for session {self.session.session_id}"
