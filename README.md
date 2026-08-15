# Coding Time Tracker Python

A simple Python background tool that tracks the amount of time you spend programming each day.

The script monitors the active Windows application and starts counting time when you are working in your IDE. For example, when `pycharm64.exe` is the active application, the timer starts counting your programming time.

The timer stops when you switch to another application or stop interacting with the IDE. It also includes a built-in **10-minute idle-time limit**. If there is no user input for 10 minutes, the timer stops counting. This means that the tool tracks your **actual active programming time**, rather than simply measuring how long your IDE is open.

## Features

* Tracks active programming/coding time.
* Detects the currently active Windows application.
* Built-in idle-time detection.
* Saves coding data locally.
* Sends coding statistics to the **Pixela API**.
* Periodically saves data both locally and online.
* Detects when the IDE is closed and saves the accumulated data.
* Error handling for HTTPS/API requests.
* Error handling for PID/process-related operations.
* Error handling when creating and retrieving local files.
* Can run directly from Python or as a standalone `.exe`.
* Runs in the background without a user interface.

## Pixela

The project uses the **Pixela API**, which allows you to track your programming activity day by day and visualize your coding time.

You will need to create your own Pixela account and configure your own project/graph before using the online tracking functionality.

## Running as a `.exe`

The script is ready to run both from an IDE and as a standalone executable. I recommend running it as an `.exe` and configuring it to start automatically with Windows.

### 1. Create the `.exe`

Install PyInstaller if you haven't already and run the following command from your PyCharm terminal, inside the directory containing your Python file:

```bash
pyinstaller --onefile --noconsole .\<name_of_file>.py
```

After the process finishes, the executable will be located inside the `dist` folder.

### 2. Run it automatically with Windows

Create a shortcut of the generated `.exe`.

Then:

1. Press `Win + R`.
2. Type:

```text
shell:startup
```

3. Press Enter.
4. Place the shortcut inside the Startup folder.

The program will now start automatically when you log in to Windows.

## Configuration

Currently, the script supports **PyCharm,VS Code,Visual Studio,IntelliJ IDEA** as the target IDE.

You can easily modify the code to support another IDE, such as Android Studio Code, by changing the corresponding process name (for example, `studio64.exe`).

## VERY IMPORTANT

For those who download for the first time the win32gui win32process **DO NOT** try to pip install win32gui. You need to install **pywin32** via **pip install pywin32**. This will take care both  win32gui and win32process.

## Notes

This is a simple personal tool and currently does not include a graphical user interface. It is designed to work quietly in the background without distracting the user.

This is one of my first useful Python tools that I have built for my own daily programming routine. I am continuing to learn Python and plan to expand the project with additional features in the future.
