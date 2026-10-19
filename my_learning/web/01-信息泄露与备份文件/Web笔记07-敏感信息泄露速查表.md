# Web笔记07-敏感信息泄露速查表（Hello-CTF 专栏 1）

> 来源：docs/hc-web/sensitive_info.md 蒸馏 ｜ 日期：2026-08-01
> 口诀：**备份、配置、版本控制、历史记录**——都是开发者"忘了删"的敏感信息

## 总览（12 种，✅=已做过）

| 泄露类型 | 状态 | 发现手段 | 利用 |
|---|---|---|---|
| 代码注释 | ✅ | F12/Ctrl+U | 注释里直接藏 flag |
| JS 源码 | ✅ | 看引入的 .js | 下载 grep flag |
| .git | ✅ | 目录扫描 | git log / git show / git-dumper |
| .swp | ✅ | 目录扫描 | 下载提取源码（swp_extract.py） |
| .bak 备份 | ⬜ | 目录扫描 | 访问 `xxx.php.bak` / `xxx.php~` 下载源码 |
| robots.txt | ⬜ | 直接访问 /robots.txt | 看爬虫规则里的隐藏路径 |
| .DS_Store | ⬜ | 访问 /.DS_Store | 解析目录清单拿文件名 |
| .svn | ⬜ | 目录扫描 .svn/ | rip-svn.pl 克隆仓库 |
| .hg | ⬜ | 目录扫描 .hg/ | rip-hg.pl 克隆仓库 |
| SSL 证书 | ⬜ | 证书查询站 | 查域名 HTTPS 启用时间等 |
| 历史信息 | ⬜ | web.archive.org | 找网站旧快照翻 flag |
| JS 接口 | ⬜ | 读 JS 找接口 | 测隐藏参数（arjun 工具） |

## 新知识点详解

### .bak 文件泄露
- 备份习惯：`index.php` → `index.php.bak`、`index.php~`、`index.php.swp`、`1.php.bak`
- 直接访问对应 URL 下载 → 得到源码 → 审计
- 关键：**备份文件不会被 PHP 执行**（.bak 后缀），所以能看到明文源码

### robots.txt
- 写给搜索引擎爬虫看的"禁区清单"，但人也能看
- 常列出：`/flag.php`、`/admin`、`/secret` 等敏感路径
- 例：robots.txt 说 Disallow: /result.php → 访问 /result.php 拿源码 → 结合题目传参

### .DS_Store（MacOS）
- MacOS 在每个文件夹自动生成的"目录索引"文件
- 部署时从 Mac 拷贝网站没删它 → 访问 `/.DS_Store` 下载
- 解析工具：`python-dsstore`（GitHub: gehaxelt/Python-dsstore）
- 得到目录内所有文件名清单 → 找到隐藏文件

### .svn / .hg（版本控制元数据）
- SVN 的 `.svn/`、Mercurial 的 `.hg/` 和 Git 的 `.git/` 同理：元数据泄露
- `.svn/` 关键文件：`wc.db`（SQLite 数据库，记录全部文件状态，用 sqlite3 查）、`pristine/`（存原始文件内容）、`entries`（旧版）
- `.hg/` 关键文件：`00changelog.i`（提交历史索引）、`dirstate`（工作区状态）、`store/`（版本数据核心）
- 工具：`dvcs-ripper` 的 `rip-svn.pl` / `rip-hg.pl`
```perl
perl rip-svn.pl -u http://目标/.svn/
perl rip-hg.pl  -u http://目标/.hg/
```

### SSL 证书 / 历史信息（信息搜集向）
- SSL 证书：在线证书查询站查域名的证书信息（启用时间等）
- 历史信息：`web.archive.org` 提供全球网站历史快照，按题目给的时间找旧版页面

### JS 接口泄露（进阶）
- 读 JS 源码发现 PHP 接口 + 提示"只允许本地访问"
- 用 `arjun` 工具扫隐藏参数：`pip install arjun` → `arjun -u http://目标/接口.php`
- 本地访问限制绕过：SSRF（`?shell=http://localtest.me/secret.php` 域名跳转绕过）

## 做题流程（敏感信息泄露章通用）
```
① 打开页面：F12/Ctrl+U 看注释、JS 文件 ← 最基础
② 直接访问常见路径：/robots.txt /.DS_Store /flag.txt /xxx.bak
③ 目录扫描（mini_scanner）：找 .git/.svn/.hg/.bak/备份文件
④ 拿到源码 → 审计（找 flag 或下一个漏洞）
```

## 已做过的题（复习）
- 3861 我Flag呢 → 注释泄露
- 3862 就当无事发生 → .git 泄露
- 3863/3871 导弹迷踪/1zjs → JS 源码
- 3866 Vim yyds → .swp 泄露
