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

if [ $# != 1 ]; then
  echo "Usage: $0 <stage>"
  echo "e.g.: $0 train"
  echo "e.g.: $0 test"
  exit 1;
fi

stage=$1
nnetdir=$exp/basemodel/xvector_nnet_pretrain
checkpoint='last'

if [ $stage = train ]; then
  cd $extractor
  #extract xvector in data
  nnet/run_extract_embeddings.sh --cmd "$train_cmd" --nj 1 --use-gpu false --checkpoint $checkpoint --stage 0 \
    --chunk-size 10000 --normalize false --node "output" \
    $nnetdir $data/spkrs $nnetdir/xvectors
  #normalize X
fi

if [ $stage = test ]; then
  #extract xvector in test data
  nnetdir_test=$nnetdir/xvectors_test_novad
  cd $extractor
  nnet/run_extract_embeddings_diar.sh --cmd "$train_cmd" --nj 1 --use-gpu false --checkpoint $checkpoint --stage 0 \
    --chunk-size 80 --normalize false --node "output" \
    $nnetdir $data/test $nnetdir_test
  #cosine similarity between test xvector and spkrs xvector
  mkdir -p $nnetdir_test/scores
  cd $PROJECT_ROOT
  make_trial.sh $nnetdir_test
  cat $nnetdir_test/trials.txt | awk '{print $1, $2}' | \
    ivector-compute-dot-products - \
      "ark:ivector-normalize-length scp:$nnetdir/xvectors/spk_xvector.scp ark:- |" \
      "ark:ivector-normalize-length scp:$nnetdir_test/xvector.scp ark:- |" \
      $nnetdir_test/scores/scores.cos

fi
