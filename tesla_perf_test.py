import os
import sys
import time
import random
import math

# Windows sound support for launch beeps
try:
    import winsound
    def beep(freq, dur):
        try:
            winsound.Beep(freq, dur)
        except Exception:
            pass
except ImportError:
    def beep(freq, dur):
        pass

# ANSI Color codes
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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def type_text(text, delay=0.015, color=C_WHITE):
    sys.stdout.write(color)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(C_RESET + "\n")

def progress_bar(label, current, total, width=30, color=C_CYAN, suffix=""):
    percent = float(current) / total
    filled = int(width * percent)
    bar = "=" * filled + "-" * (width - filled)
    print(f"\r  {color}{label:<22} [{bar}] {int(percent * 100):>3}% {suffix}{C_RESET}", end="", flush=True)

def boot_sequence():
    clear_screen()
    print(f"{C_RED}{C_BOLD}")
    print(r"""
  _______ ______  _____ _            _____       _             _ 
 |__   __|  ____|/ ____| |   /\     |  __ \     | |           | |
    | |  | |__  | (___ | |  /  \    | |__) |___ | |__   ___  | |_ 
    | |  |  __|  \___ \| | / /\ \   |  _  // _ \| '_ \ / _ \ | __|
    | |  | |____ ____) | |/ ____ \  | | \ \ (_) | |_) | (_) || |_ 
    |_|  |______|_____/|_/_/    \_\ |_|  \_\___/|_.__/ \___/  \__|
    """)
    print(f"{C_WHITE}{C_BOLD}   === MODEL 3 PERFORMANCE // DIAGNOSTIC & TELEMETRY v4.2 ==={C_RESET}")
    print(f"{C_DIM}   VIN: 5YJ3E1EB9PF****** | Dual Motor AWD Ludicrous | Pack: 82.0 kWh{C_RESET}\n")
    
    type_text("[+] Initializing CAN-3 Gateway Interface (500 kbps)...", 0.01, C_CYAN)
    time.sleep(0.3)
    type_text("[+] Interrogating BMS (Battery Management System) 96S Master Controller...", 0.01, C_CYAN)
    time.sleep(0.4)
    type_text("[+] Front Induction & Rear Permanent Magnet SiC Inverters Online.", 0.01, C_GREEN)
    time.sleep(0.3)
    type_text("[+] Adaptive Damping & Track Mode V3 Firmware: ACTIVATED.", 0.01, C_YELLOW)
    time.sleep(0.5)

    print("\n" + f"{C_BOLD}>>> RUNNING HARDWARE SELF-CHECK...{C_RESET}")
    items = [
        ("Rear 4D1 Motor (3D6 Stator)", "NOMINAL [303 kW / 406 HP]"),
        ("Front 3D3 Motor (Induction)", "NOMINAL [158 kW / 212 HP]"),
        ("Silicon Carbide MOSFETs", "100% HEALTH (1200V / 800A)"),
        ("Battery Pack Voltage", "401.8V (96.4% SoC)"),
        ("Cell Delta-V Variance", "0.003V (Cell Balance: OPTIMAL)"),
        ("Pyrotechnic Fuse Status", "ARMED & CONTINUOUS"),
        ("Supermanifold & Octovalve", "READY [Target Temp: 48.5 deg C]"),
        ("Track Carbon-SiC Brakes", "4-Piston Monobloc Front (Temp: 24 deg C)")
    ]

    for name, stat in items:
        time.sleep(0.18)
        print(f"  {C_WHITE}* {name:<30} -> {C_GREEN}{stat}{C_RESET}")

    print("\n" + f"{C_BOLD}{C_GREEN}[V] ALL SYSTEMS CALIBRATED FOR PEAK PERFORMANCE.{C_RESET}\n")
    time.sleep(0.8)

def battery_telemetry():
    clear_screen()
    print(f"{C_RED}{C_BOLD}=== MODEL 3 PERFORMANCE // LIVE BMS TELEMETRY ==={C_RESET}\n")
    
    soc = 96.5
    volts = 401.4
    temp = 42.0
    
    print(f"{C_WHITE}  STATE OF CHARGE : {C_GREEN}{soc}%{C_RESET}")
    print(f"{C_WHITE}  TOTAL PACK VOLTS: {C_GREEN}{volts} V{C_RESET}")
    print(f"{C_WHITE}  MAX DISCHARGE PWR: {C_YELLOW}460 kW (616 HP available){C_RESET}")
    print(f"{C_WHITE}  OCTOVALVE STATUS: {C_CYAN}Active Pre-conditioning for Launch{C_RESET}\n")

    print(f"{C_BOLD}  [96-SERIES CELL VOLTAGE MATRIX]{C_RESET}")
    for row in range(4):
        cells = [f"{random.uniform(4.178, 4.183):.3f}V" for _ in range(8)]
        print(f"  Bank {row+1:02d}: " + " | ".join([f"{C_GREEN}{c}{C_RESET}" for c in cells]))
        time.sleep(0.1)

    print("\n" + f"{C_CYAN}  Pre-heating battery cells to optimal 48.0°C launch window...{C_RESET}")
    for t in range(int(temp), 49):
        progress_bar("BMS Battery Pre-Heat", t - int(temp) + 1, 48 - int(temp) + 1, width=30, color=C_RED, suffix=f"[{t}°C / 48°C]")
        time.sleep(0.08)
    print("\n\n" + f"{C_GREEN}{C_BOLD}  >>> BATTERY READY FOR MAXIMUM CURRENT DRAW (1,250 AMPS) <<<{C_RESET}\n")
    input(f"{C_YELLOW}  Press [ENTER] to proceed to Dyno & Spec Test...{C_RESET}")

def dyno_pull():
    clear_screen()
    print(f"{C_RED}{C_BOLD}=== VIRTUAL ALL-WHEEL DRIVE DYNO RUN ==={C_RESET}\n")
    print(f"{C_WHITE}Simulating wide-open throttle dyno sweep (0 - 18,000 Motor RPM)...{C_RESET}\n")
    time.sleep(1)

    hp = 0
    tq = 0
    max_hp = 510
    max_tq = 546

    print(f"{C_BOLD}  {'RPM':<8} | {'HORSEPOWER':<15} | {'TORQUE (LB-FT)':<16} | {'G-FORCE':<8}{C_RESET}")
    print("  " + "-" * 55)

    for rpm in range(1000, 18500, 1500):
        # Electric motor torque curve: peak from 0-6000, tapering as back-EMF increases
        if rpm <= 5500:
            current_tq = max_tq - random.uniform(0, 5)
            current_hp = int((current_tq * rpm) / 5252)
        elif rpm <= 8500:
            current_hp = max_hp - random.uniform(0, 8)
            current_tq = int((current_hp * 5252) / rpm)
        else:
            drop_factor = 1.0 - ((rpm - 8500) / 18000) * 0.35
            current_hp = int(max_hp * drop_factor)
            current_tq = int((current_hp * 5252) / rpm)

        g_force = f"{(current_tq / 450.0):.2f} G"
        hp_bar = f"{C_GREEN}{int(current_hp)} HP{C_RESET}"
        tq_bar = f"{C_YELLOW}{int(current_tq)} lb-ft{C_RESET}"
        
        print(f"  {rpm:<8} | {hp_bar:<24} | {tq_bar:<25} | {C_RED}{g_force:<8}{C_RESET}")
        beep(int(600 + (rpm / 15)), 60)
        time.sleep(0.12)

    print("\n" + f"{C_BOLD}{C_GREEN}  ======================================================{C_RESET}")
    print(f"{C_BOLD}  🏆 DYNO PEAK VERIFIED: {C_GREEN}510 HP @ 7,400 RPM{C_RESET} | {C_YELLOW}546 LB-FT @ 1,200 RPM{C_RESET}")
    print(f"{C_BOLD}{C_GREEN}  ======================================================{C_RESET}\n")
    input(f"{C_YELLOW}  Press [ENTER] to load Track Mode Launch Control...{C_RESET}")

def launch_control():
    clear_screen()
    print(f"{C_RED}{C_BOLD}=== TESLA LUDICROUS LAUNCH CONTROL (0-60 & 1/4 MILE) ==={C_RESET}\n")
    print(f"{C_WHITE}  * Track Mode V3: {C_GREEN}ACTIVE{C_RESET}")
    print(f"{C_WHITE}  * Torque Split : {C_YELLOW}35% Front / 65% Rear (Optimized Grip){C_RESET}")
    print(f"{C_WHITE}  * Stability    : {C_CYAN}-2 (Permits slip angle & instant hook){C_RESET}")
    print(f"{C_WHITE}  * Suspension   : {C_RED}CHEETAH STANCE LOWERED (-15mm){C_RESET}\n")

    input(f"{C_YELLOW}  [STEP 1] HOLD LEFT FOOT FIRMLY ON BRAKE & PRESS [ENTER]...{C_RESET}")
    print(f"\n{C_RED}[!] BRAKE PRESSURE: 95 BAR (HOLDING){C_RESET}")
    time.sleep(0.6)

    input(f"\n{C_YELLOW}  [STEP 2] FLOOR ACCELERATOR PEDAL TO 100% & PRESS [ENTER]...{C_RESET}")
    print(f"\n{C_YELLOW}>>> INVERTER ARMED: PEAK STALL TORQUE PRE-TORQUING DRIVETRAIN... <<<{C_RESET}")
    print(f"{C_GREEN}>>> 'CHEETAH STANCE' DAMPING LOCKED. LAUNCH CONTROL READY. <<<{C_RESET}\n")
    time.sleep(1)

    print(f"{C_BOLD}{C_WHITE}  DRAG STRIP TREE INITIATING:{C_RESET}")
    for i in range(3):
        print(f"  {BG_RED}{C_WHITE}{C_BOLD}  [ STAGING YELLOW {i+1} ]  {C_RESET}")
        beep(1000, 250)
        time.sleep(0.6)

    print(f"\n  {BG_GREEN}{C_WHITE}{C_BOLD}  >>> 🟢 GREEN LIGHT // LAUNCH! 🟢 <<<  {C_RESET}\n")
    beep(2200, 600)

    start_sim = time.time()
    speed = 0.0
    distance = 0.0 # feet
    g_force = 1.35

    # Realistic 0-60 acceleration curve for Model 3 Performance
    # ~2.9 seconds to 60mph
    t0_60 = None
    t0_100 = None
    t_quarter = None

    t = 0.0
    dt = 0.04
    
    while t <= 11.2:
        t += dt
        
        # Acceleration model
        if speed < 35:
            accel_mph_per_s = 28.0 # High instant punch
            g = 1.32 + random.uniform(-0.02, 0.03)
        elif speed < 60:
            accel_mph_per_s = 20.5
            g = 1.05 + random.uniform(-0.02, 0.02)
        elif speed < 100:
            accel_mph_per_s = 13.0
            g = 0.65
        else:
            accel_mph_per_s = 8.5
            g = 0.42

        speed += accel_mph_per_s * dt
        feet_per_sec = speed * 1.46667
        distance += feet_per_sec * dt

        if speed >= 60.0 and t0_60 is None:
            t0_60 = t
        if speed >= 100.0 and t0_100 is None:
            t0_100 = t
        if distance >= 1320.0 and t_quarter is None:
            t_quarter = t

        # Visual gauges
        rpm_disp = int(speed * 112)
        speed_bar = "#" * int(min(speed / 3.5, 40))
        print(f"\r  {C_CYAN}TIME: {t:05.2f}s{C_RESET} | {C_RED}{speed:>5.1f} MPH{C_RESET} [{C_GREEN}{speed_bar:<40}{C_RESET}] | {C_YELLOW}{g:04.2f} G{C_RESET} | {distance:>6.0f} ft", end="", flush=True)
        time.sleep(0.025)

    print("\n\n" + f"{C_BOLD}{C_GREEN}" + "=" * 65)
    print("                🏁 TELEMETRY RUN CERTIFIED RESULTS 🏁")
    print("=" * 65 + f"{C_RESET}")
    print(f"  {C_WHITE}0 - 30 MPH  :{C_RESET} {C_GREEN}1.05 s{C_RESET}")
    print(f"  {C_WHITE}0 - 60 MPH  :{C_RESET} {C_GREEN}{C_BOLD}{t0_60:.2f} s{C_RESET}  {C_YELLOW}(*Supercar Territory!*){C_RESET}")
    print(f"  {C_WHITE}0 - 100 MPH :{C_RESET} {C_GREEN}{t0_100:.2f} s{C_RESET}")
    print(f"  {C_WHITE}1/4 MILE    :{C_RESET} {C_GREEN}{C_BOLD}{t_quarter:.2f} s @ {speed:.1f} MPH{C_RESET}")
    print(f"  {C_WHITE}MAX G-FORCE :{C_RESET} {C_RED}{C_BOLD}1.35 G (Longitudinal){C_RESET}")
    print(f"{C_BOLD}{C_GREEN}" + "=" * 65 + f"{C_RESET}\n")

def main():
    os.system("title TESLA MODEL 3 PERFORMANCE // TELEMETRY SUITE")
    boot_sequence()
    
    while True:
        print(f"{C_BOLD}{C_WHITE}SELECT SIMULATION MODULE:{C_RESET}")
        print(f"  {C_CYAN}[1]{C_RESET} Live Battery & Inverter Telemetry (96S Cells / Pre-Heat)")
        print(f"  {C_CYAN}[2]{C_RESET} Dual-Motor AWD Dyno Pull (510 HP / 546 lb-ft)")
        print(f"  {C_CYAN}[3]{C_RESET} 0-60 & 1/4 Mile Launch Control Simulator (Cheetah Stance)")
        print(f"  {C_CYAN}[4]{C_RESET} Run Full Benchmark Suite (All Tests)")
        print(f"  {C_RED}[Q]{C_RESET} Exit")
        
        choice = input(f"\n{C_YELLOW}Enter option (1-4, Q): {C_RESET}").strip().upper()
        
        if choice == "1":
            battery_telemetry()
        elif choice == "2":
            dyno_pull()
        elif choice == "3":
            launch_control()
        elif choice == "4":
            battery_telemetry()
            dyno_pull()
            launch_control()
        elif choice in ("Q", "QUIT", "EXIT"):
            print(f"\n{C_CYAN}[+] Disconnecting from vehicle CAN-bus. Have a safe drive!{C_RESET}\n")
            time.sleep(1)
            break
        else:
            print(f"{C_RED}Invalid option.{C_RESET}")
            time.sleep(0.5)
        clear_screen()

if __name__ == "__main__":
    main()
