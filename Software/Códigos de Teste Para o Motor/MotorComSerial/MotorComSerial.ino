/*
-> Pino de sleep ativado em high por default, pino reset floating --> ligar o sleep no floating (testar isso se não der certo)
-> pinos de microsteep tem resistor de pull down e deixar sem nada resulta em full step
-> enable sempre ligado 
*/

//usar define faz ele demorar para compilar, por algumar razão
//lembrar que define não ocupa memoria como variavel, só
//substitui o texto
#define DIR_PIN A5
#define STEP_PIN A4
#define ENABLE_PIN A3


void setup() {

  //Seta pins como output
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);

  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(DIR_PIN, HIGH);     // define direção (troque HIGH/LOW para inverter)

}

void loop() {

  for (int i = 0; i < 50; i++) // gera 50 pulsos de step (1.8 * 50 = 90)
    {
    digitalWrite(STEP_PIN, HIGH);   // Liga o motor ao setar o pin de step como high, cada setamento desse pino faz passar um passo
    digitalWrite(LED_BUILTIN, HIGH);
    delayMicroseconds(1000);         
    digitalWrite(STEP_PIN, LOW);    // seta pin como low 
    digitalWrite(LED_BUILTIN, LOW);
    delayMicroseconds(1000);         
    }

delay(1000);
}