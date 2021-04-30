import math
VELOCITY_SPLITS = 16
DEFAULT_PPQ = 480


# Converts ticks to MS based on current BPM and Default pulses per quarter note (PPQ)
def ticks2ms(tick, bpm):
    # PPQ = Listed in header of MIDI (480 by default for Listz dataset)
    ms_per_tick = 60_000 / (bpm * DEFAULT_PPQ)
    return round(tick * ms_per_tick)


# Split velocity (0-128) into SPLITS parts
def simplify_velocity(velocity, splits):
    # +1 because the range is 0-127
    return math.ceil((velocity+1)/(128/splits))


# Return velocity back into MIDI velocity
def unsimplify_velocity(velocity, splits):
    # -1 because the range is 0-127
    return round((velocity*(128/splits))-1)


class MidiEvent:
    def __init__(self, start_time=0):
        self.start_time = start_time


class TempoEvent(MidiEvent):
    def __init__(self, start_time=0, tempo=0):
        super().__init__(start_time)
        self.tempo = tempo
        # Round BPM to nearest 10th
        self.bpm = round(round(60_000_000 / tempo), -1)


class SustainOnEvent(MidiEvent):
    pass


class SustainOffEvent(MidiEvent):
    pass


class NoteOnEvent(MidiEvent):
    def __init__(self, start_time=0,  note=0):
        super().__init__(start_time)
        self.note = note


class NoteOffEvent(MidiEvent):
    def __init__(self, start_time=0,  note=0):
        super().__init__(start_time)
        self.note = note


class TimeShiftEvent(MidiEvent):
    def __init__(self, start_time=0, ticks=0, ms=0, current_bpm=0):
        super().__init__(start_time)
        self.ticks = ticks
        self.current_bpm = current_bpm
        temp_ms = ticks2ms(self.ticks, current_bpm)

        # Round Time Shift amount
        # Studies show that people begin to realize audio delay at 15ms so rounding down tempos less than or equal
        # to 10ms should be acceptable and should not affect the music a noticable amount.
        if temp_ms < 10:
            temp_ms = 0
        else:
            temp_ms = round(temp_ms, -1)

        self.ms = temp_ms


class VelocityEvent(MidiEvent):
    def __init__(self, start_time=0, raw_velocity=0):
        super().__init__(start_time)
        self.raw_velocity = raw_velocity
        self.velocity = simplify_velocity(self.raw_velocity, VELOCITY_SPLITS)