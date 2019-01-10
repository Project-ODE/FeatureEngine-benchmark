#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2018 Project-ODE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Authors: Dorian Cazau, Alexandre Degurse

"""
Module providing tools for spectral analysis
"""

import numpy
import scipy.signal


def segmentation(signal, window_size, window_overlap):
    """
    Computes a simple segmentation dropping incomplete windows
    and allowing for overlap.
    """
    n_windows = (signal.shape[0] - window_overlap) // (
        window_size - window_overlap)

    shape = (n_windows, window_size)

    if window_overlap != 0:
        strides = (window_overlap * signal.strides[0], signal.strides[0])
    else:
        strides = (window_size * signal.strides[0], signal.strides[0])

    windows = numpy.lib.stride_tricks.as_strided(
        signal, shape=shape, strides=strides)

    return windows


def spectrogram(signal, sample_rate, window_size, window_overlap, nfft):
    """
    Computes the power spectral density over the given signal.
    """
    windows = segmentation(signal, window_size, window_overlap)

    # For some reason, pylint can't resolve scipy.signal.hamming
    # pylint: disable=no-member,no-name-in-module
    window_function = scipy.signal.hamming(window_size, sym=False)
    # pylint: enable=no-member,no-name-in-module

    windowed_signal = windows * window_function

    fft = numpy.fft.fft(windowed_signal, nfft)

    spectrum_size = int(nfft / 2 + (nfft % 2 == 0))

    one_sided_fft = fft[..., :spectrum_size]

    periodograms = numpy.abs(one_sided_fft) ** 2

    if nfft % 2 == 0:
        periodograms[..., 1:spectrum_size-1] *= 2
    else:
        periodograms[..., 1:spectrum_size-1] *= 2

    # normalized spectrogram
    periodograms /= (sample_rate * (window_function ** 2).sum())

    return periodograms


def welch(signal, sample_rate, window_size, window_overlap, nfft):
    """
    Computes the power spectral density over the given signal
    using welch method.
    """
    periodograms = spectrogram(
        signal, sample_rate, window_size, window_overlap, nfft)

    welchs = numpy.mean(periodograms, axis=0)

    return welchs
