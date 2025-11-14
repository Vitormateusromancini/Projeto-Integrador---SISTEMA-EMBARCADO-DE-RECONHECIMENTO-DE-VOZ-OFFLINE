# Sistema Embarcado de Reconhecimento de Voz Offline

Documentação do projeto integrador (Engenharia de Computação – UFSM) para um pipeline completo de reconhecimento de voz offline, com captura de áudio, pré-processamento, ASR com Vosk e interpretação de comandos (NLP) baseada em regras.

Esta documentação descreve a arquitetura, componentes, fluxos internos, comportamento esperado do sistema e diagramas UML em Mermaid.

---

## Visão Geral do Sistema

O sistema opera totalmente offline e é estruturado em camadas independentes:

* **Captura de áudio** em tempo real.
* **Pré-processamento** (normalização, redução de ruído, filtro passa-faixa, VAD, trim de silêncio).
* **Reconhecimento de fala (ASR)** usando modelo Vosk local.
* **Interpretação de comandos (NLP)** em português, baseada em sinônimos, regras e composição.

**Formato de dados entre módulos:**  
PCM16 mono (bytes), com taxa de amostragem definida em `src/core/config.py`.

---

## Estrutura do Código

* `src/audio/microphone.py` — `AudioInput` (stream de entrada usando sounddevice; fila de chunks).
* `src/audio/recorder.py` — `AudioRecorder` (consome fila do microfone).
* `src/audio/preprocessor.py` — `AudioPreprocessor` (resample, bandpass, redução de ruído opcional, normalização, AGC, VAD, trim e framing).
* `src/recognition/model_manager.py` — `ModelManager` (carrega `vosk.Model` localmente).
* `src/recognition/vosk_recognizer.py` — `VoskRecognizer` (ASR por chunk ou stream).
* `src/nlp/keys.py` — dicionários de sinônimos e regras (ações, dispositivos, cômodos, negação, composição).
* `src/nlp/nlp.py` — parser de comandos (`parse_command`).
* `src/core/config.py` — `CONFIG` (parâmetros de áudio e caminho do modelo Vosk).

---

## Diagrama de Componentes (UML)

```mermaid
graph TD
    UI[Usuário/Microfone] -->|PCM16| AudioInput

    subgraph Audio
      AudioInput -->|bytes| AudioRecorder
      AudioRecorder -->|bytes| AudioPreprocessor
    end

    subgraph ASR
      ModelManager -.-> VoskRecognizer
      AudioPreprocessor -->|bytes| VoskRecognizer
    end

    VoskRecognizer -->|texto parcial/final| NLPParser
    NLPParser -->|intent + entidades + confiança| OutputLayer[Camada de Saída / Atuadores]

    subgraph Core
      CONFIG[(CONFIG)] --- AudioInput
      CONFIG --- AudioPreprocessor
      CONFIG --- VoskRecognizer
      CONFIG --- ModelManager
    end
```

---

## Diagrama de Classes (UML)

```mermaid
classDiagram
    class AudioInput {
      - q: queue.Queue
      - samplerate: int
      - blocksize: int
      - device: int|str|None
      + start_stream(): RawInputStream
      + _callback(indata, frames, time, status)
    }

    class AudioRecorder {
      - audio_input: AudioInput
      + get_next_chunk(): bytes
    }

    class AudioPreprocessor {
      - sample_rate: int
      - do_resample: bool
      - do_noise_reduction: bool
      - do_bandpass: bool
      - lowcut: float
      - highcut: float
      - vad: VAD
      - normalize_mode: str
      - agc: bool
      + process_chunk_bytes(chunk: bytes, orig_sr: int?): bytes?
      + process_stream_generator(iterable: <bytes>, orig_sr: int?): <bytes>
    }

    class VAD {
      - sample_rate: int
      - energy_threshold: float
      - vad: webrtcvad.Vad?
      + is_speech(chunk_int16: np.ndarray): bool
    }

    class ModelManager {
      - model_path: str
      - model: vosk.Model?
      + load_model(): vosk.Model
    }

    class VoskRecognizer {
      - model: vosk.Model
      - sample_rate: int
      - recognizer: KaldiRecognizer
      + recognize_chunk(chunk: bytes): str
      + recognize_stream(audio_source: <bytes>): str
    }

    class NLPParser {
      + parse_command(text: str): dict
    }

    AudioRecorder --> AudioInput
    AudioPreprocessor --> VAD
    VoskRecognizer ..> ModelManager
```

---

## Diagrama de Sequência: Fluxo em Tempo Real

```mermaid
sequenceDiagram
    participant Mic as Microfone
    participant In as AudioInput
    participant Rec as AudioRecorder
    participant Pre as AudioPreprocessor
    participant MM as ModelManager
    participant ASR as VoskRecognizer
    participant NLP as NLP Parser
    participant Out as Saída/Atuadores

    Mic->>In: amostras PCM16
    In->>Rec: enqueue bytes

    loop stream
        Rec->>Pre: next chunk (bytes)
        Pre->>Pre: resample/bandpass/NR/normalize/AGC/VAD/trim
        Pre-->>ASR: bytes processados

        alt AcceptWaveform == true
            ASR->>ASR: Result()
            ASR-->>NLP: texto final (segmento)
            NLP->>NLP: parse_command()
            NLP-->>Out: intent + entidades + confiança
        else
            ASR->>ASR: PartialResult()
            ASR-->>NLP: texto parcial (opcional)
        end
    end
```

---

## Diagrama de Atividade: Interpretação de Comandos (NLP)

```mermaid
flowchart TD
    A[Texto reconhecido] --> B[_normalize]
    B --> C{Ação encontrada?}
    C -->|não| D[Fallback de cômodo / ação genérica]
    C -->|sim| E[_is_negated]
    D --> E
    E --> F[_apply_negation]
    F --> G{Dispositivo encontrado?}
    G -->|não| H[Composição genérica possível?]
    H -->|sim| I[monta dispositivo composto]
    H -->|não| J[intent = desconhecido]
    G -->|sim| K[intent = controlar_dispositivo]
    I --> K
    J --> L[_confidence]
    K --> L[_confidence]
    L --> M[retorna intent + entidades + confiança]
```

---

## Diagrama de Estados: Comportamento do Reconhecedor

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Capturando: start_stream()
    Capturando --> Processando: novo chunk
    Processando --> NaoVoz: VAD == false
    Processando --> Reconhecendo: VAD == true
    NaoVoz --> Capturando: próximo chunk
    Reconhecendo --> EmitindoParcial: AcceptWaveform == false
    Reconhecendo --> EmitindoFinal: AcceptWaveform == true
    EmitindoParcial --> Capturando
    EmitindoFinal --> Capturando
```

---

## Comportamento Esperado do Sistema

* Resistência a ruído leve via redução opcional de ruído + normalização + AGC.
* Filtro passa-faixa (80–8000 Hz, quando SciPy disponível).
* VAD evita processar regiões sem voz, reduzindo custos e falsos positivos.
* Vosk deve operar na taxa configurada (`CONFIG["audio"]["samplerate"]`), padrão **16 kHz**.
* `recognize_chunk()` retorna resultado **final do segmento** quando `AcceptWaveform()` é verdadeiro.
* `recognize_stream()` concatena parciais + finais ao longo da fala.
* NLP retorna estrutura:

```json
{
  "intent": "str",
  "entities": {
    "acao": "...",
    "dispositivo": "...",
    "valor": "...?",
    "unidade": "...?"
  },
  "confidence": 0.0
}
```

---

## Requisitos e Setup

* Python 3.8+
* Dependências em `requirements.txt`
* Modelo Vosk em `models/vosk-model-small-pt-0.3/`
  (configurável em `src/core/config.py`)

Instalação:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
./venv/Scripts/activate    # Windows
pip install -r requirements.txt
```

Estrutura mínima:

```
models/
  vosk-model-small-pt-0.3/
src/
  audio/
  core/
  recognition/
  nlp/
```

---

## Execução (exemplo de orquestração)

```python
from src.audio.microphone import AudioInput
from src.audio.recorder import AudioRecorder
from src.audio.preprocessor import AudioPreprocessor
from src.recognition.model_manager import ModelManager
from src.recognition.vosk_recognizer import VoskRecognizer
from src.nlp.nlp import parse_command

audio_in = AudioInput()
pre = AudioPreprocessor()
mm = ModelManager()
model = mm.load_model()
asr = VoskRecognizer(model)

with audio_in.start_stream():
    rec = AudioRecorder(audio_in)

    processed = pre.process_stream_generator(
        (rec.get_next_chunk() for _ in iter(int, 1))
    )

    text = asr.recognize_stream(processed)
    result = parse_command(text)
    print(result)
```

---

## Testes

```bash
python -m pytest -v tests/
```

---

## Notas e Limitações

* Recursos opcionais dependem de: `noisereduce`, `webrtcvad`, `scipy`.
* Se ausentes, há fallback para implementações simplificadas.
* O módulo `output` é apenas um placeholder; a integração real com atuadores depende do hardware embarcado.

---

## Licença

Projeto acadêmico para fins educacionais (todos os direitos reservados, exceto uso acadêmico).

---
