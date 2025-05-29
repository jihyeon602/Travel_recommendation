from flask import Flask, request, jsonify
from catboost import CatBoostRegressor
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import pandas as pd

# Flask 앱 초기화
app = Flask(__name__)

# 모델, 벡터라이저, 질문-답변 데이터 로드
model = CatBoostRegressor()
model.load_model("catboost_model.cbm")

with open("catboost_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# 🔸 질문-답변 CSV 파일 로드
qa_df = pd.read_csv("medical_QA_dataset.csv")
questions = qa_df["input_text"].tolist()
answers = qa_df["answer_text"].tolist()
domains = qa_df["domain"].tolist()  # 정수형 진료과 ID

# 🔹 진료과 매핑 딕셔너리
domain_map = {
    14: "산부인과",
    15: "소아청소년과",
    16: "응급의학과",
    17: "내과"
}

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        input_text = data.get("text", "")

        if not input_text:
            return jsonify({"error": "No input text provided"}), 400

        # 입력 벡터화
        input_vector = vectorizer.transform([input_text])
        similarities = []

        # 모든 질문에 대해 유사도 계산
        for i, q_vec in enumerate(vectorizer.transform(questions)):
            sim = cosine_similarity(input_vector, q_vec)[0][0]
            similarities.append((i, sim))

        # 유사도 상위 3개 선택
        top3 = sorted(similarities, key=lambda x: x[1], reverse=True)[:3]

        results = []
        for i, (idx, score) in enumerate(top3):
            domain_raw = domains[idx]
            try:
                domain_id = int(domain_raw)
                domain_name = domain_map.get(domain_id, "정보 없음")
            except:
                domain_name = "정보 없음"

            results.append({
                "rank": i + 1,
                "input_text": questions[idx],
                "answer_text": answers[idx],
                "score": round(score, 4),
                "domain": domain_name
            })

        return jsonify({"query": input_text, "results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
