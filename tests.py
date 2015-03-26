__author__ = 'galarius'

from stego_helpers import *


def run_tests():
    test_chunks()
    test_str_to_vec()
    test_d2b()


def test_chunks():
    l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    L = chunks(l, 5)
    assert (len(L[0]) == 5 and len(L[1]) == 5)


def test_str_to_vec():
    str = "Test string!"
    str_check = vec2str(str2vec(str))
    assert (str == str_check)


def test_d2b():
    dec = 7
    dec_check = b2d(d2b(dec, 8))
    assert (dec == dec_check)