#!/bin/bash
# Copyright   2017   Johns Hopkins University (Author: Daniel Garcia-Romero)
#             2017   Johns Hopkins University (Author: Daniel Povey)
#        2017-2018   David Snyder
#             2018   Ewald Enzinger
#             2019   Yi Liu. Modified to support network training using TensorFlow
#             2019   Minsoo Kim
# Apache 2.0.
#
#
# See ../README.txt for more info on data required.
# Results (mostly equal error-rates) are inline in comments below.

# make sure to modify "cmd.sh" and "path.sh", change the KALDI_ROOT to the correct directory
. ./cmd.sh
. ./path.sh
set -e

stage=14

# The kaldi voxceleb egs directory
kaldi_voxceleb=$KALDI_ROOT/egs/voxceleb
data=$PROJECT_ROOT/data
traindata=$data/voxceleb2_train
exp=$PROJECT_ROOT/preprocess_log
mfccdir=$PROJECT_ROOT/mfcc
vaddir=$PROJECT_ROOT/mfcc
voxceleb1_root=/home/craftkim/dataset/VoxCeleb1
voxceleb2_root=/home/craftkim/dataset/VoxCeleb2
voxceleb1_trials=$data/voxceleb1_test/trials
skip_train=0
stage=0
musan_root=/home/craftkim/dataset/musan
rirs_root=/home/craftkim/dataset/RIRS_NOISES

if [ $# != 0 ]; then
  echo "Usage: $0"
  echo "e.g.: $0"
  echo "Options: "
  echo "  --skip_train 0 # Whether to skip training stage. train the extractor when skip_train 0"
  exit 1;
fi


# In this section, we augment the VoxCeleb2 data with reverberation,
# noise, music, and babble, and combine it with the clean data.
if [ $stage -le 2 -a $skip_train -eq 0 ]; then
  frame_shift=0.01
  awk -v frame_shift=$frame_shift '{print $1, $2*frame_shift;}' $data/${traindata}/utt2num_frames > $data/${traindata}/reco2dur

  # Make sure you already have the RIRS_NOISES dataset
#  # Make a version with reverberated speech
#  rvb_opts=()
#  rvb_opts+=(--rir-set-parameters "0.5, RIRS_NOISES/simulated_rirs/smallroom/rir_list")
#  rvb_opts+=(--rir-set-parameters "0.5, RIRS_NOISES/simulated_rirs/mediumroom/rir_list")

  # Make a reverberated version of the VoxCeleb2 list.  Note that we don't add any
  # additive noise here.
  python steps/data/reverberate_data_dir.py \
    "${rvb_opts[@]}" \
    --speech-rvb-probability 1 \
    --pointsource-noise-addition-probability 0 \
    --isotropic-noise-addition-probability 0 \
    --num-replications 1 \
    --source-sampling-rate 16000 \
    $data/${traindata} $data/${traindata}_reverb
  cp $data/${traindata}/vad.scp $data/${traindata}_reverb/
  utils/copy_data_dir.sh --utt-suffix "-reverb" $data/${traindata}_reverb $data/${traindata}_reverb.new
  rm -rf $data/${traindata}_reverb
  mv $data/${traindata}_reverb.new $data/${traindata}_reverb

  # Prepare the MUSAN corpus, which consists of music, speech, and noise
  # suitable for augmentation.
  local/make_musan.sh $musan_root $data

  # Get the duration of the MUSAN recordings.  This will be used by the
  # script augment_data_dir.py.
  for name in speech noise music; do
    utils/data/get_utt2dur.sh $data/musan_${name}
    mv $data/musan_${name}/utt2dur $data/musan_${name}/reco2dur
  done

  # Augment with musan_noise
  python steps/data/augment_data_dir.py --utt-suffix "noise" --fg-interval 1 --fg-snrs "15:10:5:0" --fg-noise-dir "$data/musan_noise" $data/${traindata} $data/${traindata}_noise
  # Augment with musan_music
  python steps/data/augment_data_dir.py --utt-suffix "music" --bg-snrs "15:10:8:5" --num-bg-noises "1" --bg-noise-dir "$data/musan_music" $data/${traindata} $data/${traindata}_music
  # Augment with musan_speech
  python steps/data/augment_data_dir.py --utt-suffix "babble" --bg-snrs "20:17:15:13" --num-bg-noises "3:4:5:6:7" --bg-noise-dir "$data/musan_speech" $data/${traindata} $data/${traindata}_babble

  # Combine reverb, noise, music, and babble into one directory.
  utils/combine_data.sh $data/${traindata}_aug $data/${traindata}_reverb $data/${traindata}_noise $data/${traindata}_music $data/${traindata}_babble
fi

if [ $stage -le 3 -a $skip_train -eq 0 ]; then
  # Take a random subset of the augmentations
  utils/subset_data_dir.sh $data/${traindata}_aug 1000000 $data/${traindata}_aug_1m
  utils/fix_data_dir.sh $data/${traindata}_aug_1m

  # Make MFCCs for the augmented data.  Note that we do not compute a new
  # vad.scp file here.  Instead, we use the vad.scp from the clean version of
  # the list.
  steps/make_mfcc.sh --mfcc-config conf/mfcc.conf --nj 40 --cmd "$train_cmd" \
    $data/${traindata}_aug_1m $exp/make_mfcc $mfccdir

  # Combine the clean and augmented VoxCeleb2 list.  This is now roughly
  # double the size of the original clean list.
  utils/combine_data.sh $data/${traindata}_combined $data/${traindata}_aug_1m $data/${traindata}
fi

# Now we prepare the features to generate examples for xvector training.
if [ $stage -le 4 -a $skip_train -eq 0 ]; then
  local/nnet3/xvector/prepare_feats_for_egs.sh --nj 40 --cmd "$train_cmd" \
    $data/${traindata}_combined $data/${traindata}_combined_no_sil $exp/${traindata}_combined_no_sil
  utils/fix_data_dir.sh $data/${traindata}_combined_no_sil
fi

if [ $stage -le 5 -a $skip_train -eq 0 ]; then
  # Now, we need to remove features that are too short after removing silence
  # frames.  We want atleast 5s (500 frames) per utterance.
  min_len=400
  mv $data/${traindata}_combined_no_sil/utt2num_frames $data/${traindata}_combined_no_sil/utt2num_frames.bak
  awk -v min_len=${min_len} '$2 > min_len {print $1, $2}' $data/${traindata}_combined_no_sil/utt2num_frames.bak > $data/${traindata}_combined_no_sil/utt2num_frames
  utils/filter_scp.pl $data/${traindata}_combined_no_sil/utt2num_frames $data/${traindata}_combined_no_sil/utt2spk > $data/${traindata}_combined_no_sil/utt2spk.new
  mv $data/${traindata}_combined_no_sil/utt2spk.new $data/${traindata}_combined_no_sil/utt2spk
  utils/fix_data_dir.sh $data/${traindata}_combined_no_sil

  # We also want several utterances per speaker. Now we'll throw out speakers
  # with fewer than 8 utterances.
  min_num_utts=8
  awk '{print $1, NF-1}' $data/${traindata}_combined_no_sil/spk2utt > $data/${traindata}_combined_no_sil/spk2num
  awk -v min_num_utts=${min_num_utts} '$2 >= min_num_utts {print $1, $2}' $data/${traindata}_combined_no_sil/spk2num | utils/filter_scp.pl - $data/${traindata}_combined_no_sil/spk2utt > $data/${traindata}_combined_no_sil/spk2utt.new
  mv $data/${traindata}_combined_no_sil/spk2utt.new $data/${traindata}_combined_no_sil/spk2utt
  utils/spk2utt_to_utt2spk.pl $data/${traindata}_combined_no_sil/spk2utt > $data/${traindata}_combined_no_sil/utt2spk

  utils/filter_scp.pl $data/${traindata}_combined_no_sil/utt2spk $data/${traindata}_combined_no_sil/utt2num_frames > $data/${traindata}_combined_no_sil/utt2num_frames.new
  mv $data/${traindata}_combined_no_sil/utt2num_frames.new $data/${traindata}_combined_no_sil/utt2num_frames

  # Now we're ready to create training examples.
  utils/fix_data_dir.sh $data/${traindata}_combined_no_sil
fi

if [ $stage -le 6 -a $skip_train -eq 0 ]; then
  # Split the validation set
  num_heldout_spks=64
  num_heldout_utts_per_spk=20
  mkdir -p $data/${traindata}_combined_no_sil/train2/ $data/${traindata}_combined_no_sil/valid2/

  sed 's/-noise//' $data/${traindata}_combined_no_sil/utt2spk | sed 's/-music//' | sed 's/-babble//' | sed 's/-reverb//' |\
    paste -d ' ' $data/${traindata}_combined_no_sil/utt2spk - | cut -d ' ' -f 1,3 > $data/${traindata}_combined_no_sil/utt2uniq

  utils/utt2spk_to_spk2utt.pl $data/${traindata}_combined_no_sil/utt2uniq > $data/${traindata}_combined_no_sil/uniq2utt
  cat $data/${traindata}_combined_no_sil/utt2spk | utils/apply_map.pl -f 1 $data/${traindata}_combined_no_sil/utt2uniq |\
    sort | uniq > $data/${traindata}_combined_no_sil/utt2spk.uniq

  utils/utt2spk_to_spk2utt.pl $data/${traindata}_combined_no_sil/utt2spk.uniq > $data/${traindata}_combined_no_sil/spk2utt.uniq
  python $TF_KALDI_ROOT/misc/tools/sample_validset_spk2utt.py $num_heldout_spks $num_heldout_utts_per_spk $data/${traindata}_combined_no_sil/spk2utt.uniq > $data/${traindata}_combined_no_sil/valid2/spk2utt.uniq

  cat $data/${traindata}_combined_no_sil/valid2/spk2utt.uniq | utils/apply_map.pl -f 2- $data/${traindata}_combined_no_sil/uniq2utt > $data/${traindata}_combined_no_sil/valid2/spk2utt
  utils/spk2utt_to_utt2spk.pl $data/${traindata}_combined_no_sil/valid2/spk2utt > $data/${traindata}_combined_no_sil/valid2/utt2spk
  cp $data/${traindata}_combined_no_sil/feats.scp $data/${traindata}_combined_no_sil/valid2
  utils/filter_scp.pl $data/${traindata}_combined_no_sil/valid2/utt2spk $data/${traindata}_combined_no_sil/utt2num_frames > $data/${traindata}_combined_no_sil/valid2/utt2num_frames
  utils/fix_data_dir.sh $data/${traindata}_combined_no_sil/valid2

  utils/filter_scp.pl --exclude $data/${traindata}_combined_no_sil/valid2/utt2spk $data/${traindata}_combined_no_sil/utt2spk > $data/${traindata}_combined_no_sil/train2/utt2spk
  utils/utt2spk_to_spk2utt.pl $data/${traindata}_combined_no_sil/train2/utt2spk > $data/${traindata}_combined_no_sil/train2/spk2utt
  cp $data/${traindata}_combined_no_sil/feats.scp $data/${traindata}_combined_no_sil/train2
  utils/filter_scp.pl $data/${traindata}_combined_no_sil/train2/utt2spk $data/${traindata}_combined_no_sil/utt2num_frames > $data/${traindata}_combined_no_sil/train2/utt2num_frames
  utils/fix_data_dir.sh $data/${traindata}_combined_no_sil/train2

  awk -v id=0 '{print $1, id++}' $data/${traindata}_combined_no_sil/train2/spk2utt > $data/${traindata}_combined_no_sil/train2/spklist
#  awk -v id=0 '{print $1, id++}' $data/${traindata}_combined_no_sil/valid2/spk2utt > $data/${traindata}_combined_no_sil/valid2/spklist
exit 1
fi


if [ $stage -le 7 -a $skip_train -eq 0 ]; then
# Add attention : Best Performance in voxceleb2_dev case
# Another models : https://github.com/mycrazycracy/tf-kaldi-speaker
nnetdir=$exp/xvector_nnet
nnet/run_train_nnet.sh --cmd "$cuda_cmd" --env tf_gpu --continue-training false nnet_conf/tdnn_amsoftmax_m0.20_linear_bn_1e-2_tdnn4_att.json \
    $data/${traindata}_combined_no_sil/train2 $data/${traindata}_combined_no_sil/train2/spklist \
    $data/${traindata}_combined_no_sil/valid2 $data/${traindata}_combined_no_sil/valid2/spklist \
    $nnetdir

exit 1
echo
fi


nnetdir=$exp/xvector_nnet_pretrained
checkpoint='last'

if [ $stage -le 8 -a $skip_train -eq 0 ]; then
  # Extract the embeddings with ${traindata}_combined_no_sil
  nnet/run_extract_embeddings_no_vad.sh --cmd "$train_cmd" --nj 80 --use-gpu false --checkpoint $checkpoint --stage 0 \
    --chunk-size 10000 --normalize false --node "tdnn6_dense" \
    $nnetdir $data/${traindata}_combined_no_sil $nnetdir/xvectors_${traindata}_combined_no_sil

  nnet/run_extract_embeddings.sh --cmd "$train_cmd" --nj 40 --use-gpu false --checkpoint $checkpoint --stage 0 \
    --chunk-size 10000 --normalize false --node "tdnn6_dense" \
    $nnetdir $data/voxceleb1_test $nnetdir/xvectors_voxceleb1_test

fi

if [ $stage -le 9 -a $skip_train -eq 0 ]; then
  # Cosine similarity
  mkdir -p $nnetdir/scores
  cat $voxceleb1_trials | awk '{print $1, $2}' | \
    ivector-compute-dot-products - \
      "ark:ivector-normalize-length scp:$nnetdir/xvectors_voxceleb1_test/xvector.scp ark:- |" \
      "ark:ivector-normalize-length scp:$nnetdir/xvectors_voxceleb1_test/xvector.scp ark:- |" \
      $nnetdir/scores/scores_voxceleb1_test.cos

  eer=`compute-eer <(local/prepare_for_eer.py $voxceleb1_trials $nnetdir/scores/scores_voxceleb1_test.cos) 2> /dev/null`
  mindcf1=`sid/compute_min_dcf.py --c-miss 10 --p-target 0.01 $nnetdir/scores/scores_voxceleb1_test.cos $voxceleb1_trials 2> /dev/null`
  mindcf2=`sid/compute_min_dcf.py --p-target 0.001 $nnetdir/scores/scores_voxceleb1_test.cos $voxceleb1_trials 2> /dev/null`
  echo "EER: $eer%"
  echo "minDCF(p-target=0.01): $mindcf1"
  echo "minDCF(p-target=0.001): $mindcf2"

fi


if [ $stage -le 10 ]; then
  # Compute the mean vector for centering the evaluation xvectors.
  $train_cmd $nnetdir/xvectors_${traindata}_combined_no_sil/log/compute_mean.log \
    ivector-mean scp:$nnetdir/xvectors_${traindata}_combined_no_sil/xvector.scp \
    $nnetdir/xvectors_${traindata}_combined_no_sil/mean.vec || exit 1;

  # This script uses LDA to decrease the dimensionality prior to PLDA.
  lda_dim=200
  $train_cmd $nnetdir/xvectors_${traindata}_combined_no_sil/log/lda.log \
    ivector-compute-lda --total-covariance-factor=0.0 --dim=$lda_dim \
    "ark:ivector-subtract-global-mean scp:$nnetdir/xvectors_${traindata}_combined_no_sil/xvector.scp ark:- |" \
    ark:$data/${traindata}_combined_no_sil/utt2spk $nnetdir/xvectors_${traindata}_combined_no_sil/transform.mat || exit 1;
#
#  # Train the PLDA model.
#  $train_cmd $nnetdir/xvectors_${traindata}_combined_no_sil/log/plda.log \
#    ivector-compute-plda ark:$data/${traindata}_combined_no_sil/spk2utt \
#    "ark:ivector-subtract-global-mean scp:$nnetdir/xvectors_${traindata}_combined_no_sil/xvector.scp ark:- | transform-vec $nnetdir/xvectors_${traindata}_combined_no_sil/transform.mat ark:- ark:- | ivector-normalize-length ark:-  ark:- |" \
#    $nnetdir/xvectors_${traindata}_combined_no_sil/plda || exit 1;
#fi

#if [ $stage -le 11 ]; then
#  $train_cmd $nnetdir/scores/log/voxceleb1_test_scoring.lda_cos.log \
#    ivector-compute-dot-products "cat '$voxceleb1_trials' | cut -d\  --fields=1,2 |" \
#    "ark:ivector-subtract-global-mean $nnetdir/xvectors_${traindata}_combined_no_sil/mean.vec scp:$nnetdir/xvectors_voxceleb1_test/xvector.scp ark:- | transform-vec $nnetdir/xvectors_${traindata}_combined_no_sil/transform.mat ark:- ark:- | ivector-normalize-length ark:- ark:- |" \
#    "ark:ivector-subtract-global-mean $nnetdir/xvectors_${traindata}_combined_no_sil/mean.vec scp:$nnetdir/xvectors_voxceleb1_test/xvector.scp ark:- | transform-vec $nnetdir/xvectors_${traindata}_combined_no_sil/transform.mat ark:- ark:- | ivector-normalize-length ark:- ark:- |" \
#    $nnetdir/scores/scores_voxceleb1_test.lda_cos || exit 1;

#  $train_cmd $nnetdir/scores/log/voxceleb1_test_scoring.log \
#    ivector-plda-scoring --normalize-length=true \
#    "ivector-copy-plda --smoothing=0.0 $nnetdir/xvectors_${traindata}_combined_no_sil/plda - |" \
#    "ark:ivector-subtract-global-mean $nnetdir/xvectors_${traindata}_combined_no_sil/mean.vec scp:$nnetdir/xvectors_voxceleb1_test/xvector.scp ark:- | transform-vec $nnetdir/xvectors_${traindata}_combined_no_sil/transform.mat ark:- ark:- | ivector-normalize-length ark:- ark:- |" \
#    "ark:ivector-subtract-global-mean $nnetdir/xvectors_${traindata}_combined_no_sil/mean.vec scp:$nnetdir/xvectors_voxceleb1_test/xvector.scp ark:- | transform-vec $nnetdir/xvectors_${traindata}_combined_no_sil/transform.mat ark:- ark:- | ivector-normalize-length ark:- ark:- |" \
#    "cat '$voxceleb1_trials' | cut -d\  --fields=1,2 |" $nnetdir/scores/scores_voxceleb1_test.plda || exit 1;

#  eer=`compute-eer <(local/prepare_for_eer.py $voxceleb1_trials $nnetdir/scores/scores_voxceleb1_test.lda_cos) 2> /dev/null`
#  mindcf1=`sid/compute_min_dcf.py --c-miss 10 --p-target 0.01 $nnetdir/scores/scores_voxceleb1_test.lda_cos $voxceleb1_trials 2> /dev/null`
#  mindcf2=`sid/compute_min_dcf.py --p-target 0.001 $nnetdir/scores/scores_voxceleb1_test.lda_cos $voxceleb1_trials 2> /dev/null`
#  echo "EER: $eer%"
#  echo "minDCF(p-target=0.01): $mindcf1"
#  echo "minDCF(p-target=0.001): $mindcf2"

#  eer=`compute-eer <(local/prepare_for_eer.py $voxceleb1_trials $nnetdir/scores/scores_voxceleb1_test.plda) 2> /dev/null`
#  mindcf1=`sid/compute_min_dcf.py --c-miss 10 --p-target 0.01 $nnetdir/scores/scores_voxceleb1_test.plda $voxceleb1_trials 2> /dev/null`
#  mindcf2=`sid/compute_min_dcf.py --p-target 0.001 $nnetdir/scores/scores_voxceleb1_test.plda $voxceleb1_trials 2> /dev/null`
#  echo "EER: $eer%"
#  echo "minDCF(p-target=0.01): $mindcf1"
#  echo "minDCF(p-target=0.001): $mindcf2"
#fi

if [ $stage -le 13 ]; then
  # Continue training from softmax
  pretrain_nnet=$exp/xvector_nnet_tdnn_amsoftmax_m0.20_linear_bn_1e-2_mhe0.01
  pretrain_ckpt='last'

  nnetdir=$exp/xvector_nnet_tdnn_amsoftmax_m0.20_linear_bn_1e-2_mhe0.01_2
  nnet/run_finetune_nnet.sh --cmd "$cuda_cmd" --env tf_gpu --continue-training false \
    --checkpoint $pretrain_ckpt \
    nnet_conf/tdnn_amsoftmax_m0.20_linear_bn_1e-2_mhe0.01.json \
    $data/${traindata}_combined_no_sil/train $data/${traindata}_combined_no_sil/train/spklist \
    $data/${traindata}_combined_no_sil/softmax_valid $data/${traindata}_combined_no_sil/train/spklist \
    $pretrain_nnet $nnetdir

fi


#nnetdir=$exp/xvector_nnet_tdnn_amsoftmax_m0.20_linear_bn_1e-2_mhe0.01_2
nnetdir=$exp/xvector_nnet_tdnn_amsoftmax_m0.20_linear_bn_1e-2_tdnn4_att_mhe0.01_1
#nnetdir=$exp/xvector_nnet_tdnn_amsoftmax_m0.20_linear_bn_1e-2_tdnn4_att
checkpoint='last'

if [ $stage -le 14 ]; then
#  nnet/run_extract_embeddings.sh --cmd "$train_cmd" --nj 40 --use-gpu false --checkpoint $checkpoint --stage 0 \
#    --chunk-size 10000 --normalize false --node "output" \
#    $nnetdir $data/voxceleb1_test $nnetdir/xvectors_voxceleb1_test
  nnet/run_extract_embeddings_no_vad.sh --cmd "$train_cmd" --nj 80 --use-gpu false --checkpoint $checkpoint --stage 0 \
    --chunk-size 10000 --normalize false --node "output" \
    $nnetdir $data/${traindata}_combined_no_sil $nnetdir/xvectors_${traindata}
fi

if [ $stage -le 15 ]; then
  # Cosine similarity
  mkdir -p $nnetdir/scores
  cat $voxceleb1_trials | awk '{print $1, $2}' | \
    ivector-compute-dot-products - \
      "ark:ivector-normalize-length scp:$nnetdir/xvectors_voxceleb1_test/xvector.scp ark:- |" \
      "ark:ivector-normalize-length scp:$nnetdir/xvectors_voxceleb1_test/xvector.scp ark:- |" \
      $nnetdir/scores/scores_voxceleb1_test.cos

  eer=`compute-eer <(local/prepare_for_eer.py $voxceleb1_trials $nnetdir/scores/scores_voxceleb1_test.cos) 2> /dev/null`
  mindcf1=`sid/compute_min_dcf.py --c-miss 10 --p-target 0.01 $nnetdir/scores/scores_voxceleb1_test.cos $voxceleb1_trials 2> /dev/null`
  mindcf2=`sid/compute_min_dcf.py --p-target 0.001 $nnetdir/scores/scores_voxceleb1_test.cos $voxceleb1_trials 2> /dev/null`
  echo "EER: $eer%"
  echo "minDCF(p-target=0.01): $mindcf1"
  echo "minDCF(p-target=0.001): $mindcf2"

fi
