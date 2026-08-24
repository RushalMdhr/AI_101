from AIs.ollama_tools import use_ollama_chat

def thinker_loop(query):
    # System prompt that encourages self-reflection
    message = [{
        "role": "system",
        "content": "You are thinking step-by-step. Ask yourself questions, explore ideas, then provide a final answer. End with 'exit' when ready."
    }]
    message.append({"role": "user", "content": query})
    
    while True:
        res = use_ollama_chat(message)
        bot_says = res["message"]["content"]
        print(f"🧠 Thought: {bot_says}\n")
        
        if bot_says.strip().lower() == "exit":
            break
            
        message.append({"role": "assistant", "content": bot_says})
        
        # CRITICAL: Re-prompt with the original user query to keep it on track
        message.append({"role": "user", "content": f"Continue thinking about: {query}"})
    
    # Return the last thought before 'exit'
    return message[-2]["content"] if len(message) > 2 else query