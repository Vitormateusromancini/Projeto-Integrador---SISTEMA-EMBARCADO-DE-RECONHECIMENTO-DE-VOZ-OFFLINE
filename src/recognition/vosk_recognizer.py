from vosk import KaldiRecognizer
import json
from src.core.config import CONFIG

class VoskRecognizer():
    def __init__(self, model):
        self.model = model
        self.sample_rate = CONFIG["audio"]["samplerate"]
        self.reset_session()
        print(f"VoskRecognizer inicializado em {self.sample_rate} Hz.")

    def reset_session(self):
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)

    def recognize_chunk(self, chunk: bytes) -> str:
        if self.recognizer.AcceptWaveform(chunk):
            result = json.loads(self.recognizer.Result())
            return result.get("text", "")
        else:
            partial = json.loads(self.recognizer.PartialResult())
            return partial.get("partial", "")

    def recognize_stream(self, audio_source) -> str:
        final_text = ""
        for chunk in audio_source:  # precisa ser iterável
            if self.recognizer.AcceptWaveform(chunk):
                final_text += json.loads(self.recognizer.Result()).get("text", "") + " "
        final_text += json.loads(self.recognizer.FinalResult()).get("text", "")
        return final_text.strip()
