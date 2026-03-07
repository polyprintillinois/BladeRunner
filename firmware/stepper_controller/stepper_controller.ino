#include <AccelStepper.h>

// --- Configuration & Calibration Data ---
const float stepsPerMm = 203.17; 
const float minLimit = 0.0;
const float maxLimit = 45.0;
const int stepPin = 2;
const int dirPin = 3;
const int limitPin = 9;

// Homing configuration
const unsigned long HOMING_TIMEOUT_MS = 20000; // 20 seconds
const float HOMING_SPEED_MM_S = 5.0;
const float HOMING_BACKOFF_MM = 2.0;

// User settings (Persisted)
float userMaxSpeed = 5.0 * stepsPerMm;
float userAcceleration = 500.0 * stepsPerMm; // Modified to 500 based on user preference

AccelStepper stepper(AccelStepper::DRIVER, stepPin, dirPin);

void setup() {
  Serial.begin(115200);
  pinMode(limitPin, INPUT_PULLUP);

  // Initial default settings
  stepper.setMaxSpeed(userMaxSpeed);
  stepper.setAcceleration(userAcceleration);
  
  Serial.println("STATUS:READY");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    processCommand(input);
  }

  stepper.run();

  // Real-time Position Report (100ms interval)
  static unsigned long lastReport = 0;
  if (millis() - lastReport > 100) {
    reportPosition();
    lastReport = millis();
  }
}

void processCommand(String input) {
  if (input.length() == 0) return;
  
  char cmd = input[0];
  float val = input.substring(1).toFloat();

  switch (cmd) {
    case 'G': // Absolute Move (Go to)
      if (val >= minLimit && val <= maxLimit) {
        stepper.moveTo(val * stepsPerMm);
      } else {
        Serial.println("WARNING:Target_Out_Of_Bounds");
      }
      break;
      
    case 'J': // Relative Move (Jog)
      {
        float target = (stepper.currentPosition() / stepsPerMm) + val;
        // Check soft limits
        if (target >= minLimit && target <= maxLimit) {
          stepper.moveTo(target * stepsPerMm);
        } else {
          Serial.println("WARNING:Target_Out_Of_Bounds");
        }
      }
      break;
      
    case 'V': // Set Max Speed
      userMaxSpeed = val * stepsPerMm;
      stepper.setMaxSpeed(userMaxSpeed); 
      break;
      
    case 'A': // Set Acceleration
      userAcceleration = val * stepsPerMm;
      stepper.setAcceleration(userAcceleration); 
      break;
      
    case 'H': // Homing
      runHoming(); 
      break;
      
    case 'S': // Emergency Stop
      stepper.stop(); 
      Serial.println("STATUS:STOPPED");
      break;
  }
}

void runHoming() {
  Serial.println("STATUS:HOMING_START");
  
  // Set homing speed
  stepper.setMaxSpeed(HOMING_SPEED_MM_S * stepsPerMm);
  stepper.setSpeed(-HOMING_SPEED_MM_S * stepsPerMm); // Move negative towards switch

  unsigned long startTime = millis();

  // Move until switch is hit, or timeout, or Cancelled
  while (digitalRead(limitPin) == HIGH) {
    // 1. Check Timeout
    if (millis() - startTime > HOMING_TIMEOUT_MS) {
      stepper.stop();
      Serial.println("ERROR:HOMING_TIMEOUT");
      // Restore settings even on error to be safe? 
      // safer to leave stopped, but let's restore to allow recovery
      stepper.setMaxSpeed(userMaxSpeed); 
      return;
    }

    // 2. Check Input for Emergency Stop
    if (Serial.available() > 0) {
      char emergencyCmd = Serial.peek(); // Peek first to see if it makes sense to read
      if (emergencyCmd == 'S') {
        Serial.read(); // Consume 'S'
        stepper.stop();
        Serial.println("STATUS:EMERGENCY_STOP_DURING_HOMING");
        // Restore settings
        stepper.setMaxSpeed(userMaxSpeed);
        return; 
      }
    }
    
    stepper.runSpeed();
  }

  // Current state: Switch hit or exited loop
  stepper.stop();
  stepper.setCurrentPosition(0);
  
  // Backoff
  Serial.println("STATUS:HOMING_BACKOFF");
  stepper.moveTo(HOMING_BACKOFF_MM * stepsPerMm);
  stepper.runToPosition();
  
  // Reset Zero
  stepper.setCurrentPosition(0);
  
  // Restore operational speed
  stepper.setMaxSpeed(userMaxSpeed);
  stepper.setAcceleration(userAcceleration); // Just in case, though only speed was changed
  Serial.println("STATUS:HOMED");
}

void reportPosition() {
  Serial.print("P");
  Serial.println(stepper.currentPosition() / stepsPerMm, 3);
}
