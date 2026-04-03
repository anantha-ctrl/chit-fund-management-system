from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control rounded-pill px-4'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control rounded-pill px-4'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-pill px-4'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
