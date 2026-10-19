# 🍶 13 · Flask 与 Session

## 一、题型概述

Python Flask 应用的两条经典攻击面：**Session 伪造**（知道密钥就能签任意身份）与 **SSTI**（模板注入执行代码）。看到 `Server: gunicorn` / `Werkzeug` 或 cookie 是 `eyJ...` 的 JWT 样子，就往这想。

## 二、常考考点

- **Session 弱密钥**：Flask 用 `itsdangerous` 对 session 做**签名**（不加密）。若 `SECRET_KEY` 弱/可爆破 → `flask-unsign` 解/爆出密钥，再签一个管理员 session。
- **伪造流程**：解 session 内容 → 爆破/已知密钥 → 改角色 → 重新签名 → 带着假 cookie 访问。
- **SSTI（服务端模板注入）**：Jinja2 把用户输入拼进模板 → `{{7*7}}` / `{{config}}` / `{{''.__class__.__mro__}}` 读配置、RCE。
- **调试模式 RCE**：`Werkzeug` 开发服务器 `debug=True` 时错误页带交互控制台（PIN 保护，CTF 常考推算 PIN）。

## 三、解决方法 / 通用套路

1. **解 session**：`flask-unsign --decode --cookie <val>` 看里面有什么。
2. **爆密钥**：`flask-unsign --unsign --wordlist rockyou.txt`（弱密钥一击即中）。
3. **伪造**：改角色字段 → `--sign --secret <key>` 生成新 cookie。
4. 若涉及模板 → 测 `{{7*7}}` 判断是否 SSTI，再拉 globals 链打 RCE。

## 四、已收容题目

| 题目 | 关键手法 | WriteUp |
|---|---|---|
| NSSCTF Flask session 伪装 | session 弱密钥爆破（flask-unsign）+ 伪造管理员身份 | `WP-[NSSCTF]Flask的session伪装-弱密钥伪造.md` |

## 五、相关笔记与工具

- 工具：`flask-unsign`（外部）、`git-dumper`（配合代码审计）
- 关联：SSTI 常与 14-综合组合题、04-RCE 联动

> 返回总入口：`../../README.md`
