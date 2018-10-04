# ODE Feature Engine benchmark

## Pre-requisites

### FeatureEngine-benchmark

Make sure you have java 8, scala and sbt installed to run FeatureEngine-benchmark
and Matlab with the signal processing toolbox to run Matlab's benchmark.

#### Debian / Unbuntu FeatureEngine-benchmark setup

```sh
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install openjdk-8-jdk scala
```

And for sbt: https://www.scala-sbt.org/1.0/docs/Installing-sbt-on-Linux.html


## Usage

### FeatureEngine-benchmark

In the *FeatureEngine* directory, start sbt, then compile and test:

```sh
sbt
compile
test
```

First run of sbt might be long as it will download all needed dependencies.
