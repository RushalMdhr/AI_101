from database import get_connection


def setup_database():

    conn = get_connection()
    cur = conn.cursor()

    # Enable pgvector
    cur.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
    """)
 # Remove old table
    cur.execute("""
        DROP TABLE IF EXISTS interview_questions;
    """)
    # Create table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interview_questions (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL,
            category TEXT,
            role TEXT,
            experience TEXT,
            difficulty TEXT,
            source_type TEXT,
            ideal_answer TEXT,
            keywords TEXT,
            embedding VECTOR(768)
        );
    """)

    # Create vector similarity index
    cur.execute("""
        CREATE INDEX IF NOT EXISTS interview_questions_embedding_idx
        ON interview_questions
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """)

    conn.commit()

    cur.close()
    conn.close()

    print("Database setup completed.")


if __name__ == "__main__":
    setup_database()