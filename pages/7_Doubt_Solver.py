import streamlit as st
import google.generativeai as genai
import time
# DO NOT import LocalStorage globally
# from streamlit_local_storage import LocalStorage

# --- Page configuration ---
st.set_page_config(page_title="Doubt Solver", layout="wide")

# --- Inject CSS for Button Styling (Optional - if you want red 'Get Answer' button) ---
st.markdown("""
<style>
/* Target the regular button used for 'Get Answer' */
.stButton>button {
    background-color: #FF4B4B !important; /* Streamlit red */
    color: white !important; border: none !important; padding: 0.75rem 1rem !important;
    border-radius: 0.5rem !important; transition: background-color 0.2s ease !important;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7) !important;
    width: 100% !important; /* Make it full width if desired */
}
.stButton>button:hover { background-color: #DC3545 !important; color: white !important; border: none !important; }
.stButton>button:active { background-color: #B02A37 !important; color: white !important; border: none !important; }
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
                localS_check.setItem('logged_in', False, key="clear_login_inconsistent_doubt")
                localS_check.setItem('user_id', None, key="clear_userid_inconsistent_doubt")
                localS_check.setItem('username', None, key="clear_username_inconsistent_doubt")
        elif isinstance(stored_login_data, bool): # Handle old boolean format
             if stored_login_data is True:
                 logged_in = True
                 old_user_id = localS_check.getItem('user_id'); old_username = localS_check.getItem('username')
                 if isinstance(old_user_id, dict) and 'value' in old_user_id: user_id = old_user_id['value']
                 elif isinstance(old_user_id, (int, str)): user_id = old_user_id
                 if isinstance(old_username, dict) and 'value' in old_username: username = old_username['value']
                 elif isinstance(old_username, str): username = old_username
                 if user_id is not None and username is not None:
                     localS_check.setItem('logged_in', True, key="fix_login_doubt_func")
                     localS_check.setItem('user_id', user_id, key="fix_userid_doubt_func")
                     localS_check.setItem('username', username, key="fix_username_doubt_func")
                 else: # Invalid details from old format
                      logged_in = False
                      localS_check.setItem('logged_in', False, key="clear_login_old_invalid_doubt")
                      localS_check.setItem('user_id', None, key="clear_userid_old_invalid_doubt")
                      localS_check.setItem('username', None, key="clear_username_old_invalid_doubt")
             else: # Old format was False
                  logged_in = False
                  localS_check.setItem('logged_in', False, key="clear_login_old_false_doubt")
                  localS_check.setItem('user_id', None, key="clear_userid_old_false_doubt")
                  localS_check.setItem('username', None, key="clear_username_old_false_doubt")
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
    if st.sidebar.button("Logout", key="logout_doubt_sidebar"):
        from streamlit_local_storage import LocalStorage # Import locally
        localS_logout = LocalStorage() # Initialize locally
        # --- Explicitly set logged_in to False, others to None ---
        localS_logout.setItem('logged_in', False, key="logout_set_login_status_doubt") # Unique key
        localS_logout.setItem('user_id', None, key="logout_set_userid_none_doubt")       # Unique key, use None
        localS_logout.setItem('username', None, key="logout_set_username_none_doubt")   # Unique key, use None
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
st.title("Aptiking Doubt Solver ❓") # <-- TITLE RENDERS FIRST


# --- Page Logic ---
st.write("Ask about an aptitude topic or problem!")

# --- Configure Gemini API ---
try:
    # Ensure secrets are loaded correctly
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found in secrets.toml")
        st.stop()
    genai.configure(api_key=api_key)
    # Ensure the model name is correct and available for your key
    model = genai.GenerativeModel('models/gemini-pro-latest') # Or your specific available model
except Exception as e:
    st.error(f"API Configuration Error: {e}")
    st.stop()

# --- User Input ---
user_question = st.text_area("Type your doubt here...", height=150, placeholder="e.g., Explain compound interest formula.")

# Button - CSS should style this (removed type="primary")
if st.button("Get Answer", use_container_width=True):
    if user_question:
        with st.spinner("Thinking... 🧠"):
            try:
                prompt = f"You are Aptiking, an expert aptitude tutor. Answer clearly, concisely, and step-by-step if needed.\nStudent's Doubt: \"{user_question}\""
                # Make the API call
                response = model.generate_content(prompt)
                # Display the response
                st.divider()
                st.subheader("Answer:")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error generating answer: {e}") # Provide more specific error
    else:
        st.warning("Please enter your question first.")