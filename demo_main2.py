# -*- coding: utf-8 -*-
import queue
import threading
import os
from tkinter import *
from message import decode_msg_size


msgQ = queue.Queue()
count = 0
pre_txt = ''

IPC_FIFO_NAME = 'ipc'
fifo = os.open(IPC_FIFO_NAME, os.O_CREAT | os.O_RDONLY)


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


def change_queue(stt_lbl, spk_lbl, env_lbl):
    global pre_txt
    while True:
        try:
            type, text = msgQ.get()
            if type == 'stt':
                stt_lbl.config(text=text)
            elif type == 'spk':
                pre_txt = text
                spk_lbl.config(text=text+'\n\n'+pre_txt)
            elif type == 'env':
                env_lbl.config(text=text)
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

    env_lbl = Label(root, text="env")
    env_lbl.config()
    env_lbl.config(width=50) #, borderwidth=2, relief="groove")
    env_lbl.config(font=("Courier", 55, 'bold'))
    env_lbl.place(relx=0.5, rely=0.90, anchor=CENTER)

    ths = list()
    ths.append(threading.Thread(target=read_thd))
    ths.append(threading.Thread(target=change_queue, args=(stt_lbl, spk_lbl, env_lbl)))
    for th in ths:
        th.daemon = True
        th.start()

    root.mainloop()


if __name__ == '__main__':
    main()
