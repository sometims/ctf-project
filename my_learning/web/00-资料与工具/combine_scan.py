"""
合并扫描器 combine_scan.py —— 目录扫描 + 敏感文件扫描 二合一
流程：
  第1阶段：目录扫描（复用 mini_scanner 逻辑）→ 发现目录/文件（如 /backup/ /upload/ /admin）
  第2阶段：对每个发现的目录，再跑敏感文件探测（复用 sensitive_scan 逻辑）
           → /backup/.git /backup/index.php~ /backup/.DS_Store ...
用法：python combine_scan.py <url>
"""
import sys
import os
import re
import requests
import warnings

warnings.filterwarnings('ignore')
requests.packages.urllib3.disable_warnings()

# 复用两个工具的模块
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mini_scanner
import sensitive_scan

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def get(url, timeout=8):
    try:
        return requests.get(url, verify=False, timeout=timeout, headers=UA)
    except Exception:
        return None


def probe_dir(base, subpath):
    """对 subpath 目录做敏感文件探测，返回 (路径, flag片段) 命中列表"""
    hits = []
    for sp in sensitive_scan.SENSITIVE_PATHS:
        url = base + subpath.rstrip('/') + '/' + sp
        r = get(url)
        if r is None or r.status_code == 404:
            continue
        body = r.content
        flags = sensitive_scan.check_flag(body.decode('utf-8', errors='replace')) if body else []
        print(f"    [{r.status_code}] {subpath}{sp}  ({len(body)}B)"
              + (f"  FLAG: {flags[:2]}" if flags else ''))
        hits.append((subpath + sp, flags))
    return hits


def main(base_url):
    base_url = base_url.rstrip('/')
    print("=" * 50)
    print("[第1阶段] 目录扫描...")
    print("=" * 50)
    found = mini_scanner.scan(base_url)

    # 只把"明确的目录"作为第2阶段目标：词表里带 / 结尾的 + 已知目录名（不带扩展名）
    DIR_NAMES = {'admin', 'login', 'upload', 'wp-admin', 'phpmyadmin', 'api',
                 'source', 'src', 'data', 'backup', 'uploads', 'images', 'static'}
    dirs = []
    for p, _, _ in found:
        last = p.rstrip('/').split('/')[-1]
        if p.endswith('/') or last in DIR_NAMES:
            dirs.append(p.rstrip('/'))
    print()
    print("=" * 50)
    print(f"[第2阶段] 对 {len(dirs)} 个目录做敏感文件探测...")
    print("=" * 50)
    all_flags = []
    for d in dirs:
        print(f"\n--- 探测目录: {d}/ ---")
        for path, flags in probe_dir(base_url, d):
            all_flags += flags

    # 若发现 .git 泄露，自动下载仓库搜 flag
    if any(p == '.git/HEAD' for p, _, _ in found):
        hits = [(200, '.git/HEAD', 0, [])]
        sensitive_scan.git_dump_and_check(base_url, hits)

    print()
    print("=" * 50)
    print(f"扫描完成。共发现 {len(all_flags)} 个 flag 片段:")
    for f in all_flags:
        print('  ', f)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        url = input('请输入靶机URL: ').strip()
        if not url:
            print('用法: python combine_scan.py <url>')
            input('按回车退出...')
            sys.exit(1)
        main(url)
        input('\n按回车退出...')
    else:
        main(sys.argv[1])
