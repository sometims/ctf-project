# -*- coding: utf-8 -*-
"""
迷你目录扫描器 mini_scanner.py
原理：逐个请求常见路径，看哪些返回非404（存在）
★ 防假200：有些服务器对"不存在的路径"统一返回首页(200)，会刷屏假结果。
  本工具先探测"默认页内容"，扫描时内容一样的标记为【假200】自动忽略。
用法：python mini_scanner.py http://靶机/
"""
import sys
import requests

# 常见敏感文件/目录词表（CTF 常用）
WORDS = [
    # 备份与源码
    "index.php", "index.html", "index.php.bak", "index.php~", "1.php",
    "www.zip", "backup.zip", "backup.tar.gz", "bak.zip", "web.zip",
    "config.php", "config.php.bak", "database.sql", "db.sql", "flag.txt",
    "flag.php", "flag", "f1ag", "admin.zip",
    # Vim / 编辑器残留
    ".index.php.swp", ".index.php.swo", ".index.php.swn", "index.php.swp",
    # git / 版本控制
    ".git/HEAD", ".git/config", ".svn/entries", ".hg",
    # 信息泄露
    "robots.txt", ".DS_Store", ".bash_history", ".env", "env",
    "phpinfo.php", "info.php", "test.php", "shell.php", "cmd.php",
    # 后台/目录
    "admin", "admin/", "login", "upload", "uploads/", "backup/", "data/",
    "wp-admin", "phpmyadmin", "api/", "source/", "src/",
]

def get_fallback(s, base_url):
    """探测服务器的"默认页内容"：
    请求一个几乎不可能存在的路径，如果返回200，它的内容就是默认页（假200的模板）。
    返回该内容（bytes），或 None（如果404，则说明服务器是正常404，不需要防假200）。
    """
    probe = base_url.rstrip("/") + "/zzz__definitely_not_exists__12345"
    try:
        r = s.get(probe, timeout=5, allow_redirects=False)
        if r.status_code == 200:
            print(f"[*] 检测到服务器对所有路径返回200（假200），已记录默认页用于过滤\n")
            return r.content
        return None
    except requests.exceptions.RequestException:
        return None

def scan(base_url):
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    print(f"[*] 扫描目标: {base_url}\n")
    fallback = get_fallback(s, base_url)  # 假200检测
    found, fake = [], 0
    for w in WORDS:
        url = base_url.rstrip("/") + "/" + w
        try:
            r = s.get(url, timeout=5, allow_redirects=False)
            if r.status_code == 404:
                continue
            body = r.content
            # 假200检测：内容等于默认页 → 忽略
            if fallback is not None and body == fallback:
                fake += 1
                continue
            size = len(body)
            print(f"[+] {w:<20} -> {r.status_code}  ({size} bytes)")
            found.append((w, r.status_code, size))
        except requests.exceptions.RequestException:
            pass
    print(f"\n[*] 真实发现 {len(found)} 个；忽略假200 {fake} 个")
    return found

if __name__ == "__main__":
    # 支持两种方式输入靶机：
    # ① 命令行带参：python mini_scanner.py http://靶机/
    # ② 直接运行，然后手动输入（推荐）
    target = ""
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("请输入靶机地址（如 http://192.168.1.1:8080/）：").strip()
    if not target:
        print("[!] 没有输入地址，退出")
        sys.exit(1)
    if not target.startswith(("http://", "https://")):
        target = "http://" + target
        print(f"[*] 已自动补全 http:// -> {target}")
    scan(target)

    # 防止运行完窗口自动关闭（尤其是双击运行 .py 时）
    print("\n按回车键退出...")
    try:
        input()
    except EOFError:
        pass  # 在自动化环境（如管道）里没有输入也不报错
