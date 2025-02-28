import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

for index, voice in enumerate(voices):
    print(f"ID: {index} - Nome: {voice.name} - Idioma: {voice.languages}")