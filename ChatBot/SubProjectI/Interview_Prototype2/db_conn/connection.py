import psycopg2

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="postgres",
        user="postgres",
        password="rushal"
    )
    conn.autocommit = True
    print("Connected successfully!")

except psycopg2.Error as e:
    print("POSTGRESQL ERROR:")
    print(str(e))

cur = conn.cursor()

def fetch(SQLquery):
    cur.execute(SQLquery)
    datas = cur.fetchall()
    col = cur.description
    columns = [c.name for c in col]
    return datas, columns

def get_role_questions(role,need_col=False):
    cur.execute("""SELECT * FROM public.interview_questions
    WHERE role = %s 
    ORDER BY id ASC 
    LIMIT 100;
""", (role,))
    datas = cur.fetchall()
    if need_col:
        col = cur.description
        columns = [c.name for c in col]
        return datas, columns
    return datas
