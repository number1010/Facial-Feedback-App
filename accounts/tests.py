from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Product, Topic
from emotion_feedback.models import UserFeedback

class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Tạo người dùng mẫu
        self.normal_user = User.objects.create_user(username='normal', password='pass123')
        self.analyst = User.objects.create_user(username='analyst', password='pass123', is_staff=True)
        self.admin = User.objects.create_user(username='admin', password='admin123', is_superuser=True)
        self.topic = Topic.objects.create(name='Topic1')

    # TC1: Kiểm tra trang home
    def test_home_view_anonymous(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/home.html')

    # TC2: Đăng ký thành công
    def test_register_success(self):
        data = {'username': 'newuser', 'email': 'new@exam.com', 'password': 'pass123', 'password2': 'pass123'}
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    # TC6: Truy cập select_topic (phân quyền)
    def test_select_topic_access(self):
        self.client.login(username='normal', password='pass123')
        response = self.client.get(reverse('select_topic'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='analyst', password='pass123')
        response = self.client.get(reverse('select_topic'))
        self.assertEqual(response.status_code, 200)

    # TC7: Upload sản phẩm thành công
    def test_upload_product_success(self):
        self.client.login(username='analyst', password='pass123')
        data = {'name': 'Product1', 'description': 'Desc', 'topic': self.topic.id}
        response = self.client.post(reverse('upload_product', args=[self.topic.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name='Product1').exists())

    # Thêm các test case khác (TC3, TC4, TC5, TC8, TC9, TC10, TC11, TC12) tương tự