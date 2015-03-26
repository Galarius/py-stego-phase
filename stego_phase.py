# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
The method of phase encoding in audio steganography.

stego_phase.py
"""

__author__ = 'Ilya Shoshin'
__copyright__ = 'Copyright 2015, Ilya Shoshin'

#---------------------------------------------------
# to capture console args
import sys
# math functions
from math import *
import cmath
# use numpy
import numpy as np
# wav io wrapper module
import wav_io
# helper methods for stego operations
from stego_helpers import *
# run some tests
from tests import run_tests
#---------------------------------------------------


def hide(source, destination, message):
    """
    :param source:  source stego container filename
    :param destination:    dest stego container filename
    :param message:       message to hide
    :return:        segment_width - segment width
    """
    # read wav file
    (nchannels, sampwidth, framerate, nframes, comptype, compname),\
    (left, right) = wav_io.wav_load(source)
    # select channel to hide message in
    container = left
    container_len = len(container)
    # --------------------------------------
    # prepare container
    # --------------------------------------
    message_len = 8 * len(message)          # msg len in bits
    v = int(ceil(log(message_len, 2)+1))    # get v from equation: 2^v >= 2 * message_len
    segment_width = 2**(v+1)                # + 1 to reduce container distortion after msg integration
    segment_count = int(ceil(container_len / segment_width))    # number of segments to split container in
    # add silence if needed
    if segment_count > container_len / segment_width:
        container = [(container[i] if i < container_len else 0) for i in range(0, segment_count*segment_width)]
    container_len = len(container)          # new container length
    # split signal in 'segment_count' segments with 'segment_width' width
    segments = chunks(container, segment_width)
    # --------------------------------------
    # apply FFT
    # --------------------------------------
    delta = [np.fft.rfft(segments[n]) for n in range(0, segment_count)]  # -> segment_width / 2 + 1
    # extract amplitudes
    vabs = np.vectorize(abs)    # apply vectorization
    amps = [vabs(delta[n]) for n in range(0, segment_count)]
    # extract phases
    varg = np.vectorize(arg)    # apply vectorization
    phases = [varg(delta[n]) for n in range(0, segment_count)]
    # --------------------------------------
    # save phase subtraction
    delta_phases = segment_count*[None]
    delta_phases[0] = 0 * phases[0]
    def sub (a, b): return a - b
    vsub = np.vectorize(sub)
    for n in range(1, segment_count):
        delta_phases[n] = vsub(phases[n], phases[n-1])
    # --------------------------------------
    # integrate msg, modify phase
    msg_vec = str_2_vec(message)
    msg_bits = [d_2_b(msg_vec[t]) for t in range(0, len(message))]
    msg_bits = [item for sub_list in msg_bits for item in sub_list]  # msg is a list of bits now

    segment_width_half = segment_width / 2
    phase_data = (segment_width_half + 1) * [None]  # preallocate list where msg will be stored
    for k in range(0, segment_width_half + 1):
        if k <= len(msg_bits):
            if k == 0 or k == segment_width_half:   # do not modify phases at the ends
                phase_data[k] = phases[0][k]
            if 0 < k < segment_width_half:          # perform integration begining from the hi-freq. components
                if msg_bits[k-1] == 1:
                    phase_data[segment_width_half+1-k] = -pi / 2.0
                elif msg_bits[k-1] == 0:
                    phase_data[segment_width_half+1-k] = pi / 2.0
        if k > len(msg_bits):                       # original phase
            phase_data[segment_width_half+1-k] = phases[0][segment_width_half+1-k]
    phases_modified = [phase_data]
    for n in range(1, segment_count):
        phases_modified.append((phases_modified[n-1] + delta_phases[n]))
    # --------------------------------------
    # convert data back to the frequency domain: amplitude * exp(1j * phase)
    def to_frequency_domain (amp, ph): return amp * cmath.exp(1j * ph)
    vto_fft_result = np.vectorize(to_frequency_domain)
    delta_modified = [vto_fft_result(amps[n], phases_modified[n]) for n in range(0, segment_count)]
    # restore segments
    segments_modified = [np.fft.irfft(delta_modified[n]) for n in range(0, segment_count)]
    # join segments
    container_modified = [item for sub_list in segments_modified for item in sub_list]
    # sync the size of unmodified channel with the size of modified one
    right_synced = len(container_modified) * [None]
    for i in range(0, len(container_modified)):
        if i < len(right):
            right_synced[i] = right[i]
        else:
            right_synced[i] = 0
    # --------------------------------------
    # save stego container with integrated message in freq. scope as wav file
    wav_io.wav_save(destination, (container_modified, right_synced),
                    nchannels, sampwidth, framerate, nframes, comptype, compname)
    # to recover the message the one must know the segment width, used in the process
    return segment_width


def recover(source, segment_width):
    """
    :param source: filename for the file with integrated message
    :param segment_width: segment width
    :return: message
    """
    # read wav file with integrated message
    (nchannels, sampwidth, framerate, nframes, comptype, compname),\
    (left, right) = wav_io.wav_load(source)
    container = left    # take left channel for msg recovering
    container_len = len(container)
    # --------------------------------------
    # prepare container
    segment_count = int(container_len / segment_width)
    # split signal in 'segment_count' segments with 'width' width
    segments = chunks(container, segment_width)
    # --------------------------------------
    # apply FFT
    delta = [np.fft.rfft(segments[0])]
    # extract phases
    varg = np.vectorize(arg)    # apply vectorization
    phases = [varg(delta[0])]
    phases_0_len = len(phases[0])
    b = []
    for t in range(0, segment_width / 2):
        d = phases[0][phases_0_len-1-t]
        if d < -pi/3.0:
            b.append(1)
        elif d > pi/3.0:
            b.append(0)
        else:
            break
    msg_bits_len = int(floor(len(b) / 8.0))
    msg_bits_splitted = chunks(b, 8)
    msg_vec = []
    for i in range(0, msg_bits_len):
        msg_vec.append(b_2_d(msg_bits_splitted[i]))
    return vec_2_str(msg_vec)


def main(argv):

    # run tests
    run_tests()
    # hide
    input_file_name = 'wav/sinus.wav'
    dest_file_name = 'wav/stego.wav'
    message = "Test string string string string string string string string string string string string string string string!"
    segment_width = hide(input_file_name, dest_file_name, message)
    # recover
    message_uncovered = recover(dest_file_name, segment_width)
    print message_uncovered

if __name__ == "__main__":
    main(sys.argv[1:])