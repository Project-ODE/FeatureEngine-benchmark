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

import os, sys
from subprocess import Popen
from time import time
from abc import ABC, abstractmethod


def announce(s):
    print("*" * 15 + "   {}   ".format(s) + "*" * 15)

class Benchmark(ABC):
    VERSION = None

    def __init__(
        self, n_nodes, n_files, input_base_dir, output_base_dir, **kwargs
    ):

        self.duration = -1
        self.n_files = n_files
        self.n_nodes = n_nodes
        self.dry_run = kwargs.get("dry_run", False)

        self.job_params = [str(p) for p in [n_nodes, self.n_files,
            input_base_dir, output_base_dir]]

        if hasattr(self, 'N_THREADS'):
            self.job_params.append(str(self.N_THREADS))

        self.run_command = self.BASE_COMMAND.format(" ".join(self.job_params))

    def run(self):
        announce("Starting {} benchmark with {} files".format(self.VERSION, self.n_files))
        print("Running command: {}".format(self.run_command))
        sys.stdout.flush()

        t_start = time()

        if not self.dry_run:
            p = Popen(self.run_command, shell=True)
            p.wait()

            if (p.return_code != 0):
                print("Run failed !!!")
                sys.exit(1)

        self.duration = time() - t_start

        announce("Benchmark {} with {} files, completed in {} sec".format(
            self.VERSION, self.n_files, self.duration))

        print("\n\n")
        sys.stdout.flush()

        return [
            self.VERSION,
            str(self.n_nodes),
            str(self.n_files),
            str(self.duration)
        ]

class FEBenchmark(Benchmark):
    VERSION = "feature_engine_benchmark"

    SPARK_PARAMS = [
        "--driver-memory 4G",
        "--executor-cores 3",
        "--num-executors 17",
        "--executor-memory 5500M",
        "--class org.oceandataexplorer.engine.benchmark.SPM",
        "--conf spark.hadoop.mapreduce.input"\
            + ".fileinputformat.split.minsize=268435456"
    ]

    FE_JAR_LOCATION = (
        " FeatureEngine-benchmark/target/scala-2.11/"
        "FeatureEngine-benchmark-assembly-0.1.jar "
    )

    BASE_COMMAND = "spark-submit " + " ".join(SPARK_PARAMS)\
        + FE_JAR_LOCATION + " {}"

class FEMinBenchmark(Benchmark):
    VERSION = "feature_engine_benchmark_min"

    SPARK_PARAMS = [
        "--driver-memory 4G",
        "--executor-cores 1",
        "--num-executors 1 ",
        "--executor-memory 80G",
        "--class org.oceandataexplorer.engine.benchmark.SPM",
        "--conf spark.hadoop.mapreduce.input"\
            + ".fileinputformat.split.minsize=268435456"
    ]

    FE_JAR_LOCATION = (
        " FeatureEngine-benchmark/target/"
        "scala-2.11/FeatureEngine-benchmark-assembly-0.1.jar "
    )

    BASE_COMMAND = "spark-submit " + " ".join(SPARK_PARAMS)\
        + FE_JAR_LOCATION + " {}"

class ScalaOnlyBenchmark(Benchmark):
    # "scala_only" designates single threaded runs, equivalent to "scala_only_1"
    VERSION = "scala_only"
    # number of threads used is statically defined,
    # subclassing and overriding is the recommended way to change it
    N_THREADS = 1

    JAR_LOCATION = (
        " FeatureEngine-benchmark/target/"
        "scala-2.11/FeatureEngine-benchmark-assembly-0.1.jar "
    )

    BASE_COMMAND =  "java -Xms64g -Xmx100g -classpath " + JAR_LOCATION\
            + "org.oceandataexplorer.engine.benchmark.SPMScalaOnly {} "



class PythonVanillaBenchmark(Benchmark):
    VERSION = "python_vanilla"
    BASE_COMMAND =  "cd python_benchmark_workflow && python3 spm_vanilla.py {} "

class PythonNoBBBenchmark(Benchmark):
    VERSION = "python_nobb"
    BASE_COMMAND =  "cd python_benchmark_workflow && python3 spm_nobb.py {} "


class PythonMTBenchmark(Benchmark):
    # "python_mt" designates single threaded runs, equivalent to "python_mt_1"
    VERSION = "python_mt"
    BASE_COMMAND =  "cd python_benchmark_workflow && python3 spm_mt.py {} "
    # number of threads used is statically defined,
    # subclassing and overriding is the recommended way to change it
    N_THREADS = 1

class MatlabVanillaBenchmark(Benchmark):
    VERSION = "matlab_vanilla"
    BASE_COMMAND =  (
        "cd Matlab-workflow && "
        "matlab -nodisplay -nosplash -nodesktop "
        "-r \"spm_vanilla {}; exit\""
    )

class MatlabMTBenchmark(Benchmark):
    # "matlab_mt" designates single threaded runs, equivalent to "matlab_mt_1"
    VERSION = "matlab_mt"
    BASE_COMMAND =  (
        "cd Matlab-workflow && "
        "matlab -nodisplay -nosplash -nodesktop "
        "-r \"spm_vanilla {}; exit\""
    )
    # number of threads used is statically defined,
    # subclassing and overriding is the recommended way to change it
    N_THREADS = 1


class BenchmarkManager(object):
    def __init__(
        self,
        n_nodes,
        input_base_dir,
        output_base_dir,
        runs,
        benchmark_classes,
        **kwargs
    ):
        self.n_nodes = n_nodes
        self.input_base_dir = input_base_dir
        self.output_base_dir = output_base_dir
        self.benchmarks = []
        self.results = []
        self.extra_args = kwargs

        self.init_benchmarks(runs, benchmark_classes)

    def init_benchmarks(self, runs, benchmark_classes):
        for n_files in runs[self.n_nodes]:
            for benchmark_class in benchmark_classes:
                self.benchmarks.append(benchmark_class(
                    self.n_nodes,
                    n_files,
                    self.input_base_dir,
                    self.output_base_dir,
                    **self.extra_args
                ))

    def run_benchmarks(self):
        t_start = time()

        for benchmark in self.benchmarks:
            result = benchmark.run()
            self.results.append(result)

        print("\n" * 4)
        announce(time() - t_start)

    def save_as_csv(self, result_file_path):
        csv_string = "\n".join([",".join(result) for result in self.results])
        f = open(result_file_path, "w")
        f.write(csv_string)
        f.close()


def new_mt_run(MTBaseClass, n_threads):
    """
    Creates new multi-threaded benchmark classes given a number of threads
    """
    return type(
        MTBaseClass.VERSION + "_{}".format(n_threads),
        (MTBaseClass,),
        {
            'N_THREADS': n_threads,
            'VERSION': MTBaseClass.VERSION + "_{}".format(n_threads)
        }
    )

if __name__ == "__main__":
    if (len(sys.argv) < 4):
        print("Invalid syntax\nUsage: python3 run_benchmark.py n_nodes indir outdir")
        exit(1)

    n_nodes = int(sys.argv[1])
    input_base_dir = sys.argv[2]
    output_base_dir = sys.argv[3]

    tag = 'notag'
    if (len(sys.argv) == 5):
        tag = sys.argv[4]

    runs = {
        1: [1, 2, 5, 10, 25, 50, 75, 100],
        2:  [5, 10, 25, 50, 75, 100, 200],
        4:  [50, 75, 100, 200, 400],
        8:  [100, 200, 400, 800, 1600],
    }

    # put the classes that should be run during benchmark here
    benchmarks = [
        FEBenchmark,
        FEMinBenchmark,
        PythonVanillaBenchmark,
        PythonNoBBBenchmark,
        new_mt_run(PythonMTBenchmark, 2),
        MatlabVanillaBenchmark,
        new_mt_run(MatlabMTBenchmark, 2)
    ]

    # optionals arguments for benchmark
    extra_args = {
        #'dry_run': True
    }

    benchmarks = BenchmarkManager(
        n_nodes,
        input_base_dir,
        output_base_dir,
        runs,
        benchmarks,
        **extra_args
    )

    benchmarks.run_benchmarks()

    if not extra_args.get('dry_run', False):
        benchmarks.save_as_csv(
            output_base_dir + "/times/benchmark_durations_{}node_{}.csv".format(n_nodes, tag))
