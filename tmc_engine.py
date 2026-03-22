import re # 导入正则
import sys # 导入系统

class Token: # 定义词法单元
    def __init__(self, t, v): # 构造函数
        self.t = t # 类型
        self.v = v # 值

class Lexer: # 定义词法分析器
    def __init__(self, s): # 构造函数
        self.s = s # 源代码
        self.ts = [] # Token 列表
        self.p = 0 # 当前指针

    def lex(self): # 执行词法分析
        ps = [ # 定义正则模式列表
            ('KW', r'cout|return|break|输出|结束并返回|跳出|如果|否则|循环直到|不成立'), # 关键字
            ('NUM', r'\d+\.?\d*'), # 数字
            ('STR', r'\".*?\"'), # 字符串
            ('ID', r'[a-zA-Z_]\w*|<.*?>|\[.*?\]'), # 标识符
            ('OP', r'\*\*|[:{}();=><+\-*/]'), # 符号
            ('CM', r'//.*'), # 注释
            ('SP', r'\s+'), # 空白
            ('VER', r'#\*.*'), # 版本指令
            ('LIB', r'#<.*?>|#加载拓展.*'), # 库加载
        ] # 模式列表结束
        while self.p < len(self.s): # 循环扫描源码
            m = None # 初始化匹配对象
            for t, r in ps: # 遍历所有模式
                re_m = re.compile(r) # 编译正则
                m = re_m.match(self.s, self.p) # 执行匹配
                if m: # 如果匹配成功
                    v = m.group(0) # 获取匹配值
                    if t not in ['SP', 'CM']: # 过滤空白和注释
                        self.ts.append(Token(t, v)) # 添加 Token
                    self.p = m.end() # 移动指针
                    break # 跳出当前循环
            if not m: # 如果没匹配到
                self.p += 1 # 强制前进跳过非法字符
        return self.ts # 返回 Token 流

class Node: # 定义语法树节点
    def __init__(self, t, v=None, c=None): # 构造函数
        self.t = t # 节点类型
        self.v = v # 节点值
        self.c = c or [] # 子节点列表

class Parser: # 定义语法解析器
    def __init__(self, ts): # 构造函数
        self.ts = ts # Token 列表
        self.p = 0 # 指针

    def p_s(self): # 解析主逻辑
        p_n = Node('Prog') # 创建程序根节点
        while self.p < len(self.ts): # 遍历 Token
            tk = self.ts[self.p] # 获取当前 Token
            if tk.t == 'VER' or tk.t == 'LIB': # 预处理指令
                p_n.c.append(Node('Dir', tk.v)) # 添加指令节点
                self.p += 1 # 前进
            elif tk.t == 'OP' and tk.v == '{': # 进入全局块
                p_n.c.append(self.p_b()) # 解析块内容
            elif tk.t == 'OP' and tk.v == '**': # 启动线程
                self.p += 1 # 跳过 **
                p_n.c.append(self.p_f()) # 解析函数
            else: # 其他语句
                p_n.c.append(self.p_e()) # 解析表达式
        return p_n # 返回 AST

    def p_b(self): # 解析代码块
        b_n = Node('Block') # 创建块节点
        self.p += 1 # 跳过 {
        while self.p < len(self.ts) and self.ts[self.p].v != '}': # 循环解析直到 }
            b_n.c.append(self.p_e()) # 添加表达式
        self.p += 1 # 跳过 }
        return b_n # 返回块

    def p_f(self): # 解析函数/线程
        n = self.ts[self.p].v # 获取名称
        self.p += 1 # 跳过 ID
        while self.p < len(self.ts) and self.ts[self.p].v != '{': self.p += 1 # 寻找左括号
        f_n = Node('Func', n) # 创建函数节点
        f_n.c.append(self.p_b()) # 解析函数体
        return f_n # 返回

    def p_e(self): # 解析语句
        tk = self.ts[self.p] # 获取当前 Token
        self.p += 1 # 前进
        if tk.t == 'KW' and tk.v in ['cout', '输出']: # 输出
            v = self.ts[self.p].v # 内容
            self.p += 1 # 跳过
            if self.p < len(self.ts) and self.ts[self.p].v == ';': self.p += 1 # 过滤分号
            return Node('Print', v) # 返回输出节点
        if '定义十进制数变量' in tk.v: # 变量定义
            if self.ts[self.p].v == ':': self.p += 1 # 跳过冒号
            n = self.ts[self.p].v.strip('<>') # 获取名
            self.p += 1 # 跳过
            v = self.ts[self.p].v.strip('[]') # 获取值
            self.p += 1 # 跳过
            if self.p < len(self.ts) and self.ts[self.p].v == ';': self.p += 1 # 过滤分号
            return Node('VarDef', n, [Node('Val', v)]) # 返回节点
        return Node('Expr', tk.v) # 其他

class Interpreter: # 解释器
    def __init__(self, ast): # 构造
        self.ast = ast # 树
        self.m = {} # 内存

    def run(self, n): # 递归执行
        if n.t == 'Prog': # 程序
            for s in n.c: self.run(s) # 执行子节点
        elif n.t == 'Func': # 函数
            self.run(n.c[0]) # 执行块
        elif n.t == 'Block': # 块
            for s in n.c: self.run(s) # 执行语句
        elif n.t == 'Print': # 打印
            v = n.v.strip('"') # 去引号
            print(f"[TMC] {self.m.get(v, v)}") # 优先从内存取值
        elif n.t == 'VarDef': # 定义
            self.m[n.v] = n.c[0].v # 存入

def main(): # 主程序
    if len(sys.argv) < 2: # 检查参数
        print("Usage: python tmc_engine.py <file.tmc>") # 用法
        return # 退出
    with open(sys.argv[1], 'r', encoding='utf-8') as f: # 读取
        s = f.read() # 获取全文
    lx = Lexer(s) # 词法分析
    ts = lx.lex() # 获取 Token
    ps = Parser(ts) # 语法分析
    ast = ps.p_s() # 获取 AST
    it = Interpreter(ast) # 初始化解释器
    it.run(ast) # 启动执行并传入根节点

if __name__ == "__main__": # 入口
    main() # 启动
