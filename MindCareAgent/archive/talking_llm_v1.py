'''
Proposta
1. Usar um atalho para gravar a voz.
2. Transcrever o áudio para texto (em português) -> Whisper.
3. Com o texto pronto inserir numa LLM -> Agente
4. Com a resposta da LLM, utilizar um modelo de tech tool speech (TTS)(API da OpenAI, mas com o Groq).
'''

from dotenv import load_dotenv
import os

from langchain_groq import ChatGroq
import openai

from pynput import keyboard
import sounddevice as sd
import wave
import whisper # on Windows using Scoop (https://scoop.sh/)| scoop install ffmpeg

import io
import threading
import soundfile as sf

import numpy as np
from queue import Queue


# Setup: Groq -> OpenAI
load_dotenv('.env')
api_key = os.getenv("GROQ_API_KEY")

chat = ChatGroq(
    temperature=0, 
    groq_api_key=api_key, 
    model_name="llama3-8b-8192")

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

# Setup: Classe principal
class TalkingLLM():
    def __init__(self, whisper_size='small'):
        self.is_recording=False
        self.audio_data=[]
        self.samplerate=44100
        self.channels=1
        self.dtype='int16'

        self.whisper = whisper.load_model(whisper_size)
        self.llm = chat
        self.llm_queue = Queue()

    def start_or_stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.save_and_transcribe()
            self.audio_data = []
        else:
            print('Starting record')
            self.is_recording = []
            self.is_recording = True

    def create_agent(self):
        pass

    def save_and_transcribe(self):
        print("Saving the recording...")
        if "temp.wav" in os.listdir(): os.remove("temp.wav")
        wav_file = wave.open("test.wav", 'wb')
        wav_file.setnchannels(self.channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(self.samplerate)
        wav_file.writeframes(np.array(self.audio_data, dtype=self.dtype))
        wav_file.close()

        result = self.whisper.transcribe('test.wav', fp16=False)
        print(f'Usuário:', result['text'])

        response = self.llm.invoke(result['text'])
        print('AI:', response)
        self.llm_queue.put(response.content)

    def convert_and_play(self):
        tts_text = ''
        while True:
            tts_text+= self.llm_queue.get()

            if '.' in tts_text or '?' in tts_text or '!' in tts_text:
                print(tts_text)

                spoken_response = client.audio.speech.create(model='tts-1',
                voice='alloy',
                response_format='opus', # highly efficient compressed audio
                input=tts_text
                )

                # store temporarily
                buffer = io.BytesIO() # Salvando um arquivo temporariamente
                for chunk in spoken_response.iter_bytes(chunk_size=4096):
                    buffer.write(chunk)
                buffer.seek(0) # Reset no buffer

                with sf.SoundFile(buffer, 'r') as sound_file: # Carregar o buffer, ler e executar o áudio
                    data = sound_file.read(dtype='int16')
                    sd.play(data, sound_file.samplerate)
                    sd.wait()
                tts_text = ''

    def run(self):
        print('On')
        t1 = threading.Thread(target=self.convert_and_play)
        t1.start()

        def callback(indata,frame_count,time_info,status): # from documentation
            if self.is_recording:
                self.audio_data.extend(indata.copy())

        with sd.InputStream(samplerate=self.samplerate, # from documentation
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