from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib.auth.decorators import login_required
import json
import uuid
import base64
import numpy as np
import cv2
import os
from .models import FeedbackSession, EmotionFeedback, UserFeedback
from .vit_model import load_vit_model, predict_emotion
from django.urls import reverse

# Định nghĩa các lớp cảm xúc
EMOTIONS = ['angry', 'disgusted', 'fearful', 'happy', 'neutral', 'sad', 'surprised']

# Load pre-trained ViT model
model_path = os.path.join('models', 'vit_b16_fer2013.pth')
if os.path.exists(model_path):
    model = load_vit_model(model_path)
else:
    raise FileNotFoundError(f"Model file not found at {model_path}")

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class HomeView(TemplateView):
    template_name = 'emotion_feedback/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = str(uuid.uuid4())
        session = FeedbackSession.objects.create(session_id=session_id)
        context['session_id'] = session_id
        return context

@method_decorator(csrf_exempt, name='dispatch')
class EmotionCaptureView(TemplateView):
    template_name = 'emotion_feedback/capture.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = str(uuid.uuid4())
        session = FeedbackSession.objects.create(session_id=session_id)
        context['session_id'] = session_id
        return context

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            image_data = data.get('image')
            
            if not session_id:
                return JsonResponse({'status': 'error', 'message': 'No session ID provided'}, status=400)
            
            try:
                session = FeedbackSession.objects.get(session_id=session_id)
            except FeedbackSession.DoesNotExist:
                session = FeedbackSession.objects.create(session_id=session_id)
            
            # Process the base64 image
            try:
                # Remove the data URL prefix if present
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                
                # Decode base64 image
                image_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is None:
                    return JsonResponse({'status': 'error', 'message': 'Invalid image data'}, status=400)
                
                # Convert BGR to RGB (ViT expects RGB input)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) == 0:
                    return JsonResponse({'status': 'error', 'message': 'No face detected'}, status=400)
                
                # Process the largest face
                x, y, w, h = max(faces, key=lambda face: face[2] * face[3])
                
                # Extract face region (in RGB)
                face_roi = img_rgb[y:y+h, x:x+w]
                
                # Predict emotion using ViT model
                emotion, confidence = predict_emotion(model, face_roi)
                
                # Save the feedback
                feedback = EmotionFeedback.objects.create(
                    session=session,
                    emotion=emotion,
                    confidence=confidence * 100  # Convert to percentage
                )
                
                return JsonResponse({
                    'status': 'success',
                    'emotion': emotion,
                    'confidence': confidence * 100,  # Convert to percentage
                    'session_id': session_id
                })
                
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class FeedbackView(CreateView):
    model = UserFeedback
    template_name = 'emotion_feedback/feedback.html'
    fields = ['rating', 'comment']
    
    def form_valid(self, form):
        session_id = self.kwargs.get('session_id')
        session = FeedbackSession.objects.get(session_id=session_id)
        form.instance.session = session
        session.completed = True
        session.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('emotion_feedback:thank-you')

def start_session(request):
    session = FeedbackSession.objects.create(
        session_id=str(uuid.uuid4())
    )
    return JsonResponse({'session_id': session.session_id})

def save_emotion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        emotion = data.get('emotion')
        confidence = data.get('confidence')
        
        try:
            session = FeedbackSession.objects.get(session_id=session_id)
            EmotionFeedback.objects.create(
                session=session,
                emotion=emotion,
                confidence=confidence
            )
            return JsonResponse({'status': 'success'})
        except FeedbackSession.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Session not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def save_feedback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        try:
            session = FeedbackSession.objects.get(session_id=session_id)
            UserFeedback.objects.create(
                session=session,
                user=request.user,
                rating=rating,
                comment=comment
            )
            session.completed = True
            session.save()
            return JsonResponse({'status': 'success'})
        except FeedbackSession.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Session not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def dashboard(request):
    if request.user.is_staff:
        # Admin users can see all feedback
        feedback_list = UserFeedback.objects.all().order_by('-submitted_at')
    else:
        # Regular users can only see their own feedback
        feedback_list = UserFeedback.objects.filter(user=request.user).order_by('-submitted_at')
    
    return render(request, 'emotion_feedback/dashboard.html', {
        'feedback_list': feedback_list
    })

class ThankYouView(TemplateView):
    template_name = 'emotion_feedback/thank_you.html'
