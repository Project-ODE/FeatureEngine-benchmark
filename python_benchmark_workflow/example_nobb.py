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
Example of main script used to run the benchmark on test data
"""

import pandas as pd
from dateutil.parser import parse

from signal_processing_nobb import FeatureGenerator
from io_handlers import SoundHandler, ResultsHandler
from utils import single_file_handler

DATASET_ID = "Example"

RESOURCES_DIR = "../test/resources"
WAV_FILES_LOCATION = RESOURCES_DIR + "/sounds"
METADATA_FILE_PATH = RESOURCES_DIR + "/metadata/Example_metadata.csv"

CALIBRATION_FACTOR = 0.0
SEGMENT_DURATION = 1.0
WINDOW_SIZE = 256
NFFT = 256
WINDOW_OVERLAP = 128

RUN_ID = DATASET_ID + "_" + "_".join(
    [str(p) for p in [SEGMENT_DURATION, WINDOW_SIZE, WINDOW_OVERLAP, NFFT]])

RESULTS_DESTINATION = RESOURCES_DIR + "/results/python_nobb/1/" + RUN_ID


if __name__ == "__main__":
    configs = [{
        "location": WAV_FILES_LOCATION,
        "name": file_metadata[0],
        "timestamp": parse(file_metadata[1]),
        "sample_rate": 1500.0,
        "wav_bits": 16,
        "n_samples": 3587,
        "n_channels": 1,
        "results_destination": RESULTS_DESTINATION,
        "calibration_factor": CALIBRATION_FACTOR,
        "segment_duration": SEGMENT_DURATION,
        "window_size": WINDOW_SIZE,
        "window_overlap": WINDOW_OVERLAP,
        "nfft": NFFT
    } for file_metadata in pd.read_csv(METADATA_FILE_PATH).values]

    for config in configs:
        single_file_handler.process_file(config)
