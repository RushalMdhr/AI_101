import pandas as pd
import ollama
from psycopg2.extras import execute_values

from database import get_connection


CSV_FILE = "../../hr_interview_questions_cleaned.csv"

EMBEDDING_MODEL = "nomic-embed-text"

# Number of rows processed by PostgreSQL at once
DB_BATCH_SIZE = 1000

# Number of texts sent to Ollama in one embedding request
EMBED_BATCH_SIZE = 500

# Keep model loaded in memory
KEEP_ALIVE = "10m"


def clean_value(value):

    if pd.isna(value):
        return ""

    return str(value)


def create_embedding_text(row):

    question = clean_value(row.question)
    category = clean_value(row.category)
    role = clean_value(row.role)
    experience = clean_value(row.experience)
    difficulty = clean_value(row.difficulty)
    source_type = clean_value(row.source_type)
    keywords = clean_value(row.keywords)

    # Keep ideal_answer out of the embedding.
    # It is stored in PostgreSQL and retrieved after similarity search.

    return f"""
Question: {question}
Category: {category}
Role: {role}
Experience: {experience}
Difficulty: {difficulty}
Type: {source_type}
Keywords: {keywords}
"""


def create_embeddings(texts):

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=texts,
        keep_alive=KEEP_ALIVE
    )

    return response["embeddings"]


def process_batch(rows):

    # Create embedding text for every row
    texts = [
        create_embedding_text(row)
        for row in rows
    ]

    # Send multiple texts to Ollama in one request
    embeddings = create_embeddings(texts)

    records = []

    for row, embedding in zip(rows, embeddings):

        records.append(
            (
                clean_value(row.question),
                clean_value(row.category),
                clean_value(row.role),
                clean_value(row.experience),
                clean_value(row.difficulty),
                clean_value(row.source_type),
                clean_value(row.ideal_answer),
                clean_value(row.keywords),
                embedding
            )
        )

    return records


def import_data():

    print("Reading dataset...")

    df = pd.read_csv(CSV_FILE)

    total_rows = len(df)

    print(f"Total CSV rows: {total_rows:,}")

    conn = get_connection()
    cur = conn.cursor()

    # Check how many rows are already imported
    cur.execute("""
        SELECT COUNT(*)
        FROM interview_questions;
    """)

    already_imported = cur.fetchone()[0]

    print(
        f"Already in database: "
        f"{already_imported:,}"
    )

    if already_imported >= total_rows:

        print("\nAll rows are already imported.")

        cur.close()
        conn.close()

        return

    # Skip rows that are already in PostgreSQL
    df = df.iloc[already_imported:]

    remaining = len(df)

    print(
        f"Remaining rows: "
        f"{remaining:,}"
    )

    print(
        f"Starting from row: "
        f"{already_imported + 1:,}"
    )

    print(
        f"Database batch size: "
        f"{DB_BATCH_SIZE}"
    )

    print(
        f"Ollama embedding batch size: "
        f"{EMBED_BATCH_SIZE}"
    )

    print("\nStarting optimized import...\n")

    # Process database batches
    for start in range(
        0,
        remaining,
        DB_BATCH_SIZE
    ):

        batch = df.iloc[
            start:start + DB_BATCH_SIZE
        ]

        first_row = (
            already_imported
            + start
            + 1
        )

        last_row = (
            already_imported
            + start
            + len(batch)
        )

        print(
            f"Processing rows "
            f"{first_row:,} - "
            f"{last_row:,}"
        )

        # Convert dataframe rows to tuples
        rows = list(
            batch.itertuples(
                index=False
            )
        )

        all_records = []

        # Generate embeddings in smaller groups
        for embed_start in range(
            0,
            len(rows),
            EMBED_BATCH_SIZE
        ):

            embed_rows = rows[
                embed_start:
                embed_start + EMBED_BATCH_SIZE
            ]

            print(
                f"  Embedding "
                f"{first_row + embed_start:,} - "
                f"{min(first_row + embed_start + len(embed_rows) - 1, last_row):,}"
            )

            records = process_batch(
                embed_rows
            )

            all_records.extend(
                records
            )

        # Insert the complete database batch
        execute_values(
            cur,

            """
            INSERT INTO interview_questions (
                question,
                category,
                role,
                experience,
                difficulty,
                source_type,
                ideal_answer,
                keywords,
                embedding
            )
            VALUES %s
            """,

            all_records,

            page_size=500
        )

        conn.commit()

        total_imported = (
            already_imported
            + start
            + len(batch)
        )

        percentage = (
            total_imported
            / total_rows
        ) * 100

        print(
            f"Database progress: "
            f"{total_imported:,}/"
            f"{total_rows:,} "
            f"({percentage:.2f}%)"
        )

        print("Batch saved.\n")

    cur.close()
    conn.close()

    print("=" * 60)
    print("IMPORT COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    import_data()