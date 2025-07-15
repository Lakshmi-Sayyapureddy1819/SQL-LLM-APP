from dotenv import load_dotenv
load_dotenv()  # Load environment variables

import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Configure Gemini API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get SQL from Gemini
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    response = model.generate_content([prompt[0], question])
    return response.text

# Function to execute SQL query
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        print(f"Executing SQL: {sql}")
        cur.execute(sql)
        rows = cur.fetchall()
        return rows
    except Exception as e:
        print(f"SQL execution error: {e}")
        raise e
    finally:
        conn.close()

# STRICT Prompt for Gemini
prompt = [
    """
    You are an expert at converting English questions into SQL queries.
    The SQLite database has a single table named STUDENT with the following columns:

    ➤ NAME (Text)  
    ➤ CLASS (Text)  
    ➤ SECTION (Text)  
    ➤ MARKS (Integer)

    Return only the raw SQL query. Do not use markdown formatting or include explanations.

    Examples:
    Q: Show all students with more than 80 marks.  
    A: SELECT * FROM STUDENT WHERE MARKS > 80;

    Q: How many students are in section A?  
    A: SELECT COUNT(*) FROM STUDENT WHERE SECTION = "A";

    Q: Show name and marks of students in Data Science class.  
    A: SELECT NAME, MARKS FROM STUDENT WHERE CLASS = "Data Science";

    Only return valid SQL as plain text. No ``` or extra text.
    """
]


# Streamlit App UI
st.set_page_config(page_title="SQL Query Generator with Gemini")
st.header("🎓 Gemini-Powered SQL Data Explorer")

# Input box
question = st.text_input("Enter your question:", key="input")
submit = st.button("Ask")

# Process user query
if submit and question:
    raw_response = get_gemini_response(question, prompt)
    print("Raw Gemini output:", raw_response)

    # Clean the Gemini output
    clean_sql = raw_response.strip().replace("```", "").replace("sql", "").strip()
    print("Sanitized SQL:", clean_sql)

    # Run the SQL
    try:
        results = read_sql_query(clean_sql, "test.db")
        st.subheader("📄 Query Results:")
        if results:
            for row in results:
                st.text(str(row))
        else:
            st.warning("No results found.")
    except sqlite3.OperationalError as e:
        if "no such column" in str(e):
            st.error("❌ Your query used a column that doesn't exist. Use only: NAME, CLASS, SECTION.")
        elif "no such table" in str(e):
            st.error("❌ Table 'STUDENT' does not exist in test.db.")
        else:
            st.error(f"⚠️ SQL error: {e}")
