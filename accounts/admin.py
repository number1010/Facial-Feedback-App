from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Topic, Product

admin.site.register(User, UserAdmin)
admin.site.register(Topic)
admin.site.register(Product)
