__author__ = 'galarius'

import sys
import matplotlib.pyplot as plt
import numpy as np
import wave
import struct
from math import *

# http://stackoverflow.com/a/2602334
def wav_load(fname):
    wav = wave.open(fname, "r")
    (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
    frames = wav.readframes(nframes * nchannels)
    out = struct.unpack_from("%dh" % nframes * nchannels, frames)
    wav.close()
    print("sampling rate = {0} Hz, channels = {1}".format(framerate, nchannels))
    # Convert 2 channles to numpy arrays
    if nchannels == 2:
        left = np.array(list(out[0::2]))
        right = np.array(list(out[1::2]))
    else:
        left = np.array(out)
        right = left

    return (nchannels, left, right)

def plot_signal(audion_data, title, x_lbl, y_lbl):
    # plot the first 1024 samples
    plt.plot(audion_data)
    # label the axes
    plt.ylabel(y_lbl)
    plt.xlabel(x_lbl)
    # set the title
    plt.title(title)
    # display the plot
    plt.show()

# http://stackoverflow.com/a/1751478
def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

def main(argv):

    input_file_name = 'wav/sinus.wav'
    M = "Test string!"
    inverse = False
    # wave reading
    # --------------------------------------
    nchannels, left, right = wav_load(input_file_name)
    C = left, right
    # plot_signal(left[0:1024], 'Original', 'Time (samples)', 'Amplitude')
    S = C[0]    # take left channel for msg integration
    I = len(S)
    if not inverse:
        print 'stego direct'
        # stego direct
        # --------------------------------------
        Lm = 8 * len(M)
        v = int(ceil(log(Lm, 2)+1))
        K=2**(v+1)
        N=ceil(I/K)
        # add silense if nessesary
        if N > I/K:
            S = [(S[i] if i < I else 0) for i in range(0, N*K)]
        I = len(S)
        # split signal in N segments with K width
        s = chunks(S, K)
        

if __name__ == "__main__":
    main(sys.argv[1:])