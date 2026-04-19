import pygame
import os
import tkinter as tk
from tkinter import simpledialog, filedialog
import webbrowser
from logic import esegui_azione

# Costanti globali
FONT = None
SMALL_FONT = None
SCREEN = None

BTN_SIZE = 100
SPACING_X = 140
SPACING_Y = 120
MARGIN_Y = 20
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 650

cancel_button_rect = None
browse_button_rect = None
save_button_rect = None
tipo_button_rects = {}

temp_config_type = None
temp_config_value = None

save_enabled = False
save_clicked = False

input_active = False
input_rect = None

def init_pygame():
    global FONT, SMALL_FONT, SCREEN
    pygame.init()
    FONT = pygame.font.SysFont(None, 24)
    SMALL_FONT = pygame.font.SysFont(None, 16)
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ConsoleDeck V2")


def disegna_pulsanti(config, selezionato=None):
    SCREEN.fill((30, 30, 30))

    btn_size = 100
    spacing_x = 140
    spacing_y = 120
    total_width = 3 * btn_size + 2 * (spacing_x - btn_size)
    start_x = (640 - total_width) // 2
    margin_y = 20

    for i in range(9):
        key = f"BUTTON_{i+1}"
        x = start_x + (i % 3) * spacing_x
        y = margin_y + (i // 3) * spacing_y

        # Sfondo pulsante
        pygame.draw.rect(SCREEN, (50, 50, 50), (x, y, btn_size, btn_size), border_radius=8)

        # Bordi
        if selezionato == key:
            border_color = (200, 120, 40)
        else:
            border_color = (200, 200, 200) 

        pygame.draw.rect(SCREEN, border_color, (x, y, btn_size, btn_size), width=3, border_radius=8)

        # Numero centrale
        num_text = FONT.render(str(i+1), True, (255, 255, 255))
        num_x = x + (btn_size - num_text.get_width()) // 2
        num_y = y + (btn_size - num_text.get_height()) // 2
        SCREEN.blit(num_text, (num_x, num_y))

    linea_y = margin_y + 3 * spacing_y + 5
    pygame.draw.line(SCREEN, (180, 180, 180), (start_x, linea_y), (start_x + total_width, linea_y), 2)

    font_18 = pygame.font.SysFont(None, 18)

    if selezionato:
        testo = f"Program button {selezionato[-1]}"
    else:
        testo = "Click on a button to program it"

    testo_render = font_18.render(testo, True, (255, 255, 255))
    area_testo_y = linea_y + 10
    area_testo_height = btn_size

    testo_x = (640 - testo_render.get_width()) // 2
    testo_y = area_testo_y + (area_testo_height - testo_render.get_height()) // 2

    SCREEN.blit(testo_render, (testo_x, testo_y))

    if selezionato:
        disegna_configuratore_avanzato(selezionato, config)

    pygame.display.flip()

def disegna_configuratore_avanzato(selezionato, config):
    # Globals used for click detection in the main loop
    global tipo_button_rects, cancel_button_rect, input_rect, browse_button_rect, save_button_rect
    small_font = pygame.font.SysFont(None, 16)

    data = config.get(selezionato, {"type": "none", "value": ""})

    global temp_config_type, temp_config_value

    tipo = temp_config_type if temp_config_type is not None else data.get("type", "none")
    valore = temp_config_value if temp_config_value is not None else data.get("value", "")

    opzioni = ["LINK", "START", "EXE", "NONE"]
    base_y = 460
    btn_width = 120
    btn_height = 40
    spazio = 20
    total_width = len(opzioni) * btn_width + (len(opzioni) - 1) * spazio
    start_x = (SCREEN_WIDTH - total_width) // 2
    tipo_button_rects = {}
    input_rect = None
    browse_button_rect = None

    for i, nome in enumerate(opzioni):
        x = start_x + i * (btn_width + spazio)
        y = base_y
        attivo = (nome.lower() == tipo)
        colore = (200, 120, 40) if attivo else (80, 80, 80)

        rect = pygame.Rect(x, y, btn_width, btn_height)
        tipo_button_rects[nome] = rect

        pygame.draw.rect(SCREEN, colore, rect, border_radius=6)
        testo = small_font.render(nome, True, (255, 255, 255))
        SCREEN.blit(testo, testo.get_rect(center=rect.center))

    base_y += btn_height + 15

    if tipo == "link":
        label = small_font.render("ENTER URL:", True, (200, 200, 200))
        SCREEN.blit(label, (50, base_y))

        base_y += label.get_height() + 5

        input_rect = pygame.Rect(50, base_y, 540, 30)
        pygame.draw.rect(SCREEN, (255, 255, 255), input_rect, border_radius=4)

        colore_testo = (0, 0, 0)
        testo_url = valore if valore else ""
        render_text = small_font.render(testo_url, True, colore_testo)
        SCREEN.blit(render_text, (input_rect.x + 5, input_rect.y + 7))

        base_y += 40

    elif tipo == "start":
        label = small_font.render("ENTER TARGET FOR START:", True, (200, 200, 200))
        SCREEN.blit(label, (50, base_y))

        base_y += label.get_height() + 5

        input_rect = pygame.Rect(50, base_y, 540, 30)
        pygame.draw.rect(SCREEN, (255, 255, 255), input_rect, border_radius=4)

        colore_testo = (0, 0, 0)
        testo_cmd = valore if valore else ""
        render_text = small_font.render(testo_cmd, True, colore_testo)
        SCREEN.blit(render_text, (input_rect.x + 5, input_rect.y + 7))

        base_y += 40

    elif tipo == "exe":
        label = small_font.render("SELECT EXECUTABLE FILE:", True, (200, 200, 200))
        SCREEN.blit(label, (50, base_y))

        base_y += label.get_height() + 5
        browse_rect = pygame.Rect(50, base_y, 100, 30)
        pygame.draw.rect(SCREEN, (200, 120, 40), browse_rect, border_radius=5)
        btn_text = small_font.render("BROWSE", True, (255, 255, 255))
        SCREEN.blit(btn_text, btn_text.get_rect(center=browse_rect.center))
        browse_button_rect = browse_rect
        
        base_y += 40


    # Bottoni Cancel e Save (solo layout, azioni altrove)
    button_y = base_y + 20
    total_button_width = 80 + 20 + 80
    start_x = (SCREEN_WIDTH - total_button_width) // 2

    cancel_text = small_font.render("Cancel", True, (200, 120, 40))
    cancel_rect = cancel_text.get_rect()
    SCREEN.blit(cancel_text, (start_x, button_y + (30 - cancel_rect.height) // 2))
    cancel_button_rect = pygame.Rect(start_x, button_y, 60, 30)

    save_rect = pygame.Rect(start_x + 100, button_y, 80, 30)

    if save_clicked:
        colore_save = (200, 120, 40)  # arancione standard (dopo clic)
    elif save_enabled:
        colore_save = (200, 120, 40)  # arancione scuro (modificato)
    else:
        colore_save = (100, 100, 100)  # disabilitato

    pygame.draw.rect(SCREEN, colore_save, save_rect, border_radius=5)

    save_text = small_font.render("Save", True, (255, 255, 255))
    text_rect = save_text.get_rect(center=save_rect.center)
    SCREEN.blit(save_text, text_rect)

    # salva area cliccabile globale
    global save_button_rect
    save_button_rect = save_rect


def is_dirty(selezionato, config):
    global temp_config_type, temp_config_value
    if not selezionato:
        return False

    current = config.get(selezionato, {"type": "none", "value": ""})
    tipo = temp_config_type if temp_config_type is not None else current["type"]
    valore = temp_config_value if temp_config_value is not None else current["value"]

    return tipo != current["type"] or valore != current["value"]


def trova_pulsante_click(mx, my):
    total_width = 3 * BTN_SIZE + 2 * (SPACING_X - BTN_SIZE)
    start_x = (SCREEN_WIDTH - total_width) // 2

    for i in range(9):
        x = start_x + (i % 3) * SPACING_X
        y = MARGIN_Y + (i // 3) * SPACING_Y
        if x <= mx <= x + BTN_SIZE and y <= my <= y + BTN_SIZE:
            return f"BUTTON_{i+1}"
    return None


def config_pulsante(button_key, config):
    root = tk.Tk()
    root.title(f"Configura {button_key}")

    scelta_var = tk.StringVar(root)
    scelta_var.set(config[button_key]["type"])

    valore_var = tk.StringVar(root)
    valore_var.set(config[button_key].get("value", ""))

    def aggiorna_valore_widget(tipo):
        for widget in root.pack_slaves():
            if getattr(widget, "is_value_widget", False):
                widget.destroy()

        if tipo == "link":
            tk.Label(root, text="Inserisci URL:").pack()
            entry = tk.Entry(root, width=50, textvariable=valore_var)
            entry.pack()
            entry.is_value_widget = True

            tk.Button(root, text="Testa Azione", command=lambda: webbrowser.open(valore_var.get())).pack()
            tk.Button(root, text="Salva", command=salva).pack()

        elif tipo == "exe":
            def apri_file():
                path = filedialog.askopenfilename(title="Seleziona file eseguibile")
                if path:
                    valore_var.set(path)

            tk.Button(root, text="Scegli file .exe", command=apri_file).pack()
            lbl_file = tk.Label(root, textvariable=valore_var)
            lbl_file.pack()
            lbl_file.is_value_widget = True

            tk.Button(root, text="Testa Azione", command=lambda: esegui_azione({"type": "exe", "value": valore_var.get()})).pack()
            tk.Button(root, text="Salva", command=salva).pack()

    def salva():
        tipo = scelta_var.get()
        val = valore_var.get()
        config[button_key] = {"type": tipo, "value": val} if tipo != "none" else {"type": "none", "value": ""}
        root.destroy()

    tk.Label(root, text="Seleziona tipo azione:").pack()
    tk.OptionMenu(root, scelta_var, "link", "exe", "none", command=aggiorna_valore_widget).pack()
    aggiorna_valore_widget(scelta_var.get())

    root.mainloop()
