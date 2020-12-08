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

scoredir=$PROJECT_ROOT/basemodel/xvector_nnet_pretrain/xvectors_test_novad/scores
num_spkr=`cat $PROJECT_ROOT/basemodel/xvector_nnet_pretrain/xvectors/num_utts.ark | wc -l`

python make_online_result_frame.py $scoredir $num_spkr
python make_online_result.py $scoredir 400 400
cp $scoredir/result.txt result.txt


