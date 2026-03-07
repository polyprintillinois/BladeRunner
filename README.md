# BladeRunner - Linear Stage Controller

**BladeRunner** is a high-precision linear stage control system powered by Arduino firmware and a Python Tkinter GUI. It provides safe, user-friendly control of a stepper-driven linear actuator with adjustable speed and acceleration.

![BladeRunner Icon](gui_app/logo.png)

## Documentation

- [Hardware Assembly Guide](docs/hardware-assembly-guide.md)
- [Implementation Guide](docs/implementation-guide.md)

To assemble, wire, and operate the system from scratch, use the Hardware Assembly Guide and Implementation Guide together.

## Features

- **Precise Control**: Move to absolute positions or jog in relative steps.
- **Reliable Operation**: Blocking homing routine, emergency stop, and software travel limits from 0 to 45 mm.
- **Adjustable Parameters**: Real-time control of speed (mm/s) and acceleration (mm/s^2).
- **Robust Communication**: Custom serial protocol with error handling and status feedback.

## Hardware Requirements

- **Microcontroller**: Arduino Uno R4 Minima
- **Driver**: Adafruit TMC2209 breakout in DIR/STEP mode
- **Motor**: NEMA 17 stepper motor (for example, StepperOnline 17HS08-1004S)
- **Actuator**: Linear rail/stage with 45 mm travel

## Limitations and Safety

- **Travel Limit**: The controller enforces a 45 mm software travel limit. Ensure the physical stage matches this usable range.
- **Homing Requirement**: The system must be homed after connecting before motion commands are enabled.
- **Blocking Homing**: The homing sequence blocks on the Arduino side until the limit switch is hit or the 20-second timeout expires. Emergency stop is still checked during this routine.
- **Emergency Stop**: Pressing the E-stop halts the motor immediately and puts the system in a stopped state. Re-home before resuming motion.
- **Speed and Acceleration Limits**: The GUI caps speed at 30 mm/s and acceleration at 1000 mm/s^2 to reduce the chance of stalls or mechanical damage.

## Installation and Usage

### Method 1: Executable

No Python installation is required.

1. Go to the **[Releases](../../releases)** page of this repository.
2. Download the latest `BladeRunner.exe` from the Assets section.
3. Connect the Arduino over USB and run the executable.

### Method 2: Run from Source

1. Install Python 3.x.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python gui_app/main.py
```

### Firmware Setup

1. Open `firmware/stepper_controller/stepper_controller.ino` in Arduino IDE.
2. Install the `AccelStepper` library.
3. Upload the firmware to the Arduino board.

## Usage Guide

1. **Connect**: Select a COM port and click `Connect`.
2. **Home**: Click `HOME AXIS (Required)` to establish the zero position.
3. **Move**: Enter a target position in millimeters and click `GO`, or use the jog buttons.
4. **Set Parameters**: Adjust speed and acceleration as needed.
5. **Emergency Stop**: Press `EMERGENCY STOP` to halt motion immediately.

## Project Structure

```text
BladeRunner/
|-- dist/                        # Compiled executable output
|   `-- BladeRunner.exe
|-- firmware/
|   `-- stepper_controller/
|       `-- stepper_controller.ino
|-- docs/
|   |-- README.md
|   |-- hardware-assembly-guide.md
|   `-- implementation-guide.md
|-- gui_app/
|   |-- main.py                  # Tkinter application
|   |-- serial_link.py           # Serial communication layer
|   |-- app.ico                  # Executable icon
|   |-- icon.png                 # Window icon
|   `-- logo.png                 # App logo
|-- parts/                       # 3D-printed mechanical parts
|-- BladeRunner.spec             # PyInstaller spec file
`-- README.md
```

---
**BladeRunner Controller v1.0.1**  
Created by Changhyun Hwang (2026)
