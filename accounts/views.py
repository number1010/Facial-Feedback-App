from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, ProductForm, UserLoginForm
from .models import Topic, Product, User

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            if user.is_market_analyst:
                return redirect('accounts:select_topic')
            return redirect('emotion_feedback:product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_market_analyst:
                    return redirect('accounts:analyst_dashboard')
                return redirect('emotion_feedback:product_list')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def select_topic(request):
    if not request.user.is_market_analyst:
        return redirect('emotion_feedback:home')
    
    topics = Topic.objects.all()
    return render(request, 'accounts/select_topic.html', {'topics': topics})

@login_required
def upload_product(request, topic_id):
    if not request.user.is_market_analyst:
        return redirect('emotion_feedback:home')
    
    try:
        topic = Topic.objects.get(id=topic_id)
    except Topic.DoesNotExist:
        messages.error(request, 'Đề tài không tồn tại!')
        return redirect('accounts:select_topic')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.topic = topic
            product.save()
            messages.success(request, 'Sản phẩm đã được đăng thành công!')
            return redirect('accounts:analyst_dashboard')
    else:
        form = ProductForm()
    
    return render(request, 'accounts/upload_product.html', {
        'form': form,
        'topic': topic
    })

@login_required
def delete_product(request, product_id):
    if not request.user.is_market_analyst:
        return redirect('emotion_feedback:home')
    
    product = get_object_or_404(Product, id=product_id, user=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Sản phẩm đã được xóa thành công!')
        return redirect('accounts:analyst_dashboard')
    
    return render(request, 'accounts/delete_product.html', {'product': product})

@login_required
def edit_product(request, product_id):
    if not request.user.is_market_analyst:
        return redirect('emotion_feedback:home')
    
    product = get_object_or_404(Product, id=product_id, user=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được cập nhật thành công!')
            return redirect('accounts:analyst_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'accounts/edit_product.html', {
        'form': form,
        'product': product
    })

@login_required
def analyst_dashboard(request):
    if not request.user.is_market_analyst:
        return redirect('emotion_feedback:home')
    topics = Topic.objects.all()
    selected_topic_id = request.GET.get('topic')
    products = Product.objects.filter(user=request.user)
    if selected_topic_id and selected_topic_id != 'all':
        products = products.filter(topic_id=selected_topic_id)
    return render(request, 'accounts/analyst_dashboard.html', {
        'user': request.user,
        'products': products,
        'topics': topics,
        'selected_topic_id': selected_topic_id or 'all',
    })

@login_required
def profile(request):
    return render(request, 'accounts/user_profile.html', {'user': request.user})

@login_required
def product_feedback(request, product_id):
    if not request.user.is_market_analyst:
        return redirect('emotion_feedback:home')
    product = get_object_or_404(Product, id=product_id, user=request.user)
    feedbacks = product.userfeedback_set.all()
    return render(request, 'accounts/product_feedback.html', {
        'product': product,
        'feedbacks': feedbacks
    })

# @login_required
# def dashboard(request):
#     if hasattr(request.user, 'is_market_analyst') and request.user.is_market_analyst:
#         # Nhà nghiên cứu thị trường: xem tất cả feedback
#         feedback_list = UserFeedback.objects.select_related('user', 'product').order_by('-submitted_at')
#     else:
#         # User thường: chỉ xem feedback của mình
#         feedback_list = UserFeedback.objects.filter(user=request.user).order_by('-submitted_at')
#     return render(request, 'emotion_feedback/dashboard.html', {
#         'feedback_list': feedback_list
#     })
