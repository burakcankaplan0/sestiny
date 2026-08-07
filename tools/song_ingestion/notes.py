"""Frekans ↔ MIDI ↔ nota adı dönüşümü.

Bu, backend/app/services/music_theory.py'nin bilinçli, bağımlılıksız bir
kopyasıdır (yalnızca skaler işlevler, numpy yok). Neden kopya: lab'ı backend'in
paketine (ve dolaylı olarak ağır venv'ine) bağlamamak için. Formül aynıdır —
standart MIDI, A4 = 440 Hz — böylece lab ve production aynı notaları üretir.
"""

import math

A4_HZ = 440.0
A4_MIDI = 69
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def hz_to_midi(frequency_hz: float) -> float:
    """Tek bir frekansı (Hz) kesirli MIDI nota numarasına çevirir."""
    if frequency_hz <= 0:
        raise ValueError("Frekans pozitif olmalı.")
    return A4_MIDI + 12 * math.log2(frequency_hz / A4_HZ)


def midi_to_note_name(midi_number: float) -> str:
    """En yakın yarım tona yuvarlayıp nota adını döndürür (örn. 'C#3')."""
    rounded = round(midi_number)
    note = NOTE_NAMES[rounded % 12]
    octave = rounded // 12 - 1
    return f"{note}{octave}"


def hz_to_note_name(frequency_hz: float) -> str:
    return midi_to_note_name(hz_to_midi(frequency_hz))
