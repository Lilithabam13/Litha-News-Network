# news/views.py
"""Views for the LNN News Application.

This module contains:
- Authentication views
- Dashboard views
- Article management views
- Password reset functionality
- Email helper utilities
- Role-based access control"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .forms import CustomUserCreationForm, ArticleForm, PublisherForm, NewsletterForm
from .models import Article, ResetToken, Newsletter, CustomUser, Publisher
from django.contrib.auth.models import Group
import requests
from django.core.mail import send_mail, EmailMessage
from django.contrib import messages
import secrets
from django.utils import timezone
from datetime import timedelta
from hashlib import sha1
# Create your views here.


# Role check functions
def is_journalist(user):
    """Checks whether a user belongs to journalist group.

    :param user: Authenticated user instance
    :type user: CustomUser
    :return: True if a user is a journalist, otherwise False
    :rtype: bool"""

    return user.is_authenticated and user.groups.filter(
        name="Journalist").exists()


def is_reader(user):
    """Checks whether a user belongs to reader group.

    :param user: Authenticated user instance
    :type user: CustomUser
    :return: True if a user is a reader, otherwise False
    :rtype: bool"""

    return user.is_authenticated and user.groups.filter(name="Reader").exists()


def is_editor(user):
    """Checks whether a user belongs to editor group.

    :param user: Authenticated user instance
    :type user: CustomUser
    :return: True if a user is an editor, otherwise False
    :rtype: bool"""

    return user.is_authenticated and user.groups.filter(name="Editor").exists()


# Journalist
@login_required
@user_passes_test(is_journalist)
def create_article(request):
    """Creates a new article submitted by a journalist.

    Validates article form data and assigns the logged-in user as the author
    of the aticle.

    :param request: HTTP request object
    :type request: HttpRequest
    :return: Rendered article form or redirect response
    :rtype: HttpResponse"""

    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()

            messages.success(request, "Article submitted for editor review")
            return redirect("news:journalist_dashboard")
    else:
        form = ArticleForm()

    return render(request, "journalist/create_article.html", {"form": form})


# Journalist/Editor
@login_required
@permission_required("news.change_article", raise_exception=True)
def edit_article(request, article_id):
    """Edits an existing article.

    Journalists only edit their own articles while editors may edit any article

    :param request: HTTP request object
    :type request: HttpRequest
    :param article_id: Unique article identifier
    :type article_id: int
    :return: Rendered edit form or redirect response
    :rtype: HttpResponse"""

    article = get_object_or_404(Article, id=article_id)

    if request.user.role == "journalist" and article.author != request.user:
        return redirect("news:journalist_dashboard")

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)

        if form.is_valid():
            form.save()

            messages.success(request, "Article updated successfully")

            if request.user.role == "editor":
                return redirect("news:editor_dashboard")

            return redirect("news:journalist_dashboard")
    else:
        form = ArticleForm(instance=article)

    return render(request, "articles/edit_article.html",
                  {"form": form, "article": article})


@login_required
@permission_required("news.delete_article", raise_exception=True)
def delete_article(request, article_id):
    """Deletes an existing article.

    :param request: HTTP request object
    :type request: HttpRequest
    :param article_id: Unique article identifier
    :type article_id: int
    :return: Rendered confirmation page or redirect response
    :rtype: HttpResponse"""

    article = get_object_or_404(Article, id=article_id)

    if request.user.role == "journalist" and article.author != request.user:
        return redirect("news:journalist_dashboard")

    if request.method == "POST":
        article.delete()

        messages.success(request, "Article deleted successfully")

        if request.user.role == "editor":
            return redirect("news:editor_dashboard")

        return redirect("news:journalist_dashboard")

    return render(request, "articles/delete_article.html",
                  {"article": article})


# Editor
@login_required
@user_passes_test(is_editor)
def approve_article(request, article_id):
    """Approves an article for publication.

    Sends an email to subscribers and posts article updates to external
    API X(twitter).

    :param request: HTTP request object
    :type request: HttpRequest
    :param article_id: Unique article identifier
    :type article_id: int
    :return: Redirect response to editor dashboard
    :rtype: HttpResponseRedirect"""

    if request.method != "POST":
        return redirect("news:review_articles")

    article = get_object_or_404(Article, id=article_id)

    if not article.is_approved:
        article.is_approved = True
        article.save()

        if article.publisher:
            publisher_subscribers = article.publisher.subscribers.all()
        else:
            publisher_subscribers = []

        journalist_subscribers = article.author.followers.all()

        publisher_list = list(publisher_subscribers)
        journalist_list = list(journalist_subscribers)

        combined_lists = publisher_list + journalist_list

        unique_subscribers = []
        for user in combined_lists:
            if user not in unique_subscribers:
                unique_subscribers.append(user)

        subscribers = unique_subscribers

        for user in subscribers:
            if user.email:
                send_mail(subject=f"New Article: {article.title}",
                          message=article.body,
                          from_email="admin@LNN.com",
                          recipient_list=[user.email],
                          fail_silently=True,)

        try:
            requests.post("https://api.x.com/2/tweets",
                          json={"text": article.title},
                          headers={"Authorization": "Bearer Token"})

        except Exception:
            pass

        messages.success(request, "Article approved and notififications sent.")

    return redirect("news:editor_dashboard")


# Editor
@login_required
@user_passes_test(is_editor)
def review_articles(request):
    articles = Article.objects.filter(is_approved=False)
    return render(request, "editor/review_articles.html",
                  {"articles": articles})


# Dashboard Views
@login_required
@user_passes_test(is_journalist)
def journalist_dashboard(request):
    """Displays the journalist dashboard, shows all articles created by
    a journalist.

    Journalist may create, read, update and delete their own articles

    :param request: HTTP request object
    :type request: HttpRequest
    :return: Rendered journalist dashboard
    :rtype: HttpResponse"""

    articles = Article.objects.filter(author=request.user)
    newsletters = Newsletter.objects.filter(author=request.user)
    return render(request, "dashboards/journalist_dashboard.html",
                  {"articles": articles, "newsletters": newsletters})


@login_required
@user_passes_test(is_editor)
def editor_dashboard(request):
    """Displays the editor dashboard, shows articles and newsletters.

    Editors may read, update, delete all items including already approved
    content.

    :param request: HTTP request object
    :type request: HttpRequest
    :return: Rendered journalist dashboard
    :rtype: HttpResponse"""
    all_articles = Article.objects.order_by("created_at")
    newsletters = Newsletter.objects.all().order_by("created_at")
    return render(request, "dashboards/editor_dashboard.html",
                  {"articles": all_articles, "newsletters": newsletters})


@login_required
@user_passes_test(is_reader)
def reader_dashboard(request):
    """Displays the reader dashboard, shows personalised content feed.

    Reader may read newsletters and approved articles only tailored to their
    subscribed publishers and journalists they follow.

    :param request: HTTP request object
    :type request: HttpRequest
    :return: Rendered journalist dashboard
    :rtype: HttpResponse"""
    current_user = request.user
    my_publishers = current_user.subscribed_publishers.all()
    my_journalists = current_user.subscribed_journalists.all()

    all_approved = Article.objects.filter(is_approved=True)

    feed_articles = []

    for article in all_approved:
        if article.publisher in my_publishers or article.author in my_journalists:
            feed_articles.append(article)

        all_newsletters = Newsletter.objects.all()
        feed_newsletters = []

        for newsletter in all_newsletters:
            if newsletter.author in my_journalists:
                feed_newsletters.append(newsletter)

    all_publishers = Publisher.objects.all()
    all_journalists = CustomUser.objects.filter(role="journalist")

    return render(request, "dashboards/reader_dashboard.html",
                  {"articles": feed_articles, "newsletters": feed_newsletters,
                   "all_publishers": all_publishers,
                   "all_journalists": all_journalists})


def role_redirect(user):
    if user.role == "journalist":
        return redirect("news:journalist_dashboard")

    elif user.role == "editor":
        return redirect("news:editor_dashboard")

    return redirect("news:reader_dashboard")


# Authorisation and Authentication
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            if user.role == "journalist":
                group, _ = Group.objects.get_or_create(name="Journalist")

            elif user.role == "editor":
                group, _ = Group.objects.get_or_create(name="Editor")

            elif user.role == "reader":
                group, _ = Group.objects.get_or_create(name="Reader")

            user.groups.add(group)

            login(request, user)

            return role_redirect(user)
    else:
        form = CustomUserCreationForm()

    return render(request, "auth/register.html", {"form": form})


# Login user
def login_user(request):
    """Authenticates and logs in a user.

    Redirects authenticated users to dashboards based on their role.

    :param request: Http request object
    :type request: HttpRequest
    :return: Rendered login page or redirect response
    :type: HttpResponse"""

    if request.method == "POST":
        # authentication logic
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return role_redirect(user)

        else:
            messages.error(request, "Invalid username or password")
    return render(request, "auth/login.html")


# Logout user
def logout_user(request):
    """Logs out a logged-in user.

    :param request: Http request object
    :type request: HttpRequest
    :return: Redirect response to login page
    :rtype: HttpResponseRedirect"""

    logout(request)
    return redirect("news:login")


# Welcome user
@login_required(login_url="news:login")
def welcome(request):
    return role_redirect(request.user)


# Reset user password
def reset_user_password(request, token):
    """Resets a user's password using a secure token.

    Validates token existence and expiry before updating the user's password.

    :param request: Http request object
    :type request: HttpRequest
    :param token: Password reset token
    :type token: str
    :return: Redendered reset page or redirect response
    :rtype: HttpResponse"""

    hashed_token = sha1(token.encode()).hexdigest()

    try:
        user_token = ResetToken.objects.get(token=hashed_token)
    except ResetToken.DoesNotExist:
        return render(request, "auth/password_reset.html", {"token": None})

    if user_token.expiry_date < timezone.now():
        user_token.delete()
        return render(request, "auth/password_reset.html", {"token": None})

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(
                request, "auth/password_reset.html", {"token": user_token})

        user = user_token.user
        user.set_password(new_password)
        user.save()

        user_token.delete()
        return redirect("news:login")

    return render(request, "auth/password_reset.html", {"token": user_token})


def password_reset_request(request):
    """Displays the password reset request form.

    :param request: HttpRequest object
    :return: Rendered password reset request template"""

    return render(request, "auth/password_reset_request.html")


# Send reset email
def send_password_reset(request):
    """Sends a password reset email to a user.

    Generate a secure reset URL and emails the password reset instructions.

    :param request: Http request object
    :type request: HttpRequest
    :return: Redirect response to login page
    :rtype: HttpResponseRedirect"""

    User = get_user_model()

    if request.method != "POST":
        return redirect("news:login")
    user_email = request.POST.get("email")
    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:

        messages.error(request, "No account found with that email")
        return redirect("news:password_reset_request")

    url = generate_reset_url(user)
    email = build_email(user, url)
    email.send()
    messages.success(request, "Password reset email sent")
    return redirect("news:login")

# ----------------------------------------
# Emails
# ----------------------------------------


# Build email
def build_email(user, reset_url):
    """Builds the password reset email message.

    :param user: User requesting password reset
    :type user: CustomUser
    :param reset_url: Secure password reset URL
    :type reset_url: str
    :return: Configured email message object
    :rtype: EmailMessage"""

    subject = "Password Reset"
    user_email = user.email
    domain_email = "mango@domain.com"
    body = (f"Hi {user.username},\n\n"
            f"\nHere is your link to reset your password:\n"
            f"{reset_url}")

    email = EmailMessage(subject=subject,
                         body=body, from_email=domain_email, to=[user_email])
    return email


# Reset token
def generate_reset_url(user):
    """Generates a secure password reset URL.

    Creates a hashed token with an expiry timestamp and stores
    it in the databse.

    :param user: User requesting password reset
    :type user: CustomUser
    :return: Secure password reset URL
    :rtype: str"""

    domain = "http://127.0.0.1:8000/"

    url = f"{domain}/reset_password/"

    token = str(secrets.token_urlsafe(16))
    expiry_date = timezone.now() + timedelta(minutes=5)

    ResetToken.objects.filter(user=user).delete()
    reset_token = ResetToken.objects.create(
        user=user, token=sha1(token.encode()).hexdigest(),
        expiry_date=expiry_date)
    reset_token.save()
    url += f"{token}/"
    return url


@login_required
@user_passes_test(is_editor)
def create_publisher(request):
    """Creates a new publisher and assigns the logged-in editor to it.

    Validates publisher form data and establishes the editor relationship.

    :param request: HTTP request object
    :type request: HttpRequest
    :return: Rendered publisher form or redirect response
    :rtype: HttpResponse"""

    if request.method == "POST":
        form = PublisherForm(request.POST)

        if form.is_valid():
            publisher = form.save()

            publisher.editors.add(request.user)

            messages.success(request, "Publisher created successfully.")

            return redirect("news:editor_dashboard")

    else:
        form = PublisherForm()

    return render(request, "editor/create_publisher.html", {"form": form})


@login_required
@user_passes_test(is_journalist)
def create_newsletter(request):
    """Creates a new newsletter submitted by a journalist.

    Validates newsletter form data and assigns the logged-in user as the
    author.

    :param request: HTTP request object
    :type request: HttpRequest
    :return: Rendered newsletter form or redirect response
    :rtype: HttpResponse"""

    if request.method == "POST":
        form = NewsletterForm(request.POST)

        if form.is_valid():
            newsletter = form.save(commit=False)

            newsletter.author = request.user
            newsletter.save()

            form.save_m2m()

            messages.success(request, "Newsletter created successfully.")

            return redirect("news:journalist_dashboard")

    else:
        form = NewsletterForm()

    return render(request, "journalist/create_newsletter.html", {"form": form})


# Journalist/Editor
@login_required
@permission_required("news.change_newsletter", raise_exception=True)
def edit_newsletter(request, newsletter_id):
    """Edits an existing newsletter.

    Journalists only edit their own articles while editors may edit any
    newsletter.

    :param request: HTTP request object
    :type request: HttpRequest
    :param article_id: Unique newsletter identifier
    :type article_id: int
    :return: Rendered edit form or redirect response
    :rtype: HttpResponse"""

    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if request.user.role == "journalist" and newsletter.author != request.user:
        return redirect("news:journalist_dashboard")

    if request.method == "POST":
        form = NewsletterForm(request.POST, instance=newsletter)

        if form.is_valid():
            form.save()

            messages.success(request, "Newsletter updated successfully")

            if request.user.role == "editor":
                return redirect("news:editor_dashboard")

            return redirect("news:journalist_dashboard")
    else:
        form = NewsletterForm(instance=newsletter)

    return render(request, "newsletters/edit_newsletter.html",
                  {"form": form, "newsletter": newsletter})


@login_required
@permission_required("news.delete_newsletter", raise_exception=True)
def delete_newsletter(request, newsletter_id):
    """Deletes an existing newsletter.

    :param request: HTTP request object
    :type request: HttpRequest
    :param article_id: Unique newsletter identifier
    :type article_id: int
    :return: Rendered confirmation page or redirect response
    :rtype: HttpResponse"""

    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if request.user.role == "journalist" and newsletter.author != request.user:
        return redirect("news:journalist_dashboard")

    if request.method == "POST":
        newsletter.delete()

        messages.success(request, "Newsletter deleted successfully")

        if request.user.role == "editor":
            return redirect("news:editor_dashboard")

        return redirect("news:journalist_dashboard")

    return render(request, "newsletters/delete_newsletter.html",
                  {"newsletter": newsletter})


@login_required
@user_passes_test(is_reader)
def toggle_publisher_subscription(request, publisher_id):
    """Allows a reader to subscribe or unsubscribe from a publisher.

    :param request: HTTP request object
    :type request: HttpRequest
    :param publisher_id: Unique publisher identifier
    :type publisher_id: int
    :return: Redirect response back to reader feed
    :rtype: HttpResponseRedirect"""

    publisher = get_object_or_404(Publisher, id=publisher_id)
    if request.user.subscribed_publishers.filter(id=publisher.id).exists():
        request.user.subscribed_publishers.remove(publisher)
        messages.success(request, f"Unsubscribed from {publisher.name}")
    else:
        request.user.subscribed_publishers.add(publisher)
        messages.success(request, f"Subscribed to {publisher.name}")
    return redirect("news:reader_dashboard")


@login_required
@user_passes_test(is_reader)
def toggle_journalist_subscription(request, journalist_id):
    """Allows a reader to follow or unfollow from an independent journalist.

    :param request: HTTP request object
    :type request: HttpRequest
    :param journalist_id: Unique journalist identifier
    :type journalist_id: int
    :return: Redirect response to reader feed
    :rtype: httpResponseRedirect"""

    journalist = get_object_or_404(CustomUser, id=journalist_id,
                                   role="journalist")
    if request.user.subscribed_journalists.filter(id=journalist.id).exists():
        request.user.subscribed_journalists.remove(journalist)
        messages.success(request, f"Unfollowed {journalist.username}")
    else:
        request.user.subscribed_journalists.add(journalist)
        messages.success(request, f"Following {journalist.username}")
    return redirect("news:reader_dashboard")
