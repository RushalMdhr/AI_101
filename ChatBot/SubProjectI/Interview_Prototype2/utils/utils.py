from AIs.ollama_tools import use_ollama_chat
from db_conn.connection import fetch,get_role_questions
import pandas as pd, json

def checkRole(role):
    data,col  = fetch("SELECT DISTINCT role FROM public.interview_questions;")
    roles = []
    for x in data:  
        roles.append(x[0])
    prompt = f"""
Roles available: {roles}
User's interest is given by user:
Return ONLY one role from the available list that best matches user's interest.
If NO match exists, return just 'RETRY'.
and your job is not to reject them but to make sure what the user wants any spelling correction might be good
user can say anything but try your best what user wants dont reject cause user is telling product mnger instead of Product Mananger
you must be able to know what user wants 
and dont give too much explain what every you think is from the choice roles u ll send only that value else no other word
"""
    print("ollama thinking .....")
    res = use_ollama_chat([{"role":"system","content":prompt},{"role":"user","content":role}])
    exact_role = res.message.content
    print(exact_role)
    exact_role = exact_role.strip().strip('"').strip("'")
    if exact_role not in roles:
        return "Ops _ Not In Role"
    else:
        return exact_role



def all_in_one(role):
    exact_role = checkRole(role)
    data = get_role_questions(exact_role,True)
    df = pd.DataFrame(data[0],columns=data[1])
    print(df)
    context = json.dumps(df.to_dict('records'), indent=2)

    prompt = f"""
You are an AI interview assistant.

Use the following interview knowledge to answer the user's question.

CONTEXT:
{context}

USER QUESTION:
{exact_role}

Answer naturally and clearly.
If the context does not contain enough information, say so instead of making up information.
"""
    print("ollama responding .....")
    res = use_ollama_chat([{"role":"assistent","content":prompt},{"role":"user","content":"ask me a question"}])
    print(res.message.content)