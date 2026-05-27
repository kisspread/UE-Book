# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | 动画状态树 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器数据） |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Runtime), `UAFStateTreeUncookedOnly` (Runtime), `UAFStateTreeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

该插件是 Unreal Animation Framework (UAF) 与 StateTree 系统的深度集成。其核心目的是将 StateTree 作为动画逻辑的核心驱动层，无缝融入 UAF 的动画图编辑和运行时环境中。

与独立的 StateTree 组件不同，此插件旨在让动画师和程序员能在 **UAF 动画图编辑器** 内，直接使用 StateTree 来设计、组织和触发复杂的、状态驱动的动画逻辑。它解决了在 UAF 框架下实现复杂状态机和逻辑流程需要外部关卡蓝图或额外组件编排的痛点，将状态管理内化到动画资产本身。

## 使用场景

-   你正在使用 **UAF (Animation Framework)** 制作角色动画，需要实现一个包含多种状态（如巡逻、警觉、战斗、死亡）和复杂转换逻辑（如基于感知、距离、事件触发）的动画状态机。
-   你希望动画逻辑（状态、转换条件）与动画图（状态树、混合节点）**在同一个动画资产中**进行定义和编辑，而不是分散在多个外部组件中。
-   你需要一个**声明式、可视化**的工具来管理复杂的动画逻辑，而不是在蓝图或 C++ 中编写大量状态检查代码。

## 蓝图用法

该插件主要提供底层数据结构和编辑器集成，运行时蓝图节点通常在 `UAFStateTree` 主模块中。

### 核心节点（数据结构）

这些结构体通常作为 StateTree 的上下文或数据载体。

| 节点/结构体 | 说明 | 所在类/结构体 |
|---|---|---|
| `FAnimNextStateTreeOutlinerData` | 用于在 UAF 工作区大纲中表示一个包含 StateTree 的动画资产条目。 | `FAnimNextStateTreeOutlinerData` |
| `FAnimNextStateTreeStateOutlinerData` | 用于在大纲中表示 StateTree 内部的单个状态（State）条目，包含状态名、类型、颜色等详细信息。 | `FAnimNextStateTreeStateOutlinerData` |

## C++ 用法

此插件侧重于编辑器集成和编译流程，运行时 API 相对较少。主要的 C++ 交互发生在编辑器模块和动画图编译上下文中。

### 头文件引入

```cpp
#include “AnimNextStateTreeWorkspaceExports.h” // 包含大纲数据结构
#include “AnimNextStateTreeEditorData.h” // 包含编辑器数据
```

### 基本用法（编辑器数据集成）

以下代码展示了如何从 UAF 编辑器数据中获取与 StateTree 相关的信息，通常用于自定义编辑器扩展或工具。

```cpp
// 来源：推测基于 Internal/AnimNextStateTree_EditorData.h 和 Public/AnimNextStateTreeEditorData.h 的交互逻辑

// 假设你有一个指向 UAnimNextStateTree_EditorData 的指针
UAnimNextStateTree_EditorData* StateTreeEditorData = GetStateTreeEditorData();

if (StateTreeEditorData)
{
    // 1. 获取根参数属性包（所有共享变量的集合）
    const FInstancedPropertyBag& RootParams = StateTreeEditorData->GetRootParametersPropertyBag();
    
    // 2. (在编辑器上下文中) 你可能需要重新编译整个动画图的虚拟机
    StateTreeEditorData->RecompileVM();
    
    // 3. 获取该资产支持的条目类型（例如，StateTree 资源条目）
    TConstArrayView<TSubclassOf<UUAFRigVMAssetEntry>> EntryClasses = StateTreeEditorData->GetEntryClasses();
    // ... 使用 EntryClasses 来了解可以添加哪些类型的资源到这个动画图中
}
```

### 进阶用法（自定义工作区导出）

如果你想扩展工作区大纲，显示自定义的 StateTree 信息，可以参考 `UAnimNextStateTreeWorkspaceAssetUserData` 的实现模式。

```cpp
// 来源：Internal/AnimNextStateTreeWorkspaceAssetUserData.h
// 展示如何重写函数来为资产添加自定义导出数据（例如，大纲节点）

class UMyCustomWorkspaceUserData : public UAnimNextAnimGraphWorkspaceAssetUserData
{
    GENERATED_BODY()

protected:
    // 重写此函数以提供资产根节点的导出数据（通常对应 FAnimNextStateTreeOutlinerData）
    virtual void GetRootAssetExport(FAssetRegistryTagsContext Context) const override
    {
        // ... 创建 FAnimNextStateTreeOutlinerData 并设置到 Context
        Super::GetRootAssetExport(Context);
    }

    // 重写此函数以提供资产内部资源（如每个 State 状态）的导出数据
    virtual void GetWorkspaceAssetExports(FAssetRegistryTagsContext Context) const override
    {
        // 遍历资产内的所有状态，为每个状态创建一个 FAnimNextStateTreeStateOutlinerData
        // 并设置其 StateName, StateId, Type, Color 等属性
        // 最后将这些数据添加到 Context
        Super::GetWorkspaceAssetExports(Context);
    }
};
```

## Demo 示例

一个最小示例，展示如何从自定义动画图资产中提取 StateTree 状态信息用于显示。

```cpp
// MyAnimationTool.h
#pragma once

#include “CoreMinimal.h”
#include “AnimNextStateTreeWorkspaceExports.h”

class FMyAnimationTool
{
public:
    // 从资产数据中解析出状态树状态列表
    static TArray<FAnimNextStateTreeStateOutlinerData> GetStateTreeStatesFromAssetData(const UAnimNextStateTree_EditorData* EditorData);
};

// MyAnimationTool.cpp
#include “MyAnimationTool.h”
#include “AnimNextStateTreeEditorData.h” // 访问编辑器数据
// #include “StateTreeEditorData.h” // 假设包含 StateTree 状态定义的头文件

TArray<FAnimNextStateTreeStateOutlinerData> FMyAnimationTool::GetStateTreeStatesFromAssetData(const UAnimNextStateTree_EditorData* EditorData)
{
    TArray<FAnimNextStateTreeStateOutlinerData> Result;
    if (!EditorData) return Result;

    // 从 EditorData 获取其关联的 StateTree 编辑器数据
    // 注意：具体获取路径依赖于内部实现，以下为概念性代码
    const UStateTreeEditorData* STEditorData = /* ... 从 EditorData 获取 ... */;

    if (STEditorData)
    {
        // 遍历 StateTree 编辑器数据中的状态
        // for (const FStateTreeStateHandle& StateHandle : STEditorData->GetAllStates())
        // {
        //     FAnimNextStateTreeStateOutlinerData StateData;
        //     StateData.StateName = STEditorData->GetStateName(StateHandle);
        //     StateData.StateId = STEditorData->GetStateId(StateHandle);
        //     StateData.Type = STEditorData->GetStateType(StateHandle);
        //     // ... 设置其他属性
        //     Result.Add(MoveTemp(StateData));
        // }
    }

    return Result;
}
```

## 模块依赖

该插件为 UAF 框架扩展，使用前需确保你的模块已依赖 UAF 核心。

| 模块 | 用途 |
|---|---|
| `UAF` | 动画框架（Unreal Animation Framework）的核心模块，提供动画图、编辑器数据等基础设施。 |
| `StateTree` | Epic 的状态树系统，提供状态机运行时和编辑器逻辑。 |
| `RigVM` | UAF 底层使用的虚拟机框架，用于驱动动画图逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏更新为新的格式。 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rather | 状态树：更新了引用结构体细节，现在显示结构体的显示名称而非技术名。 |
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in sepa | 添加了 UAFSharedAssets 插件，用于存放引用其他 UAF 插件资产的共享内容。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将 GetComponent 函数重命名为 GetOrAddComponent，更准确反映其功能。 |
| 2026-03-31 | `4e41a45f` | Fix crash attempting to manually create UAF ST by hiding UAF ST Schema | 修复了手动创建 UAF StateTree 时因显示 Schema 导致的崩溃问题，通过隐藏相关 Schema 解决。 |

### 维护评价

该插件创建于 **2025年6月**，目前处于**积极维护**状态。从近期提交记录看，更新非常频繁（最近一次更新在2026年4月），内容涉及功能增强（结构体显示优化）、错误修复（崩溃修复）和底层架构调整（日志宏迁移、函数重命名）。由于它被标记为 **实验性** (`IsExperimentalVersion=true`) 且 **默认未启用**，表明它仍在快速迭代和验证阶段，尚未稳定。

**建议**：可以积极关注和用于原型开发，但不建议在关键生产项目中作为唯一方案。需留意其 API 和行为可能随版本更新而变化。鉴于其活跃的开发状态和与核心动画框架（UAF）的深度集成，它未来有潜力成为 UAF 工作流中的重要组成部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree)
- 测试用例路径 (推测): `Engine/Plugins/Experimental/UAF/UAFStateTree/Tests/`