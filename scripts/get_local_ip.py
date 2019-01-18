#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket


f = open('used_ips.txt', 'a')
f.write(socket.gethostbyname(socket.gethostname()))
f.write('\n')
f.write(socket.gethostbyname(socket.gethostname()))
f.write('\n')
f.close()