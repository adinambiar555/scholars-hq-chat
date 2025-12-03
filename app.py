import streamlit as st
import google.generativeai as genai
import glob

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Scholars HQ", page_icon="🎓")
st.title("🎓 Scholars HQ: Franchise Support")

# Securely fetch the API key
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Missing API Key. Please configure it in Streamlit Secrets.")

# --- 2. LOAD KNOWLEDGE BASE (LOCAL) ---
def load_knowledge():
    """Reads all .txt files in the repository and combines them."""
    combined_text = ""
    # This grabs every file ending in .txt
    files = glob.glob("*.txt")
    
    if not files:
        return "No specific internal documents found."
        
    for filename in files:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            combined_text += f"\n\n--- DOCUMENT: {filename} ---\n{content}"
            
    return combined_text

# Load the data into memory
knowledge_base_text = load_knowledge()

# --- 3. THE PERSONA ---
# We inject the text directly into the brain
system_instruction = f"""
You are 'Scholars HQ', the central support AI for Scholars Education.
Your goal is to support new franchisees with operational, curricular, and historical inquiries.

CORE KNOWLEDGE:
- Origin: Founded in 1999, based in Toronto, Canada.
- Tone: Professional, encouraging, corporate but accessible.

REFERENCE MATERIAL:
Use the following internal documents to answer questions. If the answer is not here, use general franchising knowledge but mention you are doing so.
{knowledge_base_text}
"""

# --- 4. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "model", 
        "content": "Hello. I have read the internal files. How can I help?"
    })

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle User Input
if prompt := st.chat_input("Ask Scholars HQ..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("model"):
        # We use the standard model now (no complex file tools needed)
        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_instruction)
        
        # Simple chat generation
        chat = model.start_chat(history=[
            {"role": m["role"], "parts": m["content"]} 
            for m in st.session_state.messages[:-1]
        ])
        
        response = chat.send_message(prompt)
        st.markdown(response.text)
    
    st.session_state.messages.append({"role": "model", "content": response.text})