import os
import sys

f=open(sys.argv[1]+"/result_frame.txt",'r')
lines=f.readlines()
f2=open(sys.argv[1]+"/frame_label.txt",'w')
for i in range(len(lines)):
    blist=lines[i].split(' ')
    alist=blist[0].split('_')
    spkr1=alist[1]
    spkr2=alist[2]
    changetime=int(alist[3])*2
    currenttime=int(alist[4])*750+750
    if changetime > currenttime :
        f2.write(blist[0]+' '+spkr1+'\n')
    else:
        f2.write(blist[0]+' '+spkr2+'\n')

f2.close
f.close
