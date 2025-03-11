# Nereus Chatbot
Nereus is a Python-based chatbot assistant inspired by the ancient Greek sea god known for wisdom and honesty. Designed with a friendly and wise persona, Nereus leverages language models to process and respond to queries based on various document types.
# Overview
Nereus uses Streamlit for a simple web interface and LangChain for memory and prompt management. The chatbot is powered by an LLM (via Ollama's gemma2:2b model) and can load and extract information from multiple file formats:

Web pages
YouTube videos
PDF documents
CSV files
TXT files
The personality and behavior of Nereus are defined within the system prompt. He is instructed to remain friendly, concise, and helpful while using the provided documents to answer user queries.

# Step by Step -> LocalHost LLM
Start Ollama

Download the model:
$ ollama pull <model name>

Start the model:
$ ollama run <model name>

Check the host port:
$ ollama serve
-> Error: listen tcp xxx.x.x.x:YYYYY:[...]
The code is YYYYY

Python code:
from langchain_ollama import ChatOllama
llm = ChatOllama(model='<model name>, base_url='http://localhost:<YYYY>')

-> Check the model name: $ ollama list

# Structure
Nereus_Chatbot/
├── app.py          # Main application file with the Streamlit interface
├── utils.py        # Utility functions for document loading (websites, YouTube, PDFs, CSVs, TXT)
└── icon/
    └── nereus.ico  # Icon file for Nereus used in the app interface

- app.py: Sets up the chatbot interface, manages conversation memory, handles file inputs, and integrates with the language model.
- utils.py: Contains helper functions to load and process different document types, including a custom YouTube loader.

# Configuration
LLM Setup: The chatbot uses Ollama’s gemma2:2b model. Adjust the model configuration in app.py if needed.
Prompt Customization: The system prompt within app.py defines Nereus’s persona and behavior. Modify it as necessary to suit your application.