import json
import serial
from vosk import Model, KaldiRecognizer

from src.nlp.nlp import parse_command
from src.nlp.keys import ACTIONS  # pra reutilizar as listas de palavras

# ========= CONFIGURAÇÕES =========

SAMPLE_RATE = 8000
SERIAL_PORT = "/dev/ttyACM0"   
BAUD = 230400

# confiança mínima pra levar o comando a sério
CONF_MIN = 0.4


# ========= HELPERS DE NLP / DIÁLOGO =========

def classificar_dispositivo(dispositivo: str) -> str:
    """Decide o tipo do dispositivo:"""
    dispositivo = dispositivo or ""
    if any(p in dispositivo for p in ["porta", "janela", "cortina"]):
        return "abrir_fechar"
    return "ligar_desligar"


def detectar_acao_em_texto(texto: str) -> str | None:
    if not texto:
        return None

    t = texto.lower()

    # checa nas listas do keys.py
    for acao, palavras in ACTIONS.items():
        for p in palavras:
            if p in t:
                return acao

    # fallback pra sim/não (será tratado na função que chama)
    return None


def perguntar_acao(dispositivo: str, model: Model, ser: serial.Serial) -> str | None:
    """
    Pergunta o que fazer com o dispositivo e espera resposta de voz.
    """
    tipo = classificar_dispositivo(dispositivo)

    if tipo == "abrir_fechar":
        opcao1, opcao2 = "abrir", "fechar"
    else:
        opcao1, opcao2 = "ligar", "desligar"

    print("------------------------------------------------")
    print(f"O que você deseja fazer com {dispositivo}?")
    print(f"Diga '{opcao1}' ou '{opcao2}'.")
    print("Você também pode responder 'sim' para", opcao1, "ou 'não' para cancelar.\n")
    print("------------------------------------------------")

    while True:
        rec2 = KaldiRecognizer(model, SAMPLE_RATE)

        # Escuta até formar uma frase
        while True:
            data = ser.read(4000)
            if len(data) == 0:
                continue

            if rec2.AcceptWaveform(data):
                res2 = json.loads(rec2.Result())
                text2 = (res2.get("text") or "").strip()
                break
            # se quiser ver parciais, poderia usar rec2.PartialResult()

        print(f"Resposta reconhecida para ação: '{text2}'\n")

        if not text2:
            print("Não entendi nada, tente novamente...\n")
            continue

        lower = text2.lower()

        # 1) tenta achar ação explícita (ligar, desligar, abrir, fechar)
        acao_detectada = detectar_acao_em_texto(lower)
        if acao_detectada in ["ligar", "desligar", "abrir", "fechar"]:
            print("Ação escolhida:", acao_detectada)
            return acao_detectada

        # 2) trata 'sim' / 'não'
        if "sim" in lower:
            print("Entendido 'sim' ->", opcao1)
            return opcao1

        if "nao" in lower or "não" in lower:
            print("Entendido 'não' -> cancelando comando para esse dispositivo.")
            return None

        # 3) se chegou aqui, não entendeu
        print("Não entendi a ação. Por favor, diga claramente", opcao1, "ou", opcao2, "ou 'sim'/'não'.\n")


# ========= PROGRAMA PRINCIPAL =========

def main():
    print("Carregando modelo Vosk...")
    model = Model("models/vosk-model-small-pt-0.3")
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)
    print(f"Serial aberta em {SERIAL_PORT}")
    print("Fale perto do microfone...")

    while True:
        # ~0,25 s de áudio da ESP32
        data = ser.read(4000)
        if len(data) == 0:
            continue

        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            text = (res.get("text") or "").strip()
            if not text:
                continue

            print("\n================ RECONHECIMENTO ================")
            print("Texto reconhecido:", text)

            # 1) NLP original do projeto
            nlp_raw = parse_command(text)
            print("Resultado NLP (bruto):", nlp_raw)

            intent_raw = nlp_raw.get("intent")
            entities_raw = nlp_raw.get("entities") or {}
            acao_raw = entities_raw.get("acao")
            disp_raw = entities_raw.get("dispositivo")
            conf_raw = nlp_raw.get("confidence", 0.0)

            # 2) Lógica de diálogo / interação

            # Caso A: confiança muito baixa ou nada reconhecido -> ignora
            if conf_raw < CONF_MIN and not acao_raw and not disp_raw:
                print("Confiança muito baixa e sem ação/dispositivo -> ignorando comando.\n")
                print("================================================\n")
                continue

            # Caso B: temos ação E dispositivo -> comando pronto
            if acao_raw and disp_raw and conf_raw >= CONF_MIN:
                nlp_final = nlp_raw

            # Caso C: só dispositivo (tipo 'microondas', 'televisão', 'porta') -> perguntar ação
            elif disp_raw and not acao_raw and conf_raw >= CONF_MIN:
                print("Somente dispositivo reconhecido. Iniciando diálogo para definir ação...\n")
                acao_escolhida = perguntar_acao(disp_raw, model, ser)
                if acao_escolhida is None:
                    nlp_final = {
                        "intent": "desconhecido",
                        "entities": {"acao": None, "dispositivo": disp_raw},
                        "confidence": conf_raw,
                    }
                else:
                    entities_final = dict(entities_raw)
                    entities_final["acao"] = acao_escolhida
                    nlp_final = {
                        "intent": "controlar_dispositivo",
                        "entities": entities_final,
                        "confidence": conf_raw,
                    }

            # Caso D: só ação ou tudo muito confuso -> marca como desconhecido
            else:
                nlp_final = {
                    "intent": "desconhecido",
                    "entities": {"acao": acao_raw, "dispositivo": disp_raw},
                    "confidence": conf_raw,
                }

            print("Resultado NLP (final):", nlp_final)

            intent = nlp_final.get("intent")
            entities = nlp_final.get("entities", {})
            acao = entities.get("acao")
            dispositivo = entities.get("dispositivo")

            print(f"Intent final: {intent}")
            print(f"Ação: {acao}")
            print(f"Dispositivo: {dispositivo}")
            print("================================================\n")

            # >>> Aqui vai o envio pra ESP32 (porta, janela, luz, relé, etc.)
            # if intent == "controlar_dispositivo" and acao and dispositivo:
            #     enviar_para_esp32(acao, dispositivo)

        else:
            parc = json.loads(rec.PartialResult())
            partial = (parc.get("partial") or "").strip()
            if partial:
                print("parcial:", partial)


if __name__ == "__main__":
    main()