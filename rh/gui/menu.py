#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as Tk
import tkFont
import tkFileDialog as filedialog
from tkfilebrowser import askopendirname, askopenfilenames, asksaveasfilename
import time


class Application(Tk.Frame):
    WIDTH = 640
    HEIGHT = 480
    root = None

    def __init__(self, **kwargs):
        # Create window
        self.root = Tk.Tk()

        # Init master frame
        Tk.Frame.__init__(self, self.root, width=self.WIDTH, height=self.HEIGHT)
        self.grid(column=0, row=0)
        # self.grid_propagate(0)

        # Frame
        # frame_com_ports = DIV_Frame(self, 0, '任务源数据入库', width=self.WIDTH, height=self.HEIGHT / 3)
        # Tk.Label(frame_com_ports, text='选择文件').grid(column=0, row=1, sticky='EW', pady=3, padx=3)
        # Tk.Button(frame_com_ports, text="Open files", command=self.c_open_file_old).grid(row=1, column=2, padx=4, pady=4, sticky='ew')
        # Tk.Button(frame_com_ports, text="导入", command=self.change_log).grid(row=1, column=3, padx=4, pady=4, sticky='ew')
        # self.spamVar = Tk.StringVar()

        # scrollbar = Tk.Scrollbar(frame_com_ports)
        # scrollbar.pack(side=Tk.BOTTOM, fill=Tk.Y)

        self.yScroll = Tk.Scrollbar(self, orient=Tk.VERTICAL)
        self.yScroll.grid(row=0, column=1, sticky=Tk.N + Tk.S)

        self.xScroll = Tk.Scrollbar(self, orient=Tk.HORIZONTAL)
        self.xScroll.grid(row=1, column=0, sticky=Tk.E + Tk.W)

        self.listbox = Tk.Listbox(self,
                                  xscrollcommand=self.xScroll.set,
                                  yscrollcommand=self.yScroll.set)

        s = """
        This is line number
         ,,,
         here is the left ...
        """
        for line in range(100):
            self.listbox.insert(Tk.END, s + str(line))

        self.listbox.grid(row=0, column=0, sticky=Tk.N + Tk.S + Tk.E + Tk.W)
        self.xScroll['command'] = self.listbox.xview
        self.yScroll['command'] = self.listbox.yview

        # msg = Tk.Message(frame_com_ports, text='', textvariable=self.spamVar, bg='black', fg='white',
        #                  yscrollcommand=scrollbar.set)
        # msg.grid(row=2, column=0, columnspan=5, sticky='ew')

        # frame_com_ports1 = DIV_Frame(self, 1, '别名核实任务', width=self.WIDTH, height=self.HEIGHT / 3)
        # frame_com_ports1 = DIV_Frame(self, 2, 'TC核实任务', width=self.WIDTH, height=self.HEIGHT / 3)

    def change_log(self):
        self.spamVar.set("hello now is %s" % time.time())

    @staticmethod
    def c_open_file_old():
        rep = filedialog.askopenfilenames(parent=Application.root, initialdir='/', initialfile='tmp',
                                          filetypes=[("CSV", "*.csv"), ("TXT", "*.txt"), ("All files", "*")])
        print(rep)

    @staticmethod
    def import_data():
        print 'import begin'


class DIV_Frame(Tk.Frame):
    def __init__(self, parent, row, label, **kwargs):
        kwargs.update({'borderwidth': 2, 'relief': Tk.SOLID})
        Tk.Frame.__init__(self, parent, kwargs)

        # Widgets
        self.txt_ports = Tk.Label(self, text=label, font=(20))
        self.txt_ports.grid(column=0, row=0, sticky='EW', pady=3, padx=3)

        self.grid(column=0, row=row, sticky='EW')
        self.grid_propagate(0)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
