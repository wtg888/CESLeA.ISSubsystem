# -*- coding: utf-8 -*-
import queue
import threading
from tkinter import *
import flask_fn

stream = queue.Queue()
speechQ = queue.Queue()
count = 0


def main():
    root = Tk()
    root.geometry("1500x500")
    root.title('Result')

    lbl = Label(root, text="")
    lbl.config()
    lbl.config(width=50)
    lbl.config(font=("Courier", 44))
    lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

    ths = list()
    ths.append(threading.Thread(target=flask_fn.run_app))
    for th in ths:
        th.daemon = True
        th.start()

    root.mainloop()


if __name__ == '__main__':
    main()
