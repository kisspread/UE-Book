# Targeting System

> Generic targeting system for use with gameplay abilities, aim assist, etc

| 属性 | 值 |
|---|---|
| 中文名 | 瞄准系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TargetingSystem` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-01-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayTargetingSystem) | |

## 用途

TargetingSystem 是一个通用的运行时瞄准系统框架。它解决的核心问题是为游戏玩法提供灵活、可扩展、可异步的目标选择和处理能力。这个系统不仅仅用于“瞄准”或“射击”这些狭义的场景，而是抽象为一套“选择、过滤、排序目标”的通用任务流水线。

开发者可以通过定义一系列“瞄准任务”（Targeting Task）来构建复杂的瞄准逻辑，这些任务可以按顺序执行，共同处理一个瞄准请求。系统支持同步执行和异步执行两种模式，非常适合集成到 Gameplay Ability System 或任何需要动态目标管理的系统中。它的存在是为了将复杂的瞄准逻辑（如射线检测、AOE、过滤、排序）从业务代码中解耦出来，使其可配置、可复用。

## 使用场景

- 你需要为一个 MOBA 游戏的技能（如指向性技能、范围技能）实现灵活的瞄准逻辑。
- 你想为一个射击游戏实现复杂的瞄准辅助系统，需要根据距离、角度、障碍物等条件动态筛选最佳目标。
- 你正在开发一个 RPG 游戏，需要一个通用的系统来处理法术的施法目标选择。
- 你需要处理复杂的、需要跨帧执行的异步瞄准请求（例如，长时间的充能瞄准或等待物理模拟结果）。
- 你想让策划能够通过数据资产（`UTargetingPreset`）来配置和调整瞄准行为，而无需修改代码。

## 蓝图用法

系统主要通过 `UTargetingSubsystem` 子系统暴露蓝图接口，并使用 `UTargetingPreset` 数据资产来定义瞄准任务。

### 核心节点

**瞄准请求**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute Targeting Request` | 根据预设和源上下文立即执行一次瞄准请求。完成后触发委托。 | `UTargetingSubsystem` |
| `Start Async Targeting Request` | 根据预设和源上下文发起一个异步瞄准请求。返回瞄准句柄，完成后触发委托。 | `UTargetingSubsystem` |
| `Remove Async Targeting Request With Handle` | 通过句柄移除一个正在排队的异步瞄准请求。 | `UTargetingSubsystem` |
| `Perform Targeting Async Action` | 蓝图异步操作节点，用于执行瞄准请求。 | `UAsyncAction_PerformTargeting` |
| `Perform Filtering Async Action` | 蓝图异步操作节点，用于执行目标过滤请求（预填充目标）。 | `UAsyncAction_PerformTargeting` |

**结果获取**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Targeting Results Actors` | 从瞄准句柄中获取命中的 Actor 数组。 | `UTargetingSubsystem` |
| `Get Targeting Results` | 从瞄准句柄中获取命中的 HitResult 数组。 | `UTargetingSubsystem` |
| `Get Targeting Source Context` | 获取指定瞄准句柄的源上下文信息。 | `UTargetingSubsystem` |

**配置与数据**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Override Collision Query Task Data` | 静态方法，用于覆盖指定瞄准句柄的碰撞查询数据（如添加忽略的 Actor）。 | `UTargetingSubsystem` |

### 使用示例（蓝图描述）

**基本瞄准请求（蓝图）**
1. 获取 `Targeting Subsystem`。
2. 创建一个 `TargetingPreset` 数据资产，在编辑器中配置好一系列瞄准任务（如射线检测、过滤、排序）。
3. 构建一个 `TargetingSourceContext` 结构体，设置 `SourceActor`（例如玩家角色）。
4. 调用 `Execute Targeting Request` 或 `Start Async Targeting Request`，传入预设和上下文。
5. 绑定完成委托，在委托中通过 `Get Targeting Results Actors` 获取命中的敌人列表并进行处理。

**自定义蓝图任务**
1. 创建一个继承自 `USimpleTargetingSelectionTask` 的蓝图类。
2. 重写 `SelectTargets` 事件，在其中使用 `Add Hit Result` 或 `Add Target Actor` 节点来添加你自定义逻辑选择的目标。
3. 创建一个继承自 `USimpleTargetingFilterTask` 的蓝图类。
4. 重写 `Should Remove Target` 事件，返回 `true` 表示应移除该目标。
5. 将这些自定义任务添加到你的 `TargetingPreset` 的任务列表中。

## C++ 用法

系统在 C++ 层面提供了更高的灵活性和性能，核心类是 `UTargetingSubsystem` 和 `UTargetingTask` 的子类。

### 头文件引入

```cpp
#include "TargetingSystem/TargetingSubsystem.h"
#include "TargetingSystem/TargetingPreset.h"
#include "Types/TargetingSystemTypes.h"
```

### 基本用法

通过子系统发起一次立即的瞄准请求。

```cpp
// 假设在某个 Actor 或 Component 中
UTargetingSubsystem* TargetingSubsystem = UTargetingSubsystem::Get(GetWorld());
if (TargetingSubsystem)
{
    // 1. 创建源上下文
    FTargetingSourceContext SourceContext;
    SourceContext.SourceActor = GetOwner();
    SourceContext.InstigatorActor = GetOwner();
    SourceContext.SourceLocation = GetActorLocation();

    // 2. 准备瞄准预设 (UTargetingPreset*)
    const UTargetingPreset* MyTargetingPreset = /* ... */;

    // 3. 发起立即瞄准请求
    TargetingSubsystem->ExecuteTargetingRequest(MyTargetingPreset, SourceContext,
        FTargetingRequestDynamicDelegate::CreateUObject(this, &ThisClass::OnTargetingRequestComplete));
}

// 回调函数
void AMyActor::OnTargetingRequestComplete(FTargetingRequestHandle TargetingRequestHandle)
{
    if (TargetingRequestHandle.IsValid())
    {
        TArray<AActor*> TargetActors;
        UTargetingSubsystem::Get(GetWorld())->GetTargetingResultsActors(TargetingRequestHandle, TargetActors);
        
        // 对目标进行处理...
    }
}
```

### 进阶用法

手动控制瞄准句柄和数据存储，实现更精细的控制。

```cpp
// 创建一个基础的瞄准句柄
FTargetingRequestHandle Handle = UTargetingSubsystem::CreateTargetRequestHandle();

// 手动设置必需的数据存储
// 1. 设置任务集 (可以来自预设或手动构建)
const FTargetingTaskSet* TaskSet = MyTargetingPreset->GetTargetingTaskSet();
FTargetingTaskSet::FindOrAdd(Handle) = TaskSet;

// 2. 设置源上下文
FTargetingSourceContext& Context = FTargetingSourceContext::FindOrAdd(Handle);
Context.SourceActor = MyActor;

// 3. (可选) 设置请求数据 (用于回调)
FTargetingRequestData& RequestData = FTargetingRequestData::FindOrAdd(Handle);
RequestData.TargetingRequestDelegate.BindLambda([](FTargetingRequestHandle CompletedHandle){
    // 立即请求完成的回调
});

// (可选) 设置自定义碰撞覆盖数据
FCollisionQueryTaskData& CollisionData = FCollisionQueryTaskData::FindOrAdd(Handle);
CollisionData.IgnoredActors.Add(IgnoreThisActor);

// 4. 执行请求 (可以是立即或异步)
UTargetingSubsystem* Subsystem = UTargetingSubsystem::Get(MyWorld);
Subsystem->ExecuteTargetingRequestWithHandle(Handle, CompletionDelegate);
// 或者
// Subsystem->StartAsyncTargetingRequestWithHandle(Handle, CompletionDelegate);

// 5. 请求完成后，务必释放句柄以清理所有关联的数据存储
UTargetingSubsystem::ReleaseTargetRequestHandle(Handle);
```

**创建自定义任务 (C++)**
继承 `UTargetingTask` 并重写 `Execute` 函数。

```cpp
// MyCustomTargetingTask.h
UCLASS(Blueprintable, EditInlineNew)
class UMyCustomTargetingTask : public UTargetingTask
{
    GENERATED_BODY()
public:
    virtual void Execute(const FTargetingRequestHandle& TargetingHandle) const override;
    // ... 其他属性和方法
};
```

## Demo 示例

一个最小的可运行示例，演示如何从 C++ 代码中执行一次瞄准请求。

```cpp
// MyTargetingComponent.h
UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyTargetingComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Targeting")
    TObjectPtr<const UTargetingPreset> MyPreset;

    UFUNCTION(BlueprintCallable)
    void PerformImmediateTargeting();

private:
    void OnTargetingComplete(FTargetingRequestHandle Handle);
};

// MyTargetingComponent.cpp
#include "TargetingSystem/TargetingSubsystem.h"
#include "TargetingSystem/TargetingPreset.h"

void UMyTargetingComponent::PerformImmediateTargeting()
{
    if (!MyPreset || !GetOwner()) return;

    UTargetingSubsystem* Subsystem = UTargetingSubsystem::Get(GetWorld());
    if (!Subsystem) return;

    FTargetingSourceContext Context;
    Context.SourceActor = GetOwner();
    Context.InstigatorActor = GetOwner();
    Context.SourceLocation = GetOwner()->GetActorLocation();

    Subsystem->ExecuteTargetingRequest(MyPreset, Context,
        FTargetingRequestDynamicDelegate::CreateUObject(this, &UMyTargetingComponent::OnTargetingComplete));
}

void UMyTargetingComponent::OnTargetingComplete(FTargetingRequestHandle Handle)
{
    UTargetingSubsystem* Subsystem = UTargetingSubsystem::Get(GetWorld());
    if (Subsystem && Handle.IsValid())
    {
        TArray<AActor*> Targets;
        Subsystem->GetTargetingResultsActors(Handle, Targets);
        
        for (AActor* Target : Targets)
        {
            UE_LOG(LogTemp, Log, TEXT("Target Found: %s"), *Target->GetName());
            // 处理每个目标...
        }
    }
    // Handle 会在子系统内部根据设置自动释放，或需手动管理
}
```

## 模块依赖

此插件依赖 Gameplay Abilities 插件。你的模块需要在 `Build.cs` 中添加以下依赖。

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 提供 `UAbilityTask_PerformTargeting` 的基类 `UAbilityTask`，以及与技能系统集成的能力 |
| `GameplayTargetingSystem` | 目标系统核心模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-20 | `992fad6c` | Gameplay systems deprecation removal pass for 5.4 and earlier, I skipped anything that was still in | 对5.4及更早版本的 gameplay 系统进行了过时代码清理，跳过了仍在使用的内容。 |
| 2026-01-26 | `df61996e` | Fixup API errors | 修复了 API 错误。 |
| 2026-01-14 | `6904f27a` | Expose some targeting system enum, functions and type | 暴露了一些瞄准系统的枚举、函数和类型，增强了可访问性。 |
| 2025-07-18 | `462ec4ed` | Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created and sub | 修复了关于三元运算符可能导致临时对象创建的编译器警告。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为具有对应 .gen.cpp 文件的源文件添加了内联宏，应用于包括此插件在内的多个模块。 |

### 维护评价

TargetingSystem 是一个相对较新（约1年）的插件，并且 **仍在积极维护**。从提交历史看，Epic 在持续进行 API 优化（如暴露更多类型）、错误修复和代码清理（移除过时部分）。该插件目前标记为 `IsBetaVersion=true`（在 .uplugin 中为 `IsExperimentalVersion: true`，但用户提供的信息中 `IsBetaVersion: true`，此处根据模板应输出 `⚠️ 是`）和 `EnabledByDefault=false`，表明它仍处于实验性阶段，API 和功能可能在未来发生变化。

**使用建议**：该系统设计良好，功能强大，非常适合需要复杂瞄准逻辑的新项目。由于其处于 Beta 阶段，建议在生产环境中使用时，密切关注版本更新，并做好适配准备。对于不需要如此高灵活性的简单瞄准需求，直接使用传统的射线检测或重叠检测可能更简单直接。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayTargetingSystem)
- 官方文档：无（插件无 DocsURL）
- 测试用例：未在分析文件中找到独立的测试用例。