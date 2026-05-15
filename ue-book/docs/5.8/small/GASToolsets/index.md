# GASToolsets

> Toolsets for the Gameplay Ability System

| 属性 | 值 |
|---|---|
| 中文名 | GAS 工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GASToolsets` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GASToolsets) | |

## 用途

GASToolsets 是 Epic 为 **AI 助手（AI Assistant）** 集成所提供的 Gameplay Ability System 辅助工具插件。它将 GAS 的常见检查操作封装为 AI 可调用的工具函数（`meta = (AICallable)`），使 AI 助手能够：

1. **查询与管理 GameplayCue**：枚举项目中的 GameplayCue 标签、查找对应的 Notify 资产、在编辑器中预览执行 Cue、创建/删除 Cue 标签和 Notify 蓝图资产。
2. **检查 AbilitySystemComponent 运行时状态**：读取 Actor 上的所有属性值（基础值 + 当前值）、活跃的 GameplayEffect、已授予的 Ability、当前拥有的 GameplayTag。
3. **发现 AttributeSet 类**：枚举项目中所有 AttributeSet 子类（包括 C++ 原生类和蓝图子类）及其定义的属性。

本质上，这是 GAS 的 **AI 驱动调试/巡检工具包**，解决了 AI 助手无法直接"看到"游戏能力系统内部状态的问题。

## 使用场景

- 你正在使用 GAS 开发游戏，希望 AI 助手能帮你检查某个 Actor 的生命值、Buff 列表或已装备的技能 → 用 `AbilitySystemInspectorToolset`
- 你需要 AI 助手帮你排查"Cue 触发了但没有视觉效果"的问题 → 用 `GameplayCueToolset` 的 `FindCueTagsWithoutNotifies()` 找出缺失 Notify 的标签
- 你想让 AI 助手快速列出项目中所有 AttributeSet 类及其属性定义 → 用 `AttributeSetToolset`
- 你想让 AI 助手帮你新建一个 GameplayCueNotify 蓝图资产 → 用 `GameplayCueToolset` 的 `CreateCueNotifyAsset()`

## 蓝图用法

> **注意**：本插件的所有函数均使用 `meta = (AICallable)` 元数据标记，专门为 AI 助手调用设计，**未声明 `BlueprintCallable`**，因此不能直接作为蓝图节点使用。以下列出供 C++ 开发者和自定义工具集作者参考。

### GameplayCue 工具集 — `UGameplayCueToolset`

| 函数 | 说明 |
|---|---|
| `ListCues(ParentTag)` | 列出指定父标签下的所有 GameplayCue 标签，传空返回全部 |
| `GetCueInfo(CueTag)` | 查询单个 Cue 的 Notify 资产路径和类型（Static/Actor/None） |
| `ExecuteCueOnSelectedActor(CueTag, Magnitude, Location, Normal)` | 在编辑器选中的 Actor 上非复制执行 Cue，用于预览效果 |
| `FindCueNotifyAssets(ParentTag)` | 通过资产注册表查找项目中所有 GameplayCueNotify 资产 |
| `CreateCueNotifyAsset(CueTag, PackagePath, AssetName, bIsActor)` | 创建新的 GameplayCueNotify 蓝图资产（Static 或 Actor） |
| `AddCueTag(CueTag, Comment)` | 向项目添加一个新的 GameplayCue 标签 |
| `RemoveCueTag(CueTag)` | 从项目中移除一个 GameplayCue 标签 |
| `FindCueTagsWithoutNotifies()` | 找出所有没有对应 Notify 资产的 Cue 标签 |

### AbilitySystem 检查工具集 — `UAbilitySystemInspectorToolset`

| 函数 | 说明 |
|---|---|
| `GetAttributeValues(Actor)` | 获取 Actor 上 ASC 的所有属性基础值和当前值 |
| `GetActiveEffects(Actor)` | 获取 Actor 上当前活跃的所有 GameplayEffect（含层数、剩余时间、授予标签） |
| `GetGrantedAbilities(Actor)` | 获取 Actor 上已授予的所有 Ability（含等级、是否激活） |
| `GetActiveTags(Actor)` | 获取 Actor 上 ASC 当前拥有的所有 GameplayTag |

### AttributeSet 工具集 — `UAttributeSetToolset`

| 函数 | 说明 |
|---|---|
| `FindAttributeSetClasses()` | 枚举项目中所有 AttributeSet 子类（C++ 原生 + 蓝图），含各自定义的属性 |
| `ListAttributes(ClassName)` | 查询指定 AttributeSet 类定义的属性列表 |

### 核心数据结构

| 结构体 | 说明 | 所在工具集 |
|---|---|---|
| `FGameplayCueInfo` | 单个 Cue 的标签、Notify 资产路径、Notify 类型 | GameplayCue |
| `FGameplayCueNotifyInfo` | Notify 资产的标签、路径、名称、类型 | GameplayCue |
| `FRuntimeAttributeValue` | 属性名称、所属 AttributeSet、基础值、当前值 | AbilitySystemInspector |
| `FActiveEffectInfo` | 效果名称、层数、总时长、剩余时长、授予标签 | AbilitySystemInspector |
| `FGrantedAbilityInfo` | Ability 名称、等级、是否激活 | AbilitySystemInspector |
| `FGameplayAttributeInfo` | 属性名称、全名、所属 AttributeSet 类名 | AttributeSet |
| `FAttributeSetClassInfo` | AttributeSet 类名、资产路径、属性列表 | AttributeSet |

## C++ 用法

> 本插件的工具函数位于 Private 头文件中，不属于公开 API。以下用法供需要与 AI 助手系统集成或理解内部实现的开发者参考。

### 头文件引入

```cpp
// 模块接口
#include "GASToolsets.h"

// 工具集头文件（Private，非公开 API）
#include "GameplayCueToolset.h"
#include "AbilitySystemInspectorToolset.h"
#include "AttributeSetToolset.h"
```

### 基本用法

来自测试用例的 Actor 设置模式：

```cpp
// 来源: Source/GASToolsets/Private/Tests/AbilitySystemInspectorToolsetTest.h

// 创建一个带有 AbilitySystemComponent 的测试 Actor
UCLASS(Hidden, MinimalAPI)
class AGASToolsetsTestActor : public AActor, public IAbilitySystemInterface
{
    GENERATED_BODY()

public:
    AGASToolsetsTestActor()
    {
        AbilitySystemComponent =
            CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("AbilitySystemComponent"));
    }

    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override
    {
        return AbilitySystemComponent;
    }

    UPROPERTY()
    TObjectPtr<UAbilitySystemComponent> AbilitySystemComponent;
};
```

```cpp
// 来源: Source/GASToolsets/Private/Tests/AttributeSetToolsetTest.h

// 创建一个测试用 AttributeSet，定义 Health 和 MaxHealth 属性
UCLASS(Hidden, MinimalAPI)
class UGASToolsetsTestAttributeSet : public UAttributeSet
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadOnly, Category = "Attribute")
    FGameplayAttributeData Health;

    UPROPERTY(BlueprintReadOnly, Category = "Attribute")
    FGameplayAttributeData MaxHealth;
};
```

### 进阶用法 — 调用工具函数

```cpp
// 检查选中 Actor 的运行时属性
AActor* SelectedActor = /* ... */;
TArray<FRuntimeAttributeValue> AttrValues =
    UAbilitySystemInspectorToolset::GetAttributeValues(SelectedActor);

for (const FRuntimeAttributeValue& Attr : AttrValues)
{
    UE_LOG(LogGASToolsets, Log, TEXT("%s: Base=%.1f, Current=%.1f"),
        *Attr.FullName, Attr.BaseValue, Attr.CurrentValue);
}

// 查找项目中所有 Cue 标签，检查哪些缺少 Notify 资产
TArray<FString> OrphanCues = UGameplayCueToolset::FindCueTagsWithoutNotifies();
for (const FString& Tag : OrphanCues)
{
    UE_LOG(LogGASToolsets, Warning, TEXT("Cue tag '%s' has no GameplayCueNotify asset!"), *Tag);
}

// 枚举所有 AttributeSet 类及其属性
TArray<FAttributeSetClassInfo> AllSets = UAttributeSetToolset::FindAttributeSetClasses();
for (const FAttributeSetClassInfo& Set : AllSets)
{
    UE_LOG(LogGASToolsets, Log, TEXT("AttributeSet: %s (%d attributes)"),
        *Set.ClassName, Set.Attributes.Num());
}
```

## Demo 示例

一个可编译的最小示例，展示如何设置与 GASToolsets 测试相同的 Actor 环境：

```cpp
// MyGASTestActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AbilitySystemInterface.h"
#include "AbilitySystemComponent.h"
#include "MyGASTestActor.generated.h"

UCLASS()
class UMyTestAttributeSet : public UAttributeSet
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadOnly, Category = "Attribute")
    FGameplayAttributeData Health;

    UPROPERTY(BlueprintReadOnly, Category = "Attribute")
    FGameplayAttributeData MaxHealth;
};

UCLASS()
class AMyGASTestActor : public AActor, public IAbilitySystemInterface
{
    GENERATED_BODY()

public:
    AMyGASTestActor()
    {
        AbilitySystemComponent =
            CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("AbilitySystemComponent"));
        TestAttributeSet =
            CreateDefaultSubobject<UMyTestAttributeSet>(TEXT("TestAttributeSet"));
    }

    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override
    {
        return AbilitySystemComponent;
    }

private:
    UPROPERTY()
    TObjectPtr<UAbilitySystemComponent> AbilitySystemComponent;

    UPROPERTY()
    TObjectPtr<UMyTestAttributeSet> TestAttributeSet;
};
```

```cpp
// MyGASTestActor.cpp
#include "MyGASTestActor.h"
// 无需额外实现，构造函数中已完成所有子对象创建
```

将此 Actor 放入关卡后，AI 助手即可通过 GASToolsets 工具集检查其属性、效果、能力和标签。

## 模块依赖

Build.cs 中仅声明了 `Core` 依赖，但插件本身需要以下外部插件：

| 插件 | 用途 |
|---|---|
| `GameplayAbilities` | 提供 AbilitySystemComponent、AttributeSet、GameplayEffect 等核心 GAS 类 |
| `ToolsetRegistry` | 提供 `UToolsetDefinition` 基类和 AI 工具注册框架 |

无特殊模块依赖（仅标准 Core 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 更改了 UToolsetDefinition 识别工具函数的机制 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 回退了上一次提交的改动 |
| 2026-04-17 | `9404cd3e` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 首次尝试更改工具函数识别机制（后被回退） |
| 2026-04-01 | `27afb6e8` | [AI Assistant Toolsets] Move toolset tests under AI.Toolsets. | 将工具集测试用例迁移到 AI.Toolsets 目录下 |
| 2026-03-31 | `95b6ab9c` | [AI Assistant] Disable GAS toolset plugin by default. | 创建仅 4 天后即设为默认禁用 |

### 维护评价

⚠️ **实验性早期开发阶段，谨慎使用。**

- **创建时间**：2026-03-27，插件历史不足 1 个月
- **活跃度**：近 3 周内有 5 次提交，处于活跃迭代中
- **稳定性**：API 尚未稳定 — 最近的提交中出现了功能改动后回退（`9404cd3e` → `8c911af5` → `6471b168`），说明底层工具函数识别机制仍在调整
- **默认禁用**：创建仅 4 天后（03-31）就被设为 `EnabledByDefault: false`，表明 Epic 认为该插件尚未准备好面向所有用户
- **依赖关系**：依赖的 `ToolsetRegistry` 插件同样为实验性，整体工具链风险叠加
- **推荐**：仅建议关注 AI 助手集成的开发者试用，不建议在生产项目中依赖此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GASToolsets)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GASToolsets/Source/GASToolsets/Private/Tests)