from classes import *
import py_midicsv as pm

# Converts ticks to MS based on current BPM and Default pulses per quarter note (PPQ)
def ticks2ms(tick, bpm):
    # PPQ = Listed in header of MIDI (480 by default for Listz dataset)
    ms_per_tick = 60_000 / (bpm * DEFAULT_PPQ)
    return round(tick * ms_per_tick)


# Converts ms back into ticks
def ms2ticks(ms, bpm):
    tick_per_ms = (bpm*DEFAULT_PPQ) / 60_000
    return round(tick_per_ms * ms)


# Ticks Until the next event (should be > 0)
def get_time_shift(events, index, bpm):
    return ticks2ms(events[index + 1].start_time - events[index].start_time, bpm)


# Return a set of all unique time shifts in between events
def get_all_time_shifts(events):
    time_shifts = set()
    current_bpm = 0
    for i in range(len(events) - 1):
        if isinstance(events[i], TempoEvent):
            current_bpm = events[i].bpm
        time_shift = ticks2ms(events[i + 1].start_time - events[i].start_time, current_bpm)
        if time_shift > 0:
            time_shifts.add(round(time_shift, -1))
        elif time_shift < 0:
            pass
    return sorted(time_shifts)


# Writes a str version of each MIDI event object in the passed in list into a text file
def objects2txt(events):
    str_events = ""
    for event in events:
        if isinstance(event, VelocityEvent):
            str_events += f'{event.velocity}.v '
        elif isinstance(event, SustainOnEvent):
            str_events += f'sus.on '
        elif isinstance(event, SustainOffEvent):
            str_events += f'sus.off '
        elif isinstance(event, NoteOnEvent):
            str_events += f'{event.note}.on '
        elif isinstance(event, NoteOffEvent):
            str_events += f'{event.note}.off '
        elif isinstance(event, TimeShiftEvent):
            if event.ms != 0:
                str_events += f'{event.ms}.shift '
            # Ignore TimeShiftEvent if it shifts 0ms
            else:
                pass
    # Remove last space
    str_event = str_events.rstrip()
    with open(rf'./input.txt', "w") as txt:
        txt.write(str_events)


def change_speed(csv_list, change_percentage):
    changed = []
    if change_percentage > 0:
        for event in csv_list:
            if 'Tempo' in event:
                event[2] = str(round(int(event[2])*change_percentage + int(event[2])))
                changed.append(event)
            else:
                changed.append(event)
    return changed


# Convert midi song into 2d string list, convert numerical values from string to int
def midi2list(path):
    str_list = pm.midi_to_csv(path)
    for i in range(len(str_list)):
        str_list[i] = (str_list[i].replace(' ', '').replace('\n', '')).split(',')
        for j in range(len(str_list[i])):
            if str_list[i][j].isdigit():
                str_list[i][j] = int(str_list[i][j])

    return str_list



