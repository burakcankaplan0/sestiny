"""Frekans, MIDI nota numarası ve nota adı arasında dönüşüm.

Standart MIDI formülü kullanılır, A4 referansı 440 Hz'dir (bkz. CLAUDE.md bölüm 11).
Nota adları diyezli gösterilir (C#3, F#4 gibi); ilk sürümde bemol kullanılmaz.
"""

import math

import numpy as np

A4_HZ = 440.0
A4_MIDI = 69

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def hz_to_midi(frequency_hz: float) -> float:
    """Tek bir frekansı (Hz) kesirli MIDI nota numarasına çevirir."""
    if frequency_hz <= 0:
        raise ValueError("Frekans pozitif olmalı.")
    return A4_MIDI + 12 * math.log2(frequency_hz / A4_HZ)


def hz_array_to_midi(frequency_hz: np.ndarray) -> np.ndarray:
    """hz_to_midi'nin dizi (numpy) hâli. Girdi yalnızca pozitif frekanslar içermelidir."""
    return A4_MIDI + 12 * np.log2(frequency_hz / A4_HZ)


def midi_to_note_name(midi_number: float) -> str:
    """En yakın yarım tona yuvarlayıp nota adını döndürür (örn. 'C#3')."""
    rounded = round(midi_number)
    note = NOTE_NAMES[rounded % 12]
    octave = rounded // 12 - 1
    return f"{note}{octave}"


def hz_to_note_name(frequency_hz: float) -> str:
    return midi_to_note_name(hz_to_midi(frequency_hz))
