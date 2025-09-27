from ..core.config import CONFIG
import sounddevice as sd
import queue
import sys

class AudioInput:
    def __init__(self):
        self.q = queue.Queue()
        self.samplerate = CONFIG["audio"]["samplerate"]
        self.blocksize = CONFIG["audio"]["blocksize"]
        self.device = CONFIG["audio"]["device"]

    def _callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def start_stream(self):
        return sd.RawInputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            dtype="int16",
            channels=1,
            callback=self._callback,
            device=self.device
        )
