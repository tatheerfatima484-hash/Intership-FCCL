📄 AI Resume Builder
An AI-powered resume builder built with Streamlit that lets you fill in your details, generate or enhance your "About Me" summary using Google Gemini AI, choose from multiple templates, and export a polished PDF resume — all data is also saved locally in a SQLite database.

✨ Features
📝 Dynamic input for personal info, education, experience, skills, and projects (add/remove entries freely)
🤖 AI-powered "About Me" section — write from scratch or enhance your own draft, in 4 different tones (Professional, Creative, Catchy, Detailed)
🎨 Multiple resume templates to choose from
📥 One-click PDF export (Jinja2 + WeasyPrint)
🗄️ SQLite database integration — every generated resume is saved for later reference
🌙 Light/Dark mode toggle
🛠️ Tech Stack
Component	Technology
Frontend / UI	Streamlit
AI	Google Gemini API (google-genai)
Templating	Jinja2
PDF Generation	WeasyPrint
Database	SQLite
🚀 Getting Started
1. Clone the repository
git clone https://github.com/your-username/ai-resume-builder.git
cd ai-resume-builder
2. Install dependencies
pip install -r requirements.txt
3. Set up environment variables
Copy .env.example to .env and add your own Gemini API key:

cp .env.example .env
Then edit .env:

GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-flash-latest
Get a free API key from Google AI Studio.

4. Run the app
streamlit run app.py
The app will open at http://localhost:8501.

📁 Project Structure
ai-resume-builder/
├── app.py              # Main Streamlit application
├── database.py         # SQLite schema + save logic
├── templates.py        # Resume HTML template definitions
├── requirements.txt    # Python dependencies
├── .env.example         # Sample environment file (no real secrets)
├── .gitignore
└── README.md
🗄️ Database
All submitted resumes are saved locally in resume_data.db (auto-created on first run, and excluded from version control). It stores:

resumes — personal info, about-me, skills
education, experience, projects — linked to each resume via resume_id
You can inspect this file using the SQLite Viewer or SQLTools extension in VS Code.
