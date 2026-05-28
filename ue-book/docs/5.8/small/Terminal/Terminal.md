# Terminal

> Native Slate terminal emulator.

| 属性 | 值 |
|---|---|
| 中文名 | 终端模拟器 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Terminal` (Editor), `TerminalTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal) | |

## 用途

这是一个在 Unreal Editor 内嵌原生终端模拟器的插件。它通过 Slate 的 `SLeafWidget` 直接在 `OnPaint` 中逐字符单元格渲染终端画面，不依赖任何外部 UI 框架，也不需要蓝图资产。

插件的核心价值在于：在编辑器中提供一个功能完备的终端窗口，支持 VT/ANSI 转义序列、256 色、鼠标追踪、选区复制粘贴、滚动回看等功能。底层通过平台原生 PTY 接口（Windows 使用 ConPTY，Linux/macOS 使用 POSIX PTY）与系统 Shell 进程通信，由后台 I/O 线程读取输出并在游戏线程上解析渲染。

这解决的问题是：开发者经常需要在编辑器和外部终端之间频繁切换来执行构建脚本、运行命令行工具或查看日志。该插件将终端直接嵌入编辑器的 Dock Tab 中，减少上下文切换开销。

## 使用场景

- 你需要在 UE 编辑器内直接运行 Shell 命令（编译、Git、构建脚本等） → 用 Terminal 插件
- 你想在编辑器中查看长时间运行的命令输出而不需要切换窗口 → 用 Terminal 插件
- 你需要一个支持 VT 转义序列、颜色、鼠标追踪的完整终端体验 → 用 Terminal 插件

## 蓝图用法

本插件是纯 Slate/C++ 实现，不暴露任何 `BlueprintCallable` 节点。终端的配置通过 `UTerminalSettings`（编辑器设置面板）完成。

### 编辑器设置项

在 **编辑 → 编辑器偏好设置 → Terminal** 中可配置以下选项：

| 设置 | 说明 | 默认值 |
|---|---|---|
| ShellExecutablePath | Shell 可执行文件路径（空则使用系统默认） | 空（系统默认） |
| FontFamily | 字体名称（不含扩展名） | `CascadiaMono` |
| FontSize | 字体大小（6-72 磅） | 10 |
| ScrollbackLimit | 最大滚动回看行数 | 131072 |
| ColorSchemeName | 颜色方案名称 | `Default` |
| StartupCommands | 新终端窗口创建时自动执行的命令列表 | 空 |
| bPreventCloseDuringActivity | 关闭编辑器时如有输出活动则提示确认 | `true` |
| ActivityTimeoutSeconds | 输出静默超时秒数（1.0-60.0） | 5.0 |

## C++ 用法

### 头文件引入

```cpp
#include "STerminal.h"
#include "ITerminalSession.h"
#include "TerminalBuffer.h"
#include "VTParser.h"
#include "TerminalColorScheme.h"
#include "TerminalKeyTranslator.h"
```

### 基本用法：在 Slate 布局中嵌入终端

```cpp
// 创建一个带滚动条的终端 Widget
TSharedPtr<SScrollBar> ScrollBar;
TSharedRef<STerminal> TerminalWidget = SNew(STerminal)
    .ExternalScrollbar(ScrollBar);

// 向终端发送命令
TerminalWidget->ExecuteCommand(TEXT("dir"));

// 检查终端会话是否正在运行
if (TerminalWidget->IsSessionRunning())
{
    UE_LOG(LogTemp, Log, TEXT("Terminal session is active"));
}

// 监听输出事件
TerminalWidget->OnOutputReceived.AddLambda([](int32 NumBytes)
{
    UE_LOG(LogTemp, Log, TEXT("Received %d bytes of output"), NumBytes);
});
```

### 进阶用法：自定义 PTY 会话

```cpp
// 通过工厂方法创建平台适配的 PTY 会话
FString Error;
TSharedPtr<ITerminalSession> Session = ITerminalSession::CreateForCurrentPlatform(Error);
if (!Session.IsValid())
{
    UE_LOG(LogTerminal, Error, TEXT("Failed to create session: %s"), *Error);
    return;
}

// 创建会话：指定 Shell 路径、工作目录、终端尺寸
Session->Create(TEXT(""), TEXT("C:/Projects"), 120, 40);

// 写入输入
TArray<uint8> Input = { 'h', 'e', 'l', 'l', 'o', '\r' };
Session->WriteInput(Input);

// 在游戏线程中消费输出
TArray<uint8> Output = Session->ConsumeOutput();
if (Output.Num() > 0)
{
    // 用 VTParser 解析输出
    FTerminalBuffer Buffer;
    Buffer.Initialize(120, 40, 131072);

    FVTParser Parser;
    Parser.SetBuffer(&Buffer);
    Parser.Parse(Output.GetData(), Output.Num());
}

// 监听进程退出
Session->OnProcessExited.BindLambda([](int32 ExitCode)
{
    UE_LOG(LogTerminal, Log, TEXT("Shell exited with code %d"), ExitCode);
});

// 调整大小
Session->Resize(160, 50);

// 关闭会话
Session->Shutdown();
```

### 进阶用法：自定义颜色方案

```cpp
// 从 JSON 字符串解析颜色方案
FString JSON = TEXT(R"({
    "Name": "Solarized Dark",
    "DefaultForeground": "#839496",
    "DefaultBackground": "#002b36",
    "CursorColor": "#839496",
    "SelectionColor": "#073642",
    "Palette": ["#073642", "#dc322f", "#859900", "#b58900",
                "#268bd2", "#d33682", "#2aa198", "#eee8d5",
                "#586e75", "#cb4b16", "#586e75", "#657b83",
                "#839496", "#6c71c4", "#93a1a1", "#fdf6e3"]
})");

FTerminalColorScheme Scheme;
if (FTerminalColorScheme::FromJSON(JSON, Scheme))
{
    UE_LOG(LogTerminal, Log, TEXT("Loaded scheme: %s"), *Scheme.Name);
}

// 使用默认方案
FTerminalColorScheme DefaultScheme = FTerminalColorScheme::MakeDefault();
```

### 进阶用法：键位转译

```cpp
// 将 Slate 键事件转换为 VT 字节序列
FKeyTranslationOptions Options;
Options.bApplicationCursorKeys = false; // DECCKM 关闭时，方向键使用 CSI 序列

TArray<uint8> Bytes = UE::Terminal::TranslateKeyToBytes(KeyEvent, Options);
if (Bytes.Num() > 0)
{
    // 发送到 PTY 会话
    Session->WriteInput(Bytes);
}
```

## Demo 示例

### 自定义终端面板 Widget

```cpp
// MyTerminalPanel.h
#pragma once

#include "Widgets/SCompoundWidget.h"

class SScrollBar;
class STerminal;

class SMyTerminalPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyTerminalPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    void OnTerminalOutput(int32 NumBytes);

    TSharedPtr<STerminal> TerminalWidget;
    TSharedPtr<SScrollBar> TerminalScrollBar;
};
```

```cpp
// MyTerminalPanel.cpp
#include "MyTerminalPanel.h"
#include "STerminal.h"
#include "Widgets/SScrollBar.h"

void SMyTerminalPanel::Construct(const FArguments& InArgs)
{
    TerminalScrollBar = SNew(SScrollBar)
        .Orientation(Orient_Vertical);

    ChildSlot
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot()
        .FillWidth(1.0f)
        [
            SAssignNew(TerminalWidget, STerminal)
            .ExternalScrollbar(TerminalScrollBar)
        ]
        + SHorizontalBox::Slot()
        .AutoWidth()
        [
            TerminalScrollBar.ToSharedRef()
        ]
    ];

    TerminalWidget->OnOutputReceived.AddSP(
        this, &SMyTerminalPanel::OnTerminalOutput);
}

void SMyTerminalPanel::OnTerminalOutput(int32 NumBytes)
{
    // 输出到达时可在此更新 UI 状态
    UE_LOG(LogTemp, Verbose, TEXT("Terminal output: %d bytes"), NumBytes);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Json` | 解析颜色方案 JSON 文件 |
| `JsonUtilities` | JSON 序列化/反序列化工具 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：平台 PTY 依赖是通过条件编译实现的（Windows 使用 ConPTY API，Linux/macOS 使用 POSIX PTY），不需要额外模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器函数类型转换警告 |
| 2026-05-12 | `91d5944f` | [Terminal] Surface session activity and prompt before closing the editor mid-output. | 编辑器关闭时检测终端输出活动并提示确认 |
| 2026-04-28 | `2832901f` | [Terminal] Drop `defaultconfig` from `UTerminalSettings`. | 移除设置类的 defaultconfig 修饰符 |
| 2026-04-20 | `c9454ad1` | [Terminal] Forward full key/modifier matrix to the *PTY* via a dedicated translator. | 引入专用键位转译器，完整转发按键和修饰键 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF 格式 |

### 维护评价

这是一个**非常新的实验性插件**，创建于 2026 年 4 月，距今仅约一个月，但在此期间保持了**活跃的开发节奏**（5 次 commit 涉及功能增强、编译器兼容性修复和代码质量改进）。

**优点**：
- 架构清晰：通过 `ITerminalSession` 接口抽象平台差异，VT 解析器遵循 vt100.net 规范
- 功能完备：支持 256 色、鼠标追踪、选区、滚动回看、颜色方案
- 跨平台：Windows（ConPTY）和 Linux/macOS（POSIX PTY）均有实现

**风险与限制**：
- **实验性**：标记为 `IsExperimentalVersion=true`，API 可能发生破坏性变更
- **未默认启用**：需要手动在插件管理器中启用
- **NoRedist**：不可再分发，表明是 Epic 内部/引擎专属功能
- **仅限编辑器**：无法在打包游戏中使用

**推荐**：如果你在使用 UE5.5+ 且希望在编辑器内拥有终端体验，值得尝试。但不建议在生产流程中深度依赖此插件，因为其实验性状态意味着 API 可能在未来版本中变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal)
- 官方文档（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal/Source/TerminalTests)