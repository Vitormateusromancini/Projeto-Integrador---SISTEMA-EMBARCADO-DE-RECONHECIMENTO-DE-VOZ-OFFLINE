"""







Todo este código foi gerado pelo GPT, então ira sofrer mudanças






src/audio/preprocessor.py

Preprocessor de áudio completo para o pipeline:
AudioInput -> Preprocessor -> Recognizer

Responsabilidades:
- Converter bytes <-> numpy arrays
- Garantir PCM16 mono na sample_rate do sistema (config)
- Normalização (peak / RMS)
- Redução de ruído (usa noisereduce se disponível)
- Filtro passa-faixa (bandpass)
- VAD (webrtcvad se disponível, caso contrário energy-based)
- Trim de silêncio / segmentação
- AGC (ganho automático simples)
- Funções utilitárias para processamento de chunks/streams

Integra com core.config.CONFIG (usa samplerate/defaults)
"""

from typing import Optional, List
import numpy as np

# imports opcionais
try:
    import noisereduce as nr
    _HAS_NOISEREDUCE = True
except Exception:
    _HAS_NOISEREDUCE = False

try:
    import webrtcvad
    _HAS_WEBRTCVAD = True
except Exception:
    _HAS_WEBRTCVAD = False

try:
    # prefer scipy for filtering/resampling
    from scipy.signal import butter, lfilter, resample
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False

# Carregar config se existir
try:
    from src.core.config import CONFIG
    _CFG = CONFIG
except Exception:
    # fallback local defaults
    _CFG = {
        "audio": {
            "samplerate": 16000,
            "blocksize": 8000,
            "device": None
        }
    }


# ---------- helpers numpy/bytes conversions ----------
def bytes_to_int16_array(b: bytes) -> np.ndarray:
    """Converte bytes (PCM16) para numpy int16 mono array."""
    arr = np.frombuffer(b, dtype=np.int16)
    return arr


def int16_array_to_bytes(arr: np.ndarray) -> bytes:
    """Converte numpy int16 array para bytes PCM16."""
    return arr.astype(np.int16).tobytes()


def ensure_mono(arr: np.ndarray) -> np.ndarray:
    """Se for estéreo (2D ou interleaved), converte para mono por média."""
    if arr.ndim == 1:
        return arr
    # caso arr seja shape (n_frames, n_channels)
    if arr.ndim == 2:
        return arr.mean(axis=1).astype(arr.dtype)
    # caso improbable: interleaved flat array: assume stereo interleaved
    if arr.ndim == 1 and arr.size % 2 == 0:
        arr2 = arr.reshape(-1, 2)
        return arr2.mean(axis=1).astype(arr.dtype)
    return arr


# ---------- filters & resampling ----------
def butter_bandpass(lowcut, highcut, fs, order=5):
    if not _HAS_SCIPY:
        raise RuntimeError("scipy is required for bandpass filter")
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def apply_bandpass(data: np.ndarray, lowcut: float, highcut: float, fs: int, order: int = 5) -> np.ndarray:
    if not _HAS_SCIPY:
        # fallback: no filtering
        return data
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)


def resample_array(data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr == target_sr:
        return data
    if _HAS_SCIPY:
        # scipy.signal.resample uses FFT-based resampling (better than naive)
        n_samples = int(len(data) * float(target_sr) / orig_sr)
        res = resample(data, n_samples)
        return np.asarray(res, dtype=data.dtype)
    else:
        # fallback naive (nearest neighbour) -> convert indexes
        indices = (np.arange(0, len(data)) * (target_sr / orig_sr)).astype(int)
        indices = np.clip(indices, 0, len(data)-1)
        return data[indices]


# ---------- normalization & AGC ----------
def normalize_peak(arr: np.ndarray, target_peak: float = 0.95) -> np.ndarray:
    """Peak normalization: scale so that max absolute value ~= target_peak (0..1)"""
    arr_float = arr.astype(np.float32)
    max_val = np.max(np.abs(arr_float))
    if max_val == 0:
        return arr
    scale = (target_peak * 32767.0) / max_val
    scaled = (arr_float * scale).astype(np.int16)
    return scaled


def normalize_rms(arr: np.ndarray, target_rms: float = 0.1) -> np.ndarray:
    """RMS normalization (target_rms in 0..1)"""
    arr_float = arr.astype(np.float32) / 32768.0
    rms = np.sqrt(np.mean(arr_float ** 2))
    if rms == 0:
        return arr
    scale = target_rms / rms
    scaled = np.clip(arr_float * scale, -1.0, 1.0)
    return (scaled * 32767.0).astype(np.int16)


def simple_agc(arr: np.ndarray, target_level=0.1):
    """Auto gain control: combination of RMS normalization and soft limiting."""
    return normalize_rms(arr, target_rms=target_level)


# ---------- noise reduction ----------
def reduce_noise_array(arr: np.ndarray, sr: int) -> np.ndarray:
    """Applies noise reduction. Uses noisereduce if available; otherwise returns arr."""
    if not _HAS_NOISEREDUCE:
        return arr
    # noisereduce expects float64 or float32 in -1..1
    arr_f = arr.astype(np.float32) / 32768.0
    try:
        reduced = nr.reduce_noise(y=arr_f, sr=sr)
        return (np.clip(reduced, -1.0, 1.0) * 32767.0).astype(np.int16)
    except Exception:
        return arr


# ---------- VAD (webrtcvad or energy) ----------
class VAD:
    """Wrapper VAD: prefer webrtcvad, fallback to energy-based VAD."""
    def __init__(self, sample_rate: int = 16000, mode: int = 1, energy_threshold: float = 500.0):
        self.sample_rate = sample_rate
        self.energy_threshold = energy_threshold
        if _HAS_WEBRTCVAD:
            self.vad = webrtcvad.Vad()
            # mode 0-3 (0 less aggressive, 3 most aggressive)
            self.vad.set_mode(mode)
        else:
            self.vad = None

    def is_speech(self, chunk_int16: np.ndarray) -> bool:
        """
        chunk_int16: numpy int16 array containing ~10/20/30ms of audio at sample_rate.
        If webrtcvad unavailable, fallback to simple energy threshold.
        """
        if self.vad is not None:
            # webrtcvad expects 16-bit PCM bytes and frame length 10/20/30ms
            pcm_bytes = chunk_int16.tobytes()
            try:
                return self.vad.is_speech(pcm_bytes, sample_rate=self.sample_rate)
            except Exception:
                # fallback to energy
                pass
        # fallback: energy-based
        return np.abs(chunk_int16).mean() > self.energy_threshold


# ---------- trimming / segmentation ----------
def trim_silence(arr: np.ndarray, sr: int, top_db: float = 20.0) -> np.ndarray:
    """
    Very simple silence trimming: remove leading/trailing samples where RMS (in dB) below threshold.
    This is not as robust as librosa.effects.trim but avoids dependency.
    """
    arr_f = arr.astype(np.float32) / 32768.0
    frame_len = int(0.02 * sr)  # 20 ms frames
    hop = frame_len
    rms_frames = []
    for i in range(0, len(arr_f), hop):
        frame = arr_f[i:i+frame_len]
        if frame.size == 0:
            rms_frames.append(0.0)
        else:
            rms_frames.append(np.sqrt(np.mean(frame**2) + 1e-12))
    rms_db = 20 * np.log10(np.maximum(rms_frames, 1e-12))
    # frames above -top_db
    mask = rms_db > -top_db
    if not any(mask):
        return np.array([], dtype=arr.dtype)
    first = next(i for i, v in enumerate(mask) if v)
    last = len(mask) - 1 - next(i for i, v in enumerate(reversed(mask)) if v)
    start_sample = first * hop
    end_sample = min(len(arr_f), (last+1)*hop)
    return (arr_f[start_sample:end_sample] * 32767.0).astype(np.int16)


# ---------- framing utilities ----------
def frame_generator(frame_duration_ms: int, audio: np.ndarray, sample_rate: int) -> List[np.ndarray]:
    """Divide audio em frames (int16 arrays) de frame_duration_ms."""
    frame_length = int(sample_rate * (frame_duration_ms / 1000.0))
    frames = []
    for start in range(0, len(audio), frame_length):
        frames.append(audio[start:start+frame_length])
    return frames


# ---------- Main Preprocessor class ----------
class AudioPreprocessor:
    """
    Classe principal para pré-processamento.

    Uso típico:
        pre = AudioPreprocessor()
        processed_bytes = pre.process_chunk_bytes(raw_bytes)
        # processed_bytes -> bytes PCM16 mono sample_rate (CONFIG["audio"]["samplerate"])
    """

    def __init__(self,
                 sample_rate: Optional[int] = None,
                 do_resample: bool = True,
                 do_noise_reduction: bool = True,
                 do_bandpass: bool = True,
                 lowcut: float = 80.0,
                 highcut: float = 8000.0,
                 vad_mode: int = 1,
                 vad_energy_threshold: float = 500.0,
                 normalize_mode: str = "rms",  # 'peak' or 'rms' or None
                 agc: bool = True):
        self.sample_rate = sample_rate or _CFG["audio"].get("samplerate", 16000)
        self.do_resample = do_resample
        self.do_noise_reduction = do_noise_reduction and _HAS_NOISEREDUCE
        self.do_bandpass = do_bandpass and _HAS_SCIPY
        self.lowcut = lowcut
        self.highcut = highcut
        self.vad = VAD(sample_rate=self.sample_rate, mode=vad_mode, energy_threshold=vad_energy_threshold)
        self.normalize_mode = normalize_mode
        self.agc = agc

    def bytes_to_np(self, b: bytes, dtype=np.int16) -> np.ndarray:
        return np.frombuffer(b, dtype=dtype)

    def np_to_bytes(self, arr: np.ndarray) -> bytes:
        return arr.astype(np.int16).tobytes()

    def ensure_sample_rate(self, arr: np.ndarray, orig_sr: int) -> np.ndarray:
        if orig_sr == self.sample_rate or not self.do_resample:
            return arr
        return resample_array(arr, orig_sr, self.sample_rate)

    def process_array(self, arr: np.ndarray, orig_sr: int = None) -> np.ndarray:
        """
        Recebe numpy array (int16 or float) e retorna int16 mono na sample_rate configurada.
        """
        # normalize dtype to float32 in -1..1 if needed
        if arr.dtype.kind == 'i':
            arr = arr.astype(np.int16)
        # If multi-channel, make mono
        if arr.ndim == 2:
            arr = arr.mean(axis=1).astype(np.int16)

        # If arr is int16 but sample rate differs, must resample
        if orig_sr is None:
            orig_sr = self.sample_rate

        # convert to int16 np array
        arr_int16 = arr.astype(np.int16)

        # Resample if needed
        if orig_sr != self.sample_rate and self.do_resample:
            arr_int16 = resample_array(arr_int16, orig_sr, self.sample_rate).astype(np.int16)

        # Bandpass filter
        if self.do_bandpass:
            try:
                arr_int16 = apply_bandpass(arr_int16.astype(np.float32), self.lowcut, self.highcut, self.sample_rate)
                arr_int16 = np.asarray(arr_int16, dtype=np.int16)
            except Exception:
                pass

        # Noise reduction
        if self.do_noise_reduction:
            try:
                arr_int16 = reduce_noise_array(arr_int16, self.sample_rate)
            except Exception:
                pass

        # Normalize / AGC
        if self.normalize_mode == "peak":
            arr_int16 = normalize_peak(arr_int16)
        elif self.normalize_mode == "rms":
            arr_int16 = normalize_rms(arr_int16)
        if self.agc:
            arr_int16 = simple_agc(arr_int16)

        return arr_int16.astype(np.int16)

    def process_chunk_bytes(self, chunk_bytes: bytes, orig_sr: int = None) -> Optional[bytes]:
        """
        Recebe chunk em bytes (esperado PCM16 little-endian interleaved or mono),
        aplica pré-processo e retorna bytes PCM16 mono na sample_rate do sistema.
        Retorna None se o chunk foi considerado silêncio (pela VAD).
        """
        try:
            arr = bytes_to_int16_array(chunk_bytes)
        except Exception:
            return None

        # make mono
        arr = ensure_mono(arr)

        # Assume orig_sr if not given is system sample rate
        if orig_sr is None:
            orig_sr = _CFG["audio"].get("samplerate", self.sample_rate)

        # resample / filters / normalize / noise reduction
        arr_proc = self.process_array(arr, orig_sr=orig_sr)

        # VAD: split in small frames and check voice
        frame_ms = 30  # 10/20/30 ms frames recommended by webrtcvad
        frame_len = int(self.sample_rate * (frame_ms / 1000.0))
        has_voice = False
        for start in range(0, len(arr_proc), frame_len):
            frame = arr_proc[start:start+frame_len]
            if len(frame) < frame_len:
                # pad
                pad = np.zeros(frame_len - len(frame), dtype=np.int16)
                frame = np.concatenate([frame, pad])
            if self.vad.is_speech(frame):
                has_voice = True
                break

        if not has_voice:
            # silence -> skip
            return None

        # optional trim silence on edges (coarse)
        arr_trimmed = trim_silence(arr_proc, self.sample_rate, top_db=20.0)
        if arr_trimmed.size == 0:
            arr_trimmed = arr_proc

        return int16_array_to_bytes(arr_trimmed)

    def process_stream_generator(self, chunk_bytes_iterable, orig_sr: int = None):
        """
        Recebe um iterável de chunk_bytes (por exemplo a fila do AudioInput.q)
        e produz chunks processados (bytes) prontos para enviar ao recognizer.
        Use:
            for processed in pre.process_stream_generator(audio_input.q):
                if processed:
                    recognizer.AcceptWaveform(processed)
        """
        for b in chunk_bytes_iterable:
            try:
                out = self.process_chunk_bytes(b, orig_sr=orig_sr)
                if out:
                    yield out
            except Exception:
                # log if you have logger, else ignore to be robust
                continue

