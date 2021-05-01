from sub_functions import *


class MIDIDataset:
    def __init__(self, midi_songs):
        self.midi_songs = midi_songs

    # Data augmentation
    def augment(self):
        pass

    # Display bar graph of note usage
    def analyze_notes(self):
        pass


class MIDISong:
    def __init__(self, path):
        self.path = path
        # Defined in get_attr()
        self.ppq = None
        self.title = None
        self.midi_type = None
        self.key_sig = []
        self.time_sig = []
        self.events = []
        self.midi_list = midi2list(self.path)

        # Get the class attributes from midi_list
        self.get_attr()
        # Get list of events from midi_list
        self.get_events()
    # Transpose song by some numerical value (-11 to 11)
    def transpose(self, transpose_value):
        if transpose_value > 11 or transpose_value < -11:
            pass
        else:
            for event in self.events:
                if 'Note_on_c' in event or 'Note_off_c' in event:
                    event[2] = str(int(event[2]) + transpose_value)

    # Get MIDI song attributes from the midi list
    # If you are confused about the format of the midi list
    # refer to this: https://www.fourmilab.ch/webtools/midicsv/
    def get_attr(self):
        for line in self.midi_list:
            if 'Header' in line:
                self.ppq = line[5]
                self.midi_type = line[3]
            elif 'Title_t' in line and not self.title:
                self.title = line[3]
            elif 'Time_signature' in line:
                self.time_sig = [line[3], line[4]]
            elif 'Key_signature' in line:
                self.key_sig = [line[3], line[4]]

    # todo extract events from midi_list and objectify them
    def get_events(self):
        self.events = []
        for line in self.midi_list:
            if list2obj(line):
                self.events.append(list2obj(line))




class MIDIEvent:
    def __init__(self, track_num, start_time):
        self.track_num = track_num
        self.start_time = start_time


class TempoEvent(MIDIEvent):
    def __init__(self, track_num, start_time, tempo):
        super().__init__(track_num, start_time)
        self.tempo = tempo
        # Round BPM to nearest 10th
        self.bpm = round(round(60_000_000 / tempo), -1)


class SustainOnEvent(MIDIEvent):
    def __init__(self, track_num, start_time=0, tempo=0):
        super().__init__(track_num, start_time)


class SustainOffEvent(MIDIEvent):
    def __init__(self, track_num, start_time=0, tempo=0):
        super().__init__(track_num, start_time)


class NoteOnEvent(MIDIEvent):
    def __init__(self, track_num, start_time=0, note=0):
        super().__init__(track_num, start_time)
        self.note = note


class NoteOffEvent(MIDIEvent):
    def __init__(self, track_num, start_time=0, note=0):
        super().__init__(track_num, start_time)
        self.note = note


class TimeShiftEvent(MIDIEvent):
    def __init__(self, track_num, start_time=0, ticks=0, ms=0, current_bpm=0):
        super().__init__(track_num, start_time)
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


class VelocityEvent(MIDIEvent):
    def __init__(self, track_num, start_time, raw_velocity=0):
        super().__init__(track_num, start_time)
        self.raw_velocity = raw_velocity
        self.velocity = simplify_velocity(self.raw_velocity, VELOCITY_SPLITS)

# todo AAA
def list2obj(str_list):
    if 'Tempo' in str_list:
        return TempoEvent(track_num=int(str_list[0]), start_time=int(str_list[1]), tempo=int(str_list[3]))
    elif 'Control_c' in str_list and str_list[4] == '64':
        if str_list[5] == 0:
            return SustainOffEvent(track_num=str_list[0], start_time=str_list[1])
        else:
            return SustainOffEvent(track_num=str_list[0], start_time=str_list[1])
    elif 'Note_on_c' in str_list:
        if str_list[5] == 0:
            return NoteOffEvent(track_num=str_list[0], start_time=str_list[1])
    else:
        return None

test_song = MIDISong('./data/DEB_CLAI.MID')
print(test_song.midi_list)
print(test_song.ppq)
