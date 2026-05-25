# news/serializers.py
"""Serializers for converting model instances in JSON data."""

from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """Serializes Article model data fro API responses."""
    class Meta:
        model = Article
        fields = ["id", "title", "body", "author", "publisher", "created_at"]
