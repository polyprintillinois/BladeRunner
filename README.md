# BladeRunner - Linear Stage Controller

This repository accompanies **Hwang, Elangovan, Damron, Kwok, Jeon & Diao, "Democratizing Lab Automation through Multi-Agent-Assisted Design and 3D Printing"** (submitted, 2026). Archived release: [Zenodo DOI 10.5281/zenodo.22695750](https://doi.org/10.5281/zenodo.22695750). Code is released under the MIT licence; printed-part designs (STL) and documentation may be reused under the same terms with attribution.

**BladeRunner** is a high-precision linear stage control system powered by Arduino firmware and a Python Tkinter GUI. It provides safe, user-friendly control of a stepper-driven linear actuator with adjustable speed and acceleration.

![BladeRunner Icon](gui_app/logo.png)

## Documentation

- [Hardware Assembly Guide](docs/hardware-assembly-guide.md)
- [Implementation Guide](docs/implementation-guide.md)

To assemble, wire, and operate the system from scratch, use the Hardware Assembly Guide and Implementation Guide together.

## Features

- **Precise Control**: Move to absolute positions or jog in relative steps.
- **Reliable Operation**: Blocking homing routine, software stop (decelerated via `AccelStepper.stop()`), and software travel limits from 0 to 45 mm.
- **Adjustable Parameters**: Real-time control of speed (mm/s) and acceleration (mm/s^2).
- **Robust Communication**: Custom serial protocol with error handling and status feedback.

## Hardware Requirements

- **Microcontroller**: Arduino Uno R4 Minima
- **Driver**: Adafruit TMC2209 breakout in DIR/STEP mode
- **Motor**: NEMA 17 stepper motor (for example, StepperOnline 17HS08-1004S)
- **Actuator**: Linear rail/stage with 45 mm travel

## Safety

- The stage is driven by a 12 V supply. Disconnect power before wiring or swapping stepper leads.
- The carriage moves at up to 30 mm/s and can pinch fingers against the end stops; keep hands clear during homing and moves. The **EMERGENCY STOP** button performs a decelerated software stop via `AccelStepper.stop()`—it is not a hardware emergency stop.
- The blade is a thin glass or silicon piece with a sharp edge; handle it with tweezers.
- When printing with solvents (for example, chlorobenzene), operate inside a fume hood or with adequate ventilation. The 3D-printed PLA parts are not solvent-resistant and should be kept dry.

## Operating Constraints

- **Travel Limit**: The controller enforces a 45 mm software travel limit. Ensure the physical stage matches this usable range.
- **Homing Requirement**: The system must be homed after connecting before motion commands are enabled.
- **Blocking Homing**: The homing sequence blocks on the Arduino side until the limit switch is hit or the 20-second timeout expires. The software-stop command is still checked during this routine.
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

## First Run (Hello World)

A minimal test that confirms the stage, firmware, and GUI are working takes about five minutes.

1. Flash `firmware/stepper_controller/stepper_controller.ino` to the Arduino Uno R4 Minima and connect it over USB. Connect the 12 V supply to the TMC2209 driver **last**.
2. Launch the GUI (`BladeRunner.exe` from the [Releases](../../releases) page, or `python gui_app/main.py`), select the Arduino's COM port, and click `Connect`. The button should change to `Disconnect`, and the status should read `CONNECTED` or `READY` after board startup.
3. Click `HOME AXIS (Required)` and confirm the prompt. The carriage should travel toward the limit switch, back off by approximately 2 mm, report `HOMED`, and reset the displayed position to `0.000 mm`.
4. Enter `20` in `Go To (mm)` and click `GO`; then enter `0` and click `GO` again. Confirm that the position display returns to `0.000 mm`. The specified unidirectional repeatability is ±6.3 µm.
5. Optional wet test: mount a glass slide, load approximately 10 µL of water under the blade, set the speed to `1 mm/s`, click `Set`, and run one 20 mm move. A continuous wetted track indicates the expected blade-substrate gap (approximately 100 µm with the printed holder).

If step 3 or 4 fails, disconnect the 12 V supply before checking the stepper wiring (see the [Hardware Assembly Guide](docs/hardware-assembly-guide.md)). If the carriage moves away from the switch during homing, reversing one coil pair reverses the motor direction; if the motor only vibrates, verify the coil-pair identification.

## Usage Guide

1. **Connect**: Select a COM port and click `Connect`.
2. **Home**: Click `HOME AXIS (Required)` to establish the zero position.
3. **Move**: Enter a target position in millimeters and click `GO`, or use the jog buttons.
4. **Set Parameters**: Adjust speed and acceleration as needed.
5. **Software Stop**: Press `EMERGENCY STOP` to request a decelerated software stop via `AccelStepper.stop()`.

## Project Structure

```text
BladeRunner/
|-- .zenodo.json                # Zenodo archive metadata
|-- LICENSE                     # MIT license
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

## License

BladeRunner is released under the [MIT License](LICENSE).

---
**BladeRunner Controller v1.0.2**<br>
Created by Changhyun Hwang (2026)
