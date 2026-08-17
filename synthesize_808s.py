"""Create six original synthetic 808 one-shots as 48 kHz, 24-bit WAV files."""

import math
import random
import wave
from pathlib import Path


RATE = 48_000
TAU = math.tau
OUT = Path("/Users/marcusarocha/Desktop/kit/808")


def clip(value, drive=1.0):
    return math.tanh(value * drive) / math.tanh(drive)


def amp_env(t, attack, decay):
    if t < attack:
        return t / max(attack, 0.0001)
    return math.exp(-(t - attack) / decay)


def make_lcd(t, phase, noise):
    glide = 1 + 0.72 * math.exp(-t / 0.038)
    body = math.sin(phase) + 0.022 * math.sin(2 * phase)
    click = (noise * 0.16 + math.sin(TAU * 4_300 * t) * 0.08) * math.exp(-t / 0.004)
    return (body * amp_env(t, 0.001, 0.78) * 0.96 + click, 46 * glide)


def make_battery_low(t, phase, noise):
    sag = 1 - 0.23 * (1 - math.exp(-t / 0.2))
    wobble = 1 + 0.027 * math.sin(TAU * 1.3 * t) + 0.012 * math.sin(TAU * 4.8 * t)
    hollow = 0.55 * math.sin(phase) - 0.3 * math.sin(2 * phase) + 0.16 * math.sin(3 * phase)
    sputter = (round(math.sin(phase) * 7) / 7 - math.sin(phase)) * 0.18 * math.exp(-t / 0.32)
    transient = noise * 0.055 * math.exp(-t / 0.028)
    return ((hollow + sputter) * amp_env(t, 0.018, 0.25) + transient, 44 * sag * wobble)


def make_flash(t, phase, noise):
    body = math.sin(phase)
    metallic = clip(math.sin(phase) + 0.55 * math.sin(2.7 * phase), 4.0) - body
    attack = clip(noise * 0.8 + math.sin(TAU * 5_600 * t) * 0.24, 4.0) * math.exp(-t / 0.006)
    knock = math.sin(TAU * (155 - 95 * min(t / 0.035, 1)) * t) * math.exp(-t / 0.028) * 0.42
    return (body * amp_env(t, 0.0005, 0.28) * 0.94 + metallic * math.exp(-t / 0.12) * 0.22 + attack + knock, 58)


def make_memory_card(t, phase, noise):
    bend = 1 + 0.58 * math.exp(-t / 0.095)
    body = math.sin(phase)
    rubber = 0.28 * math.sin(2.18 * phase + 0.8) * math.exp(-t / 0.7)
    ring = 0.17 * math.sin(TAU * 132 * t) * math.exp(-t / 0.58)
    knock = (noise * 0.06 + math.sin(TAU * 230 * t) * 0.08) * math.exp(-t / 0.018)
    steady = amp_env(t, 0.006, 1.2) * (0.7 + 0.22 * min(t / 0.12, 1))
    return ((body + rubber + ring) * steady + knock, 48 * bend)


def make_night_mode(t, phase, noise):
    body = math.sin(phase)
    warm = clip(body, 2.4) - body
    fog = math.sin(phase * 0.5) * 0.04
    attack = min(t / 0.16, 1)
    slow_dist = (1 - math.exp(-t / 0.52))
    return ((body * 0.94 + warm * 0.5 * slow_dist + fog) * attack * math.exp(-t / 1.35), 36)


def make_corrupted(t, phase, noise):
    wobble = 1 + 0.044 * math.sin(TAU * 5.6 * t) + 0.017 * math.sin(TAU * 17.4 * t)
    body = math.sin(phase)
    digital = round(body * 5) / 5 - body
    crack = clip(noise * 1.2 + math.sin(TAU * 7_700 * t) * 0.35, 5.0) * math.exp(-t / 0.024)
    bursts = (1 if int(t * 1_400) % 9 in (0, 1) else 0) * noise * math.exp(-t / 0.085) * 0.28
    unstable = 0.1 * math.sin(phase * 1.97) * math.exp(-t / 0.35)
    return (body * amp_env(t, 0.001, 0.86) * 0.88 + digital * math.exp(-t / 0.22) * 0.46 + crack + bursts + unstable, 47 * wobble)


SOUNDS = [
    ("01 - LCD.wav", 1.5, make_lcd),
    ("02 - BATTERY LOW.wav", 0.7, make_battery_low),
    ("03 - FLASH.wav", 0.72, make_flash),
    ("04 - MEMORY CARD.wav", 1.55, make_memory_card),
    ("05 - NIGHT MODE.wav", 2.2, make_night_mode),
    ("06 - CORRUPTED.wav", 1.55, make_corrupted),
]


def render(duration, sound, seed):
    random.seed(seed)
    values = []
    phase = 0.0
    for index in range(int(duration * RATE)):
        t = index / RATE
        value, frequency = sound(t, phase, random.uniform(-1, 1))
        phase += TAU * frequency / RATE
        values.append(value)

    peak = max(max(values), -min(values), 0.001)
    return [max(-0.96, min(0.96, value / peak * 0.91)) for value in values]


def write_wav(path, values):
    frames = bytearray()
    for value in values:
        sample = int(value * 8_388_607)
        frames.extend((sample & 0xff, (sample >> 8) & 0xff, (sample >> 16) & 0xff))
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(3)
        output.setframerate(RATE)
        output.writeframes(frames)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for index, (filename, duration, sound) in enumerate(SOUNDS, start=1):
        write_wav(OUT / filename, render(duration, sound, index))
        print("created", filename)


if __name__ == "__main__":
    main()
