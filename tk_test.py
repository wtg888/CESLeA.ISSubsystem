from tkinter import *


def close_cmd(tl):
    tl.destroy()
    # tl.quit()


def command():
    tl = Toplevel(root)
    bt1 = Button(tl, text="close", command=lambda : close_cmd(tl))
    bt1.pack()


if __name__ == '__main__':
    root = Tk()
    bt1 = Button(root, text="사용자 등록", command=command)
    bt1.pack()
    try:
        root.mainloop()
    except:
        pass
