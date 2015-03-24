__author__ = 'galarius'

import sys
import wave
import struct
from math import *

def main(argv):

    # wave reading
    # --------------------------------------
    wave_reader = wave.open('3.tahikard120rate.wav', 'rb')
    channels = wave_reader.getnchannels()
    sample_rate = wave_reader.getframerate()
    bps = wave_reader.getsampwidth() * 8

    print """
    wave info
    ---------
    channels: {0}
    sample_rate: {1}
    bps: {2}
    """.format(channels, sample_rate, bps)

    wave_container = []
    length = wave_reader.getnframes()
    if channels == 2:
        for i in range(0, length):
            wave_data = wave_reader.readframes(1)
            wave_container = struct.unpack("<h", wave_data)
    else:
        for i in range(0, length):
            wave_container = wave_reader.readframes(1)
    wave_reader.close()
    print "Done reading."
    c_len = len(wave_container)
    # --------------------------------------
    message = "Test string!"
    msg_len = 8 * len(message)
    v = ceil(log(msg_len, 2)+1)
    k=int(2**(v+1))
    n=ceil(c_len/k)
    S = []
    if n > c_len/k:
        for i in range(0, n*k):
            S[i] = wave_container[i] if i < c_len else 0

    s = [S[i:i+k] for i in range(0, len(S), k)]
    print s

if __name__ == "__main__":
    main(sys.argv[1:])