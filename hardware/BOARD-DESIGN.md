# Waveshare ESP32-S3 LCD Driver Board - Hardware Design

## Board Overview

**Waveshare ESP32-S3 LCD Driver Board** is an integrated development platform combining:
- ESP32-S3-WROOM-1 microcontroller
- ETA6096 battery management IC
- LCD interface with backlight control
- 40-pin connectors for expansion
- USB Type-C for programming and power

---

## Connectors & Interfaces

### USB Type-C (J1)
```
Pin 1: VBUS (5V input)
Pin 2: D- (Serial data)
Pin 3: D+ (Serial data)
Pin 4: GND
Pin 5: CC (Configuration channel) - not used
```
- **Purpose**: Power supply, firmware upload, serial debugging
- **Current Rating**: 500mA (typical), up to 2A (with proper PSU)
- **Protocol**: USB CDC-ACM (Virtual COM Port)

### Battery Connector (J2)
- **Type**: JST (2-pin, 2.0mm pitch)
- **Voltage**: 3.7V nominal (1S LiPo)
- **Current**: Up to 2A discharge
- **Connection**: Positive (red) to BAT+, Negative (black) to GND

### 40-Pin LCD Connector (Top)
- **Type**: FPC/FFC 40-pin (0.5mm pitch)
- **Purpose**: LCD display ribbon cable connection
- **Voltage**: 3.3V logic levels
- **Signal**: Parallel RGB data + control signals

### 40-Pin I/O Expansion Connector (Bottom)
- **Type**: 2×20 header pins (2.54mm pitch)
- **Voltage**: Mix of 3.3V logic
- **Available GPIO**: Most unused pins from ESP32-S3
- **Power**: 3.3V, 5V, GND available

---

## Power Management

### Battery Management (ETA6096)
```
Input: USB 5V or Battery 3.7V
Output: 3.3V regulated power

Key Features:
├─ Over-charge protection
├─ Over-discharge protection
├─ Thermal management
├─ Low battery detection
└─ Charging status indication (LED)
```

### Power Distribution
```
USB 5V → ETA6096 → VOUT (3.3V regulated)
            ↓
        ├─ ESP32-S3 (VDD3P3, VDD3P3_CPU, VDD3P3_RTC)
        ├─ LCD backlight PWM
        ├─ Touch controller (CST816D)
        └─ I/O expansion pins (3.3V)
```

### Voltage Rails
| Rail | Voltage | Source | Max Current |
|------|---------|--------|------------|
| VBUS | 5V | USB Type-C | 500mA–2A |
| VBAT | 3.7V | LiPo battery | Up to 2A |
| VDD3P3 | 3.3V | ETA6096 regulator | ~500mA |
| VSYS | 3.3V | Regulated (internal) | All peripherals |

### Charging Circuit
- **Input**: USB 5V (VBUS via J1)
- **Battery**: JST connector J2 (1S LiPo)
- **Charging LED**: Indicates charging in progress
- **Status**: Charge protection built-in

---

## LCD Interface

### Display Connection (40-pin FPC)
**Waveshare 2-inch Capacitive-Touch LCD** (240×320 resolution)

#### Pin Mapping (FPC 40-pin connector)
```
Top Row (1-20):
1  - VDD3.3 (Power)
2  - GND
3  - LCD_CS (Chip Select) → GPIO39
4  - LCD_DC (Data/Command) → GPIO41
5  - LCD_RST (Reset) → GPIO40
6  - LCD_BL (Backlight PWM) → GPIO6
7  - LCD_SCLK (SPI Clock) → GPIO1
8  - LCD_MOSI (Data Out) → GPIO2
9  - LCD_MISO (Data In) → GPIO42
10 - (Not used)
11-20: Mostly unused in 8-line SPI mode

Bottom Row (21-40):
21-40: Touch sensor I2C + control signals
```

#### SPI Bus (Parallel to SD Card)
```
LCD_SCLK  (GPIO1)  - Clock (shared with SD)
LCD_MOSI  (GPIO2)  - Data out (shared with SD)
LCD_MISO  (GPIO42) - Data in (shared with SD)
LCD_CS    (GPIO39) - LCD chip select
LCD_DC    (GPIO41) - Data/Command select
LCD_RST   (GPIO40) - Reset (active low)
LCD_BL    (GPIO6)  - Backlight PWM (0–100%)
```

#### Display Controller
- **IC**: ST7789T3
- **Resolution**: 240 × 320 pixels
- **Color Depth**: 16-bit RGB565
- **Interface**: 8-bit/16-bit parallel SPI
- **Voltage**: 3.3V logic levels

### Backlight Control
```
GPIO6 (PWM) → Backlight circuit → LCD LED backlight
├─ PWM frequency: Configurable (20–40 kHz typical)
├─ Duty cycle: 0–100%
├─ Max current: ~100mA (current limit on board)
└─ Voltage: 3.3V to backlight series resistor
```

---

## Touch Sensor Interface

### CST816D Touch Controller
```
Connection: I2C (Two-wire)
├─ SDA: GPIO15 (Serial Data)
├─ SCL: GPIO7 (Serial Clock)
├─ RST: GPIO16 (Reset, active low)
└─ INT: GPIO17 (Interrupt, active low)

Specifications:
├─ Interface: I2C (100–400 kHz)
├─ Touch Points: Up to 5 simultaneous
├─ Resolution: 240 × 320 (matches display)
├─ Supply: 3.3V
└─ Interrupt-driven: INT pin goes low on touch
```

### I2C Address
- **Primary**: 0x15
- **Alternative**: 0x14 (configurable via hardware pins)

---

## SD Card Interface

### SD Card Connector
```
Type: Micro SD card slot (push-push)
Voltage: 3.3V
Max Speed: 50 MHz (SPI mode)
```

### SPI Connection (Shared with LCD)
```
SD_CS   (GPIO38)  - SD card chip select
SD_CLK  (GPIO1)   - Shared SPI clock
SD_MOSI (GPIO2)   - Shared data out
SD_MISO (GPIO42)  - Shared data in

Electrical:
├─ Voltage: 3.3V
├─ Speed: 25 MHz (SPI 2-line mode, typical)
├─ Impedance: Matched trace lengths
└─ Decoupling: 100nF near connector
```

### Card Support
- **Protocols**: SD 3.0, SDHC, SDXC
- **Capacity**: Up to 2TB (in SDXC mode)
- **Recommended**: Class 10 or faster, A1 minimum
- **File System**: FAT32 or exFAT

---

## I/O Expansion (Bottom 40-pin Header)

### Available GPIO Pins
```
Left Side (J3 - 20 pins):
1:  GND
2:  3V3 (Power)
3:  GPIO43 (UART TX, alt: D-) - Reserved
4:  GPIO44 (UART RX, alt: D+) - Reserved
5:  GPIO0  (Boot strapping)
6:  GPIO1  (LCD SPI - in use)
7:  GPIO2  (LCD SPI - in use)
8:  GPIO3  (JTAG/Strapping)
9:  GPIO4  (Free - ADC1_CH3)
10: GPIO5  (Free - ADC1_CH4)
11: GPIO8  (Free - ADC1_CH7)
12: GPIO9  (Free - ADC1_CH8)
13: GPIO10 (Free - ADC1_CH9)
14: GPIO11 (Free - ADC2_CH0)
15: GPIO12 (Free - ADC2_CH1)
16: GPIO13 (Free - ADC2_CH2)
17: GPIO14 (Free - ADC2_CH3)
18: GPIO6  (LCD Backlight PWM)
19: GPIO7  (Touch I2C SCL)
20: GND

Right Side (J3 - 20 pins):
21: GPIO15 (Touch I2C SDA)
22: GPIO16 (Touch reset)
23: GPIO17 (Touch interrupt)
24: GPIO18 (Free)
25: GPIO19 (USB D-, avoid)
26: GPIO20 (USB D+, avoid)
27: GPIO21 (Free)
28: GPIO38 (SD SPI CS)
29: GPIO39 (LCD SPI CS)
30: GPIO40 (LCD reset)
31: GPIO41 (LCD DC)
32: GPIO42 (LCD SPI MISO)
33: GPIO45 (Free - Strapping)
34: GPIO46 (Free - Strapping)
35: 5V (USB power, if available)
36: 5V (USB power, if available)
37: GND
38: GND
39: (Not populated)
40: (Not populated)
```

### Recommended Free GPIO for Development
```
Safe to Use (Priority 1):
├─ GPIO4, GPIO5, GPIO8, GPIO9, GPIO10
├─ GPIO11, GPIO12, GPIO13, GPIO14
└─ GPIO18, GPIO21, GPIO45, GPIO46

Use with Caution (Priority 2):
├─ GPIO0 (Strapping pin at boot)
├─ GPIO3 (JTAG/Strapping)
└─ GPIO19/20 (USB - share with Serial/JTAG)

Avoid (Reserved):
├─ GPIO1, GPIO2, GPIO39, GPIO40, GPIO41, GPIO42 (LCD SPI)
├─ GPIO6 (Backlight PWM)
├─ GPIO7, GPIO15, GPIO16, GPIO17 (Touch I2C)
├─ GPIO38 (SD CS)
└─ GPIO43, GPIO44 (Serial debug)
```

---

## User Input

### Push Buttons (3x)
```
Location: Around board edges

Button 1 (BOOT):
├─ Function: Enter download mode (hold at power-up)
├─ GPIO: GPIO0 (strapping pin)
└─ Active: Low (pulled to GND)

Button 2 (RESET):
├─ Function: Hard reset the ESP32-S3
├─ GPIO: CHIP_PU (power pin)
└─ Active: Low (pulled to GND)

Button 3 (USER):
├─ GPIO: GPIO45 (strapping pin, can be repurposed)
├─ Function: Custom (not pre-assigned)
└─ Active: Low (pulled to GND)
```

---

## LED Indicators

### Status LEDs
```
Charging LED (Red/Orange):
├─ Indicates: Battery charging in progress
├─ Control: ETA6096 (automatic)
└─ Behavior: On while charging, off when full

Power LED (Green/Blue):
├─ Indicates: System power on
├─ Control: Manual GPIO control (optional)
└─ Behavior: Always on when powered

User LED (Optional):
├─ GPIO: Available on I/O header
├─ Function: Custom status indicator
└─ Max current: 20mA per GPIO (typical)
```

---

## Schematic Highlights

### Power Supply Path
```
USB VBUS (5V)
    ↓
[USB Protected by diode + TVS]
    ↓
ETA6096 (Battery Manager)
    ├─ Charge controller
    ├─ Over-protection circuits
    └─ 3.3V Regulated output
        ↓
    [Bulk capacitors (10µF + 100µF)]
        ↓
    VDD3P3 rails (all supplies)
```

### Ground Distribution
- **Star point**: Multiple GND pins tied together near ETA6096
- **Layer**: Ground plane on PCB (likely 2-layer)
- **Decoupling**: 100nF capacitors near each major IC

### Battery Charging
```
USB VBUS → Charge control (ETA6096) → LiPo battery (J2)
              ↓
        Charge LED indicator
```

### Display Signal Conditioning
```
ESP32-S3 GPIO (3.3V) → Direct to LCD SPI pins
                     (No level shifters needed - both 3.3V)
```

### Touch Sensor Pull-ups
```
GPIO15 (SDA) ─[4.7kΩ]─ VDD3.3
GPIO7  (SCL) ─[4.7kΩ]─ VDD3.3
(Standard I2C pull-up resistors on CST816D module)
```

---

## PCB Design Notes

### Component Placement
```
Section 1 (Left):  USB Type-C + Battery connector
Section 2 (Top):   ETA6096 power management
Section 3 (Center): ESP32-S3 main SoC + supporting passives
Section 4 (Right):  LCD backlight circuit
Section 5 (Bottom): LCD/Touch FPC connectors
```

### Layer Stack (Likely 2-layer PCB)
```
Layer 1: Signal traces + component pads
Layer 2: Ground plane (continuous)
```

### Via Strategy
- Thermal vias under ESP32-S3 package
- Ground vias near high-speed SPI signals
- Power vias near ETA6096 output

### Decoupling Strategy
```
ETA6096:    10µF bulk + 100nF ceramic
ESP32-S3:   Multiple 100nF ceramics (power pins)
CST816D:    100nF ceramic on I2C lines
LCD backlight: 100µF near PWM gate driver
```

---

## Board Dimensions

From schematic header area:
```
Length: ~66.30 mm (2.61 inches)
Width:  ~25.40 mm (1.00 inches)
Height: ~2.80 mm (0.11 inches, to top of components)

Mount holes: 4 corners (M2 or M3)
```

---

## Manufacturing & Assembly

### Key Components
```
IC1: ESP32-S3-WROOM-1 (main SoC)
U1: ETA6096 (battery manager)
J1: USB Type-C connector
J2: JST 2-pin (battery)
J3: 40-pin header (expansion)
J4: 40-pin FPC (LCD)
J5: Micro SD slot

Resistors:
├─ Pull-ups: Various (I2C, SPI, GPIO)
├─ Current limiting: 10kΩ + 1kΩ (LED resistors)
└─ Sense resistors: 10mΩ–1Ω (power monitoring)

Capacitors:
├─ Bulk: 10µF (power supply stability)
├─ Ceramic: 100nF (high-frequency decoupling)
└─ Tantalum: Optional (power filtering)

Diodes:
├─ Schottky: USB input protection
├─ TVS: ESD protection on USB D+/D-
└─ Status LEDs: Red (charging), Green (power)
```

---

## Power Budget Considerations

### Typical Operating Scenarios

#### Scenario 1: Display On, No Radio
- **ESP32-S3**: ~30–50 mA (CPU + core)
- **Display + Backlight**: ~50–100 mA
- **Touch controller**: ~5 mA
- **Total**: ~85–155 mA

#### Scenario 2: Wi-Fi Active (scanning)
- **Base**: ~30 mA
- **Wi-Fi RF**: ~100 mA (RX), ~280 mA (TX)
- **Display**: ~80 mA
- **Total**: ~190–390 mA (peaks at TX)

#### Scenario 3: Deep Sleep (RTC only)
- **ULP coprocessor**: ~170 µA (FSM), ~190 µA (RISC-V)
- **RTC peripherals**: ~8 µA
- **Leakage**: ~1–5 µA
- **Total**: ~10–200 µA

### Battery Runtime Estimates
```
LiPo Capacity: 1000 mAh (typical for pocket device)

Scenario 1 (Display on, no radio):
├─ Avg current: ~120 mA
├─ Runtime: 1000mAh ÷ 120mA = ~8 hours

Scenario 2 (Average Wi-Fi use):
├─ Avg current: ~200 mA
├─ Runtime: 1000mAh ÷ 200mA = ~5 hours

Scenario 3 (Sleep mode):
├─ Avg current: ~100 µA
├─ Runtime: 1000mAh ÷ 0.1mA = ~416 days!
```

---

## Design Recommendations for KeychainOS

### Firmware Integration
1. **Configure TFT_eSPI** with exact GPIO pins from this board
2. **Initialize CST816D** on I2C (GPIO7, GPIO15)
3. **Set up battery monitoring** on ADC (if firmware adds voltage sense)
4. **Implement backlight PWM** on GPIO6 (brightness control)
5. **Handle SD card** on shared SPI bus (GPIO1, GPIO2, GPIO38, GPIO42)

### Power Management
- Use **Light-sleep mode** for idle display (240 µA total)
- Use **Deep-sleep mode** for background monitoring (10–170 µA)
- Monitor battery voltage via ADC (add external resistor divider if needed)

### Hardware Expansion
- **Reserved GPIO**: GPIO4–5, GPIO8–14, GPIO18, GPIO21, GPIO45–46
- **Recommended**: UART on GPIO43/44 for debug serial (already USB, but alternative)
- **Future**: PWM on GPIO11–13 for RGB LEDs, ADC on GPIO4–5 for sensors

### Thermal Considerations
- Continuous Wi-Fi TX can heat ESP32-S3 to 60–70°C
- Backlight adds ~0.5W heat
- Enclosure design should allow air circulation

---

## Troubleshooting Guide

### Common Issues

**USB Not Recognized**
- Check Type-C cable (data lines not just power)
- Verify USB driver installed (CH340 or similar)
- Hold BOOT button while plugging in (forces download mode)

**Display Blank**
- Check FPC ribbon cable seated properly (both ends)
- Verify backlight GPIO6 is driven high (PWM enabled)
- Reset ESP32 and check LCD initialization in logs

**Touch Not Working**
- Verify CST816D I2C address (0x15 or 0x14)
- Check GPIO7/15 have pull-up resistors (on module)
- Confirm GPIO16 reset is released (held high)
- Monitor GPIO17 interrupt signal

**Battery Not Charging**
- Check USB VBUS is 5V (multimeter)
- Verify battery connector polarity (red=+, black=-)
- Look for ETA6096 charging LED (on when charging)
- Test with different USB power adapter (≥500mA)

**Random Resets**
- Add bulk capacitors near ETA6096 output (if missing)
- Check for loose FPC ribbon cable (vibration resets)
- Verify CHIP_PU (reset) line not floating

---

## Related Documentation

- **Waveshare Product Page**: https://www.waveshare.com/esp32-s3-lcd-driver-board.htm
- **CST816D Datasheet**: Touch controller specifications
- **ST7789T3 Datasheet**: LCD display controller
- **ETA6096 Datasheet**: Battery management IC
- **ESP32-S3 Reference Manual**: (Link to Espressif docs)

---

## Revision History

### Board Version
- **Latest**: Waveshare ESP32-S3 LCD Driver Board (2024–2025)
- **Variant**: Includes ETA6096 + integrated backlight circuit

### Documentation
- Created: 2026-07-15
- Based on: Waveshare official schematic
- For: KeychainOS Project
