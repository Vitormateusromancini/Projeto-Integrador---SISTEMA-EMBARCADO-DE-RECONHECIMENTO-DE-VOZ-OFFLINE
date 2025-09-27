from .microphone import AudioInput

class AudioRecorder:
    def __init__(self, audio_input: AudioInput):
        self.audio_input = audio_input

    def get_next_chunk(self):
        return self.audio_input.q.get()