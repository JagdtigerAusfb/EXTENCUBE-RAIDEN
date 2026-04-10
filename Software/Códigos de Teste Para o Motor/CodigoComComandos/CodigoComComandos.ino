#define DIR_PIN A5
#define STEP_PIN A4
#define ENABLE_PIN A3

// 200 passos = 360 graus em full step (1.8°/passo)
// 50 passos = 90 graus
#define STEPS_90   50
#define STEPS_180  100

int stepDelay = 1000; // delay em microssegundos (velocidade padrão)

void step(int steps, bool clockwise) {
  digitalWrite(DIR_PIN, clockwise ? HIGH : LOW);
  delayMicroseconds(100); // pequena pausa após trocar direção

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(stepDelay);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(stepDelay);
  }
}

void setup() {
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  Serial.println("Pronto. Comandos: z=+90  x=-90  c=180  V<valor>=velocidade");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();

    if (cmd == 'z') {
      Serial.println("Horario 90 graus");
      step(STEPS_90, true);

    } else if (cmd == 'x') {
      Serial.println("Anti-horario 90 graus");
      step(STEPS_90, false);

    } else if (cmd == 'c') {
      Serial.println("180 graus");
      step(STEPS_180, true);

    } else if (cmd == 'V') {
      // Lê o número que vem depois do 'V', ex: "V500"
      int val = Serial.parseInt();
      if (val > 0) {
        stepDelay = val;
        Serial.print("Velocidade ajustada para: ");
        Serial.print(stepDelay);
        Serial.println(" us");
      } else {
        Serial.println("Valor invalido. Ex: V500");
      }
    }
  }
}