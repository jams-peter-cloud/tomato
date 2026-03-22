import os # 导入操作系统模块
import sys # 导入系统模块

def g_t(): # 生成游戏引擎核心模板
    c = [ # 初始化模板代码列表
        "#*tomato-1.0.0.max // 全能版以支持游戏引擎", # 版本声明
        "#加载拓展 : <*游戏引擎内核>;", # 加载游戏库
        "#<*stdlc> : <*简体中文>", # 库映射
        "{", # 开启主配置块
        "    申请空间(1024); // 申请1MB空间", # 申请内存
        "}", # 结束配置块
        "**main : {", # 主线程定义
        "    输出 \"TomatoBox Initializing...\";", # 初始化输出
        "    循环直到(1)不成立 {", # 开启游戏主循环
        "        输出 \"Game Frame Update...\";", # 帧更新输出
        "        结束并返回 0; // 防止卡死，实际应由引擎控制", # 逻辑返回
        "    }", # 结束循环
        "}" # 结束主线程
    ] # 模板内容定义完毕
    return "\n".join(c) # 返回合并后的字符串

def run_box(): # 引擎运行主逻辑
    print("\n--- TomatoBox (Game Engine) ---") # 打印引擎标题
    print("Creating new Scene: GameCore.tmc") # 提示创建新场景
    with open("GameCore.tmc", "w", encoding="utf-8") as f: # 创建并打开TMC文件
        f.write(g_t()) # 写入模板代码
    print("Scene generated successfully.") # 提示生成成功
    print("Compiling GameCore.tmc...") # 提示开始编译
    os.system("python tmc_compiler.py GameCore.tmc") # 调用编译器
    print("GameCore.cpp generated.") # 提示C++文件已生成

if __name__ == "__main__": # 判断主入口
    run_box() # 运行引擎主逻辑
