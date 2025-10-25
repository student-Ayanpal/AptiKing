import streamlit as st
from streamlit_local_storage import LocalStorage 
import hashlib
from db_connector import get_db_connection
import mysql.connector
import time 


st.set_page_config(page_title="Login", layout="centered")


st.markdown("""
<style>
/* Styling for the link button (Go to Home Page) */
.home-link-button { /* Apply style directly to the link */
    display: block;
    background-color: #FF4B4B; /* Streamlit red */
    color: white !important;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    text-align: center;
    text-decoration: none !important;
    transition: background-color 0.2s ease;
    border: none;
    margin-top: 1rem; /* Add space above link button */
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}
.home-link-button:hover { /* Hover state for the link */
    background-color: #DC3545; /* Darker red */
    color: white !important;
    text-decoration: none !important;
}
/* Optional: Style the primary submit button if type="primary" is used */
/* We rely on type="primary" for the Login button */
</style>
""", unsafe_allow_html=True)


localS_sidebar_log = LocalStorage()
if 'logged_in' in st.session_state and st.session_state.logged_in:
    
    username_display = st.session_state.get('username', 'User')
    st.sidebar.success(f"Logged in as {username_display}")
    if st.sidebar.button("Logout", key="logout_login_sidebar"): 
    
        localS_sidebar_log.setItem('logged_in', False, key="logout_set_login_status_loginpg") 
        localS_sidebar_log.setItem('user_id', None, key="logout_set_userid_none_loginpg")       
        localS_sidebar_log.setItem('username', None, key="logout_set_username_none_loginpg")   

    
        keys_to_clear = list(st.session_state.keys())
        for key_to_del in keys_to_clear:
            if key_to_del != 'startup_check_done':
                 try: del st.session_state[key_to_del]
                 except KeyError: pass
        
        time.sleep(0.2)
        st.rerun() 
else:
    st.sidebar.info("You are not logged in.")



st.title("User Login 🔐") 


localS = LocalStorage() 


if 'startup_check_done' not in st.session_state:
    stored_login_data = localS.getItem('logged_in')
    stored_user_id_data = localS.getItem('user_id')
    stored_username_data = localS.getItem('username')
    logged_in = False
    user_id = None
    username = None

    
    if isinstance(stored_login_data, dict) and stored_login_data.get('value') is not None:
        
        if isinstance(stored_login_data['value'], bool) and stored_login_data['value']:
            logged_in = True
            if stored_user_id_data and 'value' in stored_user_id_data: user_id = stored_user_id_data['value']
            if stored_username_data and 'value' in stored_username_data: username = stored_username_data['value']
        else: logged_in = False
    elif isinstance(stored_login_data, bool) and stored_login_data:
        
         logged_in = True
         old_user_id = localS.getItem('user_id')
         old_username = localS.getItem('username')
         if isinstance(old_user_id, dict) and 'value' in old_user_id: user_id = old_user_id['value']
         elif isinstance(old_user_id, (int, str)): user_id = old_user_id
         if isinstance(old_username, dict) and 'value' in old_username: username = old_username['value']
         elif isinstance(old_username, str): username = old_username
         if user_id is not None and username is not None:
             localS.setItem('logged_in', True, key="fix_login_loginpg")
             localS.setItem('user_id', user_id, key="fix_userid_loginpg")
             localS.setItem('username', username, key="fix_username_loginpg")
         else:
             logged_in = False
             localS.setItem('logged_in', False, key="clear_login_loginpg")
             localS.setItem('user_id', None, key="clear_userid_loginpg") # Use None
             localS.setItem('username', None, key="clear_username_loginpg") # Use None

    
    if logged_in and user_id is not None and username is not None:
        st.session_state.logged_in = True
        st.session_state.user_id = user_id
        st.session_state.username = username
    else: 
        if 'logged_in' in st.session_state: del st.session_state.logged_in
        if 'user_id' in st.session_state: del st.session_state.user_id
        if 'username' in st.session_state: del st.session_state.username

    st.session_state.startup_check_done = True




def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


if 'logged_in' in st.session_state and st.session_state.logged_in:

    st.success(f"You are already logged in as {st.session_state.get('username', 'User')}.")
    
    st.markdown(f"""
    <a href="/" target="_self" class="home-link-button">
        Go to Home Page
    </a>
    """, unsafe_allow_html=True)

else:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True) 

    if submitted:
        if not username or not password:
            st.warning("Please enter both username and password.")
        else:
            conn = None
            cursor = None
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    query = "SELECT user_id, password_hash FROM users WHERE username = %s"
                    cursor.execute(query, (username,))
                    result = cursor.fetchone()
                    if result:
                        user_id_db, stored_hash = result
                        entered_hash = hash_password(password)
                        if entered_hash == stored_hash:
                            st.success(f"Welcome back, {username}!")
                            st.session_state['logged_in'] = True
                            st.session_state['username'] = username
                            st.session_state['user_id'] = user_id_db

                            
                            localS.setItem('logged_in', True, key="login_set_status") 
                            localS.setItem('user_id', user_id_db, key="login_set_userid") 
                            localS.setItem('username', username, key="login_set_username") 

                            st.markdown(f"""
                            <a href="/" target="_self" class="home-link-button">
                                Go to Home Page
                            </a>
                            """, unsafe_allow_html=True)
                            
                            time.sleep(0.1)
                            st.rerun() 
                        else:
                            st.error("Invalid username or password.")
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.error("Database connection failed.")
            except mysql.connector.Error as e:
                st.error(f"Database error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn and conn.is_connected():
                    conn.close()