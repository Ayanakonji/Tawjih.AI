import openai
import streamlit as st
#initializing the history of the chat
st.title("Chatbot AI")
openai.api_key = st.secrets["OPENAI_API_KEY"]
if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-3.5-turbo"
if "messages" not in st.session_state:
    st.session_state.messages = []
#function to generate a response from the AI model
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
prompt = st.chat_input("Ask me anything")
if prompt:
    #Display the user message in the chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Append the user message to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        # Display a placeholder for the AI response
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages = [{"role":m["role"], "content":m["content"]} 
            for m in st.session_state.messages],
            stream=True,
            temperature=0.5,
        ):
            # Append the AI response to the full response
            full_response += response.choices[0].delta.get("content", "")
            # Update the placeholder with the current response
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Append the AI response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
