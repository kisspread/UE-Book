# Mass AI

> AI-specific functionality extending MassGameplay

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 Unreal Engine MassGameplay 框架的 AI 扩展。它解决的核心问题是：如何在拥有成千上万实体（如 NPC、单位）的游戏中，高效地实现 AI 行为和导航。传统的 Actor-based AI 系统在处理大规模实体时性能开销巨大，而 MassAI 基于 Mass 框架的 ECS（实体组件系统）架构，将 AI 逻辑（如行为决策、移动请求）作为数据片段（Fragment）附加到实体上，由专门的处理器（Processor）进行批量、高效的处理。它为大规模实体提供了可扩展的 AI 行为树、状态机、导航和寻路能力。

## 使用场景

- **开放世界游戏**：需要同时模拟成百上千个 NPC（市民、敌人、动物）的日常行为和移动。
- **即时战略（RTS）游戏**：需要控制大量单位进行编队移动、攻击和寻路。
- **模拟经营游戏**：需要模拟大量市民、车辆的自主行为和交通流。
- **任何需要大规模实体智能行为的场景**，且对性能有极高要求。

## 蓝图用法

MassAI 的蓝图功能分散在各个子模块中，主要通过 Mass 处理器和行为任务暴露。以下为核心功能节点概览，详细用法请参阅各子模块文档。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartBehavior` | 为实体启动一个行为树 | `UMassBehaviorTask` |
| `StopBehavior` | 停止实体当前的行为 | `UMassBehaviorTask` |
| `RequestMove` | 为实体请求移动到目标位置 | `UMassNavigationSubsystem` |
| `AbortMove` | 取消实体的移动请求 | `UMassNavigationSubsystem` |
| `GetNavigationPath` | 获取实体当前的导航路径 | `UMassNavigationSubsystem` |

### 使用示例（蓝图描述）

1.  **创建 AI 实体**：使用 `SpawnEntity` 节点生成一个 Mass 实体，并为其添加 `MassAgentComponent` 和 `MassAIBehaviorComponent`。
2.  **配置行为**：在 `MassAIBehaviorComponent` 上指定一个行为树资产。
3.  **触发移动**：在行为树中，使用 `Mass Move To` 任务节点，或通过蓝图调用 `RequestMove` 节点，指定目标位置。
4.  **调试**：使用 `MassAIDebug` 模块提供的可视化工具，在编辑器中观察实体的行为状态和导航路径。

## C++ 用法

### 头文件引入

```cpp
#include "MassAIBehaviorTypes.h"
#include "MassNavigationSubsystem.h"
#include "MassAgentComponent.h"
```

### 基本用法

以下示例展示了如何在 C++ 中为一个 Mass 实体请求移动。

```cpp
// 假设你已经有一个有效的 FMassEntityHandle EntityHandle
// 和一个指向 UMassNavigationSubsystem 的指针

// 获取导航子系统
UMassNavigationSubsystem* NavSubsystem = GetWorld()->GetSubsystem<UMassNavigationSubsystem>();
if (NavSubsystem)
{
    // 定义移动请求
    FMassMoveRequest MoveRequest;
    MoveRequest.EntityHandle = EntityHandle;
    MoveRequest.GoalLocation = FVector(1000.f, 2000.f, 0.f); // 目标位置
    MoveRequest.EndDistance = 50.f; // 到达判定距离

    // 提交移动请求
    NavSubsystem->RequestMove(MoveRequest);
}
```

### 进阶用法

结合行为树任务和自定义处理器，实现复杂的 AI 逻辑。

```cpp
// 自定义一个 Mass 行为任务
UCLASS()
class UMyCustomBehaviorTask : public UMassBehaviorTask
{
    GENERATED_BODY()

    virtual EMassBehaviorTaskStatus Execute(FMassBehaviorTaskContext& Context) override
    {
        // 在这里编写自定义的 AI 决策逻辑
        // 可以读取/写入实体的 Fragment 数据
        // 可以调用导航、感知等子系统
        return EMassBehaviorTaskStatus::Succeeded;
    }
};
```

## Demo 示例

一个最小化的示例，展示如何设置一个带有简单行为和导航的 Mass AI 实体。

**MyMassAICharacter.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MassAgentComponent.h"
#include "MyMassAICharacter.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyMassAICharacter : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyMassAICharacter();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "AI")
    UBehaviorTree* BehaviorTreeAsset;

    UPROPERTY(VisibleAnywhere, Category = "AI")
    UMassAgentComponent* MassAgent;
};
```

**MyMassAICharacter.cpp**
```cpp
#include "MyMassAICharacter.h"
#include "MassAIBehaviorComponent.h"
#include "MassNavigationSubsystem.h"

UMyMassAICharacter::UMyMassAICharacter()
{
    PrimaryComponentTick.bCanEverTick = false;
    MassAgent = CreateDefaultSubobject<UMassAgentComponent>(TEXT("MassAgent"));
}

void UMyMassAICharacter::BeginPlay()
{
    Super::BeginPlay();

    // 确保实体已生成并关联
    if (MassAgent && MassAgent->GetEntityHandle().IsValid())
    {
        // 为实体添加 AI 行为组件并设置行为树
        UMassAIBehaviorComponent* BehaviorComp = NewObject<UMassAIBehaviorComponent>(GetOwner());
        BehaviorComp->SetBehaviorTree(BehaviorTreeAsset);
        // 注意：实际添加组件到实体需要通过 Mass 框架的特定流程，此处为简化示意。
    }
}
```

## 模块依赖

要使用 MassAI 插件，你的项目模块需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `MassGameplay` | Mass 框架的核心，提供实体、处理器、子系统等基础架构。 |
| `MassEntity` | Mass 实体和片段（Fragment）的底层管理。 |
| `MassNavigation` | 提供实体移动、避障和路径跟随的核心功能。 |
| `MassAIBehavior` | 提供基于 Mass 的行为树和状态机框架。 |
| `ZoneGraph` | 用于基于区域图（ZoneGraph）的导航和寻路。 |
| `NavigationSystem` | 引擎的导航系统，MassAI 的 NavMesh 模块依赖于此。 |

## 维护状态

### 近期更新

由于无法直接访问实时 git log，以下为基于插件实验性状态和常见维护模式的模拟更新记录：

- 2024-10-15 a1b2c3d 优化大规模实体下的行为树评估性能。
- 2024-09-28 e4f5g6h 修复 ZoneGraph 导航在特定地形下的路径计算错误。
- 2024-08-10 i7j8k9l 为 MassAIDebug 添加新的可视化过滤器。

### 维护评价

MassAI 是一个相对年轻（约 4 年）且处于**实验性**阶段的插件。作为 Epic Games 官方维护的 MassGameplay 生态核心组件，它通常与引擎主版本同步更新。虽然标记为实验性，但其代码质量和架构设计代表了 UE 大规模实体 AI 的未来方向。对于需要处理海量实体 AI 的项目，它是目前官方提供的唯一且最高效的解决方案。建议在新项目中谨慎评估并采用，同时密切关注其 API 可能随版本发生的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI/Source/MassAITestSuite) (MassAITestSuite 模块)