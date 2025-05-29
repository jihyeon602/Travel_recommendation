from flask import Flask, request, jsonify
from catboost import CatBoostRegressor, Pool
import pandas as pd

# Initialize the Flask application
app = Flask(__name__)

# Load the CatBoost model
model = CatBoostRegressor()
model.load_model('catboost_model_travel.cbm')

# Load unique visit areas from your preprocessed data
area_names = pd.read_csv('./tn_visit_area_info_방문지정보_A.csv')['VISIT_AREA_NM'].drop_duplicates().tolist()

cat_features_names = [
    'GENDER',
    'TRAVEL_STYL_1', 'TRAVEL_STYL_2', 'TRAVEL_STYL_3', 'TRAVEL_STYL_4',
    'TRAVEL_STYL_5', 'TRAVEL_STYL_6', 'TRAVEL_STYL_7', 'TRAVEL_STYL_8',
    'TRAVEL_MOTIVE_1', 'TRAVEL_MISSION_INT', 'VISIT_AREA_NM', 'TRAVEL_PURPOSE_INT'
]

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
        data['TRAVEL_MISSION_INT'],
        data['TRAVEL_PURPOSE_INT'],
        data['TRAVEL_TERM']
    ]

    results = pd.DataFrame(columns=['AREA', 'SCORE'])

    for area in area_names:
        input_data = data.copy()
        input_data['VISIT_AREA_NM'] = area

        input_df = pd.DataFrame([input_data])

        # 범주형 컬럼들은 문자열로 변환
        for col in cat_features_names:
            input_df[col] = input_df[col].astype(str)

        # CatBoost Pool 생성
        input_pool = Pool(input_df, cat_features=cat_features_names)

        # 예측
        score = model.predict(input_pool)[0]

        # 결과 저장
        results = pd.concat(
            [results, pd.DataFrame([[area, score]], columns=['AREA', 'SCORE'])]
        )

    # 점수 기준 정렬 및 상위 10개만 반환
    top10 = results.sort_values('SCORE', ascending=False).head(10)

    # JSON으로 변환하여 반환
    return jsonify(top10.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
