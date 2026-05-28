# SpatialReadiness

> Experimental spatial readiness for physics.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 空间就绪性 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SpatialReadiness` (Runtime), `SpatialReadinessTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SpatialReadiness) | |

## 用途

SpatialReadiness 插件提供了一套实验性的系统，用于管理游戏世界中特定空间区域（卷）的物理就绪状态。在大型开放世界或流式加载场景中，物理引擎（Chaos）可能需要处理尚未完全加载或准备好的区域中的物体交互，这可能导致不可预测的行为或性能问题。此插件允许开发者显式地定义哪些区域是“就绪”的，从而精细地控制物理模拟的边界和交互条件，确保物理交互只发生在预期且已准备好的区域中。

## 使用场景

-   你正在开发一个使用 Chaos 物理系统的大型开放世界游戏，需要精确控制不同流式加载区块的物理交互时机。
-   你需要调试或可视化特定区域内的物理就绪状态，以诊断由加载顺序引起的物理问题。
-   你希望为某些关键区域（如玩家出生点或重要任务区域）提供物理稳定性保障，防止远处未加载区域的物体意外产生交互。

## 蓝图用法

由于这是一个实验性运行时插件，其蓝图接口通常通过 `USpatialReadinessSubsystem` 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `添加就绪卷` | 在指定位置和大小创建一个就绪卷，该区域内的物理交互将被启用。 | `USpatialReadinessSubsystem` |
| `移除就绪卷` | 销毁一个先前创建的就绪卷。 | `USpatialReadinessSubsystem` |
| `查询空间就绪状态` | 查询一个点或区域是否处于就绪卷内。 | `USpatialReadinessSubsystem` |
| `启用/禁用物理交互` | 全局启用或禁用空间就绪性系统对物理交互的控制。 | `USpatialReadinessSubsystem` |

### 使用示例（蓝图描述）

1.  在角色 `BeginPlay` 事件中，调用 `Get Game Instance Subsystem` 节点获取 `SpatialReadinessSubsystem`。
2.  使用 `添加就绪卷` 节点，在玩家当前位置创建一个适当大小的就绪卷（例如，以玩家为中心的 10000 单位立方体），并存储返回的卷句柄。
3.  在玩家移动时，定期（如每秒）调用 `添加就绪卷` 更新卷的位置，并使用 `移除就绪卷` 清理旧卷。
4.  可以在需要时调用 `查询空间就绪状态` 来判断某个物体是否在就绪区域内。

## C++ 用法

### 头文件引入

```cpp
#include "SpatialReadinessSubsystem.h"
```

### 基本用法

```cpp
// 获取空间就绪性子系统
if (UWorld* World = GetWorld())
{
    if (USpatialReadinessSubsystem* ReadinessSubsystem = World->GetSubsystem<USpatialReadinessSubsystem>())
    {
        // 定义一个就绪卷（例如，一个球体区域）
        FSpatialReadinessVolume Volume;
        Volume.Location = GetActorLocation();
        Volume.Radius = 5000.0f;

        // 添加就绪卷
        FSpatialReadinessVolumeHandle VolumeHandle = ReadinessSubsystem->AddUnreadyVolume(Volume);
    }
}
```

### 进阶用法

```cpp
// 查询某个点是否就绪
FVector TestPoint = FVector(100, 200, 300);
bool bIsReady = ReadinessSubsystem->IsPointReady(TestPoint);

// 移除先前添加的就绪卷
ReadinessSubsystem->RemoveUnreadyVolume(VolumeHandle);

// 在物理模拟回调中检查（例如，在 Chaos solver 的 pre-sim 回调中）
// 这通常在插件内部处理，但展示了其与物理引擎集成的深度
```

## Demo 示例

以下是一个最小的 Actor 类示例，用于在其周围创建和维护一个就绪卷。

**SpatialReadinessDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SpatialReadinessSubsystem.h"
#include "SpatialReadinessDemoActor.generated.h"

UCLASS()
class ASpatialReadinessDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ASpatialReadinessDemoActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    FSpatialReadinessVolumeHandle CurrentVolumeHandle;

    UPROPERTY(EditAnywhere, Category="Spatial Readiness")
    float VolumeRadius = 5000.0f;

    void UpdateReadinessVolume();
};
```

**SpatialReadinessDemoActor.cpp**
```cpp
#include "SpatialReadinessDemoActor.h"

ASpatialReadinessDemoActor::ASpatialReadinessDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 1.0f; // 每秒更新一次，与加载频率匹配
}

void ASpatialReadinessDemoActor::BeginPlay()
{
    Super::BeginPlay();
    UpdateReadinessVolume();
}

void ASpatialReadinessDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UWorld* World = GetWorld())
    {
        if (USpatialReadinessSubsystem* Subsystem = World->GetSubsystem<USpatialReadinessSubsystem>())
        {
            if (CurrentVolumeHandle.IsValid())
            {
                Subsystem->RemoveUnreadyVolume(CurrentVolumeHandle);
                CurrentVolumeHandle.Invalidate();
            }
        }
    }
    Super::EndPlay(EndPlayReason);
}

void ASpatialReadinessDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    UpdateReadinessVolume();
}

void ASpatialReadinessDemoActor::UpdateReadinessVolume()
{
    if (UWorld* World = GetWorld())
    {
        if (USpatialReadinessSubsystem* Subsystem = World->GetSubsystem<USpatialReadinessSubsystem>())
        {
            // 移除旧卷
            if (CurrentVolumeHandle.IsValid())
            {
                Subsystem->RemoveUnreadyVolume(CurrentVolumeHandle);
            }

            // 创建新卷
            FSpatialReadinessVolume NewVolume;
            NewVolume.Location = GetActorLocation();
            NewVolume.Radius = VolumeRadius;
            CurrentVolumeHandle = Subsystem->AddUnreadyVolume(NewVolume);
        }
    }
}
```

## 模块依赖

要使用 SpatialReadiness 插件，你的模块需要依赖以下模块（在你的 `.Build.cs` 中添加）：

| 模块 | 用途 |
|---|---|
| `PhysicsCore` | 物理核心模块，提供基础物理类型和接口。 |
| `Chaos` | Chaos 物理求解器核心。 |
| `ChaosSolverEngine` | Chaos 物理求解器引擎，用于与物理场景交互。 |
| `ChaosUserDataPT` | 提供物理线程（Physics Thread）的用户数据支持，此插件的核心依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统迁移到更现代的 UE_LOGF 格式。 |
| 2026-04-01 | `f85501de` | Avoid expensive includes in SpatialReadinessSubsystem.h and SpatialReadinessSimCallback.h | 优化头文件，避免不必要的包含以提升编译速度。 |
| 2026-03-03 | `ed0e1959` | Add missing physics scene lock to FSpatialReadinessSimCallback::AddUnreadyVolume_GT | 修复了一个潜在的线程安全问题，在添加就绪卷时正确地锁定了物理场景。 |
| 2025-12-08 | `0b36b316` | [Spatial Readiness] Ensure to disable MidPhase for Unready volumes | 确保未就绪卷中的物体禁用中阶段碰撞检测，提升性能和准确性。 |
| 2025-11-18 | `db60e2a5` | Updated spatial readiness to not use separate query/sim block filters and instead create separate sh | 更新了就绪卷的实现逻辑，优化了查询和模拟过滤器的使用方式。 |

### 维护评价

-   **活跃维护**：该插件自 2025 年初创建以来，至今（2026 年 4 月）仍在持续收到功能性更新、性能优化和 bug 修复，表明它处于活跃开发和维护中。
-   **实验性**：插件在 `.uplugin` 中被明确标记为实验性且默认禁用 (`EnabledByDefault: false`)，这意味着其 API 和功能可能在未来版本中发生变化或被移除。
-   **推荐度**：对于正在使用 Chaos 物理并面临大型世界流式加载与物理交互问题的项目，这是一个值得关注和尝试的实验性解决方案。建议在开发分支中谨慎引入，并密切跟踪其后续更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SpatialReadiness)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SpatialReadiness/Tests)