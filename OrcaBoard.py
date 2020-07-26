import numpy as np
import simpleaudio as sa
import PySimpleGUI as sg
import pygame



class OrcaBoard():
    def __init__(self):
        self.sample_rate = 44100
        self.nchannels = 2
        self.sampwidth = 2
        self.fade_amount = 8000
        self.fade = np.linspace(1, 0, self.fade_amount)
        self.keys = ['a','s','e','d','r','f','t','g','h','u','j','i','k','l','p']
        self.init_main_window()
        self.mainloop()

    def play_it(self, key):
        sound = self.key_notes.get(key)
        if sound is None:
            return
        play_obj = sa.play_buffer(sound, self.nchannels, self.sampwidth, self.sample_rate)

    def stop_it(self):
        sa.stop_all()

    def do_it(self, place_holder=0):
        def sinewave(f, detune=0.0):
            y = np.sin((f + detune) * x + ramp *
                    np.sin(((f + detune) * 0.5) * x + (
                        np.sin(((f + detune) * fm) * x) * 0.5)))
            return y

        fm = 0.25
        freq5 = float(self.values['-FREQ5-'])
        duration = float(self.values['-DURATION-'])
        freq1 = float(self.values['-FREQ1-'])
        ramp_amount = float(self.values['-RAMP-'])
        roll_amount = int(self.values['-ROLL-'])

        x = np.linspace(0, 2 * np.pi * duration, int(duration * self.sample_rate))
        ramp = np.logspace(1, 0, np.size(x), base=10) * ramp_amount

        notes = []
        for i in range(-5, 10):
            factor = (2**(i / 12.0))
            waveform_mod = sinewave(freq1 * factor)
            waveform = sinewave(freq1 * factor)
            waveform_detune = sinewave(freq1 * factor, freq5)

            waveform = ((waveform + waveform_detune) *
                        (waveform_mod / 2 + 0.5)) * 0.1

            waveform[-self.fade_amount:] *= self.fade
            waveform = np.int16(waveform * 32767)
            waveform2 = np.roll(waveform, roll_amount, axis=None)
            waveform3 = np.vstack((waveform2, waveform)).T
            notes.append(waveform3.copy(order='C'))

        key_notes = dict(zip(self.keys, notes))
        return key_notes

    def init_main_window(self):
        layout = [
            [sg.Text('OrcaBoard', justification='center')],
            [sg.Text('Duration'), sg.Slider((0.2, 5.0), default_value=1.0, resolution=0.2, orientation='h', size=(35, 15), key='-DURATION-')],
            [sg.Text('Detune'), sg.Slider((0.0, 13.0), default_value=5.0, resolution=0.2, orientation='h', size=(35, 15), key='-FREQ5-')],
            [sg.Text('Octave'), sg.Spin(list(np.arange(110, 660, 220)), key='-FREQ1-')],
            [sg.Text('Ramp'), sg.Slider((0.0, 2.0), default_value=0.5, resolution=0.01, orientation='h', size=(35, 15), key='-RAMP-')],
            [sg.Text('Delay'), sg.Slider((0, 4000), default_value=0, resolution=50, orientation='h', size=(35,15), key='-ROLL-')],
            [sg.Button("Stop"), sg.Button("Play")]
        ]

        self.window = sg.Window("OrcaBoard", layout, finalize=True)
        while True:
            event, self.values = self.window.read()

            if event == sg.WIN_CLOSED:
                break

            if event == 'Play':
                self.mainloop()

        self.window.close()
        
    def mainloop(self):
        self.screen = pygame.display.set_mode((240,240))
        self.clock = pygame.time.Clock()
        self.key_notes = self.do_it()

        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    self.play_it(chr(event.key))

            pygame.display.update()
            self.clock.tick(60)

        pygame.display.quit()



if __name__ == '__main__':
    pygame.init()
    OrcaBoard()
