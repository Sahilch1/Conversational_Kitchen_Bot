import streamlit as st
from query_bot import get_recipe_response

st.set_page_config(page_title="Kitchen Assistant Bot")

st.title("👩‍🍳 Conversational Kitchen Assistant")
st.write("Ask me: What can I cook with potatoes and rice?")

user_input = st.text_input("Enter your ingredients or a question")

if st.button("Get Recipe"):
    if user_input:
        with st.spinner("Cooking up something..."):
            answer = get_recipe_response(user_input)
        st.success(answer)
    else:
        st.warning("Please type something first.")
