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
Module providing functions to read benchmark results
"""

import os
import glob
import pandas as pd

def read(results_root_dir, run_id, version_list):
    results = {}

    for version in version_list:
        results[version] = _read_json_files(results_root_dir + "/" + version + "/" + run_id)

    return results

def _read_json_files(res_dir):
    results_dfs = []
    files_path = glob.glob(res_dir + "/*.json")

    for file_path in files_path:
        results_dfs.append(pd.read_json(
            file_path,
            precise_float=True,
            orient='records',
            lines=True
        ))

    results = pd.concat(results_dfs, ignore_index=True)

    return results
