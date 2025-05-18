from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    is_market_analyst = models.BooleanField(default=False, verbose_name="Nhà phân tích thị trường")
    
    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

class Topic(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên đề tài")
    description = models.TextField(verbose_name="Mô tả")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Đề tài"
        verbose_name_plural = "Đề tài"

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người đăng")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name="Đề tài")
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    description = models.TextField(verbose_name="Mô tả")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá")
    image = models.ImageField(upload_to='products/', verbose_name="Hình ảnh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
