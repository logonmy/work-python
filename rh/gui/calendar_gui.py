# !/usr/bin/env python
# -*- coding: utf-8 *-*

from Tkinter import *

root = Tk()
frame = Frame()
Label(master=frame, text='2019年1月', anchor=NW, width=30).pack(side=LEFT)
left_img = PhotoImage(file='imgs/left.gif')
right_img = PhotoImage(file='imgs/right.gif')
bullet_img = PhotoImage(file='imgs/bullet.gif')
Button(master=frame, image=right_img).pack(side=RIGHT)
Button(master=frame, image=bullet_img).pack(side=RIGHT)
Button(master=frame, image=left_img).pack(side=RIGHT)
frame.pack(anchor='w', padx=10, pady=10)

frame = Frame(bd=2, relief=GROOVE, highlightcolor='blue')
week_days = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
for i, d in enumerate(week_days):
    Label(master=frame, text=d, width=5).grid(row=0, column=i)
row = 1
column = 0
for i in range(1, 32):
    label = Label(master=frame, text=i, width=5)
    label.bind('<Enter>', func=lambda _: label.configure(relief=GROOVE))
    label.grid(row=row, column=column)
    column += 1
    if column == 7:
        column = 0
        row += 1
frame.pack(side=BOTTOM, padx=10, pady=10)

root.mainloop()
