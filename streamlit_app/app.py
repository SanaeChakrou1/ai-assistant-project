import streamlit as st
import requests
import uuid
from datetime import datetime
import time
import base64

# ---------------------------
# Configuration
# ---------------------------
WEBHOOK_URL = ""
BEARER_TOKEN = ""

# ---------------------------
# Session state
# ---------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "connection_status" not in st.session_state:
    st.session_state.connection_status = "Connected"
if "response_time" not in st.session_state:
    st.session_state.response_time = 0
if "show_upload" not in st.session_state:
    st.session_state.show_upload = False
if "processing" not in st.session_state:
    st.session_state.processing = False

# ---------------------------
# Send message to webhook
# ---------------------------
def send_message_to_webhook(message, file_content=None):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "chatInput": message,
        "sessionId": st.session_state.session_id,
        "timestamp": datetime.now().isoformat()
    }
    if file_content:
        payload["fileContent"] = file_content  # Base64 string of image
    start_time = time.time()
    try:
        response = requests.post(WEBHOOK_URL, headers=headers, json=payload, timeout=30)
        st.session_state.response_time = round((time.time() - start_time) * 1000, 2)
        if response.status_code == 200:
            return response.json().get("output", "No response received")
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return f"⚠️ {str(e)}"

# ---------------------------
# UI Styling
# ---------------------------
st.markdown("""
<style>
    /* Global theme */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    .stApp { 
        background: linear-gradient(135deg, #f9fafc, #edf2f7); 
        color: #1a202c;
    }

    /* Header */
    .app-header { 
        background: #2b6cb0; 
        color: white; 
        padding: 1rem 2rem; 
        margin-bottom: 1rem; 
        border-radius: 8px;
        display: flex; 
        justify-content: space-between;
        align-items: center;
    }
    .app-title { font-size: 1.5rem; font-weight: 600; }
    .status-indicator { width: 8px; height: 8px; background: #48bb78; border-radius: 50%; }

    /* Chat container */
    .chat-container { max-width: 800px; margin: auto; padding: 1rem; }
    .chat-bubble {
        max-width: 70%;
        padding: 0.8rem 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        line-height: 1.4;
        font-size: 0.95rem;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
        word-wrap: break-word;
    }
    .chat-bubble.user {
        background: #2b6cb0;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 0.3rem;
    }
    .chat-bubble.assistant {
        background: #e2e8f0;
        color: #1a202c;
        margin-right: auto;
        border-bottom-left-radius: 0.3rem;
    }

    /* Style the chat input container to accommodate embedded button */
    [data-testid="stChatInput"] {
        position: relative !important;
    }
    
    [data-testid="stChatInput"] > div {
        position: relative !important;
    }
    
    /* Add padding to chat input for the button */
    [data-testid="stChatInput"] input {
        padding-right: 45px !important;
    }
    
    /* Custom button container positioned over chat input */
    .chat-button-overlay {
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 1000;
    }
    
    .chat-button-overlay .stButton > button {
        background-color: #6b7280 !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        font-size: 14px !important;
        padding: 0 !important;
        min-height: 32px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }
    
    .chat-button-overlay .stButton > button:hover {
        background-color: #4b5563 !important;
        transform: scale(1.1) !important;
    }

    /* Footer */
    .app-footer {
        margin-top: 2rem;
        margin-bottom: 100px;
        padding: 1rem;
        text-align: center;
        font-size: 0.85rem;
        color: #718096;
        border-top: 1px solid #ddd;
    }

    /* Thinking dots */
    .thinking-dots {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 5px;
        margin: 1rem 0;
    }
    .thinking-dots span {
        width: 10px;
        height: 10px;
        background-color: #2b2b2b;
        border-radius: 50%;
        display: inline-block;
        animation: bounce 0.6s infinite alternate;
    }
    .thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
    .thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0); }
    }

    #MainMenu, footer, header {visibility: hidden;}
    
    /* Hide default streamlit chat input styling conflicts */
    .stChatInput > div {
        border-radius: 25px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Header
# ---------------------------
st.markdown(f"""
<div class="app-header">
    <div class="app-title">AI Assistant</div>
    <span class="status-indicator"></span>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# Chat container
# ---------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #718096;">
        <h3>Welcome to AI Assistant</h3>
        <p>Start a conversation by typing your message below or uploading an image.</p>
    </div>
    """, unsafe_allow_html=True)

# Render chat bubbles
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "assistant"
    st.markdown(
        f'<div class="chat-bubble {role_class}">{msg["content"]}</div>', 
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Processing indicator (bouncing dots)
# ---------------------------
if st.session_state.processing:
    st.markdown(
        '<div class="thinking-dots"><span></span><span></span><span></span></div>', 
        unsafe_allow_html=True
    )

# ---------------------------
# File uploader (above chat input)
# ---------------------------
uploaded_file = None
file_content = None  # <-- Fix: initialize to avoid NameError

if st.session_state.show_upload:
    with st.container():
        uploaded_file = st.file_uploader("Upload an image", type=["jpg","png"], key="file_uploader")

# ---------------------------
# Chat input with embedded plus button
# ---------------------------
input_container = st.container()

with input_container:
    col_main = st.columns(1)[0]
    
    with col_main:
        user_input = st.chat_input("Type your message...")
    
    st.markdown("""<div class="chat-button-overlay">""", unsafe_allow_html=True)
    
    if st.button("➕", key="plus_btn", help="Upload file", type="secondary"):
        st.session_state.show_upload = not st.session_state.show_upload
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Handle file upload immediately
# ---------------------------
if uploaded_file and not st.session_state.processing:
    bytes_data = uploaded_file.read()
    file_content = base64.b64encode(bytes_data).decode("utf-8")
    st.session_state.messages.append({
        "role": "user", 
        "content": f"<img src='data:{uploaded_file.type};base64,{file_content}' width='200'/>"
    })
    st.session_state.processing = True
    st.session_state.show_upload = False
    st.rerun()

# ---------------------------
# Handle chat input
# ---------------------------
if user_input and not st.session_state.processing:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.processing = True
    st.rerun()

# ---------------------------
# Process AI response if needed
# ---------------------------
if st.session_state.processing:
    last_message = st.session_state.messages[-1] if st.session_state.messages else None
    if last_message and last_message["role"] == "user":
        if last_message["content"].startswith("<img"):
            ai_response = send_message_to_webhook("User sent an image", file_content)
        else:
            ai_response = send_message_to_webhook(last_message["content"])
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.session_state.processing = False
        st.rerun()

# ---------------------------
# Sidebar info
# ---------------------------
with st.sidebar:
    st.header("Session Info")
    st.text(f"Session: {st.session_state.session_id[:8]}...")
    st.text(f"Messages: {len(st.session_state.messages)}")
    if st.session_state.response_time > 0:
        st.text(f"Response: {st.session_state.response_time}ms")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.processing = False
        st.rerun()
    if st.button("New Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.processing = False
        st.rerun()

# ---------------------------
# Footer
# ---------------------------
st.markdown("""
<div class="app-footer">
    Powered by <strong>Sanae chakrou</strong> | AI Assistant © 2025
</div>
""", unsafe_allow_html=True)
