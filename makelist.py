import os
d = dict()

# your audio data folder
fs = os.listdir("")

fps = (open("speaker_recog/ceslea_data/mm.list", "w"), 
    open("speaker_recog/ceslea_data/nm.list", "w"), 
    open("speaker_recog/ceslea_data/train_test.list", "w"), 
    open("speaker_recog/ceslea_data/test.list", "w"), 
    open("speaker_recog/ceslea_data/map.list", "w"),
    open("speaker_recog/ceslea_data/train.list", "w"))

for idx, f in enumerate(fs):
    files = os.listdir("speaker_recog/ceslea_data/" + f)
    fps[0].write("N%d\n"%idx)
    fps[1].write("N%d\n"%idx)
    fps[4].write("%d %s\n"%(idx,f))
    for i, x in enumerate(files):
        if i % 5 == 0:
            fps[3].write("N%d ./%s/%s\n"%(idx, f, x))
        else:
            fps[2].write("N%d ./%s/%s\n"%(idx, f, x))
    fps[5].write("N%d ./%s/%s\n"%(idx, f, x))

for f in fps:
    f.close()