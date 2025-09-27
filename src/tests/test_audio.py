import pytest

from src.audio.microphone import AudioInput
from src.audio.recorder import AudioRecorder

# @pytest.mark.skip("Requer microfone conectado e permissões de áudio")
def test_audio_stream():
    """Testa se o stream de áudio inicia corretamente"""
    audio_input = AudioInput()
    stream = audio_input.start_stream()

    with stream:
        # tenta pegar um chunk do microfone
        chunk = audio_input.q.get(timeout=5)  # espera até 5 segundos
        assert chunk is not None
        assert isinstance(chunk, bytes)
        assert len(chunk) > 0
    print("Stream de áudio funcionando corretamente!")


# @pytest.mark.skip("Requer microfone conectado")
def test_audio_recorder():
    """Testa se o recorder consegue capturar um chunk"""
    audio_input = AudioInput()
    recorder = AudioRecorder(audio_input)
    stream = audio_input.start_stream()

    with stream:
        chunk = recorder.get_next_chunk()
        assert chunk is not None
        assert isinstance(chunk, bytes)
        print("Recorder capturou áudio corretamente!")