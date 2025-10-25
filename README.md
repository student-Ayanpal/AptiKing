👑 AptiKing — Your All-in-One Aptitude Portal

A comprehensive aptitude preparation platform built with Streamlit.
AptiKing helps students practice, learn, and master Quantitative, Logical, and Verbal reasoning — all in one place.

🌟 Overview

AptiKing is an interactive aptitude portal featuring customizable quizzes, study materials, AI-powered doubt solving, and progress tracking.
It’s designed to make aptitude preparation smarter, faster, and more engaging.

✨ Features
🧑‍💻 User System

🔐 Secure Authentication with password hashing (hashlib)

💾 Session Persistence via streamlit-local-storage

🧠 Custom Quiz Engine

Choose by:

Category: Quantitative / Logical / Verbal

Topics: Select multiple from DB

Difficulty: Easy / Medium / Hard / All

No. of Questions & Time Limit — user-defined

⏰ Live Countdown Timer (streamlit-autorefresh) with auto-submit

📊 Instant Results showing accuracy and answer breakdown

📈 Progress Dashboard

📉 Line graph (st.line_chart) of your last 5 test scores

🧾 Full test history table from the database

📚 Study Hub

📘 Downloadable Cheatsheets (PDFs)

▶️ Smart Video Recommendations — YouTube videos fetched dynamically using YouTube Data API v3

🤖 AI Doubt Solver

💬 Powered by Google Gemini API for 24×7 aptitude doubt assistance

🎨 Dynamic UI

🧩 Multi-page layout with custom-styled buttons and responsive design

🚀 Tech Stack
Layer	Technologies
Frontend	Streamlit

Backend	Python 3

Database	MySQL

Core Libraries	pandas, google-generativeai, google-api-python-client, streamlit-local-storage, streamlit-autorefresh, mysql-connector-python
⚙️ Getting Started
1️⃣ Prerequisites

🐍 Python 3.10+

🗄️ MySQL Server (e.g. WAMP
 / XAMPP
)

🔑 Google API Keys for Gemini & YouTube Data API

2️⃣ Clone the Repository
git clone https://github.com/student-Ayanpal/AptiKing

3️⃣ Set Up the Environment
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

4️⃣ Set Up the Database
CREATE DATABASE aptitude_db;
USE aptitude_db;


Run your database_schema.sql file to create the following tables:
users, topics, questions, tests, test_results

💡 (Optional) Insert sample data into topics and questions for quick testing.

5️⃣ Configure Secrets

Create a .streamlit folder in your root directory, then add a secrets.toml file:

# .streamlit/secrets.toml

# MySQL Database Credentials
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "aptitude_db"

# API Keys
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY_HERE"

6️⃣ Run the App
streamlit run Home.py


Your app will open automatically at:
👉 http://localhost:8501

🧩 Future Enhancements

🏆 Leaderboard with global ranking

📱 Mobile-responsive layout

🗂️ Admin panel for managing questions & users

🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to fork this repo and submit a PR.

💖 Support

If you like this project, give it a ⭐ on GitHub — it really helps!

🧑‍💼 Author

Ayan Pal
📬 GitHub
