from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib.auth.decorators import login_required
import json
import uuid
import base64
import numpy as np
import cv2
import os
from .models import FeedbackSession, EmotionFeedback, UserFeedback, EmotionImage
from .vit_model import load_vit_model, predict_emotion
from django.urls import reverse
from accounts.models import Product, Topic
from django.contrib import messages
from django.core.files.base import ContentFile
from datetime import datetime
from PIL import Image
from io import BytesIO


# Định nghĩa các lớp cảm xúc
EMOTIONS = ['angry', 'disgusted', 'fearful', 'happy', 'neutral', 'sad', 'surprised']

# Load pre-trained ViT model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'models', 'vit_b16_fer2013.pth')
model = load_vit_model(model_path)

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class HomeView(TemplateView):
    template_name = 'emotion_feedback/home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_market_analyst:
            return redirect('emotion_feedback:product_list')
        return super().get(request, *args, **kwargs)

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

@csrf_exempt
@require_POST
def save_emotion(request):
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        session_id = data.get('session_id')
        if not image_data or not session_id:
            return JsonResponse({'status': 'error', 'message': 'Missing image or session_id'})
        
        # Decode base64 image
        image_data = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return JsonResponse({'status': 'error', 'message': 'Invalid image data'})
            
        # Convert BGR to RGB (OpenCV uses BGR, but we need RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to numpy array for transform
        image_np = np.array(image_rgb)
        
        # Predict emotion using ViT model
        emotion, confidence = predict_emotion(model, image_np)
        
        if emotion is None:
            return JsonResponse({'status': 'error', 'message': 'Failed to predict emotion'})
            
        # Save to session
        request.session[session_id] = emotion
        
        return JsonResponse({
            'status': 'success',
            'emotion': emotion,
            'confidence': confidence
        })
    except Exception as e:
        print(f"Error in save_emotion: {e}")  # Thêm log để debug
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def save_feedback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        try:
            session = FeedbackSession.objects.get(session_id=session_id)
            feedback = UserFeedback.objects.create(
                session=session,
                user=request.user,
                rating=rating,
                comment=comment
            )
            print(f"Created feedback: {feedback.id} for user {request.user.username}")  # Debug print
            session.completed = True
            session.save()
            return JsonResponse({'status': 'success'})
        except FeedbackSession.DoesNotExist:
            print(f"Session not found: {session_id}")  # Debug print
            return JsonResponse({'status': 'error', 'message': 'Session not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def dashboard(request):
    # User chỉ thấy đánh giá của chính mình
    feedback_list = UserFeedback.objects.filter(user=request.user).order_by('-submitted_at')
    print(f"Found {feedback_list.count()} feedbacks for user {request.user.username}")  # Debug print
    print(f"User ID: {request.user.id}")  # Debug print
    
    return render(request, 'emotion_feedback/dashboard.html', {
        'feedback_list': feedback_list
    })

class ThankYouView(TemplateView):
    template_name = 'emotion_feedback/thank_you.html'

@login_required
def product_list(request):
    topics = Topic.objects.all()
    selected_topic_id = request.GET.get('topic')
    
    # Lấy danh sách sản phẩm đã được đánh giá bởi user hiện tại
    reviewed_products = UserFeedback.objects.filter(user=request.user).values_list('product_id', flat=True)
    
    # Lấy tất cả sản phẩm, loại trừ những sản phẩm đã đánh giá
    products = Product.objects.exclude(id__in=reviewed_products)
    
    # Lọc theo topic nếu có
    if selected_topic_id and selected_topic_id != 'all':
        products = products.filter(topic_id=selected_topic_id)
        
    return render(request, 'emotion_feedback/product_list.html', {
        'products': products,
        'topics': topics,
        'selected_topic_id': selected_topic_id or 'all',
    })

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        emotion = request.POST.get('emotion')
        emotion_image = request.POST.get('emotion_image')
        
        if rating and emotion:
            try:
                # Save emotion image
                emotion_image_path = None
                if emotion_image:
                    # Convert base64 to file
                    format, imgstr = emotion_image.split(';base64,')
                    ext = format.split('/')[-1]
                    filename = f'emotion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
                    data = ContentFile(base64.b64decode(imgstr))
                    
                    # Save to EmotionImage model
                    emotion_image = EmotionImage.objects.create(
                        user=request.user,
                        image=filename
                    )
                    emotion_image.image.save(filename, data, save=True)
                    emotion_image_path = emotion_image.image.url

                # Save feedback
                feedback = UserFeedback.objects.create(
                    user=request.user,
                    product=product,
                    rating=rating,
                    comment=comment,
                    emotion=emotion,
                    emotion_image=emotion_image_path
                )
                print(f"Created feedback: {feedback.id} for product {product.name}")  # Debug print
                messages.success(request, 'Cảm ơn bạn đã đánh giá sản phẩm!')
                return redirect('emotion_feedback:product_list')
            except Exception as e:
                print(f"Error saving feedback: {e}")  # Debug print
                messages.error(request, 'Có lỗi xảy ra khi lưu đánh giá. Vui lòng thử lại!')
    
    return render(request, 'emotion_feedback/product_detail.html', {
        'product': product,
        'session_id': str(uuid.uuid4())  # Generate new session ID for emotion capture
    })

@login_required
def delete_feedback(request, feedback_id):
    try:
        feedback = UserFeedback.objects.get(id=feedback_id, user=request.user)
        product_id = feedback.product.id  # Lưu lại product_id trước khi xóa
        feedback.delete()
        messages.success(request, 'Đánh giá đã được xóa thành công!')
    except UserFeedback.DoesNotExist:
        messages.error(request, 'Không tìm thấy đánh giá!')
    
    return redirect('emotion_feedback:dashboard')
