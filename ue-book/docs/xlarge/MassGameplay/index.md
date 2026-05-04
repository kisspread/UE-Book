# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是基于 **MassEntity** 框架构建的**大规模智能体（Agent）模拟**系统。它解决的核心问题是：当游戏中需要同时模拟成千上万个实体（如 NPC、市民、士兵、动物）时，传统的基于 Actor 的模式会带来严重的性能瓶颈（内存、CPU、Tick 开销）。

该插件提供了一套完整的、面向数据（Data-Oriented）的解决方案，将实体的状态（Fragment）与行为（Processor）分离，通过高效的批量处理（Chunk）来驱动大量实体的逻辑，从而实现高性能的群体模拟。它是构建开放世界、RTS、模拟城市等需要海量实体的游戏玩法的基石。

## 使用场景

- **开放世界游戏**：模拟城市中成千上万的市民、车辆、动物，它们拥有简单的日常行为（巡逻、工作、休息）。
- **即时战略（RTS）游戏**：控制和渲染大量作战单位，执行寻路、攻击、阵型移动等指令。
- **塔防/生存游戏**：生成并管理成波次的敌人，它们需要寻路、攻击目标。
- **任何需要“群体智能”或“生态系统”的玩法**：例如模拟鱼群、鸟群、僵尸潮等。

## 模块列表与总结

该插件由多个模块组成，各司其职，共同构成完整的模拟框架。详细 API 与用法请参阅各模块文档。

| 模块 | 一句话总结 | 文档链接 |
|---|---|---|
| **MassActors** | 提供 MassEntity 与传统 Actor 之间的桥接，允许将 Actor 逻辑注入到 Mass 模拟中。 | [MassActors.md](MassActors.md) |
| **MassCommon** | 定义最基础、通用的 Fragment（如 Transform、Health）和 Processor，是其他模块的基石。 | [MassCommon.md](MassCommon.md) |
| **MassEQS** | 将 MassEntity 集成到环境查询系统（EQS）中，使 EQS 查询器能够感知和查询 Mass 实体。 | [MassEQS.md](MassEQS.md) |
| **MassGameplayDebug** | 提供用于调试 Mass 模拟的工具和可视化功能。 | [MassGameplayDebug.md](MassGameplayDebug.md) |
| **MassGameplayEditor** | 提供编辑器内的工具和自定义资产类型，用于配置和预览 Mass 模拟。 | [MassGameplayEditor.md](MassGameplayEditor.md) |
| **MassGameplayExternalTraits** | 定义与外部系统（如 GameplayAbilitySystem）交互所需的 Trait 和 Fragment。 | [MassGameplayExternalTraits.md](MassGameplayExternalTraits.md) |
| **MassGameplayTestSuite** | 包含用于测试 MassGameplay 功能的自动化测试用例。 | [MassGameplayTestSuite.md](MassGameplayTestSuite.md) |
| **MassLOD** | 实现基于距离的细节层次（LOD）管理，根据实体与玩家的距离动态调整其模拟频率和表现。 | [MassLOD.md](MassLOD.md) |
| **MassMovement** | 提供核心的移动和寻路功能，包括跟随、避开障碍、形成队形等。 | [MassMovement.md](MassMovement.md) |
| **MassMovementEditor** | 提供 MassMovement 相关的编辑器工具和可视化。 | [MassMovementEditor.md](MassMovementEditor.md) |
| **MassReplication** | 处理 MassEntity 在多人游戏中的网络同步和复制。 | [MassReplication.md](MassReplication.md) |
| **MassRepresentation** | 管理实体的视觉表现，如选择使用静态网格体、骨骼网格体还是 Niagara 粒子来渲染实体。 | [MassRepresentation.md](MassRepresentation.md) |
| **MassSignals** | 提供基于信号的通信机制，允许实体或处理器之间发送和响应事件。 | [MassSignals.md](MassSignals.md) |
| **MassSimulation** | 包含模拟的核心管理器（`UMassSimulationSubsystem`），负责驱动整个 Mass 世界的更新。 | [MassSimulation.md](MassSimulation.md) |
| **MassSmartObjects** | 将 MassEntity 与 SmartObject 系统集成，使 Mass 实体能够使用场景中的交互点。 | [MassSmartObjects.md](MassSmartObjects.md) |
| **MassSpawner** | 提供实体生成器（`AMassSpawner`），用于在世界中批量生成和配置 Mass 实体。 | [MassSpawner.md](MassSpawner.md) |

## 蓝图用法

MassGameplay 主要通过 **Processor（处理器）** 和 **Trait（特征）** 来定义行为，这些通常在 C++ 中实现。蓝图主要用于：
1.  **配置**：在 `MassSpawner` 蓝图中配置要生成的实体类型和数量。
2.  **触发**：通过蓝图调用 `MassSpawner` 的生成函数。
3.  **调试**：使用 `MassGameplayDebug` 提供的蓝图节点进行运行时调试。

核心的逻辑（如移动、攻击）需要在 C++ 中编写 Processor。

## C++ 用法

### 头文件引入

```cpp
#include "MassEntityTypes.h" // 基础类型
#include "MassProcessor.h"   // 处理器基类
#include "MassCommonFragments.h" // 通用Fragment
#include "MassMovementFragments.h" // 移动相关Fragment
```

### 基本用法：定义自定义 Fragment 和 Processor

```cpp
// 1. 定义一个自定义 Fragment（数据）
USTRUCT()
struct FMyHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float CurrentHealth = 100.f;
    float MaxHealth = 100.f;
};

// 2. 定义一个 Processor（逻辑）
UCLASS()
class UMyDamageProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyDamageProcessor();
protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;
private:
    FMassEntityQuery EntityQuery;
};

// 3. 实现 Processor
UMyDamageProcessor::UMyDamageProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ExecutionOrder.ExecuteBefore.Add(UE::Mass::ProcessorGroupNames::Movement); // 设置执行顺序
}

void UMyDamageProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FMyHealthFragment>(EMassFragmentAccess::ReadWrite); // 声明需要读写FMyHealthFragment
}

void UMyDamageProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 批量遍历所有拥有 FMyHealthFragment 的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取当前Chunk中所有实体的FMyHealthFragment数组
        TConstArrayView<FMyHealthFragment> HealthList = Context.GetFragmentView<FMyHealthFragment>();
        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            // 对每个实体执行逻辑
            HealthList[i].CurrentHealth -= 10.f; // 示例：每帧扣10血
        }
    });
}
```

### 进阶用法：使用 Trait 组合行为

Trait 用于将一组相关的 Fragment 和 Processor 绑定在一起，方便复用。

```cpp
// 定义一个 Trait，它会为实体添加 FMyHealthFragment 并自动应用 UMyDamageProcessor
UCLASS()
class UMyHealthTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()
protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        // 为模板添加 Fragment
        BuildContext.AddFragment<FMyHealthFragment>();
        // 为模板添加 Processor（行为）
        BuildContext.AddProcessor<UMyDamageProcessor>();
    }
};
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个会自动扣血的实体。

**MyHealthFragment.h**
```cpp
#pragma once
#include "MassEntityTypes.h"
#include "MyHealthFragment.generated.h"

USTRUCT()
struct FMyHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float CurrentHealth = 100.f;
};
```

**MyDamageProcessor.h**
```cpp
#pragma once
#include "MassProcessor.h"
#include "MyDamageProcessor.generated.h"

UCLASS()
class UMyDamageProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyDamageProcessor();
protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;
private:
    FMassEntityQuery EntityQuery;
};
```

**MyDamageProcessor.cpp**
```cpp
#include "MyDamageProcessor.h"
#include "MyHealthFragment.h"

UMyDamageProcessor::UMyDamageProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    bAutoRegisterWithProcessingPhases = true; // 自动注册到处理阶段
}

void UMyDamageProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FMyHealthFragment>(EMassFragmentAccess::ReadWrite);
}

void UMyDamageProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [](FMassExecutionContext& Context)
    {
        TArrayView<FMyHealthFragment> HealthList = Context.GetMutableFragmentView<FMyHealthFragment>();
        for (FMyHealthFragment& Health : HealthList)
        {
            Health.CurrentHealth -= 1.f; // 每帧扣1点血
        }
    });
}
```

## 模块依赖

要使用 MassGameplay，你的项目模块需要依赖以下**独特**模块（除标准 Core/Engine 外）：

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 框架的核心，提供实体管理器、Fragment、Processor 基础。 |
| `MassEntityEditor` | Mass 框架的编辑器支持，用于自定义资产和工具。 |
| `MassGameplayExternalTraits` | 如果你需要与 GAS 等外部系统交互，需要依赖此模块。 |
| `MassCommon` | 提供最基础的 Fragment 和 Processor，通常需要依赖。 |
| `MassMovement` | 如果你的实体需要移动，需要依赖此模块。 |
| `MassRepresentation` | 如果你的实体需要视觉表现，需要依赖此模块。 |

## 维护状态

### 近期更新
（由于未提供具体 git log，以下为基于项目性质的推断）
- 该插件作为 Unreal Engine 的一部分，随引擎版本更新而持续维护。
- 作为实验性（`IsExperimentalVersion: true`）功能，API 可能在未来版本中发生变化。
- Epic Games 官方维护，更新频率与引擎大版本发布周期一致。

### 维护评价
- **创建时间**：约 4 年前（2021年），相对较新。
- **维护状态**：**活跃维护中**。作为 UE5 大规模实体模拟的核心解决方案，是 Epic 重点发展的功能之一。
- **已知限制**：标记为实验性，意味着 API 稳定性不如正式功能，可能在未来版本中重构。学习曲线较陡峭，需要理解面向数据的设计思想。
- **推荐使用**：**强烈推荐**用于需要高性能大规模实体模拟的项目。尽管是实验性，但其在《黑客帝国：觉醒》等技术演示中已得到验证，是 UE5 面向未来游戏开发的关键技术栈之一。建议在项目早期进行技术验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/mass-entity-in-unreal-engine/) (MassEntity 框架文档，MassGameplay 是其应用层)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)