import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Scholars HQ", page_icon="🎓")
st.title("🎓 Scholars HQ: Franchise Support")

# API Key
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Missing API Key.")

# --- 2. THE KNOWLEDGE BASE (PASTE YOUR IDs HERE) ---
# Replace the brackets below with the list you just copied from your terminal
KNOWLEDGE_BASE_FILES = [
  'files/dzr9x8j2oxet', # Source: web_scholarsed.com_about-us_.txt
]

# --- 3. THE PERSONA ---
system_instruction = """
You are 'Scholars HQ', the central support AI for Scholars Education.
You have access to a library of internal documents and website content (attached to this chat). 
ALWAYS search these documents first before answering.

CORE KNOWLEDGE:
- Origin: Founded in 1999, based in Toronto, Canada.
- Tone: Professional, encouraging, corporate but accessible.
"""

# --- 4. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "model", 
        "content": "Hello. I am connected to the Scholars Central Library. How can I help?"
    })

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Scholars HQ..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("model"):
        # Explicitly use Gemini 1.5 Flash (supports file references best)
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)
        
        # We attach the files to the prompt so the model can "see" them
        request_content = [prompt]
        
        # Loop through your IDs and attach them
        for file_name in KNOWLEDGE_BASE_FILES:
             # This grabs the file from Google's cloud without re-uploading
             file_ref = genai.get_file(file_name)
             request_content.append(file_ref)

        response = model.generate_content(request_content)
        st.markdown(response.text)
    
    st.session_state.messages.append({"role": "model", "content": response.text})