import os
import sys

totaltime=int(sys.argv[2])
shifttime=int(sys.argv[3])

f=open(sys.argv[1]+"/result_frame.txt",'r')
lines=f.readlines()
f2=open(sys.argv[1]+"/frame_label.txt",'r')
lines2=f2.readlines()
f3=open(sys.argv[1]+"/result.txt",'w')
score=0
total_time=int(len(lines))*shifttime+(totaltime/2)
for i in range(len(lines)):
    alist=lines[i].split(' ')
    blist=lines2[i].split(' ')
    spkr_t=alist[1]
    spkr_l=blist[1]
    if spkr_t==spkr_l:
        score=score+shifttime

f3.write("correct time : "+str(score)+'(ms)\n')
f3.write("total time : "+str(total_time)+'(ms)\n')
f3.write("IOU : "+str((score*100)/total_time)+'%\n')
f3.close
f2.close
f.close
