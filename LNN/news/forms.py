# news/forms.py
"""Forms used in the LNN News Application."""

from django import forms
from .models import Article, CustomUser
from django.contrib.auth.forms import UserCreationForm


class ArticleForm(forms.ModelForm):
    """Form used to create and update articles."""
    class Meta:
        model = Article
        fields = ["title", "body", "publisher"]


class CustomUserCreationForm(UserCreationForm):
    """Custom registration form for creating users with roles."""
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2", "role"]
