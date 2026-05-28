# Mass AI

> AI-specific functionality extending MassGameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模AI |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，StateTree 任务/条件/评估器） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavMeshNavigation` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 UE5 MassGameplay (Mass Entity/Actor) 框架在 AI 领域的专用扩展插件。其核心目标是解决**如何在大规模实体组件系统 (ECS) 架构下，高效地为成千上万个实体实现复杂的 AI 行为**。

该插件将 Mass 实体与 UE 的导航系统（ZoneGraph、NavMesh）、视线控制（LookAt）以及行为状态机（StateTree）深度集成。它不再为每个 AI 代理（Agent）维护独立的 BrainComponent，而是通过 Mass 处理器（Processor）和片段（Fragment）来批量处理、更新和同步大量实体的 AI 状态与行为，从而实现极高的性能。它本质上是一套为大规模群体模拟（如城市中的行人、战场上的士兵、虚拟世界中的生物）设计的 AI 行为系统。

## 使用场景

- **城市模拟/人群模拟**：你需要管理成百上千个行人（NPC）在基于 ZoneGraph 道路网络上的自主导航、避障、寻找智能物体（如长椅、售货机）并交互。
- **大型战略或即时战略游戏**：你需要为地图上大量的单位集群提供统一的行为逻辑（巡逻、进攻、逃跑），并利用 StateTree 进行行为决策。
- **开放世界游戏**：你需要让大量动态生成的 NPC 具有“活着”的感觉，他们会环顾四周（LookAt）、根据环境标签（ZoneGraph Annotations）改变行为、并在导航网格上自由行走。
- **优化 AI 性能**：当传统的 `AAIController` + `UBrainComponent` 方案因实体数量过多而导致性能瓶颈时，MassAI 是理想的替代方案。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Look At Position Request` | 为与指定 Actor 关联的 Mass 实体创建一个“看向固定位置”的请求，并返回一个句柄用于管理该请求。 | `UMassLookAtSubsystem` |
| `Create Look At Actor Request` | 为与指定 Actor 关联的 Mass 实体创建一个“看向目标 Actor”的请求，支持动态跟踪目标。 | `UMassLookAtSubsystem` |
| `Delete Request` | 通过请求句柄移除一个已存在的 LookAt 请求。 | `UMassLookAtSubsystem` |

### 使用示例（蓝图描述）

1.  **创建 LookAt 请求**：
    -   在事件图表中，使用 `Get Mass Look At Subsystem` 节点获取 `UMassLookAtSubsystem` 的实例。
    -   从该实例拖出引线，调用 `Create Look At Position Request` 节点。
    -   将 `Viewer Actor` 引脚连接到你想要控制其视线的实体所对应的 Actor。
    -   设置 `Priority`（优先级，用于决定当有多个请求时哪个生效）、`Target Location`（目标世界位置）等参数。
    -   该节点会返回一个 `FMassLookAtRequestHandle` 结构体，应保存此句柄以便后续删除请求。

2.  **管理请求**：
    -   将上一步保存的 `Request Handle` 连接到 `Delete Request` 节点，即可停止该实体的 LookAt 行为。

3.  **使用 StateTree 驱动行为**：
    -   为你的 Mass 实体模板添加 `MassStateTree` 特性，并关联一个使用了 `MassStateTreeSchema` 的 StateTree 资产。
    -   在该 StateTree 资产中，可以使用插件提供的任务，如 `Mass Zone Graph Path Follow`（沿 ZoneGraph 路径移动）、`Mass Look At Task`（设置 LookAt 目标）、`Mass Find Smart Object`（寻找智能物体）等，来构建复杂的 AI 行为逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "MassAIBehaviorModule.h"
#include "MassLookAtSubsystem.h"
#include "MassStateTreeSubsystem.h"
// 包含你使用的具体任务/评估器头文件
#include "Tasks/MassZoneGraphPathFollowTask.h"
#include "Evaluators/MassZoneGraphAnnotationEvaluator.h"
```

### 基本用法

从测试案例中推断，基本用法是配置和使用 MassStateTree 来驱动实体行为。

```cpp
// 假设我们已经有一个 FMassEntityManager
// 1. 为实体配置 StateTree
// 在 MassEntityTemplate 或 Trait 中，通常通过 UMassStateTreeTrait 来指定 StateTree 资产。

// 2. 手动为实体请求 LookAt (C++ 侧)
UMassLookAtSubsystem* LookAtSubsystem = GetWorld()->GetSubsystem<UMassLookAtSubsystem>();
if (LookAtSubsystem && MyMassActor) // MyMassActor 是与 Mass 实体关联的 Actor
{
    FMassLookAtRequestHandle Handle = LookAtSubsystem->CreateLookAtPositionRequest(
        MyMassActor,
        FMassLookAtPriority(10), // 设置一个中等优先级
        SomeWorldLocation,
        EMassLookAtInterpolationSpeed::Fast);
    // 保存 Handle 以便后续删除
}
```

### 进阶用法

自定义 StateTree 任务或评估器，以访问和修改 Mass 片段数据。

```cpp
// 自定义一个 Mass StateTree 任务
USTRUCT(meta = (DisplayName = "My Custom Mass Task"))
struct FMyCustomMassTask : public FMassStateTreeTaskBase
{
    GENERATED_BODY()

protected:
    virtual bool Link(FStateTreeLinker& Linker) override;
    virtual const UStruct* GetInstanceDataType() const override;
    virtual EStateTreeRunStatus Tick(FStateTreeExecutionContext& Context, const float DeltaTime) const override;
    virtual void GetDependencies(UE::MassBehavior::FStateTreeDependencyBuilder& Builder) const override;

    // 声明对 Mass 片段的外部数据句柄
    TStateTreeExternalDataHandle<FTransformFragment> TransformHandle;
    TStateTreeExternalDataHandle<FMassMoveTargetFragment> MoveTargetHandle;
};

// 在 .cpp 中实现
bool FMyCustomMassTask::Link(FStateTreeLinker& Linker)
{
    Linker.LinkExternalData(TransformHandle);
    Linker.LinkExternalData(MoveTargetHandle);
    return true;
}

void FMyCustomMassTask::GetDependencies(UE::MassBehavior::FStateTreeDependencyBuilder& Builder) const
{
    // 声明该任务需要对 FTransformFragment 进行只读访问
    Builder.AddReadOnly<FTransformFragment>();
    // 需要对 FMassMoveTargetFragment 进行读写访问
    Builder.AddReadWrite<FMassMoveTargetFragment>();
}

EStateTreeRunStatus FMyCustomMassTask::Tick(FStateTreeExecutionContext& Context, const float DeltaTime) const
{
    // 获取 Mass 上下文以访问实体数据
    const FMassStateTreeExecutionContext& MassContext = static_cast<FMassStateTreeExecutionContext&>(Context);
    // 获取实体句柄
    const FMassEntityHandle Entity = MassContext.GetEntity();
    // 通过句柄访问片段数据（需要在 Query 中过滤）
    // ... 实现具体逻辑
    return EStateTreeRunStatus::Running;
}
```

## Demo 示例

一个最小示例，展示如何创建一个使用 MassAI 的简单实体。此实体将拥有一个用于导航的 ZoneGraph 位置和一个 LookAt 目标。

**MyMassAIEntity.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MassEntityTypes.h"
#include "MassLookAtFragments.h"
#include "MassNavigationFragments.h"
#include "MyMassAIEntity.generated.h"

// 定义实体模板构建器中需要添加的片段
USTRUCT()
struct FMyMassAIEntityTags : public FMassTag
{
    GENERATED_BODY()
};

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyMassAIEntityComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Mass AI")
    float DefaultLookAtDistance = 1000.0f;
};
```

**MyMassAIEntity.cpp**
```cpp
#include "MyMassAIEntity.h"
#include "MassEntityTemplateRegistry.h"
#include "MassEntitySubsystem.h"
#include "MassLookAtSubsystem.h"
#include "MassStateTreeTrait.h"
#include "MassLookAtTrait.h"
#include "MassZoneGraphNavigationTrait.h"

void UMyMassAIEntityComponent::BeginPlay()
{
    Super::BeginPlay();

    // 获取 Mass 实体子系统和模板注册表
    UMassEntitySubsystem* EntitySubsystem = GetWorld()->GetSubsystem<UMassEntitySubsystem>();
    UMassEntityTemplateRegistry* TemplateRegistry = EntitySubsystem->GetMutableTemplateRegistry();

    // 创建一个新的实体模板
    FMassEntityTemplateBuildContext BuildContext;
    BuildContext.AddTag<FMyMassAIEntityTags>();

    // 1. 添加导航功能 (假设使用 ZoneGraph)
    // BuildContext.AddTrait<UMassZoneGraphNavigationTrait>();

    // 2. 添加 LookAt 功能
    BuildContext.AddTrait<UMassLookAtTrait>();

    // 3. 添加 StateTree 功能以驱动复杂行为
    // BuildContext.AddTrait<UMassStateTreeTrait>();

    // 注册模板并生成实体
    const FMassEntityTemplate& EntityTemplate = TemplateRegistry->CreateTemplate(BuildContext);
    FMassEntityManager& EntityManager = EntitySubsystem->GetMutableEntityManager();

    // 创建实体（位置由 TransformFragment 等决定，此处省略）
    FMassEntityHandle NewEntity = EntityManager.CreateEntity(EntityTemplate.GetArchetype());

    // 可选：通过 LookAt 子系统为这个新实体创建一个初始的 LookAt 请求
    UMassLookAtSubsystem* LookAtSubsystem = GetWorld()->GetSubsystem<UMassLookAtSubsystem>();
    if (LookAtSubsystem && NewEntity.IsValid())
    {
        // 注意：CreateLookAtPositionRequest 需要关联的 Actor。在真实场景中，你可能需要先将实体与某个 Actor 关联起来。
        // 此处为示意代码。
        // LookAtSubsystem->CreateLookAtPositionRequest(...);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等及 MassGameplay 框架模块）。使用者需要在自己的模块 `Build.cs` 中依赖 `MassAIBehavior`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8e83e6bf` | Remove use of INFINITY to fix compile error on latest Windows SDK | 移除 INFINITY 的使用以解决最新 Windows SDK 上的编译错误 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数产生的警告代码 |
| 2026-05-12 | `328c7999` | [Mass] PR #14001: Fix Mass debugger running with invalid entity | 修复 Mass 调试器在无效实体上运行的问题 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中使用的作用域枚举可能导致输出乱码的问题 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | （关联提交，可能与调试功能相关） |

### 维护评价

MassAI 是一个功能强大且仍在积极维护的实验性插件。其创建时间较早（2021年），但近期（2026年）仍有持续的更新，主要集中在**编译修复、代码健壮性提升和调试功能完善**上，表明 Epic 团队仍在内部使用并维护此插件。

**优点**：
-   性能卓越，专为大规模实体设计。
-   与 StateTree 深度集成，行为逻辑可视化、可编辑。
-   提供了丰富的现成任务（导航、LookAt、智能物体交互等）。

**注意事项与限制**：
-   **实验性标记**：插件仍标记为 `IsExperimentalVersion = true`，且默认未启用 (`EnabledByDefault = false`)。这意味着其 API 可能在未来版本中发生变动，不适合追求绝对稳定性的项目直接使用。
-   **学习曲线**：需要开发者理解 Mass 框架（ECS）和 StateTree 的概念，与传统面向对象的 AI 编程范式差异较大。
-   **生态系统**：相关的教程、社区案例相对传统 AI 方案较少。

**推荐**：如果你的项目需要处理成千上万个 AI 实体，并且性能是关键指标，**强烈推荐尝试使用 MassAI**。尽管是实验性，但 Epic 自身在《堡垒之夜》等大型项目中已验证其可行性。对于小型项目或 AI 实体数量不多的情况，传统的 `AAIController` 方案可能更简单直接。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)
- [官方文档]() (无公开文档链接)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassAITestSuite)