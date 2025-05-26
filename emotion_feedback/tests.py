from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from accounts.models import Product, Topic
from emotion_feedback.models import UserFeedback

class NormalUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='userpass')
        self.topic = Topic.objects.create(name='Test Topic')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10000,
            topic=self.topic,
            user=self.user
        )
        self.feedback = UserFeedback.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Great!',
            emotion='happy'
        )

    def test_user_rate_product(self):
        self.client.login(username='user', password='userpass')
        response = self.client.post(f'/product/{self.product.id}/', {
            'rating': 4,
            'comment': 'Nice!',
            'emotion': 'happy',
            'emotion_image': 'base64string'
        })
        self.assertIn(response.status_code, [200, 302])
        self.assertTrue(UserFeedback.objects.filter(user=self.user, product=self.product, comment='Nice!').exists())

    def test_user_view_own_feedback(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get('/emotion_feedback/my_feedback/')
        self.assertContains(response, 'Great!')

    def test_user_delete_own_feedback(self):
        self.client.login(username='user', password='userpass')
        response = self.client.post(f'/emotion_feedback/feedback/{self.feedback.id}/delete/', follow=True)
        self.assertFalse(UserFeedback.objects.filter(id=self.feedback.id).exists())

    def test_user_profile_and_logout(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/accounts/logout/', follow=True)
        self.assertIn(response.status_code, [200, 302])