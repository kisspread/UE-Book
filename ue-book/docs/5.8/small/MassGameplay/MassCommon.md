# Mass Gameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 插件并非一个独立的游戏框架，而是基于 UE5 的 MassEntity 框架，为大规模（数以万计）智能体（Agent）的模拟提供通用游戏玩法支持功能的集合。它解决了在使用 MassEntity（一种面向数据的高性能 ECS 架构）构建游戏时，如何高效实现角色运动、渲染、LOD、网络复制、与世界对象交互等核心游戏逻辑的问题。它是连接底层 MassEntity 框架与具体游戏项目逻辑的桥梁。

## 使用场景

- 你正在开发一个需要成千上万个动态单位（如 RTS 游戏的士兵、模拟城市的市民）的游戏 → 使用 MassGameplay 来管理它们的移动、显示和行为。
- 你需要为大量 AI 角色实现高效的感知、寻路和交互逻辑 → 可以使用 MassEQS、MassSmartObjects 等模块。
- 你需要处理大量角色的细节层次（LOD）和网络状态同步，以优化性能 → 使用 MassLOD 和 MassReplication。

## 蓝图用法

MassGameplay 的大部分功能通过其 C++ 框架和配置实现，直接在蓝图中暴露的节点相对有限，主要集中在配置和调试层面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （暂无直接查询到的 BlueprintCallable 节点） | | |

### 使用示例（蓝图描述）

该插件主要用于 C++ 层面和项目配置。在蓝图中，你可以通过“项目设置”来配置 Mass Gameplay 的行为，例如在 `Mass` 分类下可以找到 `UMassGameplaySettings`，其中可以配置是否记录生成位置等调试选项。

## C++ 用法

### 头文件引入

```cpp
#include "MassCommonTypes.h"
#include "MassCommonFragments.h"
#include "RandomSequence.h"
#include "MassCommonUtils.h"
```

### 基本用法

MassCommon 模块提供了大量用于 ECS 数据存储的压缩类型，以节省内存。

```cpp
// 1. 使用压缩类型存储位置和方向（源自 MassCommonTypes.h）
// 假设这是你的一个 Mass Fragment（数据块）
USTRUCT()
struct FMyMovementFragment : public FMassFragment
{
    GENERATED_BODY()
    
    // 存储一个以厘米为单位的浮点数，占用 2 字节而非 4 字节
    FMassInt16Real Speed;
    
    // 存储一个归一化的方向向量（-1到1），占用 3 字节
    FMassSnorm8Vector Direction;
    
    // 存储一个大范围的位置坐标（精度 1cm），占用 6 字节 (int16 x3)
    FMassInt16Vector WorldPosition;
};

// 2. 使用序列化随机数（源自 RandomSequence.h）
// 在大规模模拟中，为了可重现性和性能，常使用基于索引的随机数
int32 EntityIndex = 42;
float RandomValue = UE::RandomSequence::FRand(EntityIndex); // 0.0 到 1.0
int32 RandomIntInRange = UE::RandomSequence::RandRange(EntityIndex, 0, 100); // 0 到 100
```

*来源文件：Engine/Plugins/Runtime/MassGameplay/Source/MassCommon/Public/MassCommonTypes.h, RandomSequence.h*

### 进阶用法

结合确定性模拟工具和实体句柄管理。

```cpp
// 3. 在确定性模式下运行（用于网络同步或测试）（源自 MassCommonUtils.h）
if (UE::Mass::Utils::IsDeterministic())
{
    // 在确定性模式下，系统会使用固定的随机种子
    int32 Seed = 12345;
    int32 OverriddenSeed = UE::Mass::Utils::OverrideRandomSeedForTesting(Seed); // 可能被项目设置覆盖
    int32 DeterministicRandom = UE::Mass::Utils::GenerateRandomSeed(); // 使用确定性随机数生成器
}

// 4. 管理实体句柄（源自 MassCommonUtils.h）
// Mass 实体通过 FMassEntityHandle 标识，有时需要从线程安全队列中转换格式
TQueue<FMassEntityHandle, EQueueMode::Mpsc> EntityQueue;
// ... (将实体放入队列)
int32 Count = 10;
TArray<FMassEntityHandle> EntityArray = UE::Mass::Utils::EntityQueueToArray(EntityQueue, Count);
// 现在可以用 EntityArray 进行批量处理
```

*来源文件：Engine/Plugins/Runtime/MassGameplay/Source/MassCommon/Public/MassCommonUtils.h*

## Demo 示例

一个使用 MassCommon 中压缩类型的最小 Fragment 定义示例。

```cpp
// MyMassTypes.h
#pragma once

#include "CoreMinimal.h"
#include "MassEntityTypes.h"
#include "MassCommonTypes.h"
#include "MassCommonFragments.h"
#include "MyMassTypes.generated.h"

/**
 * 一个示例 Fragment，使用 MassCommon 的压缩类型来高效存储一个智能体的基本状态。
 */
USTRUCT()
struct FMyAgentStateFragment : public FMassFragment
{
    GENERATED_BODY()

    // 智能体的移动速度，精度 1cm/s，存为 int16
    FMassInt16Real CurrentSpeed;

    // 智能体的朝向（归一化 2D 方向），存为 2 个字节
    FMassSnorm8Vector2D FacingDirection;

    // 智能体的生命值百分比 (0.0 到 1.0)，存为 uint8
    FMassUnorm8Real HealthPercent;

    // 智能体的基础尺寸（半径和高度），来自 MassCommonFragments
    FAgentRadiusFragment RadiusData;
    FAgentHeightFragment HeightData;

    /** 默认构造 */
    FMyAgentStateFragment() = default;

    /** 从普通类型构造，用于初始化 */
    FMyAgentStateFragment(float InSpeed, const FVector& InDirection, float InHealth, float InRadius, float InHeight)
        : CurrentSpeed(InSpeed)
        , FacingDirection(FVector2D(InDirection))
        , HealthPercent(InHealth)
    {
        RadiusData.Radius = InRadius;
        HeightData.Height = InHeight;
    }
};
```

```cpp
// MyMassProcessor.cpp (片段)
#include "MyMassTypes.h"
#include "MassExecutionContext.h"

// 假设这是处理所有 MyAgentStateFragment 的 Processor 的一部分
void UMyMovementProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有拥有 FMyAgentStateFragment 的实体
    Context.ForEachEntityChunk([this](FMassExecutionContext& Context)
    {
        // 获取该 Chunk 中所有实体的 FMyAgentStateFragment 数组
        TConstArrayView<FMyAgentStateFragment> StateList = Context.GetFragmentView<FMyAgentStateFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FMyAgentStateFragment& State = StateList[i];
            
            // 获取解压缩后的值进行计算
            float Speed = State.CurrentSpeed.Get(); // 从 int16 解压回 float
            FVector2D Direction = State.FacingDirection.Get(); // 从 2xint8 解压回 FVector2D
            float Health = State.HealthPercent.Get(); // 从 uint8 解压回 float (0-1)
            
            // ... 使用这些值进行移动、决策等逻辑
        }
    });
}
```

## 模块依赖

MassGameplay 包含多个子模块，其中 MassCommon 是最基础的类型和工具模块。使用者通常需要依赖 `MassCommon` 及其他与具体功能相关的模块（如 `MassMovement` 用于移动）。

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心 ECS 框架，提供实体管理、查询和处理器运行时。MassGameplay 构建于其上。 |
| `MassEntityEditor` | MassEntity 的编辑器支持，一些调试模块（如 MassGameplayDebug）会依赖它。 |

*注意：MassGameplay 内部各模块之间（如 MassMovement 可能依赖 MassCommon）也有依赖关系，但这属于插件内部结构。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚对 MassAgentComponent 的先前更改，表明正在进行功能调整或修复引入的问题。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 修复了在禁用实例化静态网格体(ISM)之前等待Actor准备就绪的问题，提高了表现稳定性。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在 Mass 群体中处理非傀儡(non-puppet)Actor的逻辑，增强了系统的兼容性。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了LOD计算器中按查看器路径的一系列潜在 bug，提升了LOD计算的准确性。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | 将两处手动计算 `bDoKeepActorExtraFrame` 的代码改为使用新的引擎API，进行代码优化和统一。 |

### 维护评价

- **创建时间**：2021年9月，历史超过5年。
- **近期活动**：最近一次提交记录在2026年5月，显示**仍在活跃维护**。近期的提交聚焦于 `MassRepresentation` 和 `MassAgentComponent` 的 bug 修复、功能回滚与优化，表明核心功能模块（如实体表现和代理）仍在持续改进。
- **版本状态**：`.uplugin` 标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，说明**仍然是实验性功能**，可能未经完全验证，API 可能变化。
- **推荐使用**：适用于对大规模实体模拟有明确需求且愿意承担实验性风险的项目。不推荐用于对稳定性要求极高的商业成品项目。建议密切关注更新日志，并在独立分支进行集成测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)（`MassGameplayTestSuite` 模块）