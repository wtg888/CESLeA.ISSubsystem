#!/bin/bash
# Copyright   2017   Johns Hopkins University (Author: Daniel Garcia-Romero)
#             2017   Johns Hopkins University (Author: Daniel Povey)
#        2017-2018   David Snyder
#             2018   Ewald Enzinger
#             2019   Yi Liu. Modified to support network training using TensorFlow
#             2019   Minsoo Kim
# Apache 2.0.
#
# See ../README.txt for more info on data required.

. ./cmd.sh
. ./path.sh
set -e

# The kaldi voxceleb egs dir
kaldi_voxceleb=$KALDI_ROOT/egs/voxceleb
data=$PROJECT_ROOT/data
mfccdir=$PROJECT_ROOT/mfcc

if [ $# != 0 ]; then
  echo "Usage: $0"
  echo "e.g.: $0"
  echo "Options: "
  exit 1;
fi

# link the directories
rm -fr utils steps sid conf local
ln -s $kaldi_voxceleb/v2/utils ./
ln -s $kaldi_voxceleb/v2/steps ./
ln -s $kaldi_voxceleb/v2/sid ./
ln -s $kaldi_voxceleb/v2/conf ./
ln -s $kaldi_voxceleb/v2/local ./
mkdir $data
mkdir $mfccdir


