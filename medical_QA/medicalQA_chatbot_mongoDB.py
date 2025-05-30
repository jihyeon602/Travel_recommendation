import streamlit as st
from streamlit_chat import message
import requests
from pymongo import MongoClient
from datetime import datetime

# ✅ MongoDB 연결
client = MongoClient("mongodb://user:password@host:port/dbname")
db = client["medicalqa"]
log_collection = db["chat_logs"]

st.header("🩺 의료 Q & A 챗봇")
st.markdown("❓ 증상, 질병명, 나이, 성별 등 자유롭게 질문하세요.")

# 세션 상태 초기화
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []

# 입력 폼
with st.form("form", clear_on_submit=True):
    user_input = st.text_input("질문을 입력하세요:", "")
    submitted = st.form_submit_button("전송")

if submitted and user_input:
    st.session_state.past.append(user_input)
    try:
        response = requests.post("http://127.0.0.1:8080/predict", json={"text": user_input})
        if response.ok:
            result = response.json().get("results", [])
            if result:
                reply = "🔎 유사한 질문 및 추천 답변:\n\n"
                for r in result:
                    domain = r.get("domain", "정보 없음")
                    reply += (
                        f"**Q:** {r['input_text']}\n"
                        f"**A:** {r['answer_text']}\n"
                        f"**유사도:** {r['score']:.4f}  \n"
                        f"🏥 **추천 진료과/병원:** {domain}\n\n"
                    )
            else:
                reply = "⚠️ 관련된 정보를 찾을 수 없습니다."
        else:
            reply = "❌ 서버 오류가 발생했습니다."
        st.session_state.generated.append(reply)

        # MongoDB 로그 저장
        log_collection.insert_one({
            "user_input": user_input,
            "response": reply,
            "timestamp": datetime.now()
        })

    except Exception as e:
        error_msg = f"❌ 서버 연결 실패: {e}"
        st.session_state.generated.append(error_msg)
        log_collection.insert_one({
            "user_input": user_input,
            "response": error_msg,
            "timestamp": datetime.now()
        })

# 대화 출력
for i in range(len(st.session_state.past)):
    message(st.session_state.past[i], is_user=True, key=f"{i}_user", avatar_style="miniavs")
    if i < len(st.session_state.generated):
        message(st.session_state.generated[i], key=f"{i}_bot", avatar_style="bottts")
