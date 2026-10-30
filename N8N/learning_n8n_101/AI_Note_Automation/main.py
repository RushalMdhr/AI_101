import requests

user_message = "I hate you."

request_message = {"message" : user_message}

url="http://localhost:5678/webhook-test/2ebe2273-2972-4125-b4c6-9975b77d6641"

response = requests.post(url, json=request_message)

print(response.status_code)
print("AI : ",response.json()[0]['text'])