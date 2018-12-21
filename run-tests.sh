#!/bin/bash

# Fail if a single command fails
set -ev

SPARK_HOME="$HOME/spark/spark-2.4.0-bin-hadoop2.7"

cd FeatureEngine-benchmark

# Asssembly also runs FeatureEngine-benchmark's tests and would fail if any
# of them doesn't pass
sbt compile
sbt assembly
sbt scalastyle

# Run benchmark on test file in order to generate workflow results.
$SPARK_HOME/bin/spark-submit --class org.oceandataexplorer.engine.benchmark.Example target/scala-2.11/FeatureEngine-benchmark-assembly-0.1.jar

# Return to project' root directory
cd ..

# Create a python environment to run python benchmark on test data
# and cross-validate results from all benchmarks.
# Downloaded packages are cached using travis' cache.
# Once all the results have been generated, they will be loaded in this python environment
# for cross-validation (ie ensure that all workflows compute the same thing)
docker run -it --rm -v $HOME/.local/lib/python3.7:/root/.local/lib/python3.7\
  -v $(pwd):/root/project\
  python:3.7 /bin/sh -c\
  "
  apt update && apt install -y libsndfile1-dev &&\
  cd /root/project/Python-benchmark-workflow &&\
  pip3 install --user -r requirements.txt &&\
  python3 -m pylint --rcfile=.pylintrc vanilla nobb &&\
  python3 -m pycodestyle vanilla nobb &&\
  cd vanilla &&\
  python3 example.py &&\
  cd ../nobb &&\
  python3 example.py &&\
  cd ../../test/python &&\
  python3 test_Example_1500_256_128_256.py
  "


# Either travis (uid=2000) or user's uid
uid=$(id -u)

# Change cached python package files owership to avoid any problems
sudo chown -R $uid:$uid $HOME/.local/lib/python3.7
