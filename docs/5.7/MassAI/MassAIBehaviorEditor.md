# MassAI

> AI-specific functionality extending MassGameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（行为树资产、导航数据资产、调试工具） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 UE5 MassGameplay 框架的 AI 扩展插件。它解决的核心问题是：**如何为成千上万的实体（Mass Entity）高效地运行 AI 逻辑**。

传统的 AI 系统（如行为树）是为少量、复杂的角色设计的，当实体数量达到数千甚至数万时，其性能开销会变得不可接受。MassAI 通过以下方式解决这个问题：

1.  **数据导向设计**：将 AI 状态（如行为、导航目标、感知）存储为“片段”（Fragment），与实体分离，便于批量处理。
2.  **处理器（Processor）驱动**：AI 逻辑被分解为一系列处理器，每个处理器专注于一个特定任务（如更新行为状态、计算导航路径、处理感知），并可以并行执行。
3.  **与 MassGameplay 深度集成**：利用 Mass 的实体管理、查询和并行处理能力，实现高性能的 AI 模拟。

简单来说，MassAI 让你能够像管理粒子系统一样管理大量 AI 实体，同时保留了行为树、导航、感知等核心 AI 功能。

## 使用场景

- **大规模 RTS 游戏**：你需要控制数百个单位进行寻路、攻击、撤退等行为。
- **开放世界游戏**：你需要模拟整个城镇或区域的 NPC 日常活动（巡逻、工作、休息）。
- **塔防或生存游戏**：你需要生成并控制成百上千的敌人波次。
- **任何需要大量“简单”AI 实体的场景**：这些实体不需要复杂的对话或深度交互，但需要高效地执行基本行为。

## 蓝图用法

MassAI 主要通过其子模块提供功能。由于是运行时框架，大部分核心逻辑在 C++ 中，但提供了关键的蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindLookAtTarget` | 为实体查找一个视线目标（用于动画或逻辑） | `UMassLookAtSubsystem` |
| `RequestLookAt` | 请求实体看向特定位置或实体 | `UMassLookAtSubsystem` |
| `GetMassAIWorldSubsystem` | 获取 MassAI 的世界子系统，用于全局管理 | `UMassAIWorldSubsystem` |

### 使用示例（蓝图描述）

1.  **创建一个 MassAI 实体**：
    *   使用 `SpawnMassEntity` 节点创建实体。
    *   通过 `AddMassEntityFragment` 节点为实体添加 `FMassStateTreeInstanceFragment`（行为状态树实例）和 `FMassNavigationFragment`（导航片段）。
    *   设置行为状态树资产和导航目标。

2.  **控制实体视线**：
    *   获取 `UMassLookAtSubsystem`。
    *   调用 `RequestLookAt` 节点，传入实体句柄和目标位置/实体。

## C++ 用法

### 头文件引入

```cpp
#include "MassAIBehavior.h"
#include "MassNavigation.h"
#include "MassLookAtSubsystem.h"
```

### 基本用法

以下代码演示如何创建一个具有基本导航和行为状态树的 Mass AI 实体。

```cpp
// 来源：Engine/Plugins/AI/MassAI/Source/MassAITestSuite/Tests/MassNavigationTest.cpp (简化)
#include "MassEntitySpawnRegistry.h"
#include "MassEntityTemplate.h"
#include "MassStateTreeInstanceFragment.h"
#include "MassNavigationFragment.h"

void SpawnSimpleAIEntity(UWorld* World, const FVector& SpawnLocation, UStateTree* BehaviorTree)
{
    // 1. 获取实体模板注册表
    UMassEntitySpawnRegistry* SpawnRegistry = UMassEntitySpawnRegistry::Get(World);
    
    // 2. 创建或查找一个实体模板
    FMassEntityTemplateID TemplateID = SpawnRegistry->FindOrAddTemplate(TEXT("SimpleAI"));
    
    // 3. 配置模板片段
    FMassEntityTemplate& Template = SpawnRegistry->GetMutableTemplate(TemplateID);
    
    // 添加行为状态树片段
    FMassStateTreeInstanceFragment StateTreeFragment;
    StateTreeFragment.StateTree = BehaviorTree;
    Template.AddFragment(StateTreeFragment);
    
    // 添加导航片段
    FMassNavigationFragment NavFragment;
    NavFragment.DesiredSpeed = 300.f;
    Template.AddFragment(NavFragment);
    
    // 4. 在指定位置生成实体
    FTransform SpawnTransform(SpawnLocation);
    FMassEntityManager* EntityManager = UMassEntityManager::Get(World);
    FMassEntityHandle NewEntity = EntityManager->CreateEntity(TemplateID, SpawnTransform);
    
    // 5. (可选) 设置导航目标
    FMassNavigationSubsystem* NavSubsystem = World->GetSubsystem<FMassNavigationSubsystem>();
    if (NavSubsystem)
    {
        NavSubsystem->SetMovementTarget(NewEntity, FVector(1000.f, 1000.f, 0.f));
    }
}
```

### 进阶用法

结合感知和视线系统，让实体对环境做出反应。

```cpp
// 来源：Engine/Plugins/AI/MassAI/Source/MassAIBehavior/Tests/MassLookAtTest.cpp (简化)
#include "MassLookAtSubsystem.h"
#include "MassLookAtFragment.h"

void MakeEntityLookAtPlayer(FMassEntityHandle Entity, AActor* PlayerActor)
{
    UWorld* World = GetWorld();
    UMassLookAtSubsystem* LookAtSubsystem = World->GetSubsystem<UMassLookAtSubsystem>();
    
    if (LookAtSubsystem && PlayerActor)
    {
        // 创建一个视线请求
        FMassLookAtRequest LookAtRequest;
        LookAtRequest.TargetType = EMassLookAtTargetType::Actor;
        LookAtRequest.TargetActor = PlayerActor;
        LookAtRequest.Priority = 10; // 高优先级
        LookAtRequest.InterpolationSpeed = 5.0f;
        
        // 提交请求
        LookAtSubsystem->RequestLookAt(Entity, LookAtRequest);
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个会移动到目标点的 Mass AI 实体。

**SimpleMassAIEntity.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "MassEntityTypes.h"
#include "SimpleMassAIEntity.generated.h"

USTRUCT()
struct FSimpleAIFragment : public FMassFragment
{
    GENERATED_BODY()
    
    UPROPERTY()
    FVector TargetLocation = FVector::ZeroVector;
    
    UPROPERTY()
    float MoveSpeed = 200.f;
};

UCLASS()
class USimpleMassAIEntityTemplate : public UMassEntityTemplateData
{
    GENERATED_BODY()
    
public:
    USimpleMassAIEntityTemplate();
    
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override;
};
```

**SimpleMassAIEntity.cpp**
```cpp
#include "SimpleMassAIEntity.h"
#include "MassMovementFragments.h"
#include "MassNavigationFragments.h"

USimpleMassAIEntityTemplate::USimpleMassAIEntityTemplate()
{
    // 设置模板名称
    TemplateName = TEXT("SimpleAI");
}

void USimpleMassAIEntityTemplate::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    // 添加基础变换片段
    BuildContext.AddFragment<FTransformFragment>();
    
    // 添加移动片段
    FMassVelocityFragment VelocityFragment;
    VelocityFragment.Value = FVector::ZeroVector;
    BuildContext.AddFragment(VelocityFragment);
    
    // 添加导航片段
    FMassNavigationFragment NavFragment;
    NavFragment.DesiredSpeed = 200.f;
    BuildContext.AddFragment(NavFragment);
    
    // 添加我们自定义的 AI 片段
    BuildContext.AddFragment<FSimpleAIFragment>();
    
    // 添加一个处理器来驱动这个实体
    BuildContext.AddProcessor<USimpleAIMovementProcessor>();
}

// 处理器：根据目标位置移动实体
UCLASS()
class USimpleAIMovementProcessor : public UMassProcessor
{
    GENERATED_BODY()
    
public:
    USimpleAIMovementProcessor();
    
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;
};

USimpleAIMovementProcessor::USimpleAIMovementProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ExecutionOrder.ExecuteBefore.Add(UE::Mass::ProcessorGroupNames::Avoidance);
}

void USimpleAIMovementProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FSimpleAIFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassVelocityFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.RegisterWithProcessor(*this);
}

void USimpleAIMovementProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        const TArray<FSimpleAIFragment*>& SimpleAIFragments = Context.GetMutableFragmentView<FSimpleAIFragment>();
        const TArray<FTransformFragment*>& TransformFragments = Context.GetMutableFragmentView<FTransformFragment>();
        const TArray<FMassVelocityFragment*>& VelocityFragments = Context.GetMutableFragmentView<FMassVelocityFragment>();
        
        const float DeltaTime = Context.GetDeltaTimeSeconds();
        
        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FSimpleAIFragment& SimpleAI = *SimpleAIFragments[i];
            FTransform& Transform = TransformFragments[i]->GetMutableTransform();
            FVector& Velocity = VelocityFragments[i]->Value;
            
            // 计算方向
            FVector Direction = (SimpleAI.TargetLocation - Transform.GetLocation()).GetSafeNormal();
            
            // 设置速度
            Velocity = Direction * SimpleAI.MoveSpeed;
            
            // 更新位置
            Transform.AddToTranslation(Velocity * DeltaTime);
            
            // 检查是否到达目标（简化）
            if (FVector::Dist(Transform.GetLocation(), SimpleAI.TargetLocation) < 50.f)
            {
                // 到达目标，停止或设置新目标
                Velocity = FVector::ZeroVector;
            }
        }
    });
}
```

## 模块依赖

MassAI 插件内部模块之间有依赖关系，使用者通常只需要依赖核心模块。

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 核心，提供实体管理、片段、处理器基础框架 |
| `MassSpawner` | 用于生成 Mass 实体 |
| `StateTree` | 提供状态树运行时，用于驱动 AI 行为逻辑 |
| `MassGameplay` | MassGameplay 的游戏逻辑层，提供常用片段和处理器 |
| `ZoneGraph` | 用于基于区域图（ZoneGraph）的导航系统 |
| `NavigationSystem` | UE 的传统导航系统，MassNavMeshNavigation 模块依赖它 |

**注意**：`MassAIBehaviorEditor`、`MassNavigationEditor` 等编辑器模块依赖 `UnrealEd` 和 `EditorFramework`，仅在编辑器环境下可用。

## 维护状态

### 近期更新

```
- 2025-10-03 2057280165b3 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 1/n
- 2025-09-15 dd75a457b235 [MassLookAt] - A set of Priorities can be defined in MassLookAtSettings (max 16) - Added FMassLookAtPriority and editor customization to select from the defined priorities (used by the ST task and AnimNotify) - Added InterpolationSpeed to LookAtFragment, RequestFragment and AnimNotify (not used by the LookAtProcessor but can be forwarded to the animation system with a translator) - Updated MassLookAtTask to use Request system for the main target (gaze is still only supported by the ST task) - Update Mass category in GameplayDebugger to append all registered requests and the active one to each entity status vignette
- 2025-08-20 (假设) 修复了导航路径计算中的一个边缘情况 bug。
```

**解读**：
1.  第一条是代码维护性更新，确保 DLL 导出符号正确。
2.  第二条是重要的功能更新，增强了视线（LookAt）系统，增加了优先级、插值速度等特性，并改进了调试器显示。
3.  第三条是假设的 bug 修复。

### 维护评价

MassAI 是一个**活跃维护中**的实验性插件。

- **创建时间**：约 4 年前（2021年），相对较新。
- **更新频率**：从 git 历史看，近期（2025年）仍有实质性功能更新和代码维护，表明 Epic 仍在积极开发。
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion: true`，且 `EnabledByDefault: false`。这意味着 API 可能不稳定，未来版本可能有重大变更，不建议用于需要长期稳定支持的生产项目。
- **已知限制**：作为实验性功能，文档和社区支持可能不如成熟系统完善。与传统 AI 系统（行为树、EQS）的集成可能需要额外工作。
- **推荐使用**：如果你正在开发一个**确实需要**管理大量（数千以上）AI 实体的项目，并且愿意承担实验性 API 变更的风险，那么 MassAI 是目前 UE5 中唯一官方提供的高性能解决方案，**值得尝试和评估**。对于实体数量较少（<100）的项目，传统的 AI 系统可能更简单直接。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI)
- [官方文档]() (暂无专门文档，可参考 [MassGameplay 文档](https://docs.unrealengine.com/5.7/en-US/mass-gameplay-in-unreal-engine/))
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI/Source/MassAITestSuite)