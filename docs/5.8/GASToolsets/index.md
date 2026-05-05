# GASToolsets

> Toolsets for the Gameplay Ability System（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GASToolsets` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GASToolsets) | |

## 用途

GASToolsets 是一个**编辑器专用**插件，为 Unreal Engine 的 Gameplay Ability System (GAS) 提供了一套工具集（Toolset）。它的核心目的是**为 AI 助手（AI Assistant）等自动化工具提供结构化的接口**，以便在编辑器内查询、检查和操作 GAS 的核心数据，例如运行时属性值、活跃效果、已授予的能力、项目中的 AttributeSet 类以及 GameplayCue。

这个插件解决了在编辑器中难以直观地查看和调试 GAS 运行状态的问题。它将 GAS 的复杂数据（如属性、效果、能力）封装成简单的结构体和函数，使得外部工具（如 AI 助手）能够以编程方式理解和操作游戏能力系统，从而辅助开发者进行调试、配置和内容创作。

## 使用场景

- 你正在使用或开发一个集成 AI 助手的编辑器工具，需要让 AI 理解项目中的 GAS 设置（如有哪些 AttributeSet，每个属性集有哪些属性）。
- 你需要在编辑器内以编程方式检查某个 Actor 当前的属性值、活跃的 GameplayEffect 或已授予的 GameplayAbility。
- 你需要在编辑器中查询项目里注册的所有 GameplayCue 标签及其关联的 Notify 资产。
- 你正在为 GAS 编写自动化测试或编辑器扩展，需要一个便捷的接口来获取 GAS 相关信息。

## 蓝图用法

该插件主要为 AI 助手（标记为 `AICallable`）设计，其函数主要通过 C++ 调用，但部分结构体和函数也暴露给了蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Attribute Set Classes` | 查找项目中所有 AttributeSet 子类（包括 C++ 和蓝图类）及其包含的属性。 | `UAttributeSetToolset` |
| `List Attributes` | 列出指定 AttributeSet 类名下的所有 Gameplay 属性。 | `UAttributeSetToolset` |
| `List Cues` | 列出项目中注册的 GameplayCue 标签，可按父标签过滤。 | `UGameplayCueToolset` |
| `Get Cue Info` | 获取指定 GameplayCue 标签的详细信息，包括关联的 Notify 资产路径和类型。 | `UGameplayCueToolset` |
| `Execute Cue On Selected Actor` | 在编辑器中当前选中的 Actor 上执行一个 GameplayCue（非复制）。 | `UGameplayCueToolset` |

### 使用示例（蓝图描述）

1.  **查询属性集**：在蓝图中，调用 `UAttributeSetToolset::FindAttributeSetClasses` 节点，返回一个 `FAttributeSetClassInfo` 数组。遍历此数组，可以获取每个属性集的类名、资产路径以及其包含的 `FGameplayAttributeInfo` 列表。
2.  **检查运行时状态**：要检查某个 Actor 的 GAS 状态，需要先获取其 `UAbilitySystemComponent`，然后调用 `UAbilitySystemInspectorToolset` 中的函数（如 `GetRuntimeAttributeValues`），传入组件引用，即可获得 `FRuntimeAttributeValue` 数组，包含每个属性的基值和当前值。

## C++ 用法

### 头文件引入

```cpp
#include "GASToolsets.h" // 模块主头文件
#include "AttributeSetToolset.h" // AttributeSet 工具集
#include "GameplayCueToolset.h" // GameplayCue 工具集
#include "AbilitySystemInspectorToolset.h" // 运行时检查工具集
```

### 基本用法

以下代码展示了如何定义一个用于测试的 AttributeSet 和 Actor，这是使用 GASToolsets 进行检查的基础。
*来源文件: `Source/GASToolsets/Private/Tests/AttributeSetToolsetTest.h` 和 `Source/GASToolsets/Private/Tests/AbilitySystemInspectorToolsetTest.h`*

```cpp
// 1. 定义一个简单的 AttributeSet 子类
UCLASS(Hidden, MinimalAPI)
class UMyHealthAttributeSet : public UAttributeSet
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintReadOnly, Category = "Attribute")
    FGameplayAttributeData Health;
    UPROPERTY(BlueprintReadOnly, Category = "Attribute")
    FGameplayAttributeData MaxHealth;
};

// 2. 定义一个拥有 AbilitySystemComponent 的 Actor
UCLASS(Hidden, MinimalAPI)
class AMyGASActor : public AActor, public IAbilitySystemInterface
{
    GENERATED_BODY()
public:
    AMyGASActor()
    {
        AbilitySystemComponent = CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("ASC"));
        // 通常还需要创建并添加 AttributeSet 子对象
    }

    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override
    {
        return AbilitySystemComponent;
    }

    UPROPERTY()
    TObjectPtr<UAbilitySystemComponent> AbilitySystemComponent;
};
```

### 进阶用法

在拥有上述基础对象后，可以在编辑器工具或自动化测试中调用 GASToolsets 的函数来获取信息。
*（基于工具集函数的典型调用模式）*

```cpp
// 假设我们已经有一个有效的 UAbilitySystemComponent* ASC

// 1. 查询项目中所有的 AttributeSet 类
TArray<FAttributeSetClassInfo> AllAttributeSets = UAttributeSetToolset::FindAttributeSetClasses();
for (const FAttributeSetClassInfo& SetInfo : AllAttributeSets)
{
    UE_LOG(LogGASToolsets, Log, TEXT("Found AttributeSet: %s"), *SetInfo.ClassName);
}

// 2. 检查特定 Actor 的运行时属性值
TArray<FRuntimeAttributeValue> RuntimeValues = UAbilitySystemInspectorToolset::GetRuntimeAttributeValues(ASC);
for (const FRuntimeAttributeValue& Value : RuntimeValues)
{
    UE_LOG(LogGASToolsets, Log, TEXT("Attribute %s: Base=%f, Current=%f"), *Value.AttributeName, Value.BaseValue, Value.CurrentValue);
}

// 3. 列出所有以 “GameplayCue.Character” 开头的 GameplayCue
TArray<FString> CharacterCues = UGameplayCueToolset::ListCues(TEXT("GameplayCue.Character"));
```

## Demo 示例

一个最小的可编译示例，定义了用于测试的 AttributeSet 和 Actor。
*（基于测试用例简化）*

**MyGASTestClasses.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "AttributeSet.h"
#include "AbilitySystemComponent.h"
#include "AbilitySystemInterface.h"
#include "MyGASTestClasses.generated.h"

UCLASS()
class UMyTestAttributeSet : public UAttributeSet
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintReadOnly, Category = "Test")
    FGameplayAttributeData TestAttribute;
};

UCLASS()
class AMyTestGASActor : public AActor, public IAbilitySystemInterface
{
    GENERATED_BODY()
public:
    AMyTestGASActor();
    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<UAbilitySystemComponent> AbilitySystemComponent;

    UPROPERTY()
    TObjectPtr<UMyTestAttributeSet> TestAttributeSet;
};
```

**MyGASTestClasses.cpp**
```cpp
#include "MyGASTestClasses.h"

AMyTestGASActor::AMyTestGASActor()
{
    AbilitySystemComponent = CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("AbilitySystemComp"));
    TestAttributeSet = CreateDefaultSubobject<UMyTestAttributeSet>(TEXT("TestAttributeSet"));
}

UAbilitySystemComponent* AMyTestGASActor::GetAbilitySystemComponent() const
{
    return AbilitySystemComponent;
}
```

## 模块依赖

该插件本身模块依赖简单，但其功能强依赖于其他插件。

| 模块/插件 | 用途 |
|---|---|
| `GameplayAbilities` (插件) | 提供核心的 Gameplay Ability System 框架，是本插件操作的对象。 |
| `ToolsetRegistry` (插件) | 提供 `UToolsetDefinition` 基类，本插件的所有工具集都继承自它。 |

## 维护状态

### 近期更新

- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- 2026-04-17 `8c911af5` [Backout] - CL52878047
- 2026-04-17 `9404cd3e` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.

### 维护评价

- **创建时间**：2026年3月31日，是一个非常新的插件。
- **最近更新**：最近一次更新在2026年4月18日，距今很近，且更新内容与核心功能（工具集定义方式）相关，表明处于**活跃开发**阶段。
- **维护状态**：**活跃维护中**。作为 Epic Games 官方维护的实验性插件，其更新与 AI 助手等新功能的开发紧密相关。
- **已知限制**：
    1.  **实验性插件**：`IsExperimentalVersion=true`，API 和功能可能在未来版本中发生重大变化。
    2.  **默认禁用**：`EnabledByDefault=false`，需要在项目设置中手动启用。
    3.  **编辑器专用**：`EditorOnly=true`，无法在打包后的游戏中使用。
- **推荐使用**：如果你正在开发或使用与 AI 助手集成的编辑器工具，并且需要操作 GAS，那么这个插件是**推荐使用**的。对于普通的 GAS 游戏开发，此插件并非必需，其价值主要体现在编辑器扩展和自动化工具链中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GASToolsets)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GASToolsets/Source/GASToolsets/Private/Tests)