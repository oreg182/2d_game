from tkinter import *


class Mybutton(Widget):
    def __init__(self, idnr, coord:tuple, master, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        self.idnr = idnr
        self.x_coord = coord[0]
        self.y_coord = coord[1]
        Widget.__init__(self, master, 'button', cnf, kw)


class _Infoframe(Frame):
    def __init__(self, master, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        Frame.__init__(self, master, cnf, **kw)


if __name__ == '__main__':
    root = Tk()
    f = _Infoframe(root)
    b1 = Button(f).pack()
    f.pack()
    mainloop()
