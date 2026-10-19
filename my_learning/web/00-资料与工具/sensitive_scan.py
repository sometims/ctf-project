"""
敏感文件自动扫描器（sensitive file scanner）
用法：python sensitive_scan.py <url>
流程：
  1. 爆破常见敏感路径（备份/版本控制/配置/flag变体）
  2. 防假200（与首页内容相同则跳过）
  3. 解析 robots.txt，自动加入其 Disallow 路径
  4. 下载可读文件，搜索 flag 特征（flag{ / flag1: / n1book{ / ctfshow{ ...）
  5. 输出 [状态] 路径 → flag 片段
"""
import sys
import re
import requests
import warnings
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings('ignore')
requests.packages.urllib3.disable_warnings()

FLAG_PATTERN = re.compile(
    r'(flag\d?\s*[:=]?\s*[A-Za-z0-9_!@#$%^&*\-{}.]+\}|'
    r'flag\d?\s*[:=]\s*[A-Za-z0-9_!@#$%^&*\-{}./\s]+|'
    # leet 变体：f1ag / fl4g / F1Ag / F1a9 ...
    r'f[1lI!][4aA@][g9q]\s*[:=]?\s*\{?[A-Za-z0-9_!@#$%^&*\-{}.]{3,}\}?|'
    # 结构模式：任意标识符+花括号（平台无关，比赛通用）
    r'[A-Za-z0-9_]{2,}\{[A-Za-z0-9_!@#$%^&*\-{}./]{5,}\})',
    re.I)

# 常见敏感路径（做题积累 + 本章教材）
SENSITIVE_PATHS = [
    # robots / sitemap
    'robots.txt', 'sitemap.xml', 'crossdomain.xml', '.htaccess', '.env', '.gitignore',
    # 版本控制
    '.git/HEAD', '.git/config', '.git/index', '.git/logs/HEAD',
    '.svn/entries', '.svn/wc.db', '.hg/00changelog.i', '.hg/dirstate',
    # Mac
    '.DS_Store', '.DS_Store/',
    # 常见备份
    'index.php~', 'index.php.bak', 'index.php.old', 'index.php.save', 'index.php.txt',
    'index.php.zip', 'index.php.gz', 'index.php.swp', '.index.php.swp',
    'index.html~', 'index.html.bak', 'index.html.old', '.index.html.swp',
    'flag.php~', 'flag.php.bak', 'flag.php.swp', '.flag.php.swp',
    'admin.php~', 'admin.php.bak', 'config.php~', 'config.php.bak',
    '1.php~', '1.php.bak', 'test.php~', 'test.php.bak', 'info.php~',
    'index.bak', 'index.txt', 'index.zip',
    # 打包备份
    'backup.zip', 'www.zip', 'site.zip', 'web.zip', 'html.zip', 'old.zip', '1.zip',
    'a.zip', 'b.zip', 'bak.zip', 'backup.tar.gz', 'www.tar.gz', 'web.tar.gz',
    # 数据/配置
    'db.sql', 'backup.sql', 'data.sql', 'dump.sql', 'database.sql',
    'composer.json', 'package.json', '.bash_history', '.viminfo', '.profile',
    # 常见入口/探针
    'flag.txt', 'flag.php', 'flag', 'flag2.txt', 'flag2.php', 'flag2',
    'flag3.txt', 'flag3.php', 'flag1.txt', 'flag1.php',
    'f1ag.txt', 'f1ag.php', 'flag_is_here.txt', 'flag_here.txt',
    'phpinfo.php', 'info.php', 'test.php', '1.php', 'shell.php', 'cmd.php',
    'x.php', 'hack.php', 'a.php', 'admin.php', 'login.php',
]

# 常见备份后缀（套在发现的 .php/.txt 文件上再爆一轮）
BACKUP_EXTS = ['~', '.bak', '.old', '.save', '.swp', '.txt', '.zip', '.tar.gz']


def get(url, timeout=8):
    try:
        return requests.get(url, verify=False, timeout=timeout,
                            headers={'User-Agent': 'Mozilla/5.0'})
    except Exception:
        return None


def check_flag(content):
    return FLAG_PATTERN.findall(content or '')


def git_dump_and_check(base, hits):
    """发现 .git 后自动 git-dumper 下载并搜索 flag"""
    if not any(p == '.git/HEAD' for _, p, _, _ in hits):
        return
    print("\n[+] 发现 .git 泄露，尝试 git-dumper 下载仓库...")
    import subprocess
    import tempfile
    import os
    dumpdir = tempfile.mkdtemp(prefix='gitrepo_')
    try:
        r = subprocess.run(
            [sys.executable, '-m', 'git_dumper', base + '/.git/', dumpdir],
            capture_output=True, timeout=180)
    except Exception as e:
        print('[!] git-dumper 执行失败（未安装?）:', e)
        return
    if r.returncode != 0:
        print('[!] git-dumper 下载失败:', r.stderr.decode('utf-8', 'replace')[-300:])
        return
    print('[+] 仓库已下载，搜索文件内容...')
    for root, _, files in os.walk(dumpdir):
        if '\\.git' in root or '/.git' in root:
            continue
        for f in files:
            path = os.path.join(root, f)
            try:
                content = open(path, encoding='utf-8', errors='ignore').read()
            except Exception:
                continue
            flags = check_flag(content)
            if flags:
                print(f'[git仓库] {os.path.relpath(path, dumpdir)} → FLAG: {flags[:3]}')


def main(base):
    base = base.rstrip('/')
    home = get(base + '/')
    home_len = len(home.content) if home and home.status_code == 200 else -1
    hits = []
    visited = set()

    def probe(path):
        if path in visited:
            return
        visited.add(path)
        url = base + '/' + path
        r = get(url)
        if r is None:
            return
        if r.status_code == 404:
            return
        # 防假200：内容与首页相同
        body = r.content
        if r.status_code == 200 and len(body) == home_len and body == (home.content if home else b''):
            return
        flags = check_flag(body.decode('utf-8', errors='replace')) if body else []
        hits.append((r.status_code, path, len(body), flags[:3]))
        print(f"[{r.status_code}] {path}  ({len(body)}B){'  FLAG: ' + str(flags[:3]) if flags else ''}")

    # 第一轮：基础路径
    for p in SENSITIVE_PATHS:
        probe(p)

    # 第二轮：robots.txt 里发现的路径（兼容 Disallow: 空值+路径在下一行的格式）
    robots = get(base + '/robots.txt')
    if robots and robots.status_code == 200:
        lines = [l.strip() for l in robots.text.splitlines() if l.strip()]
        for i, line in enumerate(lines):
            m = re.match(r'Disallow:\s*(\S*)', line, re.I)
            if not m:
                continue
            path = m.group(1)
            if not path and i + 1 < len(lines) and not re.match(r'(User-agent|Disallow|Allow|Sitemap)', lines[i + 1], re.I):
                path = lines[i + 1]
            if path and path != '/':
                probe(path.lstrip('/'))

    # 第三轮：对 200 的 .php/.txt 文件套备份后缀
    found_files = [p for s, p, _, _ in hits if s == 200 and re.search(r'\.(php|txt|html)$', p)]
    for f in found_files:
        for ext in BACKUP_EXTS:
            probe(f + ext)

    print(f"\n=== 扫描完成，共 {len(hits)} 个敏感文件 ===")
    all_flags = []
    for s, p, size, fl in hits:
        all_flags += fl
    print("检测到的 flag 片段:", all_flags if all_flags else "无（可能藏在二进制/需要人工看）")
    git_dump_and_check(base, hits)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        url = input('请输入靶机URL: ').strip()
        if not url:
            print('用法: python sensitive_scan.py <url>')
            input('按回车退出...')
            sys.exit(1)
        main(url)
        input('\n按回车退出...')
    else:
        main(sys.argv[1])
