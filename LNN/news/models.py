# news/models.py
"""Database models for the LNN News Application.

This module contains:
- Customer user model with role support
- Publisher model
- Article model
- Newsletter model
- Password reset token model"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.


class CustomUser(AbstractUser):
    """Custom user model with role-based access control.

    Extends Django's AbstractUser model by adding:
    - user roles
    - publisher subscriptions
    - journalist subscriptions"""

    ROLE_CHOICES = (
        ("reader", "Reader"),
        ("editor", "Editor"),
        ("journalist", "Journalist")
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    subscribed_publishers = models.ManyToManyField(
        "Publisher", blank=True, related_name="subscribers")

    subscribed_journalists = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="followers")


class Publisher(models.Model):
    """Represents a news publishing organisation.

    Stores publisher information and relationships with
    editors and journalists."""

    name = models.CharField(max_length=255)

    editors = models.ManyToManyField(
        CustomUser, related_name="editor_publishers", blank=True)

    journalists = models.ManyToManyField(
        CustomUser, related_name="journalist_publishers", blank=True)

    def __str__(self):
        """Returns the publisher name.

        :return: Publsher name
        :rtype: str"""

        return self.name


class Article(models.Model):
    """Represents a news aricle submitted by a journalist.

    Articles must be approved by editors before being
    distributed to readers."""

    title = models.CharField(max_length=255)
    body = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name="articles")

    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, related_name="articles")

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """Represents a newsletter published to readers."""

    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name="newsletters")

    def __str__(self):
        return self.title


# Token
class ResetToken(models.Model):
    """Represents a password reset token for a users.

    Tokens are generated during password reset requests and expire
    after a 5 minute period.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    expiry_date = models.DateTimeField()
    used = models.BooleanField(default=False)
