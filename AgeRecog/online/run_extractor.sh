#!/bin/bash
# Copyright   2019   Minsoo Kim
# Apache 2.0.
#
#
# See ../README.txt for more info on data required.

# make sure to modify "cmd.sh" and "path.sh", change the KALDI_ROOT to the correct directory
. ./cmd.sh
. ./path.sh
set -e

stage=14

# The kaldi voxceleb egs directory
kaldi_voxceleb=$KALDI_ROOT/egs/voxceleb
extractor=$PROJECT_ROOT/../extractor
data=$PROJECT_ROOT/data
exp=$PROJECT_ROOT
mfccdir=$PROJECT_ROOT/mfcc
vaddir=$PROJECT_ROOT/mfcc
datadir=$DATA_ROOT
trials=$data/test/trials

stage=$1
nnetdir=$exp/basemodel/xvector_nnet_pretrain
checkpoint='last'


cd $extractor
nnet/run_extract_embeddings_online.sh --cmd "$train_cmd" --nj 1 --use-gpu false --checkpoint $checkpoint --stage 0 \
  --chunk-size 10000 --normalize false --node "output" \
  $nnetdir $data/test $nnetdir/xvectors_test

