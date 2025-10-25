# 👑 Aptiking - Your All-in-One Aptitude Portal

Aptiking is a comprehensive web application built with Streamlit, designed to be a one-stop solution for students preparing for aptitude tests. It provides customizable quizzes, study materials, an AI-powered doubt solver, and progress tracking to help users master quantitative, logical, and verbal reasoning.

---

## ✨ Features

* **Secure User Authentication:** Full user registration and login system with password hashing (`hashlib`) and session persistence using `streamlit-local-storage`.
* **Custom Quiz Engine:** Users can create fully customized tests based on:
    * **Category:** Quantitative, Logical, and Verbal.
    * **Topics:** Select one or more topics from the database.
    * **Difficulty:** Easy, Medium, Hard, or All.
    * **Number of Questions:** User-defined.
    * **Time Limit:** User-defined.
* **Live Quiz Interface:** A real-time quiz environment with a live countdown timer (`streamlit-autorefresh`) and auto-submission when time runs out.
* **Instant Results:** Immediate scoring, accuracy calculation, and a detailed breakdown of correct, incorrect, and unattempted questions.
* **Progress Dashboard:**
    * A line graph (`st.line_chart`) visualizing scores from the user's last 5 tests.
    * A complete table of the user's test history fetched from the database.
* **Study Hub:**
    * Downloadable PDF cheatsheets for specific topics.
    * **Video Recommendations:** Automatically fetches and displays relevant YouTube video thumbnails and links for the selected topic using the YouTube Data API v3.
* **AI Doubt Solver:** An integrated chatbot (powered by the Google Gemini API) to answer any aptitude-related questions 24/7.
* **Dynamic UI:** A clean, multi-page interface with custom-styled buttons and containers.

---

## 🚀 Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Backend:** [Python 3](https://www.python.org/)
* **Database:** [MySQL](https://www.mysql.com/)
* **Core Libraries:**
    * `pandas`
    * `google-generativeai` (Gemini API)
    * `google-api-python-client` (YouTube Data API)
    * `streamlit-local-storage` (Login Persistence)
    * `streamlit-autorefresh` (Quiz Timer)
    * `mysql-connector-python` (Database Connection)

---

## 💻 Getting Started

Follow these steps to set up and run the project locally.

### 1. Prerequisites

* Python 3.10+
* A MySQL server (e.g., [WAMP](https://www.wampserver.com/en/) or [XAMPP](https://www.apachefriends.org/index.html))
* A Google account to get API keys.

### 2. Clone the Repository

```bash
git clone https://github.com/student-Ayanpal/AptiKing

Here is a complete README.md file for your Aptiking project. You can copy this, save it as README.md in your main project folder (e.g., Aptiking/), and upload it to GitHub.

Markdown

# 👑 Aptiking - Your All-in-One Aptitude Portal

Aptiking is a comprehensive web application built with Streamlit, designed to be a one-stop solution for students preparing for aptitude tests. It provides customizable quizzes, study materials, an AI-powered doubt solver, and progress tracking to help users master quantitative, logical, and verbal reasoning.

---

## ✨ Features

* **Secure User Authentication:** Full user registration and login system with password hashing (`hashlib`) and session persistence using `streamlit-local-storage`.
* **Custom Quiz Engine:** Users can create fully customized tests based on:
    * **Category:** Quantitative, Logical, and Verbal.
    * **Topics:** Select one or more topics from the database.
    * **Difficulty:** Easy, Medium, Hard, or All.
    * **Number of Questions:** User-defined.
    * **Time Limit:** User-defined.
* **Live Quiz Interface:** A real-time quiz environment with a live countdown timer (`streamlit-autorefresh`) and auto-submission when time runs out.
* **Instant Results:** Immediate scoring, accuracy calculation, and a detailed breakdown of correct, incorrect, and unattempted questions.
* **Progress Dashboard:**
    * A line graph (`st.line_chart`) visualizing scores from the user's last 5 tests.
    * A complete table of the user's test history fetched from the database.
* **Study Hub:**
    * Downloadable PDF cheatsheets for specific topics.
    * **Video Recommendations:** Automatically fetches and displays relevant YouTube video thumbnails and links for the selected topic using the YouTube Data API v3.
* **AI Doubt Solver:** An integrated chatbot (powered by the Google Gemini API) to answer any aptitude-related questions 24/7.
* **Dynamic UI:** A clean, multi-page interface with custom-styled buttons and containers.

---

## 🚀 Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Backend:** [Python 3](https://www.python.org/)
* **Database:** [MySQL](https://www.mysql.com/)
* **Core Libraries:**
    * `pandas`
    * `google-generativeai` (Gemini API)
    * `google-api-python-client` (YouTube Data API)
    * `streamlit-local-storage` (Login Persistence)
    * `streamlit-autorefresh` (Quiz Timer)
    * `mysql-connector-python` (Database Connection)

---

## 💻 Getting Started

Follow these steps to set up and run the project locally.

### 1. Prerequisites

* Python 3.10+
* A MySQL server (e.g., [WAMP](https://www.wampserver.com/en/) or [XAMPP](https://www.apachefriends.org/index.html))
* A Google account to get API keys.

### 2. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME
3. Set Up the Environment
Bash

# Create a virtual environment
python -m venv venv

# Activate the environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
4. Set Up the Database
Start your MySQL server (e.g., WAMP).

Access your MySQL console or a tool like phpMyAdmin.

Create a new database named aptitude_db.

SQL

CREATE DATABASE aptitude_db;
USE aptitude_db;
Run the SQL commands in database_schema.sql (you'll need to create this file) to create the tables:

users

topics

questions

tests

test_results

(Optional) Insert sample data into your topics and questions tables.

5. Configure Secrets
In the root of your project, create a folder named .streamlit.

Inside .streamlit, create a file named secrets.toml.

Add your database credentials and API keys:

Ini, TOML

# .streamlit/secrets.toml

# MySQL Database Credentials
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "aptitude_db"

# API Keys
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY_HERE"
6. Run the App
Bash

streamlit run Home.py
Your app will open in your browser at http://localhost:8501.
