import streamlit as st
from backend import workflow
from langchain_core.messages import HumanMessage , AIMessage # type: ignore
import uuid


# Utility function to generate unique IDs and reset chat 
def generate_unique_id():
    thread_id = uuid.uuid4()
    return str(thread_id)

def reset_chat():
    thread_id = generate_unique_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)
    
def load_conversation(thread_id):
    state = workflow.get_state(
        config={'configurable': {'thread_id': thread_id}}
    )
    if not state or "messages" not in state.values:
        return []

    return state.values["messages"]

def get_conversation_title(thread_id, max_len=28):
    messages = load_conversation(thread_id)

    for msg in messages:
        if isinstance(msg, HumanMessage):
            title = msg.content.strip()
            return title[:max_len] + "…" if len(title) > max_len else title

    return "New Conversation"
# -----------------------------------
# Message history initialization
# -----------------------------------
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_unique_id()
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = []

add_thread(st.session_state['thread_id'])
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

# # -----------------------------------
# # Sidebar (UI only)
# # -----------------------------------
# with st.sidebar:
#     st.markdown("### ⚙️ Controls")
#     st.caption("Conversation memory is enabled.")
#     if st.button("Clear Chat"):
#         st.session_state.message_history = []
#         st.rerun()
#     if st.button("New Chat"):
#         reset_chat()
#     st.header("My Conversations :")
#     for thread_id in st.session_state['chat_thread'][::-1]:
#         if st.button(thread_id):
#             st.session_state['thread_id'] = thread_id
#             messages = load_conversation(thread_id)
#             temp_history = []
#             for msg in messages:
#                 if isinstance(msg, HumanMessage):
#                     role = 'user'
#                 else:
#                     role = 'assistant'
#                 temp_history.append({"role": role, "content": msg.content})
#             st.session_state['message_history'] = temp_history

# -----------------------------------
# Sidebar (UI only – active conversation names)
# -----------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.caption("🧠 Conversation memory is enabled")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.message_history = []
            st.rerun()

    with col2:
        if st.button("➕ New Chat", use_container_width=True):
            reset_chat()

    st.divider()

    st.markdown("## 💬 My Conversations")
    st.caption("Click to resume")

    with st.container(height=320):
        for thread_id in st.session_state['chat_thread'][::-1]:

            title = get_conversation_title(thread_id)

            is_active = thread_id == st.session_state['thread_id']
            prefix = "🟢 " if is_active else "🟡 "

            if st.button(
                prefix + title,
                key=thread_id,
                use_container_width=True
            ):
                st.session_state['thread_id'] = thread_id

                messages = load_conversation(thread_id)
                temp_history = []

                for msg in messages:
                    role = "user" if isinstance(msg, HumanMessage) else "assistant"
                    temp_history.append(
                        {"role": role, "content": msg.content}
                    )

                st.session_state['message_history'] = temp_history


# -----------------------------------
# Configuration for checkpointing
# -----------------------------------
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}


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

    # Show assistant response
   
        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            # ai_message = st.write_stream(
            #     message_chunk.content for message_chunk , metadata in workflow.stream(
            #         {'message': [HumanMessage(content=user_input)]},
            #         config=CONFIG,
            #         stream_mode = 'messages'
            #     )
            # )
            ai_text = ""
            for message_chunk, metadata in workflow.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages"
            ):
                # Only stream AI messages
                if isinstance(message_chunk, AIMessage):
                    ai_text += message_chunk.content
                    placeholder.markdown(ai_text + "▌")

            placeholder.markdown(ai_text)
            st.session_state['message_history'].append(
                {"role": "assistant", "content": ai_text}
                )

