# 🤖 ResuMate – Smart Resume Shortlisting with LLMs

ResuMate is an intelligent, conversational HR screening tool that analyzes resumes against job descriptions using advanced LLMs. Designed to streamline hiring, it provides scoring, keyword analysis, and detailed feedback — all with just a few clicks.

![ResuMate Banner](https://img.shields.io/badge/Built%20With-LangChain%20%7C%20Streamlit%20%7C%20Groq-blue?style=for-the-badge)

---

## 🚀 Features

- 📄 Upload multiple PDF resumes
- 📋 Paste the Job Description
- 💡 Matches resumes with JD using Groq-powered LLMs (LLaMA3)
- 📊 Displays JD match %, missing keywords & brief summary
- 🧠 Detailed LLM-based evaluation reasoning
- 🎯 Filter candidates by match percentage
- 📥 Export results to CSV for easy use
- ⚡ Fast, secure, and minimal UI

---

## 📸 Screenshot

![screenshot](https://via.placeholder.com/800x400.png?text=Screenshot+Coming+Soon)

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **LangChain**
- **Groq API** (LLaMA 3 models)
- **dotenv** for secure API key handling
- **PyPDF2** for PDF parsing
- **Pandas** for table creation and CSV download

---

## 🧩 How It Works

1. **Upload PDF resumes**
2. **Paste job description**
3. **Click "RUN 🤖"**
4. Behind the scenes:
   - Extracts text from resumes
   - Prompts LLM to ev
