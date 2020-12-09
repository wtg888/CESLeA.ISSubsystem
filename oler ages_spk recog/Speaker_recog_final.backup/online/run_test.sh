#!/bin/bash
# Copyright   2019   Minsoo Kim
# Apache 2.0.
#
# See ../README.txt for more info on data required.

. ./cmd.sh
. ./path.sh
set -e

#rm -rf result.txt
#echo "999 test 999" >> result.txt
preprocess.sh test
#preprocess.sh test_noonline
run_xvector.sh test

#rm -rf result.txt
cat basemodel/scores/scores.cos | sort -k 3 -nr > result.txt
