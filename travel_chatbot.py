import streamlit as st
import requests

st.set_page_config(page_title="여행지 추천", layout="centered")
st.title("😉 여행지 추천")
st.markdown("여행 성향을 선택하고 아래 버튼을 누르면 최적의 여행지를 추천해드립니다.")

# 가로형 라디오버튼
gender = st.radio("성별", options=["남", "여"], horizontal=True)
age = st.selectbox("나이", options=list(range(10, 60, 10)), index=3)

style_1 = st.radio("자연1 ~ 도시7", options=list(range(1, 8)), horizontal=True)
style_2 = st.radio("숙박1 ~ 당일7", options=list(range(1, 8)), horizontal=True)
style_3 = st.radio("지역 인식도 1~7", options=list(range(1, 8)), horizontal=True)
style_4 = st.radio("가격 정도 1~7", options=list(range(1, 8)), horizontal=True)
style_5 = st.radio("활동 여부 1~7", options=list(range(1, 8)), horizontal=True)
style_6 = st.radio("인지도 1~7", options=list(range(1, 8)), horizontal=True)
style_7 = st.radio("계획도 1~7", options=list(range(1, 8)), horizontal=True)
style_8 = st.radio("사진 중요도 1~7", options=list(range(1, 8)), horizontal=True)

motive = st.selectbox("여행 동기 (코드)", options=list(range(1, 11)))
companions = st.selectbox("동반자 수", options=list(range(1, 11)))
mission = st.selectbox("여행 미션 코드", options=list(range(1, 11)))
purpose = st.selectbox("여행 목적 코드", options=list(range(1, 11)))
term = st.selectbox("여행 기간 (일수)", options=list(range(1, 15)))

if st.button("여행지 추천받기"):
    input_data = {
        "GENDER": gender,
        "AGE_GRP": float(age),
        "TRAVEL_STYL_1": style_1,
        "TRAVEL_STYL_2": style_2,
        "TRAVEL_STYL_3": style_3,
        "TRAVEL_STYL_4": style_4,
        "TRAVEL_STYL_5": style_5,
        "TRAVEL_STYL_6": style_6,
        "TRAVEL_STYL_7": style_7,
        "TRAVEL_STYL_8": style_8,
        "TRAVEL_MOTIVE_1": motive,
        "TRAVEL_COMPANIONS_NUM": float(companions),
        "TRAVEL_MISSION_INT": mission,
        "TRAVEL_PURPOSE_INT": purpose,
        "TRAVEL_TERM": term
    }

    try:
        res = requests.post("http://127.0.0.1:5000/predict", json=input_data)
        res.raise_for_status()
        recommendations = res.json()

        st.subheader("📍 추천 여행지 TOP 10")
        for idx, rec in enumerate(recommendations, 1):
            st.write(f"{idx}. {rec['AREA']} - 점수: {rec['SCORE']:.2f}")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
