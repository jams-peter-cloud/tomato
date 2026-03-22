#ifndef TMC_RUNTIME_H // 防止头文件重复包含
#define TMC_RUNTIME_H // 定义宏

#include <iostream> // 导入标准流
#include <string> // 导入字符串库
#include <vector> // 导入向量容器
#include <cstdio> // 导入标准IO
#include <cstdlib> // 导入标准工具库

// --- 内存管理 ---
void* g_mem = nullptr; // 全局内存指针
void TMC_GETSPACE(int kb) { // 申请空间函数
    g_mem = malloc(kb * 1024); // 按KB申请内存
    if (g_mem) printf("[TMC] Allocated %d KB\n", kb); // 输出分配信息
}

// --- 核心输出 ---
template<typename T>
void TMC_OUTPUT_ALL(T v) { // 核心输出模板函数
    std::cout << v << std::endl; // 输出值并换行
}

// --- 类型定义 ---
typedef double TMC_Decimal; // 定义十进制数类型
typedef std::string TMC_String; // 定义字符串类型
typedef bool TMC_Bool; // 定义布尔类型

// --- 流程控制 ---
#define TMC_END_AND_RETURN return // 结束返回
#define TMC_BREAK break // 跳出
#define TMC_THREAD_MAIN int main() // 主线程

#endif // TMC_RUNTIME_H
