import pytest
import os
import time
import numpy as np
from src.recognition.porcupine_recognizer import PorcupineRecognizer
from src.core.config import CONFIG

# O tamanho esperado do chunk em bytes (512 amostras * 2 bytes/amostra = 1024 bytes)
EXPECTED_CHUNK_SIZE = CONFIG["audio"]["blocksize"] * 2


# --- FUNÇÕES AUXILIARES (Necessárias para o fluxo de teste) ---

def create_silence_chunk():
    """Cria um chunk de silêncio no formato PCM16 do tamanho exato do KWS (512 amostras)."""
    return b'\x00' * EXPECTED_CHUNK_SIZE


def create_mock_hotword_chunk():
    """
    Cria um chunk mockado (simulado) para teste de fluxo, garantindo o tamanho correto.
    Usa ruído simulado, mas não detectará a hotword real.
    """
    # Cria um chunk com algum ruído simulado (bytes aleatórios)
    return np.random.randint(-100, 100, size=CONFIG["audio"]["blocksize"], dtype=np.int16).tobytes()


# --- FIXTURE ---

@pytest.fixture(scope="session")
def porcupine_recognizer_fixture():
    """Fixture para carregar e inicializar o Porcupine uma vez por sessão de teste."""
    recognizer = None
    try:
        recognizer = PorcupineRecognizer()
        yield recognizer
    except FileNotFoundError as e:
        pytest.skip(f"Modelo KWS não encontrado: {e}")
    except Exception as e:
        pytest.fail(f"Falha ao carregar Porcupine: {e}")
    finally:
        if recognizer:
            recognizer.delete()


# --- TESTES FUNCIONAIS ---

def test_kws_initialization(porcupine_recognizer_fixture):
    """Testa se o Porcupine inicializa e se o tamanho do frame está correto (512 amostras)."""
    recognizer = porcupine_recognizer_fixture
    assert recognizer is not None
    assert recognizer.handle.frame_length == CONFIG["audio"]["blocksize"]
    print("\nPorcupine inicializado com o tamanho de frame correto (512 amostras).")


def test_kws_silence_no_detection(porcupine_recognizer_fixture):
    """Testa se o Porcupine não detecta a hotword em um chunk de silêncio (resultado -1)."""
    silence_chunk = create_silence_chunk()
    result = porcupine_recognizer_fixture.process_chunk(silence_chunk)

    # O resultado deve ser -1 para 'nenhuma hotword detectada'
    assert result == -1
    print("\nSilêncio não ativou a hotword (resultado -1).")


@pytest.mark.skip("Requer áudio pré-gravado da hotword para detecção real.")
def test_kws_hotword_detection_with_audio(porcupine_recognizer_fixture):
    mock_hotword_chunk = create_mock_hotword_chunk()

    # Para o teste de fluxo, verifica se o chunk mockado tem o tamanho KWS correto
    assert len(mock_hotword_chunk) == EXPECTED_CHUNK_SIZE

    print("\nTeste de detecção de Hotword pulado (requer áudio real pré-gravado).")