import os
import sys

num_spkr=int(sys.argv[2])
f=open(sys.argv[1]+"/scores.cos",'r')
lines=f.readlines()
f2=open(sys.argv[1]+"/result_frame.txt",'w')
for i in range(len(lines)/num_spkr):
    start=i*num_spkr
    firstlist=lines[start].split(' ')
    spkr=firstlist[0]
    utt=firstlist[1]
    cos=firstlist[2]
    for ii in range(1,num_spkr):
        sublist=lines[start+ii].split(' ')
        if float(sublist[2][:-1]) > float(cos[:-1]):
            cos=sublist[2]
            spkr=sublist[0]
    if float(cos) < 0.0:
        spkr="unknown"
    f2.write(utt+' '+spkr+'\n')
f2.close
f.close
