import csv
from recommendation.models import UserInteraction

def load_interactions():
    file_path = r"ecommerce/data/user_product_interactions_no_rating.csv"
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        interactions = [
            UserInteraction(user_id=row["user_id"], product_id=row["product_id"], action=row["action"])
            for row in reader
        ]
        UserInteraction.objects.bulk_create(interactions)
    print("Data loaded successfully!")
