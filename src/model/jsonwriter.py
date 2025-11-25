import json
import os
from datetime import datetime
from typing import Dict, Any

class JsonWriter:
    def __init__(self, output_dir: str = "command_logs"):
        """
        Inicializa o writer
        :param output_dir: Pasta aonde os arquivos json são salvos.
        """
        # Pega o caminho absoluto relativo a raiz do projeto
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.output_dir = os.path.join(base_path, output_dir)
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_command(self, nlp_data: Dict[str, Any]):
        """
        Recebe o dicionário do nlp e salva como arquivo JSON
        """
        if not nlp_data:
            return

        # 1. registra o tempo(essencial pra log offline)
        timestamp = datetime.now()
        data_to_save = nlp_data.copy()
        data_to_save["timestamp"] = timestamp.isoformat()

        # 2. Gera um arquivo com nome unico
        filename = f"cmd_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        file_path = os.path.join(self.output_dir, filename)

        # 3. Grava no disco
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # ensure_ascii=False is critical for Portuguese accents (e.g., "portão")
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            print(f"[JsonWriter] Comando salvo em: {file_path}")
        except Exception as e:
            print(f"[JsonWriter] Erro ao salvar JSON: {e}")

# Teste simples pra verificar se funciona isolado do projeto
if __name__ == "__main__":
    # simulando a data que vem do src/nlp/nlp.py
    mock_data = {
        "intent": "controlar_dispositivo",
        "entities": {
            "acao": "ligar",
            "dispositivo": "luz_sala"
        },
        "confidence": 0.95
    }
    writer = JsonWriter()
    writer.save_command(mock_data)