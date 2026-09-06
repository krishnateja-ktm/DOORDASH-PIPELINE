import os
import json
import snowflake.connector
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

model = "gpt-4o-mini"
topics = ["delivery", "food quality", "service", "packaging", "pricing", "other"]
sample_n = 5

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

system_prompt = f"""
You classify customer reviews for a food delivery app.

For the review you are given, return:
- sentiment_label: positive, negative, or neutral
- sentiment_score: a number between -1.0 and 1.0
- topic: one of {topics}
- key_issue: a short phrase of 6 words or less that describes the main issue in the review, if any. If there is no issue, return Null.

reply as JSON in this exact format:

{{
    "sentiment_label": "<sentiment_label>",
    "sentiment_score": <sentiment_score>,
    "topic": "<topic>",
    "key_issue": "<key_issue>"
}}
"""

def get_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
    
def create_output_table(cursor):
    cursor.execute("CREATE SCHEMA IF NOT EXISTS DOORDASH.AI")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DOORDASH.AI.REVIEW_ENRICHED (
            review_id STRING,
            sentiment_label STRING,
            sentiment_score FLOAT,
            topic STRING,
            key_issue STRING,
            model STRING,
            enriched_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        
def get_reviews_to_enrich(cursor):
    cursor.execute(f"""
        SELECT review_id, comment
        FROM DOORDASH.RAW.REVIEWS
        WHERE review_id NOT IN (SELECT review_id FROM DOORDASH.AI.REVIEW_ENRICHED)
        LIMIT {sample_n}
    """)
    return cursor.fetchall()

def classify_review(comment):
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": comment}
        ]
    )
    answer = response.choices[0].message.content
    return json.loads(answer)

def save_results(cursor, results):
    """Insert all the enriched rows into Snowflake in one go."""
    print(f"Saving {len(results)} enriched reviews to Snowflake...")
    cursor.executemany(
        """
        INSERT INTO DOORDASH.AI.REVIEW_ENRICHED
            (review_id, sentiment_label, sentiment_score, topic, key_issue, model)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        results)
    
def main():
    conn = get_connection()
    cursor = conn.cursor()
    
    create_output_table(cursor)
    
    reviews = get_reviews_to_enrich(cursor)
    
    if len(reviews) == 0:
        print("No new reviews to enrich.")
        return
    
    print(f"Enriching {len(reviews)} reviews...")
    
    results = []
    for review_id, comment in reviews:
        try:
            labels = classify_review(comment)
            results.append({
                "review_id": review_id,
                "sentiment_label": labels["sentiment_label"],
                "sentiment_score": labels["sentiment_score"],
                "topic": labels["topic"],
                "key_issue": labels["key_issue"],
                "model": model
            })
        except Exception as e:
            print(f"Error occured while processing review {review_id}: {e}")

    save_results(cursor, results)
    print(f"Saved {len(results)} enriched reviews to snowflake.")
    conn.commit()
    cursor.close()
    conn.close()
    
if __name__ == "__main__":
    main()