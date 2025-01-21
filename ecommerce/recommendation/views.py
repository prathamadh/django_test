from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from recommendation.models import UserInteraction

def recommend_products(request, user_id):
    # Fetch products the user interacted with
    user_interactions = UserInteraction.objects.filter(user_id=user_id)
    
    # Placeholder: Add collaborative filtering logic here
    recommendations = UserInteraction.objects.exclude(user_id=user_id)[:10]  # Sample recommendations

    return render(request, "recommendation/recommendations.html", {
        "user_id": user_id,
        "interactions": user_interactions,
        "recommendations": recommendations
    })
