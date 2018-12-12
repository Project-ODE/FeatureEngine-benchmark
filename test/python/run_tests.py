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
Module providing function to tests whether all benchmarks produces the same results
"""

import numpy as np
from itertools import combinations

def run_tests(results):
    """
    Function testing if results are consistent.

    :param results: The results of the benchmark as a python dict:
    {"LANGUAGE_VERSION": pandas.DataFrame}, the dict should contain all results
    as pandas DataFrame for a `run_id` of `LANGUAGE_VERSION`.
    :return: None
    """
    for result_tuple in combinations(results.keys(), 2):
        print("  - {} against {}:".format(result_tuple[0], result_tuple[1]))

        df_a = results[result_tuple[0]]
        df_b = results[result_tuple[1]]

        print("    * results should contains the same number of features " +
            "computed on the same number of segments")
        assert df_a.shape == df_b.shape

        print("    * results should the same timestamps")
        df_a_ts = df_a.sort_values("timestamp").timestamp.values
        df_b_ts = df_b.sort_values("timestamp").timestamp.values
        assert (df_a_ts == df_b_ts).all()

        n_segments = df_a.shape[0]

        for i_segment in range(n_segments):
            ts = df_a.timestamp[i_segment]
            print("    + moving to time segment {}"
                .format(ts))

            if len(df_a.shape) == 2:
                n_channels = 1
            else:
                n_channels = df_a.shape[1]

            for i_channel in range(n_channels):
                a = df_a[df_a.timestamp == ts]
                b = df_b[df_b.timestamp == ts]

                welch_a = np.array(a.welch.values[0][i_channel])
                welch_b = np.array(b.welch.values[0][i_channel])

                print("      * welchs should match for segment {} and channel {}".format(i_segment, i_channel))
                assert np.allclose(welch_a, welch_b, atol=1.e-14)

                tol_a = np.array(a.tol.values[0][i_channel])
                tol_b = np.array(b.tol.values[0][i_channel])

                print("      * tols should match for segment {} and channel {}".format(i_segment, i_channel))
                assert np.allclose(tol_a, tol_b, atol=1.e-4, rtol=1.e-4)

                spl_a = np.array(a.spl.values[0][i_channel])
                spl_b = np.array(b.spl.values[0][i_channel])

                print("      * spls should match for segment {} and channel {}".format(i_segment, i_channel))
                assert np.allclose(spl_a, spl_b, atol=1.e-14, rtol=1.e-14)
