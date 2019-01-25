#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
import time

def click():
    mylist.insert(END, 'now is %s\n' % time.time())
    # scrollbar.set(0.8, 1)
    # mylist.yview_moveto(1)

# 初始化Tk()
myWindow = Tk()
# 设置标题
myWindow.title('Python GUI Learning')

scrollbar = Scrollbar(myWindow)
scrollbar.pack(side=RIGHT, fill=Y)

mylist = Text(myWindow, wrap=WORD, yscrollcommand=scrollbar.set)
s = """This is line number 
        hwejlkjeg %s
 """
for line in range(100):
    mylist.insert(END, s % str(line))

mylist.pack(side=LEFT, fill=BOTH)
scrollbar.config(command=mylist.yview)

btn = Button(myWindow, text='点我', command=click)
btn.pack(side=BOTTOM, fill=X)
# 进入消息循环
myWindow.mainloop()