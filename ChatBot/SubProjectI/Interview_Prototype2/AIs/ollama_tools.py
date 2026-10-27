import ollama

def use_ollama_chat(message):
    return ollama.chat(model='llama3.2:latest', messages=message)
