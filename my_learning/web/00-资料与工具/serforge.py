#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serforge.py —— 快速构造 PHP 序列化字符串（CTF 反序列化伪造对象神器）

为什么需要它：手工数长度、拼 \x00 保护字符极容易出错。本工具按 PHP 规则自动算长度。

三种用法：
1) 当库 import：
   from serforge import serialize, obj
   s = serialize(obj("test", user="test", pswd="escaping"))

2) 命令行 JSON（public 属性 + 数组）：
   python serforge.py '{"__class__":"test","user":"test","pswd":"escaping"}'
   python serforge.py '{"name":"bob","age":18}'

3) 命令行支持 protected / private 可见性：
   python serforge.py '{"__class__":"User","*token":"abc","User@secret":"x"}'
   （键以 * 开头 = protected；键形如 Class@attr = private）

说明：protected / private 的属性名里含有 \x00 不可见字节。终端打印时
NUL 会被替换成 %00（URL 安全形式）方便复制进 payload；同时打印 repr 原始串。
"""

import sys
import json

NUL = "\x00"


def serialize(value):
    """递归把 Python 值转成 PHP 序列化字符串。"""
    if isinstance(value, _Obj):
        return value._ser()
    if value is True:
        return "b:1;"
    if value is False or value is None:
        return "b:0;"
    if isinstance(value, int):
        return f"i:{value};"
    if isinstance(value, float):
        return f"d:{value};"
    if isinstance(value, str):
        b = value.encode("utf-8")
        return f's:{len(b)}:"{value}";'
    if isinstance(value, (list, tuple)):
        parts = [serialize(i) + serialize(v) for i, v in enumerate(value)]
        return f"a:{len(value)}:{{{''.join(parts)}}}"
    if isinstance(value, dict):
        parts = [serialize(k) + serialize(v) for k, v in value.items()]
        return f"a:{len(value)}:{{{''.join(parts)}}}"
    raise TypeError(f"不支持的类型: {type(value).__name__}")


class _Obj:
    """表示一个 PHP 对象。props 是 [(php_key_str, value), ...]。"""

    def __init__(self, class_name, props):
        self.class_name = class_name
        self.props = props

    def _ser(self):
        body = "".join(serialize(k) + serialize(v) for k, v in self.props)
        cn = self.class_name.encode("utf-8")
        return f'O:{len(cn)}:"{self.class_name}":{len(self.props)}:{{{body}}}'


def obj(class_name, **props):
    """构造一个 PHP 对象。键名规则：
    - 普通键         -> public
    - 以 '*' 开头     -> protected  (如 "*token")
    - 形如 "Class@attr" -> private  (如 "User@secret")
    """
    out = []
    for k, v in props.items():
        if k.startswith("*") and len(k) > 1:
            out.append((f"{NUL}*{NUL}{k[1:]}", v))          # protected
        elif "@" in k:
            cls, _, attr = k.partition("@")
            if cls:
                out.append((f"{NUL}{cls}{NUL}{attr}", v))    # private
            else:
                out.append((k, v))
        else:
            out.append((k, v))                               # public
    return _Obj(class_name, out)


def from_json(data):
    """把 JSON 解析结果转成可序列化值。含 __class__ 的 dict 视为对象。"""
    if isinstance(data, dict) and "__class__" in data:
        cls = data.pop("__class__")
        return obj(cls, **data)
    return data


def _print_pair(label, s):
    safe = s.replace(NUL, "%00")
    print(f"[{label}] 可复制(URL安全): {safe}")
    print(f"[{label}] 原始repr      : {repr(s)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        data = json.loads(sys.argv[1])
        _print_pair("结果", serialize(from_json(data)))
    else:
        print("=== 自测示例 ===")
        _print_pair("对象 test(pswd=escaping)",
                    serialize(obj("test", user="test", pswd="escaping")))
        _print_pair("关联数组", serialize({"name": "bob", "age": 18}))
        _print_pair("索引数组", serialize(["a", "b", "c"]))
        _print_pair("protected", serialize(obj("User", **{"*token": "abc"})))
        _print_pair("private", serialize(obj("User", **{"User@secret": "x"})))
        print("\n提示: 传入 JSON 参数可自定义，例如:")
        print('  python serforge.py \'{"__class__":"test","pswd":"escaping"}\'')
