# GenAI Intern Assignment: RAG Application

## Overview
This project is a Retrieval-Augmented Generation (RAG) application that allows users to ask questions about a MySQL database and receive user-friendly answers using an LLM (via LangChain).

## Features
- Chat interface (Streamlit)
- MySQL database integration
- Retrieval-Augmented Generation using LangChain and OpenAI

## Setup Instructions

### 1. Clone the repository
```
git clone <your-repo-url>
cd <project-directory>
```

### 2. Set up Python environment
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Import the MySQL database
- Use the provided SQL file (see `db/` folder) to import into your MySQL instance.

### 4. Configure environment variables
- Create a `.env` file in the project root with the following:
```
MYSQL_URI=mysql+pymysql://user:password@host:port/dbname
```

### 5. Run the application
```
streamlit run streamlit_app.py
```

## Usage
- Open the Streamlit app in your browser.
- Ask questions about the database in plain English.

## Submission
- Source code, README, and a demo video.

--- 
