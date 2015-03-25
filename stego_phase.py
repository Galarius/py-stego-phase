__author__ = 'galarius'

import sys
import matplotlib.pyplot as plt
import numpy as np
import wave
import struct
from math import *
import cmath
from itertools import *

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

    return (nchannels, sampwidth, framerate, nframes, comptype, compname, left, right)


def wav_save(fname, samples, nchannels=2, sampwidth=2, framerate=44100, nframes=None, comptype='NONE', compname='not compressed',  bufsize=2048):
    wv = wave.open(fname, 'w')
    wv.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
    if nchannels == 2:
        data = [None]*(len(samples[0])+len(samples[1]))
        data[::2] = samples[0]
        data[1::2] = samples[1]
    else:
        data = samples[0]
    frames = struct.pack("%dh" % len(data), *data)
    wv.writeframesraw(frames)
    wv.close()


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


def arg(z):
    return atan2(z.imag, z.real)


def to_fft_result(amp, ph):
    return amp * cmath.exp(1j * ph)


def str2vec(str):
    return [ord(i) for i in str]


def sign(value):
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0


def d2b(x, bps):
    s = sign(x)
    V = bps * [None]
    for i in range(0, bps):
        V[i] = abs(x) % 2
        x = floor(abs(x)/2)
    return s * V


def b2d(x):
    s = 0
    for i in range(1, len(x)):
        s += x[i]*2**(i-1)


def main(argv):

    inverse = False
    # wave reading
    # --------------------------------------
    if not inverse:
        input_file_name = 'wav/sinus.wav'
        M = "Test string!"
        nchannels, sampwidth, framerate, nframes, comptype, compname, left, right = wav_load(input_file_name)
        C = left, right
        Q = sampwidth * 8
        # plot_signal(left[0:1024], 'Original', 'Time (samples)', 'Amplitude')
        S = C[0]    # take left channel for msg integration
        I = len(S)
        print 'stego direct'
        # stego direct
        # --------------------------------------
        Lm = 8 * len(M)
        v = int(ceil(log(Lm, 2)+1))
        K = 2**(v+1)
        N = int(ceil(I/K))
        # add silense if nessesary
        if N > I/K:
            S = [(S[i] if i < I else 0) for i in range(0, N*K)]
        I = len(S)
        # split signal in N segments with K width
        s = chunks(S, K)
        # FFT
        delta = [np.fft.rfft(s[n]) for n in range(0, N)] # -> K/2 + 1
        # amplitudes
        vabs = np.vectorize(abs)
        amps = [vabs(delta[n]) for n in range(0, N)]
        # phaases
        varg = np.vectorize(arg)
        phases = [varg(delta[n]) for n in range(0, N)]
        # inline test
        #vto_fft_result = np.vectorize(to_fft_result)
        #delta_test = [vto_fft_result(amps[n], phases[n]) for n in range(0, N)]
        # save phase subtraction
        delta_phases = N*[None]
        delta_phases[0] = 0 * phases[0]
        def sub (a, b): return a - b
        vsub = np.vectorize(sub)
        for n in range(1, N):
            delta_phases[n] = vsub(phases[n], phases[n-1])
        # integrate msg, modify phase
        mvec = str2vec(M)
        m = [d2b(mvec[t], Q) for t in range(0, len(M))]
        m = [item for sublist in m for item in sublist]

        phase_data = (K/2+1) * [None]
        for k in range(0, K/2+1):
            if k <= len(m):
                if k == 0 or k == K/2:
                    phase_data[k] = phases[0][k]
                if 0 < k < K/2:
                    if m[k-1] == 1:
                        phase_data[K/2+1-k] = -pi/2
                    elif m[k-1] == 0:
                        phase_data[K/2+1-k] = pi/2
            if k > len(m):
                phase_data[K/2+1-k] = phases[0][K/2+1-k]
        phases_ = len(delta_phases) * [None]
        phases_[0] = phase_data
        for n in range(1, N):
            phases_[n] = (phases_[n-1] + delta_phases[n])
        # restore segments
        vto_fft_result = np.vectorize(to_fft_result)
        delta_ = [vto_fft_result(amps[n], phases_[n]) for n in range(0, N)]
        s_= [np.fft.irfft(delta_[n]) for n in range(0, N)]
        # join segments
        S_ = [item for sublist in s_ for item in sublist]
        C2 = len(S_) * [None]
        for i in range(0, len(S_)):
            if i <= len(right):
                C2[i] = right[i]
            else:
                C2[i] = 0
        wav_save("wav/stego.wav", (S_, C2), nchannels, sampwidth, framerate, nframes, comptype, compname)
    else:
        # recover msg
        pass




if __name__ == "__main__":
    main(sys.argv[1:])