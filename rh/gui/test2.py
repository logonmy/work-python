#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *

# 初始化Tk()
myWindow = Tk()
# 设置标题
myWindow.title('Python GUI Learning')

scrollbar = Scrollbar(myWindow)
scrollbar.pack(side=RIGHT, fill=Y)

mylist = Listbox(myWindow, yscrollcommand=scrollbar.set)
for line in range(100):
    mylist.insert(END, "This is line number " + str(line))

mylist.pack(side=LEFT, fill=BOTH)
scrollbar.config(command=mylist.yview)
# 进入消息循环
myWindow.mainloop()