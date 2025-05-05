import streamlit as st
from openai import OpenAI

# Load API key securely from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Tawjih.AI", layout="centered")
st.title("🎓 Tawjih.AI – Smart Academic Advisor")

# Initial system prompt
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are Tawjih.AI, an academic advisor that helps Moroccan post-baccalaureate students "
                "choose the best academic path. Ask the user questions about their favorite subjects, "
                "baccalaureate specialization, average grades, and career goals. Then give personalized advice."
            )
        }
    ]

# Display previous chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input from user
user_input = st.chat_input("Tell me about your studies or ask for advice")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=st.session_state.messages,
            temperature=0.7,
        )

    reply = response.choices[0].message.content
    st.chat_message("assistant").write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
