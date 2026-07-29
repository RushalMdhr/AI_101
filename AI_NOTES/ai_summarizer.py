import ollama

def summarize_text(text):

    prompt = f"""
Convert this classroom lecture into clean markdown notes.

Rules:
- Create headings
- Create bullet points
- Keep important concepts
- Remove useless filler words
- Keep language simple

Lecture:
{text}
"""

    response = ollama.chat(
        model='phi3',
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )

    return response['message']['content']