import streamlit as st
import time 


st.set_page_config(page_title="AptiKing", page_icon="👑", layout="wide")


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
    margin-top: 0.25rem; /* Reduced space between prompt and button */
    /* Text shadow for better visibility */
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}
/* Style for hover */
.dashboard-button-link:hover {
    background-color: #DC3545; /* Darker red */
    color: white !important; /* Keep text white on hover */
    text-decoration: none !important; /* Ensure no underline */
}

/* --- Temporarily Comment Out Info Container CSS --- */
/*
.info-container {
    border: 1px solid #4F8BF9;
    border-radius: 0.5rem;
    padding: 1.5rem;
    background-color: rgba(79, 139, 249, 0.1);
    margin-bottom: 1.5rem;
    margin-top: 1rem;
    font-size: 18px;
    color: inherit;
}
.info-container b {
    color: inherit !important;
}
*/
/* --- End Comment Out --- */

/* Style for small text above buttons */
.button-prompt {
    font-size: 0.9rem;
    color: #a0a0a0; /* Lighter text color */
    text-align: center;
    margin-bottom: 0.1rem; /* Small space below prompt */
}
</style>
""", unsafe_allow_html=True)



def run_startup_check():
    
    if 'startup_check_done' not in st.session_state:
        from streamlit_local_storage import LocalStorage 
        localS_check = LocalStorage() 

        stored_login_data = localS_check.getItem('logged_in')
        stored_user_id_data = localS_check.getItem('user_id')
        stored_username_data = localS_check.getItem('username')
        logged_in = False
        user_id = None
        username = None

        
        if isinstance(stored_login_data, dict) and stored_login_data.get('value') is True:
    
            if stored_user_id_data and stored_user_id_data.get('value') is not None:
                user_id = stored_user_id_data['value']
            if stored_username_data and stored_username_data.get('value') is not None:
                username = stored_username_data['value']

            
            if user_id is not None and username is not None:
                logged_in = True
            else:
                
                logged_in = False
                localS_check.setItem('logged_in', False, key="clear_login_inconsistent_home")
                localS_check.setItem('user_id', None, key="clear_userid_inconsistent_home") 
                localS_check.setItem('username', None, key="clear_username_inconsistent_home") 

        
        elif isinstance(stored_login_data, bool):
             if stored_login_data is True: 
                 logged_in = True
                 old_user_id = localS_check.getItem('user_id')
                 old_username = localS_check.getItem('username')
                
                 if isinstance(old_user_id, dict) and 'value' in old_user_id: user_id = old_user_id['value']
                 elif isinstance(old_user_id, (int, str)): user_id = old_user_id
                 if isinstance(old_username, dict) and 'value' in old_username: username = old_username['value']
                 elif isinstance(old_username, str): username = old_username
                 
                 if user_id is not None and username is not None:
                     localS_check.setItem('logged_in', True, key="fix_login_home_func")
                     localS_check.setItem('user_id', user_id, key="fix_userid_home_func")
                     localS_check.setItem('username', username, key="fix_username_home_func")
                 else: 
                      logged_in = False
                      localS_check.setItem('logged_in', False, key="clear_login_old_invalid_home")
                      localS_check.setItem('user_id', None, key="clear_userid_old_invalid_home")
                      localS_check.setItem('username', None, key="clear_username_old_invalid_home")
             else: 
                  logged_in = False
                  localS_check.setItem('logged_in', False, key="clear_login_old_false_home")
                  localS_check.setItem('user_id', None, key="clear_userid_old_false_home")
                  localS_check.setItem('username', None, key="clear_username_old_false_home")
        
        if logged_in and user_id is not None and username is not None:
            st.session_state.logged_in = True
            st.session_state.user_id = user_id
            st.session_state.username = username
        else: 
            if 'logged_in' in st.session_state: del st.session_state.logged_in
            if 'user_id' in st.session_state: del st.session_state.user_id
            if 'username' in st.session_state: del st.session_state.username

        st.session_state.startup_check_done = True

run_startup_check()


if 'logged_in' in st.session_state and st.session_state.logged_in:
    username_display = st.session_state.get('username', 'User')
    st.sidebar.success(f"Logged in as {username_display}")
    if st.sidebar.button("Logout", key="logout_home_sidebar"):
        from streamlit_local_storage import LocalStorage 
        localS_logout = LocalStorage() 
    
        localS_logout.setItem('logged_in', False, key="logout_set_login_status_home") 
        localS_logout.setItem('user_id', None, key="logout_set_userid_none_home")       
        localS_logout.setItem('username', None, key="logout_set_username_none_home")   

    
        keys_to_clear = list(st.session_state.keys())
        for key_to_del in keys_to_clear:
            if key_to_del != 'startup_check_done':
                 try: del st.session_state[key_to_del]
                 except KeyError: pass
        
        time.sleep(0.2)
        st.rerun()
else:
    st.sidebar.info("You are not logged in.")


st.title("Welcome to Aptiking! 👑")


st.markdown('<div class="info-container">', unsafe_allow_html=True) 
st.markdown("""
    Tired of scattered notes and confusing test platforms? <b>Aptiking</b> is your all-in-one
    solution to conquer aptitude.
    <br><br>
    ✔️ Master key topics with our study materials.<br>
    ✔️ Sharpen your skills with custom quizzes.<br>
    ✔️ Track your progress on your personal dashboard.<br>
    ✔️ AptiKing Doubt Solver for solving Doubts 24/7.<br>
    <br>
    <b>Stop guessing. Start mastering.</b>
""", unsafe_allow_html=True) 
st.markdown('</div>', unsafe_allow_html=True) 




if 'logged_in' in st.session_state and st.session_state.logged_in:
    
    st.write("You are logged in. Please proceed to your dashboard.")
    
    st.markdown(f"""
    <a href="Dashboard" target="_self" class="dashboard-button-link" style="max-width: 400px; margin: 1rem auto;">
        Go to My Dashboard 🚀
    </a>
    """, unsafe_allow_html=True)

else:
    
    st.write("Please log in or register to begin your journey.")

    col1, col2 = st.columns(2)
    with col1:
        
        st.markdown('<p class="button-prompt">New User?</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <a href="Register" target="_self" class="dashboard-button-link">
            📝 Register Now
        </a>
        """, unsafe_allow_html=True)
    with col2:
        
        st.markdown('<p class="button-prompt">Already have an account?</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <a href="Login" target="_self" class="dashboard-button-link">
            🔐 Login
        </a>
        """, unsafe_allow_html=True)