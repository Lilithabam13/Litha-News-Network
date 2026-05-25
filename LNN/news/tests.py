# news/tests.py
"""Unit and integration tests for LNN News Applicaton."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Article, Publisher

# Create your tests here.

User = get_user_model()


class ArticleAPITest(TestCase):
    """Tests API functionality for subscribed article retireval."""

    def setUp(self):
        """Creates test readers, journalists, publishers and articles.

        Sets up reusable test data for API endpoint testing."""

        self.client = APIClient()

        self.reader = User.objects.create_user(username="Jacob",
                                               password="pass123",
                                               role="Reader")

        self.journalist = User.objects.create_user(username="Edward",
                                                   password="pass456",
                                                   role="Journalist")

        self.publisher = Publisher.objects.create(name="Orange Publishers")

        self.reader.subscribed_publishers.add(self.publisher)

        self.article1 = Article.objects.create(title="Music Article",
                                               body="Music123",
                                               author=self.journalist,
                                               publisher=self.publisher,
                                               is_approved=True)

        self.article2 = Article.objects.create(title="Politics Article",
                                               body="Politics123",
                                               author=self.journalist,
                                               publisher=self.publisher,
                                               is_approved=False)

    def test_api_returns_only_approved_articles(self):
        """Tests that only approved articles are returned by the API.

        Verifies:
        - authenticated access
        - filtering of approved articles
        - correct article serialization"""

        self.client.login(username="Jacob", password="pass123")

        response = self.client.get("/api/articles/")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]["title"], "Music Article")


class ArticleModelTest(TestCase):
    """Tests Article model creation and relationships."""

    def test_article_creation(self):
        """Tests successful creation of an article instance.

        Verifies:
        - article title
        - author relationship
        - publisher relationship"""

        user = User.objects.create_user(username="bruno", password="manutd789")

        publisher = Publisher.objects.create(name="Pink publishers")

        article = Article.objects.create(title="Monk is title",
                                         body="Mexico is red", author=user,
                                         publisher=publisher)

        self.assertEqual(article.title, "Monk is title")
        self.assertEqual(article.author.username, "bruno")
        self.assertEqual(article.publisher.name, "Pink publishers")


class UrlTests(TestCase):
    """Tests application URL responses."""

    def test_login_page(self):
        """Tests that the login page loads successfully.

        :return: None
        :rtype: None"""

        response = self.client.get("/login/")

        self.assertEqual(response.status_code, 200)
