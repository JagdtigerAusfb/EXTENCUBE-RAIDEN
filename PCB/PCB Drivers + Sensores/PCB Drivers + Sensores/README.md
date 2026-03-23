## Drivers & Sensors Shield

![PCB Drivers + Sensores](https://github.com/user-attachments/assets/c0fdf90f-f2a9-47dc-80e2-0086166bc332)

This board functions as a custom shield for the **Arduino Mega**. It integrates everything needed to control the mechanics and inputs of the project:
* **6x A4988 Stepper Motor Drivers**
* **12x Color Sensor Connectors**
* **1x Multiplexer** (to handle the sensor inputs)

## Power Supply & Distribution

The system is powered by a 12V power supply with two output ports. **We strongly advise using both ports.** During testing, relying on a single port caused voltage drops, which resulted in some motors stalling. 

To distribute the current load evenly, the board features **two DC Jack connectors**. Each jack supplies 12V to a dedicated group of three motor drivers.

## A4988 Drivers

**Pin configuration:**

| Driver | DIR Pin | STEP Pin | ENABLE Pin |
| :--- | :---: | :---: | :---: |
| **Driver 1** | A0 | A1 | A2 |
| **Driver 2** | A3 | A4 | A5 |
| **Driver 3** | A6 | A7 | A8 |
| **Driver 4** | 53 | 51 | 49 |
| **Driver 5** | 43 | 41 | 39 |
| **Driver 6** | 29 | 27 | 25 |

Note that these are based on what was easiest to route on the board physicaly.

In this project, we only utilize the **DIR**, **STEP**, and **EN** (Enable) pins of the motor drivers. The configuration for the remaining pins is as follows:

* **Microstepping (MS Pins):** These pins are left disconnected.
* **RESET & SLEEP Pins:** These pins are tied together. 

This specific setup is possible because the drivers used in this project include internal **pull-up or pull-down resistors**, which stabilize the signals even when left unconnected. 

> [!CAUTION]
> These pins are not accessible in the current board design. If you decide to use a different or "equivalent" driver, ensure it also features internal pull-up/down resistors. Some simpler or cheaper versions of these drivers lack these resistors; in such cases, the pins **cannot** be left floating (unconnected), or the driver will not function correctly.

## Multiplexer (CD74HC4067) and Sensors (TCS34725)

### Sensors (TCS34725)

**Pin configuration:**

| Sensor | Pino do Arduino (LED Control) |
| :--- | :---: |
| **Sensor 1** | **13** |
| **Sensor 2** | **12** |
| **Sensor 3** | **11** |
| **Sensor 4** | **10** |
| **Sensor 5** | **9** |
| **Sensor 6** | **8** |
| **Sensor 7** | **14** |
| **Sensor 8** | **15** |
| **Sensor 9** | **16** |
| **Sensor 10** | **17** |
| **Sensor 11** | **18** |
| **Sensor 12** | **19** |

In this project, we only utilize the **VIN**, **GND**, **SDA**, **SCL**, and **LED** pins of the TCS34725 color sensors. The configuration for the remaining pins is as follows:

* **Interrupt (INT Pin):** This pin is left disconnected. 
* **3.3V Pin:** This pin is also left disconnected.

> [!NOTE]
> This configuration assumes you are using a standard TCS34725 breakout module (like the ones from Adafruit or similar clones) that includes a built-in voltage regulator and I2C pull-up resistors. If you are using a different, 3.3V-only version of the board, do not connect 5V to the power pins, as it will damage the sensor!

Note that these are based on what was easiest to route on the board physicaly.

## Multiplexer (CD74HC4067)

| Pino do MUX | Pino do Arduino (Mux Control) |
| :--- | :---: |
| **S0 (LSB)** | **5** |
| **S1** | **4** |
| **S2** | **3** |
| **S3 (MSB)** | **2** |

| Sinal SDA (Sensor) | Pino do Header | Entrada do MUX |
| :--- | :---: | :---: |
| **SDA_1** | JP1-1 | **C0** |
| **SDA_2** | JP1-2 | **C1** |
| **SDA_3** | JP1-3 | **C2** |
| **SDA_4** | JP1-4 | **C3** |
| **SDA_5** | JP1-5 | **C4** |
| **SDA_6** | JP1-6 | **C5** |
| **SDA_7** | JP1-7 | **C6** |
| **SDA_8** | JP1-8 | **C7** |
| **SDA_9** | JP1-9 | **C8** |
| **SDA_10** | JP1-10 | **C9** |
| **SDA_11** | JP1-11 | **C10** |
| **SDA_12** | JP1-12 | **C11** |
| *Not Connected* | JP1-13 | **C12** |
| *Not Connected* | JP1-14 | **C13** |
| *Not Connected* | JP1-15 | **C14** |
| *Not Connected* | JP1-16 | **C15** |

## Optional Components

 **Indicator LEDs:** There are LEDs (and their corresponding resistors) to indicate power from the two 12V jacks and the 5V line from the Arduino. Additionally, each A4988 driver has a dedicated LED to show when a step signal is being sent to the motor. You can safely exclude these if you prefer. 
 
 **Reset Button:** The board includes a physical Reset button for the Arduino. This can also be omitted.
 
 **Highly Recommended - Capacitors:** While the board might technically work without them, installing the decoupling capacitors for the motor drivers is **highly recommended**. They are crucial for preventing voltage spikes that can permanently damage the A4988 drivers.

## Comments

 > [!NOTE]
> The Arduino connectors in the PCB project are only female, but in reality they should be male and female connects (they should have the female connector on top and the male pins on the bottom to connect to the Arduino), the 3D model just shows the famele pins. Be carefull not to order the wrong connector!
