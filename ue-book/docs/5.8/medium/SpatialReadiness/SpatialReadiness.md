# Spatial Readiness

> Add world readiness and world readiness test modules

| 属性 | 值 |
|---|---|
| 中文名 | 空间准备状态 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SpatialReadiness` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SpatialReadiness) | |

## 用途

SpatialReadiness 插件旨在解决**动态流式加载或生成环境中的物理穿模问题**。在开放世界游戏或使用程序化内容生成的场景中，当新的地形、建筑或对象被异步加载时，物理模拟可能会因为这些“未准备”区域尚未就绪而导致角色或物体穿过尚未加载的几何体，出现“掉出世界”或“穿模”的情况。

该插件通过标记一个“未准备”（Unready）的空间体积，并**冻结所有与该体积发生物理交互的刚体粒子**，直到相关资产完全加载并标记为“准备就绪”（Ready）。它与 Chaos 物理引擎深度集成，利用物理线程的回调来精确控制粒子的状态，从而在资产加载期间保证物理世界的稳定性和合理性。

## 使用场景

- 你在开发一个大型开放世界游戏，需要流式加载远处的地形和建筑 → 用 SpatialReadiness 标记正在加载的区域，防止玩家在加载过程中掉入虚空。
- 你使用程序化生成（PCG）或动态生成关卡，物理对象的生成顺序不确定 → 用 SpatialReadiness 冻结与正在生成的区域重叠的物体，避免它们因为生成顺序问题而发生错误的碰撞或穿透。
- 你需要在一个具有复杂物理模拟的场景中安全地替换或卸载大型物理资产 → 用 SpatialReadiness 标记即将被替换的资产所占用的空间，保护其他物体。

## 蓝图用法

该插件提供了 `USpatialReadinessVolumeComponent`，可以在蓝图中轻松创建和管理“准备状态”体积。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Ready` | 检查该体积当前是否处于“准备就绪”状态。 | `USpatialReadinessVolumeComponent` |
| `Mark Ready` | 将该体积标记为“准备就绪”，相关物理限制将被解除。 | `USpatialReadinessVolumeComponent` |
| `Mark Unready` | 将该体积标记为“未准备就绪”，会冻结与之重叠的物理对象。 | `USpatialReadinessVolumeComponent` |
| `Set Readiness` | 通过布尔值直接设置体积的准备状态。 | `USpatialReadinessVolumeComponent` |
| `Set Description` | 为该体积设置一个描述字符串，用于调试和日志。 | `USpatialReadinessVolumeComponent` |
| `Set Bounds` | 设置该体积影响的空间范围（AABB盒）。 | `USpatialReadinessVolumeComponent` |

### 使用示例（蓝图描述）

1. 在你的 Actor（例如一个代表流式加载区块的 `ALevelStreamingVolume`）中，添加一个 `USpatialReadinessVolumeComponent` 组件。
2. 在组件的细节面板中，设置 `Description` 为例如 `"StreamingChunk_01"`，并调整 `Bounds` 以匹配该区块的物理范围。
3. 设置 `bStartReady` 属性为 `false`（默认），以确保游戏开始时该体积就是“未准备”状态。
4. 当相关的资产（如地形网格、碰撞体）流式加载完成时，在你的加载完成回调中调用 `Mark Ready` 节点。
5. 如果需要动态调整体积大小或描述，可以使用 `Set Bounds` 和 `Set Description` 节点。

## C++ 用法

插件的核心 C++ 接口是 `USpatialReadiness` 子系统和 `FSpatialReadinessVolume` 句柄。

### 头文件引入

```cpp
#include "SpatialReadinessSubsystem.h"
#include "SpatialReadinessVolume.h"
```

### 基本用法

**创建和查询“未准备”体积**（来源：`Public/SpatialReadinessSubsystem.h`）：

```cpp
// 获取空间准备状态子系统
if (UWorld* World = GetWorld())
{
    if (USpatialReadiness* SpatialReadinessSubsystem = World->GetSubsystem<USpatialReadiness>())
    {
        // 1. 定义一个未准备区域的包围盒和描述
        FBox UnreadyBox(FVector(-1000, -1000, 0), FVector(1000, 1000, 500));
        FString Description = TEXT("ProceduralTreeForest_Generating");

        // 2. 添加一个“未准备”体积，并获取一个句柄用于后续管理
        FSpatialReadinessVolume VolumeHandle = SpatialReadinessSubsystem->AddReadinessVolume(UnreadyBox, Description);

        // ... 在某个时刻，资产加载完成 ...

        // 3. 将该体积标记为“准备就绪”
        VolumeHandle.MarkReady();

        // 4. 查询某个区域是否“准备就绪”（例如角色当前位置）
        FBox QueryBox = FBox::BuildAABB(GetActorLocation(), FVector(50.f));
        TArray<FString> UnreadyReasons;
        bool bIsReady = SpatialReadinessSubsystem->QueryReadiness(QueryBox, UnreadyReasons, true);
        if (!bIsReady)
        {
            UE_LOG(LogTemp, Warning, TEXT("Area is not ready for reasons: %s"), *FString::Join(UnreadyReasons, TEXT(", ")));
        }
    }
}
```

### 进阶用法

**监听未准备体积的变化**（来源：`Public/SpatialReadinessSubsystem.h`）：

```cpp
// 在某个类的 BeginPlay 或 Initialize 中绑定委托
if (USpatialReadiness* Subsystem = GetWorld()->GetSubsystem<USpatialReadiness>())
{
    // 使用成员函数绑定
    Subsystem->OnUnreadyVolumeChangedDelegate_AddUObject(this, &AMyClass::HandleUnreadyVolumeChanged);
}

// 回调函数实现
void AMyClass::HandleUnreadyVolumeChanged(const FBox& Bounds, const FString& Description, EUnreadyVolumeAction Action)
{
    if (Action == EUnreadyVolumeAction::Added)
    {
        UE_LOG(LogSpatialReadiness, Log, TEXT("New unready volume added: %s, Bounds: %s"), *Description, *Bounds.ToString());
        // 可以在此触发加载逻辑或UI提示
    }
    else if (Action == EUnreadyVolumeAction::Removed)
    {
        UE_LOG(LogSpatialReadiness, Log, TEXT("Unready volume removed: %s"), *Description);
    }
}
```

## Demo 示例

以下是一个最小可运行示例，演示如何在 C++ 中创建和查询空间准备状态体积。

**MyReadinessActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SpatialReadinessVolume.h"
#include "MyReadinessActor.generated.h"

UCLASS()
class AMyReadinessActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    FSpatialReadinessVolume ReadinessVolumeHandle;
};
```

**MyReadinessActor.cpp**
```cpp
#include "MyReadinessActor.h"
#include "SpatialReadinessSubsystem.h"

void AMyReadinessActor::BeginPlay()
{
    Super::BeginPlay();

    if (UWorld* World = GetWorld())
    {
        if (USpatialReadiness* Subsystem = World->GetSubsystem<USpatialReadiness>())
        {
            // 创建一个覆盖自身位置的未准备体积
            FBox ActorBounds = GetComponentsBoundingBox();
            ReadinessVolumeHandle = Subsystem->AddReadinessVolume(ActorBounds, TEXT("MyReadinessActor"));

            // 假设3秒后资源加载完成
            FTimerHandle TimerHandle;
            World->GetTimerManager().SetTimer(TimerHandle, [this]()
            {
                if (ReadinessVolumeHandle.IsValid())
                {
                    ReadinessVolumeHandle.MarkReady();
                    UE_LOG(LogTemp, Log, TEXT("Actor’s readiness volume marked as ready!"));
                }
            }, 3.0f, false);
        }
    }
}

void AMyReadinessActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 析构时，FSpatialReadinessVolume 的析构函数会自动将其标记为 Ready
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

要使用 SpatialReadiness 插件，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `SpatialReadiness` | 核心插件模块，提供子系统和 API。 |
| `PhysicsCore` | 基础物理框架，用于 `FPhysScene_Chaos` 等类型。 |
| `Chaos` | Chaos 物理引擎核心，用于粒子句柄、求解器等。 |
| `ChaosUserDataPT` | （插件依赖）提供 Chaos 用户数据的物理线程访问。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到更现代的 UE_LOGF 宏。 |
| 2026-04-01 | `f85501de` | Avoid expensive includes in SpatialReadinessSubsystem.h and SpatialReadinessSimCallback.h | 优化头文件，避免在频繁包含的头文件中引入昂贵的依赖。 |
| 2026-03-03 | `ed0e1959` | Add missing physics scene lock to FSpatialReadinessSimCallback::AddUnreadyVolume_GT | 修复了一个线程安全问题，为添加未准备卷的操作补充了物理场景锁。 |
| 2025-12-08 | `0b36b316` | [Spatial Readiness] Ensure to disable MidPhase for Unready volumes | 确保禁用未准备卷的中间阶段碰撞检测。 |
| 2025-11-18 | `db60e2a5` | Updated spatial readiness to not use separate query/sim block filters and instead create separate sh | 重构了过滤机制，不再使用单独的查询/模拟过滤器，转而创建独立的形状。 |

### 维护评价

- **活跃维护**：该插件自 2025 年 1 月创建至今（约 1.5 年），最近一次更新在 2026 年 4 月，显示仍在积极维护和迭代。
- **内容实质**：近期的提交包括性能优化（减少头文件包含）、关键修复（添加物理锁）和功能完善（中间阶段策略调整），表明其处于功能稳定和优化阶段。
- **实验性状态**：插件位于 `Experimental` 目录下且默认禁用，符合其“实验性”标签。虽然 API 已经相对完善，但仍需注意其可能在未来版本中发生变化。
- **已知限制**：强依赖于 Chaos 物理引擎，不适用于其他物理后端。
- **推荐使用**：**推荐**。对于使用 Chaos 物理且需要处理动态流式加载或生成场景穿模问题的项目，这是一个设计精良、维护活跃的官方实验性解决方案。建议在项目早期进行集成测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SpatialReadiness)
- 官方文档（暂无）
- 测试用例（位于 `Tests/SpatialReadinessTests` 目录）