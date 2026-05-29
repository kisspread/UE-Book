# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏对象 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 UE5 大规模实体（MassEntity）框架的核心应用层实现。它解决的核心问题是：**如何在游戏运行时，高效地驱动、模拟和交互成千上万甚至数十万个游戏对象（如NPC、子弹、可破坏环境等）**。

它不是简单的组件堆叠，而是基于 ECS (实体-组件-系统) 架构的 MassEntity 框架，将游戏对象拆解为纯数据（实体与片段），通过批处理和系统化的处理器（Processor）进行更新。此插件为 MassEntity 提供了游戏玩法相关的具体实现，包括：
- **智能体行为与AI**：通过 `MassAI` 模块（属于此插件族）集成行为树和 EQS。
- **移动与物理**：提供基于片段和处理器的移动逻辑。
- **LOD与表现**：管理实体的细节层级（LOD），智能地在 Actor、静态网格实例（ISM）和隐匿之间切换。
- **网络同步**：为大规模实体提供复制方案。
- **生成与销毁**：控制实体的生命周期和 Actor 生成预算。
- **调试工具**：在游戏视图中可视化和调试海量实体。

本质上，MassGameplay 是 Epic 为《堡垒之夜》等大型游戏优化的、面向玩法的 ECS 方案。

## 使用场景

- 你在开发一个**开放世界游戏**，需要同时渲染和更新一个城市里的上千名 NPC 和车辆 → 用 MassGameplay 驱动他们的移动和LOD。
- 你正在制作一个**即时战略（RTS）游戏**，需要处理成百上千个单位寻路、战斗和状态更新 → 用 MassMovement 和 MassAI 模块。
- 你的游戏有**大量同质化的可交互对象**（如草地、粒子特效、子弹），需要极致的性能 → 用 MassRepresentation 在 Actor 和纯数据间智能切换。
- 你需要在服务器上**模拟大规模生物群落或物体**，并同步到客户端 → 用 MassReplication。
- 你想**调试和优化**一个包含海量实体的游戏场景 → 用 MassGameplayDebug 模块的可视化工具。

## 蓝图用法

MassGameplay 的蓝图 API 主要通过其核心子系统 `UMassSimulationSubsystem` 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PauseSimulation` | 暂停模拟，所有处理器将不再执行，但相位仍会切换 | `UMassSimulationSubsystem` |
| `ResumeSimulation` | 恢复模拟执行 | `UMassSimulationSubsystem` |
| `IsSimulationPaused` | 查询模拟是否处于暂停状态 | `UMassSimulationSubsystem` |
| `IsSimulationStarted` | 查询模拟是否已启动 | `UMassSimulationSubsystem` |
| `GetOnSimulationPaused` | 获取模拟暂停事件委托（单播） | `UMassSimulationSubsystem` |
| `GetOnSimulationResumed` | 获取模拟恢复事件委托（单播） | `UMassSimulationSubsystem` |
| `GetOnSimulationStarted` | 获取模拟启动事件委托（静态多播） | `UMassSimulationSubsystem` |

### 使用示例（蓝图描述）

1.  **暂停/恢复游戏**：在游戏主菜单打开时，调用 `PauseSimulation`；关闭菜单时，调用 `ResumeSimulation`。这可以暂停所有基于 Mass 的 AI 和物理计算，节省性能。
2.  **监听模拟事件**：在关卡蓝图中，绑定到 `GetOnSimulationStarted` 静态委托，当所有世界的模拟开始时执行全局初始化逻辑。
3.  **游戏状态控制**：在游戏模式（GameMode）中，根据游戏状态（如回合结束）调用 `PauseSimulation` 或 `ResumeSimulation`。

## C++ 用法

### 头文件引入

```cpp
#include "MassSimulationSubsystem.h"
```

### 基本用法

**获取子系统并暂停/恢复模拟** (来自 `MassSimulationSubsystem` 接口设计)
```cpp
// 获取当前世界的 MassSimulation 子系统
UMassSimulationSubsystem* MassSimulation = UWorld::GetSubsystem<UMassSimulationSubsystem>(GetWorld());
if (MassSimulation && MassSimulation->IsSimulationStarted())
{
    // 暂停所有 Mass 处理器
    MassSimulation->PauseSimulation();
    
    // 在一段时间后恢复
    FTimerHandle TimerHandle;
    GetWorldTimerManager().SetTimer(TimerHandle, [MassSimulation]()
    {
        if (MassSimulation)
        {
            MassSimulation->ResumeSimulation();
        }
    }, 5.0f, false);
}
```

**监听模拟事件** (来自 `MassSimulationSubsystem.h` 委托定义)
```cpp
// 在某个Actor（如GameMode或Subsystem）中监听
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();
    
    // 监听模拟暂停事件
    UMassSimulationSubsystem* MassSimulation = GetWorld()->GetSubsystem<UMassSimulationSubsystem>();
    if (MassSimulation)
    {
        PauseDelegateHandle = MassSimulation->GetOnSimulationPaused().AddUObject(this, &AMyGameMode::OnMassSimulationPaused);
    }
}

void AMyGameMode::OnMassSimulationPaused(UMassSimulationSubsystem* InSimulationSubsystem)
{
    UE_LOG(LogTemp, Warning, TEXT("Mass Simulation Paused!"));
    // 执行游戏逻辑，如显示暂停界面
}

void AMyGameMode::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理委托
    UMassSimulationSubsystem* MassSimulation = GetWorld()->GetSubsystem<UMassSimulationSubsystem>();
    if (MassSimulation && PauseDelegateHandle.IsValid())
    {
        MassSimulation->GetOnSimulationPaused().Remove(PauseDelegateHandle);
    }
    Super::EndPlay(EndPlayReason);
}
```

### 进阶用法

**动态注册处理器** (来自 `MassSimulationSubsystem.h`)
```cpp
// 在运行时向模拟中添加自定义处理器
UMassSimulationSubsystem* MassSimulation = GetWorld()->GetSubsystem<UMassSimulationSubsystem>();
if (MassSimulation)
{
    UMassProcessor* MyCustomProcessor = NewObject<UMyCustomSpawningProcessor>();
    MassSimulation->RegisterDynamicProcessor(MyCustomProcessor);
    
    // ... 在某处反注册
    MassSimulation->UnregisterDynamicProcessor(MyCustomProcessor);
}
```

**配置模拟预算** (来自 `MassSimulationSettings.h`)
```cpp
// 通过 CVar 或配置文件调整 Actor 生成预算
// 在项目的 DefaultMass.ini 中设置：
// [/Script/MassSimulation.MassSimulationSettings]
// DesiredActorSpawningTimeSlicePerTick=0.002
// DesiredActorDestructionTimeSlicePerTick=0.001
```

## Demo 示例

一个最小示例，展示如何从 C++ 中控制 Mass 模拟的暂停和恢复，并监听事件。

**MyMassGameplayController.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "MassSimulationSubsystem.h"
#include "MyMassGameplayController.generated.h"

UCLASS()
class MYGAME_API UMyMassGameplayController : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    UFUNCTION(BlueprintCallable, Category = "MassControl")
    void ToggleSimulationPause();

    void OnMassSimulationPaused(UMassSimulationSubsystem* InSubsystem);

    FDelegateHandle PauseDelegateHandle;
    bool bIsPaused = false;
};
```

**MyMassGameplayController.cpp**
```cpp
#include "MyMassGameplayController.h"
#include "MassSimulationSubsystem.h"

void UMyMassGameplayController::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    // 延迟到 PostInitialize 或更晚再获取其他子系统
    GetWorld()->GetTimerManager().SetTimerForNextTick([this]()
    {
        UMassSimulationSubsystem* MassSim = GetWorld()->GetSubsystem<UMassSimulationSubsystem>();
        if (MassSim)
        {
            // 监听暂停事件
            PauseDelegateHandle = MassSim->GetOnSimulationPaused().AddUObject(this, &UMyMassGameplayController::OnMassSimulationPaused);
        }
    });
}

void UMyMassGameplayController::Deinitialize()
{
    UMassSimulationSubsystem* MassSim = GetWorld()->GetSubsystem<UMassSimulationSubsystem>();
    if (MassSim && PauseDelegateHandle.IsValid())
    {
        MassSim->GetOnSimulationPaused().Remove(PauseDelegateHandle);
    }
    Super::Deinitialize();
}

void UMyMassGameplayController::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 可以在这里添加周期性检查或调试逻辑
}

TStatId UMyMassGameplayController::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UMyMassGameplayController, STATGROUP_Tickables);
}

void UMyMassGameplayController::ToggleSimulationPause()
{
    UMassSimulationSubsystem* MassSim = GetWorld()->GetSubsystem<UMassSimulationSubsystem>();
    if (MassSim && MassSim->IsSimulationStarted())
    {
        if (bIsPaused)
        {
            MassSim->ResumeSimulation();
            bIsPaused = false;
        }
        else
        {
            MassSim->PauseSimulation();
            bIsPaused = true;
        }
    }
}

void UMyMassGameplayController::OnMassSimulationPaused(UMassSimulationSubsystem* InSubsystem)
{
    UE_LOG(LogTemp, Display, TEXT("Mass Simulation has been paused."));
    // 在此处更新游戏状态，例如：bIsPaused = true;
    // 注意：此回调可能在 PauseSimulation 内部触发，因此直接修改 bIsPaused 是安全的。
}
```

## 模块依赖

该插件的模块大量依赖 `MassEntity` 核心框架。

| 模块 | 用途 |
|---|---|
| `MassEntity` | 大规模实体框架的核心库，提供实体、片段、处理器等基础概念 |
| `MassEntityEditor` | MassEntity 的编辑器支持，部分Runtime模块依赖它（如MassSimulation, MassSpawner） |
| `GameplayAbilities` | 被 `MassGameplayExternalTraits` 模块使用，用于将GAS（游戏能力系统）特性映射到Mass片段 |
| `MassAIBehavior` | 属于 `Engine/Plugins/AI/MassAI` 插件，用于集成行为树和EQS |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了 MassAgentComponent 的一项早期更改。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | [MassRepresentation] 在切换关闭 ISM（实例化静态网格）前等待 Actor 就绪。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了 Mass 群组中对非傀儡（non-puppet）Actor 的处理问题。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | [MassRepresentation] 修复了 `TMassLODCalculator` 逐观察者 LOD 路径中的一系列历史遗留 Bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | [MassRepresentation] 将两处手动计算的 `bDoKeepActorExtraFrame` 标志切换为使用新的 UE::M 函数。 |

### 维护评价

**活跃维护中**。MassGameplay 作为 UE5 的核心大规模模拟方案，仍在由 Epic Games 积极开发和维护。尽管标记为 **实验性 (IsExperimentalVersion=true)** 且默认不启用，但从 2026 年的近期提交记录看，该插件仍在频繁更新，主要围绕 `MassRepresentation`、`MassAgentComponent` 等模块进行功能改进和 Bug 修复，表明其仍在为《堡垒之夜》等旗舰项目服务。对于需要处理海量实体的新项目，这是一个值得评估和使用的前沿方案，但需接受其 API 可能随版本变动的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/mass-entity-and-mass-gameplay-in-unreal-engine/)（UE5 官方概述页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)