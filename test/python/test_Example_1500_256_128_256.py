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
Script testing the correctness of benchmarks feature computation
Once all benchmark have been run and the results have been written in resources/results,
this scripts read the results and compares them using numpy.allclose.
"""

import os

import pandas as pd

import read_results
from run_tests import run_tests

# constants
N_CHANNELS = 1

RESULTS_ROOT_DIR = "../resources/results"
VERSION_LIST = [
    "feature_engine_benchmark",
    "scala_only",
    "python_vanilla",
    "matlab_vanilla",
    "python_nobb",
    "python_mt",
    "python_dask"
]

N_NODES_COMPUTED = [1]

DATASET_ID = "Example"
SOUND_IDS = ["Example0", "Example1"]

SEGMENT_SIZE = 1500
WINDOW_SIZE = 256
WINDOW_OVERLAP = 128
NFFT = 256


RUN_ID = DATASET_ID + "_" +"_".join(
    [str(p) for p in [SEGMENT_SIZE, WINDOW_SIZE, WINDOW_OVERLAP, NFFT]])

if __name__ == "__main__":
    for n_nodes in N_NODES_COMPUTED:
        results_dict_dfs = read_results.read(
            RESULTS_ROOT_DIR,
            n_nodes,
            RUN_ID,
            VERSION_LIST)

        print("Beginning tests on {} nodes results:".format(n_nodes))

        run_tests(results_dict_dfs)
