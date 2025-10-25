import streamlit as st
from db_connector import get_db_connection
import mysql.connector
import pandas as pd
# DO NOT import LocalStorage globally
import time # Import time

# --- Page configuration ---
st.set_page_config(page_title="Your Progress", layout="wide")

# --- Inject CSS for Button Styling ---
st.markdown("""
<style>
/* Style for the link button */
.dashboard-button-link {
    display: block;
    background-color: #FF4B4B; /* Streamlit red */
    color: white !important; /* Force white text */
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    text-align: center;
    text-decoration: none !important; /* Remove underline */
    transition: background-color 0.2s ease;
    border: none;
    margin-top: 0.75rem; /* Space */
    /* Text shadow for better visibility */
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}
/* Style for hover */
.dashboard-button-link:hover {
    background-color: #DC3545; /* Darker red */
    color: white !important; /* Keep text white on hover */
    text-decoration: none !important; /* Ensure no underline */
}
/* Specifically target the link text color again if needed */
.dashboard-button-link span {
     color: white !important;
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
                localS_check.setItem('logged_in', False, key="clear_login_inconsistent_prog")
                localS_check.setItem('user_id', None, key="clear_userid_inconsistent_prog")
                localS_check.setItem('username', None, key="clear_username_inconsistent_prog")
        elif isinstance(stored_login_data, bool): # Handle old boolean format
             if stored_login_data is True:
                 logged_in = True
                 old_user_id = localS_check.getItem('user_id'); old_username = localS_check.getItem('username')
                 if isinstance(old_user_id, dict) and 'value' in old_user_id: user_id = old_user_id['value']
                 elif isinstance(old_user_id, (int, str)): user_id = old_user_id
                 if isinstance(old_username, dict) and 'value' in old_username: username = old_username['value']
                 elif isinstance(old_username, str): username = old_username
                 if user_id is not None and username is not None:
                     localS_check.setItem('logged_in', True, key="fix_login_prog_func")
                     localS_check.setItem('user_id', user_id, key="fix_userid_prog_func")
                     localS_check.setItem('username', username, key="fix_username_prog_func")
                 else: # Invalid details from old format
                      logged_in = False
                      localS_check.setItem('logged_in', False, key="clear_login_old_invalid_prog")
                      localS_check.setItem('user_id', None, key="clear_userid_old_invalid_prog")
                      localS_check.setItem('username', None, key="clear_username_old_invalid_prog")
             else: # Old format was False
                  logged_in = False
                  localS_check.setItem('logged_in', False, key="clear_login_old_false_prog")
                  localS_check.setItem('user_id', None, key="clear_userid_old_false_prog")
                  localS_check.setItem('username', None, key="clear_username_old_false_prog")
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
    if st.sidebar.button("Logout", key="logout_prog_sidebar"):
        from streamlit_local_storage import LocalStorage # Import locally
        localS_logout = LocalStorage() # Initialize locally
        # --- Explicitly set logged_in to False, others to None ---
        localS_logout.setItem('logged_in', False, key="logout_set_login_status_prog") # Unique key
        localS_logout.setItem('user_id', None, key="logout_set_userid_none_prog")       # Unique key, use None
        localS_logout.setItem('username', None, key="logout_set_username_none_prog")   # Unique key, use None
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

# --- Page Title ---
st.title("Your Progress 📊") # <-- TITLE RENDERS FIRST


# --- Helper Functions ---
def get_last_5_scores(user_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn: raise mysql.connector.Error("DB connection failed")
        cursor = conn.cursor(dictionary=True)
        query = "SELECT score, test_timestamp FROM tests WHERE user_id = %s ORDER BY test_timestamp DESC LIMIT 5"
        cursor.execute(query, (user_id,))
        scores = cursor.fetchall()
        return scores
    except mysql.connector.Error as e:
        st.error(f"DB Error fetching scores: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

def get_test_history(user_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn: raise mysql.connector.Error("DB connection failed")
        cursor = conn.cursor(dictionary=True)
        query = "SELECT test_id, test_timestamp, score, total_questions FROM tests WHERE user_id = %s ORDER BY test_timestamp DESC"
        cursor.execute(query, (user_id,))
        history = cursor.fetchall()
        return history
    except mysql.connector.Error as e:
        st.error(f"DB Error fetching history: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

# --- Page Logic ---
# Ensure user_id exists before proceeding
if 'user_id' not in st.session_state:
     st.error("User session error. Please log in again.")
     st.stop()
user_id = st.session_state['user_id']


st.header("Your Last 5 Test Scores")
last_5_scores_data = get_last_5_scores(user_id)
if not last_5_scores_data:
    st.info("No tests completed yet.")
else:
    df_scores = pd.DataFrame(last_5_scores_data).iloc[::-1].reset_index(drop=True)
    df_scores.rename(columns={'score': 'Score'}, inplace=True)
    df_scores['Test Number'] = [f"Test {i+1}" for i in df_scores.index]
    st.line_chart(df_scores, x='Test Number', y='Score')


st.divider()
st.header("Your Full Test History")
history_data = get_test_history(user_id)
if not history_data:
    st.info("No test history found.")
else:
    df_history = pd.DataFrame(history_data)
    # Ensure 'test_timestamp' is datetime before formatting
    df_history['test_timestamp'] = pd.to_datetime(df_history['test_timestamp'], errors='coerce') # Add coerce
    df_history.dropna(subset=['test_timestamp'], inplace=True) # Drop rows where conversion failed
    df_history['Date & Time'] = df_history['test_timestamp'].dt.strftime('%Y-%m-%d %I:%M %p')
    df_history.rename(columns={'test_id': 'ID', 'score': 'Score (%)', 'total_questions': 'Total Qs'}, inplace=True)
    # Select and display relevant columns
    st.dataframe(df_history[['ID', 'Date & Time', 'Score (%)', 'Total Qs']], use_container_width=True, hide_index=True)


st.divider()
# Use the CSS class directly on the link - CORRECTED HREF
st.markdown(f"""
<a href="Take_Test" target="_self" class="dashboard-button-link">
    Take Another Test ↩️
</a>
""", unsafe_allow_html=True)