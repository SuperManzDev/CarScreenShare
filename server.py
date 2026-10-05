import asyncio
import io
import json
import os
import socket
import sys
import threading
import time
from typing import Optional

try:
    import mss
    from PIL import Image, ImageDraw
    import uvicorn
    from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse, StreamingResponse
    import psutil
    from pynput.mouse import Button, Controller as MouseController
    from pynput.keyboard import Controller as KeyController
except ImportError as e:
    print(f"Missing dependency: {e}. Installing...")
    os.system(f"{sys.executable} -m pip install mss pillow fastapi uvicorn pynput psutil")
    import mss
    from PIL import Image, ImageDraw
    import uvicorn
    from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse, StreamingResponse
    import psutil
    from pynput.mouse import Button, Controller as MouseController
    from pynput.keyboard import Controller as KeyController

import ctypes
from ctypes import wintypes

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class CURSORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hCursor", wintypes.HANDLE),
        ("ptScreenPos", POINT)
    ]

user32 = ctypes.windll.user32

def get_cursor_position():
    cursor_info = CURSORINFO()
    cursor_info.cbSize = ctypes.sizeof(CURSORINFO)
    if user32.GetCursorInfo(ctypes.byref(cursor_info)):
        if cursor_info.flags & 1:  # CURSOR_SHOWING
            return cursor_info.ptScreenPos.x, cursor_info.ptScreenPos.y, True
    return 0, 0, False

def get_local_ips():
    ips = []
    # Try getting primary outbound IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        primary = s.getsockname()[0]
        s.close()
        if primary and not primary.startswith("127."):
            ips.append(primary)
    except Exception:
        pass

    # Add other non-loopback, non-APIPA IPv4s
    try:
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip = addr.address
                    if not ip.startswith("127.") and not ip.startswith("169.254.") and ip not in ips:
                        ips.append(ip)
    except Exception:
        pass

    if not ips:
        ips.append("127.0.0.1")
    return ips

# Global streamer state
class ScreenStreamer:
    def __init__(self):
        try:
            self.sct = mss.MSS()
        except AttributeError:
            self.sct = mss.mss()

        self.monitor_idx = 1 if len(self.sct.monitors) > 1 else 0
        self.quality = 70
        self.fps = 30
        self.scale = 0.85
        self.draw_cursor = True
        self.enable_remote_control = True
        
        self.latest_frame: bytes = b""
        self.lock = threading.Lock()
        self.running = True
        self.mouse = MouseController()
        self.keyboard = KeyController()
        
        # Start capture thread
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def get_monitors(self):
        result = []
        for i, m in enumerate(self.sct.monitors):
            name = "All Monitors Combined" if i == 0 else f"Monitor {i} ({m['width']}x{m['height']})"
            result.append({
                "id": i,
                "name": name,
                "width": m["width"],
                "height": m["height"],
                "left": m["left"],
                "top": m["top"]
            })
        return result

    def _capture_loop(self):
        while self.running:
            start_time = time.time()
            try:
                # Select monitor
                idx = self.monitor_idx if self.monitor_idx < len(self.sct.monitors) else 1
                mon = self.sct.monitors[idx]
                
                # Grab screenshot
                sct_img = self.sct.grab(mon)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

                # Draw mouse pointer if enabled
                if self.draw_cursor:
                    cx, cy, visible = get_cursor_position()
                    if visible:
                        # Relativize cursor to current monitor
                        rx = cx - mon["left"]
                        ry = cy - mon["top"]
                        if 0 <= rx < mon["width"] and 0 <= ry < mon["height"]:
                            draw = ImageDraw.Draw(img)
                            # Draw clean cursor dot / pointer
                            r = 7
                            draw.ellipse([rx - r, ry - r, rx + r, ry + r], fill=(255, 60, 0), outline=(255, 255, 255), width=2)
                            draw.ellipse([rx - 2, ry - 2, rx + 2, ry + 2], fill=(255, 255, 255))

                # Resize if scaling is active
                if self.scale != 1.0:
                    new_w = int(img.width * self.scale)
                    new_h = int(img.height * self.scale)
                    img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)

                # Compress to JPEG
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=self.quality, optimize=False)
                frame_data = buf.getvalue()

                with self.lock:
                    self.latest_frame = frame_data

            except Exception as e:
                pass

            # Maintain target FPS
            elapsed = time.time() - start_time
            sleep_time = max(0.005, (1.0 / self.fps) - elapsed)
            time.sleep(sleep_time)

    def get_frame(self) -> bytes:
        with self.lock:
            return self.latest_frame

streamer = ScreenStreamer()
app = FastAPI()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>PC to Car Screen Streamer</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-touch-callout: none;
            -webkit-user-select: none;
            user-select: none;
        }
        body {
            background: #000;
            color: #e5e7eb;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        #topbar {
            height: 52px;
            background: rgba(18, 18, 24, 0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.12);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            z-index: 50;
            transition: transform 0.3s ease, opacity 0.3s ease;
        }
        #topbar.hidden {
            transform: translateY(-100%);
            opacity: 0;
            pointer-events: none;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 700;
            font-size: 15px;
            letter-spacing: 0.5px;
            color: #38bdf8;
        }
        .status-dot {
            width: 9px;
            height: 9px;
            background: #22c55e;
            border-radius: 50%;
            box-shadow: 0 0 10px #22c55e;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.85); }
            100% { opacity: 1; transform: scale(1); }
        }
        .controls {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        select, button {
            background: #272730;
            color: #f3f4f6;
            border: 1px solid #474754;
            border-radius: 8px;
            padding: 7px 12px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            outline: none;
            transition: all 0.2s;
            touch-action: manipulation;
        }
        select:focus, button:hover {
            background: #363644;
            border-color: #38bdf8;
        }
        button.btn-primary {
            background: #0284c7;
            border-color: #0369a1;
            color: white;
        }
        button.btn-primary:hover {
            background: #0369a1;
        }
        button.active {
            background: #15803d;
            border-color: #16a34a;
            color: #fff;
        }
        #stream-container {
            flex: 1;
            position: relative;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        #stream-img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            display: block;
            pointer-events: auto;
            touch-action: none;
        }
        #stream-img.stretch {
            width: 100%;
            height: 100%;
            object-fit: fill;
        }
        #hud-btn {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 10px 16px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 600;
            backdrop-filter: blur(10px);
            z-index: 60;
            cursor: pointer;
            opacity: 0.8;
            transition: opacity 0.2s, transform 0.1s;
        }
        #hud-btn:active {
            transform: scale(0.95);
        }
        #hud-btn:hover {
            opacity: 1;
        }
        #click-indicator {
            position: absolute;
            width: 24px;
            height: 24px;
            border: 2px solid #38bdf8;
            background: rgba(56, 189, 248, 0.3);
            border-radius: 50%;
            pointer-events: none;
            transform: translate(-50%, -50%) scale(0);
            transition: transform 0.2s ease-out, opacity 0.2s ease-out;
            opacity: 1;
            z-index: 70;
        }
    </style>
</head>
<body>
    <div id="topbar">
        <div class="brand">
            <div class="status-dot"></div>
            <span>CAR PC LINK</span>
        </div>

        <div class="controls">
            <select id="monitorSelect" onchange="updateConfig()">
                <option value="1">Monitor 1</option>
            </select>

            <select id="presetSelect" onchange="applyPreset()">
                <option value="ultra">60 FPS (Ultra)</option>
                <option value="balanced" selected>30 FPS (Balanced)</option>
                <option value="fast">15 FPS (Saver)</option>
            </select>

            <select id="fitSelect" onchange="toggleFit()">
                <option value="contain">Aspect: Fit</option>
                <option value="stretch">Aspect: Fill</option>
            </select>

            <button id="touchBtn" class="active" onclick="toggleRemoteTouch()">Touch: ON</button>
            <button class="btn-primary" onclick="toggleFullScreen()">[ ] Fullscreen</button>
        </div>
    </div>

    <div id="stream-container">
        <img id="stream-img" src="/video_feed" alt="PC Stream" draggable="false" />
        <div id="click-indicator"></div>
        <div id="hud-btn" onclick="toggleControls(event)">Menu</div>
    </div>

    <script>
        let remoteTouchEnabled = true;
        let controlsVisible = true;
        let currentMonId = 1;

        async function loadMonitors() {
            try {
                const res = await fetch('/api/monitors');
                const monitors = await res.json();
                const sel = document.getElementById('monitorSelect');
                sel.innerHTML = '';
                monitors.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m.id;
                    opt.textContent = m.name;
                    if (m.id === 1 || (monitors.length === 1 && m.id === 0)) opt.selected = true;
                    sel.appendChild(opt);
                });
            } catch (e) {
                console.error(e);
            }
        }

        function toggleControls(e) {
            if (e) e.stopPropagation();
            controlsVisible = !controlsVisible;
            document.getElementById('topbar').classList.toggle('hidden', !controlsVisible);
        }

        function toggleFullScreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.log('Fullscreen error:', err);
                });
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        }

        function toggleFit() {
            const fit = document.getElementById('fitSelect').value;
            const img = document.getElementById('stream-img');
            if (fit === 'stretch') {
                img.classList.add('stretch');
            } else {
                img.classList.remove('stretch');
            }
        }

        function toggleRemoteTouch() {
            remoteTouchEnabled = !remoteTouchEnabled;
            const btn = document.getElementById('touchBtn');
            btn.classList.toggle('active', remoteTouchEnabled);
            btn.textContent = `Touch: ${remoteTouchEnabled ? 'ON' : 'OFF'}`;
        }

        function applyPreset() {
            const preset = document.getElementById('presetSelect').value;
            let fps = 30, quality = 70, scale = 0.85;
            if (preset === 'ultra') {
                fps = 60; quality = 85; scale = 1.0;
            } else if (preset === 'balanced') {
                fps = 30; quality = 70; scale = 0.85;
            } else if (preset === 'fast') {
                fps = 15; quality = 50; scale = 0.65;
            }
            updateConfigValues({ fps, quality, scale });
        }

        async function updateConfig() {
            const mon = parseInt(document.getElementById('monitorSelect').value);
            currentMonId = mon;
            await updateConfigValues({ monitor: mon });
        }

        async function updateConfigValues(cfg) {
            try {
                await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(cfg)
                });
            } catch (e) {
                console.error(e);
            }
        }

        // Handle Touch / Mouse click on car screen to control PC
        const streamImg = document.getElementById('stream-img');
        const clickIndicator = document.getElementById('click-indicator');

        function showIndicator(x, y) {
            clickIndicator.style.left = x + 'px';
            clickIndicator.style.top = y + 'px';
            clickIndicator.style.transform = 'translate(-50%, -50%) scale(1)';
            clickIndicator.style.opacity = '1';
            setTimeout(() => {
                clickIndicator.style.transform = 'translate(-50%, -50%) scale(1.6)';
                clickIndicator.style.opacity = '0';
            }, 150);
        }

        function sendClickEvent(e, type) {
            if (!remoteTouchEnabled) return;
            const rect = streamImg.getBoundingClientRect();
            
            let clientX, clientY;
            if (e.touches && e.touches.length > 0) {
                clientX = e.touches[0].clientX;
                clientY = e.touches[0].clientY;
            } else {
                clientX = e.clientX;
                clientY = e.clientY;
            }

            if (clientX < rect.left || clientX > rect.right || clientY < rect.top || clientY > rect.bottom) {
                return;
            }

            showIndicator(clientX, clientY);

            const normX = (clientX - rect.left) / rect.width;
            const normY = (clientY - rect.top) / rect.height;

            fetch('/api/mouse', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: type,
                    x: normX,
                    y: normY,
                    monitor: currentMonId
                })
            }).catch(() => {});
        }

        streamImg.addEventListener('click', (e) => sendClickEvent(e, 'click'));
        streamImg.addEventListener('dblclick', (e) => sendClickEvent(e, 'double_click'));
        streamImg.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            sendClickEvent(e, 'right_click');
        });

        // Two finger tap opens/closes controls menu
        streamImg.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
                toggleControls();
            }
        });

        window.onload = () => {
            loadMonitors();
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=HTML_PAGE)

@app.get("/video_feed")
def video_feed():
    def frame_generator():
        while streamer.running:
            frame = streamer.get_frame()
            if frame:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            time.sleep(1.0 / (streamer.fps + 5))
            
    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/api/monitors")
def api_monitors():
    return streamer.get_monitors()

@app.post("/api/config")
async def api_config(payload: dict):
    if "monitor" in payload:
        streamer.monitor_idx = int(payload["monitor"])
    if "fps" in payload:
        streamer.fps = int(payload["fps"])
    if "quality" in payload:
        streamer.quality = int(payload["quality"])
    if "scale" in payload:
        streamer.scale = float(payload["scale"])
    if "draw_cursor" in payload:
        streamer.draw_cursor = bool(payload["draw_cursor"])
    return {"status": "ok", "config": {
        "monitor": streamer.monitor_idx,
        "fps": streamer.fps,
        "quality": streamer.quality,
        "scale": streamer.scale
    }}

@app.post("/api/mouse")
async def api_mouse(payload: dict):
    try:
        mon_idx = payload.get("monitor", streamer.monitor_idx)
        if mon_idx >= len(streamer.sct.monitors):
            mon_idx = 1
        mon = streamer.sct.monitors[mon_idx]

        norm_x = payload.get("x", 0)
        norm_y = payload.get("y", 0)
        action = payload.get("type", "click")

        target_x = mon["left"] + int(norm_x * mon["width"])
        target_y = mon["top"] + int(norm_y * mon["height"])

        streamer.mouse.position = (target_x, target_y)

        if action == "click":
            streamer.mouse.click(Button.left, 1)
        elif action == "double_click":
            streamer.mouse.click(Button.left, 2)
        elif action == "right_click":
            streamer.mouse.click(Button.right, 1)

        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def print_banner(port=8080):
    ips = get_local_ips()
    primary_ip = ips[0] if ips else "127.0.0.1"
    
    print("\n" + "=" * 70, flush=True)
    print("   ================================================================", flush=True)
    print("                 CAR SCREEN STREAMER IS READY & LIVE!", flush=True)
    print("   ================================================================", flush=True)
    print("   ", flush=True)
    print("   >>> TYPE THIS EXACT LINK INTO YOUR CAR SCREEN BROWSER: <<<", flush=True)
    print("   ", flush=True)
    print(f"       >>  http://{primary_ip}:{port}  <<", flush=True)
    print("   ", flush=True)
    if len(ips) > 1:
        print("   (Other available network addresses:)", flush=True)
        for ip in ips[1:]:
            print(f"       - http://{ip}:{port}", flush=True)
    print("   ", flush=True)
    print(f"   PC Local Test Link: http://localhost:{port}", flush=True)
    print("   ================================================================", flush=True)
    print("   TIPS:", flush=True)
    print("   - Make sure your car is connected to the same Wi-Fi / Hotspot.", flush=True)
    print("   - Tap 'Fullscreen' on your car screen for full immersive display.", flush=True)
    print("   - Keep this window open while streaming.", flush=True)
    print("=" * 70 + "\n", flush=True)

if __name__ == "__main__":
    port = 8080
    print_banner(port)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
