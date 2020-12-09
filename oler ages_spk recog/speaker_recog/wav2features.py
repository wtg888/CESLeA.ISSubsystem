from scipy.io import wavfile
from scipy import signal
import numpy as np
import python_speech_features as psf


# read wav file with given sampling rate
def wavreadmono(filename, target_fs):
    # read wav file
    fs, sig = wavfile.read(filename)
    
    # merge left and right channels, if necessary
    if len(sig.shape) > 1 :
        sig = np.average(sig,1)
        
    # resample to target_fs
    if fs != target_fs :
        newsize = np.int(np.float(len(sig))/np.float(fs)*np.float(target_fs))
        sig = signal.resample(sig,newsize,None,0)
        fs = target_fs

    return fs, sig


# log powerspectra of short-time Fourier transform
def wav2spect(filename, target_fs=16000, winlen=0.025, winstep=0.01):
    fs, sig = wavreadmono(filename, target_fs)
    
    # segment input 1-D signal into 0.025 sec frames
    frame_len = np.int(np.float(fs)*winlen)
    frame_step = np.int(np.float(fs)*winstep)
    sig = psf.sigproc.preemphasis(sig,0.97)
    frames = psf.sigproc.framesig(sig,frame_len,frame_step,np.hamming)
    lp = psf.sigproc.logpowspec(frames,frame_len)

    return lp, fs, sig


# log filterbank energies
def wav2logfilteng(filename, target_fs=16000, winlen=0.025, winstep=0.01, nfilt=29):
    fs, sig = wavreadmono(filename, target_fs)
    
    # log filterbank energies
    frame_len = np.int(np.float(fs)*winlen)
    nfft = np.int(2**np.ceil(np.log2(frame_len)))   # closest 2's power
    lfe = psf.logfbank(sig,fs,winlen,winstep,nfilt,nfft)

    return lfe, fs, sig


# we used mfcc as features in this project
# mfcc + delta + double delta
def wav2mfcc(filename, target_fs=16000, winlen=0.025, winstep=0.01, nfilt=29, numcep=13 ):
    fs, sig = wavreadmono(filename, target_fs)
    
    frame_len = np.int(np.float(fs)*0.025)
    nfft = np.int(2**np.ceil(np.log2(frame_len)))   # closest 2's power
    x = psf.mfcc(sig,fs,winlen,winstep,numcep,nfilt,nfft)
    dx = psf.delta(x,1)   # delta frames over 3 frames
    ddx = psf.delta(dx,1) # delta-delta frames over 3 delta frames (5 frames)
    y = np.concatenate([x,dx],axis=1)
    z = np.concatenate([y,ddx],axis=1)
    return z, fs, sig

