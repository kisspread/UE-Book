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

Terminal 插件在 Unreal Editor 内部实现了一个**原生 Slate 终端模拟器**，让你无需切换到外部终端窗口即可直接执行 shell 命令。

它解决的核心问题是：编辑器内的命令行操作。开发者经常需要在编辑器和外部终端之间来回切换（运行构建脚本、Git 操作、adb 命令等），这个插件将终端直接嵌入编辑器的 Tab 面板中。

底层架构由三层组成：
1. **ITerminalSession** — 平台抽象的 PTY 会话接口，Windows 使用 ConPTY，Linux/macOS 使用 POSIX PTY
2. **FTerminalBuffer + FVTParser** — 环形缓冲区 + 完整的 VT/ANSI 转义序列解析器（遵循 vt100.net Paul Williams 状态机模型）
3. **STerminal** — Slate 叶节点 Widget，逐单元格绘制字符网格，处理键盘/鼠标输入

支持的功能包括：颜色方案、鼠标跟踪、文本选择与复制粘贴、滚动回看、备用屏幕缓冲区、同步输出模式等。

## 使用场景

- 你在编辑器中频繁运行 Git 命令或构建脚本 → 用 Terminal 直接在编辑器 Tab 中操作
- 你需要快速执行 shell 命令而不想离开编辑器 → 用 Terminal
- 你在做一个编辑器扩展，需要嵌入终端面板 → 用 `STerminal` Widget
- 你需要在 Linux/macOS 上使用终端 → Terminal 支持 POSIX PTY 跨平台后端

## 蓝图用法

此插件为纯 C++/Slate 实现，**没有暴露蓝图 API**。所有交互通过编辑器菜单（Window → Terminal）或 C++ 代码进行。

## C++ 用法

### 头文件引入

```cpp
#include "STerminal.h"
#include "ITerminalSession.h"
#include "TerminalBuffer.h"
#include "VTParser.h"
#include "TerminalColorScheme.h"
#include "TerminalSettings.h"
#include "TerminalSubsystem.h"
#include "TerminalKeyTranslator.h"
```

### 基本用法 — 创建终端会话

通过 `ITerminalSession` 抽象接口创建跨平台终端会话：

```cpp
#include "ITerminalSession.h"

// 创建当前平台对应的 PTY 会话
FString Error;
TSharedPtr<ITerminalSession> Session = ITerminalSession:: CreateForCurrentPlatform(Error);
if (!Session.IsValid())
{
    UE_LOG(LogTerminal, Error, TEXT("无法创建终端会话: %s"), *Error);
    return;
}

// 创建会话，指定 shell 路径（空字符串使用系统默认）、工作目录和窗口大小
if (!Session->Create(TEXT(""), FPaths::ProjectDir(), 80, 24))
{
    UE_LOG(LogTerminal, Error, TEXT("终端会话创建失败"));
    return;
}

// 写入命令
FString Cmd = TEXT("echo Hello from UE5\r");
FTCHARToUTF8 Converter(*Cmd);
Session->WriteInput(
    TArrayView<const uint8>(
        reinterpret_cast<const uint8*>(Converter.Get()),
        Converter.Length()
    )
);

// 消费输出（在游戏线程调用）
TArray<uint8> Output = Session->ConsumeOutput();
```

### 基本用法 — 使用 STerminal Widget

```cpp
#include "STerminal.h"

// 在 Slate 面板中创建终端 Widget
TSharedRef<STerminal> TerminalWidget = SNew(STerminal);

// 发送命令执行
TerminalWidget->ExecuteCommand(TEXT("ls -la"));

// 检查会话是否运行中
if (TerminalWidget->IsSessionRunning())
{
    // 订阅输出通知
    TerminalWidget->OnOutputReceived.AddLambda([](int32 NumBytes)
    {
        UE_LOG(LogTerminal, Log, TEXT("终端输出了 %d 字节"), NumBytes);
    });
}
```

### 进阶用法 — 手动解析 VT 序列

```cpp
#include "VTParser.h"
#include "TerminalBuffer.h"

// 创建缓冲区和解析器
FTerminalBuffer Buffer;
Buffer.Initialize(80, 24, 131072);

FVTParser Parser;
Parser.SetBuffer(&Buffer);

// 解析一段包含 ANSI 转义序列的输出
const char* Data = "\033[1;32mBold Green\033[0m Normal";
Parser.Parse(
    reinterpret_cast<const uint8*>(Data),
    FCStringAnsi::Strlen(Data)
);

// 读取单元格内容
const FTerminalCell& Cell = Buffer.GetCell(0, 0);
// Cell.Character == 'B', Cell.Attributes 包含 Bold 标志
```

### 进阶用法 — 自定义颜色方案

```cpp
#include "TerminalColorScheme.h"

// 从 JSON 创建自定义颜色方案
FString JSON = TEXT(R"({
    "Name": "Solarized Dark",
    "DefaultForeground": "#839496",
    "DefaultBackground": "#002b36",
    "CursorColor": "#839496",
    "SelectionColor": "#073642",
    "Palette": ["#073642","#dc322f","#859900","#b58900","#268bd2","#d33682","#2aa198","#eee8d5","#002b36","#cb4b16","#586e75","#657b83","#839496","#6c71c4","#93a1a1","#fdf6e3"]
})");

FTerminalColorScheme Scheme;
if (FTerminalColorScheme::FromJSON(JSON, Scheme))
{
    // 通过子系统应用
    UTerminalSubsystem* Subsystem = GEditor->GetEditorSubsystem<UTerminalSubsystem>();
    // Subsystem->GetColorScheme() 可获取已加载的方案
}
```

### 进阶用法 — 键盘事件转译

```cpp
#include "TerminalKeyTranslator.h"

// 将 Slate 键盘事件转为终端字节序列
UE::Terminal::FKeyTranslationOptions Options;
Options.bApplicationCursorKeys = false;

TArray<uint8> Bytes = UE::Terminal::TranslateKeyToBytes(KeyEvent, Options);
if (Bytes.Num() > 0)
{
    Session->WriteInput(Bytes);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Freetype` | 字体渲染（等宽字体加载） |
| `HarfBuzz` | 文本整形（结合字符处理） |
| `ApplicationCore` | 系统字体路径解析 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告，兼容 MSVC 和 Clang 编译器 |
| 2026-05-12 | `91d5944f` | [Terminal] Surface session activity and prompt before closing the editor mid-output. | 编辑器关闭时检测终端活动并提示用户确认 |
| 2026-04-28 | `2832901f` | [Terminal] Drop `defaultconfig` from `UTerminalSettings`. | 移除设置类的 defaultconfig 标记，改为用户级配置 |
| 2026-04-20 | `c9454ad1` | [Terminal] Forward full key/modifier matrix to the *PTY* via a dedicated translator. | 重构键盘输入，使用专用转译器处理完整的按键/修饰键矩阵 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |

### 维护评价

Terminal 插件创建于 2026 年 4 月，是一个**非常新的实验性插件**（约 1 个月）。

**积极信号**：
- 创建以来保持活跃开发，不到一个月内有 5 次实质性提交
- 功能逐步完善：键盘输入重构、编辑器关闭保护、跨编译器兼容修复
- 架构设计成熟：平台抽象层（ConPTY/POSIX PTY）、完整的 VT 状态机解析器、环形缓冲区

**注意事项**：
- 标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- 目前处于早期阶段，API 可能会有变动
- Windows 使用 ConPTY，需要 Windows 10 1809+ 版本
- `NoRedist=true`，不可单独再分发

**推荐**：适合对编辑器内终端功能有需求的开发者试用和反馈。作为实验性功能，不建议在生产工作流中强依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal)