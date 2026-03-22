from http.server import HTTPServer, BaseHTTPRequestHandler # 导入基础服务器模块
import json # 导入JSON模块
import os # 导入系统模块
import subprocess # 导入子进程模块
import tmc_converter as cv # 导入转换模块
import sys # 导入系统

class StudioAPI(BaseHTTPRequestHandler): # 定义API处理器
    def _s_h(self, t='application/json'): # 设置响应头
        self.send_response(200) # 发送200状态
        self.send_header('Content-type', t) # 设置内容类型
        self.send_header('Access-Control-Allow-Origin', '*') # 允许跨域
        self.end_headers() # 结束头信息

    def do_GET(self): # 处理GET请求
        try: # 捕获异常
            if self.path == '/': # 访问根目录
                self._s_h('text/html') # 设置HTML头
                with open('studio_ui.html', 'rb') as f: # 读取UI文件
                    self.wfile.write(f.read()) # 返回UI内容
            elif self.path == '/api/files': # 获取文件列表API
                self._s_h() # 设置头
                fs = [f for f in os.listdir('.') if f.endswith('.tmc')] # 筛选TMC文件
                self.wfile.write(json.dumps({"files": fs}).encode('utf-8')) # 返回文件列表
        except Exception as e: # 错误处理
            print(f"[GET Error] {e}") # 打印错误
            self.send_error(500, str(e)) # 返回500

    def do_POST(self): # 处理POST请求
        try: # 捕获异常
            l = int(self.headers.get('Content-Length', 0)) # 获取内容长度
            raw = self.rfile.read(l).decode('utf-8') # 读取数据
            d = json.loads(raw) # 解析JSON
            print(f"[API] {self.path} Request received") # 打印日志
            
            res_data = {} # 准备返回数据
            
            if self.path == '/api/run': # 编译运行模式
                p = d.get('file', 'temp.tmc') # 文件名
                with open(p, 'w', encoding='utf-8') as f: # 保存
                    f.write(d['code']) # 写入
                os.system(f"{sys.executable} tmc_compiler.py {p}") # 编译TMC
                c_p = p.replace('.tmc', '.cpp') # CPP
                e_p = p.replace('.tmc', '.exe') # EXE
                r1 = subprocess.run(f"g++ {c_p} -o {e_p}", shell=True, capture_output=True, text=True) # 编译
                if r1.returncode != 0: # 失败
                    res_data = {"out": r1.stderr, "status": "Compile Error"} # 记录
                else: # 成功
                    r2 = subprocess.run(e_p, shell=True, capture_output=True, text=True) # 运行
                    res_data = {"out": r2.stdout + r2.stderr, "status": "Success"} # 记录
                
            elif self.path == '/api/interpret': # 原生引擎模式
                p = 'temp_run.tmc' # 临时文件
                with open(p, 'w', encoding='utf-8') as f: # 写入
                    f.write(d['code']) # 保存内容
                # 使用 sys.executable 确保使用当前的 python 环境
                r = subprocess.run([sys.executable, 'tmc_engine.py', p], capture_output=True, text=True, encoding='utf-8') # 运行引擎
                res_data = {"out": r.stdout + r.stderr, "status": "Native Engine"} # 准备结果
                
            elif self.path == '/api/convert': # 转换模式
                m = d.get('mode', 'exp') # 模式
                c = d.get('code', '') # 代码
                rl = [cv.exp(l) if m == 'exp' else cv.to_core(l) for l in c.splitlines()] # 批量转换
                res_data = {"res": "\n".join(rl)} # 准备结果
            else: # 未找到
                self.send_error(404) # 404
                return

            self._s_h() # 响应头
            self.wfile.write(json.dumps(res_data).encode('utf-8')) # 统一返回数据
            
        except Exception as e: # 错误处理
            print(f"[POST Error] {e}") # 打印错误
            # 即使报错也尝试返回一个 JSON，防止 fetch 失败
            try:
                self._s_h()
                self.wfile.write(json.dumps({"out": str(e), "status": "Server Error"}).encode('utf-8'))
            except:
                pass

if __name__ == '__main__': # 入口
    srv = HTTPServer(('localhost', 8080), StudioAPI) # 初始化
    print("TomatoStudio Pro Server Running at http://localhost:8080") # 消息
    srv.serve_forever() # 运行
