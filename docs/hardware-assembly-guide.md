# Hardware Assembly Guide

## Overview

BladeRunner is a compact linear stage built around a goBILDA open goRAIL, a lead screw drive, several 3D-printed interface parts, and an Arduino-controlled stepper system.

This guide covers:

- Purchased hardware
- 3D-printed parts
- Mechanical assembly order
- Electrical wiring
- Final setup checks

## System Summary

- **Controller**: Arduino Uno R4 Minima
- **Motor Driver**: Adafruit TMC2209 breakout
- **Stepper Motor**: StepperOnline 17HS08-1004S
- **Stage Format**: goBILDA open goRAIL with lead screw
- **Travel Range**: 45 mm usable software limit
- **Arduino Power**: USB
- **Motor Power**: External 12 V supply

## 3D-Printed Parts

Print all files in [parts](C:/Users/chwang12/PycharmProjects/BladeRunner/parts) before assembly.

| File | Purpose |
| --- | --- |
| `baseplate.stl` | Main mounting base for the motor and rail assembly |
| `bladeholder_connector.stl` | Connector between the lead screw nut and the blade holder |
| `fixer_double.stl` | Side clamping part used with the rail/bladeholder area |
| `substrate_fixer.stl` | Holds the substrate in place during experiments |

## Purchased Parts

### Control Electronics

| Item | Qty | Supplier | Part Number | Notes |
| --- | --- | --- | --- | --- |
| Arduino Uno R4 Minima | 1 | Arduino | Uno R4 Minima | Main controller |
| Adafruit TMC2209 | 1 | Adafruit | 6121 | Stepper driver, used in DIR/STEP mode |
| Arduino Perma-Proto board | 1 | Arduino | N/A | Used for power and wiring distribution |
| Stepper motor | 1 | StepperOnline | 17HS08-1004S | NEMA 17 motor |
| Snap-action switch | 1 | Digi-Key / Omron | V-153-1A5 | Used as the home/zero switch |

### Mechanical Actuator Parts

| Item | Qty | Supplier | Supplier PN | Notes |
| --- | --- | --- | --- | --- |
| Shaft coupler 8x5 mm | 1 | goBILDA | 4002-0005-0008 | Couples motor shaft to lead screw |
| Lead screw nut | 1 | goBILDA | 3503-0804-0038 | Mounts to bladeholder connector |
| Lead screw 150 mm | 1 | goBILDA | 3501-0804-0150 | Main drive screw |
| Open goRAIL 96 mm | 1 | goBILDA | 1118-0024-0096 | Main rail body |
| Lead screw clamping collar | 1 | goBILDA | 3504-0804-2109 | Screw retention/clamping component |
| Thrust ball bearing | 2 | goBILDA | 1613-0516-0008 | Axial load support |
| Flanged ball bearing | 1 pack | goBILDA | 1611-0514-0008 | Radial support for lead screw |

### Power Parts

| Item | Qty | Supplier | Part Number | Notes |
| --- | --- | --- | --- | --- |
| 12 V power adapter | 1 | Digi-Key / GlobTek | TR9CE5000LCP-N(R6B) | 12 V, 60 W motor supply |
| AC power cord | 1 | Digi-Key / Eaton Tripp Lite | P006-002-13A | Adapter input cable |
| Barrel jack connector set | 1 | Amazon / Thsinde | 5.5 mm x 2.5 mm pair set | Used on the perfboard power interface |

## Fasteners and Inserts

Most of the assembly uses:

- M3 heat-set inserts
- M3 screws
- M4 screws

Current usage mapping:

- **M4 screws**: goRAIL to baseplate, lead screw nut to bladeholder connector
- **M3 screws**: `fixer_double`, snap-action switch, and most remaining printed-part mounting points

## Mechanical Assembly

### 1. Print and prepare parts

1. Print all STL files in [parts](C:/Users/chwang12/PycharmProjects/BladeRunner/parts).
2. Install M3 heat-set inserts where required by the printed parts.
3. Confirm that the motor, rail, and printed interfaces fit without interference.

### 2. Build the base assembly

1. Mount the stepper motor to the `baseplate`.
2. Mount the open goRAIL to the `baseplate` using M4 hardware.

### 3. Assemble the internal goRAIL stack

Insert the following components into the goRAIL in this order:

1. Lead screw clamping collar
2. Thrust ball bearing
3. Flanged ball bearing
4. Lead screw nut
5. Flanged ball bearing
6. Thrust ball bearing
7. Flexible shaft coupler
8. Stepper motor

After alignment, connect the lead screw to the motor through the shaft coupler.

### 4. Attach the bladeholder interface

1. Attach `bladeholder_connector` to the lead screw nut using M4 screws.
2. Insert `fixer_double` into the goRAIL side area.
3. Secure the `fixer_double` assembly with M3 hardware.
4. Attach the blade holder or blade-specific interface to `bladeholder_connector`.

The blade itself is treated as experiment-specific hardware and should be selected separately.

### 5. Mount the home switch

1. Mount the Omron snap-action switch in the intended zeroing position.
2. Confirm that the moving assembly reliably actuates the switch at the home end of travel.
3. Adjust position as needed so the home trigger is repeatable.

### 6. Final experiment setup

1. Place the substrate into the fixture area.
2. Use `substrate_fixer` to clamp the substrate in place.
3. Verify that the blade path clears all fixtures before powering the motor.

## Electrical Wiring

The current firmware uses only `STEP`, `DIR`, and a single home switch input.

### Arduino Connections

| Arduino Pin | Connects To | Notes |
| --- | --- | --- |
| `D2` | TMC2209 `STEP` | Step pulse output |
| `D3` | TMC2209 `DIR` | Direction output |
| `D9` | Home switch signal | Configured as `INPUT_PULLUP` in firmware |
| `5V` | TMC2209 logic supply | Driver logic power |
| `GND` | TMC2209 logic ground and switch ground | Common reference |
| USB | PC | Arduino power and serial communication |

### TMC2209 and Motor Power

| Connection | Notes |
| --- | --- |
| External `12 V +` | To TMC2209 motor power input |
| External `12 V -` | To TMC2209 motor power ground |
| Motor coil A/B outputs | To the four motor wires on the stepper |

### Home Switch Wiring

Use the switch so that the firmware reads the input as:

- `HIGH`: not triggered
- `LOW`: triggered

That matches the current Arduino `INPUT_PULLUP` configuration. In practice, wire the switch between `D9` and `GND` using the switch terminals that close the circuit when the switch is actuated.

### Perfboard Power Distribution

The Perma-Proto board is used as a simple power distribution point:

1. Bring the 12 V adapter output onto the board through the barrel jack connector.
2. Route 12 V and GND from the perfboard to the TMC2209 motor power input.
3. Keep Arduino USB power separate from the motor power rail except for shared signal ground where required.

## Recommended Bring-Up Procedure

1. Power the Arduino over USB only and confirm serial connection.
2. Verify the home switch input before connecting motor power.
3. Apply 12 V motor power.
4. Confirm motor direction with a short jog.
5. Run homing and verify that the switch is hit cleanly.
6. Test motion over a short distance before using the full travel range.

## Checks Before Use

- Printed parts fit without rubbing or binding
- goRAIL is firmly mounted to the baseplate
- Lead screw rotates freely by hand before powered testing
- Bearings and collar are seated correctly
- Home switch triggers repeatably
- Arduino USB connection is stable
- 12 V motor power polarity is correct
- Stage motion is clear across the intended working range
