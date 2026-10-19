# 🔁 09 · PHP 反序列化

## 一、题型概述

`unserialize()` 处理我们可控的字符串 → 通过**属性覆盖**和**魔法方法自动触发**，把数据流导进危险函数（eval / 命令执行 / 文件操作），是 PHP 栈进阶核心题。

## 二、常考考点

- **属性覆盖**：构造对象让某属性等于期望值（如 `pswd="escaping"`）绕过判断。
- **魔法方法自动触发**：请求结束对象销毁时 `__destruct` 自动调用；`__toString` 在对象被当字符串时调用——不需要手动调用。
- **POP 链**：`__destruct` → `__toString` → `eval`/`system`，把多个类的魔法方法串成利用链。
- **结构细节**：`protected` 属性序列化带 `\x00*\x00`、`private` 带 `\x00类名\x00`；需要精确构造。
- **黑名单绕过**：过滤 `flag`/`php` 等 → 用其他触发路径或属性名绕开。

## 三、解决方法 / 通用套路

1. **读源码**：找哪个类有危险魔法方法（`__destruct`/`__toString`/`__wakeup`），危险落点在哪。
2. **定链**：从入口魔法方法一路跟到危险函数，确认需要哪些属性。
3. **构造串**：手写易错 → 用 `serforge.py` 生成（支持 public/protected/private、嵌套对象）。
4. **属性覆盖**：把判断条件需要的属性设成期望的值。
5. **生命周期**：记住对象在脚本结束才销毁，魔法方法"自动"触发（`img/lifecycle_destruct.svg`）。

## 四、已收容题目

| 题目 | 关键手法 | WriteUp |
|---|---|---|
| qsnctf 40507 | 反序列化绕过黑名单：伪造对象属性 `pswd=escaping` | `WP-[qsnctf]反序列化绕过黑名单.md` |
| qsnctf 40515 | POP 链：`GIT` 对象 `__destruct` → `ZeroZone` `__toString` → `eval` 执行代码 | `WP-[qsnctf]反序列化POP链-eval代码执行.md` |
| qsnctf 40785 | POP 链：`Monitor` `__destruct` → `Screen` 变量函数调用 `$format($content)` → `system` RCE（private 属性 `\x00` + 通配符避 `flag`） | `WP-[qsnctf]反序列化变量函数调用RCE.md` |

## 五、相关笔记与工具

- 笔记：`Web笔记12-PHP序列化与反序列化.md`（基础/对照表）、`Web笔记14-PHP反序列化进阶POP链与魔法方法.md`
- 工具：`serforge.py` + `serforge使用说明.md`（见 `../00-资料与工具/`）
- 图示：`img/pop_chain.svg`、`img/lifecycle_destruct.svg`

> 返回总入口：`../../README.md`
