# Web 笔记12-服务器架构与文件系统（概念打通）

> 更新：2026-08-03 ｜ 来源：N1Page 重做复盘 + 学生提问
> 定位：把"服务器/框架/文件系统/工作目录"这些词彻底捋清，做题不再混

---

## 一、"服务器"的三种含义（混乱的根源）

| 词 | 意思 | 例子 |
|---|---|---|
| ① 服务器（机器） | 一台电脑/虚拟机 | 靶机那台 Linux |
| ② Web 服务器（软件） | 收 HTTP 请求、转发 | nginx / Apache / openresty |
| ③ 后端/应用服务器（软件） | 跑业务代码 | gunicorn / uwsgi / Werkzeug / Tomcat |

② 和 ③ 都是跑在 ① 这台机器上的软件。**"后端服务器"≠"Web 服务器"**，但两者**都能收请求**，区别是分工。

## 二、后端 = 接待员 + 厨师（两层）

```
后端 = 接收请求(接待员) + 业务逻辑(厨师)，缺一不可

每个技术栈都是"厨师+接待员"，区别只在接待员是焊死还是独立：
| 技术栈 | 厨师(业务) | 接待员(收请求) | 一条龙？ |
|---|---|---|---|
| Python | Flask | Werkzeug（内置） | ✅ 开发时焊死 |
| Python 生产 | Flask | gunicorn（WSGI） | ❌ 拆开 |
| PHP | PHP 代码 | PHP-FPM（独立） | ❌ 拆开 |
| Java | Spring Boot | Tomcat（内嵌） | ✅ 内嵌 |
| Node | Express | Node 自带 http | ✅ 焊死 |
```

**开发 vs 生产**：
- 开发：浏览器 → Werkzeug（Flask 自带的接待员）→ Flask 厨师，不需要 nginx
- 生产：浏览器 → nginx（前台保安）→ gunicorn（接待员）→ Flask 厨师

## 三、完整请求链路（二级转发）

```
浏览器 → /xx
  ↓
nginx（② Web服务器）—— 收请求、静态文件直接给、动态请求转发
  ↓ 转发
gunicorn（③ 后端服务器）—— 接单，叫厨师
  ↓
Flask —— 按路由表找函数 → 执行 → 读文件
  ↓ 原路返回：Flask → gunicorn → nginx → 浏览器
```

## 四、工作目录关系（一棵树理论）

**整个 Linux 只有一个文件系统，一棵从 `/` 开始的大树。**

```
/                        ← 树根
├── bin / sbin           ← 基础命令
├── etc                  ← 配置文件（nginx.conf, passwd）
├── var                  ← 运行时数据（/var/www/html 默认网站目录）
├── usr                  ← 已装软件
├── home                 ← 用户的家（/home/sssssserver）
├── tmp                  ← 临时文件
├── proc                 ← 虚拟目录！进程信息
├── dev                  ← 设备
└── flag（非标准）       ← 靶机自定义，flag 常见位置
```

**关键认知**：
- "工作目录"(cwd) = 进程启动时"站在树上的哪个节点"，**不是独立文件系统**
- 所有进程（nginx/gunicorn/Flask）都在同一棵树上
- 硬编码路径 ≠ cwd：源码写死的路径和进程实际站位可以是两个地方（N1Page 实锤：写死 /home/nu11111111l，实际 cwd=/home/sssssserver）

## 五、/proc 虚拟文件家族（进程照妖镜）

```
/proc/self/cwd      目录（软链→进程工作目录）：读源码不猜路径
/proc/self/cmdline  文件：启动命令（认厨师+泄露路径）注意 \0 分隔
/proc/self/environ  文件：环境变量（PWD=真实路径；可能有诱饵 flag）
/proc/self/fd/      目录：进程打开着的文件
/proc/self/status   文件：进程状态
```

**cmdline 读取技巧**：字段用空字节 `\0` 分隔 → Python 读后 `replace("\x00", " | ")`。

## 六、读源码 = 扫雷（不用全懂，按清单找危险特征）

| 找什么 | 对应漏洞 | N1Page 收获 |
|---|---|---|
| `open(路径)` 拼用户输入 | 读文件题 | 穿越点 |
| `execfile`/`include`/`import` | 加载文件泄露 | flag.py、key.py |
| `.replace` 过滤 | 找没被过滤的侧门 | `. _ {}` 过滤→走 session |
| `render_template_string`/`eval`/`system` | SSTI / RCE | SSTI 漏洞 |
| `secret_key`/`app.config` | session 伪造 | key 泄露 |

**速记**：看到 `open`→读文件；`include`→LFI；`eval/system`→RCE；`render_template_string`→SSTI；`replace`过滤→找侧门；`secret_key`→伪造。

## 七、LFI / RCE / 读文件 = "三兄弟"（不是同一个）

| | 读文件题 | LFI 文件包含 | RCE 命令执行 |
|---|---|---|---|
| 危险函数 | `open().read()` | PHP `include`/`require` | `eval`/`system`/`exec` |
| 输入变成 | 文件路径 | 文件路径 | 代码/命令 |
| 后果 | 读内容 | 读 + **文件被当 PHP 执行** | 直接执行命令 |

**区分口诀**：输入进了哪个函数？`open`→只能看；`include`→看+执行；`eval/system`→执行你的话。

## 八、报错信息泄露（画地图技能）

- 服务器把异常回显 = `[Errno 2] No such file or directory: '<完整路径>'`
- 用途：①确认真实拼接路径 ②确认过滤是否生效 ③探测目录结构
- **报错不是噪音，它在帮你画地图**

## 九、画地图方法论（任意读题通用流程）

```
能力(任意读) → 读主文件(骨架) → 报错/实测填目录 → 路径矛盾触发修正 → 读environ拿真路径 → 验证
```

**核心心法**：
1. 源码 = 设计图：先读主文件
2. 报错信息也是证据：泄露真实路径
3. 对比实验抓矛盾：同一文件两条路径一成一败 → cwd≠硬编码 → 追查 /proc/self/environ

---

## 相关题目
- N1Page（DASCTF）→ `WP-[DASCTF]N1Page-全案笔记.md`：整套实操
