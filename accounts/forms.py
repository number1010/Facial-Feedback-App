from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Topic

class UserRegistrationForm(UserCreationForm):
    is_market_analyst = forms.BooleanField(
        required=False,
        label="Tôi là nhà phân tích thị trường",
        help_text="Tích vào nếu bạn là nhà phân tích thị trường"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_market_analyst')

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        } 