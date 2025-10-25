import streamlit as st
from db_connector import get_db_connection
import mysql.connector
import time
import pandas as pd
import random
from streamlit_autorefresh import st_autorefresh
# DO NOT import LocalStorage globally anymore
# from streamlit_local_storage import LocalStorage

# --- Page configuration ---
st.set_page_config(page_title="Take a Test", layout="wide")

# --- Inject CSS (Optional - if styling buttons with CSS) ---
# st.markdown("""<style>...</style>""", unsafe_allow_html=True)

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

        # Update session state based ONLY on the final 'logged_in' status
        if logged_in and user_id is not None and username is not None:
            st.session_state.logged_in = True
            st.session_state.user_id = user_id
            st.session_state.username = username
        else: # Clear session state if not confirmed logged in
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
        # --- Explicitly set logged_in to False, others to None ---
        localS_logout.setItem('logged_in', False, key="logout_set_login_status_test") # Unique key
        localS_logout.setItem('user_id', None, key="logout_set_userid_none_test")       # Unique key, use None
        localS_logout.setItem('username', None, key="logout_set_username_none_test")   # Unique key, use None
        # --- End new clearing logic ---

        # Clear session state thoroughly FIRST
        keys_to_clear = list(st.session_state.keys())
        for key_to_del in keys_to_clear:
            if key_to_del != 'startup_check_done':
                 try: del st.session_state[key_to_del]
                 except KeyError: pass
        # Short delay might help ensure storage write completes before rerun
        time.sleep(0.2)
        st.rerun()
else:
    st.sidebar.info("You are not logged in.")
# --- End of sidebar code ---

# --- SECURITY CHECK ---
# Session state should be correctly set by the startup check before this runs
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view this page.")
    st.page_link("pages/2_Login.py", label="Go to Login Page 🔐")
    st.stop()
# --- END OF SECURITY CHECK ---

# --- Helper Functions ---
# (Placed before use, outside page logic functions)
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
        # Check essential keys first
        if 'user_answers' not in st.session_state or 'questions' not in st.session_state or 'user_id' not in st.session_state:
            st.error("Session state incomplete. Cannot calculate results.")
            # Attempt to clear potentially bad state and go back to setup
            keys_to_keep = ['logged_in', 'username', 'user_id', 'startup_check_done']
            for key in list(st.session_state.keys()):
                if key not in keys_to_keep: del st.session_state[key]
            # No rerun here, let it proceed to show error and maybe a back button later
            return # Exit function

        user_answers = st.session_state.user_answers
        questions = st.session_state.questions
        user_id = st.session_state.user_id

        if not questions:
            st.warning("No questions found in this test session.")
            st.session_state.final_results = {"score": 0, "correct": 0, "wrong": 0, "unattempted": 0, "total": 0, "accuracy": 0, "results_df": pd.DataFrame()}
            return

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

# --- Page Logic and State Management Functions ---
def show_setup_form():
    st.title("Create Your Custom Test 📝") # <-- TITLE HERE
    # --- Startup Check logic needs to be run if this view loads first ---
    run_startup_check() # Call the check function defined globally

    quant_topics = get_topics_by_category('Quantitative')
    logical_topics = get_topics_by_category('Logical')
    verbal_topics = get_topics_by_category('Verbal')
    with st.form("test_setup_form"):
        st.subheader("1. Select Topics")
        tab_q, tab_l, tab_v = st.tabs(["Quantitative", "Logical Reasoning", "Verbal Ability"])
        with tab_q: selected_quant = st.multiselect("Quantitative Topics", options=list(quant_topics.keys()))
        with tab_l: selected_logical = st.multiselect("Logical Reasoning Topics", options=list(logical_topics.keys()))
        with tab_v: selected_verbal = st.multiselect("Verbal Ability Topics", options=list(verbal_topics.keys()))
        st.subheader("2. Customize Your Test")
        col1, col2, col3 = st.columns(3)
        with col1: num_questions = st.number_input("Number of Questions", min_value=1, max_value=50, value=10, step=1)
        with col2: difficulty = st.selectbox("Difficulty", options=['all', 'easy', 'medium', 'hard'], index=0)
        with col3: time_limit = st.number_input("Time Limit (minutes)", min_value=1, max_value=120, value=15, step=1)
        start_button = st.form_submit_button("Start Test", use_container_width=True, type="primary") # Use primary here

    if start_button:
        selected_topic_names = selected_quant + selected_logical + selected_verbal
        if not selected_topic_names: st.error("Select at least one topic."); st.stop()
        all_topics_map = {**quant_topics, **logical_topics, **verbal_topics}; selected_topic_ids = [all_topics_map[name] for name in selected_topic_names if name in all_topics_map]
        if not selected_topic_ids: st.error("Could not find IDs for selected topics."); st.stop()
        questions = fetch_questions(selected_topic_ids, difficulty, num_questions)
        if not questions: st.error("No questions found for your selection."); st.stop()
        st.session_state.test_in_progress = True; st.session_state.questions = questions; st.session_state.current_question_index = 0
        st.session_state.user_answers = {}; st.session_state.start_time = time.time()
        st.session_state.end_time = st.session_state.start_time + (time_limit * 60)
        if 'show_results' in st.session_state: del st.session_state.show_results
        st.rerun()

def show_quiz_interface():
    st.title("Aptiking Test in Progress... ⏳") # <-- TITLE HERE
    # --- Startup Check logic needs to be run if this view loads first ---
    run_startup_check() # Call the check function defined globally

    if 'end_time' not in st.session_state or 'start_time' not in st.session_state or 'questions' not in st.session_state: st.error("Test session error."); st.stop()
    st_autorefresh(interval=1000, key="quiz_timer"); time_left = st.session_state.end_time - time.time()

    # --- CORRECTED INDENTATION FOR TIME UP LOGIC ---
    if time_left <= 0:
        if st.session_state.get('test_in_progress', False):
            st.warning("Time's up! Submitting...")
            calculate_and_save_results()
            st.session_state.show_results = True
            if 'test_in_progress' in st.session_state:
                del st.session_state.test_in_progress
            # time.sleep(1) # Delay might cause issues, removed for now
            st.rerun()
        return # Important to stop further execution if time is up
    # --- END CORRECTION ---

    mins, secs = divmod(int(max(0, time_left)), 60); timer_display = f"{mins:02d}:{secs:02d}"
    col1, col2 = st.columns([3, 1])
    with col1: st.subheader(f"Time Remaining: {timer_display}")
    with col2:
        if st.button("Submit Test Now", use_container_width=True, type="primary"): # Use primary here
            if st.session_state.get('test_in_progress', False):
                calculate_and_save_results()
                st.session_state.show_results = True
                if 'test_in_progress' in st.session_state:
                    del st.session_state.test_in_progress
                st.rerun()
    total_duration = st.session_state.end_time - st.session_state.start_time; progress_value = max(0.0, time_left / max(1, total_duration))
    st.progress(progress_value); st.divider()
    q_index = st.session_state.current_question_index; questions = st.session_state.questions
    if not questions or q_index >= len(questions): st.error("Error: Questions missing or index out of range."); st.stop()
    q = questions[q_index]; total_q = len(questions)
    st.subheader(f"Question {q_index + 1} of {total_q}"); st.markdown(f"**{q.get('question_text', 'Missing question text')}**")
    options = {'a': q.get('option_a',''), 'b': q.get('option_b',''), 'c': q.get('option_c',''), 'd': q.get('option_d','')}
    option_keys = list(options.keys()); saved_answer = st.session_state.user_answers.get(q_index); current_index = None
    if saved_answer in option_keys:
        try: current_index = option_keys.index(saved_answer)
        except ValueError: current_index = None
    with st.container():
        user_choice = st.radio("Choose:", option_keys, format_func=lambda k: f"{k}) {options.get(k,'Invalid Option')}", index=current_index, key=f"q_{q_index}")
    if user_choice is not None: st.session_state.user_answers[q_index] = user_choice
    st.divider(); nav_col1, _, nav_col3 = st.columns([1, 1, 1])
    with nav_col1:
        # Use type="primary" for Nav Buttons
        if st.button("⬅️ Previous", key=f"prev_{q_index}", disabled=(q_index <= 0), type="primary"): # Use primary
             if q_index > 0: st.session_state.current_question_index -= 1; st.rerun()
    with nav_col3:
        if st.button("Next ➡️", key=f"next_{q_index}", disabled=(q_index >= total_q - 1), type="primary"): # Use primary
             if q_index < total_q - 1: st.session_state.current_question_index += 1; st.rerun()

def show_results_page():
    st.title("Test Results 📊") # <-- TITLE HERE
    # --- Startup Check logic needs to be run if this view loads first ---
    run_startup_check() # Call the check function defined globally

    if 'final_results' not in st.session_state: st.error("Results not found."); st.stop()
    results = st.session_state.final_results; st.success(f"Score: **{results.get('score', 0):.2f}%**")
    col1, col2, col3, col4, col5 = st.columns(5); col1.metric("Total Qs", results.get('total', 0)); col2.metric("✅ Correct", results.get('correct', 0)); col3.metric("❌ Wrong", results.get('wrong', 0)); col4.metric("⚪ Unattempted", results.get('unattempted', 0)); col5.metric("Accuracy", f"{results.get('accuracy', 0):.2f}%")
    st.divider(); st.subheader("Detailed Breakdown")
    if 'results_df' in results and isinstance(results['results_df'], pd.DataFrame): st.dataframe(results['results_df'], use_container_width=True, hide_index=True)
    else: st.warning("Detailed results data missing.")
    st.divider()
    # Use type="primary" for Take Another Test Button
    if st.button("Take Another Test ↩️", use_container_width=True, type="primary"): # Use primary
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