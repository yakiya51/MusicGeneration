import matplotlib.pyplot as plt


# Count up each note in txt format midi file
def get_notes_count(input_path):
    with open(input_path, 'r') as file:
        event_list = file.read().split(' ')
        all_notes_count = {}
        octave_notes_count = {}

        for event in event_list:
            if '.on' in event and 'sus' not in event:
                note = int(event[:event.find('.')])
                # Add to all notes count
                if note in all_notes_count:
                    all_notes_count[note] += 1
                else:
                    all_notes_count[note] = 1

                # Calculate the note w/o octave number
                octave_note = note % 12
                # Add to octave notes count
                if octave_note in octave_notes_count:
                    octave_notes_count[octave_note] += 1
                else:
                    octave_notes_count[octave_note] = 1

    return all_notes_count, octave_notes_count


notes_count, octave_count = get_notes_count('./input.txt')
notes_all, count_all = list(notes_count.keys()), list(notes_count.values())
count_oct = list(octave_count.values())
notes_oct = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Configure Subplots
fig = plt.figure(figsize=[13, 4])
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

# All Octaves
ax1.set_ylabel('Count')
ax1.set_xlabel('MIDI Note')
ax1.bar(notes_all, count_all)

# Single Octave
ax2.set_ylabel('Count')
ax2.set_xlabel('Note')
ax2.bar(notes_oct, count_oct)
plt.subplots_adjust()
plt.show()
