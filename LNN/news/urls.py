# news/urls.py
"""URL routes for the news application.

Defines routes for:
- article management
- dashboards
- authentication
- password reset flow
- API endpoints"""

from django.urls import path
from . import views, api_views

app_name = "news"

urlpatterns = [

    # ------------------------------
    # Journalist
    # ------------------------------

    path("create-article/", views.create_article, name="create_article"),

    # ------------------------------
    # Editor
    # ------------------------------

    path("approve-article/<int:article_id>/", views.approve_article,
         name="approve_article"),

    path("review-articles/", views.review_articles, name="review_articles"),

    # ------------------------------
    # Journalist/Editor
    # ------------------------------
    path("edit-article/<int:article_id>/", views.edit_article,
         name="edit_article"),
    path("delete-article/<int:article_id>/", views.delete_article,
         name="delete_article"),

    # ------------------------------
    # Authorisation & Authentication
    # ------------------------------

    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),

    # Password reset flow
    path("password-reset/", views.password_reset_request,
         name="password_reset_request"),
    path("send-reset/", views.send_password_reset, name="send_password_reset"),
    path("reset_password/<str:token>/", views.reset_user_password,
         name="reset_password"),

    # ------------------------------
    # Home
    # ------------------------------

    path("", views.welcome, name="home"),

    # ------------------------------
    # Dashboard
    # ------------------------------

    path("dashboard/journalist/", views.journalist_dashboard,
         name="journalist_dashboard"),
    path("dashboard/editor/", views.editor_dashboard, name="editor_dashboard"),
    path("dashboard/reader/", views.reader_dashboard, name="reader_dashboard"),

    # ------------------------------
    # API View
    # ------------------------------

    path("api/articles/", api_views.subscribed_articles_api,
         name="api_articles"),

]
