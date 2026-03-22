import tkinter as tk # 导入GUI模块
from tkinter import messagebox # 导入消息对话框
import os # 导入系统模块
import subprocess # 导入子进程模块
import re # 导入正则模块

class BoxEngine: # 定义图形化游戏引擎类
    def __init__(self, rt): # 构造函数
        self.rt = rt # 设置根窗口
        self.rt.title("TomatoBox Professional - Game Engine") # 设置标题
        self.rt.geometry("1000x800") # 设置窗口尺寸
        self.tb = tk.Frame(rt) # 创建工具栏
        self.tb.pack(side=tk.TOP, fill=tk.X) # 放置工具栏
        self.bt_nw = tk.Button(self.tb, text="New Scene", command=self.nw_s) # 新建场景按钮
        self.bt_nw.pack(side=tk.LEFT) # 放置按钮
        self.bt_rn = tk.Button(self.tb, text="Play Game", command=self.cl_g, bg="orange") # 运行游戏按钮
        self.bt_rn.pack(side=tk.LEFT, padx=10) # 放置按钮
        self.pw = tk.PanedWindow(rt, orient=tk.VERTICAL) # 创建分窗
        self.pw.pack(expand=True, fill=tk.BOTH) # 放置分窗
        self.txt = tk.Text(self.pw, font=("Consolas", 12), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white") # 创建代码编辑器
        self.pw.add(self.txt) # 添加编辑器
        self.out = tk.Text(self.pw, height=12, bg="black", fg="#00ff00", font=("Consolas", 10)) # 创建输出台
        self.pw.add(self.out) # 添加输出台
        self.f_p = "GameCore.tmc" # 默认场景文件
        self.tag_cfg() # 初始化高亮配置
        self.txt.bind("<KeyRelease>", self.hi_l) # 绑定高亮事件

    def tag_cfg(self): # 配置语法高亮标签
        self.txt.tag_config("kw", foreground="#569cd6") # 关键字浅蓝色
        self.txt.tag_config("st", foreground="#ce9178") # 字符串橙红色
        self.txt.tag_config("cm", foreground="#6a9955") # 注释绿色
        self.txt.tag_config("tm", foreground="#c586c0") # 指令紫色

    def hi_l(self, ev=None): # 高亮逻辑实现
        c = self.txt.get(1.0, tk.END) # 获取代码
        for t in ["kw", "st", "cm", "tm"]: # 清除旧标签
            self.txt.tag_remove(t, "1.0", tk.END) # 执行清除
        kws = ["cout", "return", "break", "输出", "结束并返回", "跳出", "循环直到", "不成立", "申请空间"] # 关键字
        for k in kws: # 遍历匹配
            st = "1.0" # 搜索起点
            while True: # 循环搜索
                p = self.txt.search(k, st, stopindex=tk.END) # 执行搜索
                if not p: break # 结束
                e = f"{p}+{len(k)}c" # 结束位
                self.txt.tag_add("kw", p, e) # 加标签
                st = e # 更新起点
        for m in re.finditer(r'\".*?\"', c): # 匹配字符串
            s, e = m.span() # 获取范围
            self.txt.tag_add("st", f"1.0+{s}c", f"1.0+{e}c") # 加标签
        for m in re.finditer(r'//.*', c): # 匹配注释
            s, e = m.span() # 获取范围
            self.txt.tag_add("cm", f"1.0+{s}c", f"1.0+{e}c") # 加标签
        for m in re.finditer(r'#.*| \*\*.*', c): # 匹配指令
            s, e = m.span() # 获取范围
            self.txt.tag_add("tm", f"1.0+{s}c", f"1.0+{e}c") # 加标签

    def nw_s(self): # 创建场景模板
        c = [ # 场景代码模板
            "#*tomato-1.0.0.max // 全能版", 
            "#加载拓展 : <*游戏引擎内核>;",
            "#<*stdlc> : <*简体中文>",
            "{",
            "    申请空间(1024); // 申请1MB内存",
            "}",
            "**main : {",
            "    输出 \"TomatoBox Engine v1.0 Start...\";",
            "    输出 \"Loading Assets...\";",
            "    输出 \"Game Loop Started.\";",
            "    结束并返回 0;",
            "}"
        ] # 模板结束
        self.txt.delete(1.0, tk.END) # 清空编辑器
        self.txt.insert(tk.END, "\n".join(c)) # 插入模板
        self.hi_l() # 触发高亮

    def cl_g(self): # 构建并运行游戏
        with open(self.f_p, "w", encoding="utf-8") as f: # 保存当前编辑内容
            f.write(self.txt.get(1.0, tk.END)) # 执行写入
        self.log("Building Game Engine Core...") # 记录日志
        os.system(f"python tmc_compiler.py {self.f_p}") # 编译TMC
        c_p = self.f_p.replace('.tmc', '.cpp') # CPP路径
        e_p = self.f_p.replace('.tmc', '.exe') # EXE路径
        self.log("Compiling Kernel to Binary...") # 记录
        r = subprocess.run(f"g++ {c_p} -o {e_p}", shell=True, capture_output=True, text=True) # 编译CPP
        if r.returncode != 0: # 失败处理
            self.log(f"Kernel Error:\n{r.stderr}") # 输出错误
            return # 退出
        self.log("Launching Game Scene...") # 运行
        r2 = subprocess.run(e_p, shell=True, capture_output=True, text=True) # 执行exe
        self.log(f"--- Scene Log ---\n{r2.stdout}\n{r2.stderr}") # 输出日志

    def log(self, m): # 日志输出
        self.out.insert(tk.END, m + "\n") # 插入消息
        self.out.see(tk.END) # 滚动到底部

if __name__ == "__main__": # 入口
    r = tk.Tk() # 创建窗口
    b = BoxEngine(r) # 实例化
    r.mainloop() # 运行
