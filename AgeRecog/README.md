current state

1-1. ivector extractor : done
1-2. xvector extractor -> working
1-3. dvector extractor : future

2-1. base recognizer : working
2-2. NN recognizer : working

3-1. online model(baseline model) : done

how to install
1. install KALDI TOOLKIT, python
2. install tensorflow (only use to train new model)
3. setup some virtual env (only use some special model)
4. download pretrained model (https://drive.google.com/drive/folders/1-9iNZPW2uKRzGy-NOs3gqs9f6_07c3kF?usp=sharing)
5. move stored_data folder to recognizer/vox_mix_vector folder
6. move xvector_nnet_pretrain to extractor/Xvector folder
7. also move xvector_nnet_pretrain to online/basemodel folder if you want to use online model

how to use online model
1. check path and change path in online/path.sh if you need.
2. ./configure.sh #exec only one time
3. ./run_train.sh #if your dataset has changed you should run this script.
4. ./run_test.sh  #make result in result.txt

-----------------------------------------------------------------------------------
how to train new model
1. check path in extractor/path.sh

2. edit some parameter
2-1. ivector extractor
edit "run_ivector.sh --skip_train 1" in extractor/run.sh


