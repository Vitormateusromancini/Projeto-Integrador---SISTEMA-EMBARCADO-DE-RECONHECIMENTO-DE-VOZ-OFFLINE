import unicodedata
import re
import json
from typing import Dict, Any, Optional
from keys import *

def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"\s+", " ", text)
    return text

def _find_best_match(text: str, synonyms_dict: Dict[str, list]) -> Optional[tuple[str, str]]:
    candidates = []
    for key, syns in synonyms_dict.items():
        for s in syns:
            sn = _normalize(s)
            pattern = r'(?<!\w)' + re.escape(sn) + r'(?!\w)'
            if re.search(pattern, text):
                candidates.append((key, sn, len(sn)))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates[0][0], candidates[0][1]

def _find_room(text: str) -> Optional[str]:
    found = _find_best_match(text, ROOMS)
    return found[0] if found else None

def _find_generic_device(text: str) -> Optional[str]:
    found = _find_best_match(text, GENERIC_DEVICES)
    return found[0] if found else None

def _is_negated(text: str) -> bool:
    return bool(re.search(r"\bnao\b|\bnao\s+\w+|\bn\u00e3o\b", text)) or " nao " in text or " não " in text

def _apply_negation(action_key: Optional[str], negated: bool) -> Optional[str]:
    if not action_key:
        return action_key
    if negated and action_key in NEGATION_INVERT:
        return NEGATION_INVERT[action_key]
    return action_key

def _extract_value(text: str) -> Optional[tuple[float, str]]:
    m = re.search(r"(\d{1,3})\s*%", text)
    if m:
        v = float(m.group(1))
        return max(0.0, min(100.0, v)), "%"
    m = re.search(r"(\d{1,3})\s*(graus|c|°c|°)?", text)
    if m:
        v = float(m.group(1))
        unit = m.group(2) or ""
        if unit:
            return v, "graus"
    return None

def _confidence(has_action: bool, has_device: bool, text: str) -> float:
    conf = 0.0
    if has_action:
        conf += 0.5
    if has_device:
        conf += 0.4
    if re.search(r"\b(por favor|agora|imediatamente|por gentileza)\b", text):
        conf += 0.05
    if re.search(r"\b(abra|feche|ligue|desligue|aumente|diminua|abre|fecha|liga|desliga)\b", text):
        conf += 0.05
    if re.search(r"\d+\s*%|\d+\s*(graus|c|°c|°)", text):
        conf += 0.05
    if _find_room(text):
        conf += 0.05
    return max(0.0, min(1.0, conf))

def parse_command(text: str) -> Dict[str, Any]:
    norm = _normalize(text)
    action = _find_best_match(norm, ACTIONS)
    device = _find_best_match(norm, DEVICES)

    has_action = action is not None
    has_device = device is not None

    neg = _is_negated(" " + norm + " ")
    action_key = action[0] if has_action else None
    action_key = _apply_negation(action_key, neg)

    device_key = device[0] if has_device else None
    if not device_key:
        generic = _find_generic_device(norm)
        room = _find_room(norm)
        if generic in COMPOSABLE and room:
            device_key = f"{generic}_{room}"
            has_device = True

    intent = INTENT_DEFAULT if (action_key and has_device) else "desconhecido"

    result = {
        "intent": intent,
        "entities": {
            "acao": action_key if action_key else None,
            "dispositivo": device_key if has_device else None
        },
        "confidence": _confidence(bool(action_key), has_device, norm)
    }
    val = _extract_value(norm)
    if val:
        result["entities"]["valor"] = val[0]
        result["entities"]["unidade"] = val[1]
    return result

if __name__ == "__main__":
    samples = [
        "Abra a porta da garagem, por favor",
        "Liga a luz da sala",
        "Pode desligar o ar condicionado?",
        "Aumente o ar",
        "Baixa a cortina",
        "Nao ligar a luz da cozinha",
        "Coloca a TV da sala no 50%",
        "Ajusta o ar para 22 graus",
        "Quero pizza"
    ]
    for s in samples:
        result = parse_command(s)
        print(s)
        print(json.dumps(result, ensure_ascii=False, indent=2))