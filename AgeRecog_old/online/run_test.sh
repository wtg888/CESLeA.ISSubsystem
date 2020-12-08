#!/bin/bash
# Copyright   2019   Minsoo Kim
# Apache 2.0.
#
# See ../README.txt for more info on data required.

. ./cmd.sh
. ./path.sh
set -e

preprocess.sh test
run_xvector.sh test

cat basemodel/scores/scores.cos | sort -k 3 -nr >> result.txt
