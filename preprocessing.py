import py_midicsv as pm
import os
from classes import *
from sub_functions import *
import random

TRANSPOSE_COUNT = 1


# Convert from a list of strings to a list of MIDI event objects
def str2objects(events):
    current_bpm = 0
    obj_list = []
    # Objectify each event for easier access later on
    for i in range(len(events)):
        # If tempo event, keep track of current bpm to calculate time shift
        if 'Tempo' in events[i]:
            tempo_event = TempoEvent(start_time=int(events[i][0]), tempo=int(events[i][2]))
            obj_list.append(tempo_event)
            current_bpm = tempo_event.bpm

        # Sustain On Event
        if 'Control_c' in events[i] and events[i][3] != '0':
            obj_list.append(SustainOnEvent(start_time=int(events[i][0])))

        # Sustain Off Event
        elif 'Control_c' in events[i] and events[i][3] == '0':
            obj_list.append(SustainOffEvent(start_time=int(events[i][0])))

        # Note on Event - Add velocity event as well
        elif 'Note_on_c' in events[i] and events[i][3] != '0':
            obj_list.append(VelocityEvent(raw_velocity=int(events[i][3])))
            obj_list.append(NoteOnEvent(start_time=int(events[i][0]), note=int(events[i][2])))

        # Note off Event
        elif ('Note_on_c' in events[i] and events[i][3] == '0') or 'Note_off_c' in events[i]:
            obj_list.append(NoteOffEvent(start_time=int(events[i][0]), note=int(events[i][2])))

        # Try looking at the next event's start time to calculate a time shift if needed
        try:
            # If the next event is within the same tick, pass and loop again
            if int(events[i][0]) == int(events[i+1][0]):
                pass
            # Time Shift Event
            elif int(events[i][0]) < int(events[i+1][0]):
                gap = int(events[i+1][0]) - int(events[i][0])
                obj_list.append(TimeShiftEvent(ticks=gap, current_bpm=current_bpm))
            # New Track Start - Distinguished by a very large gap of 10000ms or 10s
            elif int(events[i][0]) > int(events[i+1][0]):
                obj_list.append(TimeShiftEvent(ticks=10000, current_bpm=125))

        # If index error, then the end of file has been reached so break out of loop
        except IndexError:
            break

    del events
    return obj_list


# Convert from a csv to a 2d list of strings (each row is a MIDI event)
def csv2str(csv_list):
    # List to append all relevant events to
    events = []
    for row in csv_list:
        # Only append rows with relevant events
        if (row[2] == 'Tempo') or (row[2] == 'Control_c' and row[4] == '64') or \
                (row[2] == 'Note_on_c' or row[2] == 'Note_off_c'):
            events.append(row)

    # Sort events based on their start time (MIDI ticks)
    events.sort(key=lambda x: int(x[1]))

    # Remove repeating tempo events
    for i in range(len(events)):
        try:
            if events[i][2] == 'Tempo' and events[i + 1][2] == 'Tempo':
                events.pop(i)
        except IndexError:
            break

    # Remove track column
    for event in events:
        del event[0]
        # For events other than the tempo event, remove the channel column as well
        if 'Note_on_c' in event or 'Control_c' in event:
            del event[2]

    # APPEND new events list into the text file. WRITING would override the text file.
    with open(rf'C:\Users\Yuta\Documents\PythonProjects\MusicGenerationV3\data\events.txt', "a") as txt:
        for event in events:
            for element in event:
                txt.write(str(element) + ' ')
            txt.write('\n')
    return events


# Convert from midi file to a text file of event strings
def midi2txt(path):
    events_list = []
    # Go through each MIDI file within the path
    for file_name in os.listdir(path):
        if file_name.endswith('.mid'):
            # Parse MIDI into a list where each element is a row in the CSV
            csv_list = pm.midi_to_csv(path + "/" + file_name)

            # Uncomment to save the csv file for each MIDI:
            #with open(rf'C:\Users\Yuta\Documents\PythonProjects\MusicGenerationV3\data\{file_name}.txt', "w") as txt:
                #txt.writelines(csv_list)

            # Put each row of the csv into a list
            for i in range(len(csv_list)):
                csv_list[i] = csv_list[i].split(",")
                # Remove Spaces and \n's in each row element
                for j in range(len(csv_list[i])):
                    csv_list[i][j] = csv_list[i][j].replace(
                        ' ', '').replace('\n', '')

            str_list = csv2str(csv_list)
            if TRANSPOSE_COUNT > 0:
                rand_transpose_values = set()
                while len(rand_transpose_values) < TRANSPOSE_COUNT:
                    random_num = random.randrange(0, 12)
                    rand_transpose_values.add(random_num)

                # Transpose the original song and a transposed version of the song to events list
                events_list.extend(str_list)
                for number in rand_transpose_values:
                    events_list.extend(transpose(str_list, number))
                    print(len(events_list))
            else:
                events_list.extend(str_list)

    # At this point, events_list is a 2d list containing all MIDI events in the dataset.
    # Time unit is still in ticks

    # Events_list is converted to a list of MidiEvent Objects
    events_obj_list = str2objects(events_list)

    # Object list is converted to text 
    objects2txt(events_obj_list)


# Convert a text file of event strings into a MIDI file with one track
def txt2midi(path):
    track_num = 1
    current_time = current_bpm = 0
    current_velocity = 6
    BPM = 120

    # Open input text file and split it into a list of strings
    with open(path, 'r') as txt:
        str_list = txt.read().split(' ')

    # Open up the output csv file and write in MIDI events in CSV format
    with open(f'output.csv', 'w') as csv:
        csv.write(f'0, 0, Header, 0, {track_num}, {DEFAULT_PPQ}\n')
        csv.write('1, 0, Start_track\n')
        csv.write(f'1, 0, Title_t, Everything\n')
        csv.write('1, 0, Copyright_t, "public domain"\n')
        csv.write('1, 0, Time_signature, 4, 4, 24, 8\n')
        # Use 120 BPM
        csv.write(f'1, 0, Tempo, {round(60_000_000/BPM)}\n')

        for str_event in str_list:
            # Velocity Event
            if '.v' in str_event:
                current_velocity = unsimplify_velocity(int(str_event[:str_event.find('.')]), VELOCITY_SPLITS)
            # Sustain On Event
            elif str_event == 'sus.on':
                csv.write(f'{track_num}, {current_time}, Control_c, 0, 64, 127\n')
            # Sustain Off Event
            elif str_event == 'sus.off':
                csv.write(f'{track_num}, {current_time}, Control_c, 0, 64, 0\n')

            # Time Shift Event
            elif '.shift' in str_event:
                current_time += ms2ticks(int(str_event[:str_event.find('.')]), BPM)
            else:
                # Note On
                if '.on' in str_event:
                    note = str_event[:str_event.find('.')]
                    csv.write(f'{track_num}, {current_time}, Note_on_c, 0, {note}, {current_velocity}\n')
                # Note Off
                elif '.off' in str_event:
                    note = str_event[:str_event.find('.')]
                    csv.write(f'{track_num}, {current_time}, Note_off_c, 0, {note}, 0\n')
                else:
                    pass

        csv.write(f'{track_num}, {current_time}, End_track\n')
        csv.write(f'0, 0, End_of_file')

    output = pm.csv_to_midi(f"output.csv")
    # Save the parsed MIDI file
    with open(f"output.mid", "wb") as output_file:
        midi_writer = pm.FileWriter(output_file)
        midi_writer.write(output)


def unique_events(path):
    with open(path, 'r') as text:
        events = text.read().split(' ')
        text.close()
    print(set(events))
    print(f'{len(sorted(set(events)))} unique events')


#midi2txt('./data')
#txt2midi('./input.txt')
unique_events('./input.txt')

