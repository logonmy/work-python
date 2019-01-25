#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
import tkFileDialog as filedialog
import ScrolledText
from rh.util import StoppableThread

FRAME_BG = '#333'
FILE_LABEL_INIT_TEXT = u'未选择任何文件'


class Application:
    def __init__(self):
        self.root = Tk()
        self.root.title('简易程序')
        self.button_frame_dict = {}
        self.log_text = None
        self.import_data_label_text = StringVar(self.root, value=FILE_LABEL_INIT_TEXT)
        self.init_body()
        self.actions = None
        self.current_thread = None

    def mainloop(self):
        if self.actions is None:
            raise Exception('没有注入业务actions，无法启动')
        self.root.mainloop()

    def init_body(self):
        button_frame = Frame(self.root, relief=SUNKEN, bd=4)
        button_frame.grid(row=0, column=0, padx=2, pady=2, sticky='we')
        # 三个按钮
        bt1 = self.create_button(button_frame, '任务源数据入库')
        bt2 = self.create_button(button_frame, '别名核实任务')
        bt3 = self.create_button(button_frame, 'TC核实任务')

        # 输入Frame
        action_frame = Frame(self.root, width=500, height=200, relief=SUNKEN, bd=4, bg=FRAME_BG)
        action_frame.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")

        Button(action_frame, text="选择文件", command=self.open_file).grid(row=0, column=0, padx=4, pady=4, sticky='ew')
        Label(action_frame, width=30, textvariable=self.import_data_label_text).grid(column=1, row=0, sticky='EW')
        Button(action_frame, text="导入", command=self._import_origin_data).grid(row=0, column=2, padx=4, pady=4,
                                                                               sticky='ew')
        self.button_frame_dict[bt1] = action_frame

        action_frame = Frame(self.root, width=500, height=200, relief=SUNKEN, bd=4, bg=FRAME_BG)
        action_frame.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
        Label(action_frame, text='制作BM任务').grid(column=0, row=0, padx=2, pady=2, sticky='EW')
        Label(action_frame, text='开始日期').grid(column=0, row=1, padx=2, pady=2, sticky='EW')
        Entry(action_frame).grid(column=1, row=1, padx=2, pady=2, sticky='EW')
        Label(action_frame, text='截止日期').grid(column=2, row=1, padx=2, pady=2, sticky='EW')
        Entry(action_frame).grid(column=3, row=1, padx=2, pady=2, sticky='EW')
        Button(action_frame, text="执行", command=self._import_origin_data).grid(row=1, column=4, padx=2, pady=2,
                                                                               sticky='ew')

        Label(action_frame, text='回收结果入库').grid(column=0, row=2, padx=2, pady=2, sticky='EW')
        Button(action_frame, text="选择文件", command=self.open_file).grid(row=3, column=0, padx=4, pady=4, sticky='ew')
        Label(action_frame, width=30, textvariable=self.import_data_label_text).grid(column=1, row=3, sticky='EW')
        Button(action_frame, text="导入", command=self._import_origin_data).grid(row=3, column=2, padx=4, pady=4,
                                                                               sticky='ew')
        self.button_frame_dict[bt2] = action_frame

        action_frame = Frame(self.root, width=500, height=200, relief=SUNKEN, bd=4, bg=FRAME_BG)
        action_frame.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
        Label(action_frame, text='制作TC任务').grid(column=0, row=0, padx=2, pady=2, sticky='EW')
        Label(action_frame, text='开始日期').grid(column=0, row=1, padx=2, pady=2, sticky='EW')
        Entry(action_frame).grid(column=1, row=1, padx=2, pady=2, sticky='EW')
        Label(action_frame, text='截止日期').grid(column=2, row=1, padx=2, pady=2, sticky='EW')
        Entry(action_frame).grid(column=3, row=1, padx=2, pady=2, sticky='EW')
        Button(action_frame, text="执行", command=self._import_origin_data).grid(row=1, column=4, padx=2, pady=2,
                                                                               sticky='ew')

        Label(action_frame, text='回收结果入库').grid(column=0, row=2, padx=2, pady=2, sticky='EW')
        Button(action_frame, text="选择文件", command=self.open_file).grid(row=3, column=0, padx=4, pady=4, sticky='ew')
        Label(action_frame, width=30, textvariable=self.import_data_label_text).grid(column=1, row=3, sticky='EW')
        Button(action_frame, text="导入", command=self._import_origin_data).grid(row=3, column=2, padx=4, pady=4,
                                                                               sticky='ew')
        self.button_frame_dict[bt3] = action_frame

        # 中间
        output_label = Label(self.root, text='日志：')
        output_label.grid(row=2, column=0, sticky="nw")

        # 日志Frame
        log_frame = Frame(self.root, width=500, height=400, relief=SUNKEN, bd=4, bg=FRAME_BG)
        log_frame.grid(row=3, column=0, padx=2, pady=2, sticky="nsew")
        log_text = ScrolledText.ScrolledText(log_frame, bg=FRAME_BG, fg="white")
        log_text.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        # # 滚动条
        # scrollbar = Scrollbar(log_frame)
        # # 日志输出文本框
        # log_text = Text(log_frame, wrap=WORD, bg=FRAME_BG, fg="white", yscrollcommand=scrollbar.set)
        # log_text.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        # scrollbar.config(command=log_text.yview)
        # scrollbar.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")

        Button(self.root, text="停止", command=self.stop_thread).grid(row=4, column=0, padx=2, pady=2)

        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.log_text = log_text
        bt1.invoke()

    def create_button(self, master, text):
        btn = Button(master, text=text, font=(None, 12))
        btn.configure(command=lambda r=btn: self.click_button(r))
        btn.pack(side=LEFT, padx=2, pady=2)
        return btn

    def click_button(self, obj):
        for btn, frame in self.button_frame_dict.items():
            if btn == obj:
                btn.configure(bg='#23527c', fg='#cc9933')
                frame.grid()
            else:
                btn.configure(bg='#FFF', fg='#000')
                frame.grid_remove()

    def open_file(self):
        rep = filedialog.askopenfilenames(parent=self.root, initialdir='/', initialfile='tmp',
                                          filetypes=[("CSV", "*.csv"), ("TXT", "*.txt"), ("All files", "*")])
        self.import_data_label_text.set(rep[0])

    def _import_origin_data(self):
        file_name = self.import_data_label_text.get()
        if file_name and file_name != FILE_LABEL_INIT_TEXT:
            # self.actions.import_origin_data.main(file_name)
            t = StoppableThread(target=self.actions.import_origin_data.main, args=(file_name,))
            self.current_thread = t
            t.setDaemon(True)
            t.start()
        else:
            self.log('请先选择文件')

    def log(self, msg):
        self.log_text.insert(END, '%s\n' % msg)
        self.log_text.yview_moveto(1)

    def stop_thread(self):
        if self.current_thread:
            self.current_thread.stop()

    def set_actions(self, actions):
        self.actions = actions


if __name__ == '__main__':
    app = Application()
    app.mainloop()
