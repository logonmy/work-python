# !/usr/bin/env python
# -*- coding: gbk -*-
import requests
import threading
import subprocess
import shlex
import time
import logging
import os

"""
��ʱ����ļ�ʵ�֣�ֻ֧�̶ֹ����ʱ�������
��ѭ�����������������������̣߳�����¼��ǰ����ʱ�䣬�Լ�ÿ��������´�ִ��ʱ�������������������������ѭ��sleepʱ��
��ѭ��sleepʱ�䵽�����߳�ʱ����=��ǰʱ��-�ϴ�����ʱ�䣬ѭ���ж����������ʱ�����Ƿ�С�ڻ�������߳�ʱ������
1�����ǣ������������̣߳�����¼��ǰ����ʱ�䣬�Լ���������´�ִ��ʱ����
2���粻�ǣ���¼��ǰ����ʱ�䣬�Լ���������´�ִ��ʱ������=�ϴε�ʱ����-���߳�ʱ������
�������������������ѭ��sleepʱ�䣬�ٴ�ѭ��
"""


class Quartz:
    def __init__(self):
        self.tasks = []
        self.task_left_interval_dict = {}
        self.sleep_time = 0

    def add_task(self, task):
        self.tasks.append(task)
        self.task_left_interval_dict[task.name] = 0

    def start(self):
        if not self.tasks:
            logger.error('There is no tasks , exit...')
            exit(0)
        logger.info("Quzrtz start ...")
        while 1:
            min_interval = 0xffff
            for task in self.tasks:
                left_interval = self.task_left_interval_dict.get(task.name) - self.sleep_time
                if left_interval <= 0:
                    left_interval = task.interval
                    threading.Thread(target=task.start, args=[]).start()
                min_interval = min(min_interval, left_interval)
                self.task_left_interval_dict[task.name] = left_interval
            self.sleep_time = min_interval
            time.sleep(self.sleep_time)


def start_cmd_task(command_args, need_new_window=False):
    logger.info(command_args)
    if need_new_window:
        return subprocess.Popen(command_args, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        return subprocess.Popen(command_args, stdout=subprocess.PIPE)


def kill_cmd_task(pid):
    subprocess.call(shlex.split("taskkill /t /f /pid %s" % pid))


class Task(object):
    def __init__(self, name, interval):
        self.name = name
        self.interval = interval
        self.is_running = False

    def run(self):
        pass

    def start(self):
        if self.is_running:
            logger.info('%s���������У����β�ִ�У�����', self.name)
        else:
            self.is_running = True
            try:
                self.run()
            except Exception, e:
                logger.error('%sִ��ʧ��, ԭ��%s', (self.name, e.message))
            logger.info('%sִ�гɹ�������', self.name)
            self.is_running = False


class ServerHeartBeatTask(Task):
    def __init__(self):
        super(ServerHeartBeatTask, self).__init__('ServerHeartBeatTask', 60)
        self.process = None

    def run(self):
        url = 'http://127.0.0.1:1234'
        try:
            requests.get(url, timeout=30)
            logger.info('server�����������')
        except:
            logger.error('server��������쳣������server')
            if self.process:
                kill_cmd_task(self.process.pid)
            self.process = start_cmd_task(['python', 'server.py'], need_new_window=True)


class ImportDataToReidsTask(Task):
    def __init__(self):
        super(ImportDataToReidsTask, self).__init__('ImportDataToReidsTask', 15 * 60 * 60)
        self.data_files = []

    def find_data_file(self):
        path = '.'
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)) and 'tyc_' in f and f not in self.data_files:
                return f
        return None

    def run(self):
        df = self.find_data_file()
        if df:
            start_cmd_task(['python', 'data_process.py', '-i', df])
        else:
            logger.info("��ʱû�������ļ�Ҫ���룡����")


def main():
    quartz = Quartz()
    quartz.add_task(ServerHeartBeatTask())
    quartz.add_task(ImportDataToReidsTask())
    quartz.start()


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('quartz.log', mode='a')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s: %(message)s"))
    logger.addHandler(console)
    main()
