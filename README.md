# 🚗 PC to Car Screen Streamer

Stream your Windows PC screen directly to your car screen (Tesla browser, Android Automotive, car browser, tablet, or phone) over Wi-Fi with ultra-low latency!

---

## ⚡ Quick Start (1-Click)

1. **Ensure both devices are on the same network**:
   - Connect your PC and car to the same Wi-Fi network, **OR**
   - Turn on your PC's Mobile Hotspot (or phone hotspot) and connect your car screen to it.

2. **Run the App**:
   - Double-click **`Start_Car_Screen_Share.bat`** on your **Desktop** (or inside this folder).

3. **Open on Car Screen**:
   - Open the web browser in your car (e.g. Tesla browser).
   - Type in the IP address shown in the console window (e.g., `http://192.168.X.X:8080`).

---

## 🎮 Features & Controls on the Car Screen

- **⛶ Fullscreen**: Tap to enter full immersive mode on your car's display.
- **👆 Touch / Remote Click**: When `Touch: ON` is active, tapping or clicking on your car screen clicks on your PC!
- **🖥️ Multi-Monitor Support**: Switch between Monitor 1, Monitor 2, or All Monitors from the top menu.
- **⚡ FPS & Quality Presets**:
  - **60 FPS (Ultra)**: Smooth 60 FPS high resolution.
  - **30 FPS (Balanced)**: Recommended for standard Wi-Fi.
  - **15 FPS (Saver)**: Optimized for weak Wi-Fi or mobile hotspots.
- **📐 Aspect Ratio**: Choose between **Fit Aspect** (no distortion) or **Fill Screen** (stretches to car's widescreen).
- **☰ Menu / Gestures**: Tap the **Menu** button at the bottom-right or two-finger tap to hide/show controls.

---

## 🛠️ Troubleshooting

- **Car browser says "Cannot connect"**:
  1. Make sure your PC and car are connected to the same Wi-Fi / hotspot.
  2. Right-click **`Allow_Firewall_Port_8080.bat`** and click **Run as administrator** to make sure Windows Firewall allows connections on port 8080.
