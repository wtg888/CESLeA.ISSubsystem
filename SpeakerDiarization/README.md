current state

1-1. diarization(offline) : done
1-2. diarization(online) -> working

how to install
1. install KALDI TOOLKIT, python
2. install tensorflow (only use to train new model)
3. setup some virtual env (only use some special model)
4. download pretrain_model https://drive.google.com/drive/folders/1-9iNZPW2uKRzGy-NOs3gqs9f6_07c3kF?usp=sharing
4. copy pretrain_model (speaker_recognition_model,path=diarization/basemodel/)

how to use diarization model
1. check path in diarization/path.sh
2. check dataset path in diarization/preprocess.sh
2. ./configure.sh #exec only one time
3. ./run_train.sh #only use to enroll speakers.
4. ./run_test.sh  #make result in result.txt

