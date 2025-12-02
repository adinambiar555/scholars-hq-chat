import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Scholars HQ", page_icon="🎓", layout="wide")
st.title("🎓 Scholars HQ: Franchise Support")

# Securely fetch the API key
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Missing API Key. Please configure it in Streamlit Secrets.")

# --- 2. THE SCHOLARS PERSONA ---
system_instruction = """
You are 'Scholars HQ', the central support AI for Scholars Education. 
Your goal is to support new franchisees with operational, curricular, and historical inquiries.

CORE KNOWLEDGE:
- Origin: Founded in 1999, based in Toronto, Canada.
- Product: Proprietary programs, certified teachers, world-class curriculum standards.
- Tone: Professional, encouraging, corporate but accessible.

RULES:
1. If a document is uploaded, PRIORITIZE that document's content for your answers.
2. If the answer is not in the document or your general knowledge, advise contacting Head Office.
3. Always maintain the professional 'Scholars HQ' persona.
"""

# --- 3. SIDEBAR: THE DIGITAL BINDER ---
with st.sidebar:
    st.header("📂 Digital Binder")
    st.write("Upload a manual, lease, or guide here for analysis.")
    uploaded_file = st.file_uploader("Choose a PDF or Text file", type=["pdf", "txt"])
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.pop("file_cache", None) # Clear memory of the file
        st.rerun()

# --- 4. PROCESSING THE FILE ---
def upload_to_gemini(file):
    """Uploads the file to Google's server and returns the reference."""
    with st.spinner("Scholars HQ is reading the document..."):
        # Create a temporary file on the server so we can upload it
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp:
            tmp.write(file.getvalue())
            tmp_path = tmp.name

        # Upload to Gemini
        remote_file = genai.upload_file(tmp_path, mime_type="application/pdf" if file.name.endswith(".pdf") else "text/plain")
        
        # Clean up the local temp file
        os.remove(tmp_path)
        return remote_file

# --- 5. INITIALIZE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "model", 
        "content": "Hello. I am Scholars HQ. Upload a document in the sidebar to begin, or just ask me a general question."
    })

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. THE CHAT INTERFACE ---
if prompt := st.chat_input("Ask Scholars HQ..."):
    
    # 1. Show User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generate Response
    with st.chat_message("model"):
        try:
            # Use the explicit stable release version
            model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_instruction)
            
            # Logic: If a file is uploaded, we include it in the prompt.
            # If we already uploaded it this session, we use the cached version to save time.
            
            content_to_send = [prompt]
            
            if uploaded_file:
                # Check if we've already uploaded this specific file to Google
                if "file_cache" not in st.session_state or st.session_state["file_cache"]["name"] != uploaded_file.name:
                    remote_file = upload_to_gemini(uploaded_file)
                    st.session_state["file_cache"] = {"name": uploaded_file.name, "data": remote_file}
                
                # Add the file to the message
                content_to_send.insert(0, st.session_state["file_cache"]["data"])
            
            # We use generate_content for single-turn with file, or chat history for pure text
            # For simplicity in this version, we are doing a "smart generate" using chat history as context string if needed,
            # but here we prioritize the FILE + PROMPT current interaction.
            
            response = model.generate_content(content_to_send)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "model", "content": response.text})

        except Exception as e:
            st.error(f"An error occurred: {e}")