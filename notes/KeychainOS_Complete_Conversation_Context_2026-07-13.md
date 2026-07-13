# KeychainOS Complete Conversation Context

**Owner:** Sagar Mirajkar  
**Last consolidated:** 13 July 2026  
**Purpose:** Durable context for GitHub Copilot and future Copilot chats across laptops.

---

## 1. Core Motivation

The project exists to solve the recurring thought:

> “Damn, I wish I had a computer right now.”

The goal is not to carry a fast laptop or replace a phone. The goal is to have an always-available device that performs tasks a phone cannot reliably perform, while extracting full value from hardware already being carried for a smart keychain device.

The device is best described as:

> An instant, low-power ESP32 utility device with an on-demand Linux performance subsystem.

The Linux SBC is not the primary interface and should not remain on continuously. The ESP32-S3 is the primary, always-available brain. The Linux SBC is a second brain or accelerator that powers on only for Linux-class workloads.

---

## 2. Product Identity

KeychainOS should feel like a finished personal product, not:

- An ESP32 demonstration
- A collection of hardware examples
- A tiny laptop for its own sake
- A Linux desktop shrunk onto a small screen

It should feel like:

- A pocket utility computer
- A universal remote
- A small retro console
- A local media and information device
- An emergency Linux computer
- A portable IoT/development toolkit

The realistic physical target is a **pocket utility computer with a keyring attachment**, rather than a conventional house-key-sized keychain.

---

## 3. Processor Architecture

### ESP32-S3: Primary brain

The ESP32-S3 should normally be on and provide:

- Instant user interface
- Display and touch
- Buttons and joystick
- Battery status and power management
- NFC
- IR receive and transmit
- Audio
- Sensors
- Vibration
- Local microSD access
- Notes and quick tools
- Simple games
- Radxa power and status control
- Control Centre

### Radxa Zero 3W: On-demand second brain

The preferred Linux SBC became the **Radxa Zero 3W**, ideally with at least **2 GB RAM**. eMMC is preferred but not mandatory. The 1 GB/no-eMMC model was considered but 2 GB was identified as the better future-proof choice.

The Radxa should handle:

- DietPi/Linux
- Terminal and SSH
- Python
- Git and Linux utilities
- ESP flashing and serial tools
- USB-heavy operations
- Larger file processing
- Torrent/download jobs
- GBA and heavier retro emulation
- Doom/Road Rash-type workloads
- Occasional desktop/browser tasks when a phone cannot perform them

The Radxa should have three logical states:

1. **Off** — normal ESP-only mode
2. **Background Linux** — headless downloads, scripts, services
3. **Interactive Linux** — gaming, terminal, flashing, desktop tools

A torrent cannot continue if the Radxa is powered off. For prolonged torrents, downloads or heavy gaming, external USB power is recommended.

Linux must finish a clean shutdown before the ESP32 cuts Radxa power.

---

## 4. SBC Research and Decision History

### Raspberry Pi Zero 2 W

Advantages considered:

- Mature ecosystem
- Strong Raspberry Pi documentation
- Good RetroPie history
- Broad tutorials
- First-class DietPi support

Weaknesses:

- Only 512 MB RAM
- Weak desktop/browser experience
- Limited future headroom for mixed Linux, browser and emulator workloads

### Radxa Zero 3W

Advantages:

- RK3566 Cortex-A55 platform
- More CPU/GPU headroom
- RAM options beyond 512 MB
- Better fit for mixed Linux and retro workloads
- Optional eMMC on some variants

Risks:

- Less mature ecosystem than Raspberry Pi
- Board-specific Linux issues may be harder to diagnose
- It may be difficult to distinguish a DietPi issue, Radxa support issue and user configuration issue

Current conclusion:

- Radxa Zero 3W remains the preferred future SBC if a 2 GB or better variant can be sourced at a sensible price.
- RAM matters more than eMMC: 2 GB + good microSD is preferred over 1 GB + eMMC.
- DietPi support is now believed viable enough to treat the Radxa as a serious option, but hardware purchase should be delayed until the ESP/display front end is proven.

---

## 5. Gaming Architecture

Original intention included RetroPie-like gaming, which explains the joystick and physical buttons.

The initial concept of starting a game on ESP and dynamically migrating it to Radxa if performance dropped was examined and rejected for V1. Seamless migration would require compatible emulators, memory state, save formats, audio/input synchronisation and display handover.

Use static assignment before launch:

- Snake/Tetris/Pong/simple games → ESP32
- Most GBA, Doom, Road Rash/PS1-era games → Radxa

The launcher may decide or present an engine choice before the game starts. Do not attempt live handoff in V1.

---

## 6. Core ESP Hardware Decision

The original ESP was an ESP32-S3 N16R8 DevKit, but loose wires created repeated display reliability problems.

The selected core is now:

**Waveshare ESP32-S3 LCD Driver Board**

- ESP32-S3-WROOM-1-N8R8
- 8 MB flash
- 8 MB PSRAM
- USB-C
- 18-pin SPI display connector
- 40-pin display connector
- Battery connector
- ETA6096 battery management
- Onboard I/O expansion

Why this was selected:

- Stable FPC/ribbon display connection
- Removes loose display wiring
- Integrates battery connector and charging management
- Maintains 8 MB PSRAM
- 8 MB flash is considered sufficient because large assets belong on SD
- Makes the device closer to a final handheld product

The old N16R8 DevKit should be kept as a backup, experimentation platform and reference for a future custom PCB.

---

## 7. Display and Storage Hardware

### Display

**Waveshare 2-inch Capacitive Touch LCD**

- 240 × 320
- IPS
- ST7789T3 display controller
- CST816D/CST816-family capacitive touch controller
- Display uses SPI
- Touch uses I2C
- Onboard TF/microSD slot
- 15-pin header interface and 18-pin FPC interface

### FPC cable

- 18 pins
- 0.5 mm pitch
- Contact orientation must be physically verified
- Type A means same-side contacts
- Type B means opposite-side contacts
- Do not assume Type B until checking the contact sides in both ZIF connectors

### Two-card storage architecture

ESP/display microSD:

- Themes
- Icons
- Images
- Music
- Notes
- Simple games
- IR profiles
- Settings
- Logs and saves

Radxa microSD/eMMC:

- DietPi/Linux OS
- Linux applications
- Larger ROMs
- Downloads/torrents
- Development tools
- Computer-mode files

A reputable Class 10/A1 card is adequate for the ESP/display side. An A2/U3/V30 card is preferred for Linux because random small-file performance matters more than simple sequential speed.

---

## 8. Official LCD Driver Board Pin Mapping

```cpp
#define SPI_MISO 42
#define SPI_MOSI 2
#define SPI_SCLK 1

#define SD_CS 38

#define LCD_CS 39
#define LCD_DC 41
#define LCD_RST 40
#define LCD_BL 6

#define TP_INT 17
#define TP_RST 16
#define TP_SDA 15
#define TP_SCL 7
```

The ribbon cable handles physical routing but does not automatically configure a graphics library. The relevant GPIO assignments still have to be defined in TFT_eSPI, Arduino_GFX or other software.

The 18 FPC contacts include GPIO-controlled signals plus power, ground and possibly unused/support contacts. Not all 18 contacts need software definitions.

---

## 9. Display Library Findings

### Confirmed working baseline

All tested **TFT_eSPI examples are working correctly**.

This proves:

- Display hardware works
- Ribbon/FPC path works
- Backlight works
- SPI/control pins work
- The LCD Driver Board is functional

### Problems with other graphics libraries

Sketches using other libraries have produced:

- Blank screen
- No backlight
- Wrong scaling
- Wrong position or offsets
- Incorrect panel geometry

Sometimes an old image remained after flashing a new sketch. This is explained by the ST7789 display retaining the previous frame in its own display RAM while still powered. If the new sketch does not initialise and clear the display, the old image can remain even though the ESP firmware has changed.

Current software decision:

> TFT_eSPI is the known-good KeychainOS v0.1 graphics baseline.

Do not switch to Arduino_GFX or LVGL merely because examples exist. LVGL can be introduced later using a proven TFT_eSPI display backend.

### Library naming clarification

The Arduino library may appear as:

- Library Manager: `GFX Library for Arduino`
- Repository name: `Arduino_GFX`
- Header: `Arduino_GFX_Library.h`

These naming differences are normal. However, duplicate ZIP and Library Manager installations can cause Arduino to select the wrong version.

---

## 10. Known-Good Display Startup Philosophy

At every boot, the main firmware should deterministically:

1. Deselect LCD and SD chip-select lines
2. Hold or manage backlight intentionally
3. Initialise TFT_eSPI
4. Set correct rotation
5. Clear display RAM
6. Turn on backlight
7. Draw the KeychainOS splash/home screen

Do not rely on whatever frame was left in the ST7789.

The known-good TFT_eSPI `User_Setup.h`, Arduino IDE version, ESP32 board-package version, TFT_eSPI version, board selection, flash size, PSRAM setting, SPI frequency, rotation and inversion setting must be saved in the repository.

---

## 11. KeychainOS v0.1 UI

Screen hierarchy:

```text
BOOT
└── HOME
    ├── FILES
    ├── GAMES
    │   └── SNAKE
    ├── NOTES
    ├── CONTROL CENTRE
    └── SETTINGS
        ├── BRIGHTNESS
        └── ABOUT
```

### Home

- Clock
- Battery
- KeychainOS title
- Files
- Games
- Notes
- Control Centre
- Settings
- SD status

### Files

Initial mock entries:

- Music
- Downloads
- Images
- Games
- Themes

A real read-only file browser comes later.

### Games

- Snake first
- Tetris
- Pong
- Flappy Bird
- Others show “Coming Soon” initially

Snake is primarily a display refresh, input latency, touch/controls and memory test.

### Notes

Initially static; later SD-backed.

### Control Centre

- Battery
- SD
- Wi-Fi
- Bluetooth
- Linux status
- USB mode
- Future torrent/download status

### Settings

- Brightness
- Theme
- Volume
- About

### About

- KeychainOS version
- ESP32-S3
- 8 MB flash
- 8 MB PSRAM
- ST7789T3
- CST816D
- SD state

---

## 12. SD Card Structure

```text
KEYCHAIN/
├── config/
├── games/
├── music/
├── images/
├── icons/
├── themes/
├── notes/
├── downloads/
├── logs/
├── remotes/
└── saves/
```

Example settings file:

```json
{
  "theme": "default-dark",
  "brightness": 80,
  "volume": 60,
  "rotation": 0
}
```

ArduinoJson was selected to save and load structured settings rather than manually handling many independent variables.

---

## 13. Integrated Peripheral Intentions

The intended core includes:

- Display and touch
- Display-side microSD
- Joystick and buttons
- Speaker and MAX98357 I2S amplifier
- IR receiver
- IR transmitter/blaster array
- NFC reader
- Accelerometer/gyroscope
- Compass
- Vibration motor
- Battery
- USB-C

Important correction from earlier discussions:

> The IR receiver is integrated in the core; it is not a dockable module.

The system must keep a GPIO allocation sheet before integrating modules. Native ESP32 pins should be reserved for time-sensitive functions such as I2S, UART, IR/RMT and high-speed buses. The onboard I/O expander is more suitable for slow buttons, status and enable signals.

---

## 14. Power Architecture

The LCD Driver Board includes an MX1.25 battery connector and ETA6096 charging/power-management circuitry. This can potentially eliminate a separate TP4056 for the ESP/display subsystem, but physical battery-only, USB-only and charge-while-running tests are still required.

Do not assume the LCD Driver Board power circuit should power the entire Radxa subsystem. The Radxa needs a robust switched 5 V rail capable of startup current and sustained load.

Likely final arrangement:

```text
Single protected LiPo battery
├── ESP/display rail
└── Switched 5 V Radxa rail
```

Extended Radxa gaming/downloads should normally be used while connected to a charger.

---

## 15. USB Architecture

The final goal is one externally exposed USB-C port for:

- Charging
- ESP programming from external PC
- ESP-side storage access
- USB keyboard/mouse/gamepad/pendrive
- Radxa storage access when requested
- Linux console/maintenance

Do not attempt to expose ESP SD, Radxa SD and Radxa eMMC simultaneously in V1.

Use explicit modes:

1. Charge Only
2. ESP Programming
3. ESP Storage
4. OTG Host
5. Radxa Storage
6. Linux Console

ESP should own the normal low-power experience. Radxa should wake only when genuinely needed.

---

## 16. ESP-to-Radxa Communication

UART is the recommended V1 control plane:

```text
ESP TX → Radxa RX
ESP RX ← Radxa TX
Common GND
```

Use UART for:

- Wake/power requests
- Boot status
- Launch commands
- Torrent/download progress
- Shutdown confirmation
- Logs and small configuration data

Do not depend on UART for large media transfers. A future high-speed data plane may use USB, Wi-Fi or another validated interface.

---

## 17. Development Roadmap

### Phase 0 — Core validation

- Freeze TFT_eSPI `User_Setup.h`
- Record all library and board versions
- Backlight diagnostic
- Display diagnostic
- Touch diagnostic
- SD read/write diagnostic
- Combined test only after independent tests pass

### Phase 1 — KeychainOS shell

- Splash
- Home
- Files mock-up
- Games mock-up
- Notes
- Settings
- Control Centre

### Phase 2 — Local storage

- Create SD structure
- Settings JSON
- Read-only file browser
- Icons/images from SD
- Card-removal/error handling

### Phase 3 — Controls and game validation

- Touch navigation
- Physical joystick and buttons
- Snake
- Frame-rate and input-latency testing

### Phase 4 — Peripherals one at a time

1. Motion sensor
2. Physical controls
3. Audio
4. IR receiver/transmitter
5. NFC
6. Vibration

### Phase 5 — Power and enclosure

- Battery runtime
- Charge-while-running
- Heat
- Physical stack
- One-handed operation
- FPC strain relief

### Phase 6 — Radxa

- Power switching
- UART protocol
- Linux service
- Status reporting
- Clean shutdown
- ESP flashing tools
- Game launcher
- Background downloads

---

## 18. Features Deferred Beyond V1

- Custom Linux distribution
- Live game migration between ESP and Radxa
- All storage volumes exposed simultaneously over one USB-C port
- Full desktop replacement
- Kodi-first experience
- FM radio
- Complex theme engine
- Sophisticated modular add-ons
- Automatic processor selection based on live load

These are not necessarily rejected forever, but they must not block the first usable device.

---

## 19. Commercial/Product Impression Discussion

As a finished stable product, the likely Indian positioning discussed was:

- ESP32 Core edition: approximately ₹9,999–₹12,999
- ESP32 + Radxa Pro edition: approximately ₹19,999–₹24,999
- Premium eMMC edition: approximately ₹24,999–₹27,999

Most natural audiences:

- Makers and IoT developers
- Technology professionals
- Field technicians
- Gadget enthusiasts
- Retro gaming users
- Smart-home users

The commercial message is not the processor specification. It is:

> A pocket utility that is instant like a gadget, but becomes a real computer when a phone cannot finish the job.

---

## 20. Repository Strategy

The GitHub repository should become the durable source of truth.

Recommended root structure:

```text
KeychainOS/
├── assets/
├── config/
├── docs/
├── firmware/
├── hardware/
├── notes/
├── research/
├── sd-card/
├── README.md
├── vision.md
├── current-status.md
├── ideas.md
└── .gitignore
```

### Three layers of memory

1. `notes/chat-history/` — raw discussion archive
2. `docs/` — distilled architecture, hardware, roadmap and lessons
3. `current-status.md` — concise authoritative current truth

GitHub Copilot Chat can read committed files as repository context, but it does not automatically save chat content into Markdown. Raw chats and distilled decisions must be explicitly committed.

Recommended repository instruction file:

```text
.github/copilot-instructions.md
```

Core instructions should include:

- Treat `current-status.md` as authoritative
- TFT_eSPI is the known-good display baseline
- Do not replace TFT_eSPI unless explicitly requested
- Target 240 × 320 Waveshare ESP32-S3 LCD Driver Board hardware
- Do not reassign fixed display/touch/SD pins
- Do not add LVGL during v0.1
- Keep diagnostics independent
- Do not present untested ideas as confirmed
- Radxa remains optional and power-gated
- Linux must shut down cleanly before power removal

---

## 21. Current Confirmed State

### Confirmed

- Waveshare ESP32-S3 LCD Driver Board selected as core
- Waveshare 2-inch capacitive touch LCD selected
- Firmware upload works through Arduino IDE
- TFT_eSPI examples render correctly
- Ribbon/FPC and display hardware work with TFT_eSPI
- Backlight works under known-good TFT_eSPI setup
- Official board pins are known

### Known inconsistent

- Some Arduino_GFX/other-library sketches produced blank output, no backlight, wrong scaling or wrong offsets
- Old display frame can persist when a new sketch fails to initialise the LCD

### Immediate next actions

1. Work from the home laptop
2. Generate the fresh GitHub repository structure
3. Recreate/upload the repository correctly with real README files in directories
4. Copy the known-good TFT_eSPI `User_Setup.h`
5. Record exact versions/settings
6. Run independent display, touch and SD diagnostics
7. Build the fake KeychainOS home interface

---

## 22. Historical Corrections and Superseded Ideas

These must not be mistaken for current truth:

- **Superseded:** ESP32-S3 SuperMini/N16R8 DevKit as the final core  
  **Current:** Waveshare ESP32-S3 LCD Driver Board

- **Superseded:** IR receiver as a dockable module  
  **Current:** IR receiver integrated

- **Superseded:** Radxa always on for USB tasks  
  **Current:** ESP is primary; Radxa powers on only when needed

- **Superseded:** Seamless live game migration  
  **Current:** Select ESP or Radxa before launch

- **Superseded:** Arduino_GFX as assumed baseline  
  **Current:** TFT_eSPI is the proven baseline

- **Superseded:** Treating the device as a literal house-key-sized keychain  
  **Current:** Pocket utility computer with keyring attachment

---

## 23. Final Design Principle

Use the simplest hardware and software path that reliably delivers a feature the owner will actually use.

The project succeeds when the device is stable enough that, during a real situation where a phone cannot complete the task, KeychainOS provides a dependable next option without requiring a laptop.
