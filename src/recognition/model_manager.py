import os
from vosk import Model
from src.core.config import CONFIG

class ModelManager:
    def __init__(self):
        self.model_path = CONFIG["recognition"]["model_path"]
        self.model = None

    def load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo Vosk não encontrado em {self.model_path}")
        if self.model is None:
            self.model = Model(self.model_path)
        return self.model
