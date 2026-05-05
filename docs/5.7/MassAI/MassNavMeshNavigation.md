# MassAI

> AI-specific functionality extending MassGameplay

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 MassGameplay 框架的 AI 扩展插件，为大规模实体（Mass Entity）提供 AI 行为和导航能力。它解决的核心问题是：**如何在数以万计的实体上高效运行 AI 逻辑**。

传统的 AI 系统（如行为树 + 导航网格）为每个 Agent 独立运行，当实体数量达到数千时性能急剧下降。MassAI 利用 ECS（Entity Component System）架构，将 AI 逻辑拆分为可批量处理的处理器（Processor），通过数据驱动的方式实现大规模 AI 行为模拟。

插件包含以下子模块：

| 模块 | 职责 |
|---|---|
| **MassNavigation** | 导航核心框架，定义移动目标、速度、转向等基础片段和处理器 |
| **MassNavMeshNavigation** | 基于 NavMesh 的导航实现，路径跟随和边界计算 |
| **MassZoneGraphNavigation** | 基于 ZoneGraph 的导航实现，用于城市/道路场景 |
| **MassAIBehavior** | AI 行为系统，包括状态机、行为树集成等 |
| **MassAIBehaviorEditor** | 行为系统的编辑器工具 |
| **MassAIDebug** | 调试可视化工具 |
| **MassAIReplication** | 网络同步支持 |
| **MassNavigationEditor** | 导航编辑器工具 |
| **MassAITestSuite** | 自动化测试套件 |

## 使用场景

- 你在做一个大型开放世界游戏，需要数千个 NPC 同时在城市中行走 → 用 MassAI + ZoneGraph Navigation
- 你需要模拟大规模战斗，数千个士兵需要寻路和避障 → 用 MassAI + NavMesh Navigation
- 你在做 RTS 游戏，大量单位需要高效移动 → 用 MassNavigation 核心模块
- 你需要为 Mass 实体添加简单的行为状态机 → 用 MassAIBehavior
- 你需要调试大量实体的导航行为 → 用 MassAIDebug 的可视化工具

## 模块概览

本插件包含 9 个模块，按功能分为 4 个领域：

### 导航系统

| 模块 | 说明 |
|---|---|
| [MassNavigation](#massnavigation) | 导航核心：移动目标、速度、转向、避障 |
| [MassNavMeshNavigation](#massnavmeshnavigation) | NavMesh 导航：路径跟随、边界计算 |
| [MassZoneGraphNavigation](#masszonegraphnavigation) | ZoneGraph 导航：道路/人行道网络 |

### 行为系统

| 模块 | 说明 |
|---|---|
| [MassAIBehavior](#massaibehavior) | AI 行为：状态机、行为树集成 |
| [MassAIBehaviorEditor](#massaibehavioreditor) | 行为编辑器工具 |

### 基础设施

| 模块 | 说明 |
|---|---|
| [MassAIDebug](#massaidebug) | 调试可视化 |
| [MassAIReplication](#massaireplication) | 网络同步 |
| [MassNavigationEditor](#massnavigationeditor) | 导航编辑器工具 |
| [MassAITestSuite](#massaitestsuite) | 自动化测试 |

---

## MassNavigation

导航核心模块，定义了 Mass 实体移动的基础片段（Fragment）和处理器（Processor）。

### 核心片段

| 片段 | 说明 |
|---|---|
| `FMassMoveTargetFragment` | 移动目标：目标位置、速度、状态 |
| `FMassVelocityFragment` | 当前速度向量 |
| `FMassNavigationEdgesFragment` | 导航边界（用于避障） |

### 核心处理器

| 处理器 | 说明 |
|---|---|
| `UMassMoveTargetInitializer` | 初始化移动目标 |
| `UMassSteerToMoveTargetProcessor` | 转向移动目标 |
| `UMassAvoidanceProcessor` | 局部避障 |
| `UMassApplyMovementProcessor` | 应用移动到位置 |

---

## MassNavMeshNavigation

基于 NavMesh 的导航实现，处理路径跟随和边界计算。

### 核心片段

#### FMassNavMeshShortPathFragment

短路径片段，存储从 NavMesh 导航走廊（NavCorridor）提取的路径点。

```cpp
USTRUCT()
struct FMassNavMeshShortPathFragment : public FMassFragment
{
    // 最大路径点数量
    static constexpr uint8 MaxPoints = 8;
    
    // 路径点数组
    TStaticArray<FMassNavMeshPathPoint, MaxPoints> Points;
    
    // 当前进度距离
    float MoveTargetProgressDistance = 0.f;
    
    // 到达终点的距离阈值
    float EndReachedDistance = 20.f;
    
    // 路径点数量
    uint8 NumPoints = 0;
    
    // 路径结束时的意图（站立、动画等）
    EMassMovementAction EndOfPathIntent = EMassMovementAction::Stand;
    
    // 是否部分结果
    uint8 bPartialResult : 1 = false;
    
    // 是否完成
    uint8 bDone : 1 = false;
    
    // 是否已初始化
    uint8 bInitialized : 1 = false;
    
    // 从 NavCorridor 请求短路径
    bool RequestShortPath(const TSharedPtr<FNavCorridor>& InCorridor, 
                          const int32 InNavCorridorStartIndex, 
                          const uint8 InNumLeadingPoints, 
                          const float InEndReachedDistance);
};
```

#### FMassNavMeshPathPoint

路径点数据结构：

```cpp
USTRUCT()
struct FMassNavMeshPathPoint
{
    // 传送门左边界
    FVector Left = FVector::ZeroVector;
    
    // 传送门右边界
    FVector Right = FVector::ZeroVector;
    
    // 路径位置
    FVector Position = FVector::ZeroVector;
    
    // 路径切线方向（压缩格式）
    FMassSnorm8Vector2D Tangent;
    
    // 距离路径起点的距离
    FMassInt16Real Distance = FMassInt16Real(0.f);
};
```

### 核心处理器

#### UMassNavMeshPathFollowProcessor

路径跟随处理器，更新移动目标以跟随 NavMesh 短路径。

```cpp
UCLASS(MinimalAPI)
class UMassNavMeshPathFollowProcessor : public UMassProcessor
{
    // 配置查询条件
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    
    // 初始化（获取 SignalSubsystem）
    virtual void InitializeInternal(UObject& Owner, const TSharedRef<FMassEntityManager>&) override;
    
    // 执行路径跟随逻辑
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;
};
```

#### UMassNavMeshNavigationBoundaryProcessor

边界处理器，从短路径片段填充导航边界片段。

```cpp
UCLASS(MinimalAPI)
class UMassNavMeshNavigationBoundaryProcessor : public UMassProcessor
{
    // 配置查询条件
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    
    // 执行边界计算
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;
};
```

### Trait

#### UMassNavMeshNavigationTrait

NavMesh 导航特性，用于在实体模板中启用 NavMesh 导航。

```cpp
UCLASS(MinimalAPI, meta = (DisplayName = "NavMesh Navigation"))
class UMassNavMeshNavigationTrait : public UMassEntityTraitBase
{
    // 构建实体模板
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override;
};
```

### 工具函数

```cpp
namespace UE::MassNavigation
{
    // 激活站立动作
    bool ActivateActionStand(const UObject* Requester, 
                             const FMassEntityHandle Entity, 
                             const float DesiredSpeed, 
                             FMassMoveTargetFragment& InOutMoveTarget, 
                             FMassNavMeshShortPathFragment& OutShortPath);
    
    // 激活动画动作
    bool ActivateActionAnimate(const UObject* Requester, 
                               const FMassEntityHandle Entity, 
                               FMassMoveTargetFragment& MoveTarget);
};
```

---

## MassZoneGraphNavigation

基于 ZoneGraph 的导航实现，适用于城市/道路场景。

ZoneGraph 是 UE5 的区域图系统，定义了道路、人行道等导航区域。MassZoneGraphNavigation 将 Mass 实体与 ZoneGraph 集成，实现高效的路径规划。

### 核心功能

- ZoneGraph 路径查询
- 路径跟随
- 交叉口处理
- 车道切换

---

## MassAIBehavior

AI 行为系统模块，为 Mass 实体提供行为逻辑。

### 核心功能

- 行为状态机
- 行为树集成
- 感知系统集成
- 决策逻辑

---

## MassAIBehaviorEditor

MassAIBehavior 的编辑器扩展模块。

### 功能

- 行为可视化
- 调试工具
- 编辑器集成

---

## MassAIDebug

调试可视化模块，提供 Mass AI 实体的调试绘制功能。

### 功能

- 导航路径可视化
- 移动目标可视化
- 避障边界可视化
- 行为状态可视化

---

## MassAIReplication

网络同步模块，处理 Mass AI 实体的网络复制。

### 功能

- 位置同步
- 状态同步
- 优化的网络带宽使用

---

## MassNavigationEditor

导航编辑器工具模块。

### 功能

- 导航配置编辑
- 可视化工具
- 调试辅助

---

## MassAITestSuite

自动化测试套件，包含 MassAI 各模块的单元测试和集成测试。

### 测试覆盖

- 导航路径计算
- 路径跟随逻辑
- 避障算法
- 行为状态机

---

## 蓝图用法

MassAI 主要通过 MassEntity 框架的 Trait 系统使用，而非传统的蓝图节点。

### 核心 Trait

| Trait | 说明 | 所在模块 |
|---|---|---|
| `UMassNavMeshNavigationTrait` | 启用 NavMesh 导航 | MassNavMeshNavigation |
| `UMassZoneGraphNavigationTrait` | 启用 ZoneGraph 导航 | MassZoneGraphNavigation |

### 使用示例（蓝图描述）

1. **创建实体模板**：
   - 在 MassEntitySpawner 或 DataAsset 中创建实体模板
   - 添加 `UMassNavMeshNavigationTrait` 或 `UMassZoneGraphNavigationTrait`
   - 配置导航参数

2. **配置移动目标**：
   - 通过 `FMassMoveTargetFragment` 设置目标位置
   - 处理器会自动更新路径跟随

3. **调试可视化**：
   - 启用 MassAIDebug 模块
   - 在编辑器中查看导航路径和边界

---

## C++ 用法

### 头文件引入

```cpp
// NavMesh 导航
#include "MassNavMeshNavigationFragments.h"
#include "MassNavMeshNavigationProcessors.h"
#include "MassNavMeshNavigationTrait.h"

// ZoneGraph 导航
#include "MassZoneGraphNavigationFragments.h"

// 核心导航
#include "MassNavigationFragments.h"
```

### 基本用法

#### 1. 请求 NavMesh 短路径

```cpp
#include "MassNavMeshNavigationFragments.h"

// 假设已有 NavCorridor
TSharedPtr<FNavCorridor> NavCorridor = /* ... */;

// 获取实体的短路径片段
FMassNavMeshShortPathFragment& ShortPath = EntityView.GetFragment<FMassNavMeshShortPathFragment>();

// 请求短路径
const int32 StartIndex = 0;
const uint8 NumLeadingPoints = 3;
const float EndReachedDistance = 50.0f;

bool bSuccess = ShortPath.RequestShortPath(
    NavCorridor, 
    StartIndex, 
    NumLeadingPoints, 
    EndReachedDistance
);

if (bSuccess)
{
    // 路径已设置，处理器会自动跟随
    UE_LOG(LogMassNavMeshNavigation, Log, TEXT("Path requested with %d points"), ShortPath.NumPoints);
}
```

#### 2. 激活站立动作

```cpp
#include "MassNavMeshNavigationUtils.h"
#include "MassNavigationFragments.h"

// 获取片段
FMassMoveTargetFragment& MoveTarget = EntityView.GetFragment<FMassMoveTargetFragment>();
FMassNavMeshShortPathFragment& ShortPath = EntityView.GetFragment<FMassNavMeshShortPathFragment>();

// 激活站立
const float DesiredSpeed = 0.0f;
bool bActivated = UE::MassNavigation::ActivateActionStand(
    this,           // Requester
    EntityHandle,   // Entity
    DesiredSpeed,   // DesiredSpeed
    MoveTarget,     // InOutMoveTarget
    ShortPath       // OutShortPath
);
```

#### 3. 激活动画动作

```cpp
#include "MassNavMeshNavigationUtils.h"

FMassMoveTargetFragment& MoveTarget = EntityView.GetFragment<FMassMoveTargetFragment>();

// 激活动画（例如到达目的地后播放动画）
bool bActivated = UE::MassNavigation::ActivateActionAnimate(
    this,           // Requester
    EntityHandle,   // Entity
    MoveTarget      // MoveTarget
);
```

### 进阶用法

#### 自定义导航处理器

```cpp
#include "MassProcessor.h"
#include "MassEntityQuery.h"
#include "MassNavMeshNavigationFragments.h"
#include "MassNavigationFragments.h"

UCLASS()
class UMyCustomNavigationProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyCustomNavigationProcessor()
    {
        // 设置执行顺序，在路径跟随之后执行
        ExecutionOrder.ExecuteAfter.Add(UE::Mass::ProcessorGroupNames::PathFollow);
    }

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override
    {
        // 查询具有短路径和移动目标的实体
        EntityQuery.AddRequirement<FMassNavMeshShortPathFragment>(EMassFragmentAccess::ReadWrite);
        EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadWrite);
        EntityQuery.AddTagRequirement<FMassNavMeshNavigationTag>(EMassFragmentPresence::All);
        
        EntityQuery.RegisterWithProcessor(*this);
    }

    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override
    {
        EntityQuery.ForEachEntityChunk(EntityManager, Context, 
            [this](FMassExecutionContext& Context)
            {
                const int32 NumEntities = Context.GetNumEntities();
                
                auto ShortPathList = Context.GetMutableFragmentView<FMassNavMeshShortPathFragment>();
                auto MoveTargetList = Context.GetMutableFragmentView<FMassMoveTargetFragment>();
                
                for (int32 i = 0; i < NumEntities; ++i)
                {
                    FMassNavMeshShortPathFragment& ShortPath = ShortPathList[i];
                    FMassMoveTargetFragment& MoveTarget = MoveTargetList[i];
                    
                    // 自定义逻辑
                    if (ShortPath.IsDone())
                    {
                        // 路径完成，执行自定义行为
                        HandlePathCompleted(Context.GetEntity(i), MoveTarget);
                    }
                }
            });
    }

private:
    FMassEntityQuery EntityQuery;
    
    void HandlePathCompleted(FMassEntityHandle Entity, FMassMoveTargetFragment& MoveTarget)
    {
        // 自定义完成逻辑
    }
};
```

#### 使用 Trait 配置实体模板

```cpp
#include "MassEntityTemplate.h"
#include "MassNavMeshNavigationTrait.h"

// 在实体生成器中配置模板
void ConfigureEntityTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World)
{
    // 添加 NavMesh 导航 Trait
    UMassNavMeshNavigationTrait* NavMeshTrait = NewObject<UMassNavMeshNavigationTrait>();
    NavMeshTrait->BuildTemplate(BuildContext, World);
    
    // 添加其他 Trait...
}
```

---

## Demo 示例

### 最小 NavMesh 导航示例

#### MyNavMeshAgent.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassEntityTypes.h"
#include "MassNavMeshNavigationFragments.h"
#include "MassNavigationFragments.h"

// 自定义 Agent 标签
USTRUCT()
struct FMyAgentTag : public FMassTag
{
    GENERATED_BODY()
};

// 自定义 Agent 片段
USTRUCT()
struct FMyAgentFragment : public FMassFragment
{
    GENERATED_BODY()
    
    // 目标位置
    FVector TargetLocation = FVector::ZeroVector;
    
    // 移动速度
    float MoveSpeed = 300.0f;
};
```

#### MyNavMeshAgentProcessor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MassEntityQuery.h"
#include "MyNavMeshAgent.h"
#include "MassNavMeshNavigationFragments.h"
#include "MassNavigationFragments.h"

UCLASS()
class UMyNavMeshAgentProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyNavMeshAgentProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

#### MyNavMeshAgentProcessor.cpp

```cpp
#include "MyNavMeshAgentProcessor.h"
#include "MassNavMeshNavigationUtils.h"
#include "MassSignalSubsystem.h"

UMyNavMeshAgentProcessor::UMyNavMeshAgentProcessor()
{
    // 在路径跟随之前执行
    ExecutionOrder.ExecuteBefore.Add(UE::Mass::ProcessorGroupNames::PathFollow);
    bAutoRegisterWithProcessingPhases = true;
}

void UMyNavMeshAgentProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMyAgentFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassNavMeshShortPathFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddTagRequirement<FMyAgentTag>(EMassFragmentPresence::All);
    
    EntityQuery.RegisterWithProcessor(*this);
}

void UMyNavMeshAgentProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context,
        [this](FMassExecutionContext& Context)
        {
            const int32 NumEntities = Context.GetNumEntities();
            
            auto AgentList = Context.GetMutableFragmentView<FMyAgentFragment>();
            auto MoveTargetList = Context.GetMutableFragmentView<FMassMoveTargetFragment>();
            auto ShortPathList = Context.GetMutableFragmentView<FMassNavMeshShortPathFragment>();
            
            for (int32 i = 0; i < NumEntities; ++i)
            {
                FMyAgentFragment& Agent = AgentList[i];
                FMassMoveTargetFragment& MoveTarget = MoveTargetList[i];
                FMassNavMeshShortPathFragment& ShortPath = ShortPathList[i];
                
                // 如果路径已完成，请求新路径
                if (ShortPath.IsDone())
                {
                    // 这里应该调用导航系统请求路径
                    // 简化示例：直接设置移动目标
                    MoveTarget.Center = Agent.TargetLocation;
                    MoveTarget.DesiredSpeed = Agent.MoveSpeed;
                    MoveTarget.CreateNewAction(EMassMovementAction::Move, *Context.GetWorld());
                }
            }
        });
}
```

---

## 模块依赖

### MassNavMeshNavigation

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体框架核心 |
| `MassNavigation` | 导航核心框架 |
| `NavigationSystem` | NavMesh 导航系统 |

### MassZoneGraphNavigation

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体框架核心 |
| `MassNavigation` | 导航核心框架 |
| `ZoneGraph` | 区域图系统 |

### MassAIBehavior

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体框架核心 |
| `MassNavigation` | 导航核心框架 |
| `AIModule` | AI 行为树/感知系统 |

### MassAIDebug

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体框架核心 |
| `MassNavigation` | 导航核心框架 |

### MassAIReplication

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体框架核心 |
| `MassSpawner` | 实体生成器 |

---

## 维护状态

### 近期更新

```
- 457eba2e5782 PR #13332: Added std::is_trivially_copyable to the CFragment concept.
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- b1980471196e [Mass] Minor MassEntityManager cleanup, including removing some header inclusion
```

### 维护评价

**活跃维护中** ✅

- **创建时间**：2021-09-29（约 4 年）
- **最近更新**：近期有代码质量改进和重构
- **维护状态**：作为 Epic 官方维护的 MassGameplay 扩展，持续更新中
- **实验性标记**：仍标记为实验性（IsExperimentalVersion=true），API 可能变化
- **推荐使用**：适合需要大规模 AI 实体的项目，但需注意实验性状态

**注意事项**：
- 插件默认未启用（EnabledByDefault=false），需要手动启用
- 作为实验性功能，API 可能在版本间发生变化
- 需要 MassGameplay 插件作为前置依赖

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI)
- [MassGameplay 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)
- [ZoneGraph 系统](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ZoneGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI/Source/MassAITestSuite)

---

## 子模块文档

由于 MassAI 是 xlarge 规模插件（328 个源文件），各子模块的详细文档请参考：

- [MassNavigation](docs/xlarge/MassAI/MassNavigation.md) - 导航核心框架
- [MassNavMeshNavigation](docs/xlarge/MassAI/MassNavMeshNavigation.md) - NavMesh 导航实现
- [MassZoneGraphNavigation](docs/xlarge/MassAI/MassZoneGraphNavigation.md) - ZoneGraph 导航实现
- [MassAIBehavior](docs/xlarge/MassAI/MassAIBehavior.md) - AI 行为系统
- [MassAIDebug](docs/xlarge/MassAI/MassAIDebug.md) - 调试可视化
- [MassAIReplication](docs/xlarge/MassAI/MassAIReplication.md) - 网络同步