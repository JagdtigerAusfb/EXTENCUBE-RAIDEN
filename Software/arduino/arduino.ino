// ================================
// DEFINIÇÃO DOS PINOS
// ================================

#define DIR_PIN_1 31
#define STEP_PIN_1 30
#define DIR_PIN_2 35
#define STEP_PIN_2 34
#define DIR_PIN_3 A12
#define STEP_PIN_3 A13
#define DIR_PIN_4 A6
#define STEP_PIN_4 A7
#define DIR_PIN_5 A0
#define STEP_PIN_5 A1
#define DIR_PIN_6 43
#define STEP_PIN_6 42

#define ENABLE_PIN_1 14
#define ENABLE_PIN_2 16
#define ENABLE_PIN_3 49
#define ENABLE_PIN_4 48
#define ENABLE_PIN_5 A3
#define ENABLE_PIN_6 19

// ================================
// CONFIG
// ================================

#define MAX_SEQ 350

char lineBuffer[50];
char sequencia[MAX_SEQ];

int seqLen = 0;
int DELAY_STEP = 1000;
int DELAY_ENTRE_MOV = 10;

bool recebendo = false;

// ================================
// CONFIGURAR MOTOR
// ================================

bool configurarMotor(char m, int &dirPin, int &stepPin, int &enablePin, int &dir, int &passos) {

    switch(m) {

        case 'A': dirPin=DIR_PIN_1; stepPin=STEP_PIN_1; enablePin=ENABLE_PIN_1; dir=LOW;  passos=50; break;
        case 'B': dirPin=DIR_PIN_1; stepPin=STEP_PIN_1; enablePin=ENABLE_PIN_1; dir=HIGH; passos=50; break;
        case 'C': dirPin=DIR_PIN_1; stepPin=STEP_PIN_1; enablePin=ENABLE_PIN_1; dir=LOW;  passos=100; break;

        case 'D': dirPin=DIR_PIN_2; stepPin=STEP_PIN_2; enablePin=ENABLE_PIN_2; dir=LOW;  passos=50; break;
        case 'E': dirPin=DIR_PIN_2; stepPin=STEP_PIN_2; enablePin=ENABLE_PIN_2; dir=HIGH; passos=50; break;
        case 'F': dirPin=DIR_PIN_2; stepPin=STEP_PIN_2; enablePin=ENABLE_PIN_2; dir=LOW;  passos=100; break;

        case 'G': dirPin=DIR_PIN_3; stepPin=STEP_PIN_3; enablePin=ENABLE_PIN_3; dir=LOW;  passos=50; break;
        case 'H': dirPin=DIR_PIN_3; stepPin=STEP_PIN_3; enablePin=ENABLE_PIN_3; dir=HIGH; passos=50; break;
        case 'I': dirPin=DIR_PIN_3; stepPin=STEP_PIN_3; enablePin=ENABLE_PIN_3; dir=LOW;  passos=100; break;

        case 'J': dirPin=DIR_PIN_4; stepPin=STEP_PIN_4; enablePin=ENABLE_PIN_4; dir=LOW;  passos=50; break;
        case 'K': dirPin=DIR_PIN_4; stepPin=STEP_PIN_4; enablePin=ENABLE_PIN_4; dir=HIGH; passos=50; break;
        case 'L': dirPin=DIR_PIN_4; stepPin=STEP_PIN_4; enablePin=ENABLE_PIN_4; dir=LOW;  passos=100; break;

        case 'M': dirPin=DIR_PIN_5; stepPin=STEP_PIN_5; enablePin=ENABLE_PIN_5; dir=LOW;  passos=50; break;
        case 'N': dirPin=DIR_PIN_5; stepPin=STEP_PIN_5; enablePin=ENABLE_PIN_5; dir=HIGH; passos=50; break;
        case 'O': dirPin=DIR_PIN_5; stepPin=STEP_PIN_5; enablePin=ENABLE_PIN_5; dir=LOW;  passos=100; break;

        case 'P': dirPin=DIR_PIN_6; stepPin=STEP_PIN_6; enablePin=ENABLE_PIN_6; dir=LOW;  passos=50; break;
        case 'Q': dirPin=DIR_PIN_6; stepPin=STEP_PIN_6; enablePin=ENABLE_PIN_6; dir=HIGH; passos=50; break;
        case 'R': dirPin=DIR_PIN_6; stepPin=STEP_PIN_6; enablePin=ENABLE_PIN_6; dir=LOW;  passos=100; break;

        default: return false;
    }
    return true;
}

// ================================
// OPOSTOS
// ================================

bool saoOpostos(char f1, char f2){

    bool U1=(f1=='A'||f1=='B'||f1=='C');
    bool D1=(f1=='J'||f1=='K'||f1=='L');
    bool F1=(f1=='G'||f1=='H'||f1=='I');
    bool B1_flag=(f1=='P'||f1=='Q'||f1=='R');
    bool R1=(f1=='D'||f1=='E'||f1=='F');
    bool L1=(f1=='M'||f1=='N'||f1=='O');

    bool U2=(f2=='A'||f2=='B'||f2=='C');
    bool D2=(f2=='J'||f2=='K'||f2=='L');
    bool F2=(f2=='G'||f2=='H'||f2=='I');
    bool B2=(f2=='P'||f2=='Q'||f2=='R');
    bool R2=(f2=='D'||f2=='E'||f2=='F');
    bool L2=(f2=='M'||f2=='N'||f2=='O');

    if((U1&&D2)||(D1&&U2)) return true;
    if((F1&&B2)||(B1_flag&&F2)) return true;
    if((R1&&L2)||(L1&&R2)) return true;

    return false;
}

// ================================
// EXECUÇÕES
// ================================

void executarSimples(char m){

    int d,s,e,dir,p;
    if(!configurarMotor(m,d,s,e,dir,p)) return;

    digitalWrite(e,LOW);
    digitalWrite(d,dir);

    for(int i=0;i<p;i++){
        digitalWrite(s,HIGH);
        delayMicroseconds(DELAY_STEP);
        digitalWrite(s,LOW);
        delayMicroseconds(DELAY_STEP);
    }

    digitalWrite(e,HIGH);
    delay(DELAY_ENTRE_MOV);
}

void executarDuplo(char m1,char m2){

    int d1,s1,e1,dir1,p1;
    int d2,s2,e2,dir2,p2;

    if(!configurarMotor(m1,d1,s1,e1,dir1,p1)) return;
    if(!configurarMotor(m2,d2,s2,e2,dir2,p2)) return;

    digitalWrite(e1,LOW);
    digitalWrite(e2,LOW);

    digitalWrite(d1,dir1);
    digitalWrite(d2,dir2);

    int maxP = max(p1,p2);

    for(int i=0;i<maxP;i++){

        if(i<p1) digitalWrite(s1,HIGH);
        if(i<p2) digitalWrite(s2,HIGH);

        delayMicroseconds(DELAY_STEP);

        if(i<p1) digitalWrite(s1,LOW);
        if(i<p2) digitalWrite(s2,LOW);

        delayMicroseconds(DELAY_STEP);
    }

    digitalWrite(e1,HIGH);
    digitalWrite(e2,HIGH);

    delay(DELAY_ENTRE_MOV);
}

// ================================
// SETUP
// ================================

void setup(){

    Serial.begin(9600);

    pinMode(ENABLE_PIN_1,OUTPUT); digitalWrite(ENABLE_PIN_1,HIGH);
    pinMode(ENABLE_PIN_2,OUTPUT); digitalWrite(ENABLE_PIN_2,HIGH);
    pinMode(ENABLE_PIN_3,OUTPUT); digitalWrite(ENABLE_PIN_3,HIGH);
    pinMode(ENABLE_PIN_4,OUTPUT); digitalWrite(ENABLE_PIN_4,HIGH);
    pinMode(ENABLE_PIN_5,OUTPUT); digitalWrite(ENABLE_PIN_5,HIGH);
    pinMode(ENABLE_PIN_6,OUTPUT); digitalWrite(ENABLE_PIN_6,HIGH);

    pinMode(DIR_PIN_1,OUTPUT); pinMode(STEP_PIN_1,OUTPUT);
    pinMode(DIR_PIN_2,OUTPUT); pinMode(STEP_PIN_2,OUTPUT);
    pinMode(DIR_PIN_3,OUTPUT); pinMode(STEP_PIN_3,OUTPUT);
    pinMode(DIR_PIN_4,OUTPUT); pinMode(STEP_PIN_4,OUTPUT);
    pinMode(DIR_PIN_5,OUTPUT); pinMode(STEP_PIN_5,OUTPUT);
    pinMode(DIR_PIN_6,OUTPUT); pinMode(STEP_PIN_6,OUTPUT);

    Serial.println("READY");
}

// ================================
// LOOP
// ================================

void loop(){

    if(!Serial.available()) return;

    int len = Serial.readBytesUntil('\n', lineBuffer, sizeof(lineBuffer)-1);
    lineBuffer[len]='\0';

    if(strcmp(lineBuffer,"<START>")==0){
        recebendo = true;
        seqLen = 0;
        return;
    }

    if(strcmp(lineBuffer,"<END>")==0){

        unsigned long t0 = micros();

        for(int i=0;i<seqLen;i++){
            if(i<seqLen-1 && saoOpostos(sequencia[i],sequencia[i+1])){
                executarDuplo(sequencia[i],sequencia[i+1]);
                i++;
            }else{
                executarSimples(sequencia[i]);
            }
        }

        unsigned long t1 = micros();

        Serial.print("DONE ");
        Serial.println((t1-t0)/1000000.0);

        recebendo=false;
        return;
    }

    if(recebendo){

        if(strncmp(lineBuffer,"<SPEED:",7)==0){
            DELAY_STEP = atoi(&lineBuffer[7]);
            return;
        }

        if(strncmp(lineBuffer,"<DELAY:",7)==0){
            DELAY_ENTRE_MOV = atoi(&lineBuffer[7]);
            return;
        }

        if(seqLen < MAX_SEQ){
            sequencia[seqLen++] = lineBuffer[0];
        }
    }
}