import wave
import struct
import numpy as np


def wav_load(file_name):
    """
    Load wav file
    source: http://stackoverflow.com/a/2602334
    :param file_name: file name
    :return: (number of channels,
             bytes per sample,
             sample rate,
             number of samples,
             compression type,
             compression name
             ),
             (left, right)

             Note: if signal is mono than left = right
    """
    wav = wave.open(file_name, "r")
    (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
    frames = wav.readframes(nframes * nchannels)
    out = struct.unpack_from("%dh" % nframes * nchannels, frames)
    wav.close()
    # print("sampling rate = {0} Hz, channels = {1}".format(framerate, nchannels))
    # Convert 2 channels to numpy arrays
    if nchannels == 2:
        left = np.array(list(out[0::2]))
        right = np.array(list(out[1::2]))
    else:
        left = np.array(out)
        right = left

    return (nchannels, sampwidth, framerate, nframes, comptype, compname), (left, right)


def wav_save(file_name, samples, nchannels=2, sampwidth=2, framerate=44100, nframes=None, comptype='NONE', compname='not compressed'):
    """
    Save wav file.
    :param file_name: file name
    :param samples:   samples = (left, right)
    :param nchannels: number of channels
    :param sampwidth: bytes per sample
    :param framerate: sample rate
    :param nframes:   number of frames
    :param comptype:  compression type
    :param compname:  compression name
    """
    wv = wave.open(file_name, 'w')
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
