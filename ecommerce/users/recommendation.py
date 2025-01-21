# from surprise import  SVD
# import joblib
# model = SVD()
# model = joblib.load('D:\\django_test\\Eco-bazar-final\\ecommerce\lightfm_model.pkl')
# def get_recommendations(user_id, model, all_product_ids):
#     # Get predictions for all products for the given user_id
#     predictions = [model.predict(user_id, product_id) for product_id in all_product_ids]
    
#     # Sort the predictions based on the estimated ratings
#     predictions.sort(key=lambda x: x.est, reverse=True)
    
#     # Get the top recommended products (based on the highest predicted ratings)
#     top_recommendations = [prediction.iid for prediction in predictions[:10]]  # Top 10 products
#     return top_recommendations