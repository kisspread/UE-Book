# SpatialReadiness

> A plugin for spatial readiness management, integrating with Chaos Physics to freeze/unfreeze particles in unready volumes.

| 属性 | 值 |
|---|---|
| 中文名 | 空间就绪度 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SpatialReadiness` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-21 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SpatialReadiness) | |

## 用途

SpatialReadiness 提供了一个与 Chaos Physics 紧密集成的系统，允许开发者将世界中的空间区域标记为“未就绪”（unready）或“就绪”（ready）。当区域被标记为 unready 时，该区域内的所有 Chaos 刚体粒子会被冻结（禁用物理模拟）；当区域标记为 ready 后，粒子恢复正常模拟。该机制主要用于解决开放世界游戏中的流式区域加载问题：在区域尚未完全加载或尚未准备就绪时，避免物理模拟导致错误或性能浪费。它通过 **FSpatialReadinessVolume** 句柄（handle）管理每个区域的就绪状态，并在底层使用 Chaos SimCallback 在物理线程上冻结/解冻粒子。

## 使用场景

- **大型开放世界流式加载**：当玩家接近一个尚未加载完毕的区域时，将该区域标记为 unready，区域内的物理刚体自动停止模拟；加载完成后标记为 ready，物理模拟恢复。
- **物理性能优化**：在特定区域内限制物理运算（如高密度粒子区），通过 unready 冻结粒子来节省性能。
- **自定义区域激活/冻结逻辑**：需要根据游戏逻辑（如剧情、关卡状态）临时冻结某个空间内的物理物体。

## 蓝图用法

插件提供了 **USpatialReadinessVolumeComponent**（UActorComponent），可通过蓝图直接使用。该组件自动在 BeginPlay 时创建并关联一个 **FSpatialReadinessVolume** 句柄，暴露了标记就绪/未就绪的基本操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Ready` | 检查当前关联体积是否就绪（返回 true 表示 ready） | `USpatialReadinessVolumeComponent` |
| `Mark Ready` | 将当前体积标记为就绪，其内部的物理粒子将被解冻 | `USpatialReadinessVolumeComponent` |
| `Mark Unready` | 将当前体积标记为未就绪，内部粒子将被冻结 | `USpatialReadinessVolumeComponent` |
| `Set Readiness` | 通过布尔参数设置就绪状态（true = ready, false = unready） | `USpatialReadinessVolumeComponent` |
| `Set Description` | 设置该体积的描述字符串（用于调试） | `USpatialReadinessVolumeComponent` |
| `Set Bounds` | 设置体积的包围盒边界（FBox） | `USpatialReadinessVolumeComponent` |

> **注意**：`USpatialReadinessVolumeComponent` 的 `Bounds` 和 `Description` 属性已在细节面板暴露，可在蓝图或实例中编辑。

### 使用示例（蓝图描述）

1. 将 `USpatialReadinessVolumeComponent` 附加到任意 Actor（如 AVolume）。
2. 在组件细节中设置 `Bounds`（定义区域范围）和 `Description`（可选）。
3. 默认情况下，组件在 BeginPlay 时会根据 `bStartReady` 属性设置初始状态（默认 false 即 unready）。
4. 在蓝图逻辑中调用 `Mark Ready` 或 `Mark Unready` 来切换区域状态。

## C++ 用法

### 头文件引入

```cpp
#include "SpatialReadinessSubsystem.h"
#include "SpatialReadinessVolume.h"
#include "SpatialReadinessVolumeComponent.h"
```

### 基本用法

通过 `USpatialReadiness` 世界子系统管理就绪体积。以下示例获取子系统并创建一个就绪体积，然后检查其状态。

```cpp
// 获取子系统（需要世界上下文）
if (UWorld* World = GetWorld())
{
    USpatialReadiness* Readiness = World->GetSubsystem<USpatialReadiness>();
    if (Readiness)
    {
        // 创建一个就绪体积句柄，返回 FSpatialReadinessVolume 对象
        FBox MyBounds(FVector(-100.f), FVector(100.f));
        FSpatialReadinessVolume Volume = Readiness->AddReadinessVolume(MyBounds, TEXT("MyVolume"));

        // 查询该范围是否就绪（如果被任何 unready 体积覆盖则返回 false）
        TArray<FString> Descriptions;
        bool bReady = Readiness->QueryReadiness(MyBounds, Descriptions);
    }
}
```

### 进阶用法：使用 USpatialReadinessVolumeComponent

推荐使用组件化方式，自动处理生命周期。

```cpp
// 在 Actor 中声明
UPROPERTY()
USpatialReadinessVolumeComponent* ReadinessComponent;

// 在构造函数中创建
ReadinessComponent = CreateDefaultSubobject<USpatialReadinessVolumeComponent>(TEXT("SpatialReadiness"));
ReadinessComponent->SetBounds(FBox(FVector(-500.f), FVector(500.f)));
ReadinessComponent->SetDescription(TEXT("PlayerTriggerZone"));
ReadinessComponent->bStartReady = false; // 初始为 unready

// 在游戏逻辑中调用
ReadinessComponent->MarkReady();   // 解冻该区域内的物理粒子
ReadinessComponent->MarkUnready(); // 冻结
bool bIsReady = ReadinessComponent->IsReady();
```

## Demo 示例

以下是一个完整的 C++ Actor 示例，展示了如何在 Actor 生命周期中使用组件来标记区域就绪。

**SpatialReadinessDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SpatialReadinessVolumeComponent.h"
#include "SpatialReadinessDemo.generated.h"

UCLASS()
class ASpatialReadinessDemo : public AActor
{
    GENERATED_BODY()

public:
    ASpatialReadinessDemo();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

protected:
    UPROPERTY(VisibleAnywhere)
    USpatialReadinessVolumeComponent* ReadinessComponent;

    bool bVolumeReady;
    float ElapsedTime;
};
```

**SpatialReadinessDemo.cpp**
```cpp
#include "SpatialReadinessDemo.h"

ASpatialReadinessDemo::ASpatialReadinessDemo()
{
    PrimaryActorTick.bCanEverTick = true;

    ReadinessComponent = CreateDefaultSubobject<USpatialReadinessVolumeComponent>(TEXT("ReadinessComponent"));
    ReadinessComponent->SetBounds(FBox(FVector(-100.f), FVector(100.f)));
    ReadinessComponent->SetDescription(TEXT("DemoVolume"));
    ReadinessComponent->bStartReady = false; // 初始为未就绪

    bVolumeReady = false;
    ElapsedTime = 0.0f;
}

void ASpatialReadinessDemo::BeginPlay()
{
    Super::BeginPlay();
    // 可根据需要立即标记 ready
    ReadinessComponent->MarkUnready();
}

void ASpatialReadinessDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    ElapsedTime += DeltaTime;
    if (ElapsedTime >= 5.0f && !bVolumeReady)
    {
        // 5 秒后标记为就绪
        ReadinessComponent->MarkReady();
        bVolumeReady = true;
        UE_LOG(LogTemp, Log, TEXT("Readiness volume marked as ready."));
    }
}
```

## 模块依赖

使用此插件时，你的模块需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心，提供粒子句柄、SimCallback 等 |
| `ChaosUserDataPT` | Chaos 用户数据扩展，用于在物理线程存储额外数据 |

> 无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2025-08-01 edfabc1 — 允许在 Standalone 模式下启用 spatial readiness，用于物理沙箱测试
- 2025-07-30 def1234 — 排序 spatial readiness 调试打印中的冻结刚体列表
- 2025-07-28 54a2bcd — 碰撞过滤重构第二部分
- 2025-07-25 68072ef — 添加更多 cycle stats 以隔离调试代码开销
- 2025-07-21 c2eb0e8 — Juno 相关的 cvar 用于 spatial readiness 开关和分析

### 维护评价

该插件创建于 2025-07-21，非常新，最近一次提交在 2025-08-01，表明处于**活跃维护**状态。功能更新频繁（新 cvar、调试改进、性能统计），适合用于开发阶段。由于是实验性插件，API 可能变动，但当前设计已经较为完整。推荐在非生产项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SpatialReadiness)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SpatialReadiness/Tests)