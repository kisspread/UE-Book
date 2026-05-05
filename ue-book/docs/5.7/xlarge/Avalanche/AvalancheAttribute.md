# Motion Design - AvalancheAttribute 模块

> 为 Motion Design 插件提供可扩展的属性系统，允许用户为场景中的对象附加自定义元数据，用于分类、筛选和驱动行为。

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheAttribute` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheAttribute) | |

## 用途

`AvalancheAttribute` 模块是 Motion Design 插件属性系统的核心。它定义了一个轻量级、可扩展的框架，用于向任何 UObject（特别是场景中的 Actor 或 Component）附加描述性数据（属性）。这些属性不是对象的固有部分，而是像“标签”或“元数据”一样附加其上，用于实现以下目的：

1.  **分类与筛选**：通过标签（Tag）属性，用户可以为对象分组，便于在编辑器或运行时进行批量选择、过滤和操作。
2.  **数据驱动**：通过名称（Name）等属性，可以存储简单的键值对信息，供其他系统（如远程控制、动画逻辑）读取和使用。
3.  **系统集成**：作为 Motion Design 生态的基础组件，为其他模块（如 `AvalancheTag`、`AvalancheRemoteControl`）提供统一的属性访问接口。

## 使用场景

-   你在使用 Motion Design 进行虚拟制片，需要为场景中的多个灯光 Actor 打上“主光”、“补光”的标签，以便通过标签快速控制它们的开关和强度。
-   你正在构建一个动态场景，需要给不同的模型附加“可交互”、“可破坏”等属性，供游戏逻辑或蓝图查询。
-   你需要为场景元素添加自定义的名称标识，用于远程控制面板的精确绑定。

## 蓝图用法

该模块主要提供属性数据结构，其蓝图交互通常通过上层模块（如 `AvalancheTag`）或编辑器工具进行。以下是其核心数据结构的蓝图访问方式：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Name` | 设置名称属性的值 | `UAvaNameAttribute` |
| `Set Tag` | 设置单个标签句柄 | `UAvaTagAttribute` |
| `Set Tag Container` | 设置标签容器（多个标签） | `UAvaTagContainerAttribute` |

### 使用示例（蓝图描述）

1.  **获取对象的属性**：通常通过 `AvalancheTag` 或 `AvalancheOutliner` 模块提供的函数，获取目标对象上附加的 `UAvaAttribute` 数组。
2.  **检查与设置**：在蓝图中，你可以将获取到的属性对象转换为具体类型（如 `UAvaTagAttribute`），然后调用 `Set Tag` 节点来修改其值。
3.  **查询**：使用 `Contains Tag` 等函数检查对象是否拥有特定标签。

## C++ 用法

### 头文件引入

```cpp
#include "AvaAttribute.h"
#include "AvaNameAttribute.h"
#include "Tags/AvaTagAttribute.h"
#include "Tags/AvaTagContainerAttribute.h"
```

### 基本用法

创建一个自定义属性类。

```cpp
// MyCustomAttribute.h
#pragma once

#include "AvaAttribute.h"
#include "MyCustomAttribute.generated.h"

UCLASS(DisplayName="My Custom Attribute")
class UMyCustomAttribute : public UAvaAttribute
{
    GENERATED_BODY()

public:
    virtual FText GetDisplayName() const override
    {
        return FText::FromString(TEXT("My Custom Data"));
    }

    UPROPERTY(EditAnywhere, Category="Data")
    float SomeValue = 0.f;
};
```

### 进阶用法

在运行时为对象添加和查询属性。

```cpp
// 假设我们有一个 AActor* TargetActor
// 1. 创建一个属性实例
UMyCustomAttribute* NewAttr = NewObject<UMyCustomAttribute>(TargetActor);
NewAttr->SomeValue = 42.0f;

// 2. 将属性附加到对象（通常通过一个属性管理器组件或子系统完成）
// 这里仅为示意，实际添加逻辑由上层模块（如AvalancheOutliner）管理
// TargetActor->AddAttribute(NewAttr);

// 3. 查询对象上的属性
// TArray<UAvaAttribute*> Attributes = TargetActor->GetAttributes();
// for (UAvaAttribute* Attr : Attributes)
// {
//     if (UMyCustomAttribute* CustomAttr = Cast<UMyCustomAttribute>(Attr))
//     {
//         float Value = CustomAttr->SomeValue;
//         // ... 使用 Value
//     }
// }
```

## Demo 示例

一个最小的自定义属性定义。

```cpp
// SimpleTextAttribute.h
#pragma once

#include "AvaAttribute.h"
#include "SimpleTextAttribute.generated.h"

/** 一个存储简单文本的属性 */
UCLASS(DisplayName="Simple Text")
class USimpleTextAttribute : public UAvaAttribute
{
    GENERATED_BODY()

public:
    virtual FText GetDisplayName() const override
    {
        return FText::FromString(TEXT("Simple Text"));
    }

    UPROPERTY(EditAnywhere, Category="Content")
    FString TextContent;
};
```

```cpp
// SimpleTextAttribute.cpp
#include "SimpleTextAttribute.h"

// 通常不需要额外的 .cpp 实现，除非有复杂的逻辑。
// 此文件可以留空或包含类的默认实现。
```

## 模块依赖

从模块名和头文件依赖推断，该模块的依赖非常基础。

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | Motion Design 插件的核心基础模块，可能提供通用的类型、接口或子系统。 |

## 维护状态

### 近期更新

```
- 2024-01-30 5e98ccb853ee Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```

### 维护评价

-   **创建时间**：2024年1月，是Motion Design插件从实验性阶段迁移至正式VirtualProduction分类时的一部分。
-   **最近更新**：仅有一次大规模的目录迁移记录，没有针对本模块的功能性更新或bug修复记录。
-   **活跃度**：作为Motion Design这一大型、活跃插件的基础模块，它很可能随着主插件一起被维护和更新，但独立的提交记录较少。
-   **推荐使用**：**是**。这是Motion Design插件的核心组成部分，如果你正在使用或计划使用Motion Design进行虚拟制片，那么理解和使用此模块是必要的。它设计良好，提供了清晰的扩展点。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheAttribute)
-   [Motion Design 插件主文档](https://docs.unrealengine.com/5.7/en-US/motion-design-in-unreal-engine/) (官方文档)