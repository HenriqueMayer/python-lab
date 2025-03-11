from langchain_community.document_loaders import (
WebBaseLoader, 
YoutubeLoader, 
CSVLoader, 
PyPDFLoader, 
TextLoader
)

import re

def site_load(url):
    loader = WebBaseLoader(url)
    documents_list = loader.load()
    documents = '\n\n'.join([documents.page_content for documents in documents_list])
    return documents


def csv_load(csv_path):
    loader = CSVLoader(file_path=csv_path)
    documents_list = loader.load()
    documents = '\n\n'.join([documents.page_content for documents in documents_list])
    return documents

def pdf_load(pdf_path):
    loader = PyPDFLoader(file_path=pdf_path)
    documents_list = loader.load()
    documents = '\n\n'.join([documents.page_content for documents in documents_list])
    return documents

def txt_load(txt_path):
    loader = TextLoader(file_path=txt_path)
    documents_list = loader.load()
    documents = '\n\n'.join([documents.page_content for documents in documents_list])
    return documents

# ==== Youtube ====
def extract_youtube_id(url):
    """Extracts the YouTube video ID from a URL."""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|shorts/|v/|)([a-zA-Z0-9_-]{11})'
    )
    youtube_match = re.search(youtube_regex, url)
    if youtube_match:
        return youtube_match.group(6)
    return None

def youtube_load(url):
    video_id = extract_youtube_id(url)
    if video_id:
        loader = YoutubeLoader(video_id, add_video_info=False, language=['pt', 'en'])
        documents_list = loader.load()
        documents = '\n\n'.join([documents.page_content for documents in documents_list])
        return documents
    else:
        return "Invalid YouTube URL"