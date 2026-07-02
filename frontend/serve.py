"""开发用静态服务器:在 http.server 基础上强制不缓存,省得改前端代码后还要手动 disable cache。
跑法:py serve.py [port](默认 5501);start.bat 用它代替 python -m http.server。
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))   # 不管从哪调用,都从本文件所在目录(frontend/)提供服务
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5501
    ThreadingHTTPServer(("", port), NoCacheHandler).serve_forever()
