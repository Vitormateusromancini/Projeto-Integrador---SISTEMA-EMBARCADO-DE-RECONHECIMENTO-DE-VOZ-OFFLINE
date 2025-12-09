import os
import json

# --- Definições de Caminhos ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# --- CONFIGURAÇÃO PRINCIPAL ---
CONFIG = {
    # --- Configurações de Áudio ---
    "audio": {
        "samplerate": 8000,
        "blocksize": 512,  # Valor estático (requerido pelo Porcupine)
        "device": 0,
    },

    # --- Configurações de Reconhecimento de Fala (Vosk ASR) ---
    "recognition": {
        "model_path": os.path.join(MODELS_DIR, "vosk-model-small-pt-0.3"),
    },

    # --- Configurações de Detecção de Hotword (Picovoice Porcupine KWS) ---
    "kws": {
        # A chave de acesso
        "access_key": "Qw2mCAcCfe2SAkzgN5SwG8N5SII0Qt7fo5M98hFmwdkh53qAsXvJaQ==",
        "keyword_paths": [
            os.path.join(MODELS_DIR, 'picovoice', 'sistema_pt.ppn')
        ],
        "model_path": os.path.join(MODELS_DIR, 'picovoice', 'porcupine_params_pt.pv'),

        "sensitivities": [0.7],
    }
}
