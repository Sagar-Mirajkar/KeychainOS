# ESP32-S3 Technical Reference

## Official Documentation

### Espressif Resources
- **Datasheet v2.2**: https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf
- **Technical Reference Manual**: https://www.espressif.com/en/support/documents/technical-documents
- **Hardware Design Guidelines**: https://www.espressif.com/en/support/documents/technical-documents
- **Series SoC Errata**: https://www.espressif.com/en/support/documents/technical-documents
- **ESP-IDF Programming Guide**: https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/

### KeychainOS Variant: ESP32-S3-WROOM-1-N8R8

Your board uses the **Waveshare ESP32-S3 LCD Driver Board** with:
- **Part Number**: ESP32-S3-WROOM-1-N8R8
- **Flash**: 8 MB (Quad SPI)
- **PSRAM**: 8 MB
- **Package**: QFN56 (7×7 mm)

---

## CPU & Processor

### Xtensa® Dual-Core 32-bit LX7
- **Clock Speed**: Up to 240 MHz
- **CoreMark Score**: 1329.92 (both cores @ 240 MHz)
- **Pipeline**: 5-stage
- **Data Bus**: 128-bit with SIMD instructions
- **FPU**: Single-precision floating point unit
- **Registers**: 64 physical general registers (windowed ABI)

### ULP Coprocessors
- **ULP-RISC-V**: RV32IMC instruction set, 32×32-bit registers
- **ULP-FSM**: Finite state machine for sensor measurement
- Both remain powered in Deep-sleep mode
- Can be used for low-power monitoring without waking main CPU

---

## Memory Organization

### Internal Memory
| Type | Size | Purpose | Retention |
|------|------|---------|-----------|
| ROM | 384 KB | Boot code, core functions | N/A |
| SRAM | 512 KB | Data & instructions @ 240 MHz | Powered down in Deep-sleep |
| RTC FAST | 8 KB | Main CPU access, traceable | Retained in Deep-sleep |
| RTC SLOW | 8 KB | CPU & coprocessor access | Retained in Deep-sleep |
| eFuse | 4096-bit | Encryption keys, device ID (1792 bits user) | Permanent (OTP) |

### External Memory Support
- **SPI Interfaces**: SPI0/1 for flash/PSRAM
- **Protocols**: Single, Dual, Quad, Octal SPI; QPI; OPI
- **Max Speed**: 120 MHz (8-line SPI SDR/DDR)
- **Max Capacity**: 1 GB total external flash + RAM

### Cache
- **Instruction Cache**: 16 KB (1 bank) or 32 KB (2 banks)
- **Data Cache**: 32 KB (1 bank) or 64 KB (2 banks)
- **Associativity**: 4-way or 8-way set associative
- **Block Size**: 16 or 32 bytes

---

## GPIO & Pin Configuration

### Total GPIO Pins: 45

**GPIO Pin Allocation**:
- **4 Strapping Pins**: GPIO0, GPIO3, GPIO45, GPIO46 (configured at boot)
- **6-7 Pins for In-Package Memory**: Used for flash/PSRAM SPI (avoid for general use)
- **Remaining**: ~32 pins available for user applications

### Pin Types
1. **IO Pins with IO MUX Functions**: Direct peripheral connections (fastest)
2. **GPIO Pins via GPIO Matrix**: Flexible routing (slight latency)
3. **RTC GPIO Pins**: Available during Deep-sleep
4. **Analog Pins**: ADC, touch sensors, USB, crystal oscillators

### Pin Voltage Levels
| Power Domain | Voltage | IO Pins |
|--------------|---------|---------|
| VDD3P3 | 3.3V | GPIO0-21 (RTC domain) |
| VDD3P3_CPU | 3.3V | GPIO38-46 (CPU domain) |
| VDD_SPI | 1.8V or 3.3V | GPIO26-37 (Flash/PSRAM domain) |
| VDDA | 3.3V | Analog domain |

---

## KeychainOS Pin Mapping

### LCD Display (SPI) - TFT_eSPI Baseline
| Function | GPIO | Pin Type | Purpose |
|----------|------|----------|---------|
| LCD_SCLK | GPIO1 | SPI | Shared SPI clock |
| LCD_MOSI | GPIO2 | SPI | Data out (MOSI) |
| LCD_MISO | GPIO42 | SPI | Data in (MISO) |
| LCD_CS | GPIO39 | SPI | Chip select |
| LCD_DC | GPIO41 | SPI | Data/Command select |
| LCD_RST | GPIO40 | SPI | Display reset |
| LCD_BL | GPIO6 | GPIO | Backlight PWM control |

### Touch Sensor (I2C) - CST816D Controller
| Function | GPIO | Pin Type | Purpose |
|----------|------|----------|---------|
| TP_SDA | GPIO15 | I2C | I2C data |
| TP_SCL | GPIO7 | I2C | I2C clock |
| TP_RST | GPIO16 | GPIO | Touch reset |
| TP_INT | GPIO17 | GPIO | Touch interrupt |

### SD Card (SPI) - Shared Bus
| Function | GPIO | Pin Type | Purpose |
|----------|------|----------|---------|
| SD_CS | GPIO38 | SPI | SD card chip select |
| SD_CLK | GPIO1 | SPI | Shared with LCD |
| SD_MOSI | GPIO2 | SPI | Shared with LCD |
| SD_MISO | GPIO42 | SPI | Shared with LCD |

### Recommendations for Future Expansion
| Use Case | Recommended GPIO Range | Notes |
|----------|----------------------|-------|
| UART | GPIO43, GPIO44, GPIO17, GPIO18 | Already assigned to serial/alt functions |
| ADC | GPIO1-14 | RTC domain ADC1/ADC2 channels |
| PWM | Any GPIO | LED PWM controller, 8 channels |
| Touch Buttons | GPIO1-14 | 14 capacitive-sensing GPIO available |
| I2S Audio | GPIO7-10, GPIO45-48 | For future speaker/audio codec |

---

## Electrical Characteristics

### Power Consumption

#### Active Mode (Wi-Fi + Bluetooth Off)
- **CPU @ 240 MHz (both cores idle)**: ~32.9 mA
- **CPU @ 240 MHz (single core, 32-bit ops)**: ~51.2 mA
- **CPU @ 240 MHz (dual core, 128-bit ops)**: ~91.7 mA

#### Wi-Fi Transmission (Active Mode)
| Standard | Power | Current | Sensitivity |
|----------|-------|---------|-------------|
| 802.11b @ 21 dBm | 1 Mbps | 340 mA | –98.4 dBm |
| 802.11g @ 19 dBm | 54 Mbps | 291 mA | –76.5 dBm |
| 802.11n HT20 @ 18.5 dBm | MCS7 | 283 mA | –74.2 dBm |

#### Bluetooth LE (Active Mode)
| Power | TX Current | RX Current |
|-------|-----------|-----------|
| 21 dBm | 335 mA | 93 mA |
| 0 dBm | 176 mA | 93 mA |
| –15 dBm | 116 mA | 93 mA |

#### Low Power Modes
| Mode | Current | Notes |
|------|---------|-------|
| **Modem-sleep** @ 240 MHz | 32.9–91.7 mA | CPU/Wi-Fi on, reduced clock |
| **Light-sleep** | 240 µA | CPU off, RTC on, wake via timer/interrupt |
| **Deep-sleep** (RTC only) | 7 µA | All off except RTC |
| **Deep-sleep** (ULP-FSM active) | 170 µA | Low-power sensor monitoring |
| **Off** (CHIP_PU low) | 1 µA | Powered down |

### Power Supply Recommendations
| Domain | Min | Typ | Max | Notes |
|--------|-----|-----|-----|-------|
| VDDA, VDD3P3 | 3.0V | 3.3V | 3.6V | Main analog/logic supply |
| VDD3P3_RTC | 3.0V | 3.3V | 3.6V | RTC always powered |
| VDD3P3_CPU | 3.0V | 3.3V | 3.6V | CPU/digital domain |
| VDD_SPI | 1.8V or 3.3V | — | — | Flash/PSRAM supply |
| Total Supply Current | — | — | 500 mA+ | Single PSU recommended |

### GPIO DC Characteristics (3.3V, 25°C)
| Parameter | Min | Typ | Max | Unit |
|-----------|-----|-----|-----|------|
| VOH (high output) | 0.8 × VDD | — | — | V |
| VOL (low output) | — | — | 0.1 × VDD | V |
| IOH (source current) | — | 40 | — | mA |
| IOL (sink current) | — | 28 | — | mA |
| Internal Pull-up | — | 45 | — | kΩ |
| Internal Pull-down | — | 45 | — | kΩ |

---

## Peripherals Used in KeychainOS

### SPI Controllers (LCD + SD)
- **SPI0/1**: Reserved for in-package flash/PSRAM
- **SPI2**: General purpose, used for LCD & SD card
- **SPI3**: Available for future expansion
- **Max Clock**: 80 MHz (SPI2/3 general use), 120 MHz (SPI0/1 flash)

### I2C Controllers
- **I2C0**: Used for CST816D touch sensor
- **I2C1**: Available for future sensors
- **Max Speed**: 400 kbit/s (standard), up to 800 kbit/s with strong pull-ups

### UART Controllers
- **UART0**: Debug/serial, GPIO43 (TX), GPIO44 (RX)
- **UART1**: Available for future use
- **UART2**: Available for future use
- **Max Speed**: 5 Mbps

### Analog-to-Digital Conversion (ADC)
- **Two 12-bit SAR ADCs**: ADC1 (9 channels), ADC2 (11 channels)
- **Resolution**: 12-bit
- **Sampling Rate**: Up to 100 kSPS
- **Voltage Range**: 0–3.3V (configurable attenuation)
- **Channels**: GPIO1-14 (RTC domain)

### Touch Sensor
- **14 Capacitive-sensing GPIO**: GPIO1-14
- **Controller**: CST816D (external, on LCD driver board)
- **Interface**: I2C @ GPIO15 (SDA), GPIO7 (SCL)

### LED PWM Controller
- **8 Channels**: Independent frequency/duty control
- **Max Frequency**: 40 MHz internal clock source
- **Resolution**: Up to 14 bits
- **Use**: Backlight control (GPIO6), RGB LEDs, etc.

### RMT (Remote Control Peripheral)
- **4 TX Channels**: IR transmit
- **4 RX Channels**: IR receive
- **Shared 384×32-bit RAM**: Across all 8 channels
- **Modulation**: Supported on TX

### GDMA (General-Purpose DMA)
- **5 TX Channels + 5 RX Channels**: Independent or shared
- **Dynamic Priority**: Configurable
- **Peripherals**: SPI2, SPI3, I2S, LCD/CAM, SHA, AES, ADC, RMT

---

## RF Characteristics

### Wi-Fi
- **Standard**: IEEE 802.11 b/g/n
- **Frequency**: 2.4 GHz (2412–2484 MHz)
- **Bandwidth**: 20 MHz, 40 MHz
- **Data Rate**: Up to 150 Mbps (HT40, MCS7)
- **TX Power**: Up to +21 dBm (802.11b), +18 dBm (802.11n)
- **RX Sensitivity**: –98.4 dBm (802.11b 1 Mbps), –71.4 dBm (802.11n HT40 MCS7)

### Bluetooth LE
- **Bluetooth Version**: Bluetooth 5, Bluetooth Mesh support
- **TX Power**: Up to +20 dBm (configurable)
- **RX Sensitivity**: –104.5 dBm (125 Kbps), –97.5 dBm (1 Mbps)
- **Data Rates**: 125 Kbps, 500 Kbps, 1 Mbps, 2 Mbps
- **Features**: Multiple advertising sets, simultaneous central/peripheral

---

## Boot Configuration

### Strapping Pins (Sampled at Power-Up)
| GPIO | Function | Default | Effect |
|------|----------|---------|--------|
| GPIO0 | Boot mode | Pulled high | SPI boot (normal) |
| GPIO3 | JTAG source | Floating | USB Serial/JTAG (default) |
| GPIO45 | VDD_SPI voltage | Pulled low | 3.3V (default) |
| GPIO46 | ROM print output | Pulled low | UART0 + USB (default) |

**Important**: Do not leave strapping pins floating during power-up. The Waveshare board handles these internally.

### Boot Modes
1. **SPI Boot** (normal): Load firmware from flash, execute
2. **Download Boot**: Accept firmware over UART/USB, store to flash
3. **OTA Updates**: Firmware updates via Wi-Fi/Bluetooth

---

## Security Features

### Hardware Acceleration
- **SHA**: SHA-1, SHA-224, SHA-256, SHA-384, SHA-512 (FIPS PUB 180-4)
- **AES**: AES-128/256 encryption/decryption (FIPS PUB 197)
- **RSA**: Up to 4096-bit modular exponentiation
- **HMAC**: RFC 2104 compliant
- **RNG**: True random number generator (hardware)

### Flash Encryption
- **Algorithm**: XTS-AES (IEEE Std 1619-2007)
- **Modes**: Manual or automatic encryption/decryption
- **Coverage**: External flash + PSRAM

### Secure Boot
- **Signature**: RSA-PSS
- **Root of Trust**: Hardware-based
- **Enforcement**: Only signed firmware boots

### Permission Control
- **Secure/Non-Secure Worlds**: Separate protection domains
- **Access Control**: Memory, peripherals, external storage
- **Monitoring**: Permission violation interrupts

---

## Timing & Reset

### Power-Up Sequence
| Parameter | Min | Typ | Max | Unit |
|-----------|-----|-----|-----|------|
| Power rail stabilization (tST_BL) | 50 | — | — | µs |
| CHIP_PU reset hold time (tRST) | 50 | — | — | µs |

### Voltage Thresholds
- **CHIP_PU High (VIH_nRST)**: 0.75 × VDD to VDD + 0.3V
- **CHIP_PU Low (VIL_nRST)**: –0.3V to 0.25 × VDD

### Reset Types
1. **CPU Reset**: Individual core reset
2. **Core Reset**: All digital + peripherals (keep RTC)
3. **System Reset**: Everything including RTC
4. **Chip Reset**: Full power cycle

---

## Pin Restrictions & Cautions

### Avoid Using These GPIO
| GPIO | Reason | Can Be Freed |
|------|--------|-------------|
| GPIO26–32 | In-package flash/PSRAM SPI | Only if external SPI used |
| GPIO33–37 | 8-line SPI mode (Octal) | Only if not using Octal SPI |
| GPIO39–42 | JTAG debugging | Yes, if JTAG disabled |
| GPIO43–44 | UART0 serial debug | Yes, if debug disabled |
| GPIO19–20 | USB Serial/JTAG | Yes, if USB disabled |
| GPIO0, GPIO45, GPIO46 | Strapping pins | After boot, can repurpose |
| GPIO3 | Strapping pin | After boot, can repurpose |

### Safe GPIO for User Applications
**Recommended free GPIO**: GPIO21, GPIO45, GPIO46 (after boot)

---

## Reliability & Testing

### JEDEC Qualifications
- **HTOL**: 125°C, 1000 hours (High Temperature Operating Life)
- **ESD**: ±2000V HBM, ±1000V CDM
- **TCT**: –65°C to +150°C, 500 cycles
- **Latch-up**: ±200 mA current trigger

### Memory Specifications
| Spec | Flash | PSRAM |
|------|-------|-------|
| Supply Voltage (3.3V) | 2.7–3.6V | 2.7–3.6V |
| Max Clock | 80 MHz | 80 MHz |
| Program/Erase Cycles | 100,000 | N/A |
| Data Retention | 20 years | — |

---

## Design Guidelines

### Minimum External Components
1. **Power Supply**: 3.3V ≥500mA capable, with bypass capacitors (100nF per rail)
2. **Reset Circuit**: CHIP_PU pull-up (10kΩ) + optional RC for debounce
3. **Crystal Oscillator**: 40 MHz main clock (critical for operation)
4. **Optional**: 32 kHz crystal for RTC accuracy

### PCB Considerations
- Separate analog/digital ground planes
- Short, low-impedance power traces
- Ground vias under QFN package
- Keep high-speed signals away from analog domains

### Thermal Management
- Junction temp range: –40°C to +105°C (ambient dependent)
- Typical thermal resistance: ~50°C/W (estimated)
- Ensure adequate heat sinking for continuous operation

---

## Version Information

### ESP32-S3 Datasheet Versions
- **Latest**: v2.2 (2026-03-05)
- **Your Variant**: ESP32-S3-WROOM-1-N8R8 (v0.2 chip revision)

### Related Espressif Documents
- ESP32-S3 Series SoC Errata
- ESP32-S3 Hardware Design Guidelines
- ESP-IDF Technical Reference Manual
- ESP RF Test Tool and Test Guide

---

## Quick Reference Links

### Official Documentation
- [Espressif Systems](https://www.espressif.com)
- [ESP32 Technical Documents](https://www.espressif.com/en/support/documents/technical-documents)
- [ESP-IDF Documentation](https://docs.espressif.com/)

### Community Resources
- [ESP32 BBS Forum](https://esp32.com)
- [Espressif GitHub](https://github.com/espressif)
- [ESP-FAQ](https://espressif.com/projects/esp-faq)

### KeychainOS Board-Specific
- [Waveshare ESP32-S3 LCD Driver Board](https://www.waveshare.com/esp32-s3-lcd-driver-board.htm)
- [CST816D Touch Controller Datasheet](Pending)
- [ST7789T3 Display Controller Datasheet](Pending)

---

## Notes for KeychainOS Development

### TFT_eSPI Configuration
Your setup uses **TFT_eSPI** as the proven graphics baseline. Pin configuration in `config/`:
- Display: GPIO1, GPIO2, GPIO39, GPIO40, GPIO41, GPIO42, GPIO6
- Touch: GPIO7, GPIO15, GPIO16, GPIO17
- SD Card: GPIO38 (shared SPI bus)

### Power Budget Estimate
- **Idle (display on)**: ~50 mA
- **Light UI interaction**: ~80–120 mA
- **Wi-Fi scanning**: ~100–150 mA
- **Full Wi-Fi TX/RX**: 280–340 mA
- **Deep-sleep (RTC only)**: 7 µA

With typical 1000–2000 mAh battery, expect 5–40 hour runtime depending on usage.

### Development Tools
- **Upload**: esptool.py via USB-C CDC
- **Monitor**: Serial terminal @ 115200 baud
- **Debugging**: JTAG via USB Serial/JTAG (GPIO39–42 if enabled)
- **OTA**: Wi-Fi firmware updates (future)
