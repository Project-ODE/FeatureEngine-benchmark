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

import os
import time
from pathlib import Path
import numpy as np
from dask.distributed import Client, LocalCluster

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

# pass N_THREADS as arg even if dask is run on multi-node
# it is required to define the results destination
# if run in multi-node give the total number of threads used across the cluster
N_THREADS = 1
if (len(sys.argv) == 6):
    N_THREADS = int(sys.argv[5])

DATASET_ID = "SPM{}files".format(N_FILES)

WAV_FILES_LOCATION = INPUT_BASE_DIR + "/PAM/SPMAuralA2010"
METADATA_FILE_PATH = INPUT_BASE_DIR + "/PAM/Metadata_SPMAuralA2010.csv"

SAMPLE_RATE = 32768
CALIBRATION_FACTOR = 0.0
SEGMENT_DURATION = 10.0
SEGMENT_SIZE = int(SEGMENT_DURATION * SAMPLE_RATE)
WINDOW_SIZE = 4096
NFFT = 4096
WINDOW_OVERLAP = 0

RUN_ID = DATASET_ID + "_" + "_".join(
    [str(p) for p in [SEGMENT_SIZE, WINDOW_SIZE, WINDOW_OVERLAP, NFFT]])

RESULTS_DESTINATION = OUTPUT_BASE_DIR +\
    "/results/python_dask_{}/{}/".format(N_NODES, N_THREADS) + RUN_ID


if __name__ == "__main__":
    scheduler_file = Path(
        "/home/datawork-alloha-ode/benchmark/tmp/scheduler.json")

    client = None

    # if multi-node, use scheduler file created by dask-mpi
    if scheduler_file.is_file():
        client = Client(
            scheduler_file=scheduler_file.resolve()
        )
    # if not, run a local cluster
    else:
        cluster = LocalCluster(
            n_workers=1,
            threads_per_worker=N_THREADS,
            processes=False
        )

        client = Client(
            cluster
        )

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
        METADATA_FILE_PATH, delimiter=";", header=None).values
    ]

    durations = client.map(
        single_file_handler.process_file, task_configs[:N_FILES])
    avg_time = np.average(client.gather(durations))

    print(
        "\nFinished job, processing file take {} sec avg".format(avg_time)
    )
