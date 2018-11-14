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

# Test that spark works - temporary, will be removed once a full version of FeatureEngine-benchmark
# will be added to the project
$SPARK_HOME/bin/spark-submit --class org.apache.spark.examples.SparkPi $SPARK_HOME/examples/jars/spark-examples_2.11-2.4.0.jar

# Run benchmark on test file in order to generate workflow results.
# $SPARK_HOME/bin/spark-submit target/scala-2.11/FeatureEngine-benchmark-assembly-0.1.jar

# Return to project' root directory
cd ..

# Create a pythonic environment to run python tests and cross-validate results from all benchmarks
# downloaded packages are cached using a volume
# Once all the results have been generated, they will be loaded in pyspark
# for cross-validation (ie ensure that all workflows compute the same thing)
docker run -it --rm -v $HOME/.local/lib/python3.7:/root/.local/lib/python3.7\
  -v $(pwd):/root/project\
  -v $SPARK_HOME:/root/spark:ro\
  python:3.7 /bin/sh -c "apt update && apt install -y libsndfile1-dev openjdk-8-jre-headless &&\
    cd /root/project/Python-benchmark-workflow &&\
    pip3 install --user -r requirements.txt &&\
    python3 main.py &&\
    /root/spark/bin/spark-submit /root/spark/examples/src/main/python/pi.py
    "


# Either travis (uid=2000) or user's uid
uid=$(id -u)

# Change cached python package files owership to avoid any problems
sudo chown -R $uid:$uid $HOME/.local/lib/python3.7
