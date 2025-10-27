import streamlit as st
from db_connector import get_db_connection
import mysql.connector
import time
import pandas as pd
import random
from streamlit_autorefresh import st_autorefresh
# DO NOT import LocalStorage globally anymore
# time is already imported above

# --- Page configuration ---
st.set_page_config(page_title="Take a Test", layout="wide")

# --- Inject CSS for Question Panel Buttons ---
st.markdown("""
<style>
/* --- Styling for the new Question Panel --- */

/* Base style for ALL panel buttons */
/* This targets any button that is a sibling (+) immediately after our status divs */
div.status-red + div[data-testid="stButton"] button,
div.status-green + div[data-testid="stButton"] button,
div.status-purple + div[data-testid="stButton"] button,
div.status-current + div[data-testid="stButton"] button {
    width: 100% !important;
    height: 45px !important; /* Uniform height */
    font-size: 1.1em !important; /* Slightly larger font */
    font-weight: bold !important;
    border: 1px solid #555 !important;
    color: white !important;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7) !important;
    transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease !important;
}

/* --- Status-specific colors --- */

/* RED (Default/Unattempted) */
div.status-red + div[data-testid="stButton"] button {
    background-color: #FF4B4B !important; /* Red */
}
div.status-red + div[data-testid="stButton"] button:hover {
    background-color: #DC3545 !important; /* Darker red */
}

/* GREEN (Attempted) */
div.status-green + div[data-testid="stButton"] button {
    background-color: #28a745 !important; /* Green */
}
div.status-green + div[data-testid="stButton"] button:hover {
    background-color: #218838 !important;
}

/* PURPLE (Marked for Review) */
div.status-purple + div[data-testid="stButton"] button {
    background-color: #8A2BE2 !important; /* Purple */
}
div.status-purple + div[data-testid="stButton"] button:hover {
    background-color: #7019C8 !important;
}

/* BLUE (Current Question) */
div.status-current + div[data-testid="stButton"] button {
    background-color: #007BFF !important; /* Streamlit Blue */
    border: 3px solid #FFD700 !important; /* Gold border */
    box-shadow: 0 0 12px rgba(0,123,255,0.9) !important;
}
div.status-current + div[data-testid="stButton"] button:hover {
    background-color: #0069D9 !important;
    border-color: #FFF !important;
}

/* This hides the empty div we use as a marker */
.status-red, .status-green, .status-purple, .status-current {
    display: none;
}

</style>
""", unsafe_allow_html=True)
# --- End CSS ---


# --- (NEW) Startup Check Function ---
def run_startup_check():
    # Run only once per session
    if 'startup_check_done' not in st.session_state:
        from streamlit_local_storage import LocalStorage # Import INSIDE function
        localS_check = LocalStorage() # Initialize INSIDE function

        stored_login_data = localS_check.getItem('logged_in')
        stored_user_id_data = localS_check.getItem('user_id')
        stored_username_data = localS_check.getItem('username')
        logged_in = False
        user_id = None
        username = None

        # --- Stricter Check ---
        if isinstance(stored_login_data, dict) and stored_login_data.get('value') is True:
            if stored_user_id_data and stored_user_id_data.get('value') is not None: user_id = stored_user_id_data['value']
            if stored_username_data and stored_username_data.get('value') is not None: username = stored_username_data['value']
            if user_id is not None and username is not None: logged_in = True
            else: # Inconsistent state
                logged_in = False
                localS_check.setItem('logged_in', False, key="clear_login_inconsistent_test")
                localS_check.setItem('user_id', None, key="clear_userid_inconsistent_test")
                localS_check.setItem('username', None, key="clear_username_inconsistent_test")
        elif isinstance(stored_login_data, bool): # Handle old boolean format
             if stored_login_data is True:
                 logged_in = True
                 old_user_id = localS_check.getItem('user_id'); old_username = localS_check.getItem('username')
                 if isinstance(old_user_id, dict) and 'value' in old_user_id: user_id = old_user_id['value']
                 elif isinstance(old_user_id, (int, str)): user_id = old_user_id
                 if isinstance(old_username, dict) and 'value' in old_username: username = old_username['value']
                 elif isinstance(old_username, str): username = old_username
                 if user_id is not None and username is not None:
                     localS_check.setItem('logged_in', True, key="fix_login_test_func")
                     localS_check.setItem('user_id', user_id, key="fix_userid_test_func")
                     localS_check.setItem('username', username, key="fix_username_test_func")
                 else: # Invalid details from old format
                      logged_in = False
                      localS_check.setItem('logged_in', False, key="clear_login_old_invalid_test")
                      localS_check.setItem('user_id', None, key="clear_userid_old_invalid_test")
                      localS_check.setItem('username', None, key="clear_username_old_invalid_test")
             else: # Old format was False
                  logged_in = False
                  localS_check.setItem('logged_in', False, key="clear_login_old_false_test")
                  localS_check.setItem('user_id', None, key="clear_userid_old_false_test")
                  localS_check.setItem('username', None, key="clear_username_old_false_test")
        # --- End Stricter Check ---
        if logged_in and user_id is not None and username is not None:
            st.session_state.logged_in = True; st.session_state.user_id = user_id; st.session_state.username = username
        else:
            if 'logged_in' in st.session_state: del st.session_state.logged_in
            if 'user_id' in st.session_state: del st.session_state.user_id
            if 'username' in st.session_state: del st.session_state.username
        st.session_state.startup_check_done = True
# --- (END) Startup Check Function ---

# --- Call Startup Check BEFORE Sidebar ---
run_startup_check()

# --- Sidebar Login Status (Corrected Logout v2) ---
if 'logged_in' in st.session_state and st.session_state.logged_in:
    username_display = st.session_state.get('username', 'User')
    st.sidebar.success(f"Logged in as {username_display}")
    if st.sidebar.button("Logout", key="logout_test_sidebar"):
        from streamlit_local_storage import LocalStorage # Import locally
        localS_logout = LocalStorage() # Initialize locally
        localS_logout.setItem('logged_in', False, key="logout_set_login_status_test")
        localS_logout.setItem('user_id', None, key="logout_set_userid_none_test")
        localS_logout.setItem('username', None, key="logout_set_username_none_test")
        keys_to_clear = list(st.session_state.keys())
        for key_to_del in keys_to_clear:
            if key_to_del != 'startup_check_done':
                 try: del st.session_state[key_to_del]
                 except KeyError: pass
        time.sleep(0.2); st.rerun()
else:
    st.sidebar.info("You are not logged in.")
# --- End of sidebar code ---

# --- SECURITY CHECK ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view this page.")
    st.page_link("pages/2_Login.py", label="Go to Login Page 🔐")
    st.stop()
# --- END OF SECURITY CHECK ---

# --- Helper Functions ---
def get_topics_by_category(category):
    conn = None; cursor = None
    try:
        conn = get_db_connection()
        if not conn: raise mysql.connector.Error("DB connection failed")
        cursor = conn.cursor(dictionary=True)
        query = "SELECT topic_id, topic_name FROM topics WHERE category = %s"
        cursor.execute(query, (category,))
        topics = cursor.fetchall()
        return {topic['topic_name']: topic['topic_id'] for topic in topics}
    except mysql.connector.Error as e:
        st.error(f"DB Error fetching topics: {e}")
        return {}
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

def fetch_questions(topic_ids, difficulty, num_questions):
    conn = None; cursor = None
    if not topic_ids: return []
    try:
        conn = get_db_connection()
        if not conn: raise mysql.connector.Error("DB connection failed")
        cursor = conn.cursor(dictionary=True)
        safe_topic_ids = [int(tid) for tid in topic_ids]; placeholders = ','.join(['%s'] * len(safe_topic_ids))
        query_parts = [f"SELECT * FROM questions WHERE topic_id IN ({placeholders})"]; params = safe_topic_ids
        if difficulty != 'all': query_parts.append("AND difficulty = %s"); params.append(difficulty)
        safe_num_questions = max(1, int(num_questions)); query_parts.append("ORDER BY RAND() LIMIT %s"); params.append(safe_num_questions)
        query = " ".join(query_parts); cursor.execute(query, tuple(params)); questions = cursor.fetchall(); random.shuffle(questions); return questions
    except (mysql.connector.Error, ValueError) as e:
        st.error(f"Error fetching questions: {e}"); return []
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

def calculate_and_save_results():
    conn = None; cursor = None
    try:
        if 'user_answers' not in st.session_state or 'questions' not in st.session_state or 'user_id' not in st.session_state: st.error("Session state incomplete."); return
        user_answers = st.session_state.user_answers; questions = st.session_state.questions; user_id = st.session_state.user_id
        if not questions: st.warning("No questions found."); st.session_state.final_results = {"score": 0, "correct": 0, "wrong": 0, "unattempted": 0, "total": 0, "accuracy": 0, "results_df": pd.DataFrame()}; return
        correct_count = wrong_count = unattempted_count = 0; results_data = []; db_results = []
        for i, q in enumerate(questions):
            user_ans = user_answers.get(i); result_text = ""; is_correct_db = False; your_answer_text = ""; correct_option_key = f'option_{q.get("correct_option", "")}'; user_answer_key = f'option_{user_ans}' if user_ans else ""
            if user_ans == q.get("correct_option"): correct_count += 1; result_text = "✅ Correct"; is_correct_db = True; your_answer_text = f"{user_ans} ({q.get(user_answer_key, 'N/A')})"
            elif user_ans is None: unattempted_count += 1; result_text = "⚪ Unattempted"; is_correct_db = False; your_answer_text = "No Answer"
            else: wrong_count += 1; result_text = "❌ Incorrect"; is_correct_db = False; your_answer_text = f"{user_ans} ({q.get(user_answer_key, 'N/A')})"
            results_data.append({"Question": q.get('question_text', 'Missing Text'), "Your Answer": your_answer_text, "Correct Answer": f"{q.get('correct_option','?')} ({q.get(correct_option_key, 'N/A')})", "Result": result_text})
            q_id = q.get('question_id');
            if q_id is not None: db_results.append((q_id, user_ans, is_correct_db))
            else: st.warning(f"Question missing ID at index {i}.")
        total_q = len(questions); score = (correct_count / total_q) * 100 if total_q > 0 else 0; attempted_q = correct_count + wrong_count; accuracy = (correct_count / attempted_q) * 100 if attempted_q > 0 else 0
        st.session_state.final_results = {"score": score, "correct": correct_count, "wrong": wrong_count, "unattempted": unattempted_count, "total": total_q, "accuracy": accuracy, "results_df": pd.DataFrame(results_data)}
        conn = get_db_connection();
        if not conn: raise mysql.connector.Error("DB connection failed for saving results.")
        cursor = conn.cursor(); test_query = "INSERT INTO tests (user_id, score, total_questions) VALUES (%s, %s, %s)"; cursor.execute(test_query, (user_id, int(score), total_q)); test_id = cursor.lastrowid
        if db_results: results_query = "INSERT INTO test_results (test_id, question_id, user_answer, is_correct) VALUES (%s, %s, %s, %s)"; db_results_with_test_id = [(test_id,) + res for res in db_results]; cursor.executemany(results_query, db_results_with_test_id)
        conn.commit()
    except mysql.connector.Error as e: st.error(f"Error saving results: {e}")
    except Exception as e: st.error(f"Unexpected error in calculate_and_save_results: {e}")
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

# --- **** CORRECTED HELPER FUNCTIONS **** ---
def update_current_question_status(action="move"):
    """Updates the status of the current question based on answer. 'action' can be 'move' or 'mark'."""
    q_index = st.session_state.current_question_index
    
    if 'question_statuses' not in st.session_state or q_index >= len(st.session_state.question_statuses):
        return 

    # If user marked for review, status is purple regardless of answer
    if action == "mark":
        st.session_state.question_statuses[q_index] = 'purple'
    
    # Don't override purple unless saving
    elif st.session_state.question_statuses[q_index] != 'purple' or action == "save_and_next":
        
        # --- THIS IS THE KEY FIX ---
        # Check the 'user_answers' dictionary for a saved answer
        answer = st.session_state.user_answers.get(q_index)
        # --- END FIX ---

        if answer is not None: # Check if an answer exists in our dictionary
            st.session_state.question_statuses[q_index] = 'green'
        else:
            # If no answer in our dictionary, it's red
            st.session_state.question_statuses[q_index] = 'red'

def on_panel_click(jump_index):
    # First, update the status of the question we are LEAVING
    update_current_question_status(action="move")
    # NOW, set the new index
    st.session_state.current_question_index = jump_index
    # A rerun will be triggered by the button click
# --- **** END CORRECTED HELPER FUNCTIONS **** ---


# --- (3) Page Logic and State Management Functions ---
def show_setup_form():
    st.title("Create Your Custom Test 📝")
    run_startup_check() # Run startup check

    quant_topics = get_topics_by_category('Quantitative')
    logical_topics = get_topics_by_category('Logical')
    verbal_topics = get_topics_by_category('Verbal')
    with st.form("test_setup_form"):
        st.subheader("1. Select Topics"); tab_q, tab_l, tab_v = st.tabs(["Quantitative", "Logical Reasoning", "Verbal Ability"])
        with tab_q: selected_quant = st.multiselect("Quantitative Topics", options=list(quant_topics.keys()))
        with tab_l: selected_logical = st.multiselect("Logical Reasoning Topics", options=list(logical_topics.keys()))
        with tab_v: selected_verbal = st.multiselect("Verbal Ability Topics", options=list(verbal_topics.keys()))
        st.subheader("2. Customize Your Test"); col1, col2, col3 = st.columns(3)
        with col1: num_questions = st.number_input("Number of Questions", min_value=1, max_value=50, value=10, step=1)
        with col2: difficulty = st.selectbox("Difficulty", options=['all', 'easy', 'medium', 'hard'], index=0)
        with col3: time_limit = st.number_input("Time Limit (minutes)", min_value=1, max_value=120, value=15, step=1)
        start_button = st.form_submit_button("Start Test", use_container_width=True, type="primary")

    if start_button:
        selected_topic_names = selected_quant + selected_logical + selected_verbal
        if not selected_topic_names: st.error("Select at least one topic."); st.stop()
        all_topics_map = {**quant_topics, **logical_topics, **verbal_topics}; selected_topic_ids = [all_topics_map[name] for name in selected_topic_names if name in all_topics_map]
        if not selected_topic_ids: st.error("Could not find IDs for selected topics."); st.stop()
        questions = fetch_questions(selected_topic_ids, difficulty, num_questions)
        if not questions: st.error("No questions found for your selection."); st.stop()
        
        st.session_state.question_statuses = ['red'] * len(questions)
        
        st.session_state.test_in_progress = True; st.session_state.questions = questions; st.session_state.current_question_index = 0
        st.session_state.user_answers = {}; st.session_state.start_time = time.time()
        st.session_state.end_time = st.session_state.start_time + (time_limit * 60)
        if 'show_results' in st.session_state: del st.session_state.show_results
        st.rerun()

def show_quiz_interface():
    st.title("Aptiking Test in Progress... ⏳")
    run_startup_check() # Run startup check
    
    if 'end_time' not in st.session_state or 'start_time' not in st.session_state or 'questions' not in st.session_state: st.error("Test session error."); st.stop()
    
    if st.session_state.get('test_in_progress', False):
        st_autorefresh(interval=1000, key="quiz_timer")
    
    time_left = st.session_state.end_time - time.time()

    q_index = st.session_state.current_question_index
    questions = st.session_state.questions
    total_q = len(questions)

    # --- Time Up Logic ---
    if time_left <= 0:
        if st.session_state.get('test_in_progress', False):
            st.warning("Time's up! Submitting...")
            answer = st.session_state.get(f"q_{q_index}")
            if answer: st.session_state.user_answers[q_index] = answer
            update_current_question_status(action="move")
            calculate_and_save_results()
            st.session_state.show_results = True
            st.session_state.test_in_progress = False 
            for key in ['questions', 'current_question_index', 'user_answers', 'start_time', 'end_time', 'question_statuses']:
                if key in st.session_state: del st.session_state[key]
            st.rerun()
        return
    # --- End Time Up Logic ---

    # --- Main Layout: Question Column and Panel Column ---
    q_col, panel_col = st.columns([2, 1]) # 66% for question, 33% for panel (WIDER PANEL)

    with q_col:
        # --- Timer and Submit Button ---
        mins, secs = divmod(int(max(0, time_left)), 60); timer_display = f"{mins:02d}:{secs:02d}"
        t_col1, t_col2 = st.columns([3, 1])
        with t_col1: st.subheader(f"Time Remaining: {timer_display}")
        with t_col2:
            if st.button("Submit Test Now", use_container_width=True, type="primary"):
                if st.session_state.get('test_in_progress', False):
                    update_current_question_status(action="move")
                    calculate_and_save_results()
                    st.session_state.show_results = True
                    st.session_state.test_in_progress = False
                    for key in ['questions', 'current_question_index', 'user_answers', 'start_time', 'end_time', 'question_statuses']:
                        if key in st.session_state: del st.session_state[key]
                    st.rerun()
        total_duration = st.session_state.end_time - st.session_state.start_time; progress_value = max(0.0, time_left / max(1, total_duration))
        st.progress(progress_value); st.divider()
        # --- End Timer/Submit ---
        
        # --- Question Display ---
        if not questions or q_index >= len(questions): st.error("Error: Questions missing."); st.stop()
        q = questions[q_index]
        st.subheader(f"Question {q_index + 1} of {total_q}"); st.markdown(f"**{q.get('question_text', 'Missing question text')}**")
        options = {'a': q.get('option_a',''), 'b': q.get('option_b',''), 'c': q.get('option_c',''), 'd': q.get('option_d','')}
        option_keys = list(options.keys()); 
        
        if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
        saved_answer = st.session_state.user_answers.get(q_index, None) 
        current_index = None
        if saved_answer in option_keys:
            try: current_index = option_keys.index(saved_answer)
            except ValueError: pass
        
        with st.container():
            user_choice = st.radio(
                "Choose:", option_keys, 
                format_func=lambda k: f"{k}) {options.get(k,'Invalid Option')}", 
                index=current_index, 
                key=f"q_{q_index}"
            )
        
        if user_choice is not None:
             st.session_state.user_answers[q_index] = user_choice
        # --- End Radio Button Logic ---

        st.divider()
        # --- End Question Display ---

        # --- NEW Navigation Buttons ---
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            if st.button("⬅️ Previous", key=f"prev_{q_index}", disabled=(q_index <= 0), use_container_width=True, type="primary"):
                update_current_question_status(action="move")
                if q_index > 0: 
                    st.session_state.current_question_index -= 1
                    st.rerun()
        with nav_col2:
            if st.button("Marked For Review", key=f"mark_{q_index}", use_container_width=True):
                st.session_state.question_statuses[q_index] = 'purple'
                answer = st.session_state.get(f"q_{q_index}") # Get current radio choice
                if answer: st.session_state.user_answers[q_index] = answer # Save it
                if q_index < total_q - 1: 
                    st.session_state.current_question_index += 1
                st.rerun()
        with nav_col3:
            # --- UPDATED Save and Next ---
            if st.button("Save and Next ➡️", key=f"next_{q_index}", disabled=(q_index >= total_q - 1), use_container_width=True, type="primary"):
                update_current_question_status(action="save_and_next") # Use new action
                if q_index < total_q - 1: 
                    st.session_state.current_question_index += 1
                    st.rerun()
            # --- END UPDATED ---
        # --- End NEW Navigation ---

    # --- NEW Question Panel ---
    with panel_col:
        st.subheader("Question Panel")
        
        # Legend
        st.markdown(
            "<span style='color: #28a745; font-weight: bold;'>● Green:</span> Attempted<br>"
            "<span style='color: #FF4B4B; font-weight: bold;'>● Red:</span> Unattempted<br>"
            "<span style='color: #8A2BE2; font-weight: bold;'>● Purple:</span> Marked for Review<br>"
            "<span style='color: #007BFF; font-weight: bold;'>● Blue:</span> Current Question",
            unsafe_allow_html=True
        )
        st.divider()

        # Check if question_statuses is initialized
        if 'question_statuses' not in st.session_state:
            st.session_state.question_statuses = ['red'] * total_q

        # --- NEW GRID LOGIC ---
        num_questions = len(st.session_state.question_statuses)
        cols_per_row = 4 # 4 columns for a wider panel
        
        for i in range(num_questions):
            # Create a new row of columns for the first button of each row
            if i % cols_per_row == 0:
                # This creates a new set of 4 columns for every 4th button
                cols = st.columns(cols_per_row)
            
            # Determine the style class for this button
            status = st.session_state.question_statuses[i]
            if i == q_index:
                style_class = "status-current" # Current question
            else:
                style_class = f"status-{status}" # green, red, or purple
            
            # Place the button inside its designated column
            with cols[i % cols_per_row]:
                # --- THIS IS THE FIX ---
                # We place an empty, styled div *immediately before* the button.
                # The CSS selector `div.status-green + div[data-testid="stButton"] button`
                # will find the div, then style the button next to it.
                st.markdown(f'<div class="{style_class}"></div>', unsafe_allow_html=True)
                if st.button(
                    f"{i + 1}",
                    key=f"panel_{i}",
                    on_click=on_panel_click,
                    args=(i,)
                ):
                    # on_click handles the logic
                    pass 
                # We NO LONGER need the closing markdown div
                # --- END FIX ---
        # --- END NEW GRID LOGIC ---
    # --- END NEW Question Panel ---


def show_results_page():
    st.title("Test Results 📊")
    run_startup_check() # Run startup check

    if 'final_results' not in st.session_state: st.error("Results not found."); st.stop()
    results = st.session_state.final_results; st.success(f"Score: **{results.get('score', 0):.2f}%**")
    col1, col2, col3, col4, col5 = st.columns(5); col1.metric("Total Qs", results.get('total', 0)); col2.metric("✅ Correct", results.get('correct', 0)); col3.metric("❌ Wrong", results.get('wrong', 0)); col4.metric("⚪ Unattempted", results.get('unattempted', 0)); col5.metric("Accuracy", f"{results.get('accuracy', 0):.2f}%")
    st.divider(); st.subheader("Detailed Breakdown")
    if 'results_df' in results and isinstance(results['results_df'], pd.DataFrame): st.dataframe(results['results_df'], use_container_width=True, hide_index=True)
    else: st.warning("Detailed results data missing.")
    st.divider()
    if st.button("Take Another Test ↩️", use_container_width=True, type="primary"):
        keys_to_keep = ['logged_in', 'username', 'user_id', 'startup_check_done']
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep: del st.session_state[key]
        st.rerun()

# --- (4) Main App Logic (Router) ---
# Check flags in a specific order
if 'show_results' in st.session_state and st.session_state.show_results:
    show_results_page()
elif 'test_in_progress' in st.session_state and st.session_state.test_in_progress:
    show_quiz_interface()
else:
    # Default to setup form if no other state is active
    show_setup_form()