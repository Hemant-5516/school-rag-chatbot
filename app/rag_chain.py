import os
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from langchain.llms import HuggingFacePipeline
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from sqlalchemy import text
from app.db_utils import engine
import re

# Load the model and tokenizer once at startup
model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
hf_pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

llm = HuggingFacePipeline(pipeline=hf_pipe)

prompt_template = PromptTemplate(
    input_variables=["question", "context"],
    template="""
You are an expert assistant for a school database. Use the following context from the database to answer the user's question in plain English.

Context:
{context}

Question: {question}
Answer:
"""
)

llm_chain = LLMChain(llm=llm, prompt=prompt_template)

def fetch_relevant_data(question: str) -> str:
    keywords = [
        ("student", "students"),
        ("parent", "parents"),
        ("class", "classes"),
        ("section", "sections"),
        ("subject", "subjects"),
        ("mark", "marks"),
        ("scholarship", "scholarships"),
        ("bank", "bankdetails"),
    ]
    table = None
    for k, t in keywords:
        if k in question.lower():
            table = t
            break
    if not table:
        table = "students"
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table} LIMIT 5"))
        rows = result.fetchall()
        columns = result.keys()
    context = "\n".join([
        ", ".join(f"{col}: {row[i]}" for i, col in enumerate(columns)) for row in rows
    ])
    return context or f"No data found in table {table}."

def relational_query(question: str):
    q = question.lower()
    # Parent (mother/father) of student
    parent_match = re.match(r"(mother|father) of ([a-zA-Z]+) ?([a-zA-Z]*)", q)
    if parent_match:
        parent_type = parent_match.group(1).capitalize()
        first_name = parent_match.group(2).capitalize()
        last_name = parent_match.group(3).capitalize() if parent_match.group(3) else ""
        with engine.connect() as conn:
            student = conn.execute(
                text("SELECT roll_no FROM students WHERE first_name=:fn AND last_name=:ln"),
                {"fn": first_name, "ln": last_name}
            ).fetchone()
            if not student:
                return "Student not found."
            prefix = 'Mrs.%' if parent_type == 'Mother' else 'Mr.%'
            parent = conn.execute(
                text("SELECT parent_name FROM parents WHERE student_roll_no=:roll AND parent_name LIKE :prefix"),
                {"roll": student.roll_no, "prefix": prefix}
            ).fetchone()
            if not parent:
                return f"{parent_type} not found."
            return parent.parent_name
    # <student> mother's name or <student> father's name
    parent_match2 = re.match(r"([a-zA-Z]+) ?([a-zA-Z]*) (mother|father)'?s name", q)
    if parent_match2:
        first_name = parent_match2.group(1).capitalize()
        last_name = parent_match2.group(2).capitalize() if parent_match2.group(2) else ""
        parent_type = parent_match2.group(3).capitalize()
        with engine.connect() as conn:
            student = conn.execute(
                text("SELECT roll_no FROM students WHERE first_name=:fn AND last_name=:ln"),
                {"fn": first_name, "ln": last_name}
            ).fetchone()
            if not student:
                return "Student not found."
            prefix = 'Mrs.%' if parent_type == 'Mother' else 'Mr.%'
            parent = conn.execute(
                text("SELECT parent_name FROM parents WHERE student_roll_no=:roll AND parent_name LIKE :prefix"),
                {"roll": student.roll_no, "prefix": prefix}
            ).fetchone()
            if not parent:
                return f"{parent_type} not found."
            return parent.parent_name
    # Bank of student
    bank_match = re.match(r"bank of ([a-zA-Z]+) ?([a-zA-Z]*)", q)
    if bank_match:
        first_name = bank_match.group(1).capitalize()
        last_name = bank_match.group(2).capitalize() if bank_match.group(2) else ""
        with engine.connect() as conn:
            student = conn.execute(
                text("SELECT bank_account_id FROM students WHERE first_name=:fn AND last_name=:ln"),
                {"fn": first_name, "ln": last_name}
            ).fetchone()
            if not student:
                return "Student not found."
            bank = conn.execute(
                text("SELECT bank_name FROM bankdetails WHERE bank_account_id=:bid"),
                {"bid": student.bank_account_id}
            ).fetchone()
            if not bank:
                return "Bank details not found."
            return bank.bank_name
    return None

def answer_question(question: str) -> str:
    rel_answer = relational_query(question)
    if rel_answer is not None:
        return rel_answer
    context = fetch_relevant_data(question)
    answer = llm_chain.run({"question": question, "context": context})
    return answer.strip() 