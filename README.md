# Projeto integrador - Sistema embarcado de reconhecimento de voz offline


Com objetivo de desenvolver um sistema de reconhecimento de voz embarcado offline para a cadeira de Projeto integrador da faculdade de Engenharia de computação - UFSM, este repositório visa organizar e estruturar o código desenvolvido para o projeto.
O sistema baseia-se na implementação de um ESP32-S3 com um microfone I2S que irá receber os chunks de audio e logo efetuar o preprocessamento de aúdio por meio de MFCCs.

## Requisitos de desenvolvimento

Os requisitos de desenvolvimento serão dividios em Hardware e Software para melhor organizar e estruturar a documentação.

#### > Hardware:
- ESP32-S3
- Microfone I2S

#### > Software
- Python 3.8+
- Vosk
- PyAudio
[...]

## Instalação do módulo de desenvolvimento 
Este módulo possuí os códigos que serão jogados para o ESP32-S3 no futuro.
Para a instalação siga exatamente os passos seguintes para evitar qualquer tipo de erro e incompatibilidade.

1. Clone o repositório:
```bash
git clone https://github.com/Vitormateusromancini/Projeto-Integrador---SISTEMA-EMBARCADO-DE-RECONHECIMENTO-DE-VOZ-OFFLINE.git
```

2. Acesse o diretório do projeto:
```bash
cd Projeto-Integrador---SISTEMA-EMBARCADO-DE-RECONHECIMENTO-DE-VOZ-OFFLINE
```

3. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
```

4. Ative o ambiente virtual:
```bash
./venv/Scripts/activate
```

5. Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```

## Casos de testes feitos com pytest

Para executar os testes:
```bash
python -m pytest -v tests/
```
