def update_prompt():
    print("updating your prompt")
    choice = input("want to type prompt yourself? Y/N : ").lower()
    if choice =="y":
        system_prompt = input("write your prompt : ")
    else:
        system_prompt = """You are a helpful, friendly assistant named Ollie.
    Always respond in 2-3 sentences maximum.
    If asked something you don't know, say "I'm not sure, but I can look that up!"
    Keep responses clear and simple."""

    return system_prompt