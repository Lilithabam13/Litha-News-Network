# news/forms.py
"""Forms used in the LNN News Application."""

from django import forms
from .models import Article, CustomUser, Publisher, Newsletter
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

    def clean_email(self):
        email = self.cleaned_data["email"]

        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already"
                                        "exists.")
        return email


class PublisherForm(forms.ModelForm):
    """Form used to create publishers."""
    class Meta:
        model = Publisher
        fields = ["name"]


class NewsletterForm(forms.ModelForm):
    """Form used to create and update newsletters"""
    class Meta:
        model = Newsletter
        fields = ["title", "articles"]
        widgets = {"articles": forms.CheckboxSelectMultiple(),
                   }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['articles'].queryset = Article.objects.filter(
            is_approved=True)
