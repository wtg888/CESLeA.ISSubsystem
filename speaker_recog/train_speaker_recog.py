"""
this code uses Python's hmmlearn library to implement HMM.
"""
from hmmlearn import hmm
import numpy as np
import os
from speaker_recog.wav2features import wav2mfcc
import warnings
from sklearn.externals import joblib
from speaker_recog.utils import tr

np.set_printoptions(threshold = 25000)

"""
https://stackoverflow.com/questions/14463277/how-to-disable-python-warnings
"""
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")


def sample_process(sample, temp_len):
    temp_len_new = []
    A = sample
    print('len',len(sample))
    for i in range(1):
        temp_len_new = np.append(len(sample[i]), (len(sample[i + 1]), len(sample[i + 2]), len(sample[i + 3]), len(sample[i + 4]), len(sample[i + 5]), len(sample[i + 6])))

    data = np.concatenate([A[i] for i in range(len(sample))])

    temp_len_new = np.array(temp_len_new, dtype=int)
    return temp_len_new, data, A


target_fs = 16000
winlen = 0.025
winstep = 0.01
nfilt = 29
numcep = 13

f = open('name.list', 'r')
names = [x for x in f.read().split('\n') if x != '']
f.close()

traindata = []
for ii in range(len(names)):
        temp = []
        path = ('train/%s'%(names[ii]))
        fname = os.listdir('train/%s'%(names[ii]))
        for jj in range(len(fname)):
            name = os.path.join(path,fname[jj])
            mcep, fs, x = wav2mfcc(name, target_fs, winlen, winstep, nfilt, numcep)
            tmp_dict = { "mcep": mcep, "fname":name}
            temp.append(tmp_dict)
        temp = np.array(temp)
        traindata.append(temp)

hmmfile = 'hmm_spr.pkl'
istrain = True
if(os.path.exists(hmmfile))==True:
  prompt = (print('file %s exists, train (will replace)?[y/n]'% (hmmfile)))
  a = input()
  if a == 'y':
    istrain = True
  if a!= 'y' :
      istrain = False
      print("istrain = %s , samples will be recognized using previously trained model " % istrain)
      hmms = joblib.load("hmm_spr.pkl")

#start building hmm for each digit

if istrain == True:
  hmms = []
  #states = []
  #fr_pr = []
  for ii in range(len(traindata)):
    #print(len(traindata[ii]))
    sample_in = []
    #print('training by (')
    len_temp = []
    for jj in range(len(traindata[ii])):
      temp = {}
      temp = traindata[ii][jj]["mcep"]
      #print(traindata[ii][jj]["fname"])
      len_temp.append(len(temp))
      sample_in.append(temp)
    len_temp, sample,sample_in = sample_process(sample_in,len_temp)
    #print(len(sample_in))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        h_temp = hmm.GaussianHMM(n_components=16, tol = 0.000001, covariance_type = 'diag',algorithm = 'viterbi', n_iter=1000, verbose = True)
        #h_temp.stratprob_prior = [0 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0]
        # h_temp.transmat_prior = tr
        h_temp.fit(sample,len_temp)

    hmms.append(h_temp)
    #print(')\n')
    joblib.dump(hmms, "hmm_spr.pkl")


#start recognising train samples

print('recognizing training samples')
err_list = []
num_correct = 0
num_samples = 0
num_wrong = 0
for ii in range (len(traindata)):
    for jj in range(len(traindata[ii])):
        mcep = traindata[ii][jj]["mcep"]
        fname = traindata[ii][jj]["fname"]

        print(fname)
        pout = []
        for k in range(len(hmms)):
            po = hmms[k].score(mcep)
            pout.append(po)
        max_value = max(pout)

        max_index = pout.index(max_value)
        num_samples = num_samples+1
        if ii == max_index:
            num_correct = num_correct+1
        if ii != max_index:
            print ("speaker %s is recognized as %s" % (names[ii],names[max_index]))
            err_list.append("speaker %s is recognized as %s" % (names[ii],names[max_index]))
            num_wrong = num_wrong+1
accuracy = (num_correct/num_samples)*100
print("training accuracy = %s " %accuracy)
print("correct = %s " %num_correct)
print("wrong = %s " %num_wrong)
for err in err_list:
    print(err)

#recognize test samples

# print('recognizing test samples')
# num_correct = 0
# num_samples = 0
# num_wrong = 0
#
# testdata = []
# for ii in range(len(names)):
#     path = ('test/%s'% names[ii])
#     fname = os.listdir('test/%s'% names[ii])
#     for jj in range(len(fname)):
#         name = os.path.join(path,fname[jj])
#         print(name)
#         mcep, fs, x = wav2mfcc(name, target_fs, winlen, winstep, nfilt, numcep)
#         pout = []
#         for k in range(len(hmms)):
#             po = hmms[k].score(mcep)
#             pout.append(po)
#         max_value = max(pout)
#         max_index = pout.index(max_value)
#         num_samples = num_samples+1
#         if ii == max_index:
#             num_correct = num_correct+1
#         if ii!= max_index:
#             print ("speaker %s is recognized as %s" % (ii,max_index))
#             num_wrong = num_wrong+1
# if num_samples:
#     accuracy = (num_correct/num_samples)*100
#     print('numcorrect %s',num_correct)
#     print('wrong %s ',num_wrong)
#     print("test data accuracy = %s" %accuracy)
