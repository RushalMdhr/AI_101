import requests

def chat_with_model(system_prompt, user_message):
    full_prompt = f"""System: {system_prompt}

    User: {user_message}"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": full_prompt,
            "stream": False
        }
    )
    return response.json()["response"]

system = """Act like a professional HR that ask questions for a job interview. You will ask questions about the candidate's experience, skills, and motivation for applying to the job. You will also provide feedback and advice on how to improve their chances of getting hired."""

user_input = "My name is Rushal and i can code very fast. i know MERN and ai ml"
print("Sending message...")
print("─" * 50)
response = chat_with_model(system, user_input)
print(response)