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

Terminal 插件为 Unreal Editor 提供了一个**原生的 Slate 终端模拟器**。它将一个功能完整的命令行终端直接嵌入编辑器 UI 内，通过 PTY（伪终端）与系统 Shell 交互。

解决的核心问题：开发者在使用 UE5 时，经常需要在编辑器和外部终端窗口之间来回切换——执行 Git 命令、运行构建脚本、查看日志输出等。Terminal 插件将这些操作统一到编辑器内部，减少上下文切换开销。

基于源码中的关键线索，插件的核心架构包括：

- **PTY（伪终端）驱动**：通过操作系统伪终端与 Shell 进程通信，而非简单的管道重定向，确保完整的终端行为（如颜色、光标移动、信号传递）
- **ANSI 转义序列渲染**：将终端输出中的 ANSI 控制码翻译为 Slate UI 可渲染的富文本样式（颜色、粗体等）
- **键盘输入翻译层**：将 Slate 的 `FKeyEvent` 转换为 PTY 可识别的字符序列，支持修饰键组合（Ctrl+C、Alt 序列等）
- **会话生命周期管理**：追踪终端输出活动，在编辑器关闭前提醒用户仍有进行中的输出
- **可配置的终端设置**：提供 `UTerminalSettings` 进行自定义配置

## 使用场景

- 你频繁在 UE5 编辑器和外部终端之间切换执行 Git、构建脚本 → 用 Terminal 在编辑器内直接操作
- 你需要在编辑器内快速查看实时编译输出或日志流 → 用 Terminal 的内嵌终端窗口
- 你在开发自定义工具链，需要将命令行交互集成到编辑器工作流中 → 用 Terminal 提供的 Slate 终端组件

## 蓝图用法

该插件主要是编辑器 UI 工具，API 以 C++ / Slate 为主。`UTerminalSettings` 提供了可通过编辑器设置面板访问的配置选项。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 终端设置 | 配置终端行为（字体、Shell 路径等） | `UTerminalSettings` |

> ⚠️ 该插件的大部分核心功能（PTY 管理、ANSI 渲染、键入翻译）位于内部实现层，主要通过 Slate UI 暴露而非蓝图函数。建议通过 C++ 用法进行深度集成。

## C++ 用法

### 头文件引入

```cpp
#include "Terminal.h"
```

### 基本用法

该插件的核心功能通过 Slate Widget 体系实现。终端会话通过 PTY 与系统 Shell 通信，键入事件通过专用翻译层转发。

**键盘输入转发**（源自 commit `c9454ad1`）：

```cpp
// 将 Slate 键事件转换为 PTY 可识别的终端序列
// 内部通过专用翻译器处理完整的键/修饰键矩阵
// 支持：Ctrl+C、Ctrl+Z、Alt+字符、方向键、功能键等
```

**会话活动监控**（源自 commit `91d5944f`）：

```cpp
// 在编辑器关闭前检查终端会话是否仍有活动输出
// 如有未完成的输出，弹出确认对话框提醒用户
// 防止意外中断长时间运行的命令
```

### 进阶用法

**设置自定义**（源自 commit `2832901f`）：

```cpp
// UTerminalSettings 不再使用 defaultconfig 修饰符
// 意味着配置按项目存储，不会跨项目共享
// 可通过 UTerminalSettings 自定义 Shell 路径、字体、配色等
```

## Demo 示例

```cpp
// TerminalDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/Docking/SDockTab.h"

class FTerminalDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    void OnSpawnTerminalTab(const FSpawnTabArgs& Args);

    static const FName TerminalTabId;

private:
    TSharedPtr<SDockTab> TerminalTab;
};
```

```cpp
// TerminalDemo.cpp
#include "TerminalDemo.h"
// #include "TerminalModule.h"  // 实际 Terminal 插件模块头文件

const FName FTerminalDemoModule::TerminalTabId("TerminalDemoTab");

void FTerminalDemoModule::StartupModule()
{
    // Terminal 插件通过编辑器 Tab 启动
    // 通常在编辑器菜单中注册"终端"选项卡
    // 用户点击后打开 Slate 终端 Widget，
    // 内部自动启动 PTY Shell 进程并开始 I/O 循环

    FGlobalTabmanager::Get()->RegisterNomadTabSpawner(
        TerminalTabId,
        FOnSpawnTab::CreateRaw(this, &FTerminalDemoModule::OnSpawnTerminalTab))
        .SetDisplayName(FText::FromString(TEXT("Terminal")))
        .SetMenuType(ETabSpawnerMenuType::Hidden);
}

void FTerminalDemoModule::ShutdownModule()
{
    FGlobalTabmanager::Get()->UnregisterNomadTabSpawner(TerminalTabId);
}

void FTerminalDemoModule::OnSpawnTerminalTab(const FSpawnTabArgs& Args)
{
    // 实际终端 Widget 由 Terminal 插件提供
    // 这里展示的是如何将终端集成到编辑器 Tab 框架中
    TerminalTab = SNew(SDockTab)
        .TabRole(ETabRole::NomadTab)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Terminal plugin widget would go here")))
        ];
}

IMPLEMENT_MODULE(FTerminalDemoModule, TerminalDemo)
```

## 模块依赖

从 Terminal 编辑器插件的特性推断（PTY 管理、Slate 渲染、编辑器集成）：

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | Terminal 作为编辑器插件，依赖 Editor 核心框架和 Slate |

> 注：TerminalTests 模块仅用于插件自身的自动化测试，使用者无需依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器（MSVC/Clang）的类型转换警告 |
| 2026-05-12 | `91d5944f` | [Terminal] Surface session activity and prompt before closing the editor mid-output. | 添加会话活动检测，关闭编辑器前提示未完成的终端输出 |
| 2026-04-28 | `2832901f` | [Terminal] Drop `defaultconfig` from `UTerminalSettings`. | 设置类移除 defaultconfig，改为项目级配置 |
| 2026-04-20 | `c9454ad1` | [Terminal] Forward full key/modifier matrix to the *PTY* via a dedicated translator. | 实现完整的键盘输入翻译层，支持所有修饰键组合 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |

### 维护评价

- **创建时间**：2026-04-08，约 1 个月前，非常新的插件
- **更新频率**：自创建以来已有 5 次提交，约每周 1-2 次，属于**密集开发期**
- **功能迭代**：从基础终端实现 → 键盘输入完善 → 设置系统优化 → 会话管理 → 编译器兼容性，开发路径清晰
- **实验性状态**：标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **编辑器专用**：`EditorOnly=true`，不会被打包到运行时

**综合评价**：Terminal 是一个处于**早期密集开发阶段**的实验性插件，功能正在快速完善。当前已具备核心终端能力（PTY、ANSI 渲染、键盘输入、会话管理）。适合愿意尝试新功能的开发者使用，但短期内可能仍有 API 变更。建议关注后续版本的稳定性改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal/Source/TerminalTests)