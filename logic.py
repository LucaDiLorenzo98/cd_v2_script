import os
import json
import subprocess
import webbrowser
import serial
import time
import ctypes
from serial.tools import list_ports

PORTA_ARDUINO = os.getenv("CONSOLEDECK_PORT", "COM11")
BAUDRATE = int(os.getenv("CONSOLEDECK_BAUDRATE", "9600"))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

# Stato del pulsante selezionato
pulsante_selezionato = None

# Stato interno per VOLUME
last_volume_value = None
is_muted = False

def load_config():
    print(f"[DEBUG] Loading config from: {CONFIG_FILE}")
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            print("[DEBUG] Config loaded:", json.dumps(config, indent=2))
            return config
    else:
        print("[DEBUG] Config file not found, creating default config.")
        config = {}
        for i in range(1, 10):
            config[f"BUTTON_{i}"] = {"type": "none", "value": ""}
        config["BUTTON_1"] = {"type": "link", "value": "https://www.youtube.com"}
        return config

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def esegui_azione(azione):
    tipo = str(azione.get("type", "none")).strip().lower()
    valore_raw = azione.get("value", "")
    valore = valore_raw.strip() if isinstance(valore_raw, str) else str(valore_raw or "").strip()

    print(f"[DEBUG] Azione ricevuta -> type={tipo}, value={valore!r}")

    if tipo == "link" and valore:
        opened = webbrowser.open(valore, new=2)
        if not opened:
            print(f"[WARN] Il browser non ha gestito il link: {valore}")
    elif tipo == "exe" and valore:
        try:
            if os.name == "nt":
                if os.path.exists(valore):
                    os.startfile(valore)
                else:
                    # Supporta anche comandi shell (es. start applemusic)
                    subprocess.Popen(valore, shell=True)
            else:
                subprocess.Popen([valore])
        except Exception as e:
            print("Errore aprendo eseguibile:", e)
    elif tipo == "start" and valore:
        try:
            subprocess.Popen(valore, shell=True)
        except Exception as e:
            print("Errore eseguendo comando start:", e)
    else:
        print("Nessuna azione definita")

def ascolta_seriale(config):
    while True:
        try:
            print(f"[DEBUG] Tentativo connessione seriale: {PORTA_ARDUINO} @ {BAUDRATE}")
            with serial.Serial(PORTA_ARDUINO, BAUDRATE, timeout=1) as ser:
                print(f"Connesso a {PORTA_ARDUINO}")
                while True:
                    linea = ser.readline().decode('utf-8', errors='ignore').strip()
                    if not linea:
                        continue

                    print("Ricevuto:", linea)
                    comando = linea.upper()

                    try:
                        if comando.startswith("VOLUME_"):
                            valore = comando.replace("VOLUME_", "", 1)
                            gestisci_volume(valore)
                        elif comando == "MUTE":
                            gestisci_mute()
                        elif comando == "MEDIA":
                            gestisci_media()
                        elif comando in config:
                            esegui_azione(config[comando])
                        else:
                            print(f"[DEBUG] Comando seriale non riconosciuto: {linea}")
                    except Exception as cmd_error:
                        print(f"[ERRORE] Gestione comando '{linea}': {cmd_error}")
        except Exception as e:
            print(f"[ERRORE] Porta seriale {PORTA_ARDUINO}: {e}")
            porte = [p.device for p in list_ports.comports()]
            if porte:
                print(f"[DEBUG] Porte disponibili: {', '.join(porte)}")
            else:
                print("[DEBUG] Nessuna porta seriale rilevata")
            time.sleep(5)

def simulate_keypress(vk_code):
    if os.name != "nt":
        print("[WARN] I media key sono supportati solo su Windows")
        return

    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    try:
        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
    except Exception as e:
        print(f"[ERRORE] Invio keypress VK {vk_code}: {e}")

def gestisci_volume(value):
    global last_volume_value
    try:
        valore = int(value)
        if last_volume_value is None:
            last_volume_value = valore
            print(f"[DEBUG] Volume baseline impostata a {valore}")
            return

        delta = valore - last_volume_value
        if delta != 0:
            vk = 0xAF if delta > 0 else 0xAE  # VK_VOLUME_UP / VK_VOLUME_DOWN
            # Evita burst troppo grandi al primo aggiornamento o dopo riconnessioni.
            step_count = min(abs(delta), 8)
            for _ in range(step_count):
                simulate_keypress(vk)
            if step_count != abs(delta):
                print(f"[DEBUG] Delta volume {delta} limitato a {step_count} step")
            print(f"[DEBUG] Volume adjusted by {delta}")
        last_volume_value = valore
    except ValueError:
        print("[ERROR] Invalid volume value:", value)

def gestisci_mute():
    global is_muted
    simulate_keypress(0xAD)  # VK_VOLUME_MUTE
    is_muted = not is_muted
    print(f"[DEBUG] Mute toggled -> {'ON' if is_muted else 'OFF'}")

def gestisci_media():
    simulate_keypress(0xB3)  # VK_MEDIA_PLAY_PAUSE
    print("[DEBUG] Media play/pause triggered")

def seleziona_pulsante(btn):
    global pulsante_selezionato
    pulsante_selezionato = btn
    print(f"[DEBUG] Pulsante selezionato: {btn}")

def deseleziona_pulsante():
    global pulsante_selezionato
    pulsante_selezionato = None    

def get_pulsante_selezionato():
    return pulsante_selezionato