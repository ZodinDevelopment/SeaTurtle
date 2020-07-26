import os
import numpy as np
import simpleaudio as sa
import pygame
import wave
import PySimpleGUI as sg
basedir = os.path.abspath(os.path.dirname(__file__))


# Should correspond to directory names in the 'samples/' directory
SOUNDS = [
    'claps',
    'closed',
    'cymbals',
    'percs',
    'kicks',
    'open',
    'toms',
    'snares'
]


class SeaTurtle():
    def __init__(self):
        self.init_main_window()
        self.sounds = []
        keysA = [' ','f','v','g','r','w','s','d']
        keysB = ['b','j','n','h','u','i','k','m']
        self.keysA = [ord(key) for key in keysA]
        self.keysB = [ord(key) for key in keysB]
        self.framerate = None
        self.nchannels = None
        self.sampwidth = None

        for s in SOUNDS:
            self.sounds.append(self.load_sample(s))

        self.padA = self.init_sounds(self.keysA)
        self.padB = self.init_sounds(self.keysB)

        self.welcome_window()

    def load_sample(self, sound, sample_path=None):
        """
        Searches for a directory based on the 'sound' paramater within the directory 'samples'. If sample_path keyword is
        not provided, loads the first .wav file listed in the directory.

        :param str sound: Name of the sample directory
        :param str sample_path: Path to a specific .wav file to load the sample from.
        :return: A numpy array of 16-bit unsigned integers representing the audio data.
        """
        samples_dir = os.path.join(basedir, 'samples', sound)
        samples = [fname for fname in os.listdir(samples_dir) if fname.endswith('wav')]

        if sample_path is None:
            sample_path = os.path.join(samples_dir, samples[0])

        try:
            with wave.open(sample_path, 'rb') as wav:
                if self.framerate == None:
                    self.framerate = wav.getframerate()
                if self.nchannels == None:
                    self.nchannels = wav.getnchannels()
                if self.sampwidth == None:
                    self.sampwidth = wav.getsampwidth()

                sample = np.frombuffer(wav.readframes(self.framerate), dtype=np.int16)

            return sample

        except FileNotFoundError:
            sg.popup_error(f'The file at specified at {sample_path} does not exist!')
            return None

        except Exception as e:
            sg.popup_error(f"There was an error reading the audio data from file at path '{sample_path}':", str(e))
            return None

    def init_sounds(self, keyset):
        key_sounds = dict(zip(keyset, self.sounds))
        return key_sounds

    def play_it(self, key):
        if key in self.keysA:
            sound = self.padA[key]
        elif key in self.keysB:
            sound = self.padB[key]
        else:
            sound = np.zeros_like(self.sounds[0], dtype=np.int16)

        play_obj = sa.play_buffer(sound, self.nchannels, self.sampwidth, self.framerate)

    def test_sample(self, pad):
        pad_ind = SOUNDS.index(pad)
        sound = self.sounds[pad_ind]

        play_obj = sa.play_buffer(sound, self.nchannels, self.sampwidth, self.framerate)

    def stop_it(self):
        sa.stop_all()

    def init_main_window(self):
        layout = [
            [sg.Text('SeaTurtleIV',justification='center')],
            [sg.Button('Play'), sg.Button("Configure")],
            [sg.Button('Quit')]
        ]
        self.window = sg.Window("SeaTurtleIV", layout)

    def init_config_window(self):
        self.window.close()
        
        sample_sets = {}
        for s in SOUNDS:
            sample_dir = os.path.join(basedir, 'samples', s)
            sample_sets[s] = [
                os.path.join(sample_dir, fname)
                for fname in os.listdir(sample_dir)
                if fname.endswith('wav')
            ]

        layout = [
            [sg.Text("Kit Configuration", justification="center")],
            [sg.Button("Confirm All")],
        ]

        for pad, samples in sample_sets.items():

            mini_layout = [
                [sg.Text(pad, justification="center")],
                [sg.Spin(samples, enable_events=True, key=pad)],
                [sg.Button('Test', key=f'TEST-{pad}')]
            ]
            for element in mini_layout:
                layout.append(element)

        self.config_window = sg.Window("Kit Configuration", layout)

        while True:
            event, values = self.config_window.read()
            if event == sg.WIN_CLOSED or event == 'Quit':
                break
            if event in sample_sets.keys():
                ind = SOUNDS.index(event)
                self.sounds[ind] = self.load_sample(sound=event, sample_path=values[event])
            if event in [f'TEST-{sound}' for sound in SOUNDS]:
                pad = event.split('-')[-1]
                self.test_sample(pad)
            if event == 'Confirm All':
                self.sounds = []
                for s in SOUNDS:
                    self.sounds.append(self.load_sample(sound=s, sample_path=values[s]))

                break

        self.config_window.close()
        self.padA = self.init_sounds(self.keysA)
        self.padB = self.init_sounds(self.keysB)
        self.init_main_window()
        

    def welcome_window(self):
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED or event == 'Quit':
                break
            if event == "Play":
                self.main_loop()
            if event == "Configure":
                self.init_config_window()
            
        self.window.close()
        self.shut_down()

    def main_loop(self):
        self.window.close()
        running = True
        self.screen = pygame.display.set_mode((240, 180))
        self.clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in self.keysA or event.key in self.keysB:
                        self.play_it(event.key)

                    elif event.key == pygame.K_ESCAPE:
                        running = False

            pygame.display.update()
            self.clock.tick(60)
        pygame.display.quit()
        self.init_main_window()
        self.welcome_window()

    def shut_down(self):
        self.stop_it()
        pygame.quit()
        raise SystemExit()



if __name__ == '__main__':
    pygame.init()
    SeaTurtle()
