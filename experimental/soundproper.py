from ctypes import windll, c_buffer
from random import random
from time import time, sleep


class Sound:  # maybe change this name to Audio or something later
    def __init__(self, filename):
        """
        Class to manage the use of sound
        :param filename: the name of the file to import
        :type filename: string
        """

        self.file = filename
        self._alias = f'pksound_{random()}'
        self._run_command(f'play "thing.wav"')
        length = int(self._run_command(f'status thing.wav length')) / 1000
        print(length)
        # self._run_command(f'open {self.file} alias {self._alias}')
        # self._run_command(f'set {self._alias} time format milliseconds')
        # self.info = self._run_command(f'info {self._alias} version')
        # print(self.info)
        # self.length = self._run_command(f'status {self._alias} length')
        # print(self.length)


    def test(self):
        self._run_command(f'play {self._alias} from 0 to 22913')


    def _run_command(self, command):
        buffer = c_buffer(255)
        error = windll.winmm.mciSendStringA(command.encode('UTF-8'), buffer, 254, 0)
        if error:
            buffer = c_buffer(255)
            windll.winmm.mciGetErrorStringA(error, buffer, 254)
            raise Exception(buffer.value.decode())

        return buffer.value.decode()


my_sound = Sound('song.mp3')
sleep(10)
#print(my_sound.length)

# start = time()
# my_sound.test()
# sleep(10)
# print(time() - start)