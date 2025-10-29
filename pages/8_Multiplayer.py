import streamlit as st
from db_connector import get_db_connection
import mysql.connector
import time
import pandas as pd
import random
from streamlit_autorefresh import st_autorefresh
# DO NOT import LocalStorage globally anymore
import json # For saving/loading JSON data
import string # For generating lobby codes
from datetime import datetime # For shared timer
import matplotlib.pyplot as plt # --- NEW IMPORT ---

# --- Page configuration ---
st.set_page_config(page_title="Multiplayer", layout="wide")

# --- Inject CSS for Question Panel Buttons ---
st.markdown("""
<style>
/* ... (Your existing CSS for the panel buttons) ... */
.status-red .stButton button {
    width: 100% !important; height: 45px !important; font-size: 1.1em !important;
    font-weight: bold !important; border: 1px solid #555 !important; color: white !important;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7) !important;
    transition: all 0.2s ease !important;
    background-color: #FF4B4B !important; /* Red */
}
.status-red .stButton button:hover { background-color: #DC3545 !important; }
.status-green .stButton button {
    width: 100% !important; height: 45px !important; font-size: 1.1em !important;
    font-weight: bold !important; border: 1px solid #555 !important; color: white !important;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7) !important;
    transition: all 0.2s ease !important;
    background-color: #28a745 !important; /* Green */
}
.status-green .stButton button:hover { background-color: #218838 !important; }
.status-purple .stButton button {
    width: 100% !important; height: 45px !important; font-size: 1.1em !important;
    font-weight: bold !important; border: 1px solid #555 !important; color: white !important;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7) !important;
    transition: all 0.2s ease !important;
    background-color: #8A2BE2 !important; /* Purple */
}
.status-purple .stButton button:hover { background-color: #7019C8 !important; }
.status-current .stButton button {
    width: 100% !important; height: 45px !important; font-size: 1.1em !important;
    font-weight: bold !important; color: white !important;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7) !important;
    transition: all 0.2s ease !important;
    background-color: #007BFF !important; /* Streamlit Blue */
    border: 3px solid #FFD700 !important; /* Gold border */
    box-shadow: 0 0 12px rgba(0,123,255,0.9) !important;
}
.status-current .stButton button:hover { background-color: #0069D9 !important; border-color: #FFF !important; }
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
        logged_in = False; user_id = None; username = None
        if isinstance(stored_login_data, dict) and stored_login_data.get('value') is True:
            if stored_user_id_data and stored_user_id_data.get('value') is not None: user_id = stored_user_id_data['value']
            if stored_username_data and stored_username_data.get('value') is not None: username = stored_username_data['value']
            if user_id is not None and username is not None: logged_in = True
            else: logged_in = False; localS_check.setItem('logged_in', False, key="clear_login_inconsistent_multi"); localS_check.setItem('user_id', None, key="clear_userid_inconsistent_multi"); localS_check.setItem('username', None, key="clear_username_inconsistent_multi")
        elif isinstance(stored_login_data, bool): # Handle old boolean format
             if stored_login_data is True:
                 logged_in = True; old_user_id = localS_check.getItem('user_id'); old_username = localS_check.getItem('username')
                 if isinstance(old_user_id, dict) and 'value' in old_user_id: user_id = old_user_id['value']
                 elif isinstance(old_user_id, (int, str)): user_id = old_user_id
                 if isinstance(old_username, dict) and 'value' in old_username: username = old_username['value']
                 elif isinstance(old_username, str): username = old_username
                 if user_id is not None and username is not None:
                     localS_check.setItem('logged_in', True, key="fix_login_multi_func")
                     localS_check.setItem('user_id', user_id, key="fix_userid_multi_func")
                     localS_check.setItem('username', username, key="fix_username_multi_func")
                 else: logged_in = False; localS_check.setItem('logged_in', False, key="clear_login_old_invalid_multi"); localS_check.setItem('user_id', None, key="clear_userid_old_invalid_multi"); localS_check.setItem('username', None, key="clear_username_old_invalid_multi")
             else: logged_in = False; localS_check.setItem('logged_in', False, key="clear_login_old_false_multi"); localS_check.setItem('user_id', None, key="clear_userid_old_false_multi"); localS_check.setItem('username', None, key="clear_username_old_false_multi")
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
    if st.sidebar.button("Logout", key="logout_multi_sidebar"):
        from streamlit_local_storage import LocalStorage # Import locally
        localS_logout = LocalStorage() # Initialize locally
        localS_logout.setItem('logged_in', False, key="logout_set_login_status_multi")
        localS_logout.setItem('user_id', None, key="logout_set_userid_none_multi")
        localS_logout.setItem('username', None, key="logout_set_username_none_multi")
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
    if 'just_joined_via_link' in st.session_state:
        st.info("You need to log in or register to join the lobby.")
    st.stop()
# --- END OF SECURITY CHECK ---

# --- HELPER FUNCTIONS (Copied from Take_Test) ---
def get_topics_by_category(category):
    conn = None; cursor = None
    try:
        conn = get_db_connection();
        if not conn: raise mysql.connector.Error("DB connection failed")
        cursor = conn.cursor(dictionary=True); query = "SELECT topic_id, topic_name FROM topics WHERE category = %s"; cursor.execute(query, (category,)); topics = cursor.fetchall(); return {topic['topic_name']: topic['topic_id'] for topic in topics}
    except mysql.connector.Error as e: st.error(f"DB Error: {e}"); return {}
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@st.cache_data(ttl=60) # Cache questions briefly
def fetch_questions(topic_ids, difficulty, num_questions):
    conn = None; cursor = None
    if not topic_ids: return []
    try:
        conn = get_db_connection();
        if not conn: raise mysql.connector.Error("DB connection failed")
        cursor = conn.cursor(dictionary=True); safe_topic_ids = [int(tid) for tid in topic_ids]; placeholders = ','.join(['%s'] * len(safe_topic_ids));
        query_parts = [f"SELECT * FROM questions WHERE topic_id IN ({placeholders})"]; params = safe_topic_ids
        if difficulty != 'all': query_parts.append("AND difficulty = %s"); params.append(difficulty)
        
        # --- FIX for num_questions ---
        try:
            limit = int(num_questions)
        except ValueError:
            limit = 10 # Default to 10
        query_parts.append(f"ORDER BY RAND() LIMIT {limit}")
        # --- END FIX ---

        query = " ".join(query_parts)
        cursor.execute(query, tuple(params)); # Pass params without limit
        questions = cursor.fetchall(); random.shuffle(questions); return questions
    except (mysql.connector.Error, ValueError) as e:
        st.error(f"Error fetching questions: {e}"); return []
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()
# --- END COPIED FUNCTIONS ---

# --- MULTIPLAYER HELPER FUNCTIONS ---

# --- NEW HELPER: Get questions by exact ID list ---
@st.cache_data(ttl=3600) # Cache these questions for an hour
def get_questions_by_ids(question_ids):
    conn = None; cursor = None
    if not question_ids: return []
    try:
        conn = get_db_connection();
        if not conn: raise mysql.connector.Error("DB connection failed")
        cursor = conn.cursor(dictionary=True)
        
        # Create placeholders
        placeholders = ','.join(['%s'] * len(question_ids))
        # Use FIELD to preserve the order from the list
        query = f"SELECT * FROM questions WHERE question_id IN ({placeholders}) ORDER BY FIELD(question_id, {placeholders})"
        
        # The parameters list must be repeated for FIELD()
        params = tuple(question_ids + question_ids)
        
        cursor.execute(query, params)
        questions = cursor.fetchall()
        return questions
    except (mysql.connector.Error, ValueError) as e:
        st.error(f"Error fetching specific questions: {e}"); return []
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()
# --- END NEW HELPER ---

def generate_lobby_code(length=6):
    conn = None; cursor = None
    try:
        conn = get_db_connection()
        if not conn: raise mysql.connector.Error("DB connection failed (lobby gen)")
        cursor = conn.cursor()
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            cursor.execute("SELECT lobby_id FROM lobbies WHERE lobby_id = %s", (code,))
            if not cursor.fetchone():
                return code # Code is unique
    except Exception as e:
        st.error(f"Error generating lobby code: {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@st.cache_data(ttl=5) # Cache lobby details for 5 seconds
def get_lobby_details(lobby_id):
    conn = None; cursor = None
    try:
        conn = get_db_connection();
        if not conn: return None
        cursor = conn.cursor(dictionary=True);
        cursor.execute("SELECT * FROM lobbies WHERE lobby_id = %s", (lobby_id,))
        return cursor.fetchone()
    except Exception as e: st.error(f"Error getting lobby details: {e}"); return None
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@st.cache_data(ttl=5) # Cache participant list for 5 seconds
def get_lobby_participants(lobby_id):
    conn = None; cursor = None
    try:
        conn = get_db_connection();
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT u.user_id, u.username, lp.status, lp.score, lp.time_taken 
            FROM lobby_participants lp 
            JOIN users u ON lp.user_id = u.user_id 
            WHERE lp.lobby_id = %s
            ORDER BY lp.score DESC, lp.time_taken ASC, lp.joined_at ASC
        """
        cursor.execute(query, (lobby_id,))
        return cursor.fetchall()
    except Exception as e: st.error(f"Error getting participants: {e}"); return []
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

def calculate_and_save_multiplayer_results():
    conn = None; cursor = None
    try:
        if 'user_answers' not in st.session_state or 'questions' not in st.session_state or 'user_id' not in st.session_state: st.error("Session state incomplete."); return
        user_answers = st.session_state.user_answers; questions = st.session_state.questions; user_id = st.session_state.user_id
        lobby_id = st.session_state.current_lobby_id; start_time = st.session_state.start_time
        if not questions: return
        correct_count = 0
        for i, q in enumerate(questions):
            if user_answers.get(i) == q.get("correct_option"): correct_count += 1
        total_q = len(questions); score = (correct_count / total_q) * 100 if total_q > 0 else 0
        time_taken = int(time.time() - start_time) # Total time since quiz start

        conn = get_db_connection()
        if not conn: raise mysql.connector.Error("DB connection failed (save results)")
        cursor = conn.cursor()
        query = "UPDATE lobby_participants SET score = %s, time_taken = %s, status = 'finished' WHERE lobby_id = %s AND user_id = %s"
        cursor.execute(query, (int(score), time_taken, lobby_id, user_id))
        conn.commit()
        st.session_state.individual_multiplayer_results = {"score": int(score), "correct": correct_count, "total": total_q}
    except Exception as e: st.error(f"Error saving multiplayer results: {e}")
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

def update_current_question_status(action="move"):
    q_index = st.session_state.current_question_index
    if 'question_statuses' not in st.session_state or q_index >= len(st.session_state.question_statuses): return
    answer = st.session_state.get(f"q_multi_{q_index}") # Use 'q_multi' key
    if answer: st.session_state.user_answers[q_index] = answer
    if action == "mark": st.session_state.question_statuses[q_index] = 'purple'
    elif st.session_state.question_statuses[q_index] != 'purple' or action == "save_and_next":
        saved_answer_for_status = st.session_state.user_answers.get(q_index)
        if saved_answer_for_status is not None: st.session_state.question_statuses[q_index] = 'green'
        else: st.session_state.question_statuses[q_index] = 'red'
def on_panel_click(jump_index):
    update_current_question_status(action="move")
    st.session_state.current_question_index = jump_index
# --- END HELPER FUNCTIONS ---


# --- PAGE LOGIC FUNCTIONS ---

# --- VIEW 1: HOST OR JOIN ---
def show_host_or_join_view():
    st.title("🎮 Multiplayer Quiz")
    run_startup_check() # Run check

    # Check if user just joined via link
    if 'join_lobby_id' in st.session_state and 'just_joined_via_link' in st.session_state:
        st.success(f"You've been invited to lobby {st.session_state.join_lobby_id}! Joining now...")
        conn = None; cursor = None
        try:
            lobby_id = st.session_state.join_lobby_id
            user_id = st.session_state.user_id
            conn = get_db_connection()
            if not conn: raise mysql.connector.Error("DB connection failed (auto-join)")
            cursor = conn.cursor(dictionary=True)
            query = "SELECT status FROM lobbies WHERE lobby_id = %s"
            cursor.execute(query, (lobby_id,))
            lobby = cursor.fetchone()
            if lobby and lobby['status'] == 'waiting':
                query_p = "INSERT IGNORE INTO lobby_participants (lobby_id, user_id) VALUES (%s, %s)"
                cursor.execute(query_p, (lobby_id, user_id))
                conn.commit()
                st.session_state.current_lobby_id = lobby_id
                del st.session_state.join_lobby_id
                del st.session_state.just_joined_via_link
                st.rerun()
            else:
                st.error("Sorry, this lobby is invalid or has already started.")
                del st.session_state.join_lobby_id
                del st.session_state.just_joined_via_link
        except Exception as e: st.error(f"Error auto-joining lobby: {e}")
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

    col1, col2 = st.columns(2)
    
    # --- HOST GAME ---
    with col1:
        st.subheader("Host a New Game")
        quant_topics = get_topics_by_category('Quantitative'); logical_topics = get_topics_by_category('Logical'); verbal_topics = get_topics_by_category('Verbal')
        with st.form("host_game_form"):
            st.write("Select quiz settings for your lobby:")
            tab_q, tab_l, tab_v = st.tabs(["Quantitative", "Logical", "Verbal"])
            with tab_q: selected_quant = st.multiselect("Quant Topics", list(quant_topics.keys()), key="mq")
            with tab_l: selected_logical = st.multiselect("Logical Topics", list(logical_topics.keys()), key="ml")
            with tab_v: selected_verbal = st.multiselect("Verbal Topics", list(verbal_topics.keys()), key="mv")
            scol1, scol2, scol3 = st.columns(3)
            with scol1: 
                # --- THIS IS THE FIX ---
                num_questions = st.number_input("Num Questions", min_value=1, max_value=50, value=10, step=1)
                # --- END FIX ---
            with scol2: difficulty = st.selectbox("Difficulty", ['all', 'easy', 'medium', 'hard'], 0)
            with scol3: time_limit = st.number_input("Time (Mins)", 1, 60, 10, 1)
            host_button = st.form_submit_button("Create Lobby", use_container_width=True, type="primary")

            if host_button:
                conn = None; cursor = None
                try:
                    selected_topic_names = selected_quant + selected_logical + selected_verbal
                    if not selected_topic_names: st.error("Please select at least one topic."); st.stop()
                    all_topics_map = {**quant_topics, **logical_topics, **verbal_topics}; selected_topic_ids = [all_topics_map[name] for name in selected_topic_names]
                    
                    # Fetch the EXACT questions the host wants
                    questions = fetch_questions(selected_topic_ids, difficulty, num_questions)
                    if not questions: st.error("No questions found."); st.stop()
                    
                    # Store only the IDs of these fetched questions
                    question_ids = [q['question_id'] for q in questions]
                    # Store the *actual* number of questions found
                    quiz_settings = {"topics": selected_topic_names, "difficulty": difficulty, "num_questions": len(questions)} 
                    
                    lobby_id = generate_lobby_code()
                    if not lobby_id: st.error("Failed to generate lobby ID."); st.stop()

                    conn = get_db_connection()
                    if not conn: raise mysql.connector.Error("DB connection failed (create lobby)")
                    cursor = conn.cursor()
                    query = "INSERT INTO lobbies (lobby_id, host_user_id, quiz_settings, question_ids, time_limit) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(query, (lobby_id, st.session_state.user_id, json.dumps(quiz_settings), json.dumps(question_ids), time_limit))
                    query_p = "INSERT INTO lobby_participants (lobby_id, user_id) VALUES (%s, %s)"
                    cursor.execute(query_p, (lobby_id, st.session_state.user_id)); conn.commit()
                    st.session_state.current_lobby_id = lobby_id; st.rerun()
                except Exception as e: st.error(f"Error creating lobby: {e}")
                finally:
                    if cursor: cursor.close()
                    if conn and conn.is_connected(): conn.close()

    # --- JOIN GAME ---
    with col2:
        st.subheader("Join an Existing Game")
        default_lobby_id = st.session_state.get('join_lobby_id', "")
        with st.form("join_game_form"):
            lobby_id_input = st.text_input("Enter Game Code", value=default_lobby_id, max_chars=6).upper()
            join_button = st.form_submit_button("Join Lobby", use_container_width=True, type="primary")

            if join_button:
                conn = None; cursor = None
                if not lobby_id_input: st.error("Please enter a game code."); st.stop()
                try:
                    conn = get_db_connection()
                    if not conn: raise mysql.connector.Error("DB connection failed (join lobby)")
                    cursor = conn.cursor(dictionary=True)
                    query = "SELECT status FROM lobbies WHERE lobby_id = %s"
                    cursor.execute(query, (lobby_id_input,)); lobby = cursor.fetchone()
                    if not lobby: st.error("Lobby not found.")
                    elif lobby['status'] != 'waiting': st.error("Game already started or finished.")
                    else:
                        query_p = "INSERT IGNORE INTO lobby_participants (lobby_id, user_id) VALUES (%s, %s)"
                        cursor.execute(query_p, (lobby_id_input, st.session_state.user_id)); conn.commit()
                        if 'join_lobby_id' in st.session_state: del st.session_state.join_lobby_id
                        st.session_state.current_lobby_id = lobby_id_input; st.rerun()
                except Exception as e: st.error(f"Error joining lobby: {e}")
                finally:
                    if cursor: cursor.close()
                    if conn and conn.is_connected(): conn.close()

# --- VIEW 2: WAITING ROOM ---
def show_waiting_room():
    st.title("🎮 Waiting Room")
    run_startup_check() # Run check

    lobby_id = st.session_state.current_lobby_id
    user_id = st.session_state.user_id
    
    lobby = get_lobby_details(lobby_id)
    if not lobby:
        st.error("Lobby not found. Returning to selection.")
        if 'current_lobby_id' in st.session_state: del st.session_state.current_lobby_id
        st.rerun(); st.stop()

    st_autorefresh(interval=5000, key="wait_room_refresh")
    
    st.subheader(f"Game Code: {lobby_id}")
    st.info("Share this code with your friends to invite them!")
    
    # TODO: Change this base_url to your deployed app's URL
    base_url = "http://localhost:8501" 
    share_link = f"{base_url}/?lobby={lobby_id}"
    st.code(share_link)
    st.write("Share this link to invite players directly.")

    st.divider()
    st.subheader("Players in Lobby:")
    participants = get_lobby_participants(lobby_id)
    if not participants: st.warning("You are the only one here...")
    else:
        for p in participants:
            if p['user_id'] == lobby['host_user_id']: st.markdown(f"👑 **{p['username']}** (Host)")
            else: st.markdown(f"👤 {p['username']}")
    
    st.divider()

    if lobby['status'] == 'active':
        st.success("The game is starting! Loading quiz...")
        
        # --- THIS IS THE FIX ---
        # Get the exact list of question IDs saved by the host
        question_id_list = json.loads(lobby['question_ids'])
        # Fetch only those specific questions
        questions = get_questions_by_ids(question_id_list)
        # --- END FIX ---
        
        if not questions: st.error("Failed to load quiz questions."); st.stop()
        
        # Set quiz state
        st.session_state.multiplayer_game_active = True
        st.session_state.questions = questions # Use the correctly fetched questions
        st.session_state.time_limit = lobby['time_limit']
        st.session_state.start_time = lobby['start_timestamp'].timestamp()
        st.session_state.current_question_index = 0
        st.session_state.user_answers = {}
        st.session_state.question_statuses = ['red'] * len(questions) # Status for the correct number
        st.rerun()

    if user_id == lobby['host_user_id']:
        if st.button("Start Game Now", use_container_width=True, type="primary"):
            conn = None; cursor = None
            try:
                conn = get_db_connection()
                if not conn: raise mysql.connector.Error("DB connection failed (start game)")
                cursor = conn.cursor()
                query = "UPDATE lobbies SET status = 'active', start_timestamp = NOW() WHERE lobby_id = %s"
                cursor.execute(query, (lobby_id,)); conn.commit()
                st.rerun()
            except Exception as e: st.error(f"Error starting game: {e}")
            finally:
                if cursor: cursor.close()
                if conn and conn.is_connected(): conn.close()
    else:
        st.info("Waiting for the host to start the game...")

# --- VIEW 3: QUIZ INTERFACE (Re-uses Take_Test logic) ---
def show_multiplayer_quiz_interface():
    st.title("Aptiking Multiplayer Test... ⏳")
    run_startup_check() # Run check
    
    if 'start_time' not in st.session_state or 'time_limit' not in st.session_state or 'questions' not in st.session_state:
        st.error("Test session error. Returning to lobby.");
        if 'current_lobby_id' in st.session_state: del st.session_state.current_lobby_id
        if 'multiplayer_game_active' in st.session_state: del st.session_state.multiplayer_game_active
        st.rerun(); st.stop()

    if st.session_state.get('multiplayer_game_active', False):
        st_autorefresh(interval=1000, key="multi_quiz_timer")
    
    time_elapsed = time.time() - st.session_state.start_time
    time_limit_seconds = st.session_state.time_limit * 60
    time_left = time_limit_seconds - time_elapsed

    q_index = st.session_state.current_question_index
    questions = st.session_state.questions
    total_q = len(questions)

    if time_left <= 0:
        if st.session_state.get('multiplayer_game_active', False):
            st.warning("Time's up! Submitting...");
            answer = st.session_state.get(f"q_multi_{q_index}") # Use multi key
            if answer: st.session_state.user_answers[q_index] = answer
            update_current_question_status(action="move")
            calculate_and_save_multiplayer_results()
            st.session_state.show_multiplayer_results = True
            st.session_state.multiplayer_game_active = False
            for key in ['questions', 'current_question_index', 'user_answers', 'start_time', 'time_limit', 'question_statuses']:
                if key in st.session_state: del st.session_state[key]
            st.rerun()
        return

    q_col, panel_col = st.columns([2, 1]) # Wider panel

    with q_col:
        mins, secs = divmod(int(max(0, time_left)), 60); timer_display = f"{mins:02d}:{secs:02d}"
        t_col1, t_col2 = st.columns([3, 1])
        with t_col1: st.subheader(f"Time Remaining: {timer_display}")
        with t_col2:
            if st.button("Submit Test Now", use_container_width=True, type="primary"):
                if st.session_state.get('multiplayer_game_active', False):
                    update_current_question_status(action="move")
                    calculate_and_save_multiplayer_results()
                    st.session_state.show_multiplayer_results = True
                    st.session_state.multiplayer_game_active = False
                    for key in ['questions', 'current_question_index', 'user_answers', 'start_time', 'time_limit', 'question_statuses']:
                        if key in st.session_state: del st.session_state[key]
                    st.rerun()
        total_duration = time_limit_seconds; progress_value = max(0.0, time_left / max(1, total_duration))
        st.progress(progress_value); st.divider()
        
        q = questions[q_index]
        st.subheader(f"Question {q_index + 1} of {total_q}"); st.markdown(f"**{q.get('question_text', 'Missing text')}**")
        options = {'a': q.get('option_a',''), 'b': q.get('option_b',''), 'c': q.get('option_c',''), 'd': q.get('option_d','')}
        option_keys = list(options.keys()); 
        if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
        saved_answer = st.session_state.user_answers.get(q_index, None) 
        current_index = None
        if saved_answer in option_keys:
            try: current_index = option_keys.index(saved_answer)
            except ValueError: pass
        with st.container():
            user_choice = st.radio("Choose:", option_keys, format_func=lambda k: f"{k}) {options.get(k,'N/A')}", index=current_index, key=f"q_multi_{q_index}")
        if user_choice is not None:
             st.session_state.user_answers[q_index] = user_choice
        st.divider()
        
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            if st.button("⬅️ Previous", key=f"prev_multi_{q_index}", disabled=(q_index <= 0), use_container_width=True, type="primary"):
                update_current_question_status(action="move")
                if q_index > 0: st.session_state.current_question_index -= 1; st.rerun()
        with nav_col2:
            if st.button("Marked For Review", key=f"mark_multi_{q_index}", use_container_width=True):
                update_current_question_status(action="mark") # Use 'mark'
                if q_index < total_q - 1: st.session_state.current_question_index += 1
                st.rerun()
        with nav_col3:
            if st.button("Save and Next ➡️", key=f"next_multi_{q_index}", disabled=(q_index >= total_q - 1), use_container_width=True, type="primary"):
                update_current_question_status(action="save_and_next") # Use 'save_and_next'
                if q_index < total_q - 1: st.session_state.current_question_index += 1
                st.rerun()

    with panel_col:
        st.subheader("Question Panel")
        st.markdown("<span style='color: #28a745;'>● Green:</span> Attempted<br><span style='color: #FF4B4B;'>● Red:</span> Unattempted<br><span style='color: #8A2BE2;'>● Purple:</span> Marked<br><span style='color: #007BFF;'>● Blue:</span> Current", unsafe_allow_html=True)
        st.divider()
        if 'question_statuses' not in st.session_state: st.session_state.question_statuses = ['red'] * total_q
        num_questions = len(st.session_state.question_statuses); cols_per_row = 4
        
        for i in range(num_questions):
            if i % cols_per_row == 0:
                cols = st.columns(cols_per_row)
            
            status = st.session_state.question_statuses[i]
            style_class = f"status-{'current' if i == q_index else status}"
            
            with cols[i % cols_per_row]:
                st.markdown(f'<div class="{style_class}"></div>', unsafe_allow_html=True)
                if st.button(
                    f"{i + 1}",
                    key=f"panel_multi_{i}",
                    on_click=on_panel_click,
                    args=(i,)
                ):
                    pass 

# --- VIEW 4: LEADERBOARD ---
def show_leaderboard():
    st.title("Game Finished! 🏆")
    run_startup_check() # Run startup check
    
    if 'current_lobby_id' not in st.session_state:
        st.error("Lobby ID lost. Returning to selection.")
        st.page_link("pages/8_Multiplayer.py", label="Go to Multiplayer Page")
        st.stop()
        
    lobby_id = st.session_state.current_lobby_id
    lobby = get_lobby_details(lobby_id)
    if not lobby: st.error("Could not find lobby details."); st.stop()

    if 'individual_multiplayer_results' in st.session_state:
        res = st.session_state.individual_multiplayer_results
        st.success(f"Your Score: {res['score']:.0f}% ({res['correct']} / {res['total']})")
    
    st.header("Final Leaderboard")
    
    # Auto-refresh to get scores
    st_autorefresh(interval=5000, key="leaderboard_refresh")
    
    participants = get_lobby_participants(lobby_id)
    
    if not participants:
        st.error("Could not retrieve leaderboard data.")
    else:
        # --- NEW: Create DataFrames for Chart and Table ---
        data_table = []
        data_chart = []
        all_finished = True
        
        for p in participants:
            is_host = (p['user_id'] == lobby['host_user_id'])
            username = "👑 " + p['username'] if is_host else p['username']
            
            # Data for the table
            data_table.append({
                "Username": username,
                "Score (%)": p['score'] if p['score'] is not None else "---",
                "Time (sec)": p['time_taken'] if p['time_taken'] is not None else "---",
                "Status": p['status'].capitalize()
            })
            
            # Data for the chart (only finished players)
            if p['status'] == 'finished' and p['score'] is not None:
                data_chart.append({
                    "Username": username,
                    "Score (%)": p['score']
                })
            elif p['status'] != 'finished':
                all_finished = False
        
        df_table = pd.DataFrame(data_table)
        
        # --- NEW: Matplotlib Bar Chart ---
        if data_chart:
            # Sort by score for the chart (highest score at the top)
            df_chart = pd.DataFrame(data_chart).sort_values(by="Score (%)", ascending=True)
            try:
                # Dynamic height: 1.5 inch base + 0.5 inch per player
                chart_height = 1.5 + len(df_chart) * 0.5
                fig, ax = plt.subplots(figsize=(10, chart_height))
                fig.patch.set_facecolor('#0E1117')
                ax.set_facecolor('#0E1117')
                
                # Create horizontal bars
                bars = ax.barh(df_chart['Username'], df_chart['Score (%)'], color='#FF4B4B')
                
                ax.set_xlabel('Score (%)', color='white')
                ax.set_title('Player Scores', color='white')
                ax.tick_params(axis='x', colors='white')
                ax.tick_params(axis='y', colors='white', labelsize=12) # Larger y-axis labels
                
                ax.spines['top'].set_color('#555')
                ax.spines['right'].set_color('#555')
                ax.spines['bottom'].set_color('white')
                ax.spines['left'].set_color('white')

                # Add score labels on the end of each bar
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + 1, # Position label slightly after the bar
                            bar.get_y() + bar.get_height() / 2,
                            f'{width:.0f}', # Format as integer
                            ha='left', va='center',
                            color='white', fontweight='bold')
                
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error creating chart: {e}")
        else:
            st.info("No scores available for chart yet...")
        # --- END: Matplotlib Bar Chart ---
        
        st.divider()
        st.subheader("Detailed Results")
        st.dataframe(df_table, use_container_width=True, hide_index=True)
        
        if not all_finished and lobby['status'] != 'finished':
            st.info("Waiting for other players to finish... The leaderboard will update automatically.")
        else:
            st.success("All players have finished!")
            # Optional: Set lobby status to finished
            conn = None; cursor = None
            try:
                conn = get_db_connection(); cursor = conn.cursor()
                cursor.execute("UPDATE lobbies SET status = 'finished' WHERE lobby_id = %s AND status != 'finished'", (lobby_id,)) # Add check
                conn.commit()
            except Exception: pass # Not critical
            finally:
                if cursor: cursor.close()
                if conn and conn.is_connected(): conn.close()

    
    st.divider()
    if st.button("Back to Dashboard", use_container_width=True, type="primary"):
        for key in ['current_lobby_id', 'multiplayer_game_active', 'show_multiplayer_results', 'individual_multiplayer_results']:
             if key in st.session_state: del st.session_state[key]
        st.page_link("pages/3_Dashboard.py", label="Go to Dashboard", icon="🏠")
        
# --- MAIN ROUTER ---
if 'show_multiplayer_results' in st.session_state:
    show_leaderboard()
elif 'multiplayer_game_active' in st.session_state:
    show_multiplayer_quiz_interface()
elif 'current_lobby_id' in st.session_state:
    show_waiting_room()
else:
    show_host_or_join_view()