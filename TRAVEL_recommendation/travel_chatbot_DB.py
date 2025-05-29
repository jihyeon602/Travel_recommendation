# ✅ STEP 2. Streamlit 챗봇 - 사용자 입력 → 서버 요청 → 별점 출력
# 파일명: travel_chatbot_DB.py

import streamlit as st
from streamlit_chat import message
import requests
import re

# 챗봇 타이틀
st.header('여행지 추천 챗봇')
st.markdown("❗필수정보: 성별 / 연령(20~60대) / 여행기간 / 여행목적(숫자) / 동반자 수를 입력해주세요.")
st.markdown("➡️ 예: 여자 20대 3일 1 5명 ")
st.markdown("➡️ 예: 30대 남성 6일 6 1명 ")

# 세션 초기화
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []

# 별점 변환 함수
def make_star(score):
    stars = int(round(score))
    return '★' * stars + '☆' * (5 - stars)

# 사용자 입력 파싱 함수
def extract_number(text):
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None

def parse_input(text):
    try:
        tokens = text.strip().split()

        # 기본값 초기화
        gender = None
        age = None

        # 전체 텍스트에서 성별 추출
        if '남' in text:
            gender = '남'
        elif '여' in text:
            gender = '여'

        # 전체 텍스트에서 나이 추출
        # 1. "20대", "30대" 등 연령대 추출
        age_match = re.search(r'(\d{2})대', text)
        if age_match:
            age = int(age_match.group(1)) + 5  # 20대면 평균 25로 처리
        else:
            # 2. "20살", "25세", 숫자만 있을 경우
            for t in tokens:
                age_search = re.search(r'\d+', t)
                if age_search:
                    num = int(age_search.group())
                    if 10 < num < 100:
                        age = num
                        break

        # 여행 기간, 목적, 동반자 수 숫자 추출
        numbers = [int(n) for n in re.findall(r'\d+', text)]
        numbers = [n for n in numbers if n != age]  # age 중복 제거

        if gender is None or age is None or len(numbers) < 3:
            return None

        term, purpose, companions = numbers[:3]

        return {
            "query_text": text,
            "GENDER": gender,
            "AGE_GRP": float(age),
            "TRAVEL_TERM": term,
            "TRAVEL_PURPOSE_INT": purpose,
            "TRAVEL_COMPANIONS_NUM": float(companions),
            "TRAVEL_STYL_1": 3, "TRAVEL_STYL_2": 3, "TRAVEL_STYL_3": 3, "TRAVEL_STYL_4": 3,
            "TRAVEL_STYL_5": 3, "TRAVEL_STYL_6": 3, "TRAVEL_STYL_7": 3, "TRAVEL_STYL_8": 3,
            "TRAVEL_MOTIVE_1": 2, "TRAVEL_MISSION_INT": 2
        }

    except Exception:
        return None


# 입력 폼
with st.form('form', clear_on_submit=True):
    user_input = st.text_input('당신: ', '')
    submitted = st.form_submit_button('전송')

if submitted and user_input:
    st.session_state.past.append(user_input)
    parsed = parse_input(user_input)
    if parsed is None:
        st.session_state.generated.append("입력 형식이 올바르지 않습니다. (예: 여자 20 3 1 5)")
    else:
        try:
            response = requests.post('http://127.0.0.1:5000/predict', json=parsed)
            if response.ok:
                results = response.json()
                reply = "입력하신 조건으로 추천 결과를 찾았습니다! 상위 10곳을 알려드릴게요.\n\n"
                reply += '\n'.join([
                    f"{i+1}. {r['area']} - 점수: {r['score']:.3f} {make_star(r['score'])}"
                    for i, r in enumerate(results)
                ])
                st.session_state.generated.append(reply)
            else:
                st.session_state.generated.append("추천을 불러오는 중 오류가 발생했습니다.")
        except Exception as e:
            st.session_state.generated.append(f"서버 연결 실패: {e}")

# 대화 출력
for i in range(len(st.session_state.past)):
    message(st.session_state.past[i], is_user=True, key=f"{i}_user")
    if i < len(st.session_state.generated):
        message(st.session_state.generated[i], key=f"{i}_bot")
