import pytest
import os
from vosk import Model
from src.recognition.model_manager import ModelManager
from src.recognition.vosk_recognizer import VoskRecognizer
from src.core.config import CONFIG

# @pytest.mark.skip("Requer modelo Vosk baixado e instalado na pasta correta")
def test_load_model():
    """Testa se o modelo Vosk é carregado corretamente"""
    manager = ModelManager()
    model = manager.load_model()
    assert isinstance(model, Model)
    assert os.path.exists(CONFIG["recognition"]["model_path"])
    print("Modelo carregado corretamente!")

