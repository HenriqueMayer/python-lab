from dotenv import load_dotenv
import os

from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

from pynput import keyboard
import sounddevice as sd
import wave
import whisper  # on Windows using Scoop (https://scoop.sh/) | scoop install ffmpeg
import threading

import numpy as np
import pandas as pd
from queue import Queue

import pyttsx3 # Troquei o gTTS pelo pyttsx3

# Setup-Base-Path:
audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio"))
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Setup: Groq -> OpenAI
load_dotenv(os.path.join(base_dir, ".env"))
api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    temperature=0, 
    groq_api_key=api_key, 
    model_name="gemma2-9b-it"
)

# Setup: Classe principal
class TalkingLLM():
    def __init__(self, whisper_size='small'):
        self.is_recording = False
        self.audio_data = []
        self.samplerate = 44100
        self.channels = 1
        self.dtype = 'int16'

        self.whisper = whisper.load_model(whisper_size)
        self.llm = llm
        self.llm_queue = Queue()
        self.create_agent()

    def start_or_stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.save_and_transcribe()
            self.audio_data = []
        else:
            print('🎙️ Starting recording...')
            self.is_recording = True

    def create_agent(self):
        agent_prompt_prefix = '''
            Your name is Mindcare, an AI assistant specialized in analyzing anxiety-related data. 
            You can answer questions about anxiety attack factors, symptoms, and severity based on the provided dataset. 
            If the user asks general questions about your capabilities, respond in a friendly and informative manner.
            Answer all the questions in Portuguese.
        '''

        df = pd.read_csv(os.path.join(base_dir,'data/anxiety_attack_dataset.csv'))
        self.agent = create_pandas_dataframe_agent(
            self.llm,
            df,
            prefix=agent_prompt_prefix,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            allow_dangerous_code=True,
        )
    
    def save_and_transcribe(self):
        print("🔄 Saving the recording...")
        
        temp_wav_path = os.path.join(audio_dir, "temp.wav")  # Caminho correto na pasta audio
        
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        
        wav_file = wave.open(temp_wav_path, 'wb')  # Usa o caminho correto
        wav_file.setnchannels(self.channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(self.samplerate)
        wav_file.writeframes(np.array(self.audio_data, dtype=self.dtype))
        wav_file.close()

        result = self.whisper.transcribe(temp_wav_path, fp16=True)  # Usa o caminho correto
        print(f'🗣️ Usuário:', result['text'])

        response = self.agent.invoke(result['text'])
        print('🤖 AI:', response['output'])
        self.llm_queue.put(response['output'])

    def convert_and_play(self):
        ttsx3_text = ''
        engine = pyttsx3.init()

        # Escolher voz (voices[0] para F-pt, voices[1] para F-en)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        # Velocidade da fala padrão é 150
        engine.setProperty('rate', 200)

        while True:
            ttsx3_text += self.llm_queue.get()

            if '.' in ttsx3_text or '?' in ttsx3_text or '!' in ttsx3_text:
                print(ttsx3_text)

                # Falar usando pyttsx3
                engine.say(ttsx3_text)
                engine.runAndWait()

                ttsx3_text = ''

    def run(self):
        print('🟢 System Online')
        t1 = threading.Thread(target=self.convert_and_play)
        t1.start()

        def callback(indata, frame_count, time_info, status):  # documentation
            if self.is_recording:
                self.audio_data.extend(indata.copy())

        with sd.InputStream(samplerate=self.samplerate,  # documentation
                            channels=self.channels,
                            dtype=self.dtype,
                            callback=callback):
            def on_activate():
                self.start_or_stop_recording()

            def for_canonical(f):
                return lambda k: f(l.canonical(k))

            hotkey = keyboard.HotKey(
                keyboard.HotKey.parse('<ctrl>'),
                on_activate)
            with keyboard.Listener(
                    on_press=for_canonical(hotkey.press),
                    on_release=for_canonical(hotkey.release)) as l:
                l.join()


# Run:
if __name__ == '__main__':
    talking_llm = TalkingLLM()
    talking_llm.run()