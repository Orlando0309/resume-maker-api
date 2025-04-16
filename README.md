# 📄 Resume Maker API

An intelligent API that uses **Gemini AI** to enhance and optimize resumes — helping users create polished, professional CVs with AI-powered insights.

---

## ✨ Features

- 🔐 **User Authentication**
- 📄 **Resume Creation & Management**
- 🎨 **AI-Powered Resume Optimization**
- 🖨️ **PDF Export**
- 📊 **User Dashboard**
- 📚 **Gemini Integration for Resume Enhancement**

---

## 📂 Project Structure

```console
resume-maker-api/
├── .env.example        # Environment variable sample
├── LLM/                # AI models and logic (Gemini / LangChain architecture)
│   └── agents.py       # Agents to process the job and the resume
│   └── generate_resume_prompt.py       # Agents to process the job and the resum
│   └── load_prompt.py       # helper for loading prompt
│   └── utils.py       # helpers
│   └── prompt/       # folder to put all prompt
├── .gitignore
├── auth.py             # Authentication logic
├── dashboard.py        # User dashboard endpoint
├── database.py         # Database connection setup
├── main.py             # Main application entrypoint
├── models.py           # Database models
├── optimization.py     # Resume optimization logic (Gemini AI)
├── pdf.py              # Resume PDF generation
├── resumes.py          # Resume CRUD operations
├── schemas.py          # Pydantic schemas
├── script.py           # Utility scripts
├── templates/          # resume templates for rendering
├── userInfo.py         # User information management
├── utils.py            # Helper functions
└── __pycache__/        # Python cache

```
## 🚀 Getting Started

1. Clone the repository

```console
git clone https://github.com/Orlando0309/resume-maker-api.git
cd resume-maker-api
```

2. Install dependencies

```console
pip install -r requirements.txt
```

3. Setup environment

Copy .env.example to .env and add your API keys and configurations.

4. Run the application

```console
python main.py
```

## 🛠️ Tech Stack

    Python 3.11+

    FastAPI

    SQLAlchemy

    Pydantic

    Gemini AI

    Jinja2 Templates

    WeasyPrint (for PDF generation)

## 🎯 Roadmap Ideas

    ✅ Resume optimization with Gemini

    ✅ PDF generation

    🔄 Create own model for the resume

    🔄 AI-driven skill suggestions

    🔄 API documentation (Swagger)

🤝 Contributing

Pull requests are welcome!
Feel free to open an issue for suggestions or improvements.
📃 License

MIT

