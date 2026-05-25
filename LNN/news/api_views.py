# news/api_views.py
"""API views for the LNN News Application.

Provides REST API endpoints for retrieving approved articles based on
user subscriptions"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscribed_articles_api(request):
    """Returns approved articles from subscribed publishers and journalists.

    :param request: Incoming API request
    :type request: Request
    :return: Serialized list of approved articles
    :rtype: Response"""

    user = request.user

    publishers = user.subscribed_publishers.all()
    journalists = user.subscribed_journalists.all()

    publisher_articles = Article.objects.filter(
        is_approved=True, publisher__in=publishers)

    journalist_articles = Article.objects.filter(
        is_approved=True, author__in=journalists)

    publisher_list = list(publisher_articles)
    journalist_list = list(journalist_articles)

    combined_lists = publisher_list + journalist_list

    unique_articles = []
    for article in combined_lists:
        if article not in unique_articles:
            unique_articles.append(article)

    articles = unique_articles

    serializer = ArticleSerializer(articles, many=True)

    return Response(serializer.data)
