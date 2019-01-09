#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

resp = requests.get('https://gsp0.baidu.com/5aAHeD3nKhI2p27j8IqW0jdnxx1xbK/tb/pms/img/st.gif?ts=1ocw&t=time&sid=jq7qs7tgp9t&dv=3&page=110_25&p=110&z_webglmap_fps=60')
with open('tile1.gif', 'wb') as w:
    w.write(resp.content)
