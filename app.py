import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Scholars Chatbot", page_icon="🎓")
st.title("🎓 Scholars HQ: Franchise Support")

# Securely fetch the API key from Streamlit Secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Missing API Key. Please configure it in Streamlit Secrets.")

# --- 2. THE SCHOLARS PERSONA (System Instructions) ---
# This is the "Brain" of the operation.
system_instruction = """
You are 'Scholars Chatbot', the central support AI for Scholars Education. 
Your goal is to support new franchisees with operational, curricular, and historical inquiries.

CORE KNOWLEDGE:
- Origin: Founded in 1999, based in Toronto, Canada.
- Unique Selling Proposition: Proprietary programs, certified teachers, world-class curriculum standards.
- Tone: Professional, encouraging, corporate but accessible.
- Role: Act as a Head Office employee or Franchise Specialist.

RULES:
1. Answer based strictly on standard franchising best practices and the provided context.
2. If asked about competitor data (Kumon, Oxford, etc.), switch to 'COO Data Research Mode' and provide high-level, objective comparisons.
3. Always emphasize our Canadian roots and long-standing history (since 1999).
"""

# --- 3. INITIALIZE THE MODEL ---
# Using Gemini 1.5 Flash (Fast & Free Tier)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# --- 4. CHAT SESSION MANAGEMENT ---
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a welcoming opening message
    st.session_state.messages.append({
        "role": "model", 
        "content": "Hello. I am Scholars Chatbot. How can I assist you with your franchise operations today?"
    })

# Display previous messages in the chat window
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. THE CHAT INTERFACE ---
# Accept user input
if prompt := st.chat_input("Ask Scholars HQ..."):
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate response
    with st.chat_message("model"):
        # Send the full history + new prompt to the model for context
        chat = model.start_chat(history=[
            {"role": m["role"], "parts": m["content"]} 
            for m in st.session_state.messages[:-1] # Exclude the very last message as we send it below
        ])
        
        response = chat.send_message(prompt)
        st.markdown(response.text)
    
    # Add AI response to history
    st.session_state.messages.append({"role": "model", "content": response.text})