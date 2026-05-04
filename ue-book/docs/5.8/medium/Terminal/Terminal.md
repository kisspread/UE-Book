# Terminal

> Native Slate terminal emulator.

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Terminal` (Editor), `TerminalTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Terminal) | |

## 用途

Terminal 插件在 Unreal Editor 内部提供了一个**原生 Slate 终端模拟器**，让你无需切换窗口即可直接在编辑器中使用系统 Shell（cmd、PowerShell、bash、zsh 等）。

它解决的核心问题是：开发者在使用 UE5 时经常需要在编辑器和外部终端之间来回切换——执行构建脚本、运行命令行工具、查看日志输出、操作版本控制等。Terminal 插件将完整的 VT100/ANSI 终端模拟器嵌入编辑器的 Tab 面板中，支持跨平台（Windows ConPTY / Linux/macOS POSIX PTY），具备完整的 VT 转义序列解析、鼠标追踪、颜色方案、滚动回溯等功能。

## 使用场景

- 你需要在编辑器内快速执行命令行操作（构建、打包、Git 操作等），不想切换到外部终端
- 你在开发编辑器扩展，需要嵌入一个功能完整的终端控件
- 你需要一个支持 ANSI 颜色和 VT100 转义序列的终端来查看彩色日志输出
- 你希望自定义终端的字体、颜色方案和启动命令

## 蓝图用法

Terminal 是一个纯 C++/Slate 编辑器插件，**不暴露蓝图 API**。所有交互通过 Slate UI 和 C++ 接口完成。

### 编辑器设置

终端行为通过 **项目设置 → Terminal** 面板配置（`UTerminalSettings`）：

| 设置项 | 说明 | 默认值 |
|---|---|---|
| ShellExecutablePath | Shell 可执行文件路径，留空使用系统默认 | 空（Windows: COMSPEC, Unix: SHELL） |
| FontFamily | 等宽字体名称（不含扩展名） | `CascadiaMono` |
| FontSize | 字体大小（磅） | 10 |
| ScrollbackLimit | 最大滚动回溯行数 | 131072 |
| ColorSchemeName | 颜色方案名称（对应 Config/ColorSchemes/ 下的 JSON 文件） | `Default` |
| StartupCommands | 新终端窗口创建时自动执行的命令列表 | 空 |

## C++ 用法

### 头文件引入

```cpp
#include "ITerminalSession.h"
#include "STerminal.h"
#include "TerminalBuffer.h"
#include "VTParser.h"
#include "TerminalColorScheme.h"
#include "TerminalKeyTranslator.h"
#include "TerminalSubsystem.h"
```

### 基本用法：创建终端会话

通过 `ITerminalSession` 的工厂方法创建跨平台 PTY 会话：

```cpp
// 来源: Public/ITerminalSession.h
FString Error;
TSharedPtr<ITerminalSession> Session = ITerminalSession::CreateForCurrentPlatform(Error);
if (!Session.IsValid())
{
    UE_LOG(LogTerminal, Error, TEXT("无法创建终端会话: %s"), *Error);
    return;
}

// 创建会话：指定 Shell 路径、工作目录、初始列数和行数
// ShellPath 为空时使用系统默认 Shell
if (!Session->Create(TEXT(""), FPaths::ProjectDir(), 120, 40))
{
    UE_LOG(LogTerminal, Error, TEXT("终端会话创建失败"));
    return;
}

// 写入输入（UTF-8 字节）
FString Command = TEXT("echo Hello from UE5\n");
FTCHARToUTF8 Converter(*Command);
Session->WriteInput(TArrayView<const uint8>((const uint8*)Converter.Get(), Converter.Length()));

// 消费输出（在游戏线程调用，线程安全）
TArray<uint8> Output = Session->ConsumeOutput();
if (Output.Num() > 0)
{
    FString OutputStr = FString(UTF8_TO_TCHAR(Output.GetData()));
    UE_LOG(LogTerminal, Log, TEXT("终端输出: %s"), *OutputStr);
}

// 检查进程是否仍在运行
if (!Session->IsRunning())
{
    UE_LOG(LogTerminal, Log, TEXT("Shell 进程已退出"));
}

// 调整终端大小
Session->Resize(160, 50);

// 关闭会话
Session->Shutdown();
```

### 基本用法：VT 解析器

```cpp
// 来源: Public/VTParser.h
FTerminalBuffer Buffer;
Buffer.Initialize(120, 40, 10000);

FVTParser Parser;
Parser.SetBuffer(&Buffer);

// 解析包含 VT 转义序列的 UTF-8 数据
TArray<uint8> VTData = /* ... 从 PTY 读取的数据 ... */;
Parser.Parse(VTData.GetData(), VTData.Num());

// 检查解析器是否设置了窗口标题
if (!Parser.WindowTitle.IsEmpty())
{
    UE_LOG(LogTerminal, Log, TEXT("终端标题: %s"), *Parser.WindowTitle);
}

// 检查是否有需要回传给 PTY 的响应（如 DA、DSR 回复）
if (Parser.ResponseBuffer.Num() > 0)
{
    Session->WriteInput(Parser.ResponseBuffer);
    Parser.ResponseBuffer.Reset();
}
```

### 基本用法：终端缓冲区

```cpp
// 来源: Public/TerminalBuffer.h
FTerminalBuffer Buffer;
Buffer.Initialize(120, 40, 10000); // 120列, 40行视口, 10000行滚动回溯

// 读取单元格
const FTerminalCell& Cell = Buffer.GetCell(0, 0);
UE_LOG(LogTerminal, Log, TEXT("字符: %c, 前景色: %s"), Cell.Character, *Cell.Foreground.ToString());

// 检查单元格属性
if (Cell.Attributes & ETerminalAttribute::Bold)
{
    // 粗体文本
}

// 获取选区文本
FString SelectedText = Buffer.GetTextInRange(5, 0, 10, 80);

// 调整大小
Buffer.Resize(160, 50);

// 清除滚动回溯
Buffer.ClearScrollback();
```

### 进阶用法：颜色方案

```cpp
// 来源: Public/TerminalColorScheme.h, Public/TerminalSubsystem.h
UTerminalSubsystem* Subsystem = GEditor->GetEditorSubsystem<UTerminalSubsystem>();

// 获取当前活动颜色方案
FTerminalColorScheme Scheme = Subsystem->GetActiveColorScheme();
UE_LOG(LogTerminal, Log, TEXT("当前方案: %s"), *Scheme.Name);
UE_LOG(LogTerminal, Log, TEXT("默认前景色: %s"), *Scheme.DefaultForeground.ToString());

// 从 JSON 加载自定义方案
FString JSON = TEXT(R"({
    "name": "Solarized Dark",
    "foreground": "#839496",
    "background": "#002b36",
    "cursor": "#839496",
    "selection": "#073642",
    "palette": ["#073642", "#dc322f", "#859900", "#b58900", "#268bd2", "#d33682", "#2aa198", "#eee8d5", "#002b36", "#cb4b16", "#586e75", "#657b83", "#839496", "#6c71c4", "#93a1a1", "#fdf6e3"]
})");

FTerminalColorScheme CustomScheme;
if (FTerminalColorScheme::FromJSON(JSON, CustomScheme))
{
    UE_LOG(LogTerminal, Log, TEXT("自定义方案加载成功: %s"), *CustomScheme.Name);
}

// 重新加载磁盘上的颜色方案
Subsystem->ReloadColorSchemes();
```

### 进阶用法：键位翻译

```cpp
// 来源: Public/TerminalKeyTranslator.h
#include "TerminalKeyTranslator.h"

// 将 Slate 键事件翻译为 VT 终端字节序列
UE::Terminal::FKeyTranslationOptions Options;
Options.bApplicationCursorKeys = true; // DECCKM 模式

TArray<uint8> Bytes = UE::Terminal::TranslateKeyToBytes(KeyEvent, Options);
if (Bytes.Num() > 0)
{
    Session->WriteInput(Bytes);
}
```

## Demo 示例

### 在编辑器 DockTab 中嵌入终端

```cpp
// MyTerminalPanel.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SMyTerminalPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyTerminalPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
};
```

```cpp
// MyTerminalPanel.cpp
#include "MyTerminalPanel.h"
#include "STerminal.h"
#include "Widgets/Input/SSearchBox.h"
#include "Widgets/Layout/SScrollBar.h"

void SMyTerminalPanel::Construct(const FArguments& InArgs)
{
    auto ScrollBar = SNew(SScrollBar)
        .Orientation(Orient_Vertical);

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            SNew(SHorizontalBox)
            + SHorizontalBox::Slot()
            .FillWidth(1.0f)
            [
                SNew(STerminal)
                .ExternalScrollbar(ScrollBar)
            ]
            + SHorizontalBox::Slot()
            .AutoWidth()
            [
                ScrollBar
            ]
        ]
    ];
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Terminal` | 终端模拟器核心模块（VT 解析、PTY 会话、Slate 控件） |
| `TerminalTests` | 自动化测试模块 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- 2026-04-08 初始提交 — Terminal 插件首次引入
```

### 维护评价

- **创建时间**：2026-04-08，非常新的插件
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，明确标记为实验性
- **NoRedist**：`NoRedist=true`，不可重新分发
- **维护状态**：刚创建，尚无后续更新记录
- **代码质量**：架构清晰，跨平台设计合理（Windows ConPTY + POSIX PTY），VT 解析器遵循 Paul Williams 规范，有独立测试模块
- **已知限制**：
  - 仅限编辑器使用（`EditorOnly=true`）
  - 实验性功能，API 可能发生变化
  - 不支持 Kitty 键盘协议和 DECKPAM（文档中明确标注为 Non-goals）
- **推荐程度**：作为实验性新插件，适合尝鲜使用，不建议在生产环境中依赖。关注后续版本的稳定性改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Terminal)
- [官方文档]()（暂无）