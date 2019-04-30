import time
from ctypes import windll, c_buffer
import random


class mci:
    # Windows connection class
    def __init__(self):
        self.w32mci = windll.winmm.mciSendStringA
        self.w32mcierror = windll.winmm.mciGetErrorStringA

    def send(self, command):
        buffer = c_buffer(255)
        errorcode = self.w32mci(str(command).encode('UTF-8'), buffer, 254, 0)
        if errorcode:
            return errorcode, self.get_error(errorcode)
        else:
            return errorcode, buffer.value

    def get_error(self, error):
        print(error)

    def directsend(self, txt):
        (err, buf) = self.send(txt)
        if err != 0:
            print('Error %s for "%s": %s' % (str(err), txt, buf))
        return (err, buf)

class AudioClip(object):
    def __init__(self, filename):
        filename = filename.replace('/', '\\')
        self.filename = filename
        self._alias = 'mp3_%s' % str(random.random())

        self._mci = mci()

        self._mci.directsend(r'open "%s" alias %s' % (filename, self._alias ))
        self._mci.directsend('set %s time format milliseconds' % self._alias)

        err, buf=self._mci.directsend('status %s length' % self._alias)
        self._length_ms = int(buf)

    def milliseconds(self):
        return self._length_ms

    def play(self, start_ms=None, end_ms=None):
        start_ms = 0 if not start_ms else start_ms
        end_ms = self.milliseconds() if not end_ms else end_ms
        err, buf = self._mci.directsend('play %s from %d to %d'
                                        % (self._alias, start_ms, end_ms))

    def pause(self):
        self._mci.directsend('pause %s' % self._alias)

    def unpause(self):
        self._mci.directsend('resume %s' % self._alias)


mysong = AudioClip('song.mp3')
#mysound = AudioClip('sound2.wav')
mysong.play()
print('playing for 5 seconds')
time.sleep(5)
mysong.pause()
print('pausing for 3 seconds')
time.sleep(3)
mysong.unpause()
#mysound.play()
print('upausing and playing for 5 seconds')
time.sleep(5)
mysong.play(100000, 122000)
print('skipping to the 100th second and going to the 122nd second')
time.sleep(100)