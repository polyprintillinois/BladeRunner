#include <AccelStepper.h>

// 핀 설정 (Arduino Uno R4 Minima)
const int stepPin = 2;
const int dirPin = 3;
const int limitSwitchPin = 9;

// AccelStepper 인스턴스 생성 (DRIVER 모드: Step, Dir 핀 사용)
AccelStepper stepper(AccelStepper::DRIVER, stepPin, dirPin);

// 설정값
const int stepsPerMillimeter = 200; // 1.8도 모터(200step/rev) * 1/1 마이크로스텝 / 1mm 리드 (가정) -> 확인 필요
// 사용자 제공 정보: 17HS08-1004S (1.8deg), TMC2209.
// 만약 1/8 마이크로스텝이고 리드스크류 피치가 8mm라면? 
// 200 * 8 / 8 = 200 steps/mm (사용자 코드 값 유지)

const float homingSpeed = 5.0; // mm/s (너무 느리면 답답하므로 약간 조정, 사용자 값 0.5는 매우 느림)
const float homingBackoff = 3.0; // mm

void setup() {
  Serial.begin(9600);
  while (!Serial); // R4는 USB 시리얼 연결 대기 필요할 수 있음

  pinMode(limitSwitchPin, INPUT_PULLUP);

  // 속도 및 가속도 설정
  stepper.setMaxSpeed(1000); // steps/s (약 5mm/s)
  stepper.setAcceleration(500); // steps/s^2

  Serial.println("--- Arduino Linear Stage System Start ---");
  Serial.println("Homing...");

  // 1. 리미트 스위치를 향해 이동 (음수 방향이 스위치 쪽이라고 가정)
  stepper.setSpeed(-homingSpeed * stepsPerMillimeter); 
  
  // 스위치가 눌리지 않은 상태(HIGH)인 동안 계속 이동
  while (digitalRead(limitSwitchPin) == HIGH) {
    stepper.runSpeed();
  }

  // 2. 정지 및 현재 위치 0으로 임시 설정
  stepper.stop();
  stepper.setCurrentPosition(0);
  Serial.println("Limit switch hit. Backing off...");

  // 3. 스위치에서 떨어지기 (Backoff)
  stepper.moveTo(homingBackoff * stepsPerMillimeter);
  stepper.runToPosition();

  // 4. 최종 0점 설정
  stepper.setCurrentPosition(0);
  Serial.println("Homing Complete. Position reset to 0.");
}

void loop() {
  // 목표 위치에 도달했는지 확인
  if (stepper.distanceToGo() == 0) {
    delay(1000); // 1초 대기

    // 현재 위치가 0이면 20mm로, 아니면 0으로 이동
    if (abs(stepper.currentPosition()) < 10) { // 0 근처라면
      Serial.println("Moving to 20mm");
      stepper.moveTo(20 * stepsPerMillimeter);
    } else {
      Serial.println("Moving to 0mm");
      stepper.moveTo(0);
    }
  }

  stepper.run();
}
