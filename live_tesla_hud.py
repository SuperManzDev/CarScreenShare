"""
TESLA MODEL 3 PERFORMANCE // TRACK TELEMETRY & DYNAMICS SIMULATOR v7.0 (ULTIMATE MACH EDITION)
=============================================================================================
- 🚀 MACH 1 HYPER-WARP: 5,000 HP / 6,500 Nm Torque / Supersonic Shockwave / 600+ MPH / 0-60 in 0.55s!
- 🏎️ ADVANCED DRIFTING: Live Drift Angle Gauge, Multipliers, Combo Points & "DRIFT GOD" Scoring System!
- 🚦 DRAG RACING CHRISTMAS TREE: NHRA Staging Lights, Amber 1-2-3 Countdown, Green/Red Lights & Reaction Time!
- 🔒 ELECTRONIC LINE LOCK: Front-wheel lock for massive stationary tire burnouts!
- 🌡️ REALISTIC MULTI-ZONE THERMAL ENGINE:
  * Individual 4-Corner Brake Rotor Temps (FL, FR, RL, RR) with Visual Molten Glow (Molten Red/Orange/Yellow)!
  * Authentic Brake Fade Physics when rotors overheat!
  * Individual 4-Corner Dynamic Tire Temps & Pressure (PV=nRT expansion)!
  * Octovalve Heat Pump Loop Management (Cool, Track Prep, Ludicrous Pre-Heat, Cryo Flash)!
- ⚙️ AUTHENTIC TESLA TRACK MODE V3 SETTINGS: Live interactive tuning drawer with sliders & presets!
- 🔊 MULTI-TRACK AUDIO: Dual-motor SiC inverter whine, tire screech, rocket thrusters, staging beeps & sonic boom!
"""

import math
import os
import random
import sys
import time
from typing import List, Tuple

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
import numpy as np

AUDIO_AVAILABLE = False
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except Exception as e:
    print(f"Audio notice: {e}. Running silent mode.")

pygame.init()
pygame.font.init()

WINDOW_WIDTH = 1380
WINDOW_HEIGHT = 840
FPS = 60

COLOR_BG = (10, 12, 16)
COLOR_PANEL = (17, 21, 28)
COLOR_PANEL_ALT = (23, 28, 38)
COLOR_BORDER = (40, 48, 62)
COLOR_TEXT_WHITE = (245, 247, 250)
COLOR_TEXT_DIM = (135, 145, 160)
COLOR_TEXT_MUTED = (85, 95, 110)

COLOR_TESLA_RED = (255, 36, 66)
COLOR_CYAN_GLOW = (0, 225, 255)
COLOR_NEON_GREEN = (0, 255, 140)
COLOR_WARNING_YELLOW = (255, 195, 20)
COLOR_MAGENTA_PURPLE = (235, 30, 215)
COLOR_ELECTRIC_BLUE = (35, 135, 255)
COLOR_WARP_ORANGE = (255, 110, 20)
COLOR_SKID_MARK = (24, 24, 28)

# -----------------------------------------------------------------------------
# TRACK MODE V3 TUNING SETTINGS
# -----------------------------------------------------------------------------
class TrackSettings:
    def __init__(self):
        # 0: OEM Stock (510 HP)
        # 1: Track Pro (1,050 HP)
        # 2: SpaceX Thrusters (2,680 HP)
        # 3: 🚀⚡ MACH 1 HYPER-WARP (5,000 HP / 600+ MPH)
        self.power_level = 3
        self.power_level_names = [
            "OEM STOCK (510 HP)",
            "TRACK PRO (1,050 HP)",
            "SPACEX THRUSTERS (2,680 HP)",
            "🚀⚡ MACH 1 HYPER-WARP (5,000 HP)"
        ]

        # Handling Balance (Torque Split F/R)
        self.torque_split_idx = 2  # 35/65 Track
        self.torque_splits = [
            (1.00, 0.00, "100/0 FWD"),
            (0.50, 0.50, "50/50 AWD CATAPULT"),
            (0.35, 0.65, "35/65 TRACK BALANCED"),
            (0.20, 0.80, "20/80 AGGRESSIVE"),
            (0.00, 1.00, "0/100 RWD DRIFT KING")
        ]

        # Stability Assist (-10 OFF, 0 Track, +10 Full Street)
        self.stability_assist = 0

        # Regenerative Braking
        self.regen_level = 1.0

        # Tire Compound
        self.tire_compound_idx = 3  # Hyper Drag Slicks
        self.tire_compounds = [
            (1.18, "STREET (PS4S)"),
            (1.42, "TRACK (CUP 2 R)"),
            (1.78, "RACING SLICKS"),
            (2.45, "HYPER DRAG RADIALS")
        ]

        # Brake Type (0: Steel 355mm, 1: Carbon-Ceramic 400mm)
        self.brake_type_idx = 1
        self.brake_types = ["BREMBO STEEL (355mm)", "CARBON-CERAMIC (400mm)"]

        # Aerodynamics Downforce
        self.aero_idx = 2
        self.aero_levels = [
            (0.19, 0.15, "LOW DRAG (HYPERSPEED RUN)"),
            (0.22, 0.40, "BALANCED TRACK SPOILER"),
            (0.28, 0.95, "EXTREME HIGH DOWNFORCE WING")
        ]

        # Speed Governor (False = No Limit, True = 163 MPH Cap)
        self.speed_governor = False

        # Octovalve Loop
        self.thermal_loop_idx = 3
        self.thermal_loops = [
            "LOOP 1: NORMAL AMBIENT",
            "LOOP 4: TRACK ACTIVE CHILL",
            "LOOP 6: LUDICROUS PRE-HEAT (48°C)",
            "LOOP 8: CRYO FLASH CHILL (25°C)"
        ]

        # Electronic Line Lock (Burnout Mode)
        self.line_lock_active = False

    def apply_stock(self):
        self.power_level = 0
        self.torque_split_idx = 2
        self.stability_assist = 0
        self.regen_level = 0.7
        self.tire_compound_idx = 1
        self.brake_type_idx = 0
        self.aero_idx = 1
        self.speed_governor = True
        self.thermal_loop_idx = 0

    def apply_track(self):
        self.power_level = 1
        self.torque_split_idx = 2
        self.stability_assist = 0
        self.regen_level = 1.0
        self.tire_compound_idx = 2
        self.brake_type_idx = 1
        self.aero_idx = 2
        self.speed_governor = False
        self.thermal_loop_idx = 1

    def apply_drift(self):
        self.power_level = 1
        self.torque_split_idx = 4
        self.stability_assist = -10
        self.regen_level = 0.4
        self.tire_compound_idx = 1
        self.brake_type_idx = 0
        self.aero_idx = 0
        self.speed_governor = False
        self.thermal_loop_idx = 1

    def apply_mach_warp(self):
        self.power_level = 3
        self.torque_split_idx = 1
        self.stability_assist = 0
        self.regen_level = 1.0
        self.tire_compound_idx = 3
        self.brake_type_idx = 1
        self.aero_idx = 2
        self.speed_governor = False
        self.thermal_loop_idx = 3

# -----------------------------------------------------------------------------
# AUDIO SYNTHESIZER
# -----------------------------------------------------------------------------
class SoundSynthesizer:
    def __init__(self):
        self.enabled = AUDIO_AVAILABLE
        self.muted = False
        self.channels = {}
        self.sounds = {}

        if self.enabled:
            try:
                sr = 44100
                dur = 0.4
                t = np.linspace(0, dur, int(sr * dur), endpoint=False)
                # Motor whine
                wave = (
                    0.45 * np.sin(2 * np.pi * 320 * t) +
                    0.30 * np.sin(2 * np.pi * 640 * t) +
                    0.15 * np.sin(2 * np.pi * 1280 * t) +
                    0.10 * np.sin(2 * np.pi * 2560 * t)
                )
                wave = (wave * 12000).astype(np.int16)
                self.sounds["motor"] = pygame.sndarray.make_sound(np.column_stack((wave, wave)))
                self.channels["motor"] = pygame.mixer.Channel(0)
                self.channels["motor"].play(self.sounds["motor"], loops=-1)
                self.channels["motor"].set_volume(0.0)

                # Tire screech
                dur_skid = 0.35
                n_samples = int(sr * dur_skid)
                noise = np.random.uniform(-1, 1, n_samples)
                carrier = np.sin(2 * np.pi * 840 * np.linspace(0, dur_skid, n_samples))
                skid_arr = ((noise * 0.75 + carrier * 0.25) * 14000).astype(np.int16)
                self.sounds["skid"] = pygame.sndarray.make_sound(np.column_stack((skid_arr, skid_arr)))
                self.channels["skid"] = pygame.mixer.Channel(1)
                self.channels["skid"].play(self.sounds["skid"], loops=-1)
                self.channels["skid"].set_volume(0.0)

                # Rocket Thrusters / Supersonic Jet
                dur_th = 0.45
                n_th = int(sr * dur_th)
                th_t = np.linspace(0, dur_th, n_th, endpoint=False)
                th_noise = np.random.uniform(-1, 1, n_th)
                th_rumble = np.sin(2 * np.pi * 65 * th_t) * 0.5 + np.sin(2 * np.pi * 130 * th_t) * 0.3
                th_arr = ((th_noise * 0.60 + th_rumble * 0.40) * 17000).astype(np.int16)
                self.sounds["thruster"] = pygame.sndarray.make_sound(np.column_stack((th_arr, th_arr)))
                self.channels["thruster"] = pygame.mixer.Channel(2)
                self.channels["thruster"].play(self.sounds["thruster"], loops=-1)
                self.channels["thruster"].set_volume(0.0)
            except Exception as e:
                print(f"Synth notice: {e}")
                self.enabled = False

    def update(self, rpm: float, power_kw: float, slip_speed: float, power_level: int, throttle: float):
        if not self.enabled or self.muted:
            for ch in self.channels.values(): ch.set_volume(0.0)
            return

        try:
            scale_kw = 3800.0 if power_level == 3 else (2000.0 if power_level == 2 else 500.0)
            pwr_ratio = min(1.0, abs(power_kw) / scale_kw)
            vol_motor = max(0.05, min(0.85, 0.08 + pwr_ratio * 0.70 + (rpm / 35000.0) * 0.25))
            self.channels["motor"].set_volume(vol_motor)

            if slip_speed > 2.5:
                skid_vol = min(0.95, (slip_speed - 2.5) / 12.0)
                self.channels["skid"].set_volume(skid_vol)
            else:
                self.channels["skid"].set_volume(0.0)

            # Thruster volume
            if power_level >= 2 and throttle > 0.2:
                self.channels["thruster"].set_volume(min(1.0, throttle * 0.95))
            else:
                self.channels["thruster"].set_volume(0.0)
        except Exception:
            pass

    def play_chime(self, freq: float, dur=0.18):
        if not self.enabled or self.muted: return
        try:
            sr = 44100
            t = np.linspace(0, dur, int(sr * dur), endpoint=False)
            chime = np.sin(2 * np.pi * freq * t) * np.linspace(1, 0, len(t))
            arr = (chime * 18000).astype(np.int16)
            snd = pygame.sndarray.make_sound(np.column_stack((arr, arr)))
            snd.set_volume(0.8)
            snd.play()
        except Exception:
            pass

    def play_sonic_boom(self):
        if not self.enabled or self.muted: return
        try:
            sr = 44100
            dur = 0.55
            t = np.linspace(0, dur, int(sr * dur), endpoint=False)
            noise = np.random.uniform(-1, 1, len(t))
            boom = (np.sin(2 * np.pi * 45 * t) * 0.7 + noise * 0.3) * (np.exp(-t * 8.0))
            arr = (boom * 24000).astype(np.int16)
            snd = pygame.sndarray.make_sound(np.column_stack((arr, arr)))
            snd.set_volume(1.0)
            snd.play()
        except Exception:
            pass

# -----------------------------------------------------------------------------
# THERMAL BMS & TIRE PRESSURE SYSTEM
# -----------------------------------------------------------------------------
class ThermalBMS:
    def __init__(self):
        # 4-Corner Rotors: [FL, FR, RL, RR] in °C
        self.rotor_temps = [45.0, 45.0, 42.0, 42.0]
        # 4-Corner Tires: [FL, FR, RL, RR] in °C
        self.tire_temps = [28.0, 28.0, 28.0, 28.0]
        # 4-Corner Pressures in PSI
        self.tire_pressures = [41.0, 41.0, 41.0, 41.0]
        # Core Powertrain
        self.battery_temp = 34.0
        self.motor_front_temp = 48.0
        self.motor_rear_temp = 52.0
        self.inverter_temp = 40.0
        self.soc_pct = 95.0
        self.brake_fade_factor = 1.0

    def update(self, dt: float, speed_mps: float, wheel_slip: List[float],
               brake_pressure: float, power_kw: float, settings: TrackSettings, is_burnout: bool):
        ambient = 22.0

        # Octovalve Loop Multipliers
        loop_cooling = [1.0, 2.2, 0.6, 3.5][settings.thermal_loop_idx]

        # Battery & Motor thermals
        pwr_heat = abs(power_kw) / 1000.0
        self.motor_front_temp += (pwr_heat * 0.45 * dt * 0.9) - (self.motor_front_temp - ambient) * 0.03 * loop_cooling * dt
        self.motor_rear_temp += (pwr_heat * 0.75 * dt * 0.9) - (self.motor_rear_temp - ambient) * 0.03 * loop_cooling * dt
        self.inverter_temp += (pwr_heat * 0.35 * dt) - (self.inverter_temp - ambient) * 0.05 * loop_cooling * dt

        if settings.thermal_loop_idx == 2:  # Ludicrous Pre-Heat
            if self.battery_temp < 48.0:
                self.battery_temp += 0.8 * dt
        else:
            target_batt = 25.0 if settings.thermal_loop_idx == 3 else 32.0
            self.battery_temp += (pwr_heat * 0.15 * dt) - (self.battery_temp - target_batt) * 0.04 * loop_cooling * dt

        # Battery consumption
        self.soc_pct = max(0.0, self.soc_pct - (abs(power_kw) / 3600.0) * dt * 0.003)

        # Rotor Heating and Cooling per corner
        base_cool = 0.045 + (speed_mps / 100.0) * 0.12
        is_ccb = (settings.brake_type_idx == 1)
        heat_rate = 0.70 if is_ccb else 1.0  # CCB dissipates faster

        for i in range(4):
            # Braking friction heating
            bias = 0.60 if i < 2 else 0.40
            corner_brake_pwr = brake_pressure * speed_mps * bias * 18.0
            self.rotor_temps[i] += corner_brake_pwr * heat_rate * dt
            # Convective cooling
            cool_speed = base_cool * (1.3 if is_ccb else 1.0)
            self.rotor_temps[i] -= (self.rotor_temps[i] - ambient) * cool_speed * dt
            self.rotor_temps[i] = max(ambient, min(1200.0, self.rotor_temps[i]))

        # Tire Heating (Slip friction + burnout)
        for i in range(4):
            slip = wheel_slip[i]
            tire_heat = slip * (speed_mps + 5.0) * 0.08
            if is_burnout and i >= 2:  # Rear wheels in line lock burnout
                tire_heat += 28.0
            self.tire_temps[i] += tire_heat * dt
            self.tire_temps[i] -= (self.tire_temps[i] - ambient) * 0.035 * dt
            self.tire_temps[i] = max(ambient, min(145.0, self.tire_temps[i]))
            # Ideal gas expansion: 0.12 PSI per °C above 25°C
            self.tire_pressures[i] = 41.0 + (self.tire_temps[i] - 25.0) * 0.13

        # Brake Fade Calculation: CCB withstands up to 780°C, Steel fades above 580°C
        fade_thresh = 780.0 if is_ccb else 580.0
        max_rotor = max(self.rotor_temps)
        if max_rotor > fade_thresh:
            self.brake_fade_factor = max(0.28, 1.0 - (max_rotor - fade_thresh) / 380.0)
        else:
            self.brake_fade_factor = 1.0

    @staticmethod
    def get_rotor_color(temp_c: float) -> Tuple[int, int, int]:
        if temp_c < 300.0:
            return (52, 56, 64)
        elif temp_c < 550.0:
            r = (temp_c - 300.0) / 250.0
            return (int(52 + r * 188), int(56 - r * 36), int(64 - r * 44))
        elif temp_c < 800.0:
            r = (temp_c - 550.0) / 250.0
            return (int(240 + r * 15), int(20 + r * 110), int(20 - r * 10))
        elif temp_c < 1050.0:
            r = (temp_c - 800.0) / 250.0
            return (255, int(130 + r * 115), int(10 + r * 170))
        else:
            return (255, 245, 225)

# -----------------------------------------------------------------------------
# TELEMETRY TIMERS & SPLIT PERFORMANCE
# -----------------------------------------------------------------------------
class TelemetryTimers:
    def __init__(self):
        self.reset()

    def reset(self):
        self.start_time = None
        self.distance_traveled = 0.0
        self.time_0_60 = None
        self.time_0_100 = None
        self.time_0_200 = None
        self.time_60ft = None
        self.time_330ft = None
        self.time_660ft = None  # 1/8 mile
        self.speed_660ft = None
        self.time_1000ft = None
        self.time_1320ft = None # 1/4 mile
        self.speed_1320ft = None
        self.top_speed_mph = 0.0
        self.peak_long_g = 0.0
        self.peak_lat_g = 0.0
        self.active_run = False
        self.run_timer = 0.0

    def update(self, dt: float, speed_mph: float, long_g: float, lat_g: float):
        self.top_speed_mph = max(self.top_speed_mph, speed_mph)
        self.peak_long_g = max(self.peak_long_g, long_g)
        self.peak_lat_g = max(self.peak_lat_g, abs(lat_g))

        if speed_mph > 0.5:
            if not self.active_run:
                self.active_run = True
                self.run_timer = 0.0
                self.distance_traveled = 0.0
            self.run_timer += dt
            dist_feet = (speed_mph * 5280.0 / 3600.0) * dt
            self.distance_traveled += dist_feet

            # Speed milestone triggers
            if speed_mph >= 60.0 and self.time_0_60 is None:
                self.time_0_60 = self.run_timer
            if speed_mph >= 100.0 and self.time_0_100 is None:
                self.time_0_100 = self.run_timer
            if speed_mph >= 200.0 and self.time_0_200 is None:
                self.time_0_200 = self.run_timer

            # Drag split triggers
            if self.distance_traveled >= 60.0 and self.time_60ft is None:
                self.time_60ft = self.run_timer
            if self.distance_traveled >= 330.0 and self.time_330ft is None:
                self.time_330ft = self.run_timer
            if self.distance_traveled >= 660.0 and self.time_660ft is None:
                self.time_660ft = self.run_timer
                self.speed_660ft = speed_mph
            if self.distance_traveled >= 1000.0 and self.time_1000ft is None:
                self.time_1000ft = self.run_timer
            if self.distance_traveled >= 1320.0 and self.time_1320ft is None:
                self.time_1320ft = self.run_timer
                self.speed_1320ft = speed_mph

# -----------------------------------------------------------------------------
# 2D ACCELEROMETER G-METER
# -----------------------------------------------------------------------------
class GMeter:
    def __init__(self):
        self.history: List[Tuple[float, float, float]] = []  # (gx, gy, alpha)
        self.lat_g = 0.0
        self.long_g = 0.0

    def update(self, dt: float, current_lat_g: float, current_long_g: float):
        # Smoothing filter
        self.lat_g += (current_lat_g - self.lat_g) * min(1.0, dt * 18.0)
        self.long_g += (current_long_g - self.long_g) * min(1.0, dt * 18.0)
        # Push trail
        self.history.append((self.lat_g, self.long_g, 1.0))
        # Fade history
        faded = []
        for gx, gy, alpha in self.history:
            new_a = alpha - dt * 2.2
            if new_a > 0:
                faded.append((gx, gy, new_a))
        self.history = faded[-35:]

# -----------------------------------------------------------------------------
# ADVANCED VEHICLE DYNAMICS PHYSICS ENGINE
# -----------------------------------------------------------------------------
class VehiclePhysics:
    def __init__(self):
        self.mass = 1840.0  # kg
        self.wheelbase = 2.875  # meters
        self.track_width = 1.58  # meters
        self.cg_to_front = 1.4375
        self.cg_to_rear = 1.4375
        self.inertia_yaw = 2750.0  # kg*m^2

        # State in world frame
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0  # radians (0 = along +X / East)

        # Velocities in body frame
        self.v_long = 0.0  # m/s (+forward)
        self.v_lat = 0.0   # m/s (+right)
        self.yaw_rate = 0.0  # rad/s

        # Telemetry readouts
        self.steer_angle = 0.0
        self.rpm = 0.0
        self.power_kw = 0.0
        self.torque_nm = 0.0
        self.speed_mps = 0.0
        self.speed_mph = 0.0
        self.speed_kmh = 0.0
        self.mach_number = 0.0
        self.long_g = 0.0
        self.lat_g = 0.0
        self.wheel_slip = [0.0, 0.0, 0.0, 0.0]  # FL, FR, RL, RR
        self.cheetah_stance = 0.0  # 0.0 to 1.0
        self.is_burnout = False
        self.sonic_boom_triggered = False

    def reset_position(self, x=0.0, y=0.0, heading=0.0):
        self.x = x
        self.y = y
        self.heading = heading
        self.v_long = 0.0
        self.v_lat = 0.0
        self.yaw_rate = 0.0
        self.steer_angle = 0.0
        self.rpm = 0.0
        self.power_kw = 0.0
        self.torque_nm = 0.0
        self.speed_mps = 0.0
        self.speed_mph = 0.0
        self.speed_kmh = 0.0
        self.long_g = 0.0
        self.lat_g = 0.0
        self.wheel_slip = [0.0, 0.0, 0.0, 0.0]
        self.sonic_boom_triggered = False

    def update(self, dt: float, throttle: float, brake: float, steer_input: float,
               handbrake: bool, settings: TrackSettings, thermal_bms: ThermalBMS,
               sound: SoundSynthesizer, is_staged: bool):

        # Cheetah Stance front suspension drop
        target_cheetah = 1.0 if (is_staged and brake > 0.4 and throttle > 0.4) else 0.0
        self.cheetah_stance += (target_cheetah - self.cheetah_stance) * min(1.0, dt * 5.0)

        # Speed-sensitive steering ratio
        max_steer = math.radians(34.0) if self.speed_mph < 40 else math.radians(max(5.5, 34.0 - (self.speed_mph - 40) * 0.12))
        target_steer = steer_input * max_steer
        self.steer_angle += (target_steer - self.steer_angle) * min(1.0, dt * 14.0)

        # Power levels configuration
        # [0: Stock, 1: Track Pro, 2: SpaceX Thrusters, 3: Mach 1 Hyper-Warp]
        power_levels_data = [
            {"pwr": 375.0,  "tq": 740.0,  "thruster": 0.0,     "top": 162.0},
            {"pwr": 780.0,  "tq": 1350.0, "thruster": 0.0,     "top": 215.0},
            {"pwr": 2000.0, "tq": 3200.0, "thruster": 12000.0, "top": 360.0},
            {"pwr": 3800.0, "tq": 6500.0, "thruster": 36000.0, "top": 780.0}
        ]
        cfg = power_levels_data[settings.power_level]

        # Top speed governor enforcement
        effective_throttle = throttle
        if settings.speed_governor and self.speed_mph >= 163.0:
            effective_throttle = 0.0

        # Electronic Line Lock (Burnout Mode)
        self.is_burnout = False
        if settings.line_lock_active and throttle > 0.05:
            self.is_burnout = True

        # Motor output calculations
        split_f, split_r, _ = settings.torque_splits[settings.torque_split_idx]
        total_torque = cfg["tq"] * effective_throttle
        self.torque_nm = total_torque
        self.power_kw = cfg["pwr"] * effective_throttle

        # Forward propulsion force
        wheel_radius = 0.345  # 235/35R20
        gear_ratio = 9.03
        f_drive = (total_torque * gear_ratio) / wheel_radius

        # Add rocket thruster direct thrust force
        if cfg["thruster"] > 0 and effective_throttle > 0.2:
            f_drive += cfg["thruster"] * effective_throttle

        # Braking force with thermal brake fade
        effective_brake = brake * thermal_bms.brake_fade_factor
        f_brake_max = self.mass * 9.81 * 1.65 * thermal_bms.brake_fade_factor
        f_brake = effective_brake * f_brake_max

        # Regen braking on off-throttle
        if effective_throttle < 0.05 and brake < 0.05 and abs(self.v_long) > 0.5:
            f_brake += settings.regen_level * (self.mass * 9.81 * 0.32)

        # Aerodynamics (Drag & Downforce)
        cd, cl, _ = settings.aero_levels[settings.aero_idx]
        frontal_area = 2.22  # m^2
        air_density = 1.225  # kg/m^3
        f_aero_drag = 0.5 * air_density * cd * frontal_area * (self.v_long ** 2) * math.copysign(1.0, self.v_long)
        f_downforce = 0.5 * air_density * cl * frontal_area * (self.v_long ** 2)

        # Rolling resistance
        f_roll = 0.012 * (self.mass * 9.81) * math.copysign(1.0, self.v_long) if abs(self.v_long) > 0.1 else 0.0

        # Normal loads with dynamic weight transfer
        g = 9.81
        w_total = self.mass * g + f_downforce
        fz_front = (w_total * 0.5) - (self.mass * self.long_g * g * 0.45 / self.wheelbase)
        fz_rear = (w_total * 0.5) + (self.mass * self.long_g * g * 0.45 / self.wheelbase)
        fz_front = max(1000.0, fz_front)
        fz_rear = max(1000.0, fz_rear)

        # Lateral tire grip calculation (Pacejka simplified)
        grip_coeff, _ = settings.tire_compounds[settings.tire_compound_idx]

        # Slip angles
        v_long_safe = max(1.5, abs(self.v_long))
        alpha_f = self.steer_angle - math.atan2(self.v_lat + self.cg_to_front * self.yaw_rate, v_long_safe)
        alpha_r = -math.atan2(self.v_lat - self.cg_to_rear * self.yaw_rate, v_long_safe)

        # Handbrake cuts rear lateral grip to 18% and locks rear
        rear_grip_mult = 0.18 if handbrake else 1.0

        # Cornering stiffness
        c_alpha = 75000.0 * grip_coeff
        f_lat_f = max(-fz_front * grip_coeff, min(fz_front * grip_coeff, c_alpha * alpha_f))
        f_lat_r = max(-fz_rear * grip_coeff * rear_grip_mult, min(fz_rear * grip_coeff * rear_grip_mult, c_alpha * alpha_r * rear_grip_mult))

        # Stability Assist yaw damping
        if settings.stability_assist > -10:
            stab_strength = (settings.stability_assist + 10) / 20.0
            yaw_damp = -self.yaw_rate * 8500.0 * stab_strength
        else:
            yaw_damp = 0.0

        # Longitudinal force summation
        if self.is_burnout:
            # Front locked, car stands still or moves very slowly
            a_long = 0.0
            self.v_long = 0.0
            self.v_lat = 0.0
            self.yaw_rate = 0.0
            # Rear wheels spinning wildly
            self.wheel_slip = [0.05, 0.05, 0.95, 0.95]
        else:
            net_f_long = f_drive - math.copysign(f_brake, self.v_long) - f_aero_drag - f_roll
            a_long = net_f_long / self.mass

            # Lateral acceleration and yaw torque
            a_lat = (f_lat_f * math.cos(self.steer_angle) + f_lat_r) / self.mass - (self.v_long * self.yaw_rate)
            torque_yaw = (f_lat_f * math.cos(self.steer_angle) * self.cg_to_front) - (f_lat_r * self.cg_to_rear) + yaw_damp
            yaw_accel = torque_yaw / self.inertia_yaw

            # Integrate body velocities
            self.v_long += a_long * dt
            if abs(self.v_long) < 0.05 and effective_throttle < 0.01 and brake > 0.1:
                self.v_long = 0.0
            self.v_lat += a_lat * dt
            self.yaw_rate += yaw_accel * dt
            # Natural yaw decay at low speed
            if abs(self.v_long) < 1.0:
                self.yaw_rate *= 0.85
                self.v_lat *= 0.85

            # Calculate individual wheel slips for thermal & smoke
            slip_base = abs(self.v_lat) / max(1.0, abs(self.v_long))
            slip_f = min(1.0, slip_base + (0.35 if brake > 0.3 else 0.0))
            slip_r = min(1.0, slip_base + (0.55 if handbrake else 0.0) + (0.45 * effective_throttle * split_r))
            self.wheel_slip = [slip_f, slip_f, slip_r, slip_r]

        # Update world pose
        self.heading += self.yaw_rate * dt
        # Heading normalization
        self.heading = (self.heading + math.pi) % (2 * math.pi) - math.pi

        # Transform body velocities into world frame
        cos_h = math.cos(self.heading)
        sin_h = math.sin(self.heading)
        v_world_x = self.v_long * cos_h - self.v_lat * sin_h
        v_world_y = self.v_long * sin_h + self.v_lat * cos_h

        self.x += v_world_x * dt
        self.y += v_world_y * dt

        # Derived telemetry
        self.speed_mps = math.hypot(self.v_long, self.v_lat)
        self.speed_mph = self.speed_mps * 2.23694
        self.speed_kmh = self.speed_mps * 3.6
        self.mach_number = self.speed_mps / 340.29  # Mach 1 = ~761 MPH at sea level
        self.long_g = a_long / 9.81 if not self.is_burnout else (throttle * 0.1)
        self.lat_g = (self.v_long * self.yaw_rate + (f_lat_f + f_lat_r) / self.mass) / 9.81
        self.rpm = min(36000.0, (abs(self.v_long) / wheel_radius) * gear_ratio * (60.0 / (2 * math.pi)))
        if self.is_burnout:
            self.rpm = 18000.0 * throttle

        # Sonic boom trigger when passing Mach 1
        if self.mach_number >= 1.0 and not self.sonic_boom_triggered:
            self.sonic_boom_triggered = True
            sound.play_sonic_boom()
        elif self.mach_number < 0.95:
            self.sonic_boom_triggered = False

# -----------------------------------------------------------------------------
# DRIFT SCORING & ANGLE TELEMETRY
# -----------------------------------------------------------------------------
class DriftScorer:
    def __init__(self):
        self.drift_angle = 0.0
        self.current_score = 0.0
        self.banked_score = 0.0
        self.multiplier = 1.0
        self.combo_timer = 0.0
        self.grace_timer = 0.0
        self.is_drifting = False
        self.last_badge = ""
        self.badge_timer = 0.0

    def update(self, dt: float, v_long: float, v_lat: float, speed_mph: float):
        # Calculate slip angle
        if abs(v_long) > 0.8:
            self.drift_angle = math.degrees(math.atan2(abs(v_lat), abs(v_long)))
        else:
            self.drift_angle = 0.0

        drifting_now = (self.drift_angle >= 7.5 and speed_mph >= 12.0)

        if drifting_now:
            self.is_drifting = True
            self.grace_timer = 1.4  # Grace period to link slides
            self.combo_timer += dt

            # Multiplier progression
            if self.combo_timer > 9.0:
                self.multiplier = 5.0
            elif self.combo_timer > 6.0:
                self.multiplier = 4.0
            elif self.combo_timer > 3.5:
                self.multiplier = 3.0
            elif self.combo_timer > 1.5:
                self.multiplier = 2.0
            else:
                self.multiplier = 1.0

            # Accumulate score
            rate = (self.drift_angle * speed_mph * 0.45) * self.multiplier
            self.current_score += rate * dt

            # Badge determination
            if self.drift_angle > 78.0:
                self.last_badge = "👑 REVERSE ENTRY DRIFT GOD! 👑"
            elif self.drift_angle > 52.0:
                self.last_badge = "⚡ INSANE ANGLE SLIDE! ⚡"
            elif self.drift_angle > 32.0:
                self.last_badge = "🔥 SICK TANDEM! 🔥"
            elif self.drift_angle > 18.0:
                self.last_badge = "CLEAN DRIFT"
            else:
                self.last_badge = "DRIFT ANGLE DETECTED"
            self.badge_timer = 1.5
        else:
            if self.grace_timer > 0.0:
                self.grace_timer -= dt
            else:
                if self.current_score > 0:
                    self.banked_score += self.current_score
                    self.current_score = 0.0
                    self.combo_timer = 0.0
                    self.multiplier = 1.0
                self.is_drifting = False

        if self.badge_timer > 0:
            self.badge_timer -= dt

# -----------------------------------------------------------------------------
# NHRA CHRISTMAS TREE DRAG RACING SYSTEM
# -----------------------------------------------------------------------------
class DragTree:
    STATE_IDLE = 0
    STATE_PRESTAGE = 1
    STATE_STAGED = 2
    STATE_COUNTDOWN = 3
    STATE_GREEN = 4
    STATE_RED_FOUL = 5

    def __init__(self):
        self.state = self.STATE_IDLE
        self.prestage_lit = False
        self.staged_lit = False
        self.amber1_lit = False
        self.amber2_lit = False
        self.amber3_lit = False
        self.green_lit = False
        self.red_lit = False
        self.countdown_timer = 0.0
        self.green_timestamp = 0.0
        self.reaction_time = None
        self.staged_stable_timer = 0.0

    def reset(self):
        self.state = self.STATE_IDLE
        self.prestage_lit = False
        self.staged_lit = False
        self.amber1_lit = False
        self.amber2_lit = False
        self.amber3_lit = False
        self.green_lit = False
        self.red_lit = False
        self.countdown_timer = 0.0
        self.green_timestamp = 0.0
        self.reaction_time = None
        self.staged_stable_timer = 0.0

    def update(self, dt: float, car_x: float, speed_mph: float, sound: SoundSynthesizer):
        # Distance to staging line (x = 0 is start line)
        dist = car_x

        if self.state in (self.STATE_IDLE, self.STATE_PRESTAGE, self.STATE_STAGED):
            if -4.5 <= dist <= 3.0:
                self.prestage_lit = True
                if -1.8 <= dist <= 1.2:
                    self.staged_lit = True
                    self.state = self.STATE_STAGED
                    if speed_mph < 2.0:
                        self.staged_stable_timer += dt
                        if self.staged_stable_timer >= 1.2:  # Car steady in beams
                            self.state = self.STATE_COUNTDOWN
                            self.countdown_timer = 0.0
                    else:
                        self.staged_stable_timer = 0.0
                else:
                    self.staged_lit = False
                    self.state = self.STATE_PRESTAGE
                    self.staged_stable_timer = 0.0
            else:
                self.reset()

        elif self.state == self.STATE_COUNTDOWN:
            self.countdown_timer += dt
            # Red light foul check (car leaves beam before green)
            if dist > 1.8:
                self.state = self.STATE_RED_FOUL
                self.red_lit = True
                self.amber1_lit = False
                self.amber2_lit = False
                self.amber3_lit = False
                self.reaction_time = -999.0
                sound.play_chime(220.0, 0.4)
                return

            # Pro-tree / Sportsman countdown
            if self.countdown_timer >= 0.5 and not self.amber1_lit:
                self.amber1_lit = True
                sound.play_chime(550.0, 0.15)
            if self.countdown_timer >= 1.0 and not self.amber2_lit:
                self.amber2_lit = True
                sound.play_chime(550.0, 0.15)
            if self.countdown_timer >= 1.5 and not self.amber3_lit:
                self.amber3_lit = True
                sound.play_chime(550.0, 0.15)
            if self.countdown_timer >= 2.0:
                self.state = self.STATE_GREEN
                self.green_lit = True
                self.green_timestamp = time.time()
                sound.play_chime(1100.0, 0.35)

        elif self.state == self.STATE_GREEN:
            # Measure reaction time when vehicle starts moving forward
            if self.reaction_time is None and dist > 1.8:
                self.reaction_time = max(0.001, time.time() - self.green_timestamp)

# -----------------------------------------------------------------------------
# PARTICLE DYNAMICS & SHOCKWAVE SYSTEM
# -----------------------------------------------------------------------------
class ParticleSystem:
    def __init__(self):
        self.smoke_particles: List[dict] = []  # x, y, vx, vy, size, alpha, color
        self.thruster_particles: List[dict] = []
        self.shockwaves: List[dict] = []  # x, y, radius, max_radius, alpha
        self.skid_marks: List[Tuple[float, float, float, float, float]] = []  # x1, y1, x2, y2, alpha

    def add_smoke(self, x: float, y: float, density: float = 1.0):
        for _ in range(int(density * 3)):
            self.smoke_particles.append({
                "x": x + random.uniform(-0.4, 0.4),
                "y": y + random.uniform(-0.4, 0.4),
                "vx": random.uniform(-0.8, 0.8),
                "vy": random.uniform(-0.8, 0.8),
                "size": random.uniform(5.0, 10.0),
                "max_size": random.uniform(28.0, 48.0),
                "alpha": random.uniform(140, 220),
                "fade": random.uniform(45.0, 75.0)
            })

    def add_thruster(self, x: float, y: float, heading: float, throttle: float):
        rear_angle = heading + math.pi
        spread = 0.22
        for _ in range(int(throttle * 5)):
            ang = rear_angle + random.uniform(-spread, spread)
            spd = random.uniform(18.0, 45.0)
            self.thruster_particles.append({
                "x": x + random.uniform(-0.2, 0.2),
                "y": y + random.uniform(-0.2, 0.2),
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd,
                "size": random.uniform(3.0, 7.0),
                "alpha": 255.0,
                "fade": random.uniform(400.0, 750.0),
                "color": random.choice([(0, 230, 255), (80, 160, 255), (255, 120, 20), (255, 40, 120)])
            })

    def add_shockwave(self, x: float, y: float):
        self.shockwaves.append({
            "x": x,
            "y": y,
            "radius": 4.0,
            "max_radius": 55.0,
            "alpha": 240.0,
            "growth": 95.0
        })

    def add_skid(self, x1: float, y1: float, x2: float, y2: float, intensity: float):
        if intensity > 0.15:
            self.skid_marks.append((x1, y1, x2, y2, min(1.0, intensity)))
            if len(self.skid_marks) > 400:
                self.skid_marks.pop(0)

    def update(self, dt: float):
        # Update smoke
        alive_smoke = []
        for p in self.smoke_particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["size"] = min(p["max_size"], p["size"] + dt * 18.0)
            p["alpha"] -= p["fade"] * dt
            if p["alpha"] > 0:
                alive_smoke.append(p)
        self.smoke_particles = alive_smoke[-180:]

        # Update thrusters
        alive_th = []
        for p in self.thruster_particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["size"] = max(1.0, p["size"] - dt * 6.0)
            p["alpha"] -= p["fade"] * dt
            if p["alpha"] > 0:
                alive_th.append(p)
        self.thruster_particles = alive_th[-140:]

        # Update shockwaves
        alive_sw = []
        for sw in self.shockwaves:
            sw["radius"] += sw["growth"] * dt
            sw["alpha"] -= dt * 180.0
            if sw["alpha"] > 0 and sw["radius"] < sw["max_radius"]:
                alive_sw.append(sw)
        self.shockwaves = alive_sw

# -----------------------------------------------------------------------------
# TRACK ENVIRONMENT & WORLD RENDERING
# -----------------------------------------------------------------------------
class TrackEnvironment:
    MODE_DRAG_STRIP = 0
    MODE_ROAD_COURSE = 1
    MODE_SKIDPAD = 2

    def __init__(self):
        self.current_mode = self.MODE_DRAG_STRIP
        self.mode_names = [
            "NHRA DRAG SUPERSTRIP (2.5 MILES)",
            "GRAND PRIX HANDLING COURSE",
            "100M DRIFT SKIDPAD ARENA"
        ]
        # Road Course Waypoints
        self.course_points = [
            (0, 0), (250, 0), (450, 40), (600, 150), (650, 320),
            (550, 480), (350, 520), (200, 430), (50, 480), (-150, 520),
            (-350, 400), (-450, 250), (-400, 100), (-250, 20), (-100, 0)
        ]

    def cycle_mode(self):
        self.current_mode = (self.current_mode + 1) % 3
        return self.mode_names[self.current_mode]

    def draw_world(self, surface: pygame.Surface, cam_x: float, cam_y: float,
                   scale: float, drag_tree: DragTree, particle_sys: ParticleSystem):
        sw, sh = surface.get_size()
        cx, cy = sw // 2, sh // 2

        def w2s(wx, wy):
            return int(cx + (wx - cam_x) * scale), int(cy - (wy - cam_y) * scale)

        # Draw skid marks
        for x1, y1, x2, y2, alpha in particle_sys.skid_marks:
            p1 = w2s(x1, y1)
            p2 = w2s(x2, y2)
            if -100 <= p1[0] <= sw + 100 and -100 <= p1[1] <= sh + 100:
                col = (int(30 * alpha), int(30 * alpha), int(34 * alpha))
                pygame.draw.line(surface, col, p1, p2, max(2, int(2.2 * scale)))

        # Render Track Mode
        if self.current_mode == self.MODE_DRAG_STRIP:
            # 2.5 Mile Superstrip
            y_bot = w2s(0, -9.0)[1]
            y_top = w2s(0, 9.0)[1]
            x_start = w2s(-60.0, 0)[0]
            x_end = w2s(4100.0, 0)[0]

            # Asphalt surface
            strip_rect = pygame.Rect(x_start, min(y_top, y_bot), max(10, x_end - x_start), abs(y_bot - y_top))
            pygame.draw.rect(surface, (22, 24, 30), strip_rect)
            pygame.draw.line(surface, (180, 185, 195), (x_start, y_top), (x_end, y_top), 2)
            pygame.draw.line(surface, (180, 185, 195), (x_start, y_bot), (x_end, y_bot), 2)

            # Center divider dashed line
            y_mid = w2s(0, 0.0)[1]
            dash_len = int(8.0 * scale)
            dash_gap = int(6.0 * scale)
            x_curr = x_start
            while x_curr < x_end:
                pygame.draw.line(surface, (230, 200, 40), (x_curr, y_mid), (min(x_end, x_curr + dash_len), y_mid), 2)
                x_curr += dash_len + dash_gap

            # Milestone lines & signage
            milestones = [
                (0.0, "START LINE / STAGING", (255, 255, 255)),
                (18.288, "60 FT", (0, 220, 255)),
                (100.584, "330 FT", (0, 220, 255)),
                (201.168, "1/8 MILE (660 FT)", (0, 255, 140)),
                (304.8, "1,000 FT", (0, 220, 255)),
                (402.336, "1/4 MILE (TRAP SPEED)", (255, 215, 0)),
                (804.672, "1/2 MILE", (255, 130, 30)),
                (1609.344, "1.0 MILE", (255, 50, 80)),
                (3218.688, "2.0 MILES", (255, 30, 180))
            ]
            font_ms = pygame.font.SysFont("Trebuchet MS", max(10, int(11 * (scale / 12.0))))
            for m_dist, m_label, m_col in milestones:
                px = w2s(m_dist, 0)[0]
                if -150 <= px <= sw + 150:
                    pygame.draw.line(surface, m_col, (px, y_top), (px, y_bot), 3 if m_dist == 0 else 2)
                    lbl = font_ms.render(m_label, True, m_col)
                    surface.blit(lbl, (px + 5, y_top - 22))

            # Drag Tree Gantry rendering on the strip
            tree_pos = w2s(0.0, 12.0)
            if -100 <= tree_pos[0] <= sw + 100:
                pygame.draw.line(surface, (90, 100, 120), (tree_pos[0], tree_pos[1] + 25), (tree_pos[0], tree_pos[1] - 40), 5)
                # Gantry head box
                gh_rect = pygame.Rect(tree_pos[0] - 14, tree_pos[1] - 80, 28, 70)
                pygame.draw.rect(surface, (15, 18, 24), gh_rect, border_radius=4)
                pygame.draw.rect(surface, (120, 130, 150), gh_rect, 2, border_radius=4)
                # Tree Bulbs
                bulbs = [
                    (tree_pos[1] - 70, (255, 255, 255) if drag_tree.prestage_lit else (40, 40, 40)),
                    (tree_pos[1] - 56, (255, 255, 255) if drag_tree.staged_lit else (40, 40, 40)),
                    (tree_pos[1] - 42, (255, 190, 0) if drag_tree.amber1_lit else (50, 40, 10)),
                    (tree_pos[1] - 30, (255, 190, 0) if drag_tree.amber2_lit else (50, 40, 10)),
                    (tree_pos[1] - 18, (255, 190, 0) if drag_tree.amber3_lit else (50, 40, 10)),
                    (tree_pos[1] - 6, (0, 255, 60) if drag_tree.green_lit else (10, 45, 15)),
                    (tree_pos[1] + 6, (255, 25, 25) if drag_tree.red_lit else (45, 10, 10))
                ]
                for by, bcol in bulbs:
                    pygame.draw.circle(surface, bcol, (tree_pos[0], by), 4)

        elif self.current_mode == self.MODE_SKIDPAD:
            # Concentric drift circles
            c_center = w2s(0, 0)
            radii = [25.0, 50.0, 75.0, 100.0]
            for r in radii:
                r_px = int(r * scale)
                pygame.draw.circle(surface, (35, 42, 55), c_center, r_px, 2)
            # Cross axes
            pygame.draw.line(surface, (45, 55, 70), (c_center[0] - int(110*scale), c_center[1]), (c_center[0] + int(110*scale), c_center[1]), 2)
            pygame.draw.line(surface, (45, 55, 70), (c_center[0], c_center[1] - int(110*scale)), (c_center[0], c_center[1] + int(110*scale)), 2)

        elif self.current_mode == self.MODE_ROAD_COURSE:
            # Track ribbon
            if len(self.course_points) > 1:
                pts = [w2s(px, py) for px, py in self.course_points]
                pygame.draw.lines(surface, (28, 32, 42), True, pts, int(16 * scale))
                pygame.draw.lines(surface, (230, 60, 60), True, pts, 3)

        # Render Shockwave rings
        for sw_p in particle_sys.shockwaves:
            sc_pos = w2s(sw_p["x"], sw_p["y"])
            r_px = int(sw_p["radius"] * scale)
            if r_px > 2:
                alpha = max(0, min(255, int(sw_p["alpha"])))
                sw_surf = pygame.Surface((r_px * 2 + 4, r_px * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(sw_surf, (0, 240, 255, alpha), (r_px + 2, r_px + 2), r_px, max(2, int(3 * scale)))
                surface.blit(sw_surf, (sc_pos[0] - r_px - 2, sc_pos[1] - r_px - 2))

        # Render Thruster Flames
        for th in particle_sys.thruster_particles:
            p_pos = w2s(th["x"], th["y"])
            sz = max(2, int(th["size"] * (scale / 14.0)))
            pygame.draw.circle(surface, th["color"], p_pos, sz)

        # Render Smoke Particles
        for smk in particle_sys.smoke_particles:
            smk_pos = w2s(smk["x"], smk["y"])
            sz = int(smk["size"] * (scale / 12.0))
            if sz > 2:
                alpha = max(0, min(255, int(smk["alpha"])))
                smk_surf = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
                pygame.draw.circle(smk_surf, (220, 225, 235, alpha), (sz, sz), sz)
                surface.blit(smk_surf, (smk_pos[0] - sz, smk_pos[1] - sz))

# -----------------------------------------------------------------------------
# HIGH-FIDELITY TESLA MODEL 3 TOP-DOWN SPRITE RENDERER
# -----------------------------------------------------------------------------
def draw_tesla_model_3(surface: pygame.Surface, cx: int, cy: int,
                       heading: float, steer_angle: float, scale: float,
                       brake_pressed: bool, settings: TrackSettings,
                       thermal_bms: ThermalBMS, cheetah_stance: float):

    # Dimensions in meters
    length_m = 4.69
    width_m = 1.85
    wb_half = (2.875 / 2.0) * scale
    tw_half = (1.58 / 2.0) * scale

    # Base car surface with alpha
    car_len_px = int(length_m * scale)
    car_w_px = int(width_m * scale)
    if car_len_px < 20 or car_w_px < 10:
        return

    car_surf = pygame.Surface((car_len_px + 40, car_w_px + 40), pygame.SRCALPHA)
    base_cx = (car_len_px + 40) // 2
    base_cy = (car_w_px + 40) // 2

    # Cheetah stance visual effect (squats front of car forward & narrows nose)
    nose_offset = int(cheetah_stance * 4.0 * (scale / 14.0))

    # Car body contour (Tesla Model 3 aerodynamic teardrop silhouette)
    hw = car_w_px // 2
    hl = car_len_px // 2
    body_pts = [
        (base_cx + hl + nose_offset, base_cy),                          # Front bumper center
        (base_cx + hl - int(0.3 * scale) + nose_offset, base_cy - hw + 4),# Front right nose
        (base_cx + hl - int(1.1 * scale), base_cy - hw),                # Front wheel arch
        (base_cx - int(0.8 * scale), base_cy - hw),                     # Cabin side
        (base_cx - hl + int(0.4 * scale), base_cy - hw + 5),            # Rear quarter
        (base_cx - hl, base_cy - hw + 10),                              # Rear spoiler edge
        (base_cx - hl, base_cy + hw - 10),                              # Rear spoiler edge
        (base_cx - hl + int(0.4 * scale), base_cy + hw - 5),            # Rear quarter
        (base_cx - int(0.8 * scale), base_cy + hw),                     # Cabin side
        (base_cx + hl - int(1.1 * scale), base_cy + hw),                # Front wheel arch
        (base_cx + hl - int(0.3 * scale) + nose_offset, base_cy + hw - 4) # Front left nose
    ]

    # Metallic Body Color
    car_body_col = (215, 25, 45) if settings.power_level < 3 else (15, 20, 28)
    pygame.draw.polygon(car_surf, car_body_col, body_pts)
    pygame.draw.polygon(car_surf, (240, 242, 248), body_pts, 2)

    # Tinted Panoramic Glass Roof
    roof_len = int(2.4 * scale)
    roof_w = int(1.15 * scale)
    roof_rect = pygame.Rect(base_cx - roof_len // 2 - int(0.2 * scale), base_cy - roof_w // 2, roof_len, roof_w)
    pygame.draw.rect(car_surf, (16, 22, 32), roof_rect, border_radius=6)
    pygame.draw.rect(car_surf, (50, 75, 105), roof_rect, 2, border_radius=6)

    # Carbon Fiber Spoiler
    spoiler_rect = pygame.Rect(base_cx - hl - 2, base_cy - hw + 8, max(4, int(0.25 * scale)), car_w_px - 16)
    pygame.draw.rect(car_surf, (25, 25, 30), spoiler_rect, border_radius=2)
    pygame.draw.rect(car_surf, (80, 85, 95), spoiler_rect, 1, border_radius=2)

    # Headlight Beams & Projectors
    hl_y1 = base_cy - hw + 6
    hl_y2 = base_cy + hw - 6
    hl_x = base_cx + hl - int(0.35 * scale) + nose_offset
    pygame.draw.circle(car_surf, (240, 250, 255), (hl_x, hl_y1), max(2, int(2.5 * scale / 14.0)))
    pygame.draw.circle(car_surf, (240, 250, 255), (hl_x, hl_y2), max(2, int(2.5 * scale / 14.0)))

    # Taillights (Tesla LED signature bar)
    tl_x = base_cx - hl + 2
    tl_col = (255, 40, 40) if brake_pressed else (190, 15, 25)
    pygame.draw.line(car_surf, tl_col, (tl_x, base_cy - hw + 10), (tl_x, base_cy - hw + 22), 3)
    pygame.draw.line(car_surf, tl_col, (tl_x, base_cy + hw - 22), (tl_x, base_cy + hw - 10), 3)

    # 4 Wheels & Glowing Brake Rotors
    # Positions relative to base_cx, base_cy
    tire_l = max(6, int(0.68 * scale))
    tire_w = max(3, int(0.26 * scale))
    wheel_offsets = [
        (wb_half, -tw_half, 0, steer_angle),  # FL
        (wb_half, tw_half, 1, steer_angle),   # FR
        (-wb_half, -tw_half, 2, 0.0),         # RL
        (-wb_half, tw_half, 3, 0.0)           # RR
    ]

    for wx, wy, corner_idx, w_steer in wheel_offsets:
        wh_center_x = int(base_cx + wx)
        wh_center_y = int(base_cy + wy)

        # Tire surface to rotate with steering
        tire_surf = pygame.Surface((tire_l + 8, tire_w + 8), pygame.SRCALPHA)
        t_cx = (tire_l + 8) // 2
        t_cy = (tire_w + 8) // 2

        # Rubber tire
        t_rect = pygame.Rect(t_cx - tire_l // 2, t_cy - tire_w // 2, tire_l, tire_w)
        pygame.draw.rect(tire_surf, (25, 26, 30), t_rect, border_radius=2)

        # Glowing Brake Rotor inside rim!
        rotor_col = ThermalBMS.get_rotor_color(thermal_bms.rotor_temps[corner_idx])
        rotor_r = max(2, int(tire_w * 0.42))
        pygame.draw.circle(tire_surf, rotor_col, (t_cx, t_cy), rotor_r)

        # Molten heat halo if rotor > 600°C
        if thermal_bms.rotor_temps[corner_idx] > 600.0:
            halo_r = rotor_r + max(2, int(2.5 * (scale / 14.0)))
            halo_surf = pygame.Surface((halo_r * 2 + 2, halo_r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(halo_surf, (*rotor_col[:3], 90), (halo_r + 1, halo_r + 1), halo_r)
            tire_surf.blit(halo_surf, (t_cx - halo_r - 1, t_cy - halo_r - 1), special_flags=pygame.BLEND_RGBA_ADD)

        # Rotate tire by steering angle
        deg = -math.degrees(w_steer)
        rot_tire = pygame.transform.rotate(tire_surf, deg)
        car_surf.blit(rot_tire, rot_tire.get_rect(center=(wh_center_x, wh_center_y)))

    # Rotate entire car by vehicle heading
    car_deg = -math.degrees(heading)
    rotated_car = pygame.transform.rotate(car_surf, car_deg)
    surface.blit(rotated_car, rotated_car.get_rect(center=(cx, cy)))

# -----------------------------------------------------------------------------
# HUD OVERLAYS, DIAGNOSTICS & SETTINGS DRAWER
# -----------------------------------------------------------------------------
class HUDSystem:
    def __init__(self):
        # Fonts
        self.font_huge = pygame.font.SysFont("Trebuchet MS", 54, bold=True)
        self.font_large = pygame.font.SysFont("Trebuchet MS", 26, bold=True)
        self.font_medium = pygame.font.SysFont("Trebuchet MS", 17, bold=True)
        self.font_small = pygame.font.SysFont("Trebuchet MS", 13)
        self.font_micro = pygame.font.SysFont("Trebuchet MS", 11)
        self.settings_open = False
        self.selected_setting_idx = 0

    def draw_hud(self, surface: pygame.Surface, physics: VehiclePhysics,
                 settings: TrackSettings, thermal_bms: ThermalBMS,
                 drift_scorer: DriftScorer, drag_tree: DragTree,
                 timers: TelemetryTimers, g_meter: GMeter, track_env: TrackEnvironment):
        sw, sh = surface.get_size()

        # ---------------------------------------------------------------------
        # TOP SPEED & POWER TELEMETRY POD (CENTER-TOP)
        # ---------------------------------------------------------------------
        top_bar_rect = pygame.Rect(sw // 2 - 270, 14, 540, 96)
        pygame.draw.rect(surface, (15, 18, 26, 230), top_bar_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_BORDER, top_bar_rect, 2, border_radius=12)

        # Speed readout
        speed_val = f"{int(physics.speed_mph)}"
        speed_lbl = self.font_huge.render(speed_val, True, COLOR_TEXT_WHITE)
        surface.blit(speed_lbl, (sw // 2 - 80, 20))
        unit_lbl = self.font_small.render("MPH", True, COLOR_TEXT_DIM)
        surface.blit(unit_lbl, (sw // 2 + 30, 28))
        kmh_lbl = self.font_small.render(f"{int(physics.speed_kmh)} km/h", True, COLOR_CYAN_GLOW)
        surface.blit(kmh_lbl, (sw // 2 + 30, 48))

        # Mach Number Indicator if in high power mode
        if physics.mach_number >= 0.20:
            mach_col = COLOR_NEON_GREEN if physics.mach_number < 0.85 else (COLOR_WARP_ORANGE if physics.mach_number < 1.0 else (255, 30, 100))
            mach_str = f"MACH {physics.mach_number:.2f}" + (" (SUPERSONIC!)" if physics.mach_number >= 1.0 else "")
            mach_surf = self.font_small.render(mach_str, True, mach_col)
            surface.blit(mach_surf, (sw // 2 + 30, 68))

        # Power Output / Regen Bar
        pwr_kw = physics.power_kw
        pwr_max = 3800.0 if settings.power_level == 3 else (1500.0 if settings.power_level == 2 else 450.0)
        pwr_ratio = max(-1.0, min(1.0, pwr_kw / pwr_max))
        bar_x = sw // 2 - 240
        bar_y = 88
        bar_w = 480
        bar_h = 10
        pygame.draw.rect(surface, (25, 30, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=5)

        half_w = bar_w // 2
        if pwr_ratio >= 0:
            fill_w = int(pwr_ratio * half_w)
            pwr_color = COLOR_WARP_ORANGE if settings.power_level == 3 else COLOR_TESLA_RED
            pygame.draw.rect(surface, pwr_color, (bar_x + half_w, bar_y, fill_w, bar_h), border_radius=5)
        else:
            fill_w = int(abs(pwr_ratio) * half_w)
            pygame.draw.rect(surface, COLOR_NEON_GREEN, (bar_x + half_w - fill_w, bar_y, fill_w, bar_h), border_radius=5)

        pwr_text = f"{int(pwr_kw)} kW  |  {int(physics.torque_nm)} Nm  |  {settings.power_level_names[settings.power_level]}"
        pwr_surf = self.font_micro.render(pwr_text, True, COLOR_TEXT_DIM)
        surface.blit(pwr_surf, (bar_x + 10, bar_y - 14))

        # Gear Selector
        gear_str = "D" if physics.v_long >= -0.5 else "R"
        gear_lbl = self.font_large.render(gear_str, True, COLOR_CYAN_GLOW)
        surface.blit(gear_lbl, (sw // 2 - 210, 32))

        # ---------------------------------------------------------------------
        # 2D G-METER & FRICTION CIRCLE (TOP-LEFT)
        # ---------------------------------------------------------------------
        gm_rect = pygame.Rect(18, 14, 210, 190)
        pygame.draw.rect(surface, (15, 18, 26, 230), gm_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_BORDER, gm_rect, 2, border_radius=12)

        gm_title = self.font_small.render("G-METER ACCELERATION", True, COLOR_TEXT_DIM)
        surface.blit(gm_title, (28, 22))

        gx_center = 123
        gy_center = 115
        max_rad = 60

        # Draw concentric G rings (1.0G, 2.0G)
        pygame.draw.circle(surface, (35, 42, 55), (gx_center, gy_center), int(max_rad * 0.5), 1)
        pygame.draw.circle(surface, (50, 60, 80), (gx_center, gy_center), max_rad, 1)
        pygame.draw.line(surface, (35, 42, 55), (gx_center - max_rad, gy_center), (gx_center + max_rad, gy_center), 1)
        pygame.draw.line(surface, (35, 42, 55), (gx_center, gy_center - max_rad), (gx_center, gy_center + max_rad), 1)

        # Plot G history trail
        for h_lat, h_long, alpha in g_meter.history:
            px = int(gx_center + (h_lat / 2.0) * max_rad)
            py = int(gy_center - (h_long / 2.0) * max_rad)
            px = max(gx_center - max_rad, min(gx_center + max_rad, px))
            py = max(gy_center - max_rad, min(gy_center + max_rad, py))
            col = (int(0 * alpha), int(220 * alpha), int(255 * alpha))
            pygame.draw.circle(surface, col, (px, py), 2)

        # Live current G point
        cur_px = int(gx_center + (g_meter.lat_g / 2.0) * max_rad)
        cur_py = int(gy_center - (g_meter.long_g / 2.0) * max_rad)
        cur_px = max(gx_center - max_rad, min(gx_center + max_rad, cur_px))
        cur_py = max(gy_center - max_rad, min(gy_center + max_rad, cur_py))
        pygame.draw.circle(surface, (255, 36, 66), (cur_px, cur_py), 5)
        pygame.draw.circle(surface, (255, 255, 255), (cur_px, cur_py), 2)

        # Numeric G
        g_txt = f"LAT: {g_meter.lat_g:+.2f}G | LONG: {g_meter.long_g:+.2f}G"
        g_readout = self.font_micro.render(g_txt, True, COLOR_TEXT_WHITE)
        surface.blit(g_readout, (26, 182))

        # ---------------------------------------------------------------------
        # DRIFT TELEMETRY & COMBO POD (TOP-RIGHT)
        # ---------------------------------------------------------------------
        drift_rect = pygame.Rect(sw - 280, 14, 262, 190)
        pygame.draw.rect(surface, (15, 18, 26, 230), drift_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_BORDER, drift_rect, 2, border_radius=12)

        d_title = self.font_small.render("DRIFT TELEMETRY", True, COLOR_TEXT_DIM)
        surface.blit(d_title, (sw - 268, 22))

        # Live Drift Angle
        angle_col = COLOR_TEXT_DIM if drift_scorer.drift_angle < 7.5 else (COLOR_NEON_GREEN if drift_scorer.drift_angle < 30 else (COLOR_WARP_ORANGE if drift_scorer.drift_angle < 60 else (255, 30, 100)))
        angle_str = f"ANGLE: {drift_scorer.drift_angle:.1f}°"
        angle_lbl = self.font_large.render(angle_str, True, angle_col)
        surface.blit(angle_lbl, (sw - 268, 44))

        # Multiplier
        mult_str = f"x{drift_scorer.multiplier:.1f} MULTIPLIER"
        mult_col = COLOR_CYAN_GLOW if drift_scorer.multiplier > 1.0 else COLOR_TEXT_MUTED
        mult_lbl = self.font_medium.render(mult_str, True, mult_col)
        surface.blit(mult_lbl, (sw - 268, 76))

        # Points
        pts_str = f"POINTS: {int(drift_scorer.current_score):,}"
        pts_lbl = self.font_medium.render(pts_str, True, COLOR_WARNING_YELLOW if drift_scorer.current_score > 0 else COLOR_TEXT_DIM)
        surface.blit(pts_lbl, (sw - 268, 102))

        banked_str = f"BANKED: {int(drift_scorer.banked_score):,}"
        banked_lbl = self.font_small.render(banked_str, True, COLOR_TEXT_MUTED)
        surface.blit(banked_lbl, (sw - 268, 128))

        # Badge banner
        if drift_scorer.badge_timer > 0:
            badge_lbl = self.font_small.render(drift_scorer.last_badge, True, COLOR_NEON_GREEN)
            surface.blit(badge_lbl, (sw - 268, 154))
        elif settings.line_lock_active:
            ll_lbl = self.font_small.render("🔒 LINE LOCK BURNOUT ACTIVE!", True, (255, 60, 60))
            surface.blit(ll_lbl, (sw - 268, 154))

        # ---------------------------------------------------------------------
        # 4-CORNER THERMAL & CHASSIS TELEMETRY POD (BOTTOM-LEFT)
        # ---------------------------------------------------------------------
        pod_rect = pygame.Rect(18, sh - 275, 320, 215)
        pygame.draw.rect(surface, (15, 18, 26, 230), pod_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_BORDER, pod_rect, 2, border_radius=12)

        pod_title = self.font_small.render("CHASSIS 4-CORNER THERMODYNAMICS", True, COLOR_TEXT_DIM)
        surface.blit(pod_title, (28, sh - 267))

        corners = ["FL", "FR", "RL", "RR"]
        corner_coords = [
            (32, sh - 240),   # FL
            (175, sh - 240),  # FR
            (32, sh - 165),   # RL
            (175, sh - 165)   # RR
        ]
        for idx, (cx_pos, cy_pos) in enumerate(corner_coords):
            c_name = corners[idx]
            r_temp = thermal_bms.rotor_temps[idx]
            t_temp = thermal_bms.tire_temps[idx]
            t_psi = thermal_bms.tire_pressures[idx]

            # Rotor color indicator box
            r_col = ThermalBMS.get_rotor_color(r_temp)
            pygame.draw.rect(surface, r_col, (cx_pos, cy_pos + 4, 12, 45), border_radius=3)
            pygame.draw.rect(surface, (100, 110, 130), (cx_pos, cy_pos + 4, 12, 45), 1, border_radius=3)

            # Labels
            c_hdr = self.font_micro.render(f"{c_name} TIRE & ROTOR", True, COLOR_CYAN_GLOW)
            surface.blit(c_hdr, (cx_pos + 18, cy_pos + 2))
            r_str = f"ROTOR: {int(r_temp)}°C"
            r_lbl = self.font_small.render(r_str, True, (255, 180, 80) if r_temp > 500 else COLOR_TEXT_WHITE)
            surface.blit(r_lbl, (cx_pos + 18, cy_pos + 18))
            t_str = f"{t_psi:.1f} PSI | {int(t_temp)}°C"
            t_lbl = self.font_micro.render(t_str, True, COLOR_TEXT_DIM)
            surface.blit(t_lbl, (cx_pos + 18, cy_pos + 36))

        # Brake fade warning banner
        if thermal_bms.brake_fade_factor < 0.95:
            fade_pct = int((1.0 - thermal_bms.brake_fade_factor) * 100)
            fade_lbl = self.font_micro.render(f"⚠️ BRAKE FADE DETECTED: -{fade_pct}% EFFECTIVENESS", True, (255, 60, 60))
            surface.blit(fade_lbl, (28, sh - 88))
        else:
            fade_lbl = self.font_micro.render(f"BRAKES: 100% GRIP ({settings.brake_types[settings.brake_type_idx]})", True, COLOR_NEON_GREEN)
            surface.blit(fade_lbl, (28, sh - 88))

        # ---------------------------------------------------------------------
        # POWERTRAIN, BATTERY & OCTOVALVE POD (BOTTOM-RIGHT)
        # ---------------------------------------------------------------------
        batt_rect = pygame.Rect(sw - 338, sh - 275, 320, 215)
        pygame.draw.rect(surface, (15, 18, 26, 230), batt_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_BORDER, batt_rect, 2, border_radius=12)

        batt_title = self.font_small.render("POWERTRAIN & OCTOVALVE BMS", True, COLOR_TEXT_DIM)
        surface.blit(batt_title, (sw - 326, sh - 267))

        soc_str = f"BATTERY SOC: {thermal_bms.soc_pct:.1f}%"
        soc_lbl = self.font_medium.render(soc_str, True, COLOR_NEON_GREEN if thermal_bms.soc_pct > 25 else COLOR_TESLA_RED)
        surface.blit(soc_lbl, (sw - 326, sh - 240))

        # Small battery charge bar
        b_bar_x = sw - 326
        b_bar_y = sh - 215
        pygame.draw.rect(surface, (30, 35, 45), (b_bar_x, b_bar_y, 290, 8), border_radius=4)
        pygame.draw.rect(surface, COLOR_NEON_GREEN, (b_bar_x, b_bar_y, int(290 * (thermal_bms.soc_pct / 100.0)), 8), border_radius=4)

        b_temp_str = f"PACK TEMP: {thermal_bms.battery_temp:.1f}°C"
        surface.blit(self.font_small.render(b_temp_str, True, COLOR_TEXT_WHITE), (sw - 326, sh - 198))

        mot_str = f"MOTORS: F {int(thermal_bms.motor_front_temp)}°C  |  R {int(thermal_bms.motor_rear_temp)}°C"
        surface.blit(self.font_small.render(mot_str, True, COLOR_TEXT_DIM), (sw - 326, sh - 176))

        inv_str = f"INVERTER SiC: {int(thermal_bms.inverter_temp)}°C  |  RPM: {int(physics.rpm):,}"
        surface.blit(self.font_small.render(inv_str, True, COLOR_TEXT_DIM), (sw - 326, sh - 154))

        octo_str = f"OCTOVALVE: {settings.thermal_loops[settings.thermal_loop_idx]}"
        surface.blit(self.font_micro.render(octo_str, True, COLOR_CYAN_GLOW), (sw - 326, sh - 130))

        track_name = track_env.mode_names[track_env.current_mode]
        surface.blit(self.font_micro.render(f"TRACK: {track_name} [T to cycle]", True, COLOR_WARNING_YELLOW), (sw - 326, sh - 105))

        # Cheetah stance indicator
        if physics.cheetah_stance > 0.1:
            ch_str = f"🐆 CHEETAH LAUNCH STANCE: {int(physics.cheetah_stance*100)}%"
            surface.blit(self.font_micro.render(ch_str, True, COLOR_WARP_ORANGE), (sw - 326, sh - 82))

        # ---------------------------------------------------------------------
        # NHRA DRAG STRIP TIMING SLIPS (CENTER-BOTTOM)
        # ---------------------------------------------------------------------
        if track_env.current_mode == TrackEnvironment.MODE_DRAG_STRIP:
            strip_card_rect = pygame.Rect(sw // 2 - 220, sh - 215, 440, 155)
            pygame.draw.rect(surface, (15, 18, 26, 230), strip_card_rect, border_radius=12)
            pygame.draw.rect(surface, COLOR_BORDER, strip_card_rect, 2, border_radius=12)

            sc_title = self.font_small.render("NHRA DRAG TIMING SLIP (0.001s ACCURACY)", True, COLOR_TEXT_DIM)
            surface.blit(sc_title, (sw // 2 - 205, sh - 207))

            rt_val = f"{drag_tree.reaction_time:.3f}s" if drag_tree.reaction_time is not None else ("RED LIGHT FOUL!" if drag_tree.state == DragTree.STATE_RED_FOUL else "--")
            rt_col = COLOR_NEON_GREEN if (drag_tree.reaction_time and drag_tree.reaction_time > 0) else ((255, 40, 40) if drag_tree.state == DragTree.STATE_RED_FOUL else COLOR_TEXT_MUTED)

            lines_left = [
                f"REACTION TIME (RT): {rt_val}",
                f"60 FT: {timers.time_60ft:.3f}s" if timers.time_60ft else "60 FT: --",
                f"330 FT: {timers.time_330ft:.3f}s" if timers.time_330ft else "330 FT: --",
                f"1/8 MILE: {timers.time_660ft:.3f}s @ {timers.speed_660ft:.1f} MPH" if timers.time_660ft else "1/8 MILE: --"
            ]
            lines_right = [
                f"0-60 MPH: {timers.time_0_60:.3f}s" if timers.time_0_60 else "0-60 MPH: --",
                f"0-100 MPH: {timers.time_0_100:.3f}s" if timers.time_0_100 else "0-100 MPH: --",
                f"1,000 FT: {timers.time_1000ft:.3f}s" if timers.time_1000ft else "1,000 FT: --",
                f"1/4 MILE: {timers.time_1320ft:.3f}s @ {timers.speed_1320ft:.1f} MPH" if timers.time_1320ft else "1/4 MILE: --"
            ]
            for i, l_txt in enumerate(lines_left):
                col = rt_col if i == 0 else COLOR_TEXT_WHITE
                surface.blit(self.font_small.render(l_txt, True, col), (sw // 2 - 205, sh - 182 + i * 22))

            for i, r_txt in enumerate(lines_right):
                surface.blit(self.font_small.render(r_txt, True, COLOR_TEXT_WHITE), (sw // 2 + 30, sh - 182 + i * 22))

        # ---------------------------------------------------------------------
        # KEYBOARD CONTROLS BAR (VERY BOTTOM)
        # ---------------------------------------------------------------------
        ctrl_rect = pygame.Rect(0, sh - 42, sw, 42)
        pygame.draw.rect(surface, (10, 12, 16), ctrl_rect)
        pygame.draw.line(surface, COLOR_BORDER, (0, sh - 42), (sw, sh - 42), 1)

        ctrl_text = "[W/S] Throttle/Brake  |  [A/D] Steer  |  [SPACE] Handbrake Drift  |  [K] Line Lock Burnout  |  [TAB] Track Mode V3 Menu  |  [T] Track  |  [R] Reset  |  [C] Clear Slips  |  [M] Mute"
        ctrl_lbl = self.font_small.render(ctrl_text, True, COLOR_CYAN_GLOW)
        surface.blit(ctrl_lbl, (sw // 2 - ctrl_lbl.get_width() // 2, sh - 28))

        # ---------------------------------------------------------------------
        # TRACK MODE V3 SETTINGS DRAWER OVERLAY
        # ---------------------------------------------------------------------
        if self.settings_open:
            self.draw_settings_drawer(surface, settings)

    def draw_settings_drawer(self, surface: pygame.Surface, settings: TrackSettings):
        sw, sh = surface.get_size()
        dw = 620
        dh = 640
        dx = sw // 2 - dw // 2
        dy = sh // 2 - dh // 2

        # Dim background
        dim_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 180))
        surface.blit(dim_surf, (0, 0))

        # Main drawer window
        drawer_rect = pygame.Rect(dx, dy, dw, dh)
        pygame.draw.rect(surface, (16, 20, 28), drawer_rect, border_radius=14)
        pygame.draw.rect(surface, (255, 36, 66), drawer_rect, 2, border_radius=14)

        # Title
        title_lbl = self.font_large.render("TESLA TRACK MODE V3 // PERFORMANCE SUITE", True, COLOR_TEXT_WHITE)
        surface.blit(title_lbl, (dx + 25, dy + 20))
        sub_lbl = self.font_micro.render("Use UP/DOWN arrows to select, LEFT/RIGHT arrows to change. Press TAB to close.", True, COLOR_TEXT_DIM)
        surface.blit(sub_lbl, (dx + 25, dy + 54))

        menu_items = [
            ("POWER PROFILE", settings.power_level_names[settings.power_level], COLOR_WARP_ORANGE if settings.power_level == 3 else COLOR_TESLA_RED),
            ("HANDLING BALANCE (TORQUE SPLIT)", settings.torque_splits[settings.torque_split_idx][2], COLOR_CYAN_GLOW),
            ("STABILITY ASSIST", f"{settings.stability_assist:+d} " + ("(OFF)" if settings.stability_assist == -10 else ("(NORMAL)" if settings.stability_assist == 10 else "(SPORT)")), COLOR_TEXT_WHITE),
            ("REGENERATIVE BRAKING", f"{int(settings.regen_level * 100)}%", COLOR_NEON_GREEN),
            ("TIRE COMPOUND", settings.tire_compounds[settings.tire_compound_idx][1], COLOR_TEXT_WHITE),
            ("BRAKE ROTOR HARDWARE", settings.brake_types[settings.brake_type_idx], COLOR_WARNING_YELLOW),
            ("AERODYNAMICS DOWNFORCE", settings.aero_levels[settings.aero_idx][2], COLOR_TEXT_WHITE),
            ("TOP SPEED GOVERNOR", "OFF (UNLIMITED 650+ MPH)" if not settings.speed_governor else "ON (163 MPH OEM CAP)", (255, 50, 50) if not settings.speed_governor else COLOR_TEXT_DIM),
            ("OCTOVALVE THERMAL LOOP", settings.thermal_loops[settings.thermal_loop_idx], COLOR_CYAN_GLOW),
            ("ELECTRONIC LINE LOCK BURNOUT", "ACTIVE" if settings.line_lock_active else "INACTIVE", (255, 50, 50) if settings.line_lock_active else COLOR_TEXT_MUTED)
        ]

        start_y = dy + 95
        for i, (label, val_str, val_col) in enumerate(menu_items):
            item_rect = pygame.Rect(dx + 20, start_y + i * 48, dw - 40, 42)
            is_sel = (i == self.selected_setting_idx)
            bg_col = (30, 38, 54) if is_sel else (20, 25, 35)
            pygame.draw.rect(surface, bg_col, item_rect, border_radius=8)
            if is_sel:
                pygame.draw.rect(surface, COLOR_CYAN_GLOW, item_rect, 2, border_radius=8)

            lbl_surf = self.font_small.render(label, True, COLOR_TEXT_WHITE if is_sel else COLOR_TEXT_DIM)
            val_surf = self.font_small.render(val_str, True, val_col)
            surface.blit(lbl_surf, (dx + 35, start_y + i * 48 + 12))
            surface.blit(val_surf, (dx + dw - val_surf.get_width() - 35, start_y + i * 48 + 12))

        # Quick preset buttons hint
        hint_str = "QUICK PRESETS: [1] Stock  |  [2] Track Pro  |  [3] Drift King  |  [4] Mach 1 Hyper-Warp"
        hint_lbl = self.font_micro.render(hint_str, True, COLOR_WARNING_YELLOW)
        surface.blit(hint_lbl, (dx + 25, dy + dh - 32))

    def handle_input(self, event: pygame.event.Event, settings: TrackSettings, sound: SoundSynthesizer):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.settings_open = not self.settings_open
                sound.play_chime(880.0, 0.1)
                return True
            if not self.settings_open:
                # Direct preset keys when drawer is closed
                if event.key == pygame.K_1:
                    settings.apply_stock()
                    sound.play_chime(520.0, 0.12)
                elif event.key == pygame.K_2:
                    settings.apply_track()
                    sound.play_chime(650.0, 0.12)
                elif event.key == pygame.K_3:
                    settings.apply_drift()
                    sound.play_chime(780.0, 0.12)
                elif event.key == pygame.K_4:
                    settings.apply_mach_warp()
                    sound.play_chime(1040.0, 0.18)
                return False

            if event.key == pygame.K_UP:
                self.selected_setting_idx = (self.selected_setting_idx - 1) % 10
                sound.play_chime(440.0, 0.08)
            elif event.key == pygame.K_DOWN:
                self.selected_setting_idx = (self.selected_setting_idx + 1) % 10
                sound.play_chime(440.0, 0.08)
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                direction = 1 if event.key == pygame.K_RIGHT else -1
                idx = self.selected_setting_idx

                if idx == 0:  # Power Level
                    settings.power_level = (settings.power_level + direction) % 4
                elif idx == 1:  # Torque Split
                    settings.torque_split_idx = (settings.torque_split_idx + direction) % len(settings.torque_splits)
                elif idx == 2:  # Stability
                    settings.stability_assist = max(-10, min(10, settings.stability_assist + direction * 5))
                elif idx == 3:  # Regen
                    settings.regen_level = round(max(0.0, min(1.0, settings.regen_level + direction * 0.2)), 2)
                elif idx == 4:  # Tire Compound
                    settings.tire_compound_idx = (settings.tire_compound_idx + direction) % len(settings.tire_compounds)
                elif idx == 5:  # Brake Type
                    settings.brake_type_idx = (settings.brake_type_idx + direction) % len(settings.brake_types)
                elif idx == 6:  # Aero
                    settings.aero_idx = (settings.aero_idx + direction) % len(settings.aero_levels)
                elif idx == 7:  # Governor
                    settings.speed_governor = not settings.speed_governor
                elif idx == 8:  # Thermal Loop
                    settings.thermal_loop_idx = (settings.thermal_loop_idx + direction) % len(settings.thermal_loops)
                elif idx == 9:  # Line Lock
                    settings.line_lock_active = not settings.line_lock_active
                sound.play_chime(660.0, 0.08)
            return True
        return False

# -----------------------------------------------------------------------------
# MAIN APPLICATION CONTROLLER
# -----------------------------------------------------------------------------
class TeslaTrackSimulatorApp:
    def __init__(self):
        pygame.display.set_caption("TESLA MODEL 3 PERFORMANCE // ULTIMATE TRACK TELEMETRY V7.0")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Subsystems
        self.settings = TrackSettings()
        self.sound = SoundSynthesizer()
        self.thermal_bms = ThermalBMS()
        self.timers = TelemetryTimers()
        self.g_meter = GMeter()
        self.physics = VehiclePhysics()
        self.drift_scorer = DriftScorer()
        self.drag_tree = DragTree()
        self.particle_sys = ParticleSystem()
        self.track_env = TrackEnvironment()
        self.hud = HUDSystem()

        # Camera state
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.cam_scale = 16.0

        # Prev wheel positions for skid marks
        self.prev_wheel_pos: List[Tuple[float, float]] = []

    def run(self):
        while self.running:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)

            # -----------------------------------------------------------------
            # EVENT HANDLING
            # -----------------------------------------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.hud.settings_open:
                            self.hud.settings_open = False
                        else:
                            self.running = False
                    elif self.hud.handle_input(event, self.settings, self.sound):
                        pass
                    elif event.key == pygame.K_k:
                        self.settings.line_lock_active = not self.settings.line_lock_active
                        self.sound.play_chime(700.0 if self.settings.line_lock_active else 350.0, 0.15)
                    elif event.key == pygame.K_t:
                        mode_name = self.track_env.cycle_mode()
                        self.physics.reset_position(0.0, 0.0, 0.0)
                        self.timers.reset()
                        self.drag_tree.reset()
                        self.sound.play_chime(900.0, 0.15)
                    elif event.key == pygame.K_r:
                        self.physics.reset_position(0.0, 0.0, 0.0)
                        self.timers.reset()
                        self.drag_tree.reset()
                        self.sound.play_chime(500.0, 0.15)
                    elif event.key == pygame.K_c:
                        self.timers.reset()
                        self.drag_tree.reset()
                        self.drift_scorer.banked_score = 0.0
                        self.sound.play_chime(600.0, 0.15)
                    elif event.key == pygame.K_m:
                        self.sound.muted = not self.sound.muted
                    elif event.key == pygame.K_u:
                        self.settings.speed_governor = not self.settings.speed_governor
                        self.sound.play_chime(750.0, 0.12)

            # -----------------------------------------------------------------
            # CONTINUOUS USER INPUTS
            # -----------------------------------------------------------------
            keys = pygame.key.get_pressed()
            throttle = 0.0
            brake = 0.0
            steer = 0.0
            handbrake = False

            if not self.hud.settings_open:
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    throttle = 1.0
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    brake = 1.0
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    steer = 1.0
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    steer = -1.0
                if keys[pygame.K_SPACE]:
                    handbrake = True

            # -----------------------------------------------------------------
            # SIMULATION UPDATE
            # -----------------------------------------------------------------
            is_staged = (self.drag_tree.state in (DragTree.STATE_STAGED, DragTree.STATE_COUNTDOWN))
            self.physics.update(
                dt, throttle, brake, steer, handbrake,
                self.settings, self.thermal_bms, self.sound, is_staged
            )

            # Update Thermal BMS
            self.thermal_bms.update(
                dt, self.physics.speed_mps, self.physics.wheel_slip,
                brake, self.physics.power_kw, self.settings, self.physics.is_burnout
            )

            # Update Timers, G-Meter, Drift Scorer, Drag Tree
            self.timers.update(dt, self.physics.speed_mph, self.physics.long_g, self.physics.lat_g)
            self.g_meter.update(dt, self.physics.lat_g, self.physics.long_g)
            self.drift_scorer.update(dt, self.physics.v_long, self.physics.v_lat, self.physics.speed_mph)
            if self.track_env.current_mode == TrackEnvironment.MODE_DRAG_STRIP:
                self.drag_tree.update(dt, self.physics.x, self.physics.speed_mph, self.sound)

            # Update Audio Synthesizer
            slip_spd = abs(self.physics.v_lat) + (25.0 if self.physics.is_burnout else 0.0)
            self.sound.update(
                self.physics.rpm, self.physics.power_kw,
                slip_spd, self.settings.power_level, throttle
            )

            # -----------------------------------------------------------------
            # PARTICLE & SKID MARKS LOGIC
            # -----------------------------------------------------------------
            cos_h = math.cos(self.physics.heading)
            sin_h = math.sin(self.physics.heading)
            wb_h = self.physics.wheelbase / 2.0
            tw_h = self.physics.track_width / 2.0

            # 4 wheel world locations
            cur_wheel_coords = [
                (self.physics.x + (wb_h * cos_h - (-tw_h) * sin_h), self.physics.y + (wb_h * sin_h + (-tw_h) * cos_h)), # FL
                (self.physics.x + (wb_h * cos_h - tw_h * sin_h),    self.physics.y + (wb_h * sin_h + tw_h * cos_h)),    # FR
                (self.physics.x + (-wb_h * cos_h - (-tw_h) * sin_h), self.physics.y + (-wb_h * sin_h + (-tw_h) * cos_h)), # RL
                (self.physics.x + (-wb_h * cos_h - tw_h * sin_h),    self.physics.y + (-wb_h * sin_h + tw_h * cos_h))   # RR
            ]

            # Smoke and skids per wheel
            for i, (wx, wy) in enumerate(cur_wheel_coords):
                slip = self.physics.wheel_slip[i]
                if self.physics.is_burnout and i >= 2:  # Huge burnout smoke
                    self.particle_sys.add_smoke(wx, wy, density=2.5)
                elif slip > 0.28:
                    self.particle_sys.add_smoke(wx, wy, density=slip * 1.6)

                if len(self.prev_wheel_pos) == 4 and (slip > 0.35 or handbrake):
                    px, py = self.prev_wheel_pos[i]
                    self.particle_sys.add_skid(px, py, wx, wy, slip)

            self.prev_wheel_pos = cur_wheel_coords

            # Rocket Thrusters / Supersonic Flames
            if self.settings.power_level >= 2 and throttle > 0.2:
                rear_x = self.physics.x - (self.physics.wheelbase * 0.8) * cos_h
                rear_y = self.physics.y - (self.physics.wheelbase * 0.8) * sin_h
                self.particle_sys.add_thruster(rear_x, rear_y, self.physics.heading, throttle)

            # Supersonic Shockwave Ring
            if self.physics.mach_number >= 1.0 and random.random() < 0.25:
                self.particle_sys.add_shockwave(self.physics.x, self.physics.y)

            self.particle_sys.update(dt)

            # -----------------------------------------------------------------
            # DYNAMIC CAMERA SMOOTHING & ZOOM
            # -----------------------------------------------------------------
            self.cam_x += (self.physics.x - self.cam_x) * min(1.0, dt * 10.0)
            self.cam_y += (self.physics.y - self.cam_y) * min(1.0, dt * 10.0)

            # Zoom out at supersonic speeds
            target_scale = max(6.0, 16.0 - (self.physics.speed_mph / 650.0) * 10.0)
            self.cam_scale += (target_scale - self.cam_scale) * min(1.0, dt * 5.0)

            # -----------------------------------------------------------------
            # RENDERING PIPELINE
            # -----------------------------------------------------------------
            self.screen.fill(COLOR_BG)

            # 1. World & Track & Particles
            self.track_env.draw_world(
                self.screen, self.cam_x, self.cam_y,
                self.cam_scale, self.drag_tree, self.particle_sys
            )

            # 2. Car Model Top-Down Sprite
            sw, sh = self.screen.get_size()
            car_screen_x = int(sw // 2 + (self.physics.x - self.cam_x) * self.cam_scale)
            car_screen_y = int(sh // 2 - (self.physics.y - self.cam_y) * self.cam_scale)

            draw_tesla_model_3(
                self.screen, car_screen_x, car_screen_y,
                self.physics.heading, self.physics.steer_angle, self.cam_scale,
                brake > 0.1, self.settings, self.thermal_bms, self.physics.cheetah_stance
            )

            # 3. HUD Overlays & Settings
            self.hud.draw_hud(
                self.screen, self.physics, self.settings, self.thermal_bms,
                self.drift_scorer, self.drag_tree, self.timers, self.g_meter, self.track_env
            )

            pygame.display.flip()

        pygame.quit()

def main():
    app = TeslaTrackSimulatorApp()
    app.run()

if __name__ == "__main__":
    main()
