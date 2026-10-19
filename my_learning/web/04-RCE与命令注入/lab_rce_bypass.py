#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lab_rce_bypass.py —— 本地 RCE 过滤绕过练习靶机（纯 Python，无需 PHP / Docker）

⚠️ 为什么用 bash -c 执行？
   真实 CTF 里的 RCE 大多跑在 Linux 的 sh/bash 上，绕过手法（${IFS}、ca$@t、分号…）
   都是「Shell 层」的。你在 Windows 上用 Git Bash 跑这个靶机，
   后端通过 `bash -c "<你的输入>"` 执行，行为 = 真实 Linux 靶机。
   （Git Bash 自带 cat/tac/nl/head/tail/sort/less/grep，和 Linux 一致）

运行方式（在 Git Bash 里）：
    cd my_learning/web
    python lab_rce_bypass.py
然后另开一个 Git Bash 标签页，用 curl.exe 打：
    curl.exe "http://127.0.0.1:8080/lv0?cmd=127.0.0.1;cat secret.txt"

关卡说明（后端「故意」把你的输入拼进 shell，再按关卡加 WAF）：
    /lv0  基础命令注入（无过滤）           —— 学会用 ; & | && || 接命令
    /lv1  空格被过滤                       —— 用 ${IFS} / < / %09(tab) / $IFS$9 / {a,b}
    /lv2  读文件命令被过滤(cat/tac/...)    —— 用 ca$@t / c\at / c${IFS}at / 通配符 / 换读器
    /lv3  命令分隔符 ; & | 被过滤          —— 用 %0a(换行) 代替
    /lv4  无回显（输出被吞）               —— 用 > 文件 重定向，再 /read?f= 取回

目标：把同目录下的 secret.txt（里面有 flag）读出来。
"""

import http.server
import socketserver
import subprocess
import urllib.parse
import os
import re
import sys

PORT = 8080
LAB_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET = os.path.join(LAB_DIR, "secret.txt")

LEVELS = {
    0: "基础命令注入（无过滤）",
    1: "空格被过滤",
    2: "读文件命令被过滤（cat/tac/more/nl/head/tail/less/sort/rev/grep…）",
    3: "命令分隔符 ; & | 被过滤",
    4: "无回显（输出被吞）",
}


def ensure_secret():
    if not os.path.exists(SECRET):
        with open(SECRET, "w", encoding="utf-8") as f:
            f.write("flag{byp4ss_w4f_l1ke_4_pr0}\n")
        print(f"[+] 已生成 secret.txt -> {SECRET}")


def run_in_bash(cmd: str) -> str:
    """模拟后端危险操作：把用户输入直接交给 shell 执行。"""
    try:
        p = subprocess.run(
            ["bash", "-c", cmd],
            cwd=LAB_DIR,
            capture_output=True,
            timeout=5,
            text=True,
        )
        out = (p.stdout or "") + (p.stderr or "")
        return out if out else "(命令执行了，但没有输出)"
    except subprocess.TimeoutExpired:
        return "[超时] 命令执行超过 5 秒"
    except Exception as e:  # noqa
        return f"[执行错误] {e}"


def page(title, body_html):
    return f"""<!doctype html><html lang=zh><head><meta charset=utf-8>
<title>{title}</title>
<style>body{{font-family:Consolas,Menlo,monospace;background:#1e1e1e;color:#d4d4d4;padding:24px;line-height:1.6}}
h1{{color:#4ec9b0}} .waf{{color:#f48771}} .ok{{color:#6a9955}} code{{background:#2d2d2d;padding:2px 6px;border-radius:4px;color:#ce9178}}
pre{{background:#252526;padding:12px;border-radius:6px;overflow:auto}} .lv{{color:#569cd6}}</style>
</head><body>{body_html}</body></html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):  # 关掉默认访问日志，保持干净
        pass

    def _send(self, html):
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        cmd = qs.get("cmd", [""])[0]

        # 首页
        if path in ("/", ""):
            items = "".join(
                f'<li><span class=lv>/lv{lv}</span> — {desc}</li>'
                for lv, desc in LEVELS.items()
            )
            self._send(page("RCE 绕过靶机", f"""
<h1>RCE 过滤绕过练习靶机</h1>
<p>目标：把 <code>secret.txt</code> 读出来（里面有 flag）。</p>
<p>用法：<code>/lvN?cmd=你的payload</code> ，例如 <code>/lv0?cmd=127.0.0.1;cat secret.txt</code></p>
<p>无回显关用：<code>/read?f=文件名</code> 取回写入的文件。</p>
<ul>{items}</ul>
<p class=ok>提示：复杂 payload 一律写进 .py 脚本用 urllib 发，别在终端手敲引号地狱。</p>
"""))
            return

        # /read?f=xxx —— 取回文件（给 lv4 无回显用），防目录穿越
        if path == "/read":
            fname = qs.get("f", [""])[0]
            if not fname or "/" in fname or "\\" in fname or ".." in fname:
                self._send(page("读取", "<p class=waf>非法文件名</p>"))
                return
            fpath = os.path.join(LAB_DIR, fname)
            if not os.path.exists(fpath):
                self._send(page("读取", f"<p class=waf>文件不存在：{fname}</p>"))
                return
            with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
            self._send(page(f"读取 {fname}",
                            f"<h1>{fname}</h1><pre>{content}</pre>"))

            return

        # 关卡路由 /lv0..lv4
        m = re.match(r"^/lv(\d)$", path)
        if not m:
            self._send(page("404", "<p class=waf>未知路径，回到 / </p>"))
            return
        lv = int(m.group(1))

        # ===== 各关 WAF（模拟 PHP preg_match 黑名单）=====
        # 设计原则：每关【只拦一种】，把单个绕过技巧隔离出来练，互不叠加。
        blocked = []
        if lv == 1:
            # lv1：只拦「空格 0x20」，放行 tab(%09)/${IFS}/< 等
            if " " in cmd:
                blocked.append("空格(0x20)")
        elif lv == 2:
            # lv2：拦所有常见读文件命令，逼你「变形 cat」
            if re.search(r"cat|tac|more|nl|less|head|tail|sort|rev|grep|od|sed|awk|vi|vim|ed|ex", cmd, re.I):
                blocked.append("读文件命令(cat/tac/more/...)")
        elif lv == 3:
            # lv3：拦 ; & | || && 但「故意漏掉换行 %0a」
            if re.search(r"[;&|]", cmd):
                blocked.append("; & | 分隔符")

        if blocked:
            self._send(page(f"lv{lv} 被拦",
                            f"<h1>lv{lv}：{LEVELS[lv]}</h1>"
                            f"<p class=waf>⛔ WAF 拦了：{'，'.join(blocked)}</p>"
                            f"<p>你发的：<code>{cmd}</code></p>"
                            f"<p class=ok>想想：用什么代替被拦的部分？</p>"))
            return

        # lv4：执行但吞掉输出
        if lv == 4:
            subprocess.run(["bash", "-c", cmd], cwd=LAB_DIR, timeout=5)
            self._send(page(f"lv{lv} 无回显",
                            f"<h1>lv{lv}：{LEVELS[lv]}</h1>"
                            f"<p class=ok>命令已执行，但输出被吞。</p>"
                            f"<p>你发的：<code>{cmd}</code></p>"
                            f"<p>试试把结果 <code>&gt; 文件名</code> 重定向到当前目录，"
                            f"再用 <code>/read?f=文件名</code> 取回。</p>"))
            return

        # 其他关：正常执行并回显
        result = run_in_bash(cmd)
        self._send(page(f"lv{lv} 结果",
                        f"<h1>lv{lv}：{LEVELS[lv]}</h1>"
                        f"<p>你发的：<code>{cmd}</code></p>"
                        f"<pre>{result}</pre>"))


def main():
    ensure_secret()
    os.chdir(LAB_DIR)
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"[*] RCE 绕过靶机已启动： http://127.0.0.1:{PORT}")
        print(f"[*] 工作目录：{LAB_DIR}")
        print("[*] 按 Ctrl+C 停止")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] 已停止")


if __name__ == "__main__":
    main()
