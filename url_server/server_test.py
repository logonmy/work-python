import requests
import json

data = {'success': [], 'failed': []}
resp = requests.post('http://127.0.0.1:1234/%s' % 'abc', json=data, timeout=60)
print json.loads(resp.content)
