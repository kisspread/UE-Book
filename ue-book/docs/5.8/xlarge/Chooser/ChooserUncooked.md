# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 中文名 | 动态选择器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产选择逻辑） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Runtime), `ChooserUncooked` (Runtime), `ProxyTable` (Runtime), `ProxyTableEditor` (Runtime), `ProxyTableUncooked` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser) | |

## 用途

Chooser 是一个数据驱动的资产选择系统。它允许开发者通过定义“选择器表”（Chooser Table）来建立一套规则，在游戏运行时根据当前的上下文（如 Gameplay Tags、参数值等）动态地选择出合适的资产（如动画蒙太奇、数据表行、逻辑资产等）。其核心价值在于将复杂的 `if-else` 或 `switch` 选择逻辑从硬编码中剥离出来，转化为可视化、易于调整的配置数据，特别适用于动画蓝图中需要根据角色状态动态混合不同动画栈的场景。

## 使用场景

- **动态动画混合**：在动画蓝图中，需要根据角色当前的状态（如持有武器类型、移动速度、姿态）从多个动画蒙太奇或动画蓝图中动态选择一个作为主要混合源。
- **数据驱动配置**：需要根据不同的游戏模式、角色职业或难度等级，从一组预设的资产（如数据表、配置对象）中选取一项来使用。
- **上下文感知逻辑**：希望根据 `FGameplayTag` 或其他上下文参数，自动选择最合适的代理对象或行为资产。

## 蓝图用法

蓝图功能主要通过自定义的 K2 节点提供。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Chooser` (Legacy) | （隐藏，旧版）查询 Chooser 表，根据输入上下文获取一个结果对象。 | `UK2Node_EvaluateChooser` |
| `Evaluate Chooser` | （新版）查询 Chooser 表，支持根据输入上下文获取一个或多个结果对象/结构体，并可指定输出模式。 | `UK2Node_EvaluateChooser2` |
| `Get Chooser Context Parameters` | 从 `UChooserSignature` 资产获取其定义的上下文参数列表，用于构建传递给 Chooser 的上下文。 | `UK2Node_GetChooserContextParameters` |
| `Chooser Player` (动画节点) | 在动画蓝图中直接作为动画节点使用，内部使用 Chooser 逻辑选择并播放动画。 | `UAnimGraphNode_ChooserPlayer` |

### 使用示例（蓝图描述）

1.  **基础资产查询**：
    - 在蓝图中添加 `Evaluate Chooser` 节点。
    - 在节点细节面板中，指定要查询的 `ChooserTable` 资产。
    - 将用于决策的上下文（如一个 Gameplay Tag 容器）连接到节点的 `Context` 输入引脚。
    - 节点将根据表中配置的规则，输出匹配到的目标对象（`Result` 引脚）。
2.  **构建上下文参数**：
    - 添加 `Get Chooser Context Parameters` 节点，并指定一个定义好的 `ChooserSignature` 资产。
    - 该节点会输出该签名所需的所有上下文参数名称和类型。
    - 利用这些信息，可以在其他蓝图逻辑中准备好对应的参数结构体，用于传递给 `Evaluate Chooser`。

## C++ 用法

### 头文件引入

使用 Chooser 的运行时功能时，通常需要引入以下头文件（具体取决于使用的模块）：

```cpp
#include "Chooser/ChooserTable.h" // 核心 Chooser 数据资产
#include "Chooser/ChooserPropertyBinding.h" // 属性绑定相关
#include "ProxyTable/ProxyTable.h" // 如果使用代理表
```

### 基本用法

从其蓝图节点的设计可以推断出 C++ 中的基本使用模式。核心是 `UChooserTable` 对象和对它的评估。

```cpp
// 假设已经有一个 UChooserTable* ChooserTableAsset 和准备好上下文的 FInstancedStruct Context。
// 评估 Chooser 表以获取结果资产
FObjectChooserBase::FObjectChooserIterator Iter;
ChooserTableAsset->Evaluate(Context, Iter);

// 迭代所有结果（如果模式是 AllResults）
while (Iter.HasNext())
{
    UObject* ResultAsset = Iter.Next();
    // 使用结果资产...
}
```

### 进阶用法

更复杂的用法涉及定义自定义的上下文和结果类型。`UChooserTable` 使用 `UChooserSignature` 来定义其输入上下文参数的结构和输出结果的类型约束。开发者可能需要继承 `UObjectChooserBase` 或实现 `IChooserParameterInterface` 来创建自定义的评估逻辑。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何程序化地评估一个已加载的 Chooser 表。

```cpp
// MyDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameplayTagContainer.h"
#include "Chooser/ChooserTable.h"

class FMyChooserDemo
{
public:
    static void EvaluateChooser(UChooserTable* InChooserTable, const FGameplayTag& InContextTag);
};
```

```cpp
// MyDemo.cpp
#include "MyDemo.h"
#include "Chooser/ChooserEvaluation.h"

void FMyChooserDemo::EvaluateChooser(UChooserTable* InChooserTable, const FGameplayTag& InContextTag)
{
    if (!InChooserTable)
    {
        return;
    }

    // 构建一个包含单个 GameplayTag 的上下文
    FInstancedStruct Context = FInstancedStruct::Make<FChooserEvaluationContext>();
    // 注意：实际的上下文构建取决于你的 Chooser 签名如何定义。这里仅为示意。
    // FGameplayTagContainer TagContainer;
    // TagContainer.AddTag(InContextTag);
    // Context.GetMutable<FChooserEvaluationContext>().ContextTags = TagContainer;

    // 评估 Chooser
    FObjectChooserBase::FObjectChooserIterator Iter;
    InChooserTable->Evaluate(Context, Iter);

    if (Iter.HasNext())
    {
        UObject* SelectedAsset = Iter.Next();
        UE_LOG(LogTemp, Log, TEXT("Chooser selected asset: %s"), *GetNameSafe(SelectedAsset));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Chooser returned no result for the given context."));
    }
}
```

## 模块依赖

从插件的模块结构和 `.uplugin` 依赖分析，使用此插件时，你的模块可能需要依赖以下非标准模块（`Core`, `Engine` 等省略）：

| 模块 | 用途 |
|---|---|
| `Chooser` | Chooser 核心运行时逻辑（评估、数据）。 |
| `ChooserEditor` | 编辑器支持，用于 Chooser 表和蓝图节点的编辑器UI。 |
| `ProxyTable` | 代理表运行时逻辑，与 Chooser 紧密相关。 |
| `GameplayTags` | 运行时 Gameplay Tag 支持，常用于 Chooser 上下文。（来自插件依赖） |
| `GameplayTagsEditor` | 编辑器 Gameplay Tag 支持。（来自插件依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `aad6fe75` | Remove build setting making chooser internal headers public, and move most of those internal headers | 移除公开内部头文件的构建设置，并重组内部头文件位置，完善模块封装。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下因双精度常量截断为浮点数而产生的编译警告。 |
| 2026-05-12 | `333cccbc` | Add profiling tag to chooser property access | 为 Chooser 的属性访问操作添加性能分析标签，便于性能追踪。 |
| 2026-04-17 | `1eda8a87` | Fix chooser editor null pointer crash after native context type rename | 修复当原生上下文类型被重命名后，在编辑器中导致的 Chooser 空指针崩溃问题。 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | （内容浏览器相关）新增数据菜单项，可能涉及 Chooser 资产的快速创建。 |

### 维护评价

- **活跃维护**：插件自 2024 年 9 月从 Experimental 移出后，截至 2026 年 5 月仍在持续收到功能性更新和 Bug 修复。
- **近期重点**：近期的提交集中在**稳定性修复**（崩溃、警告）、**性能优化**（Profiling Tag）和**代码架构改进**（头文件重组），表明项目处于积极的维护和优化阶段。
- **推荐使用**：作为官方提供的、用于动画混合选择的数据驱动方案，且仍在活跃维护，对于有相关需求的项目是推荐使用的。但需注意其 `EnabledByDefault = false`，需要手动启用插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser)
- [官方文档]() （无）
- [测试用例]() （暂未在提供信息中发现）