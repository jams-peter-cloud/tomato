import re # 导入正则模块
import sys # 导入系统模块

def exp(s): # 定义关键文到展开形式函数
    r = s # 初始化结果变量
    r = r.replace('cout(', '输出 ') # 转换输出语句
    r = r.replace('return ', '结束并返回 ') # 转换返回语句
    r = r.replace('break;', '跳出;') # 转换跳出语句
    r = r.replace('**main : {}', '直接启动线程 main :') # 转换主线程定义
    r = r.replace(');', ';') # 去除括号后缀
    return r # 返回结果

def to_core(s): # 定义关键文到CORE格式函数
    r = s # 初始化结果变量
    r = r.replace('cout(', 'TMC_OUTPUT_ALL(') # 核心输出函数
    r = r.replace('return ', 'TMC_END_AND_RETURN ') # 核心返回函数
    r = r.replace('break;', 'TMC_BREAK;') # 核心跳出函数
    r = r.replace('**main : {}', 'TMC_THREAD_MAIN : {}') # 核心主线程
    return r # 返回结果

def main(): # 定义主函数
    if len(sys.argv) < 3: # 检查参数数量
        print("Usage: python tmc_converter.py <mode: exp|core> <file>") # 输出用法
        return # 退出
    m = sys.argv[1] # 获取模式
    f_p = sys.argv[2] # 获取文件路径
    with open(f_p, 'r', encoding='utf-8') as f: # 打开文件
        ls = f.readlines() # 读取所有行
    for l in ls: # 遍历每一行
        t = l.strip() # 去除空白
        if m == 'exp': # 如果是展开模式
            print(exp(t)) # 输出展开内容
        elif m == 'core': # 如果是核心模式
            print(to_core(t)) # 输出CORE内容

if __name__ == "__main__": # 判断是否为主程序
    main() # 调用主函数
