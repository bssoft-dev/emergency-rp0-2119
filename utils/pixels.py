"""
LED light pattern like Google Home
Origianl URL https://github.com/respeaker/mic_hat/blob/master/interfaces/pixels.py
"""

# from utils import apa102
import apa102
import time
import sys
import threading
try:
    import queue as Queue
except ImportError:
    import Queue as Queue


class Pixels:
    PIXELS_N = 3

    def __init__(self):
        # self.basis is list of 9 ints i.e. [r, g, b, r, g, b, r, g, b]
        self.basis = [0] * 3 * self.PIXELS_N
        # basic brightness
        self.basis[0] = 10
        self.basis[3] = 5
        self.basis[4] = 5
        self.basis[7] = 10

        self.colors = [0] * 3 * self.PIXELS_N
        self.dev = apa102.APA102(num_led=self.PIXELS_N)

        self.next = threading.Event()
        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def wakeup(self, direction=0):
        def f():
            self._wakeup(direction)

        self.next.set()
        self.queue.put(f)

    def listen(self):
        self.next.set()
        self.queue.put(self._listen)

    def think(self):
        self.next.set()
        self.queue.put(self._think)

    def speak(self):
        self.next.set()
        self.queue.put(self._speak)

    def off(self):
        self.next.set()
        self.queue.put(self._off)

    def _run(self):
        while True:
            func = self.queue.get()
            func()

    def _wakeup(self, direction=0):
        for i in range(1, 25):
            colors = [i * v for v in self.basis]
            self.write(colors)
            time.sleep(0.01)

        self.colors = colors

    def _listen(self):
        for i in range(1, 25):
            colors = [i * v for v in self.basis]
            self.write(colors)
            time.sleep(0.01)

        self.colors = colors

    def _think(self):
        colors = self.colors

        self.next.clear()
        while not self.next.is_set():
            colors = colors[3:] + colors[:3]
            self.write(colors)
            time.sleep(0.2)

        t = 0.1
        for i in range(0, 5):
            colors = colors[3:] + colors[:3]
            self.write([(v * (4 - i) / 4) for v in colors])
            time.sleep(t)
            t /= 2

        # time.sleep(0.5)

        self.colors = colors

    def _speak(self):
        colors = self.colors
        gradient = -1
        position = 24

        self.next.clear()
        while not self.next.is_set():
            position += gradient
            self.write([(v * position / 24) for v in colors])

            if position == 24 or position == 4:
                gradient = -gradient
                time.sleep(0.2)
            else:
                time.sleep(0.01)

        while position > 0:
            position -= 1
            self.write([(v * position / 24) for v in colors])
            time.sleep(0.01)

        # self._off()

    def _off(self):
        self.write([0] * 3 * self.PIXELS_N)

    def write(self, colors):
        for i in range(self.PIXELS_N):
            self.dev.set_pixel(i, int(colors[3*i]), int(colors[3*i + 1]), int(colors[3*i + 2]))

        self.dev.show()

    def stay(self):
        self.write([0, 0, 500, 0, 0, 500, 0, 0, 500])

    def warn(self):
        self.write([500, 0, 0, 500, 0, 0, 500, 0, 500])

def welcome_light():
    pixels = Pixels()
    pixels.wakeup()
    time.sleep(3)
    pixels.think()
    time.sleep(3)
    pixels.speak()
    time.sleep(3)
    #pixels.off()
    #time.sleep(3)
    pixels.off()
    time.sleep(1)
    pixels.stay()

def alarm_light():
    pixels = Pixels()
    pixels.wakeup()
    time.sleep(1)
    pixels.speak()
    time.sleep(10)
    # pixels.off()
    # time.sleep(3)
    # pixels.off()
    # time.sleep(1)
    pixels.stay()

def turn_red():
    pixels = Pixels()
    pixels.warn()

def turn_blue():
    pixels = Pixels()
    pixels.stay()

if __name__ == '__main__':
    if sys.argv[1] == 'welcome_light':
        welcome_light()
    elif sys.argv[1] == 'alarm_light':
        alarm_light()
    elif sys.argv[1] == 'alarm_lock_light':
        alarm_lock_light()
    elif sys.argv[1] == 'turn_red':
        turn_red()
    elif sys.argv[1] == 'turn_blue':
        turn_blue()
