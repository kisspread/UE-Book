# Terminal

> Native Slate terminal emulator.

| 属性 | 值 |
|---|---|
| 中文名 | 终端模拟器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Terminal` (Editor), `TerminalTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal) | |

## 用途

Terminal 插件在 Unreal Editor 内嵌入了一个**原生 Slate 终端模拟器**，让开发者无需切换窗口即可在编辑器中直接使用系统 Shell（如 cmd、PowerShell、bash 等）。

核心架构由三层组成：
1. **PTY 会话层**（`ITerminalSession`）— 平台无关的伪终端抽象接口，Windows 通过 ConPTY 实现（`FConPTYSession`），Linux/macOS 通过 POSIX PTY 实现（`FPosixPTYSession`）
2. **终端解析层**（`FVTParser` + `FTerminalBuffer`）— 完整的 VT/ANSI 转义序列状态机解析器，配合环形缓冲区管理字符网格和滚动回溯
3. **渲染层**（`STerminal`）— 直接通过 `OnPaint` 绘制字符单元格的 Slate 叶节点控件，支持文本选择、光标闪烁、鼠标追踪

与"打开外部终端"不同，该插件完全在编辑器进程内运行，支持颜色方案定制、键位映射、滚动回溯等完整的终端功能。

## 使用场景

- 你在 UE 编辑器中频繁需要执行构建脚本、Git 命令或调试工具 → 用 Terminal 在编辑器内直接操作
- 你开发了自定义的 CLI 工具链，希望在编辑器内无缝使用 → 用 Terminal 集成工作流
- 你需要一个带有颜色高亮、文本选择、滚动回溯的终端，而不是一个简单的日志输出窗口 → 用 Terminal

## 蓝图用法

本插件是纯 C++/Slate 实现，没有暴露任何 `BlueprintCallable` 函数。`STerminal` 是 `SLeafWidget` 而非 `UWidget`，因此无法在 UMG 蓝图中直接使用。

但可以通过 **编辑器设置面板** 配置终端行为：

| 设置项 | 说明 | 位置 |
|---|---|---|
| `ShellExecutablePath` | Shell 可执行文件路径，留空使用系统默认 | Editor Preferences → Terminal |
| `FontFamily` | 字体名称（不含扩展名），默认 `CascadiaMono` | Editor Preferences → Terminal |
| `FontSize` | 字体大小（6-72pt），默认 10 | Editor Preferences → Terminal |
| `ScrollbackLimit` | 最大滚动回溯行数（0-1000000），默认 131072 | Editor Preferences → Terminal |
| `ColorSchemeName` | 颜色方案名称，默认 `Default` | Editor Preferences → Terminal |
| `StartupCommands` | 新终端启动时自动执行的命令列表 | Editor Preferences → Terminal |
| `bPreventCloseDuringActivity` | 终端有输出时关闭编辑器是否提示确认 | Editor Preferences → Terminal → Activity |
| `ActivityTimeoutSeconds` | 静默超时（1.0-60.0秒），超时后视为非活跃 | Editor Preferences → Terminal → Activity |

## C++ 用法

### 头文件引入

```cpp
#include "STerminal.h"
#include "TerminalBuffer.h"
#include "VTParser.h"
#include "ITerminalSession.h"
#include "TerminalKeyTranslator.h"
#include "TerminalColorScheme.h"
```

### 基本用法 — 创建终端会话

终端的创建通过平台工厂自动选择后端：

```cpp
// 来源: Public/ITerminalSession.h — CreateForCurrentPlatform
FString Error;
TSharedPtr<ITerminalSession> Session = ITerminalSession::CreateForCurrentPlatform(Error);
if (!Session)
{
    UE_LOG(LogTerminal, Error, TEXT("无法创建终端会话: %s"), *Error);
    return;
}

// 创建会话：Shell路径（空=系统默认）、工作目录、列数、行数
if (Session->Create(TEXT(""), TEXT(""), 80, 24))
{
    // 会话创建成功，可以通过 WriteInput 发送输入
    TArray<uint8> Input = { 'l', 's', '\r' }; // 发送 "ls\r"
    Session->WriteInput(Input);
}

// 监听进程退出
Session->OnProcessExited.BindLambda([](int32 ExitCode)
{
    UE_LOG(LogTerminal, Log, TEXT("Shell 进程退出，退出码: %d"), ExitCode);
});

// 读取输出
TArray<uint8> Output = Session->ConsumeOutput();
```

### 基本用法 — 使用终端缓冲区和解析器

```cpp
// 来源: Public/TerminalBuffer.h, Public/VTParser.h

// 创建缓冲区
FTerminalBuffer Buffer;
Buffer.Initialize(80, 24, 131072); // 列数、视口行数、滚动回溯限制

// 创建解析器并绑定缓冲区
FVTParser Parser;
Parser.SetBuffer(&Buffer);

// 解析 VT 序列数据
const uint8* Data = /* ... */;
int32 Length = /* ... */;
Parser.Parse(Data, Length);

// 读取单元格
const FTerminalCell& Cell = Buffer.GetCell(0, 0);
UE_LOG(LogTerminal, Log, TEXT("字符: %c, 前景: (%d,%d,%d)"),
    Cell.Character, Cell.Foreground.R, Cell.Foreground.G, Cell.Foreground.B);
```

### 进阶用法 — 自定义颜色方案

```cpp
// 来源: Public/TerminalColorScheme.h

// 创建默认方案
FTerminalColorScheme DefaultScheme = FTerminalColorScheme::MakeDefault();

// 从 JSON 解析自定义方案
FString JsonText = TEXT(R"({
    "name": "Solarized Dark",
    "default_foreground": "#839496",
    "default_background": "#002b36",
    "cursor_color": "#839496",
    "selection_color": "#073642",
    "palette": [
        "#073642", "#dc322f", "#859900", "#b58900",
        "#268bd2", "#d33682", "#2aa198", "#eee8d5",
        "#002b36", "#cb4b16", "#586e75", "#657b83",
        "#839496", "#6c71c4", "#93a1a1", "#fdf6e3"
    ]
})");

FTerminalColorScheme CustomScheme;
if (FTerminalColorScheme::FromJSON(JsonText, CustomScheme))
{
    // 应用到终端缓冲区的默认单元格
    Buffer.DefaultCell.Foreground = CustomScheme.DefaultForeground.ToFColor(true);
    Buffer.DefaultCell.Background = CustomScheme.DefaultBackground.ToFColor(true);
}
```

### 进阶用法 — 键位翻译

```cpp
// 来源: Public/TerminalKeyTranslator.h

// 将 Slate 按键事件翻译为 VT 字节序列
UE::Terminal::FKeyTranslationOptions Options;
Options.bApplicationCursorKeys = Parser.bApplicationCursorKeys; // DECCKM 模式

TArray<uint8> Bytes = UE::Terminal::TranslateKeyToBytes(KeyEvent, Options);
if (!Bytes.IsEmpty())
{
    Session->WriteInput(Bytes);
}
```

### 进阶用法 — 检测 ConPTY 可用性

```cpp
// 来源: Public/ConPTYSession.h
#if PLATFORM_WINDOWS
if (!FConPTYSession::IsConPTYAvailable())
{
    UE_LOG(LogTerminal, Warning, TEXT("当前系统不支持 ConPTY，终端功能不可用"));
}
#endif
```

## Demo 示例

以下示例演示如何在自定义编辑器面板中嵌入一个终端控件：

**MyTerminalPanel.h**
```cpp
#pragma once

#include "CoreMinimal.h"
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
    TSharedPtr<STerminal> TerminalWidget;
    TSharedPtr<SScrollBar> ScrollBar;
};
```

**MyTerminalPanel.cpp**
```cpp
#include "MyTerminalPanel.h"
#include "STerminal.h"
#include "TerminalSettings.h"

void SMyTerminalPanel::Construct(const FArguments& InArgs)
{
    // 创建外部滚动条
    ScrollBar = SNew(SScrollBar)
        .Orientation(Orient_Vertical)
        .AlwaysShowScrollbar(false);

    ChildSlot
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot()
        .FillWidth(1.0f)
        [
            // 终端控件，传入外部滚动条
            SAssignNew(TerminalWidget, STerminal)
            .ExternalScrollbar(ScrollBar)
        ]
        + SHorizontalBox::Slot()
        .AutoWidth()
        [
            ScrollBar.ToSharedRef()
        ]
    ];
}
```

**嵌入到编辑器 Tab**（通常在 Module 的 StartupModule 中）：

```cpp
#include "MyTerminalPanel.h"
#include "WorkspaceMenuStructure.h"
#include "WorkspaceMenuStructureModule.h"

void FMyModule::StartupModule()
{
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner("MyTerminalTab",
        FOnSpawnTab::CreateLambda([](const FSpawnTabArgs& Args) -> TSharedRef<SDockTab>
        {
            return SNew(SDockTab)
                .TabRole(ETabRole::NomadTab)
                .Label(FText::FromString(TEXT("Terminal")))
                [
                    SNew(SMyTerminalPanel)
                ];
        }))
        .SetDisplayName(FText::FromString(TEXT("Terminal")))
        .SetGroup(WorkspaceMenu::GetStructure().GetToolsCategory());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | — |

> **说明**：Terminal 的核心依赖为 Slate（SLeafWidget、FSlateDrawElement、SScrollBar 等）、InputCore（FKeyEvent）以及平台 PTY 系统调用。这些均为引擎标准模块，无需额外引入。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告，兼容 MSVC 和 Clang 编译器 |
| 2026-05-12 | `91d5944f` | [Terminal] Surface session activity and prompt before closing the editor mid-output. | 新增关闭编辑器时检测终端活动并提示用户确认 |
| 2026-04-28 | `2832901f` | [Terminal] Drop `defaultconfig` from `UTerminalSettings`. | 移除 UTerminalSettings 的 defaultconfig 标记 |
| 2026-04-20 | `c9454ad1` | [Terminal] Forward full key/modifier matrix to the *PTY* via a dedicated translator. | 新增专用键位翻译器，将完整按键/修饰键矩阵转发到 PTY |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF 格式 |

### 维护评价

Terminal 是一个**全新插件**（约 1 个月历史），处于**实验阶段**（`IsExperimentalVersion=true`，`EnabledByDefault=false`）。

**积极面**：
- 代码架构清晰，分层合理（PTY 会话层 → 解析层 → 渲染层）
- 跨平台支持（ConPTY + POSIX PTY）
- 功能完整：VT/ANSI 解析、颜色方案、文本选择、鼠标追踪、滚动回溯
- 短期内更新活跃，功能迭代快速

**注意点**：
- 实验性插件，API 可能发生破坏性变更
- `EnabledByDefault=false`，需要在 Plugins 面板手动启用
- `NoRedist=true`，不能在非 Epic 发行版中分发
- 平台支持仅限 Windows（ConPTY）和 Linux/macOS（POSIX PTY）

**推荐使用**：适合对终端功能有需求的开发者试用，但不建议在生产项目中作为关键依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal/Source/TerminalTests)