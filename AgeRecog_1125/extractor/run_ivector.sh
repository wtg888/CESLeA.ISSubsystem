#!/bin/bash
# Copyright   2017   Johns Hopkins University (Author: Daniel Garcia-Romero)
#             2017   Johns Hopkins University (Author: Daniel Povey)
#        2017-2018   David Snyder
#             2018   Ewald Enzinger
#             2019   Minsoo Kim
# Apache 2.0.
#
# See ../README.txt for more info on data required.
# Results (mostly equal error-rates) are inline in comments below.

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
voxceleb1_trials=$data/voxceleb1_test/trials
skip_train=0
stage=0

if [ $# != 0 ]; then
  echo "Usage: $0"
  echo "e.g.: $0"
  echo "Options: "
  echo "  --skip_train 0 # Whether to skip training stage. train the extractor when skip_train 0"
  exit 1;
fi

if [ $stage -le 3 -a $skip_train -eq 0 ]; then
  # Train the UBM.
  sid/train_diag_ubm.sh --cmd "$train_cmd --mem 4G" \
    --nj 40 --num-threads 8 \
    $data/voxceleb2_train 2048 \
    $exp/diag_ubm

  sid/train_full_ubm.sh --cmd "$train_cmd --mem 25G" \
    --nj 40 --remove-low-count-gaussians false \
    $data/voxceleb2_train \
    $exp/diag_ubm $exp/full_ubm
fi

if [ $stage -le 4 -a $skip_train -eq 0 ]; then
  # In this stage, we train the i-vector extractor.
  #
  # Note that there are well over 1 million utterances in our training set,
  # and it takes an extremely long time to train the extractor on all of this.
  # Also, most of those utterances are very short.  Short utterances are
  # harmful for training the i-vector extractor.  Therefore, to reduce the
  # training time and improve performance, we will only train on the 100k
  # longest utterances.
  utils/subset_data_dir.sh \
    --utt-list <(sort -n -k 2 $data/voxceleb2_train/utt2num_frames | tail -n 100000) \
    $data/voxceleb2_train $data/voxceleb2_train_100k
  # Train the i-vector extractor.
  sid/train_ivector_extractor.sh --cmd "$train_cmd --mem 16G" \
    --ivector-dim 400 --num-iters 5 \
    $exp/full_ubm/final.ubm $data/voxceleb2_train_100k \
    $exp/extractor
fi

if [ $stage -le 5 ]; then
  sid/extract_ivectors.sh --cmd "$train_cmd --mem 4G" --nj 80 \
    $exp/extractor $data/voxceleb2_train \
    $exp/ivectors_voxceleb2_train

  sid/extract_ivectors.sh --cmd "$train_cmd --mem 4G" --nj 40 \
    $exp/extractor $data/voxceleb1_test \
    $exp/ivectors_voxceleb1_test
fi

if [ $stage -le 6 -a $skip_train -eq 0 ]; then
  # Compute the mean vector for centering the evaluation i-vectors.
  $train_cmd $exp/ivectors_voxceleb2_train/log/compute_mean.log \
    ivector-mean scp:$exp/ivectors_voxceleb2_train/ivector.scp \
    $exp/ivectors_voxceleb2_train/mean.vec || exit 1;

  # This script uses LDA to decrease the dimensionality prior to PLDA.
  lda_dim=200
  $train_cmd $exp/ivectors_voxceleb2_train/log/lda.log \
    ivector-compute-lda --total-covariance-factor=0.0 --dim=$lda_dim \
    "ark:ivector-subtract-global-mean scp:$exp/ivectors_voxceleb2_train/ivector.scp ark:- |" \
    ark:$data/voxceleb2_train/utt2spk $exp/ivectors_voxceleb2_train/transform.mat || exit 1;

  # Train the PLDA model.
  $train_cmd $exp/ivectors_voxceleb2_train/log/plda.log \
    ivector-compute-plda ark:$data/voxceleb2_train/spk2utt \
    "ark:ivector-subtract-global-mean scp:$exp/ivectors_voxceleb2_train/ivector.scp ark:- | transform-vec $exp/ivectors_voxceleb2_train/transform.mat ark:- ark:- | ivector-normalize-length ark:-  ark:- |" \
    $exp/ivectors_voxceleb2_train/plda || exit 1;
fi

if [ $stage -le 7 -a $skip_train -eq 0 ]; then
  $train_cmd $exp/scores/log/voxceleb1_test_scoring.log \
    ivector-plda-scoring --normalize-length=true \
    "ivector-copy-plda --smoothing=0.0 $exp/ivectors_voxceleb2_train/plda - |" \
    "ark:ivector-subtract-global-mean $exp/ivectors_voxceleb2_train/mean.vec scp:$exp/ivectors_voxceleb1_test/ivector.scp ark:- | transform-vec $exp/ivectors_voxceleb2_train/transform.mat ark:- ark:- | ivector-normalize-length ark:- ark:- |" \
    "ark:ivector-subtract-global-mean $exp/ivectors_voxceleb2_train/mean.vec scp:$exp/ivectors_voxceleb1_test/ivector.scp ark:- | transform-vec $exp/ivectors_voxceleb2_train/transform.mat ark:- ark:- | ivector-normalize-length ark:- ark:- |" \
    "cat '$voxceleb1_trials' | cut -d\  --fields=1,2 |" $exp/scores_voxceleb1_test || exit 1;
fi

if [ $stage -le 8 -a $skip_train -eq 0 ]; then
  eer=`compute-eer <(local/prepare_for_eer.py $voxceleb1_trials $exp/scores_voxceleb1_test) 2> /dev/null`
  mindcf1=`sid/compute_min_dcf.py --p-target 0.01 $exp/scores_voxceleb1_test $voxceleb1_trials 2> /dev/null`
  mindcf2=`sid/compute_min_dcf.py --p-target 0.001 $exp/scores_voxceleb1_test $voxceleb1_trials 2> /dev/null`
  echo "EER: $eer%"
  echo "minDCF(p-target=0.01): $mindcf1"
  echo "minDCF(p-target=0.001): $mindcf2"
  # EER: 5.329%
  # minDCF(p-target=0.01): 0.4933
  # minDCF(p-target=0.001): 0.6168
fi
