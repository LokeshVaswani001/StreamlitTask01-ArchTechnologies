import streamlit as st
import requests
import json

# Ollama local endpoint
OLLAMA_API_URL = "http://localhost:11434/api/chat"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []  # Chat history

st.set_page_config(page_title="Local LLM Chat", layout="wide")

st.title("💬 Chat with Local LLM (Ollama)")

# Sidebar for reset
with st.sidebar:
    st.header("Options")
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = []
        st.experimental_rerun()


# Custom CSS for chat bubbles
st.markdown("""
<style>
.user-bubble {
    background-color: #1E90FF;
    color: white;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0px;
    max-width: 70%;
    float: right;
    clear: both;
}
.bot-bubble {
    background-color: #E8E8E8;
    color: black;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0px;
    max-width: 70%;
    float: left;
    clear: both;
}
</style>
""", unsafe_allow_html=True)


# Display past messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{msg['content']}</div>", unsafe_allow_html=True)


# User input
if prompt := st.chat_input("Ask something..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"<div class='user-bubble'>{prompt}</div>", unsafe_allow_html=True)

    # Call Ollama API (chat mode)
    try:
        payload = {
            "model": "llama2",  # change if needed
            "messages": st.session_state.messages,
            "stream": True
        }
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True)

        bot_reply = ""
        placeholder = st.empty()

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "message" in data and "content" in data["message"]:
                    bot_reply += data["message"]["content"]
                    placeholder.markdown(
                        f"<div class='bot-bubble'>{bot_reply} ▌</div>",
                        unsafe_allow_html=True
                    )
                if data.get("done", False):
                    break

        placeholder.markdown(
            f"<div class='bot-bubble'>{bot_reply}</div>",
            unsafe_allow_html=True
        )

        # Save LLM reply
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    except Exception as e:
        st.error(f"Error connecting to Ollama: {e}")
