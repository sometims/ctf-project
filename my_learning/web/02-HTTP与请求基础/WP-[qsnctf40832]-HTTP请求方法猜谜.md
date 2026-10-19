# WP · qsnctf 40832 — HTTP 请求方法猜谜（wrong request method）

> 分类：02-HTTP与请求基础 ｜ 栈：nginx/1.14.2 + PHP/5.6.40 ｜ 难度：入门（白送）
> 地址：`http://challenge.qsnctf.com:40832/`
> **Flag：`flag{c66edbc33cab4d95a7765b6b097646e1}`**

---

## 0. 一句话思路
页面按钮 fetch `backend.php`，默认用 GET（隐藏字段 method=GET）。后端校验**HTTP 请求方法**，只有用正确的才给 flag → 逐个试方法，**POST** 直接命中。

## 1. 侦察
- 页面：Get the Flag 按钮，JS 用隐藏字段 `method` 的值去 `fetch('backend.php', { method })`。
- GET `backend.php` 返回：`Get Flag ... wrong request method ... You have 9 more attempts before getting a hint.`
- 特征：服务端按 HTTP 方法分发，错误有次数提示（SESSION 计数），10 次后给 hint。

## 2. 利用
```bash
# 逐个试方法（带 cookie 保持会话计数）
for m in POST PUT DELETE PATCH OPTIONS TRACE CONNECT PROPFIND; do
    echo "$m: $(curl -s -X "$m" http://challenge.qsnctf.com:40832/backend.php)"
done
```
`POST` 返回：
```
flag{c66edbc33cab4d95a7765b6b097646e1}
```

## 3. 复盘 & 套路沉淀
1. **"wrong request method" = HTTP 方法猜谜题**：后端只对某个方法返回内容。全家桶逐个试：`POST / PUT / PATCH / DELETE / OPTIONS / HEAD / TRACE / CONNECT / PROPFIND`。
2. **curl 切方法**：`-X POST`（或 `-d` 自动变 POST）；保持 `-b/-c cookie` 让会话连续（尝试次数是 SESSION 记的）。
3. **提示机制是考点信号**："10 次后给 hint" = 出题人默认你会在浏览器里瞎点，提示你该换工具了。
4. 为什么 405 只拦 TRACE：nginx 层默认只放行少数方法，其余到 PHP 层判断——**方法分发的位置（nginx vs 应用）也是一种线索**。
