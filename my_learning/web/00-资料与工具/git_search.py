"""
git 仓库自动搜索 flag 脚本（通用）
用法：python git_search.py <仓库目录>
原理：遍历仓库里所有 blob（当前文件+历史版本+悬空对象），逐个搜 flag 特征
      + 检查提交说明 + 列出分支/暂存/reflog
输出：找到的 flag 及其位置（文件路径 / 提交哈希 / 提交说明）
"""
import subprocess
import sys
import re
import os

FLAG_PATTERN = re.compile(
    r'(flag\d?\s*[:=]?\s*[A-Za-z0-9_!@#$%^&*\-{}.]+\}|'
    r'flag\d?\s*[:=]\s*[A-Za-z0-9_!@#$%^&*\-{}./\s]+|'
    r'f[1lI!][4aA@][g9q]\s*[:=]?\s*\{?[A-Za-z0-9_!@#$%^&*\-{}.]{3,}\}?|'
    r'[A-Za-z0-9_]{2,}\{[A-Za-z0-9_!@#$%^&*\-{}./]{5,}\})',
    re.I)


def run_git(repo, args):
    try:
        r = subprocess.run(['git', '-C', repo] + args,
                           capture_output=True, timeout=30,
                           encoding='utf-8', errors='replace')
        return r.stdout
    except Exception:
        return ''


def check(content):
    return FLAG_PATTERN.findall(content or '')


def main(repo):
    if not os.path.isdir(os.path.join(repo, '.git')):
        print('[!] 不是 git 仓库（没有 .git 目录）:', repo)
        return

    print('=' * 50)
    print('[1/5] 列出所有版本的所有文件（含历史）...')
    blobs = {}  # hash -> path
    out = run_git(repo, ['rev-list', '--objects', '--all'])
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            blobs[parts[0]] = parts[1]

    print(f'      共 {len(blobs)} 个文件版本')
    print('[2/5] 逐个搜索文件内容...')
    found = []
    for h, path in blobs.items():
        content = run_git(repo, ['cat-file', 'blob', h])
        flags = check(content)
        for f in flags:
            found.append((path, h, f))
            print(f'  [文件] {path} (blob {h[:8]}) → {f}')

    print('[3/5] 搜索悬空对象（被删的提交/文件）...')
    out = run_git(repo, ['fsck', '--lost-found'])
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) == 3 and parts[0] == 'dangling':
            obj = parts[2]
            content = run_git(repo, ['cat-file', 'blob', obj])
            flags = check(content)
            for f in flags:
                found.append(('(悬空对象)', obj, f))
                print(f'  [悬空] {obj} → {f}')

    print('[4/5] 检查提交说明...')
    out = run_git(repo, ['log', '--all', '--format=%H %s'])
    for line in out.splitlines():
        if re.search(r'flag|f1ag|secret|key|删除|delete|remove', line, re.I):
            print(f'  [提交] {line[:80]}')

    print('[5/5] 分支/暂存/reflog 概览...')
    branch = run_git(repo, ['branch', '-a']).strip()
    stash = run_git(repo, ['stash', 'list']).strip()
    print('  分支:', branch.replace('\n', ' | ') if branch else '无')
    print('  暂存:', stash.replace('\n', ' | ') if stash else '无')

    print('=' * 50)
    if found:
        print(f'找到 {len(found)} 个 flag 片段！')
    else:
        print('未找到 flag 片段（检查是否有编码/提交说明提示/其他隐藏点）')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        repo = input('请输入仓库目录路径: ').strip()
        if not repo:
            print('用法: python git_search.py <仓库目录>')
            input('按回车退出...')
            sys.exit(1)
        main(repo)
        input('\n按回车退出...')
    else:
        main(sys.argv[1])
