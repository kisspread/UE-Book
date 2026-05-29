# Actor Modifier Core

> Use modifier objects on actors to apply a custom behavior（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Actor 修改器核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ActorModifierCore` (Runtime), `ActorModifierCoreBlueprint` (UncookedOnly), `ActorModifierCoreEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifierCore) | |

## 用途

ActorModifierCore 是一个**可扩展的 Actor 修改器堆栈系统**，为虚拟制片（Motion Design）工作流提供核心框架。它允许你在任意 Actor 上挂载一个**修改器堆栈（Modifier Stack）**，堆栈中可以按顺序排列多个修改器（Modifier），每个修改器对 Actor 执行自定义行为。

这个插件解决的核心问题是：**如何在不修改 Actor 本身逻辑的情况下，以可组合、可排序、可撤销的方式为 Actor 附加复杂的行为链**。类似材质编辑器中的材质表达式节点链，每个节点对结果进行增量修改。

**核心设计思想：**
- 修改器按**堆栈顺序**执行，后一个修改器依赖前一个修改器的输出
- 支持**脏标记（Dirty）机制**，仅重新执行需要更新的修改器
- 支持**状态保存与恢复**（SavePreState / RestorePreState），实现撤销/冻结
- 修改器之间有**依赖、排斥、顺序约束**等元数据规则
- 同时支持 C++ 和蓝图两种扩展方式

它是 Motion Design 插件族的基础设施之一，从 Engine/Plugins/Experimental 迁移至 VirtualProduction。

## 使用场景

- 你在做虚拟制片/Motion Design 工作流 → 需要对 Actor 施加一系列可组合的效果链（如 ClonerEffector、PropertyAnimator 等都基于此框架）
- 你需要为 Actor 添加可撤销、可重排序的行为序列 → 用修改器堆栈
- 你需要创建自定义修改器（C++ 或蓝图）并注册到全局系统 → 继承 `UActorModifierCoreBase` 或 `UActorModifierCoreBlueprintBase`
- 你需要在蓝图中动态操作修改器的增删改查 → 用 `UActorModifierCoreLibrary` 提供的蓝图节点

## 蓝图用法

`UActorModifierCoreLibrary`（显示名 "Motion Design Modifier Library"）提供了完整的蓝图 CRUD 操作节点，分类在 `Motion Design|Modifiers|Utility` 下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindModifierStack` | 获取 Actor 的修改器堆栈，不存在时可选创建 | `UActorModifierCoreLibrary` |
| `InsertModifier` | 在堆栈中插入一个新的修改器 | `UActorModifierCoreLibrary` |
| `CloneModifier` | 克隆一个已有修改器到堆栈中 | `UActorModifierCoreLibrary` |
| `MoveModifier` | 在堆栈中移动一个修改器的位置 | `UActorModifierCoreLibrary` |
| `RemoveModifier` | 从堆栈中移除一个修改器 | `UActorModifierCoreLibrary` |
| `EnableModifier` | 启用/禁用一个修改器 | `UActorModifierCoreLibrary` |
| `IsModifierEnabled` | 查询修改器是否启用 | `UActorModifierCoreLibrary` |
| `MarkModifierDirty` | 将修改器标记为脏，触发重新执行 | `UActorModifierCoreLibrary` |
| `FindModifierByClass` | 按类查找堆栈中的第一个修改器 | `UActorModifierCoreLibrary` |
| `FindModifierByName` | 按名称查找堆栈中的第一个修改器 | `UActorModifierCoreLibrary` |
| `FindModifiersByClass` | 按类查找堆栈中所有匹配的修改器 | `UActorModifierCoreLibrary` |
| `FindModifiersByName` | 按名称查找堆栈中所有匹配的修改器 | `UActorModifierCoreLibrary` |
| `ContainsModifier` | 检查堆栈是否包含指定修改器 | `UActorModifierCoreLibrary` |
| `GetStackModifiers` | 获取堆栈中的所有修改器 | `UActorModifierCoreLibrary` |
| `GetDependentModifiers` | 获取依赖于指定修改器的后续修改器 | `UActorModifierCoreLibrary` |
| `GetRequiredModifiers` | 获取指定修改器依赖的前置修改器 | `UActorModifierCoreLibrary` |
| `GetSupportedModifiers` | 获取 Actor 支持的所有修改器类 | `UActorModifierCoreLibrary` |
| `GetAvailableModifiers` | 获取全局注册的所有可用修改器类 | `UActorModifierCoreLibrary` |
| `GetModifierActor` | 获取修改器作用的目标 Actor | `UActorModifierCoreLibrary` |
| `GetModifierStack` | 获取修改器所在的堆栈 | `UActorModifierCoreLibrary` |
| `GetModifierName` / `GetModifierCategory` | 获取修改器名称/分类 | `UActorModifierCoreLibrary` |
| `GetModifierCategories` | 获取所有已注册的修改器分类 | `UActorModifierCoreLibrary` |
| `GetModifiersByCategory` | 按分类获取修改器类 | `UActorModifierCoreLibrary` |
| `GetModifierClass` | 按名称获取修改器类 | `UActorModifierCoreLibrary` |

### 元数据设置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetModifierMetadataName` | 设置修改器元数据名称 | `UActorModifierCoreLibrary` |
| `SetModifierMetadataCategory` | 设置修改器元数据分类 | `UActorModifierCoreLibrary` |
| `SetModifierMetadataDisplayName` | 设置编辑器显示名称 | `UActorModifierCoreLibrary` |
| `SetModifierMetadataDescription` | 设置修改器描述 | `UActorModifierCoreLibrary` |
| `SetModifierMetadataColor` | 设置修改器颜色 | `UActorModifierCoreLibrary` |
| `AddModifierMetadataDependency` | 添加修改器依赖 | `UActorModifierCoreLibrary` |
| `SetModifierMetadataCompatibilityRule` | 设置兼容性规则委托 | `UActorModifierCoreLibrary` |

### 使用示例（蓝图描述）

**为 Actor 添加修改器：**
1. 从目标 Actor 开始，调用 `FindModifierStack`（bCreateIfNone=true）获取或创建堆栈
2. 填充 `FActorModifierCoreInsertOperation` 结构体（设置 ModifierClass、InsertPosition、InsertPositionContext）
3. 调用 `InsertModifier`，传入堆栈和操作数据，输出新创建的修改器

**查找并操作已有修改器：**
1. 调用 `GetStackModifiers` 获取堆栈中所有修改器
2. 用 `FindModifierByClass` 或 `FindModifierByName` 定位目标修改器
3. 调用 `EnableModifier` 启用/禁用，或 `MarkModifierDirty` 触发更新

**创建蓝图修改器：**
1. 创建一个继承 `UActorModifierCoreBlueprintBase` 的蓝图类
2. 实现 `OnModifierSetupEvent` 设置元数据（名称、分类、依赖等）
3. 实现 `OnModifierApplyEvent` 定义实际的修改逻辑
4. 实现 `OnModifierSaveStateEvent` 和 `OnModifierRestoreStateEvent` 处理状态保存/恢复
5. 实现 `OnModifierAddedEvent` / `OnModifierRemovedEvent` 处理生命周期回调

## C++ 用法

### 头文件引入

```cpp
#include "Modifiers/ActorModifierCoreBase.h"
#include "Modifiers/ActorModifierCoreStack.h"
#include "Modifiers/ActorModifierCoreDefs.h"
#include "Subsystems/ActorModifierCoreSubsystem.h"
```

### 基本用法

**创建自定义修改器（C++）：**

从头文件 `Public/Modifiers/ActorModifierCoreBase.h` 可以看到修改器的生命周期方法：

```cpp
// MyCustomModifier.h
#pragma once
#include "Modifiers/ActorModifierCoreBase.h"
#include "MyCustomModifier.generated.h"

UCLASS(MinimalAPI)
class UMyCustomModifier : public UActorModifierCoreBase
{
    GENERATED_BODY()

protected:
    // 重写 CDO 初始化，设置修改器元数据（名称、分类、依赖等）
    virtual void OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata) override;

    // 保存应用前的状态（用于撤销/恢复）
    virtual void SavePreState() override;

    // 恢复到应用前的状态
    virtual void RestorePreState() override;

    // 实际的应用逻辑，完成后必须调用 Next() 或 Fail()
    virtual void Apply() override;

    // 修改器被添加到堆栈时的回调
    virtual void OnModifierAdded(EActorModifierCoreEnableReason InReason) override;

    // 修改器被移除时的回调
    virtual void OnModifierRemoved(EActorModifierCoreDisableReason InReason) override;
};
```

```cpp
// MyCustomModifier.cpp
#include "MyCustomModifier.h"
#include "Modifiers/ActorModifierCoreDefs.h"

void UMyCustomModifier::OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata)
{
    // 设置唯一名称
    InMetadata.SetName(TEXT("MyCustomModifier"));
    // 设置分类
    InMetadata.SetCategory(FActorModifierCoreMetadata::DefaultCategory);
    // 允许在同一堆栈中多次使用
    InMetadata.AllowMultiple(true);
    // 添加前置依赖（此修改器需要在 "OtherModifier" 之后）
    InMetadata.AddDependency(TEXT("OtherModifier"));
}

void UMyCustomModifier::SavePreState()
{
    // 保存当前 Actor 的状态
    AActor* Actor = GetModifiedActor();
    // ... 保存需要恢复的数据
}

void UMyCustomModifier::RestorePreState()
{
    // 恢复 Actor 到修改前的状态
    AActor* Actor = GetModifiedActor();
    // ... 恢复之前保存的数据
}

void UMyCustomModifier::Apply()
{
    // 应用修改逻辑
    AActor* Actor = GetModifiedActor();
    if (Actor)
    {
        // ... 执行实际修改
        // 完成后调用 Next() 继续执行下一个修改器
        Next();
        // 或者失败时调用 Fail(InFailReason)
    }
}

void UMyCustomModifier::OnModifierAdded(EActorModifierCoreEnableReason InReason)
{
    // 修改器被添加到堆栈时初始化
    // InReason 可以是 User(用户添加) / Load(加载时) / Undo(撤销时) / Duplicate(复制时)
}

void UMyCustomModifier::OnModifierRemoved(EActorModifierCoreDisableReason InReason)
{
    // 修改器被移除时清理
}
```

**通过子系统操作修改器堆栈：**

参考 `Public/Subsystems/ActorModifierCoreSubsystem.h`：

```cpp
#include "Subsystems/ActorModifierCoreSubsystem.h"
#include "Modifiers/ActorModifierCoreDefs.h"

// 获取全局子系统
UActorModifierCoreSubsystem* Subsystem = UActorModifierCoreSubsystem::Get();

// 获取 Actor 的修改器堆栈（不存在则返回 nullptr）
UActorModifierCoreStack* Stack = Subsystem->GetActorModifierStack(MyActor);

// 为 Actor 添加修改器堆栈组件
UActorModifierCoreStack* NewStack = Subsystem->AddActorModifierStack(MyActor);

// 插入一个修改器
FActorModifierCoreStackInsertOp InsertOp;
InsertOp.NewModifierName = TEXT("MyCustomModifier");
InsertOp.InsertPosition = EActorModifierCoreStackPosition::Before;
InsertOp.InsertPositionContext = nullptr; // nullptr 表示堆栈末尾
UActorModifierCoreBase* NewModifier = Subsystem->InsertModifier(Stack, InsertOp);
```

### 进阶用法

**使用修改器扩展（Extension）复用逻辑：**

从 `Public/Modifiers/ActorModifierCoreExtension.h` 可以看到扩展机制：

```cpp
// 定义一个扩展，多个修改器可以复用同一段逻辑
class FMyTransformExtension : public FActorModifierCoreExtension
{
protected:
    virtual void OnExtensionInitialized() override
    {
        // 扩展初始化
    }

    virtual void OnExtensionEnabled(EActorModifierCoreEnableReason InReason) override
    {
        // 扩展被启用
    }

    virtual void OnExtensionDisabled(EActorModifierCoreDisableReason InReason) override
    {
        // 扩展被禁用
    }

public:
    // 自定义逻辑
    void DoTransformWork()
    {
        AActor* Actor = GetModifierActor();
        // ...
    }
};

// 在修改器中使用扩展
void UMyCustomModifier::Apply()
{
    // 添加或获取扩展（每个类型每修改器只有一个实例）
    FMyTransformExtension* Ext = AddExtension<FMyTransformExtension>();
    if (Ext)
    {
        Ext->DoTransformWork();
    }

    // 或者仅在存在时处理
    ProcessExtension<FMyTransformExtension>([](FMyTransformExtension* InExt)
    {
        InExt->DoTransformWork();
    });

    Next();
}
```

**使用共享对象（SharedObject）跨修改器共享数据：**

```cpp
// 从 ActorModifierCoreBase.h 的 GetShared 方法
// 获取同级别的共享对象，不存在时可选创建
UMySharedData* SharedData = GetShared<UMySharedData>(true);
if (SharedData)
{
    // 共享数据在同一 Level 的所有修改器之间共享
    SharedData->SomeSharedValue = 42;
}
```

**使用 ForEachComponent / ForEachActor 遍历辅助函数：**

```cpp
// 从 ActorModifierCoreBase.h 中的模板辅助方法

// 遍历修改 Actor 的所有 StaticMeshComponent
ForEachComponent<UStaticMeshComponent>([](UStaticMeshComponent* InComp) -> bool
{
    // 处理每个 StaticMeshComponent
    // 返回 true 继续，返回 false 停止遍历
    return true;
}, EActorModifierCoreComponentType::All); // Owned + Instanced

// 遍历 Actor 的所有子 Actor
ForEachActor<AStaticMeshActor>([](AStaticMeshActor* InChildActor) -> bool
{
    // 处理每个子 StaticMeshActor
    return true;
}, EActorModifierCoreLookup::AllChildren);
```

**使用 ScopedLock 防止执行：**

```cpp
// 从 ActorModifierCoreDefs.h
// 锁定修改器执行，生命周期结束后自动解锁
{
    FActorModifierCoreScopedLock Lock(MyModifier);
    // 在此范围内修改器不会被执行
    // ... 做一些临时修改
}
// 离开作用域后自动解锁并恢复执行
```

**获取渲染状态脏原因：**

```cpp
#include "Modifiers/ActorModifierRenderStateDirtyEvent.h"

// 使用作用域追踪渲染状态脏原因，避免不必要的计算
{
    UE::ActorModifierCore::FRenderStateDirtyReasonScope Scope(
        UE::ActorModifierCore::ERenderStateDirtyReason::Geometry);

    // 在此作用域内，可以通过 GetRenderStateDirtyReason() 获取原因
    if (UE::ActorModifierCore::IsRenderStateDirtyRelevant(
        UE::ActorModifierCore::ERenderStateDirtyReason::Material))
    {
        // 仅在材质变化时处理
    }
}
```

## Demo 示例

```cpp
// SimpleScaleModifier.h
#pragma once
#include "Modifiers/ActorModifierCoreBase.h"
#include "SimpleScaleModifier.generated.h"

UCLASS(MinimalAPI)
class USimpleScaleModifier : public UActorModifierCoreBase
{
    GENERATED_BODY()

public:
    USimpleScaleModifier();

protected:
    virtual void OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata) override;
    virtual void SavePreState() override;
    virtual void RestorePreState() override;
    virtual void Apply() override;

    UPROPERTY(EditInstanceOnly, Category="Scale")
    FVector ScaleMultiplier = FVector(2.0f, 2.0f, 2.0f);

private:
    FVector OriginalScale = FVector::OneVector;
};
```

```cpp
// SimpleScaleModifier.cpp
#include "SimpleScaleModifier.h"
#include "Modifiers/ActorModifierCoreDefs.h"

USimpleScaleModifier::USimpleScaleModifier()
{
    // 默认构造函数
}

void USimpleScaleModifier::OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata)
{
    InMetadata.SetName(TEXT("SimpleScale"));
    InMetadata.SetCategory(FActorModifierCoreMetadata::DefaultCategory);
    InMetadata.AllowMultiple(false);
}

void USimpleScaleModifier::SavePreState()
{
    if (AActor* Actor = GetModifiedActor())
    {
        OriginalScale = Actor->GetActorScale3D();
    }
}

void USimpleScaleModifier::RestorePreState()
{
    if (AActor* Actor = GetModifiedActor())
    {
        Actor->SetActorScale3D(OriginalScale);
    }
}

void USimpleScaleModifier::Apply()
{
    if (AActor* Actor = GetModifiedActor())
    {
        Actor->SetActorScale3D(OriginalScale * ScaleMultiplier);
        Next();
    }
    else
    {
        Fail(NSLOCTEXT("SimpleScale", "NoActor", "No valid actor found"));
    }
}
```

## 模块依赖

从 Build.cs 和 .uplugin 插件依赖分析：

| 模块 | 用途 |
|---|---|
| `OperatorStack` | 操作堆栈插件依赖，提供基础的堆栈操作框架 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。`.uplugin` 声明依赖 `OperatorStack` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2d1c7712` | Motion Design: fixed issue where duplicating actors with modifiers and deleting those new duplicates | 修复复制带修改器的 Actor 后删除副本导致的问题 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中可能导致输出乱码的问题 |
| 2026-04-14 | `abb26688` | Actor Modifiers: added experimental freeze modifier feature | 新增实验性"冻结修改器"功能 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移到 UE_LOGF |
| 2026-04-09 | `bdd66985` | Motion Design: made render state dirty reason optional + added some fixes to the text3d update causi | 渲染状态脏原因改为可选，修复 Text3D 更新相关问题 |

### 维护评价

**活跃维护**。该插件创建于 2025 年 5 月，虽然历史不长，但近期（2026年4-5月）有多次实质性功能更新和 bug 修复，包括新增"冻结修改器"实验性功能、枚举输出修复、复制 Actor 问题修复等。作为 Motion Design / Virtual Production 套件的核心基础设施，由 Epic Games 维护，预计会持续更新。

**注意事项：**
- 插件默认未启用（`Installed: false`），需要手动在插件管理器中启用
- "冻结修改器"（Freeze Stack）功能标记为实验性
- 蓝图修改器类（`UActorModifierCoreBlueprintBase`）仅在 UncookedOnly 模块中可用，打包后不可用
- 该插件从 Experimental 迁移而来，API 可能随版本演进

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifierCore)
- 官方文档（暂无）