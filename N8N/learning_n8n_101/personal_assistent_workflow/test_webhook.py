import requests

user_message = "can you tell me whats tomorrows event on my calendar. use the calendar tool"

request_message = {"message" : user_message}

url="http://localhost:5678/webhook-test/38efd78b-993b-4dd9-ac4b-a0d616f92104"

response = requests.post(url, json=request_message)

print(response.status_code)
print(response.json()[0]["output"])