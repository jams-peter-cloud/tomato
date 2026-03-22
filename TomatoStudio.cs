using System; // 核心
using System.Windows; // WPF 基础
using System.Windows.Controls; // WPF 控件
using System.Windows.Media; // WPF 绘图
using System.Windows.Input; // WPF 输入
using System.IO; // IO
using System.Collections.Generic; // 集合
using System.Text.RegularExpressions; // 正则
using System.Windows.Documents; // 文档
using System.Data; // 数据运算支持

public class TomatoStudio : Window { // 定义主窗体
    private RichTextBox ed; // 编辑器
    private TextBlock log; // 输出台
    private ScrollViewer logScroll; // 滚动条
    private Dictionary<string, double> mem = new Dictionary<string, double>(); // 变量内存

    [STAThread] // 单线程套间
    public static void Main() { // 入口
        Console.WriteLine("[DEBUG] Main method started."); // 调试日志
        try { // 捕获启动异常
            new Application().Run(new TomatoStudio()); // 启动应用
        





} catch (Exception ex) { // 弹出错误
            Console.WriteLine("[DEBUG] Startup exception caught: " + ex.Message); // 调试日志
            MessageBox.Show("启动失败: " + ex.Message + "\n" + ex.StackTrace, "番茄 Studio 启动错误", MessageBoxButton.OK, MessageBoxImage.Error); // 显示详细信息
        }
        Console.WriteLine("[DEBUG] Main method finished."); // 调试日志
    }

    public TomatoStudio() { // 构造函数
        Console.WriteLine("[DEBUG] TomatoStudio constructor started."); // 调试日志
        this.Title = "番茄 Studio Pro 旗舰版"; // 标题
        this.Width = 1100; // 宽度
        this.Height = 800; // 高度
        this.Background = new SolidColorBrush(Color.FromRgb(30, 30, 30)); // 背景色
        this.Foreground = Brushes.White; // 文字色
        this.WindowStartupLocation = WindowStartupLocation.CenterScreen; // 居中显示

        Grid g = new Grid(); // 主网格
        g.RowDefinitions.Add(new RowDefinition { Height = new GridLength(40) }); // 菜单行
        g.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) }); // 代码行
        g.RowDefinitions.Add(new RowDefinition { Height = new GridLength(200) }); // 控制台行
        this.Content = g; // 设置内容

        // 调试日志：在每个主要组件初始化前添加
        Console.WriteLine("[DEBUG] Initializing Menu..."); // 调试日志
        InitMenu(); // 初始化菜单
        Console.WriteLine("[DEBUG] Menu Initialized."); // 调试日志
        Console.WriteLine("[DEBUG] Initializing Layout..."); // 调试日志
        InitLayout(); // 初始化布局
        Console.WriteLine("[DEBUG] Layout Initialized."); // 调试日志
        Console.WriteLine("[DEBUG] Initializing Editor..."); // 调试日志
        InitEditor(); // 初始化编辑器
        Console.WriteLine("[DEBUG] Editor Initialized."); // 调试日志
        
        SetText("#tomato-2.0\nmain {\n    num a = 50;\n    num b = 40.5;\n    out \"原生环境运行成功！\";\n    out a + b;\n    ret 0;\n}"); // 默认
        Console.WriteLine("[DEBUG] TomatoStudio constructor finished."); // 调试日志
    }

    private void SetText(string t) { // 设置文本并应用高亮
        ed.Document.Blocks.Clear(); // 清空
        var p = new Paragraph(); // 创建段落
        p.Inlines.Add(new Run(t)); // 添加文本
        ed.Document.Blocks.Add(p); // 放入文档
        ApplyHi(); // 应用初始高亮
    }

    private void ApplyHi() { // 优化的高亮逻辑
        string src = new TextRange(ed.Document.ContentStart, ed.Document.ContentEnd).Text; // 获取
        if (string.IsNullOrEmpty(src)) return; // 判空

        ed.TextChanged -= (s, e) => ApplyHi(); // 解绑
        
        TextPointer caret = ed.CaretPosition; // 记录
        int offset = ed.Document.ContentStart.GetOffsetToPosition(caret); // 偏移

        Paragraph p = new Paragraph(); // 新段落
        string pat = @"(//.*)|("".*?"")|(\b\d+\b)|(\b(main|out|ret|num|if|else|while|for)\b)|(#.*)"; // 正则
        
        int last = 0; // 索引
        foreach (Match m in Regex.Matches(src, pat)) { // 遍历
            if (m.Index > last) p.Inlines.Add(new Run(src.Substring(last, m.Index - last))); // 普通
            
            Run r = new Run(m.Value); // 着色
            if (m.Groups[1].Success) r.Foreground = Brushes.Green; // 注释
            else if (m.Groups[2].Success) r.Foreground = Brushes.Orange; // 串
            else if (m.Groups[3].Success) r.Foreground = Brushes.LightGreen; // 数
            else if (m.Groups[4].Success) r.Foreground = Brushes.DeepSkyBlue; // 键
            else if (m.Groups[6].Success) r.Foreground = Brushes.HotPink; // 指
            
            p.Inlines.Add(r); // 添加
            last = m.Index + m.Length; // 更新
        }
        if (last < src.Length) p.Inlines.Add(new Run(src.Substring(last))); // 剩余

        ed.Document.Blocks.Clear(); // 清空
        ed.Document.Blocks.Add(p); // 替换

        try { // 还原
            TextPointer next = ed.Document.ContentStart.GetPositionAtOffset(offset); // 获取
            if (next != null) ed.CaretPosition = next; // 设置
        } catch {}

        ed.TextChanged += (s, e) => ApplyHi(); // 还原绑定
    }

    private void RunCode() { // 运行逻辑
        log.Text = "[番茄内核] 正在启动原生解释引擎...\n"; // 日志
        mem.Clear(); // 清空内存
        string src = new TextRange(ed.Document.ContentStart, ed.Document.ContentEnd).Text; // 获取代码
        try { // 尝试执行
            int lineNum = 0; // 行号计数
            foreach (string l in src.Split('\n')) { // 按行执行
                lineNum++; // 递增行号
                string t = l.Trim(); // 去空
                if (string.IsNullOrEmpty(t) || t.StartsWith("//") || t.StartsWith("#") || t == "{" || t == "}") continue; // 跳过
                if (t.StartsWith("out")) { // 处理输出
                    string v = t.Substring(3).Trim().TrimEnd(';'); // 提取参数
                    if (v.StartsWith("\"")) { // 字符串字面量
                        log.Text += ">> " + v.Trim('"') + "\n"; // 输出
                    } else { // 表达式或变量
                        log.Text += ">> " + Eval(v) + "\n"; // 计算并输出
                    }
                } else if (t.StartsWith("num")) { // 处理定义
                    string[] p = t.Substring(3).Trim().Split('='); // 分割赋值
                    if (p.Length == 2) { // 成功分割
                        string varName = p[0].Trim(); // 变量名
                        string expr = p[1].Trim().TrimEnd(';'); // 表达式
                        mem[varName] = Eval(expr); // 计算并存入
                    }
                } else if (t.StartsWith("ret")) { // 处理返回
                    log.Text += "[系统] 程序退出，返回码: " + t.Substring(3).Trim().TrimEnd(';') + "\n"; // 输出返回信息
                } else if (!t.StartsWith("main")) { // 修改：支持 main 后跟空格或左括号
                    throw new Exception("第 " + lineNum + " 行: 未知指令 '" + t + "'"); // 报错
                }
            }
            log.Text += "[番茄内核] 运行结束。\n"; // 日志
        } catch (Exception ex) { // 异常捕获
            log.Text += "[运行错误] " + ex.Message + "\n"; // 显示详细错误
        }
        logScroll.ScrollToEnd(); // 自动滚动到底部
    }

    private void InitEditor() { // 初始化编辑器
        Grid mainGrid = (Grid)this.Content; // 获取主网格

        ed = new RichTextBox(); // 编辑器
        ed.Background = new SolidColorBrush(Color.FromRgb(40, 40, 40)); // 背景色
        ed.Foreground = Brushes.White; // 文字色
        ed.BorderBrush = Brushes.Transparent; // 无边框
        ed.FontFamily = new FontFamily("Consolas"); // 字体
        ed.FontSize = 14; // 字号
        ed.VerticalScrollBarVisibility = ScrollBarVisibility.Auto; // 自动滚动条
        ed.TextChanged += (s, e) => ApplyHi(); // 绑定高亮事件
        Grid.SetRow(ed, 1); // 放置在第二行
        ((Grid)((Grid)mainGrid.Children[1]).Children[0]).Children.Add(ed); // 添加到编辑器区域网格

        log = new TextBlock(); // 输出台
        log.Background = new SolidColorBrush(Color.FromRgb(20, 20, 20)); // 背景色
        log.Foreground = Brushes.LightGray; // 文字色
        log.FontFamily = new FontFamily("Consolas"); // 字体
        log.FontSize = 12; // 字号
        log.Padding = new Thickness(5); // 内边距

        logScroll = new ScrollViewer(); // 滚动视图
        logScroll.Content = log; // 放入输出台
        logScroll.VerticalScrollBarVisibility = ScrollBarVisibility.Auto; // 自动滚动条
        Grid.SetRow(logScroll, 2); // 放置在第三行
        ((Grid)((Grid)mainGrid.Children[2]).Children[0]).Children.Add(logScroll); // 添加到控制台区域网格
    }

    private void InitMenu() { // 初始化菜单
        DockPanel menuPanel = new DockPanel(); // 菜单面板
        menuPanel.Background = new SolidColorBrush(Color.FromRgb(45, 45, 48)); // 背景色
        Grid.SetRow(menuPanel, 0); // 放置在第一行
        ((Grid)this.Content).Children.Add(menuPanel); // 添加到主网格

        Menu mainMenu = new Menu(); // 主菜单
        mainMenu.Background = Brushes.Transparent; // 透明背景
        mainMenu.Foreground = Brushes.White; // 文字色
        menuPanel.Children.Add(mainMenu); // 添加到面板

        MenuItem fileMenu = new MenuItem { Header = "文件" }; // 文件菜单
        fileMenu.Items.Add(new MenuItem { Header = "新建" }); // 新建
        fileMenu.Items.Add(new MenuItem { Header = "打开" }); // 打开
        fileMenu.Items.Add(new MenuItem { Header = "保存" }); // 保存
        mainMenu.Items.Add(fileMenu); // 添加到主菜单

        MenuItem runMenu = new MenuItem { Header = "运行" }; // 运行菜单
        runMenu.Click += (s, e) => RunCode(); // 绑定运行事件
        mainMenu.Items.Add(runMenu); // 添加到主菜单
    }

    private void InitLayout() { // 初始化布局
        Grid mainGrid = (Grid)this.Content; // 获取主网格

        Grid editorGrid = new Grid(); // 编辑器区域网格
        editorGrid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) }); // 编辑器行
        Grid.SetRow(editorGrid, 1); // 放置在第二行
        mainGrid.Children.Add(editorGrid); // 添加到主网格

        Grid consoleGrid = new Grid(); // 控制台区域网格
        consoleGrid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) }); // 控制台行
        Grid.SetRow(consoleGrid, 2); // 放置在第三行
        mainGrid.Children.Add(consoleGrid); // 添加到主网格
    }

    private double Eval(string expr) { // 表达式求值
        string r = expr; // 复制
        foreach (var kv in mem) r = r.Replace(kv.Key, kv.Value.ToString()); // 替换变量
        return Convert.ToDouble(new DataTable().Compute(r, null)); // 计算
    }
}
