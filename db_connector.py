import mysql.connector
import streamlit as st

def get_db_connection():
    """
    Establishes a connection to the MySQL database.
    Uses WAMP default credentials (root, no password).
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",        
            password="",      
            database="aptitude_db"
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None