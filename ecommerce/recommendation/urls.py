from django.urls import path
from recommendation.views import recommend_products

urlpatterns = [
    path("recommendations/<str:user_id>/", recommend_products, name="recommend_products"),
]
