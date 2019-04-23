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

"""Run bechmarks script.

Usage: run_benchmarks.py [options] N_NODES INPUT_BASE_DIR OUTPUT_BASE_DIR [TAG]

Options:
    -n --dry-run    Do not execute benchmark, simply prompt the commands that should be run.
"""

import os, sys
from subprocess import Popen
from time import time
from abc import ABC
from docopt import docopt


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

    def run(self):
        self.run_command = self.BASE_COMMAND.format(" ".join(self.job_params))

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

class ScalaAbstractBenchmark(Benchmark, ABC):
    JAR_LOCATION = (
        " FeatureEngine-benchmark/target/scala-2.11/"
        "FeatureEngine-benchmark-assembly-0.1.jar "
    )

class SparkAbstractBenchmark(ScalaAbstractBenchmark, ABC):
    SPARK_PARAMS = [
        "--driver-memory 4G",
        "--class org.oceandataexplorer.engine.benchmark.SPM",
        "--conf spark.hadoop.mapreduce.input"\
            + ".fileinputformat.split.minsize=268435456"
    ]

class FEMinBenchmark(SparkAbstractBenchmark):
    VERSION = "scala_femin"

    SPARK_PARAMS = SparkAbstractBenchmark.SPARK_PARAMS + [
        "--executor-cores 1",
        "--num-executors 1",
        "--executor-memory 80G"
    ]

    BASE_COMMAND = "spark-submit " + " ".join(SPARK_PARAMS)\
        + ScalaAbstractBenchmark.JAR_LOCATION + " {}"


class FEBenchmark(SparkAbstractBenchmark):
    VERSION = "scala_fe"

    SPARK_PARAMS = SparkAbstractBenchmark.SPARK_PARAMS + [
        "--executor-cores 1",
        "--executor-memory 80G"
    ]

    def __init__(self, n_nodes, n_files, input_base_dir, output_base_dir, **kwargs):
        super(FEBenchmark, self).__init__(n_nodes, n_files, input_base_dir, output_base_dir, **kwargs)

        # n_nodes is known only at runtime so `SPARK_PARAMS` must be completed with the number of executors
        # that depends on n_nodes. `BASE_COMMAND` contains spark parameters so it is also defined here.
        self.SPARK_PARAMS = FEBenchmark.SPARK_PARAMS + ["--num-executors {}".format(17 * n_nodes)]
        self.BASE_COMMAND = "spark-submit " + " ".join(self.SPARK_PARAMS)\
            + ScalaAbstractBenchmark.JAR_LOCATION + " {}"


class ScalaMultiThreadedBenchmark(ScalaAbstractBenchmark):
    # "scala_mt" designates single threaded runs, equivalent to "scala_mt_1"
    VERSION = "scala_mt"
    # number of threads used is statically defined,
    # subclassing and overriding is the recommended way to change it
    N_THREADS = 1

    BASE_COMMAND =  "java -Xms64g -Xmx100g -classpath " + ScalaAbstractBenchmark.JAR_LOCATION\
            + "org.oceandataexplorer.engine.benchmark.SPMScalaMultiThreaded {} "



class PythonVanillaBenchmark(Benchmark):
    VERSION = "python_vanilla"
    BASE_COMMAND =  "cd python_benchmark_workflow && python3 spm_vanilla.py {} "

class PythonNoBBBenchmark(Benchmark):
    VERSION = "python_nobb"
    BASE_COMMAND =  "cd python_benchmark_workflow && python3 spm_nobb.py {} "


class PythonMultiThreadedBenchmark(Benchmark):
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

class MatlabMultiThreadedBenchmark(Benchmark):
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
        announce("Finished running benchmarks in {} sec".format(time() - t_start))

    def save_as_csv(self, result_file_path):
        csv_string = "\n".join([",".join(result) for result in self.results])
        f = open(result_file_path, "w")
        f.write(csv_string)
        f.close()


def new_mt_benchmark(MultiThreadedBaseClass, n_threads):
    """
    Creates new multi-threaded benchmark classes given a number of threads
    """
    return type(
        MultiThreadedBaseClass.VERSION + "_{}".format(n_threads),
        (MultiThreadedBaseClass,),
        {
            'N_THREADS': n_threads,
            'VERSION': MultiThreadedBaseClass.VERSION + "_{}".format(n_threads)
        }
    )

if __name__ == "__main__":
    arguments = docopt(__doc__)

    n_nodes = int(arguments["N_NODES"])
    input_base_dir = arguments["INPUT_BASE_DIR"]
    output_base_dir = arguments["OUTPUT_BASE_DIR"]
    dry_run = arguments["--dry-run"]

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
        new_mt_benchmark(PythonMultiThreadedBenchmark, 2),
        MatlabVanillaBenchmark,
        new_mt_benchmark(MatlabMultiThreadedBenchmark, 2)
    ]

    # optionals arguments for benchmark
    extra_args = {
        'dry_run': dry_run
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

    if not dry_run:
        benchmarks.save_as_csv(
            output_base_dir + "/times/benchmark_durations_{}node_{}.csv".format(
                n_nodes, arguments["TAG"]
            )
        )
