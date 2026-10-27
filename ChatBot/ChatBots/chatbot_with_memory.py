import ollama
from PromptingAI import update_prompt

messages = [{"role": "system", "content": "You are a helpful assistant"}]

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit" or user_input.lower() == "exit()":
        break
    elif user_input.lower() == "prompt":
        system_prompt = update_prompt()
        print(system_prompt)
        messages[0]["content"] = system_prompt
        continue
    # elif user_input.lower()=
    messages.append({"role": "user", "content": user_input})
    response = ollama.chat(model='llama3.2:latest', messages=messages, 
                           options={
                                "temperature": 0.9,      # Creative but not wild
                                "top_p": 0.9,            # Standard
                                # "num_predict": 200,      # Short story (~200 tokens)
                                # "num_ctx": 4096,         # Enough for context
                                "repeat_penalty": 1.1,   # Avoid repetition
                                "seed": 123,             # Reproducible
                                "mirostat": 1            # Adaptive creativity
                            })
    messages.append({"role": "assistant", "content": response['message']['content']})
    print(f"Bot: {response['message']['content']}")
    # print(f"Messages : {messages}")