import ollama
from PromptingAI import update_prompt

messages = [{"role": "system", "content": "You are a helpful assistant"}]

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    elif user_input.lower() == "prompt":
        system_prompt = update_prompt()
        messages[0]["content"] = system_prompt
        continue
    # elif user_input.lower()=
    messages.append({"role": "user", "content": user_input})
    response = ollama.chat(model='llama3.2:latest', messages=messages)
    messages.append({"role": "assistant", "content": response['message']['content']})
    print(f"Bot: {response['message']['content']}")
    # print(f"Messages : {messages}")