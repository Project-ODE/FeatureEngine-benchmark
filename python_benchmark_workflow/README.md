# Python-workflow-benchmark for signal processing implementations

This folder contains all implementation of the signal processing workflow
used to measure python performance.

## Versions

Currently, the following version are implemented:

+ _vanilla_ - simplest implementation of the workflow that doesn't parallelize
nor distribute computation. Files are processed sequentially.

+ _nobb_ - simplest implementation of the workflow that doesn't parallelize
nor distribute computation and uses a custom implementation of signal
processing routines. Files are processed sequentially.

+ _mt_ - trivial multi-threaded approach, it is based on _vanilla_ but
processes multiple files simultaneously using multi-theading.
