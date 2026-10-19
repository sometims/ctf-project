# -*- coding: utf-8 -*-
"""
页面源码侦察器 page_scan.py —— 自动提取页面线索
功能：
  1. 抓取页面，提取 HTML 注释（<!-- -->）
  2. 提取 <script src> / <link> / <a href> / <form action> + 所有 <input name>
  3. 提取可疑关键词（tips/hint/flag/admin/debug/secret/source/upload...）
  4. 自动拉取所有 JS 文件，grep ajax/url/参数名/关键词
用法：python page_scan.py <url>
"""
import sys
import re
import requests
import warnings
from urllib.parse import urljoin, urlparse

# Windows 控制台默认 GBK，打印中文会崩 → 强制 UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

warnings.filterwarnings('ignore')
requests.packages.urllib3.disable_warnings()

# 可疑关键词（遇到就高亮，很多题目的提示/注释都带这些词）
KEYWORDS = [
    'tips', 'hint', 'flag', 'f1ag', 'fl4g', 'admin', 'debug', 'secret',
    'source', 'upload', 'backup', 'user', 'pass', 'passwd', 'sql', 'key',
    'password', 'root', 'shell', 'cmd', 'include', 'eval', 'session',
    'robots', 'backup', 'test', 'info', 'config', 'php', 'tips=1',
]

# 过滤：这些 URL 不去抓（图片/字体/CSS）
SKIP_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
             '.woff', '.woff2', '.ttf', '.eot', '.css', '.map')

# 第三方库 JS（噪音，跳过分析）
LIB_JS = ('jquery', 'semantic', 'bootstrap', 'vue', 'react', 'angular',
          'lodash', 'axios', 'moment', 'sweetalert', 'layui', 'echarts')


def fetch(url, timeout=8):
    try:
        r = requests.get(url, verify=False, timeout=timeout,
                         headers={'User-Agent': 'Mozilla/5.0'})
        # 页面常不带 charset，requests 会猜成 latin-1 导致中文乱码 → 用 chardet 重新猜
        if 'charset' not in r.headers.get('Content-Type', '').lower():
            r.encoding = r.apparent_encoding or 'utf-8'
        return r
    except Exception as e:
        print(f"  [!] 请求失败 {url}: {e}")
        return None


def extract_comments(html):
    return re.findall(r'<!--(.*?)-->', html, re.S)


def extract_scripts(html, base):
    return [urljoin(base, s) for s in re.findall(r'<script[^>]+src=["\']([^"\']+)', html, re.I)]


def extract_links(html, base):
    links = []
    links += [urljoin(base, h) for h in re.findall(r'<a[^>]+href=["\']([^"\']+)', html, re.I)]
    links += [urljoin(base, h) for h in re.findall(r'<link[^>]+href=["\']([^"\']+)', html, re.I)]
    return list(dict.fromkeys(links))


def extract_forms(html, base):
    """提取表单：action + method + 所有 input name"""
    forms = []
    for fm in re.findall(r'<form[^>]*>(.*?)</form>', html, re.S | re.I):
        action = re.search(r'action=["\']([^"\']*)', fm)
        method = re.search(r'method=["\']([^"\']*)', fm)
        inputs = re.findall(r'<input[^>]+name=["\']([^"\']+)', fm, re.I)
        forms.append({
            'action': urljoin(base, action.group(1)) if action else base,
            'method': (method.group(1).upper() if method else 'GET'),
            'inputs': inputs,
        })
    return forms


def find_keywords(text, source):
    """在文本里找可疑关键词"""
    hits = [kw for kw in KEYWORDS if re.search(re.escape(kw), text, re.I)]
    if hits:
        print(f"    [关键词] ({source}) {hits}")


def scan(url):
    base = url.rstrip('/')
    print("=" * 56)
    print(f"[目标] {url}")
    print("=" * 56)

    r = fetch(url)
    if r is None:
        print("[!] 页面都打不开，先检查地址/网络")
        return
    html = r.text

    print("\n[1] 状态码 / 服务器头")
    print(f"    {r.status_code}  Server: {r.headers.get('Server', '?')}  "
          f"X-Powered-By: {r.headers.get('X-Powered-By', '?')}")

    print("\n[2] HTML 注释（常藏提示）")
    comments = extract_comments(html)
    if comments:
        for c in comments:
            c = c.strip()
            if c:
                print(f"    <!-- {c} -->")
                find_keywords(c, '注释')
    else:
        print("    (无)")

    print("\n[3] 表单（入口 + 参数名）")
    forms = extract_forms(html, url)
    if forms:
        for f in forms:
            print(f"    {f['method']} -> {f['action']}  inputs={f['inputs']}")
    else:
        print("    (无)")

    print("\n[4] 页面内 <script src>（JS 入口）")
    scripts = extract_scripts(html, url)
    if scripts:
        for s in scripts:
            print(f"    {s}")
    else:
        print("    (无)")

    print("\n[5] 链接（a/link href）")
    links = extract_links(html, url)
    if links:
        for l in links:
            print(f"    {l}")
    else:
        print("    (无)")

    print("\n[6] 拉取 JS 文件分析（找 ajax / url / 参数）")
    js_interesting = False
    for s in scripts:
        if s.lower().endswith(SKIP_EXTS):
            continue
        if any(lib in s.lower() for lib in LIB_JS):
            print(f"    (跳过第三方库: {s.split('/')[-1]})")
            continue
        js = fetch(s)
        if js is None:
            continue
        body = js.text
        js_interesting = True
        print(f"    --- {s} ({len(body)}B) ---")
        for m in re.finditer(r'.*(?:ajax|url\s*[:=]|type\s*:\s*["\']POST|data\s*:|\.post\(|fetch\()',
                             body):
            line = m.group(0).strip()
            if line:
                print(f"      {line[:160]}")
        find_keywords(body, 'JS')
    if not js_interesting:
        print("    (无 JS 文件)")

    print("\n" + "=" * 56)
    print("扫描完成。红色线索=注释/表单/JS；可疑关键词已标出。")
    print("=" * 56)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        u = input('请输入URL: ').strip()
        if not u:
            print('用法: python page_scan.py <url>')
            sys.exit(1)
        scan(u)
    else:
        scan(sys.argv[1])

    # 防闪退：Windows 双击运行完别闪关，按任意键退出
    print("\n按任意键退出...")
    try:
        input()
    except EOFError:
        pass
