# 目标选择系统

> Generic targeting system for use with gameplay abilities, aim assist, etc

| 属性 | 值 |
|---|---|
| 中文名 | 目标选择系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TargetingSystem` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayTargetingSystem) | |

---

## 用途

本插件提供了一套通用、可配置、可扩展的目标选择框架，用于游戏中的目标获取与过滤。它允许用户通过一组 **任务（Task）** 组合（选择、过滤、排序）来定义目标挑选逻辑，并以同步或异步的方式执行。

典型使用场景包括：

- **技能系统**：为 `GameplayAbility` 提供一个 `AbilityTask`，方便在技能前后进行目标选定（如范围打击、锁敌、穿透弹道）。
- **瞄准辅助**：获取准星附近/准直方向上的有效目标列表。
- **通用目标过滤**：从已有候选列表中按类、距离、队形等条件筛选。
- **AI 决策**：为 AI 行为树提供目标感知数据源。

系统核心设计思想：

- 以 `FTargetingRequestHandle`（唯一句柄）绑定请求生命周期和数据存储。
- 使用 `UTargetingPreset`（DataAsset）描述任务管线，便于设计师在编辑器中装配。
- 内置三种任务基类：**选择任务**（生成初始目标）、**过滤任务**（剔除不符合条件的目标）、**排序任务**（对结果重新排序）。
- 支持立即执行（同步）与异步回调两种模式，适用于帧数敏感场景。
- 深度集成 `GameplayAbilities` 插件，提供 `UAbilityTask_PerformTargeting` 作为技能中常用的入口。

---

## 使用场景

| 场景 | 说明 |
|---|---|
| 制作一个需要范围锁敌的主动技能 | 使用 `UTargetingSelectionTask_AOE` 选择圆形/矩形范围内的敌人，再配合 `UTargetingFilterTask_ActorClass` 筛选指定类，最后用 `UTargetingFilterTask_SortByDistance` 排序，由 `UAbilityTask_PerformTargeting` 驱动。 |
| 实现类似《CS:GO》的准星自动吸附 | 使用 `UTargetingSelectionTask_Trace` 进行 Line Trace 获取准星前方的所有碰撞对象，再通过 `USimpleTargetingFilterTask`（Blueprint 子类）自定义过滤逻辑（如仅玩家、非友军），最后按距离排序。 |
| 给 AI 一个“看到最近敌人”的能力 | 在 AI 控制器中调用 `UTargetingSubsystem` 的立即执行接口，传入包含 `UTargetingSelectionTask_SourceActor`（获取自身位置）、`UTargetingFilterTask_SortByDistance` 的预设。 |
| 异步加载大量目标数据 | 当目标数量大或碰撞检测耗时时，使用 `bAllowAsync=true` 或 `UAsyncAction_PerformTargeting` 将目标选择卸载到后台线程，避免卡帧。 |

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Perform Targeting Request` | 从 GameplayAbility 发起一次完整的目标选择请求，结果通过 `OnTargetReady` 返回句柄 | `UAbilityTask_PerformTargeting` |
| `Perform Filtering Request` | 从 GameplayAbility 发起一次**仅过滤**的请求，传入初始 `Actor` 数组，结果同样通过 `OnTargetReady` 返回 | `UAbilityTask_PerformTargeting` |
| `Perform Targeting Async Action` | 从任意 Actor 发起异步目标选择请求（非 Ability 专用），输出 `Targeted` 事件 | `UAsyncAction_PerformTargeting` |
| `Perform Filtering Async Action` | 从任意 Actor 发起异步过滤请求 | `UAsyncAction_PerformTargeting` |
| `Get Targeting Handle` | 获取当前异步动作的 `TargetingHandle`，用于后续查询结果数据 | `UAsyncAction_PerformTargeting` |
| `GetTargetingSubsystem` | 从 TargetingTask 中获取子系统引用（仅在任务类蓝图中可用） | `UTargetingTask` |

### 使用示例（蓝图描述）

**一、完整一次选择 + 过滤（在 GameplayAbility 蓝图内）**

1. 创建一个 `UTargetingPreset` 数据资产，配置任务链：
   - 添加 `UTargetingSelectionTask_AOE`，设置形状（如 Sphere）、半径、TraceChannel。
   - 添加 `UTargetingFilterTask_ActorClass`，设置 `RequiredActorClassFilters` 为 `BP_Enemy`。
   - 添加 `UTargetingFilterTask_SortByDistance`，勾选 `bAscending`。
2. 在 Ability 蓝图中拖入 `Perform Targeting Request` 节点，将上一步的 Preset 赋值给 `InTargetingPreset`，`bAllowAsync` 设为 `false`。
3. 从 `OnTargetReady` 引脚引出执行线，获取返回的 `TargetingRequestHandle`。
4. 使用 `TargetingSubsystem`（通过 `Get Targeting Subsystem` 节点）调用 `GetTargetingResultsActors` 得到最终 `Actor` 数组。

**二、过滤已有目标（非 Ability 环境）**

1. 调用 `Perform Filtering Async Action`，传入 `SourceActor`、预设、`bUseAsyncTargeting=false`，以及 `InTargets` 数组（候选者）。
2. 在 `Targeted` 事件中拿到句柄，同样通过子系统获取结果。

**三、自定义选择/过滤任务（蓝图类）**

- 新建蓝图继承 `USimpleTargetingSelectionTask`，重写 `SelectTargets` 事件，在事件内调用 `AddTargetActor` 或 `AddHitResult` 来添加目标。
- 新建蓝图继承 `USimpleTargetingFilterTask`，重写 `ShouldFilterTarget` 事件，返回 `true` 表示剔除该目标。
- 新建蓝图继承 `USimpleTargetingSortTask`，重写 `GetScoreForTarget` 事件，返回一个浮点分数，系统将按分数排序。

---

## C++ 用法

### 头文件引入

```cpp
#include "TargetingSystem/TargetingSubsystem.h"
#include "TargetingSystem/TargetingPreset.h"
#include "TargetingSystemTypes.h"
```

### 基本用法

#### 立即执行一次完整的目标选择（同步）

```cpp
// 来源：TargetingSubsystem.h 中的 ExecuteImmediateTargetingRequest 描述
void AMyActor::SelectTargetsNow()
{
    UTargetingSubsystem* Subsystem = UTargetingSubsystem::Get(this); // 确保 GameInstance 有效
    if (!Subsystem) return;

    // 创建或从 DataAsset 获取 UTargetingPreset
    UTargetingPreset* Preset = LoadObject<UTargetingPreset>(nullptr, TEXT("/Game/TargetingPresets/BP_MyPreset.BP_MyPreset"));
    if (!Preset) return;

    // 发起立即请求（同步执行）
    FTargetingRequestHandle Handle = Subsystem->ExecuteImmediateTargetingRequest(Preset, [this](FTargetingRequestHandle InHandle)
    {
        // 处理回调（同步模式下回调在 ExecuteImmediate... 内部被调用）
        TArray<AActor*> Results;
        Subsystem->GetTargetingResultsActors(InHandle, Results);
        for (AActor* Actor : Results)
        {
            // 使用 Actor
        }
    }, nullptr, bAllowAsync);
}
```

#### 异步执行（借助 UAsyncAction_PerformTargeting）

```cpp
// 来源：Async/AsyncAction_PerformTargeting.h
void AMyActor::StartAsyncSelection()
{
    UTargetingPreset* Preset = /* 获取预设 */;
    UAsyncAction_PerformTargeting* Action = UAsyncAction_PerformTargeting::PerformTargetingRequest(this, Preset, true);
    if (Action)
    {
        Action->Targeted.AddDynamic(this, &AMyActor::OnTargetingReady);
        Action->Activate();
    }
}

void AMyActor::OnTargetingReady(FTargetingRequestHandle TargetingHandle)
{
    UTargetingSubsystem* Subsystem = UTargetingSubsystem::Get(this);
    TArray<AActor*> Targets;
    Subsystem->GetTargetingResultsActors(TargetingHandle, Targets);
    // 处理结果
}
```

### 进阶用法

#### 自定义选择任务（C++ 子类）

创建一个选择任务类，重写 `Execute` 并在其中使用自定义逻辑添加目标：

```cpp
// MySelectionTask.h
#include "Tasks/TargetingTask.h"
#include "Tasks/SimpleTargetingSelectionTask.h"
UCLASS()
class UMySelectionTask : public USimpleTargetingSelectionTask
{
    GENERATED_BODY()
public:
    virtual void Execute(const FTargetingRequestHandle& TargetingHandle) const override;
};

// MySelectionTask.cpp
void UMySelectionTask::Execute(const FTargetingRequestHandle& TargetingHandle) const
{
    // 使用子系统数据存储获取源上下文
    const FTargetingSourceContext* SourceContext = FTargetingSourceContext::Find(TargetingHandle);
    if (!SourceContext || !SourceContext->SourceActor) return;

    // 遍历世界中的敌人
    UWorld* World = GetSourceContextWorld(TargetingHandle);
    TArray<AActor*> ActorsToTest;
    // ... 填充 ActorsToTest
    for (AActor* Actor : ActorsToTest)
    {
        // 使用基类提供的辅助函数添加目标
        AddTargetActor(TargetingHandle, Actor);
    }
}
```

#### 手动构建数据存储（高级用法，无需 Preset）

```cpp
// 来源：TargetingSubsystem.h 注释
FTargetingRequestHandle ManualHandle = FTargetingRequestHandle(1);
// 设置必要的数据存储
FTargetingRequestData& RequestData = FTargetingRequestData::FindOrAdd(ManualHandle);
RequestData.bReleaseOnCompletion = true; // 自动释放

FTargetingTaskSet& TaskSet = FTargetingTaskSet::FindOrAdd(ManualHandle);
TaskSet.Tasks.Add(NewObject<UMySelectionTask>(), ...); // 添加任务

FTargetingSourceContext& SourceCtx = FTargetingSourceContext::FindOrAdd(ManualHandle);
SourceCtx.SourceActor = this->GetOwner();

// 执行
UTargetingSubsystem* Subsystem = UTargetingSubsystem::Get(this);
Subsystem->ExecuteImmediateTargetingRequest(ManualHandle);
// 完成后无需手动释放（bReleaseOnCompletion=true）
```

---

## Demo 示例

以下是一个完整的 C++ 示例，演示如何在本模块外创建一个可编译的 MiniGame、使用 Targeting System 进行距离排序选择。

### MyTargetingDemoActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TargetingSystem/TargetingPreset.h"
#include "TargetingSystemTypes.h"
#include "MyTargetingDemoActor.generated.h"

class UTargetingSubsystem;

UCLASS()
class AMyTargetingDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyTargetingDemoActor();

protected:
    virtual void BeginPlay() override;

private:
    void OnTargetingComplete(FTargetingRequestHandle Handle);
    void OnAsyncTargetingComplete(FTargetingRequestHandle Handle);

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Targeting Demo")
    UTargetingPreset* TargetingPreset;
};
```

### MyTargetingDemoActor.cpp

```cpp
#include "MyTargetingDemoActor.h"
#include "TargetingSystem/TargetingSubsystem.h"
#include "Tasks/TargetingFilterTask_SortByDistance.h"
#include "Tasks/TargetingSelectionTask_AOE.h"
#include "Tasks/TargetingFilterTask_ActorClass.h"
#include "Tasks/TargetingSelectionTask_SourceActor.h"
#include "TargetingSystemTypes.h"
#include "Async/AsyncAction_PerformTargeting.h"

AMyTargetingDemoActor::AMyTargetingDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTargetingDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 示例1：通过预设立即执行
    if (TargetingPreset)
    {
        UTargetingSubsystem* Subsystem = UTargetingSubsystem::Get(this);
        if (Subsystem)
        {
            FTargetingRequestHandle Handle = Subsystem->ExecuteImmediateTargetingRequest(
                TargetingPreset,
                FTargetingRequestDelegate::CreateUObject(this, &AMyTargetingDemoActor::OnTargetingComplete),
                nullptr, // 不适用委托上下文
                false    // 同步
            );
        }
    }

    // 示例2：异步执行（使用 Async Action）
    UAsyncAction_PerformTargeting* Action = UAsyncAction_PerformTargeting::PerformTargetingRequest(
        this, TargetingPreset, true);
    if (Action)
    {
        Action->Targeted.AddDynamic(this, &AMyTargetingDemoActor::OnAsyncTargetingComplete);
        Action->Activate();
    }
}

void AMyTargetingDemoActor::OnTargetingComplete(FTargetingRequestHandle Handle)
{
    UTargetingSubsystem* Subsystem = UTargetingSubsystem::Get(this);
    if (Subsystem)
    {
        TArray<AActor*> Results;
        Subsystem->GetTargetingResultsActors(Handle, Results);
        UE_LOG(LogTemp, Warning, TEXT("同步选择完成，找到了 %d 个目标"), Results.Num());
    }
}

void AMyTargetingDemoActor::OnAsyncTargetingComplete(FTargetingRequestHandle Handle)
{
    UTargetingSubsystem* Subsystem = UTargetingSubsystem::Get(this);
    if (Subsystem)
    {
        TArray<AActor*> Results;
        Subsystem->GetTargetingResultsActors(Handle, Results);
        for (AActor* Actor : Results)
        {
            // 对每个目标执行操作
        }
    }
}
```

**注意**：本示例假设你已将 `TargetingSystem` 插件启用，并在你的项目 `.Build.cs` 中正确添加了依赖（详见模块依赖）。另外，`TargetingPreset` 需要在内容浏览器中创建并指定。

---

## 模块依赖

要在你的模块中使用 `TargetingSystem`，请在 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "TargetingSystem",
    "GameplayAbilities"   // 因为 uplugin 声明依赖，且 AbilityTask 使用了它
});
```

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 提供 `UGameplayAbility` 和 `AbilityTask` 基类，用于 `UAbilityTask_PerformTargeting`；如果你的代码不从 Ability 发起请求，可改为 Private 依赖或移除。 |

其余均为标准依赖（Core、Engine、CoreUObject 等），此处省略。

---

## 维护状态

### 近期更新

- 2025-07-18 `462ec4ed` 修复警告 V623：检查 '?:' 运算符，临时对象创建问题
- 2025-06-26 `ec900998` 在带有对应 .gen.cpp 的源文件中添加 `UE_INLINE_GENERATED_CPP_BY_NAME`
- 2025-06-26 `a2e75189` 同上（重复提交）
- 2025-06-10 `1be7adc4` 将 GameplayFramework 模块中的部分 `FORCEINLINE` 替换为 `inline`
- 2025-06-09 `fa2bf192` 移除碰撞转换中的弱指针解引用

### 维护评价

- **创建时间**：2025‑06‑09，距今仅约2个月，是 UE 5.7 的新增插件。
- **近期更新**：最近一个月内有多次修改（修复警告、代码现代化）。
- **活跃度**：开发团队仍在持续维护，无废弃迹象。
- **已知限制**：当前标记为 `IsBetaVersion=true`，API 可能在未来版本调整。
- **推荐使用**：如果你正在使用 GameplayAbilities 或需要一个灵活的目标选择管线，强烈推荐使用。实验性标签意味着随时关注版本更新。

---

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayTargetingSystem)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/targeting-system/)（UE 5.7 文档上线后）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/TargetingSystem)（部分测试位于主仓库 Tests 目录下）