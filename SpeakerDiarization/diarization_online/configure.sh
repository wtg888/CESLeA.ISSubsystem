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
kaldi_diarization=$KALDI_ROOT/egs/callhome_diarization
data=$PROJECT_ROOT/data
exp=$PROJECT_ROOT/preprocess_log
mfccdir=$PROJECT_ROOT/mfcc
vaddir=$PROJECT_ROOT/mfcc
#voxceleb1_root=/home/craftkim/dataset/VoxCeleb1
#voxceleb2_root=/home/craftkim/dataset/VoxCeleb2

if [ $# != 0 ]; then
  echo "Usage: $0"
  echo "e.g.: $0"
  echo "Options: "
  exit 1;
fi

# link the directories
for dir in '' '../extractor'
do
  ln -fs $kaldi_voxceleb/v2/utils ./$dir
  ln -fs $kaldi_voxceleb/v2/steps ./$dir
  ln -fs $kaldi_voxceleb/v2/sid ./$dir
  ln -fs $kaldi_voxceleb/v2/conf ./$dir
  ln -fs $kaldi_voxceleb/v2/local ./$dir
  ln -fs $kaldi_diarization/v1/diarization ./$dir
done

mkdir data
mkdir mfcc


