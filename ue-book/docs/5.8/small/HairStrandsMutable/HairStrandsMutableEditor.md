# Mutable Groom Extensions

> Adds Mutable functionality to work with Grooms from the HairStrands plugin

| 属性 | 值 |
|---|---|
| 中文名 | Groom可变体 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HairStrandsMutable` (Runtime), `HairStrandsMutableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairStrandsMutable) | |

## 用途

该插件是 [Mutable](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Mutable) 可变角色系统与 [HairStrands](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands) 毛发系统之间的桥梁。其核心用途是**扩展 Mutable 系统，使其能够处理和管理 Groom（毛发）资产**。

具体来说，它允许开发者在 Mutable 的自定义对象（Customizable Object）图中，将 Groom 定义为一个**可变常量（Constant）**。这意味着角色的发型可以像改变服装材质或网格体一样，成为角色可定制系统的一部分。Mutable 系统在生成和应用实例时，会根据该节点的输出，自动实例化或移除相应的 Groom 组件，从而实现运行时角色发型的动态切换和变化。

## 使用场景

-   **角色自定义系统**：正在开发一个带有深度角色自定义功能的游戏（如 MMO、模拟人生），玩家可以选择不同的发型，这些发型由 Groom 资产构成。
-   **Groom 动态绑定**：希望 Groom 的加载、显示与角色 Mesh 的加载和 Mutable 实例的生成同步，确保在角色部件加载或卸载时，发型也能正确地附加或移除。
-   **资产流水线集成**：希望将 Groom 纳入已有的基于 Mutable 的资产管理和生成流水线中，实现统一的角色部件管理。

## 蓝图用法

该插件的核心功能（节点 `UCustomizableObjectNodeGroomConstant`）主要在 **Mutable 编辑器** 中通过节点图使用，而非在运行时通过蓝图节点调用。

### 核心节点（编辑器中）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Groom Constant` | 将一个 Groom 资产导入到 Mutable 自定义对象图中，作为一个可配置的常量数据。 | `UCustomizableObjectNodeGroomConstant` |

### 使用示例（蓝图描述）

在 Mutable 编辑器中：
1.  打开或创建一个 `UCustomizableObject` 资产。
2.  在节点图空白处右键，搜索并添加 “Groom Constant” 节点。
3.  在该节点的属性面板中，从下拉菜单选择你希望作为可变部件的 `UGroomAsset`。
4.  该节点将输出一个 `Groom Pin` 数据，可以将其连接到需要发型的 `Object` 或 `Material` 相关节点上，从而定义该发型在最终可变实例中的配置。

## C++ 用法

该插件的 C++ 接口主要用于与 Mutable 编译器集成或自定义节点行为，运行时使用主要通过上述编辑器节点配置。

### 头文件引入

```cpp
#include “CustomizableObjectNodeGroomConstant.h”
```

### 基本用法

在 C++ 中，你可以直接操作或继承 `UCustomizableObjectNodeGroomConstant` 类，但这通常只在你需要创建全新的、自定义的 Groom 常量节点变体时才需要。标准的使用流程是完全通过编辑器节点图完成的。

**示例：以编程方式设置 Groom 常量节点的数据**
```cpp
// 假设你通过某种方式（如工厂方法）获取或创建了一个 UCustomizableObjectNodeGroomConstant 节点实例
UCustomizableObjectNodeGroomConstant* GroomNode = GetMutableDefault<UCustomizableObjectNodeGroomConstant>();

// 构建 Groom 的 Pin 数据（实际中通常通过编辑器UI设置）
FGroomPinData NewGroomData;
NewGroomData.GroomAsset = LoadObject<UGroomAsset>(nullptr, TEXT(“/Game/Characters/Hairstyles/GroomAsset_LongHair.GroomAsset_LongHair”));
// ... 设置其他必要数据

// 在编辑器上下文中修改节点属性（通常在 PostEditChangeProperty 中处理）
GroomNode->SetGroomData(NewGroomData); // 注意：此函数为示意，实际属性名为 `GroomData`，访问方式可能不同
```

## Demo 示例

以下是一个最小化的、展示如何扩展或使用 `UCustomizableObjectNodeGroomConstant` 的 C++ 类结构示例。

```cpp
// MyGroomNode.h
#pragma once

#include “CoreMinimal.h”
#include “CustomizableObjectNodeGroomConstant.h”
#include “MyGroomNode.generated.h”

UCLASS()
class UMyGroomConstantNode : public UCustomizableObjectNodeGroomConstant
{
    GENERATED_BODY()

public:
    UMyGroomConstantNode();

    // 可以重写基类的方法来自定义行为或外观
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
    // ...
};
```

```cpp
// MyGroomNode.cpp
#include “MyGroomNode.h”

UMyGroomConstantNode::UMyGroomConstantNode()
{
    // 构造函数，可以初始化一些默认值
}

FText UMyGroomConstantNode::GetNodeTitle(ENodeTitleType::Type TitleType) const
{
    return LOCTEXT(“MyGroomNode_Title”, “My Custom Groom”);
}
```

## 模块依赖

该插件本身依赖于 `HairStrands` 和 `Mutable` 插件。在你的模块中使用其功能（如引用其头文件或类型），需要确保依赖这两个基础插件提供的模块。

| 模块 | 用途 |
|---|---|
| `HairStrands` | 提供 Groom 资产、组件和相关类型定义。 |
| `Mutable` | 提供可变对象、节点系统和编译器框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `814648b2` | [mutable] Fixed check failure when trying to spawn a new object on a PostLoad call. | 修复在 PostLoad 期间生成新对象时出现的检查失败错误。 |
| 2026-03-11 | `aeecf60f` | [HairStrandsMutable] Fix ensure when registgering to Movie Sequence Template actors. | 修复向电影序列模板演员注册时触发的 ensure 断言。 |
| 2026-03-06 | `87b39b7f` | [Mutable] Fix Extension Data not being applied when an Instance is already generated. | 修复当实例已生成时扩展数据未被应用的问题。 |
| 2026-02-27 | `f8a35ec8` | [Mutable] Add support for UAssetUserData in SKM Parameter and Constants nodes. | 在骨骼网格体参数和常量节点中添加对 UAssetUserData 的支持。 |
| 2026-01-29 | `17d7a59b` | [Mutable] Fix PSO check with grooms. | 修复与 Groom 相关的管线状态对象检查。 |

### 维护评价

该插件自2024年8月创建，至今约1年，仍处于 **🆕** 状态。从提交历史看，最近几个月（截至2026年5月）仍有**持续的维护和Bug修复活动**，主要聚焦于与底层 Mutable 系统的兼容性和运行时稳定性问题修复。这表明它是一个**活跃维护中**的实验性插件。

**优点**：
-   官方（Epic Games）维护，与引擎核心毛发和可变系统同步更新。
-   持续修复关键问题，保障基本功能稳定性。

**注意事项**：
-   **实验性**：插件标记为 `IsExperimentalVersion: true` 且默认未启用，意味着其API和功能可能会发生变化，不建议在最终发布的稳定产品中毫无准备地使用。
-   **依赖关系复杂**：它同时依赖 `HairStrands` 和 `Mutable` 两个较为庞大的系统，调试和理解可能具有挑战性。

**推荐**：如果你的项目已经深度使用了 Mutable 和 HairStrands 系统，并且有实现动态 Groom 的刚性需求，可以考虑使用此插件作为解决方案。在使用前，建议充分了解 Mutable 和 HairStrands 的基本工作原理，并准备好应对实验性功能可能带来的不稳定性和更新风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairStrandsMutable)
- [HairStrands 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands)
- [Mutable 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Mutable)