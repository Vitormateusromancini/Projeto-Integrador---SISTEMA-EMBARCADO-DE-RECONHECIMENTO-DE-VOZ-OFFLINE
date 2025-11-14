import pvporcupine
import numpy as np
import os
from src.core.config import CONFIG

class PorcupineRecognizer:
    """
    Motor de Detecção de Palavra-Chave (KWS) de baixo consumo,
    usando Picovoice Porcupine.
    """

    def __init__(self):
        kws_config = CONFIG["kws"]
        self.access_key = kws_config["access_key"]
        self.keyword_paths = kws_config["keyword_paths"]
        self.sensitivities = kws_config["sensitivities"]
        self.model_path = kws_config["model_path"]
        self.handle = None

        # Verifica se o arquivo da hotword (.ppn) existe
        if not os.path.exists(self.keyword_paths[0]):
            raise FileNotFoundError(f"Modelo KWS (.ppn) não encontrado em: {self.keyword_paths[0]}.")

        # Verifica se o modelo de idioma base (.pv) existe
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo base KWS (.pv) não encontrado em: {self.model_path}.")

        try:
            # Inicializa o motor do Porcupine com o modelo de idioma Português
            self.handle = pvporcupine.create(
                access_key=self.access_key,
                keyword_paths=self.keyword_paths,
                model_path=self.model_path,
                sensitivities=self.sensitivities
            )
            print(f"Porcupine ativado (PT). Frame: {self.handle.frame_length} amostras.")

        except pvporcupine.PorcupineError as e:
            print(f"Erro ao inicializar Porcupine: {e}.")
            raise

    def process_chunk(self, chunk: bytes) -> int:
        """
        Processa um chunk de áudio PCM16 (1024 bytes).
        :param chunk: Chunk de áudio em bytes.
        :return: Índice (int) da palavra-chave detectada, ou -1.
        """
        if self.handle is None:
            return -1
        frame = np.frombuffer(chunk, dtype=np.int16)

        result = self.handle.process(frame)
        return result

    def delete(self):
        """Libera os recursos do Porcupine."""
        if self.handle is not None:
            self.handle.delete()
            print("Porcupine encerrado.")