import urllib.request
import json
import sys

url = 'http://localhost:5000/health'
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=4) as resp:
    if resp.status != 200:
        sys.exit(1)
    data = json.loads(resp.read().decode())
    sys.exit(0 if data.get('status') in ('healthy', 'ok') else 1)
