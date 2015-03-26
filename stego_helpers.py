__author__ = 'galarius'

import cmath
from math import atan2, floor
from numpy import sign


def chunks(l, n):
    """
    Split list into chunks.
    source: http://stackoverflow.com/a/1751478

    :param l: list to split
    :param n: chunk size
    :return: [[],[],[],...]
    """
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]


def arg(z):
    """
    Argument of a complex number
    :param z: complex number
    :return:  arg(z)
    """
    return atan2(z.imag, z.real)


def to_fft_result(amp, ph):
    """
    amplitude * exp(1j * phase) - this is the result of FFT, which may be restored with
    amp and phase values.
    :param amp: amplitude
    :param ph:  phase
    :return: amplitude * exp(1j * phase)
    """
    return amp * cmath.exp(1j * ph)


def vec2str(vec):
    """
    Convert vector of integers to string.
    :param vec: [int, int, ...]
    :return: string
    """
    char_vec = [str(unichr(i)) for i in vec]
    return ''.join(char_vec)


def str2vec(str):
    """
    Convert vector of integers to string.
    :param str: string
    :return:    [int, int, int, ...]
    """
    return [ord(i) for i in str]


def d2b(x, size):
    """
    Convert decimal to byte list
    :param x:    decimal
    :param size: the size of byte list
    :return: e.g. [0, 0, 1, ...]
    """
    s = sign(x)
    v = size * [None]
    for i in range(0, size):
        v[i] = abs(x) % 2
        x = floor(abs(x)/2)
    return s * v


def b2d(x):
    """
    Convert byte list to decimal
    :param x:   byte list
    :return:    decimal
    """
    s = 0
    for i in range(1, len(x)):
        s += x[i]*2**(i-1)
    return s
