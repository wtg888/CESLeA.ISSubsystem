#!/bin/bash
# Copyright   2019   Minsoo Kim
# Apache 2.0.
#
# See ../README.txt for more info on data required.

. ./cmd.sh
. ./path.sh
set -e

preprocess.sh train
run_xvector.sh train
