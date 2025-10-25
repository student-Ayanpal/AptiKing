import streamlit as st
import hashlib
import mysql.connector
from db_connector import get_db_connection
# DO NOT import LocalStorage globally
import time # Import time

# --- Page configuration ---
st.set_page_config(page_title="Register", layout="centered")

# --- CSS for ONLY the link button after registration ---
st.markdown("""
<style>
/* Styling for the link button after successful registration */
.login-link-button a {
    display: block;
    background-color: #FF4B4B; /* Streamlit red */
    color: white !important;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    text-align: center;
    text-decoration: none !important;
    transition: background-color 0.2s ease;
    border: none;
    margin-top: 1rem;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}
.login-link-button a:hover {
    background-color: #DC3545; /* Darker red */
    color: white !important;
    text-decoration: none !important;
}
/* Optional: Style the primary submit button if type="primary" is used */
/* We rely on type="primary" for the Register button */
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
        # Check if login status exists and is explicitly True
        if isinstance(stored_login_data, dict) and stored_login_data.get('value') is True:
            # If logged in according to storage, try to get user details
            if stored_user_id_data and stored_user_id_data.get('value') is not None:
                user_id = stored_user_id_data['value']
            if stored_username_data and stored_username_data.get('value') is not None:
                username = stored_username_data['value']

            # Only confirm login if we have all details
            if user_id is not None and username is not None:
                logged_in = True
            else:
                # If details are missing despite logged_in=True, force logout
                logged_in = False
                localS_check.setItem('logged_in', False, key="clear_login_inconsistent_reg")
                localS_check.setItem('user_id', None, key="clear_userid_inconsistent_reg") # Use None
                localS_check.setItem('username', None, key="clear_username_inconsistent_reg") # Use None

        # Handle potential old boolean format (and immediately fix/clear it)
        elif isinstance(stored_login_data, bool):
             if stored_login_data is True: # If old format says logged in
                 logged_in = True
                 old_user_id = localS_check.getItem('user_id')
                 old_username = localS_check.getItem('username')
                 # Safely extract values
                 if isinstance(old_user_id, dict) and 'value' in old_user_id: user_id = old_user_id['value']
                 elif isinstance(old_user_id, (int, str)): user_id = old_user_id
                 if isinstance(old_username, dict) and 'value' in old_username: username = old_username['value']
                 elif isinstance(old_username, str): username = old_username
                 # Overwrite with correct format only if details are valid
                 if user_id is not None and username is not None:
                     localS_check.setItem('logged_in', True, key="fix_login_reg_func")
                     localS_check.setItem('user_id', user_id, key="fix_userid_reg_func")
                     localS_check.setItem('username', username, key="fix_username_reg_func")
                 else: # If details invalid from old format, clear storage
                      logged_in = False
                      localS_check.setItem('logged_in', False, key="clear_login_old_invalid_reg")
                      localS_check.setItem('user_id', None, key="clear_userid_old_invalid_reg")
                      localS_check.setItem('username', None, key="clear_username_old_invalid_reg")
             else: # If old format was False, ensure cleared properly
                  logged_in = False
                  localS_check.setItem('logged_in', False, key="clear_login_old_false_reg")
                  localS_check.setItem('user_id', None, key="clear_userid_old_false_reg")
                  localS_check.setItem('username', None, key="clear_username_old_false_reg")
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
    if st.sidebar.button("Logout", key="logout_reg_sidebar"):
        from streamlit_local_storage import LocalStorage # Import locally
        localS_logout = LocalStorage() # Initialize locally
        # --- Explicitly set logged_in to False, others to None ---
        localS_logout.setItem('logged_in', False, key="logout_set_login_status_reg") # Unique key
        localS_logout.setItem('user_id', None, key="logout_set_userid_none_reg")       # Unique key, use None
        localS_logout.setItem('username', None, key="logout_set_username_none_reg")   # Unique key, use None
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

# --- Helper Function ---
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- Page Content ---
st.title("User Registration 📝")

with st.form("register_form"):
    st.write("Please fill in the details below to create an account.")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    # Use built-in styling for reliability
    submitted = st.form_submit_button("Register", type="primary", use_container_width=True)

if submitted:
    if not username or not email or not password or not confirm_password:
        st.warning("Please fill out all fields.")
    elif password != confirm_password:
        st.error("Passwords do not match!")
    else:
        conn = None # Initialize conn
        cursor = None # Initialize cursor
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                hashed_pw = hash_password(password)
                query = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
                cursor.execute(query, (username, email, hashed_pw))
                conn.commit()
                st.success(f"Account created successfully for {username}!")
                # Apply styling to the link button as well
                st.markdown('<div class="login-link-button">', unsafe_allow_html=True)
                st.page_link("pages/2_Login.py", label="Click here to Login 🔐")
                st.markdown('</div>', unsafe_allow_html=True)

        except mysql.connector.Error as e:
            if e.errno == 1062: st.error(f"Username or email already taken.")
            else: st.error(f"An error occurred: {e}")
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()