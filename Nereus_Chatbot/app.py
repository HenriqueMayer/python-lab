import streamlit as st

from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate

import base64
import time
import bs4
import tempfile
from pathlib import Path

from utils import *

# ==== Setup: Icon ====
file_ico_nereus = Path(__file__).parent / 'icon/nereus.ico'
with open(file_ico_nereus, 'rb') as f:
    base64_ico = base64.b64encode(f.read()).decode("utf-8")

icon_html = f'<img src="data:image/x-icon;base64,{base64_ico}" width="100">' # Create HTML with Base64 image

# ==== Setup: Valid files ====
valid_files = ['Sites', 'YouTube', 'PDF', 'CSV', 'TXT']

# ==== Setup: Langchain-Memory ====
memory = ConversationBufferMemory()

# ==== Setup: Files ====
def file_loader(file_selected, file):

    if file_selected == 'Sites':
        documents = site_load(file)

    if file_selected == 'YouTube':
        documents = youtube_load(file)

    if file_selected == 'PDF':
        with tempfile.NamedTemporaryFile(suffix='.pdf',delete=False) as temp:
            temp.write(file.read())
            temp_path = temp.name
        documents = pdf_load(temp_path)

    if file_selected == 'CSV':
        with tempfile.NamedTemporaryFile(suffix='.csv',delete=False) as temp:
            temp.write(file.read())
            temp_path = temp.name
        documents = csv_load(temp_path)

    if file_selected == 'TXT':
        with tempfile.NamedTemporaryFile(suffix='.txt',delete=False) as temp:
            temp.write(file.read())
            temp_path = temp.name
        documents = txt_load(temp_path)

    return documents

# ==== Setup: LLM ====
def model(file_selected, file):
    documents = file_loader(file_selected, file)

    system_message = ''' 
        You are Nereus, a friendly and wise assistant.

        **Persona:**

        * **Name:** Nereus
        * **Origin:** Ancient Greek mythology, "Old Man of the Sea"
        * **Attributes:** Wisdom, honesty, virtue, prophetic abilities, shape-shifting.
        * **Background:** Son of Pontus and Gaia, husband of Doris, father of the Nereids and Nerites. Renowned for guiding heroes like Heracles.

        **Function:**

        * Use the information provided in the following documents to answer user queries: document type {}; document information {}.
        * If the response contains a "$", replace it with "s".
        * If the response indicates an issue with Javascript or cookies (e.g., "Just a moment... enable Javascript and cookies to continue"), instruct the user to reload the chat.

        **Behavior:**

        * Maintain a friendly tone.
        * Do not talk about your persona. Just answer the question briefly and precisely.
    '''.format(file_selected, documents)

    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'), # If there is a chat history
        ('user', '{input}')
    ])

    llm = Ollama(model="gemma2:2b") # model: gemma2:2b
    chain = template | llm

    st.session_state['chain'] = chain

# ==== Setup: Chat Page ====
def chat_page():
    # Create an empty placeholder
    st.header('💡 Welcome! I am Nereus!')
    icon_placeholder = st.empty()

    # Place the markdown with the icon
    icon_placeholder.markdown(f'''
    <div style="text-align: left;">\n
    - From Greek, Νηρευς
    - A chatbot inspired by the ancient Greek sea god renowned for his 
    wisdom and honesty
    - I can help navigate and comprehend various digital content formats, 
    including PDFs, websites, YouTube videos, CSV, and TXT files
    </div>
    <div style="text-align: center;">
        <img src="data:image/x-icon;base64,{base64_ico}" width="150">
    </div>
    ''', unsafe_allow_html=True)

    st.divider()

    # ==== Session State: It's like a memory, every message is stored here
    stored_memory = st.session_state.get('stored_memory', memory)
    chain = st.session_state.get('chain')
    
    if chain is None:
        st.error('Select an option')
        st.stop()


    for message in stored_memory.buffer_as_messages: # The messages are stored
        chat = st.chat_message(message.type) # Who sent the message? -> .type
        chat.markdown(message.content)


    user_input = st.chat_input('Speak with Nereus...') # Receive message
    if user_input:
        chat = st.chat_message('human')
        chat.markdown(user_input)

        chat = st.chat_message('ai')
        llm_answer = chat.write_stream(chain.stream({ # stream is a method to define how messages are sent
            'input': user_input, 
            'chat_history': stored_memory.buffer_as_messages
            })) 

        stored_memory.chat_memory.add_user_message(user_input)
        stored_memory.chat_memory.add_ai_message(llm_answer)

        st.session_state['stored_memory'] = stored_memory

def sidebar():
    tabs = st.tabs(['File uploader'])
    with tabs[0]:
        file_type = st.selectbox('Select the file', valid_files)

        if file_type == 'Sites':
            file = st.text_input('Paste the URL...')

        if file_type == 'YouTube':
            file = st.text_input('Paste the URL...')

        if file_type == 'PDF':
            file = st.file_uploader('Upload the .pdf file', type=['.pdf'])

        if file_type == 'CSV':
            file = st.file_uploader('Upload the .csv file', type=['.csv'])

        if file_type == 'TXT':
            file = st.file_uploader('Upload the .txt file', type=['.txt'])

    if st.button('Start Nereus...'):
        model(file_selected=file_type, file=file)

    if st.button('Clear history...', use_container_width=True):
        st.session_state['stored_memory'] = memory


# ==== Run ====
def main():
    with st.sidebar:
        sidebar()
    chat_page()

if __name__ == '__main__':
    main()