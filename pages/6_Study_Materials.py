import streamlit as st
from db_connector import get_db_connection
import mysql.connector
import os
import time 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



st.set_page_config(page_title="Study Materials", layout="wide")


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
            if stored_user_id_data and stored_user_id_data.get('value') is not None: user_id = stored_user_id_data['value']
            if stored_username_data and stored_username_data.get('value') is not None: username = stored_username_data['value']
            if user_id is not None and username is not None: logged_in = True
            else: 
                logged_in = False
                localS_check.setItem('logged_in', False, key="clear_login_inconsistent_study")
                localS_check.setItem('user_id', None, key="clear_userid_inconsistent_study")
                localS_check.setItem('username', None, key="clear_username_inconsistent_study")
        elif isinstance(stored_login_data, bool): 
             if stored_login_data is True:
                 logged_in = True
                 old_user_id = localS_check.getItem('user_id'); old_username = localS_check.getItem('username')
                 if isinstance(old_user_id, dict) and 'value' in old_user_id: user_id = old_user_id['value']
                 elif isinstance(old_user_id, (int, str)): user_id = old_user_id
                 if isinstance(old_username, dict) and 'value' in old_username: username = old_username['value']
                 elif isinstance(old_username, str): username = old_username
                 if user_id is not None and username is not None:
                     localS_check.setItem('logged_in', True, key="fix_login_study_func")
                     localS_check.setItem('user_id', user_id, key="fix_userid_study_func")
                     localS_check.setItem('username', username, key="fix_username_study_func")
                 else: 
                      logged_in = False
                      localS_check.setItem('logged_in', False, key="clear_login_old_invalid_study")
                      localS_check.setItem('user_id', None, key="clear_userid_old_invalid_study")
                      localS_check.setItem('username', None, key="clear_username_old_invalid_study")
             else: 
                  logged_in = False
                  localS_check.setItem('logged_in', False, key="clear_login_old_false_study")
                  localS_check.setItem('user_id', None, key="clear_userid_old_false_study")
                  localS_check.setItem('username', None, key="clear_username_old_false_study")
        

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
    if st.sidebar.button("Logout", key="logout_study_sidebar"):
        from streamlit_local_storage import LocalStorage
        localS_logout = LocalStorage() 
        localS_logout.setItem('logged_in', False, key="logout_set_login_status_study") 
        localS_logout.setItem('user_id', None, key="logout_set_userid_none_study")       
        localS_logout.setItem('username', None, key="logout_set_username_none_study")   
        
        keys_to_clear = list(st.session_state.keys())
        for key_to_del in keys_to_clear:
            if key_to_del != 'startup_check_done':
                 try: del st.session_state[key_to_del]
                 except KeyError: pass
        
        time.sleep(0.2)
        st.rerun()
else:
    st.sidebar.info("You are not logged in.")



if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view this page.")
    st.page_link("pages/2_Login.py", label="Go to Login Page 🔐")
    st.stop()



st.title("Study Materials 📚") 



def get_topics_by_category(category):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn: raise mysql.connector.Error("DB connection failed")
        cursor = conn.cursor()
        query = "SELECT topic_name FROM topics WHERE category = %s ORDER BY topic_name"
        cursor.execute(query, (category,))
        
        topics = [item[0] for item in cursor.fetchall()]
        return topics
    except mysql.connector.Error as e:
        st.error(f"DB Error fetching topics: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()


@st.cache_data(ttl=3600) 
def search_youtube_videos(query, api_key, max_results=3):
    """Searches YouTube for videos based on a query."""
    if not api_key:
        st.warning("YouTube API Key not found in secrets. Cannot search for videos.")
        return []
    try:
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        search_response = youtube.search().list(
            q=query,
            part='snippet', 
            maxResults=max_results,
            type='video', 
            relevanceLanguage='en', 
            # topicId='/m/01k8wb'
        ).execute()

        videos = []
        
        for search_result in search_response.get('items', []):
            if 'videoId' in search_result.get('id', {}): # Ensure it's a video result
                video_id = search_result['id']['videoId']
                video_title = search_result['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                thumbnail_url = search_result['snippet']['thumbnails']['high']['url']
                videos.append({'title': video_title, 'url': video_url, 'thumbnail': thumbnail_url})
        return videos
    except HttpError as e:
    
        st.error(f"YouTube API Error {e.resp.status}: {e.content}")
        return []
    except Exception as e:
        st.error(f"An error occurred searching YouTube: {e}")
        return []




st.write("Select a category and topic to download a cheatsheet and find relevant videos.")

categories = ['Quantitative', 'Logical', 'Verbal']
selected_category = st.selectbox("Step 1: Choose a category", options=categories, index=None, placeholder="Select category...")

if selected_category:
    topic_list = get_topics_by_category(selected_category)
    if not topic_list:
        st.warning(f"No topics found for {selected_category}. Please add topics via admin/DB.")
        st.stop() 

    selected_topic = st.selectbox("Step 2: Choose a topic", options=topic_list, index=None, placeholder="Select topic...")

    if selected_topic:
        
        st.subheader(f"Cheatsheet for '{selected_topic}'")
    
        current_dir = os.path.dirname(os.path.abspath(__file__)) 
        project_root = os.path.dirname(current_dir) 
        file_path = os.path.join(project_root, "study_materials", selected_category, f"{selected_topic}.pdf")

        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as file:
                    pdf_data = file.read()
                st.download_button(
                    label=f"Download {selected_topic}.pdf",
                    data=pdf_data,
                    file_name=f"{selected_topic}_cheatsheet.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Error reading file '{file_path}': {e}")
        else:
            st.error(f"Sorry, the cheatsheet for '{selected_topic}' is not available yet.")
            st.info(f"Admin: Add '{selected_topic}.pdf' to 'study_materials/{selected_category}/' folder.")

        st.divider() 

        
        st.subheader(f"Recommended Videos for '{selected_topic}'")
        youtube_api_key = st.secrets.get("YOUTUBE_API_KEY") 
        search_query = f"{selected_topic} aptitude tutorial explanation tricks" 

        
        with st.spinner(f"Searching YouTube..."):
            video_results = search_youtube_videos(search_query, youtube_api_key, max_results=3)

        if not video_results:
            st.info("No relevant YouTube videos found, or there was an API error.")
        else:
            st.write("Here are a few videos that might help:")
        
            cols = st.columns(len(video_results))
            for i, video in enumerate(video_results):
                with cols[i]:
                    st.image(video['thumbnail'], use_container_width=True) 
                    st.markdown(f"**[{video['title']}]({video['url']})**", unsafe_allow_html=True)