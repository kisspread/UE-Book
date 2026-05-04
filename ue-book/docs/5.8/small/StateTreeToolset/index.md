# StateTreeToolset

> Toolset for StateTree Inspection

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StateTreeToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/StateTreeToolset) | |

## 用途

该插件为 Unreal Engine 的 **StateTree** 系统提供了一套编辑器内的检查（Inspection）工具。它并非一个运行时功能插件，而是一个编辑器扩展，旨在帮助开发者在编辑器中更方便地调试、查看和分析 StateTree 的状态与数据。其核心价值在于将 StateTree 的调试信息集成到引擎的“工具集（Toolset）”框架中，可能以自定义面板、窗口或上下文菜单的形式呈现，从而提升 AI 行为设计的效率。

## 使用场景

- 你正在使用 StateTree 为游戏中的 AI 或复杂游戏逻辑设计行为树。
- 你需要在编辑器运行时（PIE）或调试构建中，实时查看某个 Actor 的 StateTree 当前激活的状态、转换条件、以及黑板（Blackboard）中的变量值。
- 你希望有一个统一的、集成在引擎工具集中的界面来检查所有 StateTree 实例，而不是依赖分散的日志输出或断点。

## 蓝图用法

无公开蓝图 API。此插件为纯编辑器工具集扩展，其功能通过编辑器 UI（如菜单、面板）触发，不暴露蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "StateTreeToolset.h"
```

### 基本用法

该插件主要通过模块接口加载。其核心功能由 `StateTree` 和 `ToolsetRegistry` 插件提供，本插件作为集成层。通常，你不需要直接调用其 C++ API。你可以通过检查模块是否加载来确认工具是否可用。

```cpp
// 检查 StateTreeToolset 模块是否已加载并可用
if (FModuleManager::Get().IsModuleLoaded(TEXT("StateTreeToolset")))
{
    UE_LOG(LogTemp, Log, TEXT("StateTree 检查工具集已加载。"));
}
```
*来源：基于 `StateTreeToolset.h` 中的模块接口推断。*

### 进阶用法

由于该插件本身不提供复杂的 C++ API，其“进阶用法”体现在理解其架构上。它依赖 `ToolsetRegistry` 插件来注册自己的工具。如果你正在开发自己的 StateTree 相关工具，可以参考此插件的模式，通过 `ToolsetRegistry` 注册自定义的检查器或面板。

## Demo 示例

一个最小的示例，展示如何在自己的编辑器模块中检查 `StateTreeToolset` 是否可用。

**MyEditorModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "StateTreeToolset.h" // 引入目标插件头文件

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    // 在编辑器启动时，检查 StateTreeToolset 插件状态
    if (FModuleManager::Get().IsModuleLoaded(TEXT("StateTreeToolset")))
    {
        UE_LOG(LogTemp, Display, TEXT("StateTreeToolset 插件已激活，检查工具可用。"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("StateTreeToolset 插件未加载。请确保在插件设置中启用它。"));
    }
}

void FMyEditorModule::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。其 `.Build.cs` 仅依赖 `Core` 模块。但请注意，该插件在 `.uplugin` 中声明了对 `StateTree` 和 `ToolsetRegistry` 插件的运行时依赖。

## 维护状态

### 近期更新

- 2026-04-03 7f02bd73 [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r
- 2026-04-01 4dcdfdfe [AI Toolsets]: Move StateTreeToolset under the Toolsets directory

### 维护评价

- **创建时间**：2026年4月1日，非常新的插件。
- **最近更新**：在创建后两天内就有一次提交，主要是架构调整（移动加载阶段和目录），表明其处于积极的初期开发和整合阶段。
- **活跃状态**：**活跃维护**。作为 Epic Games 官方维护的实验性工具集，预计将随着 StateTree 和 ToolsetRegistry 框架的发展而持续更新。
- **已知限制**：标记为 `IsExperimentalVersion` 和 `EnabledByDefault=false`，意味着它可能不稳定，API 和功能在未来版本中可能发生重大变化，且需要用户手动启用。
- **推荐使用**：**谨慎推荐**。如果你正在深度使用 StateTree 并需要高级调试功能，可以启用此插件以获取可能的便利。但由于其实验性质，不建议在需要高度稳定性的生产项目中依赖它。建议关注其后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/StateTreeToolset)
- [官方文档]() （暂无）