# 🎮 ConsoleDeck

ConsoleDeck is a simple graphical interface that allows you to configure up to 9 buttons to launch websites or executable files with a click.  
Ideal for creating your own customizable macro deck or personal launcher.

---

## ✅ Requirements

- A Windows PC
- Python 3.11 or higher
- Internet connection (only for the initial setup)

---

## 🐍 Step 1 – Install Python

1. Go to 👉 [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest version of Python 3
3. During installation, **check the box** ✅ **"Add Python to PATH"**
4. Click **Install Now**

---

## 📦 Step 2 – Install required libraries

1. Open the Start menu
2. Type `cmd` and press Enter
3. In the terminal window, paste the following command:

```bash
pip install pygame-ce pyperclip pyserial
```

(or, from inside the project folder: `pip install -r requirements.txt`)

> ℹ️ This uses **pygame-ce**, a maintained drop-in replacement for `pygame`. The original `pygame` package has no installer for the newest Python versions (e.g. 3.15), so `pip install pygame` tries to compile it and fails with errors like `No module named 'distutils.msvccompiler'`. If you already installed `pygame`, remove it first with `pip uninstall pygame`; the two cannot be installed together.

If you get an error like `'pip' is not recognized`, try restarting your PC.

---

## ▶️ Step 3 – Program your buttons

1. Download all project files into a folder (e.g., Desktop)
2. Double-click `consoledeck.bat`, or open that folder in the terminal (`cmd`) and run:

```bash
python main.py --gui
```

If everything is set up correctly, a graphical window will open. Program your buttons and click **Save**, then close the window.

---

## 🎛️ Step 4 – Use the deck

1. Plug in the ConsoleDeck (Arduino) over USB
2. Double-click `avvio_consoledeck.bat`, or run:

```bash
python main.py
```

The terminal should print `Connesso a COM…` ("Connected to COM…"). Leave this window open: it listens to the deck and performs each button's action. If you change your buttons in the GUI later, close this window and start it again so it picks up the new settings.

---

## ⚙️ Features

- Click one of the 9 buttons to assign an action
- Choose between:
  - a website URL (e.g. `https://youtube.com`)
  - a `.exe` file on your PC
  - a keyboard macro, either a preset:
    - `CTRL+C` – copy
    - `CTRL+V` – paste
    - `SNIP` – `Win+Shift+S`, select an area to screenshot (copied to clipboard)
    - `SCREENSHOT` – `Win+PrtScn`, full-screen screenshot saved to `Pictures\Screenshots`
  - or any key combination typed in the box, keys joined with `+` (e.g. `ctrl+z`, `alt+tab`, `ctrl+shift+esc`, `win+d`)
    - Modifiers: `ctrl`, `shift`, `alt`, `win`
    - Keys: `a`–`z`, `0`–`9`, `f1`–`f24`, `enter`, `esc`, `tab`, `space`, `backspace`, `delete`, `insert`, `home`, `end`, `pageup`, `pagedown`, `up`, `down`, `left`, `right`, `printscreen`
    - Symbols: `plus`, `minus`, `,` `.` `/` `;` `'` `[` `]` `\` `` ` ``
  - or no action
- Modify the fields directly inside the app
- Use the "Browse" button to select `.exe` files
- Save your changes only when you're ready
- Supports volume control, mute toggle, and media play/pause via serial

Settings are stored in a local file called `config.json`.

---

## ❓ Troubleshooting

**🟡 Nothing happens when I click a button?**  
Make sure you launched the app using: `python main.py --gui`

**🎛️ Nothing happens when I press a button on the deck?**  
The deck only works while `python main.py` (without `--gui`) is running; see Step 4. If it prints `[ERRORE] Porta seriale`, make sure the deck is plugged in and that nothing else is using its port (for example, close the Arduino IDE's Serial Monitor).

**🔗 Can I use YouTube or other links?**  
Yes, any valid `https://` link will work.

**🧩 Can I assign programs like `.exe` files?**  
Yes! Use the “Browse” button to pick an executable file.

**⌨️ Where do keyboard macros go?**  
Macros are sent to whichever window currently has focus, just like pressing the keys yourself. Click into the app you want to copy from / paste into before pressing the deck button.

**💾 It says 'pip' is not recognized**  
Restart your computer or reinstall Python and ensure "Add Python to PATH" is selected during setup.

---

## 🧼 How to uninstall

- You can delete the project folder at any time
- To uninstall Python, go to **Apps & Features** in Windows

---

## 📬 Need help?

If you get stuck or the app doesn’t behave as expected, feel free to contact the developer or open an issue on the project repository.
