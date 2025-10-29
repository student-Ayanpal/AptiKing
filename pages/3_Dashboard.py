import streamlit as st
from streamlit_local_storage import LocalStorage # Corrected import
import time # Import time

# --- Page configuration ---
st.set_page_config(page_title="Dashboard", layout="wide")

# --- Inject CSS for Button Styling ---
st.markdown("""
<style>
/* Style for the link buttons */
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
    margin-top: 0.75rem; /* Space between image and button */
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}
/* Style for hover */
.dashboard-button-link:hover {
    background-color: #DC3545; /* Darker red */
    color: white !important; /* Keep text white on hover */
    text-decoration: none !important; /* Ensure no underline */
}
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
        logged_in = False; user_id = None; username = None
        if isinstance(stored_login_data, dict) and stored_login_data.get('value') is True:
            if stored_user_id_data and stored_user_id_data.get('value') is not None: user_id = stored_user_id_data['value']
            if stored_username_data and stored_username_data.get('value') is not None: username = stored_username_data['value']
            if user_id is not None and username is not None: logged_in = True
            else: logged_in = False; localS_check.setItem('logged_in', False, key="clear_login_inconsistent_dash"); localS_check.setItem('user_id', None, key="clear_userid_inconsistent_dash"); localS_check.setItem('username', None, key="clear_username_inconsistent_dash")
        elif isinstance(stored_login_data, bool):
             if stored_login_data is True:
                 logged_in = True; old_user_id = localS_check.getItem('user_id'); old_username = localS_check.getItem('username')
                 if isinstance(old_user_id, dict) and 'value' in old_user_id: user_id = old_user_id['value']
                 elif isinstance(old_user_id, (int, str)): user_id = old_user_id
                 if isinstance(old_username, dict) and 'value' in old_username: username = old_username['value']
                 elif isinstance(old_username, str): username = old_username
                 if user_id is not None and username is not None: localS_check.setItem('logged_in', True, key="fix_login_dash_func"); localS_check.setItem('user_id', user_id, key="fix_userid_dash_func"); localS_check.setItem('username', username, key="fix_username_dash_func")
                 else: logged_in = False; localS_check.setItem('logged_in', False, key="clear_login_old_invalid_dash"); localS_check.setItem('user_id', None, key="clear_userid_old_invalid_dash"); localS_check.setItem('username', None, key="clear_username_old_invalid_dash")
             else: logged_in = False; localS_check.setItem('logged_in', False, key="clear_login_old_false_dash"); localS_check.setItem('user_id', None, key="clear_userid_old_false_dash"); localS_check.setItem('username', None, key="clear_username_old_false_dash")
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
    if st.sidebar.button("Logout", key="logout_dash_sidebar"):
        from streamlit_local_storage import LocalStorage
        localS_logout = LocalStorage()
        localS_logout.setItem('logged_in', False, key="logout_set_login_status_dash")
        localS_logout.setItem('user_id', None, key="logout_set_userid_none_dash")
        localS_logout.setItem('username', None, key="logout_set_username_none_dash")
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

# --- Page Title ---
if 'username' in st.session_state:
    st.title(f"Welcome to your Dashboard, {st.session_state.username}! 👋")
else:
     st.title("Welcome to your Dashboard! 👋")

# --- Page Content ---
st.subheader("What would you like to do today?")
st.divider()

# --- UPDATED LAYOUT: 5 columns in a single row ---
col1, col2, col3, col4, col5 = st.columns(5)

# --- Feature 1: Take Test ---
with col1:
    st.image("images/take_test.png") # Removed width
    st.markdown(f""" <a href="Take_Test" target="_self" class="dashboard-button-link"> Take a New Test 📝 </a> """, unsafe_allow_html=True)

# --- Feature 2: View Progress ---
with col2:
    st.image("images/progress.png") # Removed width
    st.markdown(f""" <a href="Your_Progress" target="_self" class="dashboard-button-link"> View Your Progress 📊 </a> """, unsafe_allow_html=True)

# --- Feature 3: Study Materials ---
with col3:
    st.image("images/study_materials.png") # Removed width
    st.markdown(f""" <a href="Study_Materials" target="_self" class="dashboard-button-link"> Get Study Materials 📚 </a> """, unsafe_allow_html=True)

# --- Feature 4: Doubt Solver ---
with col4:
    st.image("images/doubt_solver.png") # Removed width
    st.markdown(f""" <a href="Doubt_Solver" target="_self" class="dashboard-button-link"> Ask a Doubt ❓ </a> """, unsafe_allow_html=True)

# --- Feature 5: Multiplayer ---
with col5:
    st.image("images/multiplayer.png") # Removed width
    st.markdown(f""" <a href="Multiplayer" target="_self" class="dashboard-button-link"> 🎮 Multiplayer Quiz </a> """, unsafe_allow_html=True)