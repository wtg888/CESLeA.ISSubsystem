# -*- coding: utf-8 -*-
import queue
import threading
import os
from tkinter import *
from message import decode_msg_size
import requests
import win32com.client
import playsound
import time


def tts(text):
    tts = win32com.client.Dispatch("SAPI.SpVoice")
    tts.Speak(text)


msgQ = queue.Queue()
count = 0
pre_txt = ''
speaker = ''
IPC_FIFO_NAME = 'ipc'
fifo = os.open(IPC_FIFO_NAME, os.O_CREAT | os.O_RDONLY)


URL = 'http://192.168.1.115:8080/iss'


def post_res(text, spk):
    try:
        res = requests.post(URL, data={'text': text, 'speaker':spk})
    except:
        pass


def get_message():
    """Get a message from the named pipe."""
    msg_size_bytes = os.read(fifo, 4)
    while len(msg_size_bytes) < 4:
        msg_size_bytes += os.read(fifo, 4 - len(msg_size_bytes))
    msg_size = decode_msg_size(msg_size_bytes)
    msg_content = os.read(fifo, msg_size)
    while len(msg_content) < msg_size:
        msg_content += os.read(fifo, 4 - len(msg_content))
    return msg_content.decode("utf8").split('\t')


def read_thd():
    while True:
        msg = get_message()
        print(msg)
        msgQ.put_nowait(msg)


def change_queue(stt_lbl, spk_lbl):
    global pre_txt
    global speaker
    while True:
        try:
            type, text = msgQ.get()
            if type == 'stt':
                stt_lbl.config(text=text.replace('f', '') + '\n\n' + pre_txt)
                if text[-1] == 'f':
                    text = text[:-1]
                    pre_txt = text
                    post_res(text, speaker)
            elif type == 'spk':
                spk_lbl.config(text=text)
                speaker = text
            elif type == 'tts':
                tts(text)
        except queue.Empty:
            continue


def main():
    root = Tk()
    root.geometry("1500x1200")
    root.title('Result')

    stt_lbl = Label(root, text="text")
    stt_lbl.config()
    stt_lbl.config(width=50, height=8) #, borderwidth=2, relief="groove")
    stt_lbl.config(wraplength=1550)
    stt_lbl.config(font=("Courier", 50, 'bold'))
    stt_lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

    spk_lbl = Label(root, text="spk\npre_spk")
    spk_lbl.config()
    spk_lbl.config(width=50, height=2) #, borderwidth=2, relief="groove")
    spk_lbl.config(font=("Courier", 55, 'bold'))
    spk_lbl.place(relx=0.5, rely=0.10, anchor=CENTER)

    ths = list()
    ths.append(threading.Thread(target=read_thd))
    ths.append(threading.Thread(target=change_queue, args=(stt_lbl, spk_lbl)))
    for th in ths:
        th.daemon = True
        th.start()

    root.mainloop()


if __name__ == '__main__':
    main()
