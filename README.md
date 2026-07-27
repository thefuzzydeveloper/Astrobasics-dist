# AstroBasics Diamond Chart Pro | Vedic Astrology Desktop Suite

[**Main Website / Online Portal**](https://thefuzzydeveloper/Astrobasics-website/) | [**GitHub Repository**](https://github.com/thefuzzydeveloper/Astrobasics-dist) | [**Download Windows Installer (.exe)**](https://github.com/thefuzzydeveloper/Astrobasics-dist/releases/download/v-final-installer/astrobasics_installer.exe) | [**Download Android App (.apk)**](https://github.com/thefuzzydeveloper/Astrobasics-dist/releases/download/v-final-installer/AstroBasics.apk)

---

## Overview

AstroBasics Diamond Chart Pro is an offline, private Vedic Astrology (Jyotish) desktop application. Started as an effort to visualize astrology, it provides high-precision calculations, flexible chart rendering, multi-varga diagnostic tools, and structured analysis modules.

The application offers both **Swiss Ephemeris (`swisseph`) astronomical calculation support** and **pure J2 offline mathematical fallbacks**. It features an interactive Diamond chart visualizer, custom rule builders, multi-level dasha trees, and trilingual interface options (English, Hindi, Sanskrit).

---

## Key Feature Highlights

### 1. Six-Pillar Kundali Milan Engine
A comprehensive matchmaking architecture evaluating structural, psychological, and karmic compatibility:
* **Pillar 1: Ashtakoota Matrix (36 Points)** – Computes Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, and Nadi with step-by-step mathematical breakdown.
* **Pillar 2: Pāpasāmya Matrix (Kuja Differential)** – Evaluates malefic influence from Mars, Saturn, and Sun across houses 2, 4, 7, 8, and 12 to verify energetic balance.
* **Pillar 3: Mutual Synergy (D1-D9 Synastry)** – Overlays D1 Ascendant Lords and D9 Relationship Lords across both charts to verify mutual psychological alignment.
* **Pillar 4: Navamsha 7th Interplay (Spouse Projection)** – Analyzes planetary placements in the D9 7th house to determine long-term domestic realities.
* **Pillar 5: Birth Dasha Alignment (Timeline Sync)** – Evaluates birth Mahadasha lords in partner D9 charts to ensure ongoing life period support.
* **Pillar 6: D9 8th Lord Overlay (Transformation Shield)** – Checks placement of the 8th lord in partner Navamsha to verify resistance against sudden crises.

### 2. Visual Yoga Explorer & Bhanga Canvas
* **Dynamic Chart Overlays**: Projects planetary linkages, aspects, exchanges, and cancellation shields directly onto chart layouts.
* **Bhanga Detection**: Detects when beneficial or malefic yogas are neutralized/cancelled.
* **Unified D1 & D9 Scanning**: Scans physical (D1) and subtle (D9) vargas simultaneously.

### 3. Numerology Engine
Merges Parashari planetary friendships with traditional 3x3 grid planes:
* **Ank Analysis**: Calculates Moolank, Bhagyank, and Namank using standard alphabet grids.
* **Compatibility Testing**: Matches house/apartment numbers and partner/friend numbers against your core digits.
* **Numerology Dashas**: Generates annual Mahadasha, Antardasha, and Pratyantar Dasha timelines based on birthday shifts.
* **Flexible Grids**: Switch between Standard Lo Shu (4-9-2), Western Pythagorean (3-6-9), and Natural Sequence (1-2-3) layouts.

---

## Core Workspace Modules & Diagnostics

* **Interactive Diamond Visualizer**: Render Diamond (Rashi) charts with smooth line rendering. Double-clicking any house rotates the chart to treat that house as a temporary Lagna for derivative house analysis.
* **Parashari Vargas (D1 to D60)**: Access all 20 standard Parashari divisional Vargas or build custom divisional charts via the Varga Manager.
* **Horary (Prashna) Studio**: Includes a natural language parser to automatically assign significators, angular aspect evaluation, perfection/prohibition checks, and lost object triangulation.
* **Research Mode**: Compare two charts, time periods, or vargas side-by-side and store multi-chart research sessions locally.
* **Time Progression Engines**:
  * **Multi-Dasha Engine**: Hierarchical 5-level navigation for Vimshottari, Yogini, Jaimini Chara, Kalachakra, Ashtottari, and BPHS conditional Dashas.
  * **Gochar & Nadi Transit Overlay**: Live planetary transits over D1/D9 with D9 Taramsha, Dhruva Nadi trine indicators, and automatic rashi jumps.
  * **Life Activity Curve**: Lifetime energy fluctuation graphs tracking peak/low periods and Pushkara Navamsha transits.
* **Custom Rules Engine**: Define point-based multi-condition rules across D1, D9, D10, and D60 simultaneously.
* **Educational Degree Mapping**: Triangulate educational streams across D1, D9, D24, and D60.
* **Chart Rectification Engine**: Search historical date ranges to match timestamps for hypothetical layouts.
* **Composite Strength Index (CSI)**: Integrates Shadbala, Ashtakavarga (SAV), and Avasthas into unified planetary/house scores.
* **PDF Report Builder**: Export multi-page structured reports with Panchang, Shadbala, Ashtakavarga, Bhava Padas, and Argala summaries.

---

## House Outlines Matrix

| Outline Mode | Explanation | Visual Border Output |
| :--- | :--- | :--- |
| **Vitality (Lords)** | Rulership strength, Dusthana placements, combustion, and Kendra/Trine factors. | Green (Strong Lord), Orange (Mixed), or Red (Compromised). |
| **Pressure (Aspects)** | Total count of planetary aspects targeting a house. | Red (4+ Influences), Gold (3 Influences), Blue (2 Influences). |
| **Regime (Forces)** | Identifies Dispositor Terminals, Aspect Projection Hubs, and Convergence Centers. | System Identified Hubs |
| **Argala Interference** | Calculates intervention houses against obstruction houses. | Computed Balance Vector |

---

## Technical Stack & Languages

* **Core Engine**: Python, PyQt6
* **Astronomical Calculations**: Swiss Ephemeris (`swisseph`) with offline J2 mathematical fallback
* **UI Languages**: Full trilingual support across Menus, Tooltips, Chart Details, and PDF Exports:
  1. **English**: Standard astrological terminology and degree markers.
  2. **हिन्दी (Hindi)**: पारंपरिक शब्दावली (नवग्रह, भाव, नक्षत्र स्वामी, पंचांग, योगकारक).
  3. **संस्कृतम् (Sanskrit)**: शास्त्रोक्त शब्दावली (राशि, वर्ग, बलाबलम्, दृष्टयः).

---

## Installation Guides

### Windows (.exe)
1. Download `astrobasics_installer.exe`.
2. If your browser flags the download as uncommonly downloaded, select **Keep** / **Keep Anyway**.
3. If Windows SmartScreen appears ("Windows protected your PC"), click **More info** and then click **Run anyway**.
4. Grant User Account Control (UAC) permission when prompted to complete setup.

### Android (.apk)
1. Download `AstroBasics.apk` to your device.
2. Tap the downloaded file to open it.
3. If prompted by Android security, enable **Allow from this source** in Settings.
4. If Play Protect flags the app, tap **More details** ➔ **Install anyway**.

---

## Data Privacy & OS Vault Security

All chart profiles, saved sessions, research data, and exported reports remain strictly on your local device. 
* Zero telemetry or tracking scripts
* No external ads or mandatory network calls
* Local database and master key storage encrypted using hardware-backed OS Credential Vault mechanisms.

---

## Important Note & Disclaimer

> **Note**: Astrology helps only those who are genuinely in need; try not to test astrology itself using this software.

*AstroBasics Diamond Chart Pro is released for consultation, educational, and research purposes.*
