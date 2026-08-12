import json

def saveMD(answer):
    with open("datas\\GROQ_ANSWERS.md","a") as f:
        f.write(answer)

def saveJSON(answer):
    with open("datas\\GROQ_ANSWERS_JSON.json", "a") as f:
        json.dump(answer, f, indent=2)  # ← Use json.dump(), not f.dump()