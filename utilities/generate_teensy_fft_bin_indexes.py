from typing import List, Sequence, Tuple

import numpy as np


def erb_from_freq(freq: int) -> float:
    """Get equivalent rectangular bandwidth from the given frequency.

    See: https://en.wikipedia.org/wiki/Equivalent_rectangular_bandwidth

    Args:
        freq: input frequency

    Returns:
        int: cam
    """

    return float(9.265 * np.log(1 + np.divide(freq, 24.7 * 9.16)))


def generate_bin_edges(low_freq: int, high_freq: int, count: int) -> List[int]:
    """Bin sizes designed around Equivalent Rectangular Bandwidth

    NOTE: this becomes less accurate as the bin values increase,
        but should be good enough (TM)

    Args:
        low_freq: where to start the bins (> 0)
        high_freq: where to end the bins (<= 20,000)
        count: number of bin edges to generate

    Returns:
        List[int]: bin seperators in Hz
    """

    bin_edges = []
    cams = np.linspace(
        erb_from_freq(low_freq), erb_from_freq(high_freq), count
    )
    for i, cam in enumerate(cams):
        if not i:
            # this is probably not nessesary, but better safe than sorry?
            bin_edges.append(low_freq)
        elif i == len(cams) - 1:
            bin_edges.append(high_freq)
        else:
            bin_edges.append(round(10 ** (cam / 21.4) / 0.00437 - 1 / 0.00437))

    return bin_edges


def generate_bins_from_edges(edges: List[int]) -> List[Tuple[int, int]]:
    bins = []
    previous_edge = edges[0]
    for edge in edges[1:]:
        bins.append((previous_edge, edge))
        previous_edge = edge
    return bins


def generate_edges_from_bin_centers(bin_centers: Sequence[int]) -> List[int]:
    # we assume for the first and last bin is symetrical
    # (we actually assume they all are)
    # obviously no edge can be negative
    edges: List[int] = []

    previous_center = None
    for center in bin_centers:
        if previous_center is None:
            previous_center = center
            continue

        edge = previous_center + (center - previous_center) / 2
        # print(f"edge between {previous_center} and {center}: {edge}")
        if not edges:
            first_edge = previous_center - edge
            if first_edge < 0:
                first_edge = 0
            edges.append(first_edge)

        edges.append(edge)
        previous_center = center
    else:
        assert previous_center is not None
        # assume previous center truly is center
        final_edge = (previous_center - edges[-1]) + previous_center
        edges.append(final_edge)

    return edges


def main():
    ideal_bin_edges = generate_bin_edges(40, 16000, 25)
    teensy_fft1024_bin_centers = tuple(i * 43 for i in range(512))
    ideal_bins = generate_bins_from_edges(ideal_bin_edges)

    teensy_fft1024_bins = generate_bins_from_edges(
        generate_edges_from_bin_centers(teensy_fft1024_bin_centers)
    )

    # what range of indexes from the teensy_fft1024 bins need grouped
    approximate_bin_indexes: List[Tuple[int, ...]] = []
    teensy_bin_index = 0
    lower_teensy_bin_index = teensy_bin_index
    for i_low_edge, i_high_edge in ideal_bins:
        while True:
            t_low_edge, t_high_edge = teensy_fft1024_bins[teensy_bin_index]
            # compare the teensy bin center to the ideal high edge to see where it best fits
            # if we are at the final index, just drop it into the final bin
            if (
                (t_high_edge - t_low_edge) / 2
            ) + t_low_edge > i_high_edge or teensy_bin_index == len(
                teensy_fft1024_bins
            ) - 1:
                approximate_bin_indexes.append(
                    tuple([lower_teensy_bin_index, teensy_bin_index - 1])
                )
                break
            teensy_bin_index += 1
        lower_teensy_bin_index = teensy_bin_index

    # correlate the index with the centers vs the ideal
    for i_bin, t_bin_idx in zip(ideal_bins, approximate_bin_indexes):
        centers = []
        for i in range(t_bin_idx[0], t_bin_idx[1] + 1):
            centers.append(teensy_fft1024_bins[i])
        # print(f"{i_bin}: {centers}")

    # verify that all indexes in range are accounted for
    foo = []
    for lower, higher in approximate_bin_indexes:
        for i in range(lower, higher + 1):
            foo.append(i)
    for i, j in zip(foo, range(len(foo))):
        assert i == j

    # verify that there are the correct number of bins
    assert len(ideal_bins) == len(approximate_bin_indexes)

    # print(approximate_bin_indexes)

    for i, bin in enumerate(approximate_bin_indexes):
        print(f"level[{i}] = fft1024.read({bin[0]},{bin[1]});")


if __name__ == "__main__":
    main()

print("hello")
