from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Activation
from keras.layers import BatchNormalization as BatchNorm
from keras.utils import np_utils
import numpy
import os


def testing(composer, song_name, save_path, output_size, save, progress_bar):
    progress = 0
    progress_bar.update_idletasks()

    with open('./data/{composer}/input.txt', 'r') as text:
        events = text.read().split(' ')
        text.close()
    # Define the length of each sequence of input data
    seq_length = 12
    # Get number of unique events in the data
    n_vocab = len(set(events))
    print(f'{n_vocab} unique events')
    # get all pitch names
    event_names = sorted(set(event for event in events))

    # create a dictionary to map pitches to integers
    event_to_int = dict((event, number) for number, event in enumerate(event_names))

    network_input = []
    network_output = []

    # create input sequences and their labels
    for i in range(0, len(events) - seq_length, 1):
        seq_in = events[i:i + seq_length]
        seq_out = events[i + seq_length]
        network_input.append([event_to_int[char] for char in seq_in])
        network_output.append(event_to_int[seq_out])

    n_patterns = len(network_input)

    # reshape the input into a format compatible with LSTM layers
    network_input = numpy.reshape(network_input, (n_patterns, seq_length, 1))
    # normalize input
    network_input = network_input / float(n_vocab)

    network_output = np_utils.to_categorical(network_output)

    # Define Neural Network Architecture -------------------------------------------
    model = Sequential()
    model.add(LSTM(
        512,
        input_shape=(network_input.shape[1], network_input.shape[2]),
        return_sequences=True
    ))
    model.add(Dropout(0.3))
    model.add(LSTM(512, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(512))
    model.add(BatchNorm())
    model.add(Dropout(0.3))
    model.add(Dense(256))
    model.add(Activation('relu'))
    model.add(BatchNorm())
    model.add(Dropout(0.3))
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    model.load_weights('./data/{composer}/weights.txt')

    # pick a random sequence from the input as a starting point for the prediction
    start = numpy.random.randint(0, len(network_input)-1)

    int_to_event = dict((number, event) for number, event in enumerate(event_names))

    pattern = list(network_input[start])
    prediction_output = []

    # generate events
    for note_index in range(output_size):
        progress_bar['value'] = progress
        progress_bar.update_idletasks()
        prediction_input = numpy.reshape(pattern, (1, len(pattern), 1))
        prediction_input = prediction_input / float(n_vocab)
        prediction_input = numpy.asarray(prediction_input).astype(numpy.float32)
        prediction = model.predict(prediction_input, verbose=0)
        index = numpy.argmax(prediction)
        result = int_to_event[index]
        prediction_output.append(result)
        print(result, end=' ')
        pattern.append(index)
        pattern = pattern[1:len(pattern)]
        progress += 1

    with open('./outputs/{song_name}.txt', "w") as txt:
        for event in prediction_output:
            print(event, end=' ')
            txt.write(f'{event} ')

    progress = 0
    progress_bar.update_idletasks()


def gui_init():
    def generate():
        if song_name_input.get():
            try:
                song_name = song_name_input.get().isalnum()
                if song_length_input.get():
                    try:
                        song_length = int(song_length_input.get())
                        try:
                            messagebox.showinfo("Alert", "Specify Save Location.")
                            save_path = filedialog.askdirectory()
                            # Define progress bar
                            progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=100, mode='determinate')
                            progress_bar.grid(row=4, column=1, pady=5)
                            testing(clicked.get(), song_name, song_length, save_path, progress_bar)
                            messagebox.showinfo("Alert", "Song Saved")
                            progress_bar.grid_forget()
                        except ValueError:
                            messagebox.showerror("Error", "Failed to generate song.")
                    except ValueError:
                        messagebox.showerror("Error", "Song length must be an integer.")
                else:
                    messagebox.showerror("Error", "Specify song length.")
            except ValueError:
                messagebox.showerror("Error", "Song title is invalid. Must be alpha numeric.")
        else:
            messagebox.showerror("Error", "Specify song title.")

    root = Tk()
    root.resizable(width=False, height=False)
    root.title("MIDI Generator")
    root.resizable(height=False, width=False)

    # Song Style Select ------------------------------------------------------
    style_list = [style for style in os.listdir("./data")]
    clicked = StringVar()
    # Set default style
    clicked.set(style_list[0])
    # Get all styles (all folders in ./data)
    song_style_label = Label(text="Song Style:")
    song_style_label.grid(row=1, column=0, sticky='w', padx=10)
    song_style_menu = OptionMenu(root, clicked, *style_list)
    song_style_menu.grid(row=1, column=1, sticky='w', padx=10, pady=5)
    # Song Title Entry --------------------------------------------------------
    song_name_label = Label(text="Song Title:")
    song_name_label.grid(row=2, column=0, sticky='w', padx=10)
    song_name_input = Entry(root, width=30, bd=3)
    song_name_input.grid(row=2, column=1, sticky='w', padx=10, pady=5)
    # Song Length Entry -------------------------------------------------------
    song_length_label = Label(text="Song Length:")
    song_length_label.grid(row=3, column=0, sticky='w', padx=10)
    song_length_input = Entry(root, width=30, bd=3)
    song_length_input.grid(row=3, column=1, sticky='w', padx=10)
    # Generate Button ---------------------------------------------------------
    gen_song_button = Button(root, text="Generate", width=10, height=1, command=generate)
    gen_song_button.grid(row=4, column=1, pady=10)
    root.mainloop()


gui_init()
