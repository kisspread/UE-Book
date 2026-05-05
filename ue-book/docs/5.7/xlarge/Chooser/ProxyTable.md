# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Runtime), `ChooserUncooked` (Runtime), `ProxyTable` (Runtime), `ProxyTableEditor` (Runtime), `ProxyTableUncooked` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser) | |

## 用途

Chooser 插件提供了一套基于数据驱动的动态资产选择系统。其核心思想是通过“代理表”（Proxy Table）建立间接引用，将资产选择逻辑从硬编码中解耦。这使得开发者可以在不修改代码或蓝图逻辑的情况下，通过编辑数据表来动态改变运行时选择的资产（如动画蒙太奇、音效、材质等）。该插件主要解决动画系统中复杂、可配置的资产选择问题，是 Epic 为高级动画工作流提供的实验性工具。

## 使用场景

- 你的游戏需要根据角色状态（如装备、技能、Buff）动态选择不同的动画蒙太奇。
- 你希望美术或策划能够通过编辑数据表（而非修改蓝图）来调整动画播放逻辑。
- 你需要一个系统来管理大量动画资产的间接引用，避免在蓝图中直接硬引用资产路径。
- 你在构建一个需要高度可配置性的动画状态机或动画选择器。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Proxy Asset` | 根据上下文对象和代理资产，解析并返回最终的 UObject。 | `UProxyTableFunctionLibrary` |
| `Make Lookup Proxy` | 创建一个用于在 Chooser 表中查找代理资产的结构体。 | `UProxyTableFunctionLibrary` |
| `Make Lookup Proxy With Override Table` | 创建一个查找代理结构体，并允许覆盖默认的代理表。 | `UProxyTableFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **创建代理资产**：在内容浏览器中右键 -> Animation -> Proxy Asset，创建一个 `UProxyAsset`。在资产详情中设置其预期的输出类型（如 `UAnimMontage`）。
2.  **创建代理表**：创建一个 `UProxyTable` 资产。在代理表编辑器中，为上一步创建的 `ProxyAsset` 添加条目，并为其指定具体的资产（例如，一个具体的 `AnimMontage`）。
3.  **在蓝图中查询**：
    - 使用 `Make Lookup Proxy` 节点，传入你的 `ProxyAsset`，得到一个 `FInstancedStruct`。
    - 将这个结构体作为输入，连接到 Chooser 表的某个列（例如，一个 `FObjectChooserBase` 类型的列）。
    - 当 Chooser 表评估并选中该行时，系统会自动通过代理表解析出最终的资产。
4.  **直接查询（不经过 Chooser 表）**：使用 `Evaluate Proxy Asset` 节点，传入上下文对象（如角色）和 `ProxyAsset`，直接获取解析后的资产对象。

## C++ 用法

### 头文件引入

```cpp
#include "ProxyTable.h"
#include "ProxyAsset.h"
#include "LookupProxy.h"
```

### 基本用法

创建并使用代理资产和代理表进行资产查找。

```cpp
// 假设你已经有了一个 UProxyAsset* MyProxyAsset 和一个 UProxyTable* MyProxyTable
// 1. 创建一个查找代理结构体
FLookupProxy LookupProxy;
LookupProxy.Proxy = MyProxyAsset;
// 可以选择性地设置一个覆盖的代理表
// LookupProxy.ProxyTable = MakeInstancedStruct<FProxyTableContextProperty>(...);

// 2. 在 Chooser 评估上下文中使用它
FChooserEvaluationContext Context(/* ... */);
UObject* ResolvedObject = LookupProxy.ChooseObject(Context);

if (ResolvedObject)
{
    // 使用解析出的对象，例如 UAnimMontage
    UAnimMontage* Montage = Cast<UAnimMontage>(ResolvedObject);
    // ...
}
```

### 进阶用法

直接通过 `UProxyTable` 的 API 进行查找，适用于更底层的控制。

```cpp
// 通过 GUID 查找（GUID 通常在编辑器中由 ProxyAsset 生成）
FGuid ProxyGuid = MyProxyAsset->Guid;
FChooserEvaluationContext Context(/* ... */);

// 方法1：查找单个对象
UObject* SingleResult = MyProxyTable->FindProxyObject(ProxyGuid, Context);

// 方法2：迭代所有可能的结果（如果代理表条目本身也是一个 Chooser）
MyProxyTable->IterateProxyObjects(ProxyGuid, Context, [](UObject* Object) -> FObjectChooserBase::EIteratorStatus
{
    // 处理每个可能的对象
    UE_LOG(LogTemp, Log, TEXT("Found potential object: %s"), *GetNameSafe(Object));
    return FObjectChooserBase::EIteratorStatus::Continue;
});
```

## Demo 示例

以下示例展示了如何在 C++ 中创建一个简单的代理查找流程。

**MyAnimInstance.h**
```cpp
#pragma once
#include "Animation/AnimInstance.h"
#include "MyAnimInstance.generated.h"

class UProxyAsset;
class UProxyTable;

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    // 在蓝图或编辑器中设置的代理资产
    UPROPERTY(EditAnywhere, Category = "Animation")
    TObjectPtr<UProxyAsset> AttackMontageProxy;

    // 在蓝图或编辑器中设置的代理表
    UPROPERTY(EditAnywhere, Category = "Animation")
    TObjectPtr<UProxyTable> CharacterProxyTable;

    // 一个蓝图可调用的函数，用于播放通过代理解析出的攻击蒙太奇
    UFUNCTION(BlueprintCallable, Category = "Animation")
    void PlayAttackMontage();
};
```

**MyAnimInstance.cpp**
```cpp
#include "MyAnimInstance.h"
#include "ProxyAsset.h"
#include "ProxyTable.h"
#include "LookupProxy.h"
#include "ChooserEvaluationContext.h"

void UMyAnimInstance::PlayAttackMontage()
{
    if (!AttackMontageProxy || !CharacterProxyTable)
    {
        return;
    }

    // 构建评估上下文，通常需要传入拥有此动画实例的 Actor
    AActor* OwnerActor = GetOwningActor();
    FChooserEvaluationContext Context;
    Context.AddObjectParam(OwnerActor);

    // 方法一：使用 FLookupProxy 结构体（推荐，与 Chooser 表集成）
    FLookupProxy Lookup;
    Lookup.Proxy = AttackMontageProxy;
    // 如果需要覆盖默认表，可以设置 Lookup.ProxyTable
    UObject* ResolvedAsset = Lookup.ChooseObject(Context);

    // 方法二：直接通过代理表查找
    // UObject* ResolvedAsset = CharacterProxyTable->FindProxyObject(AttackMontageProxy->Guid, Context);

    if (UAnimMontage* Montage = Cast<UAnimMontage>(ResolvedAsset))
    {
        Montage_Play(Montage);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chooser` | Chooser 表的核心运行时逻辑，ProxyTable 模块依赖于它。 |
| `StructUtils` | 提供 `FInstancedStruct` 等工具，用于存储异构数据。 |
| `GameplayTags` | 用于基于标签的条件判断和数据绑定。 |

## 维护状态

### 近期更新

- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- ca504591958a UE: Lower verbosity to display for now
- 7788ae1f8a8e Fix crash with Proxy table compilation

### 维护评价

Chooser 插件创建于 2022 年，相对年轻。从最近的提交记录看，它仍在被维护，近期修复了编译崩溃问题并进行了代码清理。然而，该插件在 .uplugin 中明确标记为 **Experimental**（实验性），且默认未启用。这意味着其 API 和功能在未来版本中可能发生重大变更，不建议在生产环境中作为核心依赖使用。它更适合作为高级动画工作流的探索性工具或在内部项目中谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser)