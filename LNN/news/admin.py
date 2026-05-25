# news/admin.py
"""Admin configuration and group permission setup."""

from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Article, Newsletter, Publisher, CustomUser

# Register your models here.
admin.site.register(Article)
admin.site.register(Newsletter)
admin.site.register(Publisher)
admin.site.register(CustomUser)
# -------------------------------


def create_groups():
    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)

    # ----------------------------------------
    # Readers
    # ----------------------------------------

    reader_group, _ = Group.objects.get_or_create(name="Reader")

    reader_permissions = Permission.objects.filter(
        content_type__in=[article_ct, newsletter_ct],
        codename__in=["view_article", "view_newsletter"])

    reader_group.permissions.set(reader_permissions)

    # ----------------------------------------
    # Editors
    # ----------------------------------------

    editor_group, _ = Group.objects.get_or_create(name="Editor")

    editor_permissions = Permission.objects.filter(
        content_type__in=[article_ct, newsletter_ct],
        codename__in=["view_article", "change_article", "delete_article",
                      "view_newsletter", "change_newsletter",
                      "delete_newsletter"])

    editor_group.permissions.set(editor_permissions)

    # ----------------------------------------
    # Journalists
    # ----------------------------------------

    journalist_group, _ = Group.objects.get_or_create(name="Journalist")

    journalist_permissions = Permission.objects.filter(
        content_type__in=[article_ct, newsletter_ct],
        codename__in=["add_article", "view_article", "change_article",
                      "delete_article", "add_newsletter", "view_newsletter",
                      "change_newsletter", "delete_newsletter"])

    journalist_group.permissions.set(journalist_permissions)
