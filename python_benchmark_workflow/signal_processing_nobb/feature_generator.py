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
Module containing the FeatureGenerator class
"""

from datetime import datetime, timezone

import numpy
import pandas

# For some reason, pylint can't resolve spectral_computation
# pylint: disable=no-member,no-name-in-module
from signal_processing_nobb import spectral_computation
# pylint: enable=no-member,no-name-in-module
from .tol import TOL


class FeatureGenerator:
    """
    Class handling feature generation of acoustic features
    """
    def __init__(
            self, sound_handler, timestamp, sample_rate, calibration_factor,
            segment_size, window_size, window_overlap, nfft,
            low_freq=None, high_freq=None
    ):

        self.sound_handler = sound_handler
        self.timestamp = timestamp
        self.sample_rate = sample_rate
        self.calibration_factor = calibration_factor
        self.segment_size = segment_size
        self.window_size = window_size
        self.window_overlap = window_overlap
        self.nfft = nfft

        if low_freq is None:
            self.low_freq = 0.2 * self.sample_rate
        if high_freq is None:
            self.high_freq = 0.4 * self.sample_rate

        if segment_size < sample_rate:
            raise Exception(
                "Incorrect segment size ({}) for feature generation"
                .format(segment_size)
                + "(lower sample rate ({}) for TOL computation"
                .format(sample_rate)
            )

        self.tol_class = TOL(
            self.sample_rate, int(self.sample_rate),
            self.low_freq, self.high_freq
        )

        self.results = {}

    @staticmethod
    def format_complex_results(result_value):
        """
        Results containing complex values are reformatted following
        the same convention as in FeatureEngine, ie:
        [z_0, z_1, ... , z_n] => [Re(z_0), Im(z_0), Re(z_1), ... Im(z_n)]
        """
        initial_shape = result_value.shape

        n_windows = initial_shape[1]
        feature_size = initial_shape[0]

        value_as_scala_format = numpy.zeros(
            (n_windows, 2*feature_size), dtype=float)
        value_as_complex = result_value.transpose()

        for i in range(n_windows):
            value_as_scala_format[i, ::2] = value_as_complex[i].real
            value_as_scala_format[i, 1::2] = value_as_complex[i].imag

        return value_as_scala_format.transpose()

    def generate(self):
        """
        Function generation pre-defined features with the specified parameters
        :return: A dictionary containing the results
        """
        raw_sound, sample_rate = self.sound_handler.read()

        if sample_rate != self.sample_rate:
            raise Exception(
                "The given sampling rate doesn't match the one read"
            )

        calibrated_sound = raw_sound / 10 ** (self.calibration_factor / 20)

        n_segments = raw_sound.shape[0] // self.segment_size

        segmented_sound = numpy.split(
            calibrated_sound[:self.segment_size * n_segments], n_segments
        )

        results = []

        for i_segment in range(n_segments):
            welch = spectral_computation.welch(
                segmented_sound[i_segment],
                sample_rate,
                self.window_size,
                self.window_overlap,
                self.nfft)

            psd = spectral_computation.spectrogram(
                signal=segmented_sound[i_segment],
                sample_rate=sample_rate,
                window_size=sample_rate,
                window_overlap=0,
                nfft=int(sample_rate))

            tols = numpy.zeros((psd.shape[0], self.tol_class.tob_size))

            for j_tol in range(psd.shape[0]):
                tols[j_tol] = self.tol_class.compute(psd=psd[j_tol])

            tol = numpy.mean(tols, axis=0)

            spl = numpy.array([
                10 * numpy.log10(numpy.sum(welch))
            ])

            timestamp = datetime.fromtimestamp(
                self.timestamp.timestamp()
                + i_segment * (self.segment_size / self.sample_rate),
                tz=timezone.utc
            ).isoformat()

            results.append((
                timestamp,
                numpy.array([welch]),
                numpy.array([tol]),
                numpy.array([spl])
            ))

        return pandas.DataFrame(
            results, columns=("timestamp", "welch", "tol", "spl")
        )
