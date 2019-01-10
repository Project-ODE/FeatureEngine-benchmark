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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Authors: Alexandre Degurse, Paul Nguyen HD

"""
Module providing Third Octave Level computation function
"""

from math import floor, log10
import numpy as np

# We're using some accronymes here:
#   toc: third octave center
#   tob: third octave band


class TOL:
    """
    Class computing TOL
    """
    def __init__(
            self,
            sample_rate,
            nfft,
            low_freq_tol=None,
            high_freq_tol=None
    ):

        if nfft is not int(sample_rate):
            Exception(
                "Incorrect fft-computation window size ({})".format(nfft)
                + "for TOL (should be higher than {})".format(sample_rate)
            )

        self.lower_limit = 1.0
        self.upper_limit = max(sample_rate / 2.0,
                               high_freq_tol if high_freq_tol
                               is not None else 0.0)

        if low_freq_tol is None:
            self.low_freq_tol = self.lower_limit
        elif low_freq_tol < self.lower_limit:
            Exception(
                "Incorrect low_freq_tol ({}) for TOL".format(low_freq_tol)
                + "(lower than lower_limit{})".format(self.lower_limit)
            )
        elif high_freq_tol is not None and low_freq_tol > high_freq_tol:
            Exception(
                "Incorrect low_freq_tol ({}) for TOL".format(low_freq_tol)
                + "(higher than high_freq_tol {}".format(high_freq_tol)
            )
        elif high_freq_tol is None and low_freq_tol > high_freq_tol:
            Exception(
                "Incorrect low_freq_tol ({}) for TOL".format(low_freq_tol)
                + "(higher than upper_limit {}".format(self.upper_limit)
            )
        else:
            self.low_freq_tol = low_freq_tol

        if high_freq_tol is None:
            self.high_freq_tol = self.upper_limit
        elif high_freq_tol > self.upper_limit:
            Exception(
                "Incorrect high_freq_tol ({}) for TOL".format(high_freq_tol)
                + "(higher than upper_limit {})".format(self.upper_limit))
        elif low_freq_tol is not None and high_freq_tol < low_freq_tol:
            Exception(
                "Incorrect high_freq_tol ({}) for TOL".format(low_freq_tol)
                + "(lower than low_freq_tol {})".format(high_freq_tol)
            )
        elif low_freq_tol is None and high_freq_tol < self.lower_limit:
            Exception(
                "Incorrect high_freq_tol ({}) for TOL".format(high_freq_tol)
                + "(lower than lower_limit {})".format(self.lower_limit)
            )
        else:
            self.high_freq_tol = high_freq_tol

        # when wrong low_freq_tol, high_freq_tol are given,
        # computation falls back to default values
        if not self.lower_limit <= self.low_freq_tol\
                < self.high_freq_tol <= self.upper_limit:

            Exception(
                "Unexpected exception occurred - "
                + "wrong parameters were given to TOL"
            )

        self.sample_rate = sample_rate
        self.nfft = nfft

        self.tob_indices = self._compute_tob_indices()
        self.tob_size = len(self.tob_indices)

    def _compute_tob_indices(self):
        max_third_octave_index = floor(10 * log10(self.upper_limit))

        tob_center_freqs = np.power(
            10, np.arange(0, max_third_octave_index + 1) / 10
        )

        all_tob = np.array([
            _tob_bounds_from_toc(toc_freq) for toc_freq in tob_center_freqs
        ])

        tob_bounds = np.array([
            tob for tob in all_tob
            if self.low_freq_tol <= tob[1] < self.upper_limit
            and tob[0] < self.high_freq_tol
        ])

        return np.array([self._bound_to_index(bound) for bound in tob_bounds])

    def _bound_to_index(self, bound):
        return np.array([floor(bound[0] * self.nfft / self.sample_rate),
                         floor(bound[1] * self.nfft / self.sample_rate)],
                        dtype=int)

    def compute(self, psd):

        """
        Function computing Third Octave Level over power spectral density.

        :param psd: The power spectral density the be used for TOL computation.
        :param sample_rate: The sounds sample rate.
        :param nfft: The size of the FFT-computation window
        :param low_freq_tol: The lower limit of the TOL study range.
        :param high_freq_tol: The higher limit of the TOL study range
        :return:
        """

        third_octave_power_bands = np.array([
            np.sum(psd[indices[0]:indices[1]]) for indices in self.tob_indices
        ])

        return 10 * np.log10(third_octave_power_bands)


def _tob_bounds_from_toc(center_freq):
    return center_freq * np.power(10, np.array([-0.05, 0.05]))
