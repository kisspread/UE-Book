# Actor Modifier Core

> Use modifier objects on actors to apply a custom behavior

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（SVG 图标资源） |
| 模块 | `ActorModifierCore` (Runtime), `ActorModifierCoreBlueprint` (UncookedOnly), `ActorModifierCoreEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ActorModifierCore) | |

## 用途

ActorModifierCore 是 Unreal Engine 5 中的一个**可扩展的 Actor 修改器（Modifier）框架**，最初为 Motion Design（虚拟制作中的动态图形）场景设计。它提供了一种结构化的方式，将一系列"修改器"以**栈（Stack）**的形式附加到 Actor 上，按顺序执行自定义行为。

核心理念：**把 Actor 的变换、材质、几何体等修改操作抽象为可组合、可排序、可撤销的 Modifier 链**。每个 Modifier 是一个独立的逻辑单元，通过依赖关系和排序规则自动管理执行顺序。

该框架解决的关键问题：
- **行为组合**：多个修改器可以叠加在同一个 Actor 上，自动处理依赖和顺序
- **可撤销/可恢复**：每个 Modifier 保存前置状态（SavePreState），支持 Undo/Redo
- **按需执行**：只有标记为 Dirty 的 Modifier 才会重新执行，避免不必要的计算
- **蓝图支持**：可以通过蓝图创建自定义 Modifier，无需编写 C++
- **性能分析**：内置 Profiler 系统，可以测量每个 Modifier 的执行时间

## 使用场景

- 你在做 Motion Design / 动态图形，需要对大量 Actor 应用复杂变换链 → 用 ActorModifierCore 管理修改器栈
- 你需要一套可扩展的 Actor 行为系统，支持依赖排序、启用/禁用、Undo/Redo → 基于此框架构建自定义 Modifier
- 你需要在蓝图中创建可复用的 Actor 修改逻辑 → 用 Blueprint Modifier 资产
- 你需要对 Actor 修改操作做性能分析 → 使用内置 Profiler 系统

## 架构概览

```
UActorModifierCoreSubsystem (UEngineSubsystem)
├── 管理所有已注册的 Modifier 类元数据
├── 管理所有活跃的 Modifier Stack（按 Actor 索引）
└── 提供创建/查询/操作 Modifier 的 API

UActorModifierCoreComponent (UActorComponent)
└── 附加到 Actor 上，持有根 Stack

UActorModifierCoreStack (UActorModifierCoreBase)
├── 继承自 UActorModifierCoreBase（本身也是一个 Modifier）
├── 持有 TArray<UActorModifierCoreBase*> Modifiers
├── 支持嵌套 Stack
└── 管理执行任务（FActorModifierCoreExecutionTask）

UActorModifierCoreBase (UObject)
├── 所有 Modifier 的抽象基类
├── 生命周期：Initialize → SavePreState → Apply → RestorePreState
├── 支持 Extension 扩展机制
└── 支持 SharedObject 共享数据

UActorModifierCoreBlueprintBase (UActorModifierCoreBase)
└── 蓝图 Modifier 基类，暴露 BlueprintImplementableEvent
```

### 执行流程

1. **Dirty 标记**：Modifier 属性变更或外部调用 `MarkModifierDirty()`
2. **执行任务**：Stack 创建 `FActorModifierCoreExecutionTask`
3. **Restore 阶段**：从最后一个 Dirty Modifier 向前，逐个调用 `RestorePreState()` 恢复原始状态
4. **Apply 阶段**：从第一个 Dirty Modifier 向后，逐个调用 `SavePreState()` + `Apply()`
5. **完成**：调用 `Next()` 进入下一个 Modifier，或 `Fail()` 中断链

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindModifierStack` | 获取 Actor 的 Modifier Stack，可选自动创建 | `UActorModifierCoreLibrary` |
| `InsertModifier` | 向 Stack 中插入新 Modifier | `UActorModifierCoreLibrary` |
| `CloneModifier` | 克隆已有 Modifier 到 Stack | `UActorModifierCoreLibrary` |
| `MoveModifier` | 在 Stack 中移动 Modifier 位置 | `UActorModifierCoreLibrary` |
| `RemoveModifier` | 从 Stack 中移除 Modifier | `UActorModifierCoreLibrary` |
| `EnableModifier` | 启用/禁用 Modifier | `UActorModifierCoreLibrary` |
| `IsModifierEnabled` | 查询 Modifier 启用状态 | `UActorModifierCoreLibrary` |
| `GetModifierActor` | 获取 Modifier 修改的目标 Actor | `UActorModifierCoreLibrary` |
| `GetModifierName` | 获取 Modifier 名称 | `UActorModifierCoreLibrary` |
| `GetModifierCategory` | 获取 Modifier 分类 | `UActorModifierCoreLibrary` |
| `GetStackModifiers` | 获取 Stack 中所有 Modifier | `UActorModifierCoreLibrary` |
| `FindModifierByName` | 按名称查找 Modifier | `UActorModifierCoreLibrary` |
| `FindModifierByClass` | 按类查找 Modifier | `UActorModifierCoreLibrary` |
| `GetSupportedModifiers` | 获取 Actor 支持的 Modifier 类列表 | `UActorModifierCoreLibrary` |
| `GetAvailableModifiers` | 获取所有已注册的 Modifier 类 | `UActorModifierCoreLibrary` |
| `GetModifierStack` | 获取 Modifier 所在的 Stack | `UActorModifierCoreLibrary` |
| `GetDependentModifiers` | 获取依赖此 Modifier 的后续 Modifier | `UActorModifierCoreLibrary` |
| `GetRequiredModifiers` | 获取此 Modifier 依赖的前置 Modifier | `UActorModifierCoreLibrary` |
| `MarkModifierDirty` | 标记 Modifier 需要重新执行 | `UActorModifierCoreLibrary` |
| `GetModifierStack` (Component) | 从 Component 获取 Stack | `UActorModifierCoreComponent` |

### 蓝图 Modifier 事件

在 `UActorModifierCoreBlueprintBase` 中创建蓝图 Modifier 时，可以实现以下事件：

| 事件 | 说明 |
|---|---|
| `OnModifierSetupEvent` | 设置 Modifier 元数据（名称、分类、依赖等） |
| `OnModifierAddedEvent` | Modifier 被添加到 Stack 时调用 |
| `OnModifierRemovedEvent` | Modifier 从 Stack 移除时调用 |
| `OnModifierEnabledEvent` | Modifier 启用时调用 |
| `OnModifierDisabledEvent` | Modifier 禁用时调用 |
| `OnModifierSaveStateEvent` | Apply 前保存状态 |
| `OnModifierRestoreStateEvent` | 恢复之前保存的状态 |
| `OnModifierApplyEvent` | 执行 Modifier 的核心逻辑 |
| `OnModifierReplacedEvent` | 蓝图重编译后 Modifier 被替换时调用 |
| `FlagModifierDirty` | 蓝图可调用，标记 Modifier 需要更新 |

### 使用示例（蓝图描述）

**获取并操作 Actor 的 Modifier Stack：**

1. 获取一个 Actor 的引用
2. 调用 `FindModifierStack`，传入 Actor，勾选 `bInCreateIfNone = true`
3. 调用 `InsertModifier`，传入 Stack 和 `FActorModifierCoreInsertOperation`（指定 ModifierClass 和位置）
4. 新 Modifier 会自动按依赖顺序插入并执行

**创建蓝图自定义 Modifier：**

1. 右键 Content Browser → 创建 `ActorModifierCoreBlueprint` 资产
2. 打开蓝图，实现 `OnModifierSetupEvent` 设置元数据
3. 实现 `OnModifierSaveStateEvent` 保存需要的原始状态
4. 实现 `OnModifierApplyEvent` 编写修改逻辑
5. 实现 `OnModifierRestoreStateEvent` 恢复原始状态

## C++ 用法

### 头文件引入

```cpp
#include "Modifiers/ActorModifierCoreBase.h"       // Modifier 基类
#include "Modifiers/ActorModifierCoreStack.h"       // Modifier Stack
#include "Modifiers/ActorModifierCoreComponent.h"   // Actor 组件
#include "Modifiers/ActorModifierCoreDefs.h"         // 定义和元数据
#include "Subsystems/ActorModifierCoreSubsystem.h"  // 子系统
```

### 创建自定义 C++ Modifier

继承 `UActorModifierCoreBase` 并实现虚函数：

```cpp
// MyModifier.h
#pragma once
#include "Modifiers/ActorModifierCoreBase.h"
#include "MyModifier.generated.h"

UCLASS()
class UMyModifier : public UActorModifierCoreBase
{
    GENERATED_BODY()

protected:
    // 设置 Modifier 元数据（名称、分类、依赖等）
    virtual void OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata) override
    {
        InMetadata.SetName(TEXT("MyModifier"))
                  .SetCategory(TEXT("Custom"))
                  .AllowMultiple(false)
                  .AddDependency(TEXT("SomeOtherModifier")); // 可选：声明依赖
    }

    // 保存原始状态
    virtual void SavePreState() override
    {
        // 保存 Actor 当前状态
    }

    // 执行修改逻辑
    virtual void Apply() override
    {
        // 应用修改
        // 完成后必须调用 Next() 或 Fail()
        Next();
    }

    // 恢复原始状态
    virtual void RestorePreState() override
    {
        // 恢复之前保存的状态
    }

    // Modifier 被添加时
    virtual void OnModifierAdded(EActorModifierCoreEnableReason InReason) override
    {
        // 初始化逻辑
    }

    // Modifier 被移除时
    virtual void OnModifierRemoved(EActorModifierCoreDisableReason InReason) override
    {
        // 清理逻辑
    }
};
```

### 通过 Subsystem 操作 Modifier Stack

```cpp
#include "Subsystems/ActorModifierCoreSubsystem.h"

// 获取 Subsystem
UActorModifierCoreSubsystem* Subsystem = UActorModifierCoreSubsystem::Get();

// 获取 Actor 的 Modifier Stack
UActorModifierCoreStack* Stack = Subsystem->GetActorModifierStack(MyActor);

// 如果没有 Stack，自动创建
if (!Stack)
{
    Stack = Subsystem->AddActorModifierStack(MyActor);
}

// 查找特定 Modifier
UActorModifierCoreBase* FoundMod = Stack->FindModifier(FName("MyModifier"));

// 使用模板查找
UMyModifier* MyMod = Stack->GetClassModifier<UMyModifier>();
```

### 使用 Extension 扩展 Modifier

```cpp
// 自定义 Extension
class FMyExtension : public FActorModifierCoreExtension
{
protected:
    virtual void OnExtensionInitialized() override { /* 初始化 */ }
    virtual void OnExtensionEnabled(EActorModifierCoreEnableReason InReason) override { /* 启用 */ }
};

// 在 Modifier 中添加 Extension
FMyExtension* Ext = AddExtension<FMyExtension>();

// 查询 Extension
FMyExtension* FoundExt = GetExtension<FMyExtension>();

// 处理 Extension（如果存在）
ProcessExtension<FMyExtension>([](FMyExtension* Ext) {
    // 使用 Extension
});
```

### 使用 SharedObject 跨 Modifier 共享数据

```cpp
// 定义共享数据类
UCLASS()
class UMySharedData : public UActorModifierCoreSharedObject
{
    GENERATED_BODY()
public:
    // 共享数据成员
    TArray<FVector> CachedPositions;
};

// 在 Modifier 中获取共享数据
UMySharedData* Shared = GetShared<UMySharedData>(true); // true = 不存在时创建
if (Shared)
{
    // 读写共享数据
    Shared->CachedPositions.Add(FVector::ZeroVector);
}
```

### 使用 ForEachComponent / ForEachActor 遍历

```cpp
// 遍历 Actor 的所有 StaticMeshComponent
ForEachComponent<UStaticMeshComponent>([](UStaticMeshComponent* Comp) -> bool
{
    // 处理组件
    return true; // 返回 false 停止遍历
}, EActorModifierCoreComponentType::Owned);

// 遍历子 Actor
ForEachActor<AStaticMeshActor>([](AStaticMeshActor* ChildActor) -> bool
{
    // 处理子 Actor
    return true;
}, EActorModifierCoreLookup::DirectChildren);
```

## Demo 示例

### 最小自定义 Modifier（完整可编译）

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "ActorModifierCore"
});
```

**SimpleScaleModifier.h：**

```cpp
#pragma once
#include "Modifiers/ActorModifierCoreBase.h"
#include "SimpleScaleModifier.generated.h"

UCLASS()
class USimpleScaleModifier : public UActorModifierCoreBase
{
    GENERATED_BODY()

protected:
    virtual void OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata) override
    {
        InMetadata.SetName(TEXT("SimpleScale"))
                  .SetCategory(FActorModifierCoreMetadata::DefaultCategory)
                  .AllowMultiple(false);
    }

    virtual void SavePreState() override
    {
        if (AActor* Actor = GetModifiedActor())
        {
            SavedScale = Actor->GetActorScale3D();
        }
    }

    virtual void Apply() override
    {
        if (AActor* Actor = GetModifiedActor())
        {
            Actor->SetActorScale3D(SavedScale * ScaleMultiplier);
            Next();
        }
        else
        {
            Fail(FText::FromString(TEXT("No valid actor")));
        }
    }

    virtual void RestorePreState() override
    {
        if (AActor* Actor = GetModifiedActor())
        {
            Actor->SetActorScale3D(SavedScale);
        }
    }

private:
    FVector SavedScale = FVector::OneVector;

    UPROPERTY(EditAnywhere, Category="Modifier")
    float ScaleMultiplier = 2.0f;
};
```

**使用方式：**

```cpp
// 通过 Subsystem 添加 Modifier 到 Actor
UActorModifierCoreSubsystem* Sub = UActorModifierCoreSubsystem::Get();
UActorModifierCoreStack* Stack = Sub->AddActorModifierStack(MyActor);

FActorModifierCoreStackInsertOp InsertOp;
InsertOp.NewModifierName = FName("SimpleScale");
Sub->InsertModifier(Stack, InsertOp);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、数学库 |
| `CoreUObject` | UObject 系统、反射、序列化 |
| `Engine` | Actor、Component、World 等核心引擎类 |
| `Slate` / `SlateCore` | UI 框架（Editor 模块使用） |
| `TraceLog` | 性能追踪日志 |
| `BlueprintGraph` | 蓝图节点图支持（Blueprint 模块） |
| `OperatorStackEditor` | 操作栈编辑器 UI（Editor 模块） |
| `PropertyEditor` | 属性面板自定义（Editor 模块） |
| `UnrealEd` | 编辑器工具（Editor 模块） |
| `ToolMenus` | 工具菜单系统（Editor 模块） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-03 | `3279a835` | 新增蓝图中标记 Modifier 为 Dirty 的能力 |
| 2025-09-29 | `d30bd8c8` | 材质参数和全局透明度 Modifier 改用结构体数组存储，兼容 Remote Control |
| 2025-09-23 | `e17a6bba` | 修复默认 Modifier 名称使用类名替代 None；Taper Modifier 移除/废弃无用的 Resolution 属性 |

### 维护评价

- **创建时间**：2024-01-28（最初在 Experimental 目录），2025-05-08 迁移到 VirtualProduction
- **最近更新频率**：2025 年 9-10 月有持续更新，处于**活跃维护**状态
- **维护团队**：Epic Games Motion Design 团队
- **平台支持**：Win64、Linux、Mac
- **依赖插件**：OperatorStack（必须启用）
- **推荐程度**：✅ 推荐使用，这是 Epic 官方维护的虚拟制作 Modifier 框架，持续有功能更新和 bug 修复

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ActorModifierCore)
