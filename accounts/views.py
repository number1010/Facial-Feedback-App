from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg, Count, Max, Min
from .forms import UserRegistrationForm, ProductForm, UserLoginForm
from .models import Topic, Product, User
from emotion_feedback.models import UserFeedback
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def is_market_researcher_or_superuser(user):
    return user.is_staff or user.is_superuser

# Create your views here.

def home(request):
    """
    Home page view with website introduction and start feedback session button
    """
    return render(request, 'accounts/home.html', {
        'user': request.user
    })

def register(request):
    if request.method == 'POST':
        # Get form data manually since we're not using the form class anymore
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        is_market_analyst = request.POST.get('is_market_analyst') == 'on'

        # Basic validation
        if password != password2:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return render(request, 'accounts/register.html')

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Set market analyst permissions if checked
            if is_market_analyst:
                user.is_staff = True  # Cấp quyền staff status
                user.is_market_analyst = True
                user.save()

            # Log the user in
            login(request, user)
            messages.success(request, 'Đăng ký tài khoản thành công!')
            
            # Redirect based on user role
            if user.is_superuser or user.is_market_analyst:
                return redirect('accounts:product_management')
            else:
                return redirect('emotion_feedback:product_list')

        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'accounts/register.html')

    return render(request, 'accounts/register.html')

def user_login(request):
    error_message = None
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user role
                if user.is_superuser or user.is_market_analyst:
                    return redirect('accounts:product_management')
                else:
                    return redirect('emotion_feedback:product_list')
            else:
                error_message = 'Tên đăng nhập hoặc mật khẩu không đúng'
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {
        'form': form,
        'error_message': error_message
    })

@login_required
def select_topic(request):
    if not (request.user.is_market_analyst or request.user.is_superuser):
        return redirect('emotion_feedback:home')
    
    topics = Topic.objects.all()
    return render(request, 'accounts/select_topic.html', {'topics': topics})

@login_required
def upload_product(request, topic_id):
    if not (request.user.is_market_analyst or request.user.is_superuser):
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
            return redirect('accounts:product_management')
    else:
        form = ProductForm()
    
    return render(request, 'accounts/upload_product.html', {
        'form': form,
        'topic': topic
    })

@login_required
def delete_product(request, product_id):
    # Allow superuser to delete any product, others can only delete their own
    if request.user.is_superuser:
        product = get_object_or_404(Product, id=product_id)
    else:
        product = get_object_or_404(Product, id=product_id, user=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Sản phẩm đã được xóa thành công!')
        return redirect('accounts:product_management')
    
    return render(request, 'accounts/delete_product.html', {'product': product})

@login_required
@user_passes_test(is_market_researcher_or_superuser)
def edit_product(request, product_id):
    # Allow superuser to edit any product, others can only edit their own
    if request.user.is_superuser:
        product = get_object_or_404(Product, id=product_id)
    else:
        product = get_object_or_404(Product, id=product_id, user=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được cập nhật thành công!')
            return redirect('accounts:product_management')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin sản phẩm!')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'accounts/edit_product.html', {
        'form': form,
        'product': product
    })

@login_required
def analyst_dashboard(request):
    if not (request.user.is_market_analyst or request.user.is_superuser):
        return redirect('emotion_feedback:home')
    
    topics = Topic.objects.all()
    selected_topic_id = request.GET.get('topic')
    
    # Get products based on user role
    if request.user.is_superuser:
        products = Product.objects.all().select_related('user')
    else:
        products = Product.objects.filter(user=request.user)
    
    # Apply topic filter
    if selected_topic_id and selected_topic_id != 'all':
        products = products.filter(topic_id=selected_topic_id)
    
    # Order products by creation date
    products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 16)  # 4 rows x 4 columns = 16 products per page
    page = request.GET.get('page', 1)
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    return render(request, 'accounts/analyst_dashboard.html', {
        'user': request.user,
        'products': products_page,
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
    
    # Get filter parameters
    rating_filter = request.GET.get('rating')
    emotion_filter = request.GET.get('emotion')
    
    # Base queryset
    feedbacks = product.userfeedback_set.all()
    
    # Apply filters
    if rating_filter and rating_filter.isdigit():
        feedbacks = feedbacks.filter(rating=rating_filter)
    
    if emotion_filter and emotion_filter != 'all':
        feedbacks = feedbacks.filter(emotion=emotion_filter)

    # Get unique emotions for the filter dropdown
    unique_emotions = product.userfeedback_set.values_list('emotion', flat=True).distinct()
    
    context = {
        'product': product,
        'feedbacks': feedbacks,
        'current_rating': rating_filter,
        'current_emotion': emotion_filter,
        'unique_emotions': unique_emotions,
        'ratings_range': range(1, 6),  # 1 to 5 stars
    }
    
    return render(request, 'accounts/product_feedback.html', context)

@login_required
def product_statistics(request, product_id):
    if not request.user.is_market_analyst:
        return redirect('emotion_feedback:home')
    
    product = get_object_or_404(Product, id=product_id, user=request.user)
    feedbacks = product.userfeedback_set.all()
    
    # Thống kê đánh giá sao
    rating_stats = {
        'average': feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0,
        'max': feedbacks.aggregate(Max('rating'))['rating__max'] or 0,
        'min': feedbacks.aggregate(Min('rating'))['rating__min'] or 0,
        'distribution': feedbacks.values('rating').annotate(count=Count('rating')).order_by('rating'),
    }
    
    # Chuyển đổi distribution thành dạng list để dễ xử lý trong template
    rating_distribution = []
    for i in range(1, 6):
        count = 0
        for item in rating_stats['distribution']:
            if item['rating'] == i:
                count = item['count']
                break
        rating_distribution.append({'rating': i, 'count': count})
    
    # Thống kê cảm xúc
    emotion_stats = {
        'distribution': feedbacks.values('emotion').annotate(count=Count('emotion')),
        'total': feedbacks.count(),
    }
    
    # Tính phần trăm cho mỗi cảm xúc
    emotion_distribution = []
    for emotion in emotion_stats['distribution']:
        percentage = (emotion['count'] / emotion_stats['total'] * 100) if emotion_stats['total'] > 0 else 0
        emotion_distribution.append({
            'emotion': emotion['emotion'],
            'count': emotion['count'],
            'percentage': round(percentage, 1)
        })
    
    context = {
        'product': product,
        'rating_stats': rating_stats,
        'rating_distribution': rating_distribution,
        'emotion_distribution': emotion_distribution,
        'total_feedbacks': emotion_stats['total'],
    }
    
    return render(request, 'accounts/product_statistics.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_market_analyst)
def product_management(request):
    # Get selected topic
    selected_topic_id = request.GET.get('topic', 'all')
    
    # Get all topics for filter dropdown
    topics = Topic.objects.all()
    
    # Get products based on user role
    if request.user.is_superuser:
        products = Product.objects.all().select_related('user', 'topic')
    else:
        products = Product.objects.filter(user=request.user).select_related('topic')
    
    # Filter by topic if selected
    if selected_topic_id != 'all':
        products = products.filter(topic_id=selected_topic_id)
    
    # Order products by creation date
    products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'topics': topics,
        'selected_topic_id': selected_topic_id,
        'is_superuser': request.user.is_superuser
    }
    return render(request, 'accounts/product_management.html', context)

@login_required
@user_passes_test(is_market_researcher_or_superuser)
def view_feedback(request, product_id):
    # Get product with permission check
    if request.user.is_superuser:
        product = get_object_or_404(Product, id=product_id)
    else:
        product = get_object_or_404(Product, id=product_id, user=request.user)
        
    # Get base queryset
    feedbacks = product.userfeedback_set.all().order_by('-submitted_at')
    
    # Apply filters
    rating_filter = request.GET.get('rating')
    emotion_filter = request.GET.get('emotion')
    
    if rating_filter:
        feedbacks = feedbacks.filter(rating=rating_filter)
    
    if emotion_filter:
        feedbacks = feedbacks.filter(emotion=emotion_filter)
    
    # Get unique emotions for filter dropdown
    emotions = product.userfeedback_set.exclude(emotion__isnull=True).values_list('emotion', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(feedbacks, 12)
    page = request.GET.get('page', 1)
    
    try:
        feedbacks_page = paginator.page(page)
    except PageNotAnInteger:
        feedbacks_page = paginator.page(1)
    except EmptyPage:
        feedbacks_page = paginator.page(paginator.num_pages)
    
    return render(request, 'accounts/view_feedback.html', {
        'product': product,
        'feedbacks': feedbacks_page,
        'emotions': emotions,
        'current_rating': rating_filter,
        'current_emotion': emotion_filter
    })

@login_required
@user_passes_test(is_market_researcher_or_superuser)
def product_stats(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    feedbacks = product.userfeedback_set.all()
    
    # Tính toán thống kê
    total_feedbacks = feedbacks.count()
    emotion_stats = {}
    rating_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    for feedback in feedbacks:
        emotion = feedback.emotion or 'unknown'
        emotion_stats[emotion] = emotion_stats.get(emotion, 0) + 1
        rating_stats[feedback.rating] = rating_stats.get(feedback.rating, 0) + 1
    
    return render(request, 'accounts/product_stats.html', {
        'product': product,
        'total_feedbacks': total_feedbacks,
        'emotion_stats': emotion_stats,
        'rating_stats': rating_stats
    })

@login_required
@user_passes_test(is_market_researcher_or_superuser)
def add_product(request):
    topics = Topic.objects.all()
    
    if request.method == 'POST':
        # Xử lý thêm sản phẩm mới
        try:
            price = float(request.POST.get('price', 0))
            if price < 0 or price > 999999999999999:
                raise ValueError("Giá không hợp lệ. Giá phải từ 0 đến 999,999,999,999,999 VNĐ")

            topic = Topic.objects.get(id=request.POST.get('topic'))
            product = Product.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                price=price,
                topic=topic,
                user=request.user
            )
            if 'image' in request.FILES:
                product.image = request.FILES['image']
                product.save()
            messages.success(request, 'Thêm sản phẩm mới thành công!')
            return redirect('accounts:product_management')
        except Topic.DoesNotExist:
            messages.error(request, 'Chủ đề không tồn tại!')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    
    return render(request, 'accounts/add_product.html', {
        'topics': topics
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(UserFeedback, id=feedback_id)
    product_id = feedback.product.id
    
    # Delete the feedback directly
    feedback.delete()
    messages.success(request, 'Đánh giá đã được xóa thành công!')
    return redirect('accounts:view_feedback', product_id=product_id)

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
