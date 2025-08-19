# app.py
"""
Streamlit UI for Conversational Kitchen Assistant with Login/Signup Authentication.
"""
import streamlit as st
import sqlite3
import pandas as pd
from auth import create_usertable, add_userdata, login_user, hash_password, check_user_exists
from query_bot import fetch_recipe

# Export users to CSV safely
def export_users_to_csv():
    conn = sqlite3.connect("users.db")
    df = pd.read_sql_query("SELECT * FROM userstable", conn) # Changed 'users' to 'userstable'
    df.to_csv("users.csv", index=False)
    conn.close()

# Page settings
st.set_page_config(page_title="Kitchen Assistant", page_icon="🍳", layout="centered")

# Ensure DB exists
create_usertable()

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Authentication
if not st.session_state.logged_in:
    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)

    st.markdown("<h1 style='font-size:36px;'>🍳 Conversational Kitchen Assistant</h1>", unsafe_allow_html=True)

    if choice == "Login":
        st.subheader("Login to Continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                export_users_to_csv()  # Update CSV after login too
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Incorrect Username/Password")

    elif choice == "Sign Up":
        st.subheader("Create New Account")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if not new_username.strip() or not new_password.strip():
                st.warning("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif check_user_exists(new_username):
                st.error("Username already exists.")
            else:
                add_userdata(new_username, hash_password(new_password))
                export_users_to_csv()  # CSV export after signup
                st.success("Account created successfully! Please log in.")
                st.info("Go to Login menu to log in.")

else:
    # Logout button
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # Original Recipe Assistant UI
    st.markdown("<h1 style='font-size:36px;'>🍳 Conversational Kitchen Assistant</h1>", unsafe_allow_html=True)
    st.markdown("Welcome! Enter the ingredients you have or ask a cooking question; I'll suggest the best matching dish and provide step-by-step instructions.")

    user_input = st.text_input("📝 Enter ingredients or a recipe question (e.g., 'chicken, onion, tomato')")

    if st.button("🔍 Find Recipe"):
        if not user_input.strip():
            st.warning("Please type some ingredients or a question.")
        else:
            with st.spinner("Searching for the best match..."):
                result = fetch_recipe(user_input)

            if isinstance(result, str):
                st.error(result)
            else:
                st.markdown("#### Suggested Dish")
                st.markdown(f"**{result.get('title','(unknown)')}**")

                st.markdown("**Ingredients:**")
                st.markdown(result.get("ingredients", "Not available"))

                st.markdown("**Instructions:**")
                steps = result.get("steps", [])
                if steps:
                    md = "\n".join(f"{i}. {step}" for i, step in enumerate(steps, start=1))
                    st.markdown(md)
                else:
                    st.markdown("Step-by-step instructions not available.")
