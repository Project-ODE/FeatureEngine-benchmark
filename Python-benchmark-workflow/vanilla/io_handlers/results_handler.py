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

# Authors: Dorian Cazau, Alexandre Degurse

"""
Module providing ResultsHandler class
"""

import os


class ResultsHandler:
    """
    Class handling the naming, formatting and writing of acoustic features
    """
    def __init__(
            self,
            wav_file_id,
            results_destination,
            segment_size,
            window_size,
            window_overlap,
            nfft
    ):

        self.wav_file_id = wav_file_id
        self.results_destination = results_destination
        self.segment_size = segment_size
        self.window_size = window_size
        self.nfft = nfft
        self.window_overlap = window_overlap

    def __str__(self):
        return "{}-{}-{}-{}-{}"\
            .format(self.wav_file_id, self.segment_size,
                    self.window_size, self.window_overlap, self.nfft)

    def write(self, results):
        """
        Function writing the given results inside a json file named after the
        parameters and the version of the benchmark used to generate them.

        :param results: The acoustic features to be saved as a pandas' DataFrame
        :return: None
        """
        if not os.path.exists(self.results_destination):
            os.makedirs(self.results_destination, exist_ok=True)

        results.to_json(
            os.path.join(self.results_destination, str(self)) + ".json",
            double_precision=15,
            orient='records',
            lines=True)
