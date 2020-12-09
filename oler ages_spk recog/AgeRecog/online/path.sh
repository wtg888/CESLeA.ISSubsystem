# The virtualenv path
export TF_ENV=/home/mi/data/venv

export PROJECT_ROOT=/home/mi/PycharmProjects/CESLeA/AgeRecog/online
export DATA_ROOT=/home/mi/PycharmProjects/CESLeA/300wav_upsample
export KALDI_ROOT=/media/mi/data/tools/kaldi
export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$KALDI_ROOT/tools/sph2pipe_v2.5:$PWD:$PATH
[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "The standard file $KALDI_ROOT/tools/config/common_path.sh is not present -> Exit!" && exit 1
. $KALDI_ROOT/tools/config/common_path.sh
export LC_ALL=C
