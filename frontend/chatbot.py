import streamlit as st
import requests
import json
import time

# Configure page
st.set_page_config(page_title="IT Support RAG Bot", layout="wide")
st.title("IT Support Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_llm_response(prompt):
    """Get response from local LLM server"""
    url = "http://52.201.13.40:8000/ask"
    data = {
        "question": prompt
    }
    try:
        response = requests.post(url, json=data)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"answer": f"Error: {str(e)}", "relevant_chunks": []}

def truncate_chunk(chunk, max_length=100):
    """Truncate chunk text with ellipsis"""
    return chunk[:max_length] + "..." if len(chunk) > max_length else chunk

# Custom CSS for chunk preview
st.markdown("""
<style>
.chunk-preview {
    background-color: #f0f2f6;
    border-radius: 4px;
    padding: 8px;
    margin-top: 8px;
    font-size: 0.8em;
    color: #666;
}
.chunk-header {
    font-weight: bold;
    color: #444;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Display chunk previews for assistant messages
        if message["role"] == "assistant" and "chunks" in message:
            for i, chunk in enumerate(message["chunks"], 1):
                st.markdown(f"""
                <div class="chunk-preview">
                    <div class="chunk-header">📚 Retrieved Context {i}:</div>
                    {truncate_chunk(chunk)}
                </div>
                """, unsafe_allow_html=True)

# Accept user input
if prompt := st.chat_input("How can I help you with IT support?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Get response from LLM
        response = get_llm_response(prompt)
        
        # Stream the response word by word
        full_response = ""
        for word in response["answer"].split():
            full_response += word + " "
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.05)
        
        # Final response without cursor
        message_placeholder.markdown(full_response)
        
        # Display chunk previews
        for i, chunk in enumerate(response["relevant_chunks"], 1):
            st.markdown(f"""
            <div class="chunk-preview">
                <div class="chunk-header">📚 Retrieved Context {i}:</div>
                {truncate_chunk(chunk)}
            </div>
            """, unsafe_allow_html=True)
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "chunks": response["relevant_chunks"]
        })
