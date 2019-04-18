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
Main script used to run the benchmark on SPM dataset
"""

import sys

import pandas as pd
from dateutil.parser import parse

from signal_processing_vanilla import FeatureGenerator
from io_handlers import SoundHandler, ResultsHandler
from utils import single_file_handler


# Four arguments should be passed through the argument vector:
#  - N_NODES: The number of datarmor nodes used in this run as a Int.
#  - N_FILES: The number of SPM wav files to be processed in this run as a Int.
#  - INPUT_BASE_DIR: The base directory containing the dataset as a String.
#  - OUTPUT_BASE_DIR: The base directory where results are written as a String.
# For example, this set of parameters works as of 2018-12-17 on Datarmor:
# Array("1", "200", ""/home/datawork-alloha-ode/Datasets/SPM",
#   "/home/datawork-alloha-ode/benchmark")
N_NODES = int(sys.argv[1])
N_FILES = int(sys.argv[2])
INPUT_BASE_DIR = sys.argv[3]
OUTPUT_BASE_DIR = sys.argv[4]

DATASET_ID = "SPM{}files".format(N_FILES)

WAV_FILES_LOCATION = INPUT_BASE_DIR + "/PAM/SPMAuralA2010"
METADATA_FILE_PATH = INPUT_BASE_DIR + "/PAM/Metadata_SPMAuralA2010.csv"

SAMPLE_RATE = 32768
CALIBRATION_FACTOR = 0.0
SEGMENT_DURATION = 60.0
SEGMENT_SIZE = int(SEGMENT_DURATION * SAMPLE_RATE)
WINDOW_SIZE = 256
NFFT = 256
WINDOW_OVERLAP = 128

RUN_ID = DATASET_ID + "_" + "_".join(
    [str(p) for p in [SEGMENT_SIZE, WINDOW_SIZE, WINDOW_OVERLAP, NFFT]])

RESULTS_DESTINATION = OUTPUT_BASE_DIR +\
    "/results/python_vanilla/{}/".format(N_NODES) + RUN_ID


if __name__ == "__main__":
    task_configs = [{
        "location": WAV_FILES_LOCATION,
        "name": file_metadata[0],
        "timestamp": parse(
            file_metadata[9] + " " + file_metadata[10] + " UTC"
        ),
        "sample_rate": 32768.0,
        "wav_bits": 16,
        "n_channels": 1,
        "results_destination": RESULTS_DESTINATION,
        "calibration_factor": CALIBRATION_FACTOR,
        "segment_duration": SEGMENT_DURATION,
        "window_size": WINDOW_SIZE,
        "window_overlap": WINDOW_OVERLAP,
        "nfft": NFFT
    } for file_metadata in pd.read_csv(
        METADATA_FILE_PATH, delimiter=";").values]

    for config in task_configs[:N_FILES]:
        single_file_handler.process_file(config)
