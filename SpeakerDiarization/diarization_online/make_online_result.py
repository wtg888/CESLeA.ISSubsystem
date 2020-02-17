import os
import sys

windowtime=int(sys.argv[2])
shifttime=int(sys.argv[3])

f=open(sys.argv[1]+"/result_frame.txt",'r')
lines=f.readlines()
f3=open(sys.argv[1]+"/result.txt",'w')
current_time=0
total_time=(int(len(lines))-1)*shifttime+(windowtime)
past_spkr="none"
pastpast_spkr="none"
last_spkr="none"
for i in range(len(lines)):
    alist=lines[i].split(' ')
    spkr=alist[1]
    if pastpast_spkr!=past_spkr:
        if past_spkr==spkr:
            if last_spkr!=spkr:
                f3.write(str(current_time-shifttime)+'\n'+spkr)
                last_spkr=spkr
    elif len(lines)-1==i:
        if past_spkr==spkr:
            if last_spkr!=spkr:
                f3.write(str(current_time)+'\n'+spkr)
#       if past_spkr=="none":
#            f3.write("0\n"+spkr)
#        else:
#            f3.write(str(current_time)+'\n'+spkr)
    current_time=current_time+shifttime
    pastpast_spkr=past_spkr
    past_spkr=spkr

f3.close
f.close
