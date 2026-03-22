import tkinter as tk # 导入GUI模块
from tkinter import filedialog, messagebox # 导入对话框模块
import tmc_converter as cv # 导入转换模块
import tmc_compiler as cp # 导入编译模块
import os # 导入系统模块
import subprocess # 导入子进程模块
import re # 导入正则模块

class MapIDE: # 定义高级IDE类
    def __init__(self, rt): # 构造函数
        self.rt = rt # 设置主窗口
        self.rt.title("TomatoMap Professional IDE") # 设置标题
        self.rt.geometry("900x700") # 设置窗口大小
        self.tb = tk.Frame(rt) # 创建工具栏
        self.tb.pack(side=tk.TOP, fill=tk.X) # 放置工具栏
        self.bt_op = tk.Button(self.tb, text="Open", command=self.op_f) # 打开按钮
        self.bt_op.pack(side=tk.LEFT) # 放置打开按钮
        self.bt_sv = tk.Button(self.tb, text="Save", command=self.sv_f) # 保存按钮
        self.bt_sv.pack(side=tk.LEFT) # 放置保存按钮
        self.bt_rn = tk.Button(self.tb, text="RUN", command=self.run_c, bg="green", fg="white") # 运行按钮
        self.bt_rn.pack(side=tk.LEFT, padx=5) # 放置运行按钮
        self.bt_cl = tk.Button(self.tb, text="Compile", command=self.cl_c) # 编译按钮
        self.bt_cl.pack(side=tk.LEFT) # 放置编译按钮
        self.pw = tk.PanedWindow(rt, orient=tk.VERTICAL) # 创建分窗容器
        self.pw.pack(expand=True, fill=tk.BOTH) # 放置分窗容器
        self.txt = tk.Text(self.pw, font=("Consolas", 14), undo=True) # 创建主编辑器
        self.pw.add(self.txt) # 添加编辑器到分窗
        self.out = tk.Text(self.pw, height=10, bg="black", fg="white", font=("Consolas", 12)) # 创建输出台
        self.pw.add(self.out) # 添加输出台到分窗
        self.f_p = "" # 当前文件路径
        self.txt.bind("<KeyRelease>", self.hi_l) # 绑定按键释放事件用于高亮
        self.tag_cfg() # 初始化标签颜色

    def tag_cfg(self): # 配置高亮标签
        self.txt.tag_config("kw", foreground="blue") # 关键字蓝色
        self.txt.tag_config("st", foreground="brown") # 字符串褐色
        self.txt.tag_config("cm", foreground="green") # 注释绿色
        self.txt.tag_config("tm", foreground="red") # 特殊指令红色

    def hi_l(self, ev=None): # 实现高亮逻辑
        c = self.txt.get(1.0, tk.END) # 获取全文内容
        for t in ["kw", "st", "cm", "tm"]: # 遍历所有标签
            self.txt.tag_remove(t, "1.0", tk.END) # 先清除旧标签
        kws = ["cout", "return", "break", "输出", "结束并返回", "跳出"] # 定义关键字列表
        for k in kws: # 遍历关键字
            st = "1.0" # 开始搜索位置
            while True: # 循环搜索
                p = self.txt.search(k, st, stopindex=tk.END) # 查找关键字
                if not p: break # 没找到则跳出
                e = f"{p}+{len(k)}c" # 计算结束位置
                self.txt.tag_add("kw", p, e) # 添加关键字标签
                st = e # 更新搜索起点
        for m in re.finditer(r'\".*?\"', c): # 正则匹配字符串
            s, e = m.span() # 获取匹配起止
            self.txt.tag_add("st", f"1.0+{s}c", f"1.0+{e}c") # 添加字符串标签
        for m in re.finditer(r'//.*', c): # 正则匹配注释
            s, e = m.span() # 获取匹配起止
            self.txt.tag_add("cm", f"1.0+{s}c", f"1.0+{e}c") # 添加注释标签
        for m in re.finditer(r'#.*| \*\*.*', c): # 正则匹配特殊指令
            s, e = m.span() # 获取匹配起止
            self.txt.tag_add("tm", f"1.0+{s}c", f"1.0+{e}c") # 添加特殊指令标签

    def op_f(self): # 打开文件
        p = filedialog.askopenfilename(filetypes=[("TMC", "*.tmc")]) # 选择文件
        if p: # 如果选择了
            self.f_p = p # 记录路径
            with open(p, 'r', encoding='utf-8') as f: # 读取
                self.txt.delete(1.0, tk.END) # 清空
                self.txt.insert(tk.END, f.read()) # 插入
            self.hi_l() # 立即高亮一次

    def sv_f(self): # 保存文件
        if not self.f_p: # 没路径则另存为
            self.f_p = filedialog.asksaveasfilename(defaultextension=".tmc") # 弹框
        if self.f_p: # 有路径则写入
            with open(self.f_p, 'w', encoding='utf-8') as f: # 写入
                f.write(self.txt.get(1.0, tk.END)) # 写入内容

    def cl_c(self): # 编译逻辑
        self.sv_f() # 先保存
        if not self.f_p: return # 没路径则退出
        os.system(f"python tmc_compiler.py {self.f_p}") # 运行编译脚本
        self.log(f"TMC compiled to CPP: {self.f_p.replace('.tmc', '.cpp')}") # 记录日志

    def run_c(self): # 运行逻辑
        self.cl_c() # 先执行编译
        c_p = self.f_p.replace('.tmc', '.cpp') # 获取CPP路径
        e_p = self.f_p.replace('.tmc', '.exe') # 获取EXE路径
        self.log("Attempting to compile C++...") # 记录开始
        r = subprocess.run(f"g++ {c_p} -o {e_p}", shell=True, capture_output=True, text=True) # 尝试用g++编译
        if r.returncode != 0: # 编译失败
            self.log(f"C++ Compile Error:\n{r.stderr}") # 输出错误
            return # 退出
        self.log("Running executable...") # 记录运行开始
        r2 = subprocess.run(e_p, shell=True, capture_output=True, text=True) # 运行生成的exe
        self.log(f"--- Program Output ---\n{r2.stdout}\n{r2.stderr}") # 输出程序运行结果

    def log(self, m): # 日志输出到控制台
        self.out.insert(tk.END, m + "\n") # 插入消息
        self.out.see(tk.END) # 滚动到底部

if __name__ == "__main__": # 主入口
    r = tk.Tk() # 创建窗口
    m = MapIDE(r) # 实例化
    r.mainloop() # 循环运行
