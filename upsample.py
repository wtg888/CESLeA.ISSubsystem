import os

d = [x for x in os.listdir('/home/mi/PycharmProjects/CESLeA/300wav_sorted')]

os.mkdir('300wav_upsample')

for x in d:
    os.mkdir(os.path.join('300wav_upsample', x))
    if x == 'test':
        l = os.listdir(os.path.join('300wav_sorted', x))
        for xx in l:
            os.system('sox 300wav_sorted/%s/%s -r 16000 300wav_upsample/%s/%s'
                      %(x, xx, x, xx))

    else:
        for xx in os.listdir(os.path.join('300wav_sorted', x)):
            l = os.listdir(os.path.join('300wav_sorted', x, xx))
            os.mkdir(os.path.join('300wav_upsample', x, xx))
            for xxx in l:
                os.system('sox 300wav_sorted/%s/%s/%s -r 16000 300wav_upsample/%s/%s/%s'
                          % (x, xx, xxx, x, xx, xxx))