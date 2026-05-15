# StateTreeToolset

> Toolset for StateTree Inspection（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 状态树工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具集） |
| 模块 | `StateTreeToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-01 |
| 年龄标签 | 🆕（新） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/StateTreeToolset) | |

## 用途

此插件是 StateTree（状态树）系统的配套检查与调试工具集。StateTree 是 UE5 中用于创建复杂、分层状态机（尤其用于 AI 行为）的框架。该插件的目的是在编辑器中提供一套专用工具，方便开发者和设计师可视化地检查、调试正在运行中的 StateTree 实例的内部状态，从而简化 AI 逻辑的开发和问题排查流程。

## 使用场景

- 你正在使用 StateTree 为游戏中的 NPC 设计复杂的行为逻辑（如巡逻、追击、战斗决策），需要实时查看状态机当前激活的状态和转换条件。
- 你的 StateTree 行为运行不符合预期，需要定位是哪个节点、哪个转换或哪个任务出现了问题。
- 你作为团队中的技术美术或设计师，希望无需深入阅读 C++ 代码即可理解 NPC 的 AI 决策流程。

## 蓝图用法

该插件主要提供编辑器内的可视化工具集，并未直接暴露蓝图节点。其功能通过编辑器界面（如窗口、面板）进行交互，而非在蓝图图表中连接节点。

## C++ 用法

该插件的核心功能是向编辑器注册一套“工具集”，以供其他系统（如状态树编辑器）调用或展示。其本身不对外暴露用户可直接调用的 C++ API。

### 头文件引入

由于该插件是一个编辑器模块，主要在编辑器上下文（例如其他编辑器模块）中被依赖和使用。
```cpp
// 其他编辑器模块的 Build.cs 会依赖此插件模块
#include "StateTreeToolsetModule.h" // 注意：公开头文件为 `StateTreeToolset.h`，但实际模块类声明在其中
```

### 基本用法

此插件的典型使用方式是在您的游戏或编辑器插件模块的 `Build.cs` 中添加对 `StateTreeToolset` 模块的依赖，从而确保该工具集在编辑器环境中被正确加载和注册。

## Demo 示例

以下是一个最小化的编辑器模块示例，演示如何依赖并确保 `StateTreeToolset` 模块在上下文中可用。

**MyGameEditorModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyGameEditorModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};
```

**MyGameEditorModule.cpp**
```cpp
#include "MyGameEditorModule.h"
#include "StateTreeToolset.h" // 引入StateTreeToolset头文件，确保其符号在链接时可用

#define LOCTEXT_NAMESPACE "FMyGameEditorModule"

void FMyGameEditorModule::StartupModule()
{
    // 此处无需显式调用任何StateTreeToolset函数。
    // 只要本模块依赖了StateTreeToolset，其StartupModule就会在引擎启动阶段被调用，
    // 完成向编辑器注册工具集的工作。
    UE_LOG(LogTemp, Log, TEXT("MyGameEditorModule Started. StateTreeToolset should be loaded."));
}

void FMyGameEditorModule::ShutdownModule()
{
    UE_LOG(LogTemp, Log, TEXT("MyGameEditorModule Shutdown."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyGameEditorModule, MyGameEditor)
```

## 模块依赖

您的模块若要使用此插件的功能，需要在 `Build.cs` 中进行如下依赖配置。

| 模块 | 用途 |
|---|---|
| `StateTreeToolset` | 依赖本插件模块，以确保其编辑器工具集被加载。 |
| `StateTree` | （插件依赖）核心状态树运行时和编辑器框架。 |
| `ToolsetRegistry` | （插件依赖）用于统一注册和管理编辑器工具集的框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-03 | `7f02bd73` | [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r | 为简化工具集注册流程，将所有工具集模块的加载阶段统一调整至引擎初始化后。 |
| 2026-04-01 | `4dcdfdfe` | [AI Toolsets]: Move StateTreeToolset under the Toolsets directory | 首次提交，将 StateTreeToolset 移至通用的 Toolsets 目录下，作为 AI 工具集项目的一部分。 |

### 维护评价

该插件非常新，创建于 2026 年 4 月。从有限的 git 历史来看，它处于活跃的初始开发和整合阶段，最近的更新集中在架构调整（加载时序优化）。由于其标记为 **实验性 (`IsExperimentalVersion=true`)** 且 **默认未启用 (`EnabledByDefault=false`)**，表明 Epic Games 正在试验此工具，API 和功能可能尚未稳定，未来可能发生变更。目前可以作为早期技术预览或内部工具使用，但不建议在正式生产项目中深度依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/StateTreeToolset)
- 官方文档：暂无
- 测试用例：在给定的源码片段中未发现专门的测试文件。