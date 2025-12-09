# Vocabulário de ações, dispositivos e ambientes
# usado pelo módulo de NLP para mapear texto -> intent/entities

ACTIONS = {
    "abrir": [
        "abrir", "abre", "abra", "abrindo",
        "erguer", "ergue", "ergam",
        "levantar", "levanta", "levante",
        "subir", "suba", "sobe",
        "destravar", "destranca", "destrancar",
    ],
    "fechar": [
        "fechar", "fecha", "feche", "fechando",
        "abaixar", "abaixa", "abaixe",
        "baixar", "baixa", "baixe",
        "descer", "desce", "desça",
        "trancar", "tranca", "tranque",
        "encerrar", "encerra", "encerre",
    ],
    "ligar": [
        "ligar", "liga", "ligue", "ligando",
        "ativar", "ativa", "ative", "ativando",
        "acender", "acende", "acenda", "acendendo",
        "iniciar", "inicia", "inicie",
        "start", "startar", "começar", "comecar",
        "coloca", "colocar", "bota", "botar",
        "deixar ligado", "ligar tudo", "ligar geral",
        "ligar sistema", "acionar", "aciona", "acione",
        "rodar", "rodando", "tocar", "toca", "toque",
        "subir som", "ligar musica", "ligar música",
    ],
    "desligar": [
        "desligar", "desliga", "desligue", "desligando",
        "apagar", "apaga", "apague", "apagando",
        "desativar", "desativa", "desative", "desativando",
        "parar", "para", "pare", "parando",
        "stop", "stope", "pausar", "pausa", "pause",
        "tirar", "desligar tudo", "apagar tudo", "zerar",
        "desligar sistema", "cancelar", "cancela", "cancelar tudo",
    ],
    "aumentar": [
        "aumentar", "aumenta", "aumente", "aumentando",
        "subir", "sobe", "suba", "subindo",
        "elevar", "eleva", "eleve",
        "mais", "coloca mais", "ficar mais forte",
        "aumentar volume", "subir volume", "volume para cima",
        "aumentar intensidade", "aumentar velocidade",
        "deixa mais forte", "deixa mais alto",
        "reforçar", "reforca", "reforça",
    ],
    "diminuir": [
        "diminuir", "diminui", "diminua", "diminuindo",
        "baixar", "baixa", "baixe", "baixando",
        "reduzir", "reduz", "reduza", "reduzindo",
        "menos", "coloca menos", "deixar mais fraco",
        "baixar volume", "diminuir volume", "volume para baixo",
        "diminuir intensidade", "diminuir velocidade",
        "deixa mais fraco", "deixa mais baixo",
        "suavizar", "amenizar",
    ],
}

# Dispositivos específicos: podem ser mapeados direto do texto
DEVICES = {
    # --- LUZES ---
    "luz_sala": [
        "luz da sala", "luz sala", "luz da sala de estar",
        "lampada da sala", "lampada sala", "lâmpada da sala",
        "iluminacao da sala", "iluminação da sala",
        "luz da sala principal",
    ],
    "luz_quarto": [
        "luz do quarto", "luz quarto",
        "lampada do quarto", "lampada quarto", "lâmpada do quarto",
        "iluminacao do quarto", "iluminação do quarto",
        "luz do dormitorio", "luz do dormitório",
    ],
    "luz_cozinha": [
        "luz da cozinha", "luz cozinha",
        "lampada da cozinha", "lampada cozinha", "lâmpada da cozinha",
        "iluminacao da cozinha", "iluminação da cozinha",
    ],
    "luz_banheiro": [
        "luz do banheiro", "luz banheiro",
        "lampada do banheiro", "lâmpada do banheiro",
    ],
    "luz_corredor": [
        "luz do corredor", "luz corredor",
        "luz do hall", "luz do corredor principal",
    ],
    "luz_garagem": [
        "luz da garagem", "luz garagem",
        "lampada da garagem", "lâmpada da garagem",
    ],
    "luz_varanda": [
        "luz da varanda", "luz varanda",
        "luz da sacada", "luz sacada",
        "luz da area externa", "luz da área externa",
    ],
    "luz_escritorio": [
        "luz do escritorio", "luz do escritório",
        "luz do office", "luz do home office",
    ],

    # --- PORTAS / JANELAS ---
    # aqui entram DIRETAMENTE os teus exemplos "fechar a porta" / "abrir a janela"
    "porta_geral": [
        "porta", "a porta",
        "porta de entrada", "porta principal",
        "porta da casa",
    ],
    "porta_quarto": [
        "porta do quarto", "a porta quarto",
        "a porta do quarto", "quarto",
        "fechar quarto", 
    ],
    "janela_geral": [
        "janela", "a janela",
        "janela da sala", "janela do quarto",
    ],
    "porta_garagem": [
        "porta da garagem", "porta de garagem",
        "portao da garagem", "portão da garagem",
        "portao", "portão", "garagem",
        "portao da casa", "portão da casa",
    ],

    # --- CLIMATIZAÇÃO ---
    "ar_condicionado_sala": [
        "ar da sala", "ar condicionado da sala", "ar condicionado sala",
        "ar da sala de estar",
    ],
    "ar_condicionado_quarto": [
        "ar do quarto", "ar condicionado do quarto", "ar condicionado quarto",
        "ar do dormitorio", "ar do dormitório",
    ],
    "ar_condicionado": [
        "ar condicionado", "ar-condicionado", "arcondicionado",
        "ar", "ac", "ar frio", "ar quente",
        "climatizador", "clima",
    ],
    "ventilador_sala": [
        "ventilador da sala", "ventilador sala",
        "vento da sala", "ventilador de teto da sala",
    ],
    "ventilador_quarto": [
        "ventilador do quarto", "ventilador quarto",
        "vento do quarto", "ventilador de teto do quarto",
    ],
    "exaustor_cozinha": [
        "exaustor da cozinha", "exaustor cozinha",
        "coifa", "coifa da cozinha",
    ],

    # --- ENTRETENIMENTO / TV / SOM ---
    "tv_sala": [
        "tv da sala", "tv sala",
        "televisao da sala", "televisão da sala",
        "televisao", "televisão",
        "a tv", "a televisão", "a tele",
        "teve", "tevê",
    ],
    "tv_quarto": [
        "tv do quarto", "tv quarto",
        "televisao do quarto", "televisão do quarto",
        "teve do quarto", "tevê do quarto",
    ],
    "som_sala": [
        "som da sala", "som sala",
        "som ambiente", "som", "caixa de som",
        "home theater", "home theater da sala",
    ],
    "som_quarto": [
        "som do quarto", "som quarto",
        "caixa de som do quarto",
    ],

    # --- TOMADAS / ENERGIA ---
    "tomada_sala": [
        "tomada da sala", "tomada sala",
        "tomada da tv", "tomada da estante",
    ],
    "tomada_quarto": [
        "tomada do quarto", "tomada quarto",
        "tomada da cama", "tomada do criado",
    ],
    "tomada_geral": [
        "tomadas", "tomadas gerais",
        "tomada geral", "energia da casa",
        "energia geral", "energia",
    ],

    # --- CORTINAS / PERSIANAS ---
    "cortina_sala": [
        "cortina da sala", "cortina sala",
        "persiana da sala", "persiana sala",
        "cortina da janela da sala",
    ],
    "cortina_quarto": [
        "cortina do quarto", "cortina quarto",
        "persiana do quarto", "persiana quarto",
        "cortina da janela do quarto",
    ],
    "cortina_varanda": [
        "cortina da varanda", "cortina da sacada", "cortina da varanda da sala",
    ],

    # --- COZINHA / ELETROS ---
    # aqui cobre "microondas" que você falou
    "microondas_cozinha": [
        "microondas", "micro-ondas", "micro ondas",
        "microondas da cozinha", "micro-ondas da cozinha",
        "forno microondas", "forno micro-ondas",
    ],
    "cafeteira_cozinha": [
        "cafeteira", "cafeteira da cozinha", "maquina de cafe", "máquina de café",
    ],

    # --- MÁQUINAS / GERAIS ---
    # para comandos como "ligar a máquina"
    "maquina_geral": [
        "maquina", "máquina",
        "maquina de lavar", "máquina de lavar",
        "maquina de lavar roupa", "máquina de lavar roupa",
        "maquina da area de servico", "máquina da área de serviço",
    ],

    # --- ESCRITÓRIO / COMPUTADOR ---
    "computador_escritorio": [
        "computador do escritorio", "computador do escritório",
        "pc do escritorio", "pc do escritório",
        "computador", "pc",
    ],
    "notebook_escritorio": [
        "notebook do escritorio", "notebook do escritório",
        "notebook", "laptop",
    ],
}

INTENT_DEFAULT = "controlar_dispositivo"

ROOMS = {
    "sala": [
        "sala", "sala de estar", "estar",
        "sala de tv", "sala de televisão",
        "sala principal", "sala grande",
    ],
    "cozinha": [
        "cozinha", "cozinha americana",
        "cozinha principal",
    ],
    "quarto": [
        "quarto", "dormitorio", "dormitório",
        "quarto principal", "quarto de casal",
        "meu quarto", "quarto de visitas",
    ],
    "banheiro": [
        "banheiro", "wc", "banheiro social",
        "banheiro suite", "banheiro suíte",
        "lavabo",
    ],
    "escritorio": [
        "escritorio", "escritório", "office",
        "escritorio home", "home office",
        "escritorio da casa",
    ],
    "garagem": [
        "garagem", "garagem coberta",
        "vaga", "vaga da garagem",
    ],
    "varanda": [
        "varanda", "sacada", "terraço",
        "area externa", "área externa",
    ],
    "area_servico": [
        "area de servico", "área de serviço",
        "lavanderia", "area de lavar roupa", "área de lavar roupa",
    ],
    "corredor": [
        "corredor", "hall", "hall de entrada",
    ],
}

GENERIC_DEVICES = {
    "luz": [
        "luz", "lampada", "lâmpada",
        "iluminacao", "iluminação",
        "luz principal", "luz geral",
        "luzinha", "luz do ambiente",
    ],
    "cortina": [
        "cortina", "persiana",
        "cortina eletrica", "cortina elétrica",
        "cortina da janela", "cortina da porta",
    ],
    "tv": [
        "tv", "televisao", "televisão",
        "a tv", "a televisão", "a tele",
        "teve", "tevê",
    ],
    "ventilador": [
        "ventilador", "vento", "ventilador de teto",
        "ventilador da sala", "ventilador do quarto",
    ],
    "som": [
        "som", "som ambiente",
        "caixa de som", "audio", "áudio",
        "som da sala", "som do quarto",
    ],
    "tomada": [
        "tomada", "tomadas",
        "energia", "energia da casa",
        "tomada geral", "tomadas gerais",
    ],
    "ar_condicionado": [
        "ar", "ar condicionado", "ar-condicionado", "arcondicionado",
        "clima", "climatizador",
    ],
    "porta": [
        "porta", "portao", "portão",
        "porta de entrada", "porta principal",
    ],
    "janela": [
        "janela", "janela da sala", "janela do quarto",
    ],
    "microondas": [
        "microondas", "micro-ondas", "micro ondas",
    ],
    "maquina": [
        "maquina", "máquina",
        "maquina de lavar", "máquina de lavar",
    ],
}

# Quais GENERIC_DEVICES podem ser combinados com ROOMS para formar DEVICES
COMPOSABLE = {
    "luz",
    "cortina",
    "tv",
    "ventilador",
    "som",
    "tomada",
    "ar_condicionado",
    "porta",
    "janela",
    "microondas",
    "maquina",
}

NEGATION_INVERT = {
    "ligar": "desligar",
    "desligar": "ligar",
    "abrir": "fechar",
    "fechar": "abrir",
    "aumentar": "diminuir",
    "diminuir": "aumentar",
}
