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
Main script used to run the benchmark on test data
"""

import pandas as pd
from dateutil.parser import parse

from signal_processing import FeatureGenerator
from io_handlers import SoundHandler, ResultsHandler

DATASET_ID = "Example"

RESOURCES_DIR = "../../test/resources"
WAV_FILES_LOCATION = RESOURCES_DIR + "/sounds"
METADATA_FILE_PATH = RESOURCES_DIR + "/metadata/Example_metadata.csv"

CALIBRATION_FACTOR = 0.0
SEGMENT_SIZE = 1500
WINDOW_SIZE = 256
NFFT = 256
WINDOW_OVERLAP = 128

RUN_ID = DATASET_ID + "_" +"_".join(
    [str(p) for p in [SEGMENT_SIZE, WINDOW_SIZE, WINDOW_OVERLAP, NFFT]])
RESULTS_DESTINATION = RESOURCES_DIR + "/results/python_vanilla/" + RUN_ID

FILES_TO_PROCESS = [{
    "name": file_metadata[0],
    "timestamp": parse(file_metadata[1]),
    "sample_rate": 1500.0,
    "wav_bits": 16,
    "n_samples": 3587,
    "n_channels": 1
} for file_metadata in pd.read_csv(METADATA_FILE_PATH).values]


for wav_file in FILES_TO_PROCESS:
    sound_handler = SoundHandler(
        WAV_FILES_LOCATION,
        wav_file["name"],
        wav_file["wav_bits"],
        wav_file["sample_rate"],
        wav_file["n_channels"],
        wav_file["n_samples"])

    feature_generator = FeatureGenerator(
        sound_handler, wav_file["timestamp"],
        wav_file["sample_rate"], CALIBRATION_FACTOR,
        SEGMENT_SIZE, WINDOW_SIZE, WINDOW_OVERLAP, NFFT)

    results = feature_generator.generate()

    # extract sound's id from sound file name
    # (sound's name follow convention described in test/resources/README.md)
    sound_id = wav_file["name"].split("_")[0]

    resultsHandler = ResultsHandler(
        sound_id, RESULTS_DESTINATION, SEGMENT_SIZE,
        WINDOW_SIZE, WINDOW_OVERLAP, NFFT)

    resultsHandler.write(results)
