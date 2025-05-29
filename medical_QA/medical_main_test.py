import requests

url = "http://127.0.0.1:8080/predict"
sample_question = {
    "text": "임신 중 엽산이 왜 중요한가요?"
}

response = requests.post(url, json=sample_question)
print(response.json())