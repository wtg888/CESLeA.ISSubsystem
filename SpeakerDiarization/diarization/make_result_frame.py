import os
import sys

f=open(sys.argv[1]+"/scores.cos",'r')
lines=f.readlines()
f2=open(sys.argv[1]+"/result_frame.txt",'w')
for i in range(len(lines)/10):
    start=i*10
    firstlist=lines[start].split(' ')
    spkr=firstlist[0]
    utt=firstlist[1]
    cos=firstlist[2]
    for ii in range(1,10):
        sublist=lines[start+ii].split(' ')

        if float(sublist[2][:-1]) > float(cos[:-1]):
            cos=sublist[2]
            spkr=sublist[0]
    f2.write(utt+' '+spkr+'\n')
f2.close
f.close
