# Implementation Guide

## Overview

BladeRunner is split into two main software components:

- Arduino firmware in [firmware/stepper_controller/stepper_controller.ino](C:/Users/chwang12/PycharmProjects/BladeRunner/firmware/stepper_controller/stepper_controller.ino)
- Python Tkinter GUI in [gui_app/main.py](C:/Users/chwang12/PycharmProjects/BladeRunner/gui_app/main.py)

Serial communication is implemented in [gui_app/serial_link.py](C:/Users/chwang12/PycharmProjects/BladeRunner/gui_app/serial_link.py).

## Repository Layout

| Path | Role |
| --- | --- |
| `firmware/stepper_controller/stepper_controller.ino` | Motion control firmware |
| `gui_app/main.py` | Desktop control UI |
| `gui_app/serial_link.py` | Serial transport and parser |
| `parts/` | 3D-printable hardware parts |
| `docs/` | Project documentation |

## System Architecture

### Control path

1. The user interacts with the Tkinter GUI.
2. The GUI sends simple ASCII commands over serial.
3. The Arduino firmware parses the command and updates the `AccelStepper` state.
4. The Arduino reports position and status back over serial.
5. The GUI updates labels, state flags, and logs from incoming messages.

### Motion model

- Motion is expressed in millimeters at the GUI level.
- Firmware converts millimeters to step counts using `stepsPerMm = 203.17`.
- The firmware enforces a motion range from `0.0` to `45.0` mm.
- The GUI requires a successful homing cycle before movement commands are allowed.

## Firmware Design

### Key Constants

The firmware currently defines:

- `stepsPerMm = 203.17`
- `minLimit = 0.0`
- `maxLimit = 45.0`
- `stepPin = 2`
- `dirPin = 3`
- `limitPin = 9`
- `HOMING_TIMEOUT_MS = 20000`
- `HOMING_SPEED_MM_S = 5.0`
- `HOMING_BACKOFF_MM = 2.0`

### Startup Behavior

At startup, the firmware:

1. Starts serial at `115200`
2. Configures the limit switch pin as `INPUT_PULLUP`
3. Applies default motion parameters
4. Reports `STATUS:READY`

### Motion Defaults

The firmware stores operator motion settings in:

- `userMaxSpeed`
- `userAcceleration`

Current defaults are:

- max speed: `5 mm/s`
- acceleration: `500 mm/s^2`

These settings are later restored after homing completes.

### Command Parsing

Each line from serial is parsed as:

- first character: command code
- remaining text: numeric value when needed

### Command Table

| Command | Example | Meaning |
| --- | --- | --- |
| `G` | `G12.5` | Move to an absolute position in mm |
| `J` | `J-1.0` | Jog by a relative distance in mm |
| `V` | `V5` | Set max speed in mm/s |
| `A` | `A500` | Set acceleration in mm/s^2 |
| `H` | `H` | Start homing |
| `S` | `S` | Emergency stop |

### Homing Behavior

The homing routine is **blocking** on the Arduino side.

Flow:

1. Firmware reports `STATUS:HOMING_START`
2. Stage moves in the negative direction at the homing speed
3. The loop continues until:
   - the switch is triggered, or
   - the 20-second timeout is reached, or
   - an emergency stop command is received
4. On successful switch hit, the position is zeroed
5. The stage backs off by `2.0 mm`
6. The position is zeroed again
7. Normal speed/acceleration settings are restored
8. Firmware reports `STATUS:HOMED`

Timeout result:

- `ERROR:HOMING_TIMEOUT`

Emergency-stop-during-homing result:

- `STATUS:EMERGENCY_STOP_DURING_HOMING`

## Serial Output Format

### Position reports

The firmware sends a position report every 100 ms:

```text
P12.345
```

### Status messages

Status is reported as:

```text
STATUS:READY
STATUS:HOMING_START
STATUS:HOMING_BACKOFF
STATUS:HOMED
STATUS:STOPPED
```

Other messages may include warnings or errors such as:

```text
WARNING:Target_Out_Of_Bounds
ERROR:HOMING_TIMEOUT
```

## GUI Design

### Main Responsibilities

The GUI:

- Lists available COM ports
- Connects and disconnects from the Arduino
- Sends motion and parameter commands
- Displays live position and status
- Prevents motion until homing is complete
- Provides an operator-visible emergency stop button

### Connection Behavior

When the GUI connects:

1. The serial port opens at `115200`
2. DTR is toggled to reset the Arduino
3. The app waits for boot completion
4. The GUI sends its default motion parameters

That means GUI-side settings override firmware defaults after connection.

### GUI Limits

The GUI currently enforces:

- travel range: `0` to `45 mm`
- max speed input: `30 mm/s`
- max acceleration input: `1000 mm/s^2`

### State Handling

The GUI tracks:

- `is_connected`
- `is_homed`
- `current_position`
- `status_message`

Movement commands are blocked unless:

- the serial connection is active, and
- the stage has been homed

## Wiring Reference from Firmware

The current firmware implies this minimum electrical interface:

| Signal | Arduino Pin | Function |
| --- | --- | --- |
| `STEP` | `D2` | Step pulse output to driver |
| `DIR` | `D3` | Direction output to driver |
| `HOME_SW` | `D9` | Home switch input |

The home switch uses the Arduino internal pull-up, so the switch should pull the input low when actuated.

## Safety Model

Current safety behavior includes:

- software travel limit in firmware
- GUI-side move validation
- mandatory homing before motion
- emergency stop command
- homing timeout

Current limitations:

- Firmware does not independently clamp incoming speed or acceleration to the same limits as the GUI
- Homing is blocking and occupies the Arduino loop until completion, timeout, or emergency stop
- The system assumes the configured `stepsPerMm` matches the physical drive train

## Build and Run

### Firmware

1. Open `firmware/stepper_controller/stepper_controller.ino` in Arduino IDE.
2. Install the `AccelStepper` library.
3. Select the Arduino Uno R4 Minima board.
4. Upload the sketch.

### GUI from Source

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Run:

```bash
python gui_app/main.py
```

### Packaged App

The repository also includes a PyInstaller spec:

- `BladeRunner.spec`

Use it when generating a Windows executable build.

## Recommended Future Improvements

- Add firmware-side clamps for speed and acceleration
- Add explicit driver configuration notes for the Adafruit TMC2209 breakout
- Document motor coil wiring with the exact wire color mapping used in the build
- Add calibration notes for verifying `stepsPerMm`
