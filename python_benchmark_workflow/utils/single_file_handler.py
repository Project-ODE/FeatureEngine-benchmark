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

# Authors: Alexandre Degurse

"""
Module providing tools for wav file processing
"""

import os
from time import time

from signal_processing_vanilla import FeatureGenerator
from io_handlers import SoundHandler, ResultsHandler


def process_file(config):
    print("Start processing {}".format(config["name"]))
    tStart = time()

    sound_handler = SoundHandler(
        config["location"],
        config["name"],
        config["wav_bits"],
        config["sample_rate"],
        config["n_channels"])

    segment_size = int(config["segment_duration"] * config["sample_rate"])

    feature_generator = FeatureGenerator(
        sound_handler,
        config["timestamp"],
        config["sample_rate"],
        config["calibration_factor"],
        segment_size,
        config["window_size"],
        config["window_overlap"],
        config["nfft"]
    )

    results = feature_generator.generate()

    # extract sound's id from sound file name
    # (sound's name follow convention described in test/resources/README.md)
    sound_id = config["name"][:-4]

    resultsHandler = ResultsHandler(
        sound_id,
        config["results_destination"],
        segment_size,
        config["window_size"],
        config["window_overlap"],
        config["nfft"]
    )

    resultsHandler.write(results)

    duration = time() - tStart
    print("Finished processing {} in {}".format(config["name"], duration))

    return duration
