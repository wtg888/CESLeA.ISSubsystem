"""
this code uses Python's hmmlearn library to implement HMM.
"""
import numpy as np
import os
from speaker_recog.wav2features import wav2mfcc
from sklearn.externals import joblib

np.set_printoptions(threshold=25000)


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

hmmfile = 'hmm_spr.pkl'

if os.path.exists(hmmfile):
    hmms = joblib.load("hmm_spr.pkl")
    print(hmms[1])
else:
    print('no pickle file')
    exit(1)

testdata = []
num_samples = 0
num_correct = 0
num_wrong = 0
for ii in range(len(names)):
    path = ('test/%s'% names[ii])
    fname = os.listdir('test/%s'% names[ii])
    for jj in range(len(fname)):
        name = os.path.join(path,fname[jj])
        print(name)
        mcep, fs, x = wav2mfcc(name, target_fs, winlen, winstep, nfilt, numcep)
        pout = []
        for k in range(len(hmms)):
            po = hmms[k].score(mcep)
            pout.append(po)
        max_value = max(pout)
        max_index = pout.index(max_value)
        num_samples = num_samples+1
        if ii == max_index:
            num_correct = num_correct+1
        if ii!= max_index:
            print ("speaker %s is recognized as %s" % (ii,max_index))
            num_wrong = num_wrong+1

accuracy = (num_correct/num_samples)*100
print('numcorrect %s',num_correct)
print('wrong %s ',num_wrong)
print("test data accuracy = %s" %accuracy)
