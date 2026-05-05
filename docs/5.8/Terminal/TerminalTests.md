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
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal) | |

## 用途

Terminal 插件为 Unreal Editor 提供了一个**原生 Slate 终端模拟器**。它在编辑器内部嵌入一个功能完整的命令行终端界面，使用 Slate UI 框架原生渲染，而非依赖外部终端窗口或简单的文本日志输出。

该插件解决的核心问题是：开发者在使用 UE5 编辑器时，经常需要切换到外部终端执行命令行操作（如运行脚本、查看日志、执行构建命令等）。Terminal 插件将这一工作流集成到编辑器内部，减少窗口切换，提升开发效率。

**注意**：该插件标记为实验性（`IsExperimentalVersion=true`）且默认未启用（`EnabledByDefault=false`），属于早期开发阶段的功能。

## 使用场景

- 你需要在编辑器内直接执行命令行操作，不想频繁切换到外部终端
- 你在开发自定义工具链，需要在编辑器内嵌入终端来运行脚本或命令
- 你需要一个集成在编辑器面板中的终端，用于实时查看构建输出、日志流等
- 你正在构建自定义的编辑器扩展，需要一个可嵌入的终端组件

## 蓝图用法

该插件为 Editor 模块，主要面向 C++ 和 Slate 编辑器扩展开发，不提供蓝图可调用的运行时 API。

如需在编辑器蓝图工具中使用终端功能，需通过 C++ 暴露接口后桥接到蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "TerminalModule.h"
```

### 基本用法

Terminal 插件提供 Slate 终端控件，可在自定义编辑器面板中嵌入使用。由于该插件为实验性功能且源码尚未完全稳定，以下为基于插件架构的预期用法：

```cpp
// 在自定义编辑器 Tab 中创建终端控件
// 注：具体 API 以实际源码为准，以下为架构示意
TSharedRef<SDockTab> OnSpawnTerminalTab(const FSpawnTabArgs& Args)
{
    return SNew(SDockTab)
        .TabRole(ETabRole::NomadTab)
        [
            SNew(STerminalWidget)  // 终端 Slate 控件
        ];
}
```

### 进阶用法

Terminal 模块作为 Editor 插件，可与其他编辑器扩展模块配合，将终端集成到自定义工作区布局中。

## Demo 示例

```cpp
// MyTerminalPanel.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/Docking/SDockTab.h"

class FMyTerminalPanel
{
public:
    static void RegisterTabSpawner();
    static void UnregisterTabSpawner();

private:
    static TSharedRef<SDockTab> OnSpawnTab(const FSpawnTabArgs& Args);
    static const FName TabId;
};
```

```cpp
// MyTerminalPanel.cpp
#include "MyTerminalPanel.h"

const FName FMyTerminalPanel::TabId("MyTerminalPanel");

void FMyTerminalPanel::RegisterTabSpawner()
{
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner(
        TabId,
        FOnSpawnTab::CreateStatic(&FMyTerminalPanel::OnSpawnTab))
        .SetDisplayName(FText::FromString(TEXT("Terminal")))
        .SetMenuType(ETabSpawnerMenuType::Hidden);
}

void FMyTerminalPanel::UnregisterTabSpawner()
{
    FGlobalTabmanager::Get()->UnregisterNomadTabSpawner(TabId);
}

TSharedRef<SDockTab> FMyTerminalPanel::OnSpawnTab(const FSpawnTabArgs& Args)
{
    return SNew(SDockTab)
        .TabRole(ETabRole::NomadTab)
        [
            // 嵌入终端控件
            SNew(STextBlock)
                .Text(FText::FromString(TEXT("Terminal placeholder")))
        ];
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

- 2026-04-20 `c9454ad1` [Terminal] Forward full key/modifier matrix to the *PTY* via a dedicated translator.
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-09 `98f0c628` [Terminal] Add `StartupCommands` setting to execute commands on new terminal window creation.
- 2026-04-08 `ca248609` [Terminal] Move `Terminal` plugin to `Engine/Plugins/Experimental`.

### 维护评价

- **状态**：实验性（Experimental），默认未启用
- **成熟度**：早期开发阶段，API 可能发生重大变更
- **风险提示**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明该功能尚未稳定，不建议在生产环境中使用
- **建议**：可作为参考和实验用途，但应做好 API 变更的准备。如需终端功能，建议关注后续版本更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal)
- 官方文档：暂无
- 测试用例：`Source/TerminalTests/`（TerminalTests 模块）