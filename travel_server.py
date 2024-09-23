from flask import Flask, request, jsonify
from catboost import CatBoostRegressor
import pandas as pd

# Initialize the Flask application
app = Flask(__name__)

# Load the CatBoost model
model = CatBoostRegressor()
model.load_model('catboost_model.cbm')

# Load unique visit areas from your preprocessed data
area_names = pd.read_csv('./tn_visit_area_info_방문지정보_D.csv')['VISIT_AREA_NM'].drop_duplicates().tolist()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    traveler = [
        data['GENDER'],
        data['AGE_GRP'],
        data['TRAVEL_STYL_1'],
        data['TRAVEL_STYL_2'],
        data['TRAVEL_STYL_3'],
        data['TRAVEL_STYL_4'],
        data['TRAVEL_STYL_5'],
        data['TRAVEL_STYL_6'],
        data['TRAVEL_STYL_7'],
        data['TRAVEL_STYL_8'],
        data['TRAVEL_MOTIVE_1'],
        data['TRAVEL_COMPANIONS_NUM'],
        data['TRAVEL_MISSION_INT']
    ]

    results = []
    
    # Iterate over each area name and predict the score
    for area in area_names:
        input_features = traveler + [area]  # Append area to the features list
        score = model.predict([input_features])[0]
        results.append({'area': area, 'score': score})

    # Sort results by score in descending order and return top 10
    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
    top_10_recommendations = sorted_results[:10]

    return jsonify(top_10_recommendations)

if __name__ == '__main__':
    app.run(debug=True)
