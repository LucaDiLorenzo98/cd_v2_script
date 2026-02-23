import argparse
from logic import load_config, save_config, ascolta_seriale, seleziona_pulsante, get_pulsante_selezionato, deseleziona_pulsante
from gui import init_pygame, disegna_pulsanti, trova_pulsante_click
import pygame
import pyperclip

import gui

def main(gui_mode):
    config = load_config()

    if gui_mode:
        init_pygame()
        pygame.key.set_repeat(300, 30)
    
        running = True
        while running:
            selezionato = get_pulsante_selezionato()
            disegna_pulsanti(config, selezionato)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    selezionato = get_pulsante_selezionato()
                    click_consumed = False

                    # Click dentro il campo input URL
                    if selezionato and gui.input_rect and gui.input_rect.collidepoint(mx, my):
                        gui.input_active = True
                        click_consumed = True
                    else:
                        gui.input_active = False

                    # Click su "Cancel"
                    if selezionato and gui.cancel_button_rect and gui.cancel_button_rect.collidepoint(mx, my):
                        gui.temp_config_type = None
                        gui.temp_config_value = None
                        gui.save_enabled = False
                        gui.save_clicked = False
                        gui.input_active = False
                        deseleziona_pulsante()
                        click_consumed = True
                    
                    # Click su "Save"
                    if (
                        not click_consumed
                        and selezionato
                        and hasattr(gui, "save_button_rect")
                        and gui.save_button_rect
                        and gui.save_button_rect.collidepoint(mx, my)
                    ):
                        current = config.get(selezionato, {"type": "none", "value": ""})
                        new_type = gui.temp_config_type if gui.temp_config_type is not None else current.get("type", "none")
                        new_value = gui.temp_config_value if gui.temp_config_value is not None else current.get("value", "")
                        if new_type == "none":
                            new_value = ""
                        config[selezionato] = {
                            "type": new_type,
                            "value": new_value
                        }
                        gui.temp_config_type = None
                        gui.temp_config_value = None
                        gui.save_enabled = False
                        gui.save_clicked = True
                        save_config(config)
                        gui.save_clicked = False

                    # Click su uno dei 3 pulsanti esclusivi (LINK, EXE, NONE)
                    if not click_consumed and selezionato and hasattr(gui, "tipo_button_rects"):
                        for nome, rect in gui.tipo_button_rects.items():
                            if rect.collidepoint(mx, my):
                                tipo = nome.lower()
                                gui.temp_config_type = tipo

                                if tipo == "none":
                                    gui.temp_config_value = ""
                                else:
                                    if gui.temp_config_value is None:
                                        gui.temp_config_value = config[selezionato].get("value", "")

                                gui.save_enabled = gui.is_dirty(selezionato, config)
                                click_consumed = True
                                break
                            
                    # Click su "Browse"
                    current_type = gui.temp_config_type or (config.get(selezionato, {}).get("type") if selezionato else None)
                    if (
                        not click_consumed
                        and selezionato
                        and current_type == "exe"
                        and hasattr(gui, "browse_button_rect")
                        and gui.browse_button_rect
                        and gui.browse_button_rect.collidepoint(mx, my)
                    ):
                            from tkinter import filedialog
                            import tkinter as tk
                            import os

                            root = tk.Tk()
                            root.withdraw()  # Nasconde la finestra principale
                            path = filedialog.askopenfilename(
                                title="Select Executable",
                                filetypes=[("Executable files", "*.exe")],
                                initialdir=os.path.expanduser("~")
                            )
                            if path:
                                gui.temp_config_value = path
                                gui.save_enabled = gui.is_dirty(selezionato, config)
                            root.destroy()
                            click_consumed = True

                    if click_consumed:
                        continue

                    # Click su uno dei pulsanti 1-9
                    btn = trova_pulsante_click(mx, my)
                    if btn:
                        seleziona_pulsante(btn)
                        gui.temp_config_type = None
                        gui.temp_config_value = None
                        gui.save_enabled = False
                        gui.save_clicked = False
                        gui.input_active = False
                
                # Gestione del campo di testo per l'input URL
                elif event.type == pygame.KEYDOWN and gui.input_active:
                    selezionato = get_pulsante_selezionato()
                    if not selezionato:
                        gui.input_active = False
                        continue

                    active_type = gui.temp_config_type if gui.temp_config_type is not None else config[selezionato].get("type", "none")
                    if active_type != "link":
                        gui.input_active = False
                        continue

                    if event.key == pygame.K_BACKSPACE:
                        gui.temp_config_value = (gui.temp_config_value or "")[:-1]
                    elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        # Ctrl+V: incolla dagli appunti
                        clipboard_text = pyperclip.paste()
                        if clipboard_text:
                            gui.temp_config_value = (gui.temp_config_value or "") + clipboard_text
                    elif event.key == pygame.K_a and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        # Ctrl+A → Seleziona tutto (simbolico, nessuna azione visiva)
                        pass  # niente da fare qui (è tutto già "selezionato")

                    elif event.key == pygame.K_c and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        # Ctrl+C → Copia tutto il campo
                        if gui.temp_config_value:
                            pyperclip.copy(gui.temp_config_value)

                    elif event.key == pygame.K_x and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        # Ctrl+X → Taglia tutto
                        if gui.temp_config_value:
                            pyperclip.copy(gui.temp_config_value)
                            gui.temp_config_value = ""
                            gui.save_enabled = gui.is_dirty(selezionato, config)        
                    else:
                        char = event.unicode
                        if char.isprintable():
                            gui.temp_config_value = (gui.temp_config_value or "") + char

                    gui.save_enabled = gui.is_dirty(selezionato, config)

        pygame.quit()
    else:
        ascolta_seriale(config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', action='store_true', help="Avvia la GUI di configurazione")
    args = parser.parse_args()
    main(args.gui)
