import requests

url = 'http://127.0.0.1:5000/predict'  # Flask server URL

# Example traveler data
traveler_data = {
    'GENDER': '남',
    'AGE_GRP': 30.0,
    'TRAVEL_STYL_1': 1,
    'TRAVEL_STYL_2': 1,
    'TRAVEL_STYL_3': 1,
    'TRAVEL_STYL_4': 4,
    'TRAVEL_STYL_5': 1,
    'TRAVEL_STYL_6': 4,
    'TRAVEL_STYL_7': 2,
    'TRAVEL_STYL_8': 6,
    'TRAVEL_MOTIVE_1': 3,
    'TRAVEL_COMPANIONS_NUM': 4.0,
    'TRAVEL_MISSION_INT': 5
}

response = requests.post(url, json=traveler_data)

if response.ok:
    recommendations = response.json()
    print('Top 10 Recommended Places:')
    for idx, rec in enumerate(recommendations, 1):
        print(f"{idx}. {rec['area']} - Score: {rec['score']:.2f}")
else:
    print("Error:", response.status_code, response.text)
