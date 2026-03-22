import os # 导入操作系统模块
import sys # 导入系统模块
import tmc_converter as cv # 导入转换模块
import tmc_compiler as cp # 导入编译模块

def menu(): # 定义菜单显示函数
    print("\n--- TomatoMap (Hardcore IDE) ---") # 打印IDE标题
    print("1. Render (Show Expanded Form)") # 选项1: 渲染显示展开形式
    print("2. Core (Show CORE Form)") # 选项2: 显示CORE形式
    print("3. Compile (Generate C++ Code)") # 选项3: 编译生成C++代码
    print("4. Exit (Quit IDE)") # 选项4: 退出IDE
    return input("Select: ") # 返回用户选择

def run_ide(): # 定义IDE运行主逻辑
    if len(sys.argv) < 2: # 检查是否提供了文件名
        print("Usage: python TomatoMap.py <file.tmc>") # 提示用法
        return # 退出
    f_p = sys.argv[1] # 获取TMC文件路径
    if not os.path.exists(f_p): # 检查文件是否存在
        print("File not found.") # 提示文件未找到
        return # 退出
    with open(f_p, 'r', encoding='utf-8') as f: # 打开TMC文件
        ls = f.readlines() # 读取所有行
    while True: # 开始交互循环
        s = menu() # 显示菜单并获取选择
        if s == '1': # 如果选择渲染
            for l in ls: # 遍历每一行
                print(cv.exp(l.strip())) # 调用转换器的展开函数
        elif s == '2': # 如果选择CORE
            for l in ls: # 遍历每一行
                print(cv.to_core(l.strip())) # 调用转换器的CORE函数
        elif s == '3': # 如果选择编译
            os.system(f"python tmc_compiler.py {f_p}") # 调用编译器脚本
            print("Compile successful.") # 提示编译成功
        elif s == '4': # 如果选择退出
            break # 跳出循环
        else: # 处理无效选择
            print("Invalid select.") # 提示选择无效

if __name__ == "__main__": # 判断主程序入口
    run_ide() # 执行IDE运行逻辑
