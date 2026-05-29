# UAF Chooser

> Chooser integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 选择器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFChooser` (Runtime), `UAFChooserEditor` (Runtime), `UAFChooserUncookedOnly` (Runtime), `UAFChooserTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser) | |

## 用途

本插件的核心功能是将 Unreal 引擎的 Chooser（动画选择器）系统与 UAF（Unreal Animation Framework）动画框架进行集成。它解决了在 UAF 框架下，开发者无法直接使用 Chooser 资产来驱动动画逻辑的问题。通过此插件，开发者可以在 UAF 的动画图或数据管道中引用和评估 Chooser 资产，从而利用 Chooser 强大的表格化、条件驱动选择能力来管理复杂的动画状态和过渡，使动画系统的设计更加数据驱动和直观。

## 使用场景

- 当你在使用 UAF (Unreal Animation Framework) 开发动画系统，并希望利用 Chooser 来定义基于上下文（如速度、方向、角色状态）的动画选择逻辑时，你需要启用此插件。
- 你的 UAF 动画图需要连接一个外部定义的动画选择表，而不是硬编码一系列动画片段，此时需要本插件提供的集成节点和数据结构。
- 当你的动画资产众多且结构复杂，需要一个清晰的、类似数据库的视图（工作区大纲）来管理和选择它们时。

## 蓝图用法

基于 Chooser 插件的通用模式，UAF 集成很可能提供了用于在 UAF 环境中评估 Chooser 的核心蓝图节点。由于本插件主要为数据管道和动画图集成，以下节点是预期会提供的关键类型。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Chooser Item` | 根据提供的上下文数据（结构体）评估指定的 Chooser 资产，返回选中的结果。 | `UChooserFunctionLibrary` (推测) |
| `Set Context Value` | 向 Chooser 评估上下文中设置一个键值对。 | `UChooserFunctionLibrary` (推测) |
| `Evaluate Chooser` | 在动画蓝图或 UAF 图中调用，执行一次 Chooser 评估并输出结果。 | 相关的 UAF 集成节点 |

### 使用示例（蓝图描述）

1.  **获取动画**：在动画蓝图的 `AnimGraph` 中，使用 `Evaluate Chooser` 节点。将“Chooser Asset”引脚连接到你的 `UChooserTable` 资产。通过 `Set Context Value` 节点或直接连接结构体，将角色当前的速度、是否在空中等信息作为上下文输入。节点的输出引脚将返回根据条件表选中的动画序列或蒙太奇。
2.  **管理资产**：`FUAFChooserOutlinerItemData` 结构体用于在自定义编辑器面板（工作区大纲）中表示一个 Chooser 条目或动画资产。其 `ObjectPath` 存储资产路径，`bIsNestedObject` 标识它是否为嵌套对象，`bExternalAsset` 标识它是否为外部资产。这允许编辑器扩展以清晰的树状结构展示和管理动画资源。

## C++ 用法

### 头文件引入

要使用 `UAFChooserUncookedOnly` 模块提供的数据结构，你需要包含其公共头文件。

```cpp
#include "UAFAnimChooserOutlinerData.h"
```

### 基本用法

使用 `FUAFChooserOutlinerItemData` 结构体来存储和传递动画 Chooser 大纲项的信息。这通常用于编辑器扩展，以在自定义面板中展示资产数据。

```cpp
// 来源: Source/UAFChooserUncookedOnly/Public/UAFAnimChooserOutlinerData.h
#include "UAFAnimChooserOutlinerData.h"

void CreateOutlinerEntry()
{
    FUAFChooserOutlinerItemData ItemData;
    ItemData.ObjectPath = FSoftObjectPath("/Game/Anim/ChooserTable01.ChooserTable01");
    ItemData.bIsNestedObject = false;
    ItemData.bExternalAsset = true;

    // 将 ItemData 传递给你的自定义大纲视图进行渲染
    // ...
}
```

## Demo 示例

一个最小的示例，展示如何创建一个 `FUAFChooserOutlinerItemData` 实例并访问其属性。

**MyAnimDataHolder.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UAFAnimChooserOutlinerData.h"

UCLASS()
class UMyAnimDataHolder : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, Category = "Chooser")
    FUAFChooserOutlinerItemData StoredItem;
};
```

**MyAnimDataHolder.cpp**
```cpp
#include "MyAnimDataHolder.h"

void UMyAnimDataHolder::InitSampleData()
{
    StoredItem.ObjectPath = FSoftObjectPath("/Game/Characters/Hero/ABP_HeroAnim.ABP_HeroAnim");
    StoredItem.bIsNestedObject = true;
    StoredItem.bExternalAsset = false;

    UE_LOG(LogTemp, Log, TEXT("Stored Asset Path: %s"), *StoredItem.ObjectPath.ToString());
}
```

## 模块依赖

本插件是 UAF 生态系统的一部分，其核心依赖于 `UAF` 和 `Chooser` 插件。你的项目或模块需要依赖这些模块才能正常使用集成的完整功能。

| 模块 | 用途 |
|---|---|
| `UAF` | 提供核心的 Unreal Animation Framework 运行时和蓝图节点 |
| `Chooser` | 提供 Chooser 表的资产类型、编辑器和运行时评估逻辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 为具有单个子节点的动画节点添加了修改器动画节点数据基类，增强了动画图的扩展性 |
| 2026-03-19 | `910301d3` | UAF Anim Node rewind debugger track | 添加了 UAF 动画节点的倒带回放调试器跟踪功能，便于调试动画状态 |
| 2026-03-11 | `bda4ef8e` | Add debug update counter to UAF anim node to enforce invariants | 向 UAF 动画节点添加调试更新计数器，以确保状态更新的正确性 |
| 2026-03-11 | `7da85466` | Implement AnimOp system for new UAF runtime | 为新的 UAF 运行时实现了 AnimOp 系统，是底层架构的重要更新 |
| 2026-03-10 | `5a95823d` | AnimNodes Blend stack helper class to avoid too much code duplication (it can be used as either a b... | 添加了动画节点混合栈辅助类，减少代码重复，提高了混合逻辑的代码复用性 |

### 维护评价

该插件创建于 2025 年 6 月，截至 2026 年 4 月仍有频繁的功能性提交，表明它处于**活跃开发**阶段。最近的更新集中在 UAF 运行时动画节点的核心架构改进（如 AnimOp 系统、混合栈）、调试工具支持（倒回跟踪、更新计数器）以及代码质量优化上。这些改动表明插件正在从基础框架向功能完善和调试友好的方向快速发展。

**综合评价**：这是一个非常新的实验性插件，与最新的 UAF 和 Chooser 框架深度集成。由于它处于早期开发阶段（版本 0.1），API 和功能可能会发生快速变化。**目前仅推荐给需要在前沿 UAF 项目中使用 Chooser 集成，并且愿意跟进和适应 API 变化的开发者**。不建议用于需要高度稳定性的生产项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser)
- [官方文档]() (暂无)
- [测试用例]() (路径: `Tests/UAFChooserTests`)