import os
import sys

windowtime=int(sys.argv[2])
shifttime=int(sys.argv[3])

f=open(sys.argv[1]+"/result_frame.txt",'r')
lines=f.readlines()
f3=open(sys.argv[1]+"/result.txt",'w')
current_time=windowtime/2
total_time=(int(len(lines))-1)*shifttime+(windowtime)
past_spkr="none"
for i in range(len(lines)):
    alist=lines[i].split(' ')
    spkr=alist[1]
    if spkr!=past_spkr:
        if past_spkr=="none":
            f3.write("0\n"+spkr)
        else:
            f3.write(str(current_time)+'\n'+spkr)
    current_time=current_time+shifttime
    past_spkr=spkr

f3.close
f.close
