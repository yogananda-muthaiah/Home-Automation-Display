# Home-Automation-Display
Raspberry Pico 2 W - IoT Projects

## Components Needed
* Raspberry Pi Pico 2 W
* A display (OLED, e-ink, or LCD - I'll use OLED as an example)
* MicroUSB cable
* Breadboard and jumper wires (if needed for your display)


## Implementation Steps

1. Set up MicroPython on Pico 2 W
First, install MicroPython on your Pico:

Enter bootloader mode by holding BOOTSEL while plugging in the Pico
Drag and drop the MicroPython firmware (RP2350 version) to the RPI-RP2 drive
Use Thonny IDE to connect to your Pico

2. Install Required Libraries
Create a lib folder on your Pico and add these libraries:

main.py (for HTTP requests)
ssd1306.py (for OLED display - or appropriate library for your display)
