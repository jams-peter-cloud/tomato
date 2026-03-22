import re # 导入正则
import sys # 导入系统

def t2c(l, ctx): # 翻译函数，带上下文
    l = l.split('//')[0].strip() # 清理注释
    if not l: return "" # 跳过空行
    if l.startswith('#*tomato'): # 版本
        return f"// TomatoCore Runtime v{l.split('-')[1]}" # 注释显示版本
    if l.startswith('#加载拓展') or l.startswith('#<*stdlc>'): # 库
        if not ctx.get('lib_loaded'): # 防止重复加载
            ctx['lib_loaded'] = True # 标记已加载
            return "#include \"tmc_runtime.h\"\nusing namespace std;" # 包含运行时
        return "" # 已加载则返回空
    if l.startswith('**main') or '启动线程 main' in l: # 主线程
        ctx['in_main'] = True # 标记进入主函数
        return "int main() {" # C++ 入口
    if '申请空间' in l: # 空间申请
        v = re.findall(r'\d+', l)[0] # 提取数值
        return f"    TMC_GETSPACE({v});" # 调用运行时函数
    if 'cout(' in l or '输出 ' in l or 'TMC_OUTPUT_ALL' in l: # 输出
        c = re.findall(r'\"(.*?)\"', l) # 提取内容
        v = c[0] if c else " " # 获取内容
        return f"    TMC_OUTPUT_ALL(\"{v}\");" # 调用运行时输出
    if 'return' in l or '结束并返回' in l: # 返回
        v = l.split()[-1].replace(';', '') # 提取值
        return f"    return {v};" # C++ 返回
    if '定义十进制数变量' in l: # 变量定义
        n = re.findall(r'<(.*?)>', l)[0] # 提取变量名
        v = re.findall(r'\[(.*?)\]', l) # 提取初始值或精度
        i = v[0] if v else "0" # 设置默认
        return f"    TMC_Decimal {n} = {i};" # C++ 变量定义
    if '循环直到' in l and '不成立' in l: # 循环支持
        c = re.findall(r'\((.*?)\)', l)[0] # 提取条件
        return f"    while ({c}) {{" # 转换为 C++ while
    if '如果（' in l or '如果 (' in l: # 条件支持
        c = re.findall(r'\(|\（(.*?)\)|\）', l)[0] # 兼容中英文括号
        return f"    if ({c}) {{" # 转换为 C++ if
    if '否则' in l: # 否则
        return "    } else {" # 转换为 else
    if l == '{' or l == '}': # 括号
        return l # 保持
    return l # 原样返回

def main(): # 主逻辑
    if len(sys.argv) < 2: # 参数检查
        print("Usage: python tmc_compiler.py <file.tmc>") # 用法
        return # 退出
    f_p = sys.argv[1] # 获取路径
    o_p = f_p.replace('.tmc', '.cpp') # 生成输出名
    with open(f_p, 'r', encoding='utf-8') as f: # 读取
        ls = f.readlines() # 获取行
    
    ctx = {'lib_loaded': False, 'in_main': False} # 上下文状态
    cs = [] # 主代码缓存
    pre_b = [] # 预处理块内容
    in_pre = False # 是否在预处理块中

    for l in ls: # 翻译循环
        tl = l.split('//')[0].strip() # 清理注释
        if not tl: continue # 跳过空行
        
        if tl == '{' and not ctx['in_main']: # 还没进 main 且遇到 {
            in_pre = True # 标记进入预处理块
            continue # 不加入代码流
        if tl == '}' and in_pre: # 预处理块结束
            in_pre = False # 标记结束
            continue # 不加入代码流
            
        if in_pre: # 如果在预处理块中
            pre_b.append(t2c(tl, ctx)) # 翻译并存入预处理缓存
        else: # 正常代码流
            tr = t2c(l, ctx) # 翻译
            if tr: cs.append(tr) # 添加

    # 合并代码：将预处理块内容（申请空间等）插入 main 开头
    f_cs = [] # 最终代码列表
    for c in cs: # 遍历代码
        f_cs.append(c) # 添加代码
        if c.startswith('int main() {'): # 找到 main 入口
            f_cs.extend(pre_b) # 插入预处理逻辑
            
    with open(o_p, 'w', encoding='utf-8') as f: # 写入文件
        f.write('\n'.join(f_cs)) # 写入全部内容
    print(f"Compiled: {o_p}") # 提示完成

if __name__ == "__main__": # 入口
    main() # 启动
