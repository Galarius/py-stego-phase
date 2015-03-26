__author__ = 'galarius'

import matplotlib.pyplot as plt


def plot_signal(audio_data, title, x_lbl, y_lbl):
    """
    Simple signal plotting.
    May take a long time to build massive data.
    :param audio_data:  data to build
    :param title:       chart title
    :param x_lbl:       x axis label
    :param y_lbl:       y axis label
    """
    plt.plot(audio_data)
    # label the axes
    plt.ylabel(y_lbl)
    plt.xlabel(x_lbl)
    # set the title
    plt.title(title)
    # display the plot
    plt.show()