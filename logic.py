import os
import json
import subprocess
import webbrowser
import serial
import serial.tools.list_ports
import time
import ctypes

BAUDRATE = 9600

ARDUINO_KEYWORDS = ["arduino", "ch340", "ch341", "ftdi", "usb serial", "usb-serial"]

def trova_porta_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()
        if any(kw in description or kw in manufacturer for kw in ARDUINO_KEYWORDS):
            print(f"[DEBUG] Arduino found on {port.device}: {port.description}")
            return port.device
    if ports:
        print(f"[DEBUG] No Arduino signature found, defaulting to first port: {ports[0].device}")
        return ports[0].device
    print("[ERROR] No serial ports found.")
    return None

PORTA_ARDUINO = trova_porta_arduino()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

# Stato del pulsante selezionato
pulsante_selezionato = None

# Stato interno per VOLUME
last_volume_value = 0
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
    if azione["type"] == "link" and azione["value"]:
        webbrowser.open(azione["value"])
    elif azione["type"] == "exe" and azione["value"]:
        try:
            subprocess.Popen(azione["value"])
        except Exception as e:
            print("Errore aprendo eseguibile:", e)
    else:
        print("Nessuna azione definita")

def ascolta_seriale(config):
    try:
        with serial.Serial(PORTA_ARDUINO, BAUDRATE, timeout=1) as ser:
            print(f"Connesso a {PORTA_ARDUINO}")
            while True:
                linea = ser.readline().decode('utf-8').strip()
                if linea:
                    print("Ricevuto:", linea)
                    if linea.startswith("VOLUME_"):
                        valore = linea.replace("VOLUME_", "")
                        gestisci_volume(valore)
                    elif linea == "MUTE":
                        gestisci_mute()
                    elif linea == "MEDIA":
                        gestisci_media()
                    elif linea in config:
                        esegui_azione(config[linea])
    except Exception as e:
        print(f"[ERRORE] Porta seriale: {e}")
        time.sleep(5)
        ascolta_seriale(config)

def simulate_keypress(vk_code):
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)

def gestisci_volume(value):
    global last_volume_value
    try:
        valore = int(value)
        delta = valore - last_volume_value
        if delta != 0:
            vk = 0xAF if delta > 0 else 0xAE  # VK_VOLUME_UP / VK_VOLUME_DOWN
            for _ in range(abs(delta)):
                simulate_keypress(vk)
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
    print(f"[DEBUG] Pulsante selezionato: BUTTON_{btn}")

def deseleziona_pulsante():
    global pulsante_selezionato
    pulsante_selezionato = None    

def get_pulsante_selezionato():
    return pulsante_selezionato
