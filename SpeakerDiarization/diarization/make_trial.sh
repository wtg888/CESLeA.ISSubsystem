#!/bin/bash

. ./cmd.sh
. ./path.sh
set -e

if [ $# != 1 ]; then
  echo "Usage: $0 <dir>"
  echo "e.g.: $0 /dir/..."
  exit 1;
fi

nnetdir=$1

cat $nnetdir/xvector.scp | while read line
do
  key1=`echo $line | cut -d' ' -f1`
  cat $nnetdir/../xvectors/spk_xvector.scp | while read line2
  do
    key2=`echo $line2 | cut -d' ' -f1`
    newkey=${key2}' '${key1}
    echo $newkey >> $nnetdir/trials.txt
  done
done
