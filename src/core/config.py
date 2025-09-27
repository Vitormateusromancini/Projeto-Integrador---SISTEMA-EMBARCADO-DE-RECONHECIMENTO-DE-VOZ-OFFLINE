CONFIG = {
    "audio": {
        "samplerate": 16000,
        "blocksize": 8000,
        "device": 0  # Aqui você coloca o ID ou nome do microfone desejado, por padrão 0
    },
    "recognition": {
        "model_path": "models/vosk-model-small-pt-0.3"
    }
}