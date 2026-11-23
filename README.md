# Typing Tutor Game

Typing Tutor is a simple Python game. Letters and numbers fall down the screen. Type each one before it reaches the red **Dead Bar**. Each round lasts 60 seconds.

## What you need

- The complete `Game` folder.
- Python 3.12 or newer with Tkinter.
- No extra pip packages or virtual environment are needed.

## Run on macOS

Open Terminal and run these commands. Replace `your-name` with your Mac username, and use the actual location of the `Game` folder:

```bash
cd "/Users/your-name/Desktop/Game"
python3.12 main.py
```

If you use Homebrew Python 3.12 on another Mac and Tkinter is missing, install it first:

```bash
brew install python@3.12 python-tk@3.12
```

## Run on Windows

1. Install Python using the **Windows installer (64-bit)** from [python.org](https://www.python.org/downloads/windows/). Keep **Tcl/Tk support** selected during installation.
2. Copy the complete `Game` folder to the Windows laptop.
3. Open the `Game` folder in File Explorer. Click the address bar, type `cmd`, and press Enter.
4. In the Command Prompt window, run:

```bat
py main.py
```

## How to play

1. Click **Start Game**.
2. Type the letter or number shown on a falling character. Use **Shift** for capital letters.
3. A correct key increases **Hits**. A character that crosses the red Dead Bar increases **Misses**.
4. The round ends after 60 seconds. Click **Restart Game** to play again, or press **Esc** to end a round early.

The side panel shows hits, misses, key presses, accuracy, and the number of characters still on screen.
