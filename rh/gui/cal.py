import calendar_gui
from Tkinter import *

gui = Tk()
gui.title("CALENDAR_RIZ")

def cal():
    year = e1.get()
    month = e2.get()
    cal_x = calendar_gui.month(int(year), int(month), w = 2, l = 1)
    print (cal_x)
    cal_out = Label(gui, text=cal_x, font=('courier', 12, 'bold'), bg='lightblue')
    cal_out.pack(padx=30, pady=40)

label1 = Label(gui, text="ENTER YEAR:")
label1.pack()

e1 = Entry(gui)
e1.pack()

label2 = Label(gui, text="ENTER MONTH:")
label2.pack()

e2 = Entry(gui)
e2.pack()

button = Button(gui, text="CLICK HERE ",command=cal)
button.pack()

gui.mainloop()