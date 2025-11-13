ACTIONS = {
    "abrir": ["abrir", "abre", "abra", "abrindo"],
    "fechar": ["fechar", "fecha", "feche", "fechando"],
    "ligar": ["ligar", "liga", "ligue", "ativar", "ative", "acender", "acenda", "iniciar", "start"],
    "desligar": ["desligar", "desliga", "desligue", "apagar", "apague", "desativar", "desative", "parar", "stop"],
    "aumentar": ["aumentar", "aumenta", "aumente", "subir", "suba", "elevar", "mais", "incrementar"],
    "diminuir": ["diminuir", "diminui", "diminua", "baixar", "baixe", "reduzir", "reduza", "menos", "decrementar"]
}

DEVICES = {
    "porta_garagem": ["porta da garagem", "porta de garagem", "portao da garagem", "portão da garagem", "portao", "portão", "garagem"],
    "luz_sala": ["luz da sala", "luz sala", "luz da sala de estar"],
    "ar_condicionado": ["ar condicionado", "ar-condicionado", "arcondicionado", "ar", "ac"],
    "tv_sala": ["tv da sala", "tv sala"],
    "cortina_sala": ["cortina da sala", "cortina sala"],
    "ventilador_sala": ["ventilador da sala", "ventilador sala"],
}

INTENT_DEFAULT = "controlar_dispositivo"

ROOMS = {
    "sala": ["sala", "sala de estar", "estar"],
    "cozinha": ["cozinha"],
    "quarto": ["quarto", "dormitorio", "dormitório"],
    "banheiro": ["banheiro", "wc"],
    "escritorio": ["escritorio", "escritório", "office"],
}

GENERIC_DEVICES = {
    "luz": ["luz", "lampada", "lâmpada", "iluminacao", "iluminação"],
    "cortina": ["cortina", "persiana"],
    "tv": ["tv", "televisao", "televisão"],
    "ventilador": ["ventilador", "vento"],
}

COMPOSABLE = {"luz", "cortina", "tv", "ventilador"}

NEGATION_INVERT = {
    "ligar": "desligar",
    "desligar": "ligar",
    "abrir": "fechar",
    "fechar": "abrir",
}