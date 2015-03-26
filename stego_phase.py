
__author__ = 'galarius'

# to capture console args
import sys
# math functions
from math import *
# use numpy
import numpy as np
# wav io wrapper module
import wav_io
# helper methods for stego operations
from stego_helpers import *

from tests import run_tests


def integrate(source, dest, M):
    """
    :param source:  source stego container filename
    :param dest:    dest stego container filename
    :param M:       message to hide
    :return:        K - segment width
    """
    (nchannels, sampwidth, framerate, nframes, comptype, compname), (left, right) = wav_io.wav_load(source)
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
    # phases
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
    m = [d2b(mvec[t], 8) for t in range(0, len(M))]
    m = [item for sublist in m for item in sublist]

    phase_data = (K/2+1) * [None]
    for k in range(0, K/2+1):
        if k <= len(m):
            if k == 0 or k == K/2:
                phase_data[k] = phases[0][k]
            if 0 < k < K/2:
                if m[k-1] == 1:
                    phase_data[K/2+1-k] = -pi/2.0
                elif m[k-1] == 0:
                    phase_data[K/2+1-k] = pi/2.0
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
    wav_io.wav_save(dest, (S_, C2), nchannels, sampwidth, framerate, nframes, comptype, compname)
    return K


def deintegrate(source, K):
    """
    :param source: filename for the file with integrated message
    :param K:      K - segment width
    :return:       message
    """
    (nchannels, sampwidth, framerate, nframes, comptype, compname), (left, right) = wav_io.wav_load(source)
    C = left, right
    Q = sampwidth * 8
    S = C[0]    # take left channel for msg recovering
    I = len(S)
    N = int(I/K)
    # split signal in N segments with K width
    s = chunks(S, K)
    # FFT
    delta = [None] * N
    delta[0] = np.fft.rfft(s[0])
    phases = [None] * N
    varg = np.vectorize(arg)
    phases[0] = varg(delta[0])
    b = []
    for t in range(0, K/2):
        d = phases[0][len(phases[0])-1-t]
        if d < -pi/3.0:
            b.append(1)
        elif d > pi/3.0:
            b.append(0)
        else:
            break
    Lm = int(floor(len(b)/8.0))
    B = chunks(b, 8)
    M = []
    for i in range(0, Lm):
        M.append(b2d(B[i]))
    return vec2str(M)


def main(argv):

    run_tests()

    # integrate
    input_file_name = 'wav/sinus.wav'
    dest_file_name = 'wav/stego.wav'
    message = "Test string string string string string string string string string string string string string string string!"
    K = integrate(input_file_name, dest_file_name, message)
    # recover
    message_uncovered = deintegrate(dest_file_name, K)
    print message_uncovered

if __name__ == "__main__":
    main(sys.argv[1:])