# Battery & Power Management for KeychainOS

## Overview

KeychainOS is powered by a **1S LiPo battery** (3.7V nominal) managed by the **ETA6096 battery manager IC**. This document covers power optimization, battery management, charging, and sleep modes.

---

## Power Distribution & Architecture

### Power Supply Chain
```
USB 5V (external)  ──┐
                      ├──→ ETA6096 Battery Manager ──→ 3.3V Regulated Output
LiPo 3.7V (J2) ─────┘
                
3.3V Output Distribution:
├─ VDD3P3 (ESP32-S3 main) ──→ CPU, Memory, RF
├─ VDD3P3_RTC (RTC domain) ──→ RTC, touch controller
├─ Display + Backlight ────→ ~80-100 mA @ full brightness
├─ Touch Controller (I2C) ──→ ~5 mA
└─ I/O & Peripherals ──────→ Variable
```

### Voltage Rails
| Rail | Voltage | Max Current | Source | Protection |
|------|---------|-------------|--------|------------|
| VBUS | 5V | 2A | USB Type-C | TVS diode, poly fuse |
| VBAT | 3.7V nominal | 2A discharge | LiPo battery | ETA6096 (charge/discharge control) |
| VDD3P3 | 3.3V regulated | ~500 mA | ETA6096 regulator | Over-current protection |
| VSYS | 3.3V (internal) | All peripherals | Regulated | Per-domain control |

---

## Battery Specifications

### Typical Specifications
```
Chemistry: Lithium Polymer (LiPo)
Cells: 1S (single cell)
Nominal Voltage: 3.7V
Charge Voltage: 4.2V (max)
Discharge Cutoff: 2.5V (min)

Energy: Depends on capacity
├─ 1000 mAh: ~3.7 Wh
├─ 2000 mAh: ~7.4 Wh
└─ 3000 mAh: ~11.1 Wh
```

### Battery Selection Recommendations
```
For Pocket Device (KeychainOS):
├─ Capacity: 1000-2000 mAh
├─ Form Factor: 503560, 603450, or custom shape
├─ Discharge Rate: ≥1C (at least 1000 mAh for 1000 mAh battery)
├─ Brand: Reputable (Adafruit, Sparkfun, etc.)
└─ Certification: UL/CE marked (safest)
```

### State of Charge (SOC) vs Voltage
```
100% ─────── 4.20V (fully charged)
 90% ─────── 4.00V
 80% ─────── 3.90V
 50% ─────── 3.70V (nominal)
 20% ─────── 3.40V
  0% ─────── 2.50V (cutoff, avoid discharging below)
```

---

## Battery Charging

### Charging Circuit (ETA6096)
```
USB 5V Input
    │
    ├─ Input protection (diode + TVS)
    │
    ├─ Charge controller IC (ETA6096)
    │
    ├─ Status LED (Red/Orange) - Lights during charge
    │
    └─ LiPo battery (J2 connector)
       │
       └─ Over-charge protection
           Over-discharge protection
```

### Charging Parameters
- **Charge Current**: Typically 1A (depends on USB power supply)
- **Float Voltage**: 4.2V ± 50mV
- **Charge Time**: ~1-2 hours (1A charge rate, 1000 mAh battery)
- **Termination**: Auto-termination when current drops below threshold

### Charging Safety
```
DO:
✓ Use proper USB power adapter (≥500mA, ideally 1-2A)
✓ Use original or certified battery
✓ Monitor temperature during first charge (should be warm, not hot)
✓ Keep terminals clean
✓ Store battery in cool, dry place

DON'T:
✗ Force reverse polarity (will damage board)
✗ Charge from computer USB port (insufficient current)
✗ Charge for more than 24 hours continuously
✗ Use battery if bloated/swollen (fire hazard)
✗ Charge in extremely hot/cold conditions
✗ Short circuit battery terminals
```

### Charging LED Indicator
```
LED Status:
├─ OFF     → Not charging (fully charged or no battery)
├─ Red/Orange → Charging in progress
└─ Blinking → Fault condition (check connections)
```

---

## Current Consumption Profiles

### Scenario 1: Display On, No Radio (Typical UI Use)
```
Component           Current     Notes
─────────────────────────────────────────
ESP32-S3 Core      ~30 mA      CPU + digital circuits
Display + Backlight ~85 mA      ST7789 + LED backlight
Touch Sensor       ~5 mA       I2C polling
Misc. (decoupling) ~5 mA       Leakage, etc.
─────────────────────────────────────────
TOTAL              ~125 mA      Typical UI interaction

Battery Life (1000 mAh): 1000 ÷ 125 = ~8 hours
```

### Scenario 2: Wi-Fi Scanning (Connected Mode)
```
Component           Current     Notes
─────────────────────────────────────────
Base (Core + Display) ~125 mA   (from above)
Wi-Fi (RX scanning)   ~100 mA   Listening for packets
─────────────────────────────────────────
TOTAL              ~225 mA      Average

Battery Life (1000 mAh): 1000 ÷ 225 = ~4.4 hours
```

### Scenario 3: Wi-Fi Transmit (Peak Power)
```
Component           Current     Notes
─────────────────────────────────────────
Base                ~125 mA
Wi-Fi (TX @ 18dBm)   ~280 mA    802.11n transmission
─────────────────────────────────────────
TOTAL              ~405 mA      Peak (brief)

Duration: Usually a few seconds per transmission
Average (spread over time) much lower
```

### Scenario 4: Light Sleep (Minimal Power)
```
Component           Current     Notes
─────────────────────────────────────────
ULP Coprocessor    ~170 µA     Running sensor monitor
RTC Peripherals    ~8 µA       Real-time clock
Leakage            ~5 µA       Static current
─────────────────────────────────────────
TOTAL              ~183 µA     ~0.2 mA

Battery Life (1000 mAh): 1000 ÷ 0.2 = ~5,000 hours (~200 days)
```

### Scenario 5: Deep Sleep (Maximum Power Saving)
```
Component           Current     Notes
─────────────────────────────────────────
RTC Memory         ~8 µA       Retains data in sleep
Leakage            ~1 µA       Minimal current
─────────────────────────────────────────
TOTAL              ~9 µA       Ultra-low standby

Battery Life (1000 mAh): 1000 ÷ 0.009 = ~111,000 hours (~12.7 years!)
```

---

## Power Optimization Strategies

### Strategy 1: Display Management
```cpp
// Reduce backlight brightness
ledcWrite(0, 128);  // 50% brightness saves ~40 mA

// Turn off display when idle
tft.writecommand(0x28);  // ST7789 display OFF command
// Saves ~85 mA (full display power)

// Use low refresh rate
// Default: 60 Hz refresh
// Optimized: 15 Hz refresh for static screens
// Saves: ~20-30 mA
```

### Strategy 2: CPU Frequency Scaling
```cpp
// Default: 240 MHz
// setCpuFrequencyMhz(240);  // Full speed
// setCpuFrequencyMhz(160);  // Reduced speed
// setCpuFrequencyMhz(80);   // Low speed

// Example: 160 MHz saves ~25% power
setCpuFrequencyMhz(160);    // ~20-25 mA saved
```

### Strategy 3: Wireless Power Saving
```cpp
// Wi-Fi Active/Modem Sleep
WiFi.mode(WIFI_STA);
WiFi.setSleep(WIFI_PS_MODEM);  // Modem sleep (default)
// RF off while idle, restores connection automatically

// Complete Wi-Fi Off
WiFi.disconnect(true);  // Turn off Wi-Fi radio
// Saves: ~50-100 mA
```

### Strategy 4: Sleep Modes

#### Light Sleep (CPU Off, Peripherals On)
```cpp
esp_sleep_enable_timer_wakeup(10000000);  // Wake after 10 seconds
esp_light_sleep_start();
// Current: ~240 µA
// Wake time: <1 ms
// Use case: Waiting for user input, periodic checks
```

#### Deep Sleep (Everything Off Except RTC)
```cpp
esp_sleep_enable_timer_wakeup(60000000);     // Wake after 60 seconds
esp_sleep_enable_ext0_wakeup(GPIO_NUM_17, 0); // Wake on touch
esp_deep_sleep_start();
// Current: ~8-10 µA
// Wake time: ~200 ms (full system restart)
// Use case: Overnight standby, emergency monitoring
```

### Strategy 5: Selective Peripheral Power
```cpp
// Disable unused peripherals
periph_module_disable(PERIPH_RNGCHECK_MODULE);
periph_module_disable(PERIPH_LEDC_MODULE);
// Saves: ~5-10 mA combined
```

---

## Practical Battery Runtime Calculations

### Example 1: Typical Usage Pattern (KeychainOS v0.1)
```
Scenario: Office worker uses device throughout day

Hour 0-2:   Display UI interaction       ~125 mA
Hour 2-6:   Idle, periodic checks       ~240 µA (light sleep)
Hour 6-8:   Check Wi-Fi, transmit       ~300 mA (average)
Hour 8-10:  Display + UI                ~125 mA
Hour 10-16: Idle/off                    ~10 µA  (deep sleep)

Total consumption:
  = (2h × 125mA) + (4h × 0.24mA) + (2h × 300mA) 
    + (2h × 125mA) + (6h × 0.01mA)
  = 250 + 1 + 600 + 250 + 0.06
  = 1,101 mAh-hours

With 1000 mAh battery: 1000 ÷ 1,101 = ~0.9 days (Not quite)

With 2000 mAh battery: 2000 ÷ 1,101 = ~1.8 days ✓ (Realistic)
With 3000 mAh battery: 3000 ÷ 1,101 = ~2.7 days ✓ (Good)
```

### Example 2: Maximum Battery Life (Background Monitoring)
```
Scenario: Device monitoring with periodic Wi-Fi check

Hour 0-8:   Deep sleep, wake every 1 min to check sensors
            (0.1s active @ 30mA + 59.9s sleep @ 10µA)
            ≈ 0.05mA average

Hour 8-24:  Same as above

Total consumption:
  = 24h × 0.05mA
  = 1.2 mAh

With 1000 mAh battery: 1000 ÷ 1.2 = ~833 hours = ~35 days ✓
```

### Example 3: Maximum Performance (Full Wi-Fi Usage)
```
Scenario: Continuous Wi-Fi streaming/upload

Continuous operation at ~300 mA average

With 1000 mAh battery: 1000 ÷ 300 = ~3.3 hours
With 2000 mAh battery: 2000 ÷ 300 = ~6.7 hours
With 3000 mAh battery: 3000 ÷ 300 = ~10 hours
```

---

## Monitoring Battery Voltage

### Hardware Setup (Optional)
```
Add voltage divider to measure battery:
VBAT (3.7V) ─[10kΩ]─┬─[10kΩ]─ GND
                     │
                   [100nF cap]
                     │
                   GPIO4 (ADC)
```

### Firmware Code
```cpp
#define BATT_ADC_PIN GPIO_NUM_4
#define BATT_ADC_CHAN ADC1_CHANNEL_3

void setup() {
  analogSetAttenuation(ADC_11db);  // Full 3.3V range
  analogSetWidth(12);              // 12-bit (0-4095)
}

float readBatteryVoltage() {
  int raw = analogRead(BATT_ADC_PIN);
  
  // Convert ADC value to voltage
  // Voltage divider: R1=R2, so Vmeas = Vbat/2
  float voltage = (raw / 4095.0) * 3.3 * 2.0;
  
  return voltage;  // Returns voltage in volts
}

void monitorBattery() {
  float voltage = readBatteryVoltage();
  float percentage = map(voltage, 2.5, 4.2, 0, 100);  // Rough SOC estimate
  
  Serial.printf("Battery: %.2fV (%d%%)\n", voltage, percentage);
  
  if (voltage < 3.0) {
    Serial.println("WARNING: Low battery!");
    // Enter power-saving mode
  }
}
```

---

## Charging Best Practices

### First Time Charge
1. Connect to USB power adapter (500mA+ recommended)
2. Observe charging LED (should be red/orange)
3. Allow 2-3 hours for full charge (1000 mAh battery)
4. Do NOT use device while charging (normal, but optional)

### Daily Use
```
Best practice:
✓ Charge overnight (allows topping off)
✓ Charge when battery drops to 20% (extends cycle life)
✓ Use certified USB charger (>500mA)
✓ Unplug after fully charged (avoid overcharge)

Avoid:
✗ Completely draining battery regularly
✗ Charging from computer USB ports
✗ Leaving on charger indefinitely
✗ Charging in extreme temperatures
```

### Storage
```
Battery Care for Long-Term Storage:
├─ Charge to ~50% (not 100%, not 0%)
├─ Store in cool place (0-25°C ideal)
├─ Store in dry location (moisture damages cells)
├─ Check voltage every 3 months
├─ Recharge to 50% if voltage drops below 3.6V
└─ Dispose properly at end of life (Li-Po recycling)
```

---

## Power Management API (ESP32-S3 IDF)

### Sleep Mode Functions
```cpp
// Set wake-up sources
esp_sleep_enable_timer_wakeup(uint64_t time_in_us);  // Timer wake-up
esp_sleep_enable_ext0_wakeup(gpio_num_t gpio_num, uint32_t level); // GPIO wake-up
esp_sleep_enable_ext1_wakeup(uint64_t mask, esp_sleep_ext1_wakeup_mode_t mode);

// Enter sleep
esp_light_sleep_start();    // Light sleep (CPU off, RF may stay on)
esp_deep_sleep_start();     // Deep sleep (everything off except RTC)

// Get wake-up reason
esp_sleep_wakeup_cause_t cause = esp_sleep_get_wakeup_cause();
```

### CPU Frequency Control
```cpp
// Get current frequency
uint32_t freq = getCpuFrequencyMhz();

// Set CPU frequency
setCpuFrequencyMhz(240);    // Maximum performance
setCpuFrequencyMhz(160);    // Balanced (typical)
setCpuFrequencyMhz(80);     // Power saving
setCpuFrequencyMhz(40);     // Minimal (not recommended)
```

### Wi-Fi Power Save
```cpp
// Enable modem sleep (Wi-Fi RF off when not needed)
WiFi.setSleep(WIFI_PS_MODEM);

// Wake on receive (roams in sleep for incoming packets)
WiFi.setSleep(WIFI_PS_MIN_MODEM);

// Disable sleep (always on)
WiFi.setSleep(WIFI_PS_NONE);
```

---

## Troubleshooting Power Issues

### Device Dies Unexpectedly
```
Diagnosis:
1. Check battery voltage (should be 3.0-4.2V)
2. Look for charging LED (if plugged in)
3. Check for warm/hot spots (short circuit?)
4. Try reset button (hold 2 seconds)

Solutions:
- Charge battery fully
- Check USB power adapter (must be ≥500mA)
- Verify battery connector polarity
- Test with new battery if available
```

### Battery Won't Charge
```
Likely Causes:
1. USB cable not data-capable (just power)
2. Power adapter insufficient (<500mA)
3. Battery disconnected or reversed
4. Faulty battery (swollen, damaged)
5. ETA6096 IC failure (rare)

Fixes:
- Use quality USB-C cable with data lines
- Use 1-2A USB power adapter
- Check battery connector orientation
- Swap battery if available to test
- Contact manufacturer if still failing
```

### Rapid Battery Drain (Uses Battery Quickly)
```
Investigation:
1. Enable Wi-Fi power save: WiFi.setSleep(WIFI_PS_MODEM);
2. Reduce display brightness: ledcWrite(0, 100);
3. Reduce CPU frequency: setCpuFrequencyMhz(160);
4. Use sleep modes: esp_light_sleep_start();
5. Check for runaway loops (serial monitor shows high CPU %)

Optimization:
- Profile code to find power-hungry sections
- Use light sleep when waiting for input
- Disable Wi-Fi when not needed
- Reduce refresh rates on static screens
```

### Device Hot to Touch
```
Warning Signs:
- Device warm during normal use
- Too hot to hold (>50°C)
- Battery gets warm

Causes:
1. Continuous high CPU load
2. Maximum Wi-Fi transmission
3. Display at 100% brightness
4. Short circuit or fault

Actions:
1. Check CPU usage (should be <50% typical)
2. Reduce Wi-Fi usage or turn off
3. Lower backlight brightness
4. If still hot, power off and cool down
5. If persists, check for short circuit

Note: Some warmth (body-temp) is normal during active use.
```

---

## Battery Lifecycle & Maintenance

### Expected Lifespan
```
Typical Li-Po Battery Lifecycle:
├─ Charge cycles: 300-500 typical
├─ Calendar life: 3-5 years (even unused)
├─ Performance degradation: ~20% per year (unused)
├─ Capacity fade: ~5% per 100 cycles (normal)
└─ End-of-life: <80% capacity or physical damage
```

### Signs of Aging Battery
```
Symptoms:
✗ Runtime significantly shorter than before
✗ Battery swelling/bloating (DANGER - stop using!)
✗ Won't hold charge (dies quickly even when full)
✗ Charger LED not lighting (may need charging)
✗ Device won't power on despite "charging"

If Swollen:
1. STOP using immediately
2. Remove from device
3. Place outside away from people
4. Dispose at proper Li-Po recycling center
5. Do not throw in trash (fire hazard)
```

### Replacement
```
When to Replace:
- Battery no longer holds charge
- Can't run for expected time (2-3 hours minimum)
- Physical damage or swelling
- Performance degrades significantly

How to Replace:
1. Purchase compatible 1S LiPo battery
2. Power off device completely
3. Disconnect old battery from JST connector
4. Connect new battery (red=+, black=GND)
5. Charge to full before first use
```

---

## Related Documentation

- `docs/ESP32-S3-REFERENCE.md` — Microcontroller specs and power modes
- `hardware/BOARD-DESIGN.md` — ETA6096 battery manager details
- `docs/GETTING-STARTED.md` — Quick start guide

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-15 | 1.0 | Initial document creation |

---

## Questions & Support

For detailed questions:
1. Check ESP32-S3 Technical Reference Manual (Espressif)
2. Review ETA6096 datasheet (battery manager IC)
3. Post on ESP32 forums (esp32.com)
4. Open issue on GitHub (KeychainOS project)
