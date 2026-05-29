# MassGameplay（大型插件）

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

---

## 用途

MassGameplay 是 UE5 **Mass Entity 框架**的上层应用插件，将 Mass Entity 的底层 ECS 能力转化为可直接用于游戏的高级功能模块。它解决的核心问题是：**如何用数据驱动的方式模拟和管理大规模（数万甚至数十万）游戏实体**，包括它们的移动、LOD、动画轨迹、网络复制、渲染表示等。

该插件是从原始 MassEntity 插件拆分而来（MassEntity 保留为底层框架，MassGameplay 和 MassAI 分别负责游戏玩法和 AI）。

## 模块概览

| 模块 | 功能 |
|---|---|
| **MassActors** | 将 Actor 包装为 Mass Entity，桥接传统 Actor 和 ECS |
| **MassCharacterTrajectory** | 为实体生成角色轨迹，用于动画预测和驱动 |
| **MassCommon** | 通用 Fragment、Tag 和处理器定义 |
| **MassEQS** | 将环境查询系统（EQS）集成到 Mass 框架 |
| **MassGameplayDebug** | 调试可视化工具 |
| **MassGameplayEditor** | 编辑器扩展和资产类型 |
| **MassGameplayExternalTraits** | 外部系统（SmartObjects 等）的 Trait |
| **MassGameplayTestSuite** | 自动化测试套件 |
| **MassLOD** | 基于距离/屏幕占比的 LOD 管理 |
| **MassMovement** | 通用移动框架（速度、转向、避障） |
| **MassMovementEditor** | 移动模块的编辑器支持 |
| **MassReplication** | 网络复制支持 |
| **MassRepresentation** | Actor/ISM/动画的渲染表示切换 |
| **MassSimulation** | 模拟主循环和更新调度 |
| **MassSmartObjects** | SmartObject 系统集成 |
| **MassSpawner** | 实体生成器（Spawner） |

## 子模块文档

- [MassCharacterTrajectory](MassCharacterTrajectory.md) - 角色轨迹生成模块

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚 MassAgentComponent 的早期修改 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 等待 Actor 就绪后再关闭 ISM |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复 Mass 群体中非傀儡 Actor 的处理 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复 LOD 计算器每个观察者路径中的多个已知 Bug |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | 使用新 API 替换手动计算的 Actor 帧保留逻辑 |

### 维护评价

MassGameplay 虽然标记为实验性且默认禁用，但**仍在活跃维护**。2026 年 5 月有多次实质性更新（Bug 修复、API 改进），表明 Epic 内部有持续使用和开发。作为 Mass Entity 框架的核心应用层，它在 CitySample 等官方演示中被大量使用。

**注意**：此插件标记为实验性 (`IsExperimentalVersion=true`)，API 可能在未来版本中发生不兼容变更。

---

# MassCharacterTrajectory

> 角色轨迹生成模块（MassGameplay 子模块）

| 属性 | 值 |
|---|---|
| 中文名 | 角色轨迹 |
| 分类 | MassGameplay 子模块 |
| 默认启用 | ❌ 否（随 MassGameplay 一起） |
| 包含内容 | ❌ 无 |
| 模块 | `MassCharacterTrajectory` (Runtime) |
| 实验性 | ⚠️ 是（MassGameplay 实验性） |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassCharacterTrajectory) | |

## 用途

MassCharacterTrajectory 为 Mass Entity 实体生成**角色运动轨迹**，主要用于：

1. **动画预测**：为 PoseSearch 等动画系统提供历史+未来轨迹，实现动画混合和匹配
2. **平滑移动**：结合 SpringMovement 实现阻尼平滑的移动效果
3. **轨迹驱动移动**：让实体沿着生成的轨迹移动（而非直接应用速度）

它解决了大规模场景中动画系统需要轨迹输入的问题——为每个 Agent 手动计算轨迹不可行，该模块通过处理器批量生成。

## 使用场景

- **大规模人群动画**：数万个 NPC 的移动动画需要轨迹预测（PoseSearch）
- **Spring 动画混合**：使用弹簧阻尼的平滑移动 + 轨迹驱动动画
- **群体行为动画**：蜂群、军队等大规模实体的动画控制

## 蓝图用法

### 核心 Trait

| Trait | 说明 |
|---|---|
| `UCharacterTrajectoryTrait` | 启用轨迹生成，配置采样参数 |
| `UCharacterTrajectoryMovementTrait` | 用轨迹驱动移动（禁用默认移动） |

### 参数配置（CharacterTrajectoryTrait）

在 Mass Entity Template 中添加 `Character Trajectory Generation` Trait，可配置：

| 参数 | 说明 | 默认值 |
|---|---|---|
| `NumHistorySamples` | 历史采样点数量 | 30 |
| `PredictionSamplingInterval` | 预测采样间隔（秒） | 0.1 |
| `NumPredictionSamples` | 未来预测采样点数量 | 15 |
| `Offset` | 轨迹计算时的额外变换偏移 | Identity |

### 使用示例

1. 创建 Mass Entity Template
2. 添加 `Character Trajectory Generation` Trait
3. 可选：添加 `Character Trajectory Movement` Trait 让实体沿轨迹移动
4. 可选：同时添加 SpringMovement 获得更平滑的轨迹

## C++ 用法

### 头文件引入

```cpp
#include "MassCharacterTrajectoryTrait.h"
#include "MassCharacterTrajectoryFragments.h"
#include "MassCharacterTrajectoryGenerationProcessors.h"
```

### 基本用法 - 自定义处理器读取轨迹

```cpp
// 自定义处理器，读取生成的轨迹数据
UCLASS()
class UMyTrajectoryConsumerProcessor : public UMassProcessor
{
    GENERATED_BODY()
    
public:
    UMyTrajectoryConsumerProcessor()
    {
        ExecutionFlags = (int32)EProcessorExecutionFlags::All;
        ProcessingPhase = EMassProcessingPhase::PostPhysics; // 在轨迹生成之后
    }
    
protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override
    {
        EntityQuery.AddRequirement<FCharacterTrajectoryFragment>(EMassFragmentAccess::ReadOnly);
    }
    
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override
    {
        EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
        {
            const FCharacterTrajectoryFragment* Trajectory = Context.GetFragmentViewPtr<FCharacterTrajectoryFragment>();
            if (Trajectory)
            {
                // 读取轨迹数据
                const FTransformTrajectory& TrajData = Trajectory->Trajectory;
                // ... 使用轨迹
            }
        });
    }
    
private:
    FMassEntityQuery EntityQuery;
};
```

### 进阶用法 - 访问轨迹采样点

```cpp
// FCharacterTrajectoryFragment::Trajectory 包含完整的轨迹数据
// 采样点布局：
// [0 .. NumHistory-2]  : 旧历史采样（负时间）
// [NumHistory-1]       : t=0, 上一帧位置
// [NumHistory]         : t=DeltaTime, 当前帧预测位置
// [NumHistory+1 .. end] : 未来预测采样

const FTransformTrajectory& Trajectory = TrajectoryFragment->Trajectory;
int32 TotalSamples = NumHistorySamples + 1 + NumPredictionSamples;

// 获取当前帧预测位置（即 Samples[NumHistorySamples]）
FTransform CurrentPrediction = Trajectory.Samples[NumHistorySamples];
```

## Demo 示例

### 自定义轨迹消费者处理器

```cpp
// MyTrajectoryProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MassCharacterTrajectoryFragments.h"
#include "MyTrajectoryProcessor.generated.h"

UCLASS()
class MYGAME_API UMyTrajectoryProcessor : public UMassProcessor
{
    GENERATED_BODY()
    
public:
    UMyTrajectoryProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

```cpp
// MyTrajectoryProcessor.cpp
#include "MyTrajectoryProcessor.h"
#include "MassEntityView.h"

UMyTrajectoryProcessor::UMyTrajectoryProcessor()
{
    bAutoRegisterWithProcessingPhases = true;
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EMassProcessingPhase::PostPhysics;
}

void UMyTrajectoryProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FCharacterTrajectoryFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddTagRequirement<FCharacterTrajectoryMovementTag>(FMassTagPresence::Any);
    EntityQuery.RegisterWithProcessor(*this);
}

void UMyTrajectoryProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
    {
        const int32 NumEntities = Context.GetNumEntities();
        const FCharacterTrajectoryFragment* Trajectories = Context.GetFragmentView<FCharacterTrajectoryFragment>().GetData();
        
        for (int32 i = 0; i < NumEntities; ++i)
        {
            const FCharacterTrajectoryFragment& Traj = Trajectories[i];
            
            // 使用轨迹数据（例如发送给动画系统）
            const FTransform& CurrentTransform = Traj.MeshRootWorldTransform;
            const FQuat& SteeringTarget = Traj.SteeringTarget;
            
            // 你的自定义逻辑...
        }
    });
}
```

## 模块依赖

该模块无特殊依赖，仅依赖 Mass Entity 核心框架。

## 维护状态

MassCharacterTrajectory 作为 MassGameplay 的子模块，随 MassGameplay 一起维护。Epic 的 CitySample 和 Matrix 项目大量使用 Mass 框架，该模块得到持续开发。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [MassEntity 基础框架](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassEntity)
- [MassAI 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)