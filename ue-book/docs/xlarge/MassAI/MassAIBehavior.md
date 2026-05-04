# docs/xlarge/MassAI/index.md

# Mass AI

> AI-specific functionality extending MassGameplay

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（StateTree Schema） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 MassGameplay 框架的 AI 扩展插件，解决的核心问题是：**如何在大规模实体（Mass Entity）上高效运行 AI 行为逻辑**。

传统 AI 系统（如 BehaviorTree）为每个 Actor 独立运行，当场景中有成千上万个 NPC 时，性能开销巨大。MassAI 通过以下方式解决这个问题：

1. **StateTree 集成**：将 StateTree 行为状态机绑定到 Mass 实体上，利用 Mass 的批处理（Chunk Processing）架构，让数千个实体共享同一个 StateTree 资产的执行逻辑
2. **导航系统**：提供两套导航方案——基于 NavMesh 的自由导航和基于 ZoneGraph 的结构化车道导航，均针对 Mass 的大规模场景优化
3. **LookAt 系统**：高效的注视行为系统，支持实体间注视追踪、随机扫视、沿路径注视等，使用空间哈希网格加速目标查找
4. **Smart Object 交互**：与 SmartObject 系统集成，让 Mass 实体能够查找、声明和使用场景中的交互对象
5. **ZoneGraph 注解**：基于 ZoneGraph 车道标签的行为注解系统，用于实现区域感知的 AI 决策

**为什么需要这个插件？** 如果你的游戏需要大量 AI 角色（如城市模拟、RTS、开放世界 NPC 群体），且使用了 MassEntity 框架，那么 MassAI 是让这些实体拥有 AI 行为的唯一途径。它不是传统 BehaviorTree 的替代品，而是 Mass 架构下的 AI 行为层。

## 使用场景

- 你在做一个城市模拟游戏，需要数千个市民在城市中自主行走、交互 → 使用 MassAI + ZoneGraph Navigation
- 你需要大量 NPC 在战斗中做出反应（逃跑、寻找掩体）→ 使用 MassAI 的 StateTree + ZoneGraph Annotation（扰动标签 + 逃跑目标任务）
- 你有大量角色需要自然地看向不同方向、追踪视线目标 → 使用 MassAI 的 LookAt 系统
- 你需要大量实体与场景中的 Smart Object 交互（如坐椅子、使用设备）→ 使用 MassAI 的 SmartObject 任务链
- 你只需要少量 AI 角色（< 100）→ **不需要 MassAI**，使用传统 BehaviorTree 或 StateTree 即可

## 子模块概览

| 子模块 | 说明 | 文档 |
|---|---|---|
| **MassAIBehavior** | 核心行为模块：StateTree 集成、LookAt、SmartObject 任务、ZoneGraph 注解 | [→ 详细文档](MassAIBehavior.md) |
| **MassAIBehaviorEditor** | 行为模块的编辑器支持（自定义 Detail、Schema 编辑等） | 待补充 |
| **MassAIDebug** | AI 调试可视化工具 | 待补充 |
| **MassAIReplication** | Mass AI 实体的网络复制支持 | 待补充 |
| **MassAITestSuite** | 自动化测试套件 | 待补充 |
| **MassNavigation** | 导航核心功能：移动目标、避障、转向 | 待补充 |
| **MassNavigationEditor** | 导航模块的编辑器支持 | 待补充 |
| **MassNavMeshNavigation** | 基于 NavMesh 的导航实现（路径查找、路径跟随） | 待补充 |
| **MassZoneGraphNavigation** | 基于 ZoneGraph 的车道导航实现 | 待补充 |

## 维护状态

### 近期更新

```
- 274755918397 [MassStateTree] updated Trait and processors to only run for Standalone and Server execution mode (now consistent with UMassStateTreeFragmentDestructor). This fixes issue with some failed requirement (e.g., SmartObjectSubsystem) not available on Client. More work will be required to enable MassStateTree on clients. #jira UE-317261
- 1192ee320773 [MassAI] minor update to SmartObject task to expose NumSlots for bindings and fail claim task when no slots are available
- f56aabefe898 [MassSmartObject] updated MassFindSmartObjectTargetTask to be able to use entrance location request.
```

- 第一条：修复了 StateTree 在客户端执行时因缺少 SmartObjectSubsystem 等依赖而失败的问题，限制为仅在 Standalone 和 Server 模式运行
- 第二条：SmartObject 任务改进，暴露 NumSlots 供数据绑定使用
- 第三条：SmartObject 查找任务新增入口位置请求支持

### 维护评价

- **状态**：实验性开发中，持续活跃更新
- **创建时间**：2021-09-29，约 4 年历史
- **更新频率**：近期有实质性功能更新和 bug 修复，开发活跃
- **已知限制**：
  - `IsExperimentalVersion = true`，API 可能随版本变化
  - `EnabledByDefault = false`，需要手动在插件管理器中启用
  - 客户端 StateTree 执行尚未完全支持（见最新 commit）
  - 部分模块（如 MassAIReplication）仍在开发中
- **推荐程度**：如果你的项目已经使用 MassEntity 框架且需要大规模 AI，这是必选插件。但要做好 API 变动的准备，不建议在需要稳定 API 的项目中深度依赖未公开接口。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI)
- [MassAIBehavior 子模块文档](MassAIBehavior.md)

---

# docs/xlarge/MassAI/MassAIBehavior.md

# MassAIBehavior

MassAI 插件的核心行为模块，提供 StateTree 行为状态机与 Mass 实体的集成，以及 LookAt 注视系统、SmartObject 交互、ZoneGraph 行为注解等功能。

## 蓝图用法

### LookAt 子系统（BlueprintCallable）

`UMassLookAtSubsystem` 提供了蓝图可调用的 LookAt 请求 API，用于从游戏逻辑中控制 Mass 实体的注视行为。

#### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateLookAtPositionRequest` | 创建看向指定世界位置的 LookAt 请求 | `UMassLookAtSubsystem` |
| `CreateLookAtActorRequest` | 创建看向指定 Actor 的 LookAt 请求（Actor 移动时自动更新） | `UMassLookAtSubsystem` |
| `DeleteRequest` | 删除一个 LookAt 请求 | `UMassLookAtSubsystem` |

#### 使用示例（蓝图描述）

**让某个 Mass 实体看向一个点：**
1. 获取 `MassLookAtSubsystem`（通过 `Get Game Instance → Get Subsystem`）
2. 调用 `CreateLookAtPositionRequest`，传入：
   - `ViewerActor`：与 Mass 实体关联的 Actor
   - `Priority`：优先级（影响多个请求竞争时的选择）
   - `TargetLocation`：目标世界坐标
   - `InterpolationSpeed`：插值速度（Instant/Fast/Regular/Slow/Custom）
3. 保存返回的 `FMassLookAtRequestHandle`
4. 需要停止时，调用 `DeleteRequest` 传入保存的 Handle

**让某个 Mass 实体持续追踪另一个 Actor：**
1. 调用 `CreateLookAtActorRequest`，传入 `TargetActor`
2. 系统会自动追踪目标 Actor 的位置变化
3. 如果目标 Actor 有关联的 Mass 实体，会使用更精确的追踪逻辑

### StateTree 节点

MassAIBehavior 的核心功能通过 StateTree 节点暴露。这些节点在 StateTree 编辑器中使用，不是传统的蓝图节点。

#### Tasks（任务节点）

**导航类：**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ZG Path Follow` | 沿 ZoneGraph 车道路径跟随到目标点 | `FMassZoneGraphPathFollowTask` |
| `ZG Stand` | 在当前 ZoneGraph 位置停止站立 | `FMassZoneGraphStandTask` |
| `ZG Find Escape Target` | 基于扰动注解查找逃跑目标位置 | `FMassZoneGraphFindEscapeTarget` |
| `ZG Find Smart Object Target` | 基于 ZoneGraph 位置查找 SmartObject 目标 | `FMassZoneGraphFindSmartObjectTarget` |
| `NavMesh Path Follow` | 沿 NavMesh 路径跟随到目标点 | `FMassNavMeshPathFollowTask` |
| `NavMesh Stand` | 在当前 NavMesh 位置停止站立 | `FMassNavMeshStandTask` |
| `NavMesh Animate` | 在当前位置停止并播放动画 | `FMassNavMeshAnimateTask` |
| `NavMesh Find Random Reachable Target` | 在 NavMesh 上查找随机可达位置 | `FMassNavMeshFindReachablePointTask` |

**SmartObject 交互类：**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Smart Object` | 搜索附近的 SmartObject 候选 | `FMassFindSmartObjectTask` |
| `Find Smart Object Target` | 计算到已声明 SmartObject 的移动目标 | `FMassFindSmartObjectTargetTask` |
| `Claim SmartObject` | 从候选结果中声明一个 SmartObject | `FMassClaimSmartObjectTask` |
| `Use SmartObject Task` | 开始使用已声明的 SmartObject | `FMassUseSmartObjectTask` |

**行为类：**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mass LookAt Task` | 设置实体的 LookAt 目标和模式 | `FMassLookAtTask` |

#### Evaluators（求值器）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ZG Annotation Tags` | 暴露当前 ZoneGraph 注解标签供决策使用 | `FMassZoneGraphAnnotationEvaluator` |
| `Mass ComponentHit Eval` | 提取最近的碰撞事件信息 | `FMassComponentHitEvaluator` |

#### Conditions（条件）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ZoneGraphTagFilter Compare` | 使用过滤器比较 ZoneGraph 标签 | `FZoneGraphTagFilterCondition` |
| `ZoneGraphTagMask Compare` | 比较两个标签掩码 | `FZoneGraphTagMaskCondition` |
| `ZoneGraphTag Compare` | 比较两个标签值 | `FZoneGraphTagCondition` |

#### Traits（实体特征）

在 Mass Entity Template 编辑器中使用，为实体添加 AI 行为能力：

| Trait | 说明 | 所在类 |
|---|---|---|
| `StateTree` | 为实体绑定一个 StateTree 行为资产 | `UMassStateTreeTrait` |
| `Look At` | 为实体添加 LookAt 注视能力 | `UMassLookAtTrait` |
| `Look At Target` | 将实体标记为可被注视的目标 | `UMassLookAtTargetTrait` |
| `ZoneGraph Annotation` | 为实体添加 ZoneGraph 注解标签能力 | `UMassZoneGraphAnnotationTrait` |

### 典型 StateTree 工作流

一个典型的 Mass AI StateTree 可能包含以下状态流转：

1. **Find Smart Object** → 搜索附近的交互对象
2. **Claim SmartObject** → 声明找到的对象
3. **Find Smart Object Target** → 计算移动目标
4. **ZG Path Follow** / **NavMesh Path Follow** → 移动到目标
5. **Use SmartObject Task** → 执行交互
6. **ZG Stand** / **NavMesh Stand** → 交互完成后站立等待
7. 回到步骤 1

## C++ 用法

### 头文件引入

```cpp
// StateTree 行为基础类型
#include "MassStateTreeTypes.h"
#include "MassStateTreeExecutionContext.h"

// LookAt 系统
#include "MassLookAtSubsystem.h"
#include "MassLookAtFragments.h"

// ZoneGraph 注解
#include "MassZoneGraphAnnotationFragments.h"

// SmartObject 集成
#include "MassFindSmartObjectTask.h"
#include "MassClaimSmartObjectTask.h"

// 导航类型
#include "MassZoneGraphPathFollowTask.h"
#include "MassNavMeshPathfollowTask.h"
```

### 基本用法：创建自定义 StateTree Task

所有 Mass StateTree Task 需要继承 `FMassStateTreeTaskBase`，并实现 `GetDependencies` 声明所需的 Mass Fragment 依赖。

```cpp
// MyMassTask.h
#pragma once

#include "MassStateTreeTypes.h"
#include "MassNavigationTypes.h"
#include "MyMassTask.generated.h"

struct FTransformFragment;
struct FMassMoveTargetFragment;

// 实例数据：每个实体独立维护的状态
USTRUCT()
struct FMyMassTaskInstanceData
{
    GENERATED_BODY()

    // 编辑器中可配置的参数
    UPROPERTY(EditAnywhere, Category = Parameter)
    float SearchRadius = 500.f;

    // 输出：计算得到的目标位置
    UPROPERTY(EditAnywhere, Category = Output)
    FMassTargetLocation TargetLocation;

    // 内部计时
    UPROPERTY()
    float Time = 0.f;
};

// Task 定义
USTRUCT(meta = (DisplayName = "My Custom Mass Task"))
struct FMyMassTask : public FMassStateTreeTaskBase
{
    GENERATED_BODY()

    using FInstanceDataType = FMyMassTaskInstanceData;

protected:
    virtual bool Link(FStateTreeLinker& Linker) override;
    virtual const UStruct* GetInstanceDataType() const override
    {
        return FInstanceDataType::StaticStruct();
    }
    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context,
        const FStateTreeTransitionResult& Transition) const override;
    virtual EStateTreeRunStatus Tick(FStateTreeExecutionContext& Context,
        const float DeltaTime) const override;

    // 声明 Mass 依赖（关键！）
    virtual void GetDependencies(UE::MassBehavior::FStateTreeDependencyBuilder& Builder) const override;

    // 外部数据句柄
    TStateTreeExternalDataHandle<FTransformFragment> TransformHandle;
    TStateTreeExternalDataHandle<FMassMoveTargetFragment> MoveTargetHandle;
};
```

```cpp
// MyMassTask.cpp
#include "MyMassTask.h"
#include "MassNavigationTypes.h"
#include "MassStateTreeExecutionContext.h"
#include "TransformFragment.h"
#include "MassMoveTargetFragment.h"

bool FMyMassTask::Link(FStateTreeLinker& Linker)
{
    Linker.LinkExternalData(TransformHandle);
    Linker.LinkExternalData(MoveTargetHandle);
    return true;
}

void FMyMassTask::GetDependencies(UE::MassBehavior::FStateTreeDependencyBuilder& Builder) const
{
    Builder.AddReadOnly<FTransformFragment>()
           .AddReadWrite<FMassMoveTargetFragment>();
}

EStateTreeRunStatus FMyMassTask::EnterState(FStateTreeExecutionContext& Context,
    const FStateTreeTransitionResult& Transition) const
{
    // 获取实例数据和外部数据
    FInstanceDataType& InstanceData = Context.GetInstanceData(*this);
    const FTransformFragment& Transform = Context.GetExternalData(TransformHandle);

    // 计算目标位置（示例：实体前方 SearchRadius 距离处）
    const FVector Forward = Transform.GetTransform().GetRotation().GetForwardVector();
    InstanceData.TargetLocation.Position = Transform.GetTransform().GetLocation()
        + Forward * InstanceData.SearchRadius;

    InstanceData.Time = 0.f;
    return EStateTreeRunStatus::Running;
}

EStateTreeRunStatus FMyMassTask::Tick(FStateTreeExecutionContext& Context,
    const float DeltaTime) const
{
    FInstanceDataType& InstanceData = Context.GetInstanceData(*this);
    InstanceData.Time += DeltaTime;

    // 5 秒后完成
    if (InstanceData.Time >= 5.0f)
    {
        return EStateTreeRunStatus::Succeeded;
    }
    return EStateTreeRunStatus::Running;
}
```

> 来源参考：`MassNavMeshFindReachablePointTask.h`、`MassZoneGraphStandTask.h` 等头文件的结构模式

### 进阶用法：使用 LookAt 子系统

```cpp
#include "MassLookAtSubsystem.h"

void AMyGameMode::SetupNPCGaze(AActor* NPCActor, AActor* TargetActor)
{
    UMassLookAtSubsystem* LookAtSubsystem = GetWorld()->GetSubsystem<UMassLookAtSubsystem>();
    if (!LookAtSubsystem) return;

    // 创建一个看向目标 Actor 的请求
    FMassLookAtRequestHandle Handle = LookAtSubsystem->CreateLookAtActorRequest(
        NPCActor,
        FMassLookAtPriority(0),  // 最高优先级
        TargetActor,
        EMassLookAtInterpolationSpeed::Fast
    );

    // 保存 Handle 以便后续删除
    ActiveLookAtHandles.Add(Handle);
}

void AMyGameMode::StopAllGaze()
{
    UMassLookAtSubsystem* LookAtSubsystem = GetWorld()->GetSubsystem<UMassLookAtSubsystem>();
    for (const FMassLookAtRequestHandle& Handle : ActiveLookAtHandles)
    {
        LookAtSubsystem->DeleteRequest(Handle);
    }
    ActiveLookAtHandles.Empty();
}
```

> 来源参考：`MassLookAtSubsystem.h` 中的 `CreateLookAtActorRequest`、`DeleteRequest` 接口

### 进阶用法：ZoneGraph 注解条件判断

在自定义 StateTree 条件中使用 ZoneGraph 标签进行区域感知决策：

```cpp
#include "ZoneGraphTypes.h"
#include "MassZoneGraphAnnotationFragments.h"
#include "MassStateTreeTypes.h"

USTRUCT()
struct FMyZoneConditionInstanceData
{
    GENERATED_BODY()

    // 从 Evaluator 获取的当前标签
    UPROPERTY(EditAnywhere, Category = Input)
    FZoneGraphTagMask CurrentTags = FZoneGraphTagMask::None;
};

USTRUCT(DisplayName = "Is In Safe Zone")
struct FMyZoneCondition : public FMassStateTreeConditionBase
{
    GENERATED_BODY()

    using FInstanceDataType = FMyZoneConditionInstanceData;

    virtual const UStruct* GetInstanceDataType() const override
    {
        return FInstanceDataType::StaticStruct();
    }

    virtual bool TestCondition(FStateTreeExecutionContext& Context) const override
    {
        const FInstanceDataType& Data = Context.GetInstanceData(*this);
        // 检查是否包含安全区域标签
        return Data.CurrentTags.Contains(SafeZoneTag);
    }

    virtual void GetDependencies(UE::MassBehavior::FStateTreeDependencyBuilder& Builder) const override
    {
        Builder.AddReadOnly<FMassZoneGraphAnnotationFragment>();
    }

    UPROPERTY(EditAnywhere, Category = Condition)
    FZoneGraphTag SafeZoneTag;
};
```

> 来源参考：`ZoneGraphTagConditions.h`、`MassZoneGraphAnnotationEvaluator.h`

## Demo 示例

以下是一个完整的自定义 Mass StateTree Task，实现"在指定半径内随机漫游"的行为。

### MyMassWanderTask.h

```cpp
#pragma once

#include "MassStateTreeTypes.h"
#include "MassNavigationTypes.h"
#include "MassStateTreeExecutionContext.h"
#include "MyMassWanderTask.generated.h"

struct FTransformFragment;
struct FMassMoveTargetFragment;
struct FAgentRadiusFragment;

USTRUCT()
struct FMyMassWanderTaskInstanceData
{
    GENERATED_BODY()

    /** 漫游半径 */
    UPROPERTY(EditAnywhere, Category = Parameter, meta = (UIMin = 100, ClampMin = 100))
    float WanderRadius = 1000.f;

    /** 每次选择新目标后的等待时间 */
    UPROPERTY(EditAnywhere, Category = Parameter)
    float WaitDuration = 2.0f;

    /** 输出：当前移动目标 */
    UPROPERTY(VisibleAnywhere, Category = Output)
    FMassTargetLocation TargetLocation;

    UPROPERTY()
    float WaitTime = 0.f;

    UPROPERTY()
    bool bWaiting = false;
};

USTRUCT(meta = (DisplayName = "Mass Wander"))
struct FMyMassWanderTask : public FMassStateTreeTaskBase
{
    GENERATED_BODY()

    using FInstanceDataType = FMyMassWanderTaskInstanceData;

protected:
    virtual bool Link(FStateTreeLinker& Linker) override;
    virtual const UStruct* GetInstanceDataType() const override
    {
        return FInstanceDataType::StaticStruct();
    }
    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context,
        const FStateTreeTransitionResult& Transition) const override;
    virtual EStateTreeRunStatus Tick(FStateTreeExecutionContext& Context,
        const float DeltaTime) const override;
    virtual void GetDependencies(UE::MassBehavior::FStateTreeDependencyBuilder& Builder) const override;

    TStateTreeExternalDataHandle<FTransformFragment> TransformHandle;
    TStateTreeExternalDataHandle<FMassMoveTargetFragment> MoveTargetHandle;
    TStateTreeExternalDataHandle<FAgentRadiusFragment> AgentRadiusHandle;
};
```

### MyMassWanderTask.cpp

```cpp
#include "MyMassWanderTask.h"
#include "MassNavigationTypes.h"
#include "MassStateTreeExecutionContext.h"

bool FMyMassWanderTask::Link(FStateTreeLinker& Linker)
{
    Linker.LinkExternalData(TransformHandle);
    Linker.LinkExternalData(MoveTargetHandle);
    Linker.LinkExternalData(AgentRadiusHandle);
    return true;
}

void FMyMassWanderTask::GetDependencies(UE::MassBehavior::FStateTreeDependencyBuilder& Builder) const
{
    Builder.AddReadOnly<FTransformFragment>()
           .AddReadWrite<FMassMoveTargetFragment>()
           .AddReadOnly<FAgentRadiusFragment>();
}

EStateTreeRunStatus FMyMassWanderTask::EnterState(FStateTreeExecutionContext& Context,
    const FStateTreeTransitionResult& Transition) const
{
    FInstanceDataType& InstanceData = Context.GetInstanceData(*this);
    const FTransformFragment& Transform = Context.GetExternalData(TransformHandle);

    // 在当前位置周围随机选择一个目标
    const FVector Origin = Transform.GetTransform().GetLocation();
    const FVector RandomDir = FMath::VRand().GetSafeNormal2D();
    InstanceData.TargetLocation.Position = Origin + RandomDir * FMath::RandRange(0.f, InstanceData.WanderRadius);
    InstanceData.TargetLocation.SegmentDirection = (InstanceData.TargetLocation.Position - Origin).GetSafeNormal();
    InstanceData.TargetLocation.Action = EMassMovementAction::Move;

    InstanceData.bWaiting = false;
    InstanceData.WaitTime = 0.f;

    return EStateTreeRunStatus::Running;
}

EStateTreeRunStatus FMyMassWanderTask::Tick(FStateTreeExecutionContext& Context,
    const float DeltaTime) const
{
    FInstanceDataType& InstanceData = Context.GetInstanceData(*this);

    if (InstanceData.bWaiting)
    {
        InstanceData.WaitTime += DeltaTime;
        if (InstanceData.WaitTime >= InstanceData.WaitDuration)
        {
            // 等待结束，重新选择目标（通过重新进入状态）
            return EStateTreeRunStatus::Succeeded;
        }
        return EStateTreeRunStatus::Running;
    }

    // 检查是否到达目标（简化判断）
    const FTransformFragment& Transform = Context.GetExternalData(TransformHandle);
    const float DistSq = FVector::DistSquared(
        Transform.GetTransform().GetLocation(),
        InstanceData.TargetLocation.Position);

    if (DistSq < FMath::Square(100.f))
    {
        // 到达目标，开始等待
        InstanceData.bWaiting = true;
        InstanceData.WaitTime = 0.f;
    }

    return EStateTreeRunStatus::Running;
}
```

> 此示例参考了 `MassNavMeshFindReachablePointTask` 和 `MassZoneGraphStandTask` 的实现模式。

## 模块依赖

从 Build.cs 和源码分析，使用 MassAIBehavior 需要以下非标准依赖：

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体框架核心（Fragment、Processor、Entity 管理） |
| `MassGameplay` | Mass 游戏play 扩展（移动、导航 Fragment 等） |
| `StateTree` | StateTree 行为状态机框架 |
| `ZoneGraph` | ZoneGraph 区域图系统（车道、标签） |
| `SmartObjects` | SmartObject 交互系统 |
| `NavigationSystem` | NavMesh 导航系统 |

> 注意：MassAIBehavior 的 Build.cs 还依赖 `EditorFramework` 和 `UnrealEd`，但这些是编辑器常见依赖，运行时不需要。

## 维护状态

### 近期更新

```
- 274755918397 [MassStateTree] updated Trait and processors to only run for Standalone and Server execution mode (now consistent with UMassStateTreeFragmentDestructor). This fixes issue with some failed requirement (e.g., SmartObjectSubsystem) not available on Client. More work will be required to enable MassStateTree on clients. #jira UE-317261
- 1192ee320773 [MassAI] minor update to SmartObject task to expose NumSlots for bindings and fail claim task when no slots are available
- f56aabefe898 [MassSmartObject] updated MassFindSmartObjectTargetTask to be able to use entrance location request.
```

### 维护评价

MassAIBehavior 是 MassAI 插件中最核心、最活跃的模块。近期更新集中在 StateTree 集成的稳定性和 SmartObject 交互的完善上。作为实验性模块，API 仍在演进中，但核心架构（StateTree + Mass Fragment 依赖声明）已经趋于稳定。建议在项目中使用时关注版本更新日志，特别是 StateTree 相关的 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI/Source/MassAIBehavior)
- [MassAI 插件主页](index.md)