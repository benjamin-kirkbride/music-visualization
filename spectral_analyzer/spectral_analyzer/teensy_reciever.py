from io import TextIOWrapper
from pathlib import Path

import numpy as np
import numpy.typing

max_bin_energies = None


def _get_bins_as_percentage_of_max(bins):
    # we intentionally don't distinguish between channels for the max
    global max_bin_energies

    # init on first run
    if max_bin_energies is None:
        max_bin_energies = np.array([float(0) for i in range(len(bins))])
    # TODO: something with this
    new_max_bin_energies = np.maximum(bins, max_bin_energies)
    max_bin_energies = new_max_bin_energies

    np.divide(bins, max_bin_energies, out=bins)
    bins = np.nan_to_num(bins)

    return bins


def _process_bins(raw_bins: numpy.typing.ArrayLike):

    bins = np.multiply(raw_bins, 100_000)

    # chop off noise
    # TODO: make this unnessesary
    bins = np.subtract(bins, 1)
    bins = np.maximum(bins, 0)

    # make logarithmic
    # TODO: see if this does anything worthwhile
    bins = np.power(np.array(bins), 0.8)

    bins = _get_bins_as_percentage_of_max(bins)

    return bins


def get_bins(
    port: TextIOWrapper,
):
    raw_bin_string = next(port)
    # TODO: something with the ID (log if channel is missed?)
    channel, id, raw_bins_string = raw_bin_string.split(":")

    # strip off the last character (newline) and split on the commas
    raw_bins_string = raw_bins_string[:-1]

    raw_bins = np.fromstring(raw_bins_string, dtype=float, sep=",")

    bins = _process_bins(raw_bins)

    return channel, bins
