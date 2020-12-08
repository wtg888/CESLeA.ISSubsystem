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
exp=$PROJECT_ROOT/preprocess_log
mfccdir=$PROJECT_ROOT/mfcc
vaddir=$PROJECT_ROOT/mfcc
voxceleb1_root=/home/craftkim/dataset/VoxCeleb1
voxceleb2_root=/home/craftkim/dataset/VoxCeleb2
stage=0

if [ $# != 0 ]; then
  echo "Usage: $0"
  echo "e.g.: $0"
  echo "Options: "
  exit 1;
fi

if [ $stage -le 0 ]; then
    # link the directories
    rm -fr utils steps sid conf local
    ln -s $kaldi_voxceleb/v2/utils ./
    ln -s $kaldi_voxceleb/v2/steps ./
    ln -s $kaldi_voxceleb/v2/sid ./
    ln -s $kaldi_voxceleb/v2/conf ./
    ln -s $kaldi_voxceleb/v2/local ./
fi

if [ $stage -le 1 ]; then
  local/make_voxceleb2.pl $voxceleb2_root dev $data/voxceleb2_train
#  local/make_voxceleb2.pl $voxceleb2_root test $data/voxceleb2_test
  local/make_voxceleb1_v2.pl $voxceleb1_root test $data/voxceleb1_test
fi

if [ $stage -le 2 ]; then
  # Make MFCCs and compute the energy-based VAD for each dataset
  for name in voxceleb2_train voxceleb1_test; do
    steps/make_mfcc.sh --write-utt2num-frames true \
      --mfcc-config conf/mfcc.conf --nj 40 --cmd "$train_cmd" \
      $data/${name} $exp/make_mfcc $mfccdir
    utils/fix_data_dir.sh $data/${name}
    sid/compute_vad_decision.sh --nj 40 --cmd "$train_cmd" \
      $data/${name} $exp/make_vad $vaddir
    utils/fix_data_dir.sh $data/${name}
  done
fi

