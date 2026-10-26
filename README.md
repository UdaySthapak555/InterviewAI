# 🤖 InterviewAI

### AI-Powered Personalized Mock Interview Platform

InterviewAI is an AI-powered mock interview platform that analyzes a candidate's resume, generates personalized interview questions, evaluates answers, and provides a detailed performance report.

The application uses Google Gemini AI to create a personalized interview experience based on the candidate's resume, selected job role, interview type, and difficulty level.

---

## ✨ Features

### 📄 Resume Upload and Analysis

- Upload resumes in PDF format.
- Extract text automatically from the uploaded resume.
- Analyze candidate skills, projects, and technical background using AI.
- Identify strong areas and interview focus areas.

### 🎯 Personalized Mock Interview

- Generates exactly 10 personalized interview questions.
- Questions are generated based on the candidate's resume.
- Supports multiple target job roles.
- Supports different interview types.
- Adjustable difficulty levels.

### 🤖 AI Answer Evaluation

Each answer is evaluated based on:

- Technical correctness
- Clarity
- Technical depth
- Relevance to the question

The AI provides:

- Score out of 10
- Answer strengths
- Areas for improvement
- A technically improved example answer

### 📊 Performance Report

After completing the interview, InterviewAI generates:

- Overall interview score
- Highest score
- Lowest score
- Question-wise performance
- Professional performance summary
- Top strengths
- Areas for improvement
- Personalized improvement roadmap
- Interview readiness assessment

---

## 🛠️ Tech Stack

### Frontend

- Streamlit

### Backend & AI Integration

- Python
- Google Gemini API

### Libraries

- Streamlit
- Google GenAI SDK
- python-dotenv
- PyPDF

### Core Concepts

- Generative AI
- Prompt Engineering
- Resume Parsing
- Personalized Question Generation
- AI Answer Evaluation
- JSON Response Validation
- Session State Management
- Error Handling and Retry Logic

---

## 📂 Project Structure

```text
InterviewAI/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
│
├── utils/
│   ├── __init__.py
│   ├── ai_engine.py
│   └── resume_parser.py
│
└── screenshots/