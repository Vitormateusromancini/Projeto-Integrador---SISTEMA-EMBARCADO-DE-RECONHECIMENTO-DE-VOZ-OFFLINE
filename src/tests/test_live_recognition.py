import json

from src.audio.microphone import AudioInput
from src.recognition.model_manager import ModelManager
from src.recognition.vosk_recognizer import VoskRecognizer
from src.audio.preprocessor import AudioPreprocessor

def run_live_recognition():
    """Executa reconhecimento de fala em tempo real"""
    manager = ModelManager()
    model = manager.load_model()
    recognizer = VoskRecognizer(model)

    audio_input = AudioInput()
    stream = audio_input.start_stream()

    print("Fale algo no microfone (Ctrl+C para parar)")
    final_text = ""

    try:
        with stream:
            while True:
                chunk = audio_input.q.get()
                preprocessor = AudioPreprocessor()
                processed_chunk = preprocessor.process_array(chunk)
                if recognizer.recognizer.AcceptWaveform(processed_chunk):
                    result = json.loads(recognizer.recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        print("→", text)
                        final_text += text + " "
                else:
                    partial = json.loads(recognizer.recognizer.PartialResult()).get("partial", "")
                    if partial:
                        print("…", partial, end="\r")

    except KeyboardInterrupt:
        print("\nReconhecimento parado pelo usuário")
        print("Texto final:", final_text.strip())

if __name__ == "__main__":
    run_live_recognition()