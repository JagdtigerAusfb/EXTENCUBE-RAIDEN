# PCB Design Files

This directory contains all the Printed Circuit Board (PCB) files required for this project. 

If you are a beginner, we highly recommend using [KiCad](https://www.kicad.org/) (which is free and open-source) to open and edit these files.

## How to Open and Edit

To view or modify the project, you only need to use with the files:

* **`.pro` / `.kicad_pro`:** The main KiCad project file. Opening this will automatically link and open both the schematic and the board layout.
* **`.sch` / `.kicad_sch`:** Contains the electronic schematics of the circuit.
* **`.pcb` / `.kicad_pcb`:** Contains the physical design and layout of the PCB.

> **Note:** These are the only files you need to open to edit the project. All other files in this directory are generated for production purposes.

## How to Manufacture the PCB

If you want to have this board manufactured by a PCB fabrication house, you will need to send them the production files.

* **`.gbr` (Gerber Files):** These are the production files. Each file corresponds to a specific physical layer of the board (copper, silkscreen, solder mask, etc.).
* **`.drl` (Drill Files):** These files dictate the exact locations and sizes of the holes to be drilled in the board. You must include these unless you plan on drilling the holes manually (which we definitely don't recommend!).

**How to order:**
1. Select all the `.gbr` and `.drl` files.
2. Compress them into a single `.zip` file.
3. Upload the `.zip` file to your PCB manufacturer of choice (e.g., JLCPCB, PCBWay, OSH Park).
