# DB_insert_server.py
from flask import Flask, request, jsonify
import mysql.connector
from catboost import CatBoostRegressor, Pool
import pandas as pd
import datetime

app = Flask(__name__)

# 모델 로드
model = CatBoostRegressor()
model.load_model('catboost_model_medi.cbm')

# 지역 목록 불러오기
area_names = pd.read_csv('./tn_visit_area_info_방문지정보_A.csv')['VISIT_AREA_NM'].drop_duplicates().tolist()

cat_features_names = [
    'GENDER', 'TRAVEL_STYL_1', 'TRAVEL_STYL_2', 'TRAVEL_STYL_3', 'TRAVEL_STYL_4',
    'TRAVEL_STYL_5', 'TRAVEL_STYL_6', 'TRAVEL_STYL_7', 'TRAVEL_STYL_8',
    'TRAVEL_MOTIVE_1', 'TRAVEL_MISSION_INT', 'VISIT_AREA_NM', 'TRAVEL_PURPOSE_INT'
]

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    query_text = data.pop('query_text')  # 자연어 입력

    # DB 연결
    conn = mysql.connector.connect(
        host="localhost", user="root", password="qwas1212!", database="travel_db"
    )
    cursor = conn.cursor()

    # 1. user_queries 테이블 저장
    cursor.execute("INSERT INTO user_queries (query_text) VALUES (%s)", (query_text,))
    conn.commit()
    user_query_id = cursor.lastrowid

    # 2. 예측 및 추천 저장
    results = []
    for area in area_names:
        input_data = data.copy()
        input_data['VISIT_AREA_NM'] = area
        df = pd.DataFrame([input_data])
        for col in cat_features_names:
            df[col] = df[col].astype(str)
        score = model.predict(Pool(df, cat_features=cat_features_names))[0]
        star = int(round(score))
        cursor.execute(
            "INSERT INTO recommendations (user_query_id, area, score, star) VALUES (%s, %s, %s, %s)",
            (user_query_id, area, score, star)
        )
        results.append({'area': area, 'score': score, 'star': star})

    conn.commit()
    conn.close()

    # 상위 5개만 반환
    results.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(results[:10])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
