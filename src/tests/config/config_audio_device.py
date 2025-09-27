import sounddevice as sd

def listar_dispositivos_ativos():
    devices = sd.query_devices()
    ativos = []

    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            try:
                with sd.InputStream(device=i, channels=1, samplerate=44100):
                    pass
                ativos.append((i, dev['name'], dev['max_input_channels']))
            except Exception:
                pass

    if not ativos:
        print("Nenhum dispositivo de entrada ativo encontrado.")

    return ativos

if __name__ == "__main__":
    listar_dispositivos_ativos()
