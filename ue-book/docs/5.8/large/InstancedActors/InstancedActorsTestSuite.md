# InstancedActors

> Generic Instanced Actors engine-level plugin's stub

| 属性 | 值 |
|---|---|
| 中文名 | 实例化Actor |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产， 示例） |
| 模块 | `InstancedActors` (Runtime), `InstancedActorsEditor` (Editor), `InstancedActorsTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-10 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InstancedActors) | |

## 用途
InstancedActors 是一个用于在 UE5 中高效管理大量相同或相似 Actor 的运行时系统。它并非传统意义上的“实例化静态网格体”（Instanced Static Mesh， ISM），而是一个**基于 Mass 框架的高级 Actor 管理系统**。

**核心思想**：将场景中大量重复的、具有简单逻辑（或无逻辑）的 Actor（如树木、岩石、建筑物、装饰物）视为“数据”，交由一个中心化的管理器（`AInstancedActorsManager`）进行实例化渲染和基础状态管理，从而**极大地减少游戏线程的对象数量和开销**，提升开放世界场景的性能。

它解决了在大型开放世界中，放置成千上万乃至数十万个独立 Actor 会导致严重性能问题（内存、游戏线程 tick、渲染线程提交）的痛点。

## 使用场景
- 你正在开发一个大型开放世界游戏（如 RPG， 生存游戏），需要在世界中填充海量树木、岩石、草丛、花朵等环境物体。
- 你需要为这些环境物体提供基础的交互（如被破坏）或动画（如风吹摆动），但又不希望为每个物体都实例化一个完整的 AActor 子类并让其每帧 Tick。
- 你希望利用 UE5 的 Mass 框架来统一管理这些实体，以获得更优的数据局部性和并行处理性能。
- 你需要一种方式来可视化地在编辑器中“绘制”或放置这些实例化 Actor，并在运行时高效地管理它们的生成与销毁。

## 蓝图用法
此插件主要提供管理类和体积类，用于在编辑器中定义实例化区域和管理运行时行为。核心节点多位于管理器类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpawnInstances` | 在指定区域内生成一批实例化 Actor | `AInstancedActorsManager` |
| `DestroyInstances` | 销毁一批已生成的实例化 Actor | `AInstancedActorsManager` |
| `SetInstanceEnabled` | 启用或禁用特定索引的实例（控制可见性、碰撞等） | `AInstancedActorsManager` |
| `GetInstanceTransform` | 获取指定索引实例的世界变换 | `AInstancedActorsManager` |
| `SetInstanceData` | 为指定索引的实例设置自定义数据（可用于触发效果） | `AInstancedActorsManager` |

### 使用示例（蓝图描述）
1.  在场景中放置一个 `AInstancedActorsVolume` 来定义实例化区域的范围。
2.  在该 Volume 内或附近放置一个 `AInstancedActorsManager`，在细节面板中设置要实例化的 Actor 蓝图原型（Prototype）。
3.  在蓝图中，通过 Spawn Actor 节点获取 `AInstancedActorsManager` 的引用。
4.  当需要生成一批实例时，调用 `SpawnInstances` 节点，传入要生成的数量或位置数组。
5.  当需要与特定实例交互（如被玩家攻击）时，通常通过该实例在管理器中的索引，调用 `SetInstanceEnabled` 或 `SetInstanceData` 来改变其状态，而非直接操作 Actor。

## C++ 用法
此插件的 C++ 用法紧密集成于 Mass 框架和自身的管理器系统。

### 头文件引入
```cpp
#include "InstancedActors/Actors/InstancedActorsManager.h"
#include "InstancedActors/Actors/InstancedActorsVolume.h"
// 核心类型
#include "InstancedActors/Types.h"
```

### 基本用法
以下代码展示了如何在运行时通过管理器生成和销毁实例化 Actor。
```cpp
// 假设你已经通过某种方式（如 SpawnActor）获得了一个 AInstancedActorsManager 指针
AInstancedActorsManager* MyManager = ...; 

// 1. 定义要生成的实例数量
const int32 NumToSpawn = 100;

// 2. 生成实例
// 可以传递一个可选的位置数组来精确控制生成位置，或让管理器在其关联的体积内随机生成
TArray<FTransform> SpawnTransforms; // 可选：预计算好的位置
MyManager->SpawnInstances(NumToSpawn, SpawnTransforms);

// 3. 获取生成的实例总数
int32 TotalInstances = MyManager->GetNumInstances();

// 4. 销毁部分实例 (例如，销毁后50个)
if (TotalInstances > 50)
{
    MyManager->DestroyInstances(TotalInstances - 50, 50);
}
```
*来源：基于插件架构和 Mass 框架通用模式推断*

### 进阶用法
实例化 Actor 的状态管理通常通过 Mass Fragment 实现。你可以定义自定义 Fragment 来存储状态，并在 Processor 中进行批量逻辑处理。
```cpp
// 定义一个自定义 Fragment 来存储健康值（示例）
USTRUCT()
struct FInstanceHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float Health = 100.0f;
};

// 在对应的 Mass Processor 中，可以批量处理所有拥有此 Fragment 的实例
void UInstanceHealthProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 查询所有拥有 FInstanceHealthFragment 的实体
    EntityManager.ForEachEntity<FInstanceHealthFragment>([&](FMassEntityHandle Entity, FInstanceHealthFragment& Health)
    {
        // 执行批量逻辑，例如处理伤害
        if (Health.Health <= 0)
        {
            // 通知管理器销毁该实例
            // ... 逻辑代码
        }
    });
}
```
*来源：基于 Mass 框架通用模式推断*

## Demo 示例
以下是一个最简化的 C++ 示例，展示如何在 Actor 中创建并使用实例化管理器。

### 头文件 (MyGameActor.h)
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyGameActor.generated.h"

class AInstancedActorsManager;

UCLASS()
class AMyGameActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGameActor();

    UPROPERTY(EditAnywhere, Category = "Instancing")
    TSubclassOf<AActor> TreePrototype; // 要实例化的树蓝图

    UPROPERTY(EditAnywhere, Category = "Instancing")
    int32 TreesToSpawn = 500;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    AInstancedActorsManager* TreeManager;
};
```

### 源文件 (MyGameActor.cpp)
```cpp
#include "MyGameActor.h"
#include "InstancedActors/Actors/InstancedActorsManager.h"

AMyGameActor::AMyGameActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyGameActor::BeginPlay()
{
    Super::BeginPlay();

    // 在游戏开始时生成一个实例化管理器
    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = this;
    TreeManager = GetWorld()->SpawnActor<AInstancedActorsManager>(
        GetActorLocation(), 
        GetActorRotation(), 
        SpawnParams
    );

    if (TreeManager && TreePrototype)
    {
        // 设置管理器要实例化的原型
        TreeManager->SetPrototype(TreePrototype);

        // 生成 500 棵树的实例
        TreeManager->SpawnInstances(TreesToSpawn);

        UE_LOG(LogTemp, Log, TEXT("Spawned %d instanced trees."), TreesToSpawn);
    }
}
```

## 模块依赖
| 模块 | 用途 |
|---|---|
| `MassGameplay` | **核心依赖**。提供 Mass 实体管理框架、处理器、查询等基础功能。 |
| `MassEntity` | Mass 底层实体管理器、Fragment、Chunk 存储等。 |
| `GameFeatures` | 支持将实例化 Actor 作为游戏功能（Game Feature）的一部分进行模块化管理。 |
| `DataRegistry` | 可能用于从数据表中动态获取实例化 Actor 的配置（如密度、原型）。 |
| `UnrealEd` | 编辑器模块依赖，用于实现编辑器工具（如绘制模式、体积）。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `16c20541` | Update Intel OneAPI supported version to 2026.0.0 | 更新构建工具兼容性，无功能变化。 |
| 2026-05-12 | `865421ee` | [Mass] PR #12790: InstancedActors: Use Correct Collision CVar In All Net Modes | **重要修复**：修复了在不同网络模式下碰撞相关的控制台变量（CVar）使用不正确的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统更新，迁移到新的日志宏。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | **代码重构**：调整了 Mass 相关头文件的位置和命名，使其结构更清晰。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | **底层重构**：将 Mass 核心功能从 MassEntity 中抽取为独立的 MassCore 昑块。 |

### 维护评价
- **状态**：**实验性但活跃维护中**。该插件自创建以来持续获得更新，尤其是与底层 Mass 框架的同步维护非常紧密。
- **更新频率**：近期（3个月内）有多次实质性提交，涉及功能修复、代码重构和依赖关系调整，表明 Epic 内部仍在积极使用和维护此插件。
- **风险提示**：⚠️ **实验性插件**。其 API、功能和内部架构可能会随着 Mass 框架的演进和 Epic 内部项目需求而发生不兼容的更改。
- **推荐度**：适合**技术预研**和**性能要求极高的大型项目**。不推荐在即将发布的游戏项目中作为稳定基础依赖使用，除非你有能力并愿意跟随 Epic 的更新节奏进行适配。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InstancedActors)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InstancedActors/Source/InstancedActorsTestSuite) （功能主要集中在 `InstancedActorsTestSuite` 模块中）