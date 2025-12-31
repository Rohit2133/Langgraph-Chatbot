import streamlit as st
from backend import workflow
from langchain_core.messages import HumanMessage

# -----------------------------------
# Page configuration
# -----------------------------------
st.set_page_config(
    page_title="LangGraph Chat Assistant",
    page_icon="🤖",
    layout="centered"
)

# -----------------------------------
# Header
# -----------------------------------
st.markdown(
    """
    <h2 style='text-align:center;'>🤖 LangGraph Chat Assistant</h2>
    <p style='text-align:center; color:gray;'>
        Gemini · LangGraph · Memory Enabled
    </p>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# Sidebar (UI only)
# -----------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    st.caption("Conversation memory is enabled.")
    if st.button("🧹 Clear Chat"):
        st.session_state.message_history = []
        st.rerun()

# -----------------------------------
# Configuration for checkpointing
# -----------------------------------
CONFIG = {'configurable': {'thread_id': 'thread-1'}}

# -----------------------------------
# Message history initialization
# -----------------------------------
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# -----------------------------------
# Display previous messages
# -----------------------------------
for message in st.session_state['message_history']:
    with st.chat_message(
        "user" if message["role"] == "user" else "assistant",
        avatar="🧑" if message["role"] == "user" else "🤖"
    ):
        st.markdown(message["content"])

# -----------------------------------
# Chat input
# -----------------------------------
user_input = st.chat_input("Ask something...")

# -----------------------------------
# Processing user input
# -----------------------------------
if user_input:
    # Show user message
    st.session_state['message_history'].append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # Spinner for better UX
    with st.spinner("Thinking..."):
        response = workflow.invoke(
            {'message': [HumanMessage(content=user_input)]},
            config=CONFIG
        )

    ai_message = response['message'][-1].content

    # Show assistant response
    st.session_state['message_history'].append(
        {"role": "assistant", "content": ai_message}
    )
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(ai_message)
