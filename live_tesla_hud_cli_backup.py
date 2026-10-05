import os
import sys
import time
import random
import math
import msvcrt
import threading

# Enable ANSI escape sequences on Windows
os.system('')

# Sound support
try:
    import winsound
    def play_tone(freq, dur):
        try:
            winsound.Beep(max(37, min(32767, int(freq))), int(dur))
        except Exception:
            pass
except ImportError:
    def play_tone(freq, dur):
        pass

# Color Codes
C_RESET = "\033[0m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN = "\033[96m"
C_WHITE = "\033[97m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_BLUE = "\033[44m"
BG_BLACK = "\033[40m"

class LiveTeslaSim:
    def __init__(self):
        # Physics state
        self.speed = 0.0       # MPH
        self.throttle = 0.0    # 0.0 to 1.0
        self.brake = 0.0       # 0.0 to 1.0
        self.steering = 0.0    # -1.0 to +1.0
        self.power_kw = 0.0    # -100 kW to +460 kW
        self.motor_rpm = 0
        self.torque_lbft = 0.0
        self.soc = 94.6        # %
        self.pack_volts = 401.8
        self.pack_amps = 0.0
        
        # Track Mode & Handling
        self.track_mode = True
        self.torque_split_rear = 0.65  # 35% Front / 65% Rear
        self.drift_preset = "BALANCED GRIP (35/65)"
        self.launch_mode_ready = False
        self.launch_count = 0
        
        # Thermals
        self.front_inv_temp = 48.0
        self.rear_inv_temp = 54.0
        self.stator_temp = 52.0
        self.battery_temp = 47.5
        self.brake_temp = 45.0
        self.octovalve_mode = "OCTOVALVE: LOOP 4 (TRACK PREP)"
        
        # Tires (FL, FR, RL, RR)
        self.tire_psi = [41.2, 41.1, 42.0, 42.1]
        self.tire_temp = [42.0, 42.0, 44.0, 44.5]
        
        # G-Force
        self.gx = 0.0  # Lateral
        self.gy = 0.0  # Longitudinal
        
        # 0-60 timer
        self.timer_active = False
        self.start_time = None
        self.last_0_60 = 2.89
        self.quarter_mile = 10.91
        
        # Sound thread control
        self.running = True
        self.sound_thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.sound_thread.start()

    def _audio_loop(self):
        while self.running:
            if self.throttle > 0.05:
                freq = 400 + (self.speed * 28) + (self.throttle * 300)
                dur = 60
                play_tone(freq, dur)
            elif self.brake > 0.05:
                freq = 900 - (self.brake * 300)
                dur = 50
                play_tone(freq, dur)
            else:
                time.sleep(0.06)

    def process_input(self):
        # Decay inputs over time
        self.throttle = max(0.0, self.throttle - 0.15)
        self.brake = max(0.0, self.brake - 0.20)
        self.steering = self.steering * 0.70  # Return steering to center

        while msvcrt.kbhit():
            key = msvcrt.getch()
            # Handle special arrow keys
            if key in (b'\x00', b'\xe0'):
                arrow = msvcrt.getch()
                if arrow == b'H': # UP
                    self.throttle = min(1.0, self.throttle + 0.45)
                elif arrow == b'P': # DOWN
                    self.brake = min(1.0, self.brake + 0.50)
                elif arrow == b'K': # LEFT
                    self.steering = max(-1.0, self.steering - 0.40)
                elif arrow == b'M': # RIGHT
                    self.steering = min(1.0, self.steering + 0.40)
                continue

            k = key.lower()
            if k in (b'w', b' '): # Throttle / Space floor it
                self.throttle = 1.0 if k == b' ' else min(1.0, self.throttle + 0.45)
            elif k == b's': # Brake
                self.brake = min(1.0, self.brake + 0.50)
            elif k == b'a': # Steer Left
                self.steering = max(-1.0, self.steering - 0.40)
            elif k == b'd': # Steer Right
                self.steering = min(1.0, self.steering + 0.40)
            elif k == b't': # Toggle Track Mode split
                if self.torque_split_rear == 0.65:
                    self.torque_split_rear = 1.0
                    self.drift_preset = "100% REAR DRIFT MODE"
                elif self.torque_split_rear == 1.0:
                    self.torque_split_rear = 0.50
                    self.drift_preset = "50/50 SNOW/RACE GRIP"
                else:
                    self.torque_split_rear = 0.65
                    self.drift_preset = "BALANCED GRIP (35/65)"
            elif k == b'l': # Launch Control
                self.trigger_launch_sequence()
            elif k in (b'q', b'\x1b'): # Quit
                self.running = False

    def trigger_launch_sequence(self):
        self.speed = 0.0
        self.timer_active = True
        self.start_time = time.time()
        self.throttle = 1.0

    def update_physics(self, dt=0.04):
        # Acceleration
        max_power = 460.0 # kW (~616 HP peak system draw)
        if self.throttle > 0.01:
            self.power_kw = self.throttle * max_power + random.uniform(-2, 2)
            accel = (self.power_kw / 460.0) * 32.0 * max(0.3, 1.0 - (self.speed / 175.0))
            self.gy = (self.power_kw / 460.0) * 1.35
        elif self.brake > 0.01:
            # Regen + Friction Brakes
            self.power_kw = -1 * min(100.0, self.brake * 120.0)
            decel = 38.0 * self.brake
            accel = -decel
            self.gy = -1.25 * self.brake
            self.brake_temp = min(680.0, self.brake_temp + (self.brake * 12.0))
        else:
            # Coasting drag
            self.power_kw = 0.0
            accel = -1.2 - (0.003 * self.speed * self.speed)
            self.gy = 0.0

        # Update Speed
        self.speed = max(0.0, min(163.5, self.speed + (accel * dt)))
        self.motor_rpm = int(self.speed * 110.5)

        # Torque calculation
        if self.speed < 45:
            self.torque_lbft = max(0.0, (self.throttle * 546.0) + random.uniform(-3, 3))
        else:
            self.torque_lbft = max(0.0, (546.0 * (45.0 / max(45.0, self.speed)) * self.throttle))

        # Lateral G-Force from steering
        self.gx = self.steering * (self.speed / 70.0) * 1.25

        # 0-60 tracking
        if self.timer_active:
            elapsed = time.time() - self.start_time
            if self.speed >= 60.0:
                self.last_0_60 = round(elapsed, 2)
                self.timer_active = False

        # Battery Pack & Inverter dynamics
        self.pack_amps = (self.power_kw * 1000.0) / max(300.0, self.pack_volts)
        self.pack_volts = 401.8 - (self.pack_amps * 0.012)
        self.soc = max(0.0, self.soc - (abs(self.power_kw) * 0.000004))

        # Thermals
        if self.power_kw > 100:
            self.rear_inv_temp = min(92.0, self.rear_inv_temp + (self.power_kw * 0.0004))
            self.front_inv_temp = min(85.0, self.front_inv_temp + (self.power_kw * 0.0002))
            self.stator_temp = min(110.0, self.stator_temp + 0.02)
        else:
            # Cooling loop
            self.rear_inv_temp = max(52.0, self.rear_inv_temp - 0.05)
            self.front_inv_temp = max(46.0, self.front_inv_temp - 0.05)
            self.stator_temp = max(50.0, self.stator_temp - 0.08)
            self.brake_temp = max(45.0, self.brake_temp - 0.3)

        # Tire dynamics
        for i in range(4):
            self.tire_temp[i] = min(85.0, max(38.0, self.tire_temp[i] + (abs(self.gx) * 0.05) + (abs(self.gy) * 0.03) - 0.01))
            self.tire_psi[i] = 40.5 + ((self.tire_temp[i] - 38.0) * 0.12)

    def draw_power_bar(self):
        width = 46
        center = width // 2
        
        # -100 kW to +460 kW
        if self.power_kw >= 0:
            ratio = min(1.0, self.power_kw / 460.0)
            blocks = int(ratio * (width - center))
            bar = " " * center + C_RED + "|" + "#" * blocks + C_RESET + " " * ((width - center) - blocks)
        else:
            ratio = min(1.0, abs(self.power_kw) / 100.0)
            blocks = int(ratio * center)
            bar = " " * (center - blocks) + C_GREEN + "<" * blocks + "|" + C_RESET + " " * (width - center)

        return bar

    def draw_g_bowl(self):
        # 5x5 grid for G-meter
        grid = [["·" for _ in range(7)] for _ in range(5)]
        
        # map gx (-1.5 to +1.5) to col 0..6
        # map gy (-1.5 to +1.5) to row 0..4 (inverted: +gy is forward/top)
        col = int(round(3 + (self.gx / 1.5) * 3))
        row = int(round(2 - (self.gy / 1.5) * 2))
        
        col = max(0, min(6, col))
        row = max(0, min(4, row))
        grid[row][col] = f"{C_RED}{C_BOLD}●{C_RESET}"

        lines = []
        for r in grid:
            lines.append(" ".join(r))
        return lines

    def render(self):
        # ANSI Cursor to top-left (no flickering!)
        sys.stdout.write("\033[H")
        
        g_lines = self.draw_g_bowl()
        power_bar = self.draw_power_bar()
        
        # Header
        output = []
        output.append(f"{C_BOLD}{C_RED}╔═══════════════════════════════════════════════════════════════════════════════════════╗{C_RESET}")
        output.append(f"{C_BOLD}{C_WHITE}║  TESLA TRACK TELEMETRY v4.2 // MODEL 3 PERFORMANCE // LIVE CAN-3 FEED (100 Hz)       ║{C_RESET}")
        output.append(f"{C_BOLD}{C_RED}╠═══════════════════════════════════════════════════════════════════════════════════════╣{C_RESET}")
        
        # Speed & Power summary line
        spd_color = C_GREEN if self.speed < 60 else (C_YELLOW if self.speed < 110 else C_RED)
        pwr_str = f"{C_GREEN}{self.power_kw:>+5.0f} kW (REGEN){C_RESET}" if self.power_kw < 0 else f"{C_RED}{self.power_kw:>+5.0f} kW ({int(self.power_kw*1.341)} HP){C_RESET}"
        
        output.append(f"║  SPEED: {spd_color}{self.speed:>6.1f} MPH{C_RESET}    POWER: {pwr_str:<28}  SOC: {C_GREEN}{self.soc:>4.1f}%{C_RESET} [{self.pack_volts:.1f}V / {self.pack_amps:>5.0f}A]  ║")
        output.append(f"║  MOTOR: {C_CYAN}{self.motor_rpm:>6d} RPM{C_RESET}    TORQUE: {C_YELLOW}{self.torque_lbft:>5.0f} lb-ft{C_RESET}           MODE: {C_MAGENTA}{self.drift_preset:<21}{C_RESET}  ║")
        output.append(f"{C_BOLD}{C_RED}╠═══════════════════════════════════════════════════════════════════════════════════════╣{C_RESET}")
        
        # Power & Regen Meter
        output.append(f"║  {C_BOLD}POWER FLOW GAUGE:{C_RESET}                                                                   ║")
        output.append(f"║  {C_GREEN}REGEN [-100kW]{C_RESET} [{power_bar}] {C_RED}[+460kW] LUDICROUS{C_RESET}  ║")
        output.append(f"║                                                                                       ║")

        # G-Force & Thermals & Tires
        output.append(f"║  {C_BOLD}{C_CYAN}[G-FORCE 2D BOWL]{C_RESET}            {C_BOLD}{C_YELLOW}[TIRE TEMPS / PSI]{C_RESET}          {C_BOLD}{C_RED}[THERMAL MANAGEMENT]{C_RESET}     ║")
        output.append(f"║       ▲ +Acc ({self.gy:>+4.2f}G)       FL: {self.tire_psi[0]:.1f} PSI | {self.tire_temp[0]:.0f}°C        Front Inverter : {self.front_inv_temp:>4.1f}°C   ║")
        output.append(f"║    ┌─────────────┐         FR: {self.tire_psi[1]:.1f} PSI | {self.tire_temp[1]:.0f}°C        Rear SiC Module: {self.rear_inv_temp:>4.1f}°C   ║")
        output.append(f"║  ◄ │ {g_lines[1]} │ ► Lat     RL: {self.tire_psi[2]:.1f} PSI | {self.tire_temp[2]:.0f}°C        3D6 Stator Temp: {self.stator_temp:>4.1f}°C   ║")
        output.append(f"║    │ {g_lines[2]} │ ({self.gx:>+4.2f}G)   RR: {self.tire_psi[3]:.1f} PSI | {self.tire_temp[3]:.0f}°C        Track Brake Rot: {self.brake_temp:>4.0f}°C   ║")
        output.append(f"║    └─────────────┘         [Brembo 4-Piston Calipers]  Octovalve State: {C_GREEN}NOMINAL{C_RESET}   ║")
        output.append(f"║       ▼ -Brake ({self.gy:>+4.2f}G)                                                         ║")
        output.append(f"{C_BOLD}{C_RED}╠═══════════════════════════════════════════════════════════════════════════════════════╣{C_RESET}")

        # Live 96S Cells
        cells_b1 = [f"{random.uniform(4.178, 4.183):.3f}V" for _ in range(6)]
        cells_b2 = [f"{random.uniform(4.178, 4.183):.3f}V" for _ in range(6)]
        output.append(f"║  {C_BOLD}96S CELL VOLTAGES:{C_RESET}  " + " ".join([f"{C_GREEN}{c}{C_RESET}" for c in cells_b1]) + "     ║")
        output.append(f"║  {C_BOLD}BALANCING DELTA: {C_GREEN}0.004V{C_RESET}  " + " ".join([f"{C_GREEN}{c}{C_RESET}" for c in cells_b2]) + f"  0-60: {C_YELLOW}{self.last_0_60}s{C_RESET} ║")
        output.append(f"{C_BOLD}{C_RED}╠═══════════════════════════════════════════════════════════════════════════════════════╣{C_RESET}")

        # Interactive controls bar
        output.append(f"║  {C_BOLD}LIVE CONTROLS:{C_RESET}                                                                       ║")
        output.append(f"║  [{C_CYAN}W / UP{C_RESET}] Throttle  |  [{C_RED}S / DOWN{C_RESET}] Regen Brake  |  [{C_YELLOW}A / D{C_RESET}] Steer  |  [{C_GREEN}SPACE{C_RESET}] 100% Floor It      ║")
        output.append(f"║  [{C_MAGENTA}L{C_RESET}] 0-60 Launch Trigger  |  [{C_BLUE}T{C_RESET}] Toggle Drift Bias / Track Split  |  [{C_WHITE}Q{C_RESET}] Exit HUD      ║")
        output.append(f"{C_BOLD}{C_RED}╚═══════════════════════════════════════════════════════════════════════════════════════╝{C_RESET}")

        sys.stdout.write("\n".join(output) + "\n")
        sys.stdout.flush()

    def run(self):
        os.system("cls")
        # Hide cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        
        last_time = time.time()
        try:
            while self.running:
                now = time.time()
                dt = now - last_time
                last_time = now

                self.process_input()
                self.update_physics(dt)
                self.render()
                time.sleep(0.04) # ~25 FPS live refresh
        finally:
            # Show cursor again
            sys.stdout.write("\033[?25h" + C_RESET + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    sim = LiveTeslaSim()
    sim.run()
