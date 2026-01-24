# BladeRunner - Linear Stage Controller

**BladeRunner** is a high-precision linear stage control system powered by an Arduino firmware and a Python Tkinter GUI. It allows for safe, user-friendly control of a stepper motor-driven linear actuator with adjustable speed and acceleration.

![BladeRunner Icon](gui_app/logo.png)

## Features

- **Precise Control**: Move to absolute positions or jog in relative steps.
- **Dual Icon System**: Distinct high-res orange runner icon for the taskbar and a leaf/feather icon for the window title bar.
- **Safety First**: Non-blocking homing routine, emergency stop, and software travel limits (0-45mm).
- **Adjustable Parameters**: Real-time control of Speed (mm/s) and Acceleration (mm/s²).
- **Robust Communication**: Custom serial protocol with error handling and status feedback.

## Hardware Requirements

- **Microcontroller**: Arduino Uno R4 Minima (or compatible)
- **Driver**: TMC2209 (UART or DIR/STEP mode)
- **Motor**: NEMA 17 Stepper (e.g., StepperOnline 17HS08-1004S)
- **Actuator**: Linear Rail/Stage (45mm travel)

## Installation & Usage

### Method 1: Executable (Recommended for Windows)
No Python installation is required.

1.  Connect your Arduino.
2.  Go to the `dist` folder.
3.  Run **`BladeRunner.exe`**.

### Method 2: Running from Source (Python)
1.  Install **Python 3.x**.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python gui_app/main.py
    ```

### Firmware Setup
1.  Open `firmware/stepper_controller.ino` in Arduino IDE.
2.  Install **AccelStepper** library.
3.  Upload to your Arduino board.

## Usage Guide

1.  **Connect**: Select COM port and click "Connect".
2.  **Home**: Click "HOME AXIS" to calibrate zero position. (Mandatory)
3.  **Move**: Enter position (mm) and click GO, or use Jog buttons.
4.  **Settings**: Adjust speed/acceleration limits on the fly.
5.  **Emergency Stop**: Press the red button to halt immediately.

## Project Structure

```text
Arduino_Linear_Stage/
├── dist/                   # Contains the compiled executable
│   └── BladeRunner.exe     # <--- RUN THIS
├── firmware/
│   └── stepper_controller.ino  # Arduino Firmware
├── gui_app/
│   ├── main.py             # Python Source Code
│   ├── serial_link.py      # Serial Communication Logic
│   ├── app.ico             # Icon for Executable
│   ├── icon.png            # Window Title Icon
│   └── logo.png            # Taskbar Icon
├── BladeRunner.spec        # PyInstaller Spec File
└── README.md               # This file
```

---
**BladeRunner Controller v3.0**
Created by Changhyun Hwang (2026)
