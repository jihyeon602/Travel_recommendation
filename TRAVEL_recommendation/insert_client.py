import requests

url = 'http://127.0.0.1:5000/insert'

test_data = {
    'gender': '여',
    'age_grp': 20.0,
    'travel_styl_1': 2,
    'travel_styl_2': 1,
    'travel_styl_3': 4,
    'travel_styl_4': 3,
    'travel_styl_5': 5,
    'travel_styl_6': 2,
    'travel_styl_7': 4,
    'travel_styl_8': 3,
    'travel_motive_1': 2,
    'travel_companions_num': 2.0,
    'travel_mission_int': 3,
    'travel_purpose_int': 1,
    'travel_term': 2
}

response = requests.post(url, json=test_data)
print(response.json())