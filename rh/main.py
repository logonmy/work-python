#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gui import app as ap
from action import create_bm_task
from action import import_origin_data


class Actions:
    def __init__(self):
        pass


def main():
    app = ap.Application()
    log = app.log
    actions = Actions()
    actions.create_bm_task = create_bm_task.Controller(log)
    actions.import_origin_data = import_origin_data.Controller(log)
    app.set_actions(actions)
    app.mainloop()


if __name__ == '__main__':
    main()