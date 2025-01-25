from surprise import  SVD
import joblib
model = SVD()
model = joblib.load(r'C:\Users\Dell\OneDrive\Desktop\git\college project\ecommerce\lightfm_model.pkl')
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
def get_recommendations(user_id, model, all_product_ids):
    # Get predictions for all products for the given user_id
    predictions = [model.predict(user_id, product_id) for product_id in all_product_ids]
    
    # Sort the predictions based on the estimated ratings
    predictions.sort(key=lambda x: x.est, reverse=True)
    
    # Get the top recommended products (based on the highest predicted ratings)
    top_recommendations = [prediction.iid for prediction in predictions[:10]]  # Top 10 products
    return top_recommendations






# Sample data (same as before)
df = pd.read_csv(r"C:\Users\Dell\OneDrive\Desktop\git\college project\ecommerce\ecommerce\data\user_product_interactions_no_rating.csv")

# Encode actions to numerical values
action_map = {'click': 1, 'view': 1, 'buy': 2}
df['action_value'] = df['action'].map(action_map)

# Step 2: Create the user-product interaction matrix
interaction_matrix = df.pivot_table(index='user_id', columns='Product_id', values='action_value', aggfunc='max', fill_value=0)

# Step 3: Compute cosine similarity between products (using their columns)
product_similarity = cosine_similarity(interaction_matrix.T)

product_similarity_df = pd.DataFrame(product_similarity, index=interaction_matrix.columns, columns=interaction_matrix.columns)

# Function to recommend top N products to a user based on product similarity
def recommend_products(user_id, top_n=10):
    # Get the user-product interaction data for the given user_id
    user_interactions = interaction_matrix.loc[user_id]

    # List of products the user has interacted with (non-zero values in interaction matrix)
    interacted_products = user_interactions[user_interactions > 0].index.tolist()

    # Calculate a score for each product based on similarity to products the user has interacted with
    product_scores = {}
    
    for product in interaction_matrix.columns:
        if product not in interacted_products:
            # Calculate the weighted score based on product similarity
            similarity_score = 0
            for interacted_product in interacted_products:
                similarity_score += product_similarity_df.loc[product, interacted_product] * user_interactions[interacted_product]
            product_scores[product] = similarity_score

    # Sort products by score in descending order and return top N
    sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Get the top N products
    top_products = [product for product, score in sorted_products[:top_n]]
    
    return top_products