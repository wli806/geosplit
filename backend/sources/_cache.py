"""磁盘缓存(层内私有工具)。key=hash(标识),存 JSON。

带 VERSION 便于整体失效(Stage 0 踩过"缓存没带版本号导致看旧结果"的坑)。
取数确定性 → 该缓存;底层数据可更新 → 调用方按需给 ttl。
"""
import os
import json
import hashlib
import time

_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache")
VERSION = "v1"


def _path(key):
    h = hashlib.sha1(f"{VERSION}:{key}".encode("utf-8")).hexdigest()
    return os.path.join(_DIR, h + ".json")


def get(key, ttl=None):
    p = _path(key)
    if not os.path.exists(p):
        return None
    if ttl is not None and (time.time() - os.path.getmtime(p)) > ttl:
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def put(key, value):
    os.makedirs(_DIR, exist_ok=True)
    with open(_path(key), "w", encoding="utf-8") as f:
        json.dump(value, f)
    return value
