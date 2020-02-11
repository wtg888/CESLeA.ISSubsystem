# The virtualenv path
export TF_ENV=/home/craftkim/venv

export PROJECT_ROOT=/home/craftkim/projects/SpeakerDiarization/diarization
export DATA_ROOT=/home/craftkim/dataset/diarization_dataset/speaker_enrollment_wav
export TESTDATA_ROOT=/home/craftkim/dataset/diarization_dataset/test
export KALDI_ROOT=/home/craftkim/SD/kaldi-master
export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$KALDI_ROOT/tools/sph2pipe_v2.5:$PWD:$PATH
[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "The standard file $KALDI_ROOT/tools/config/common_path.sh is not present -> Exit!" && exit 1
. $KALDI_ROOT/tools/config/common_path.sh
export LC_ALL=C
