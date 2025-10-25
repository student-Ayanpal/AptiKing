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
git clone 
