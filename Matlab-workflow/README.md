# Matlab-workflow for signal processing implementations

This folder contains all implementation of the signal processing workflow
used to measure matlab performance.

## Versions

Currently, the following version are implemented:
-_vanilla_ - simplest implementation of the workflow that doesn't parallelize
nor distribute conputation and has multiple limitations.

-_mt_ - trivial multi-threaded approach, it is based on _vanilla_ but
processes multiple files simultaneously using matlab parfor.
