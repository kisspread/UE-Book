# Chaos Visual Debugger

> Enables support for Visual debugging of Chaos Physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 物理模拟调试器 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运行时蓝图库） |
| 模块 | `ChaosVD` (EditorAndProgram), `ChaosVDBlueprint` (RuntimeAndProgram), `ChaosVDBuiltInExtensions` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosVD) | |

## 用途

ChaosVD 是一个用于调试 Chaos 物理引擎模拟的**可视化调试工具**。它不仅提供编辑器内的实时可视化，更重要的是，它支持**录制**物理模拟过程中的关键信息，并在后续进行**回放分析**。其核心价值在于帮助开发者理解复杂的物理交互、碰撞、约束等行为，是诊断物理模拟相关问题的强大工具。当前 `ChaosVDBlueprint` 模块提供了在**运行时**通过蓝图标记调试绘制信息的能力，这些信息可以被 CVD 录制并回放。

## 使用场景

- 你需要调试一个布娃娃（Ragdoll）在复杂场景中的物理行为，观察其骨骼、约束和碰撞。
- 你怀疑某个物体的物理模拟（如弹道、抛射）存在异常，希望录制其运动轨迹和碰撞点进行逐帧分析。
- 你需要为 AI 角色的物理寻路或障碍物规避提供可视化调试支持。
- 你需要在蓝图中运行时动态记录自定义的调试信息（如轨迹线、关注区域），并将其与物理数据一同录制和回放。

## 蓝图用法

蓝图功能主要由 `UChaosVDRuntimeBlueprintLibrary` 提供，用于在运行时向 CVD 录制流写入自定义的调试绘制形状。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CVD Record Debug Draw Box` | 记录一个盒体（包围盒）调试形状 | `UChaosVDRuntimeBlueprintLibrary` |
| `CVD Record Debug Draw Line` | 记录一条线段调试形状 | `UChaosVDRuntimeBlueprintLibrary` |
| `CVD Record Debug Draw Vector` | 记录一个从起点出发的向量（带方向箭头） | `UChaosVDRuntimeBlueprintLibrary` |
| `CVD Record Debug Draw Sphere` | 记录一个球体调试形状 | `UChaosVDRuntimeBlueprintLibrary` |
| `CVD Set Trace Relevancy Volume` | 设置一个与 CVD 调试相关的追踪卷（影响查询范围） | `UChaosVDRuntimeBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **记录玩家移动轨迹**：
    在玩家的移动更新事件中，连接 `CVD Record Debug Draw Sphere` 节点。将 `World Context` 引脚连接到玩家控制器，`In Center` 使用玩家位置，`Tag` 设为 “PlayerTrail”，`Color` 设为绿色。这样，每次物理帧更新时，都会在玩家位置记录一个绿色球体，CVD 录制时即可回放移动轨迹。

2.  **标记关注区域**：
    在关卡蓝图中，使用 `CVD Record Debug Draw Box` 节点。将 `World Context` 连接到自引用，`In Box` 设置为某个区域的包围盒，`Tag` 设为 “TargetZone”，`Color` 设为黄色。此调用在运行时只会执行一次（或根据需要），用于在 CVD 回放中高亮显示特定区域。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosVDRuntimeBlueprintLibrary.h"
```

### 基本用法

在 C++ 中，你可以像调用其他静态库函数一样调用这些录制函数。通常用于在物理相关的代码逻辑中插入调试标记。

```cpp
// 假设在某个游戏对象的物理计算函数中
void AMyPhysicsActor::OnPhysicsSimulated()
{
    // 获取当前世界上下文
    UWorld* World = GetWorld();

    // 记录当前 actor 的包围盒调试形状
    FBox ActorBounds = GetComponentsBoundingBox();
    UChaosVDRuntimeBlueprintLibrary::RecordDebugDrawBox(
        World,
        ActorBounds,
        FName("ActorBounds"),
        FLinearColor::Yellow
    );

    // 记录一个从 actor 位置向前方延伸的调试向量
    FVector ForwardDirection = GetActorForwardVector() * 500.f;
    UChaosVDRuntimeBlueprintLibrary::RecordDebugDrawVector(
        World,
        GetActorLocation(),
        ForwardDirection,
        FName("ForwardTrace"),
        FLinearColor::Green
    );

    // ... 其他物理计算逻辑
}
```
*（代码示例基于 `UChaosVDRuntimeBlueprintLibrary.h` 的公共接口设计推断）*

### 进阶用法

可以将调试绘制函数与自定义标签系统结合，实现更复杂的调试过滤。例如，根据不同的调试类别设置不同的 `Tag`，在 CVD 回放器中通过标签来筛选显示。

```cpp
// 定义调试类别标签
static const FName CVDTag_Collision = TEXT("CollisionDebug");
static const FName CVDTag_AIPath = TEXT("AIDebug");

// 在碰撞回调中记录
void AMyActor::OnHit(const FHitResult& Hit)
{
    // 只在启用 CVD 调试时记录，避免性能开销
#if ENABLE_VISUALIZE_DEBUG
    UWorld* World = GetWorld();
    if (World && Hit.bBlockingHit)
    {
        // 记录碰撞点球体
        UChaosVDRuntimeBlueprintLibrary::RecordDebugDrawSphere(
            World,
            Hit.ImpactPoint,
            20.f,
            CVDTag_Collision,
            FLinearColor::Red
        );
        // 记录碰撞法线向量
        UChaosVDRuntimeBlueprintLibrary::RecordDebugDrawVector(
            World,
            Hit.ImpactPoint,
            Hit.ImpactNormal * 100.f,
            CVDTag_Collision,
            FLinearColor::Cyan
        );
    }
#endif
}
```

## Demo 示例

下面是一个最小的 Actor 示例，它在 Tick 时持续记录自身位置的球体调试信息，供 CVD 录制。

**ChaosVDDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChaosVDDemoActor.generated.h"

UCLASS()
class AChaosVDDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AChaosVDDemoActor();

protected:
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY(EditAnywhere, Category = "Debug")
    FName DebugTag = TEXT("DemoActor");

    UPROPERTY(EditAnywhere, Category = "Debug")
    FLinearColor DebugColor = FLinearColor::Green;
};
```

**ChaosVDDemoActor.cpp**
```cpp
#include "ChaosVDDemoActor.h"
#include "ChaosVDRuntimeBlueprintLibrary.h"

AChaosVDDemoActor::AChaosVDDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AChaosVDDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 在运行时记录当前的调试绘制球体
    UWorld* World = GetWorld();
    if (World)
    {
        UChaosVDRuntimeBlueprintLibrary::RecordDebugDrawSphere(
            World,
            GetActorLocation(),
            50.f, // 球体半径
            DebugTag,
            DebugColor
        );
    }
}
```

## 模块依赖

`ChaosVDBlueprint` 模块（本文档主要描述的蓝图接口模块）本身依赖关系较为基础，但使用它时，你的项目通常也需要启用 `ChaosVD` 插件的核心模块。

| 模块 | 用途 |
|---|---|
| `ChaosVD` | ChaosVD 的核心模块，提供 CVD 录制、回放和编辑器集成的基础框架，`ChaosVDBlueprint` 的运行时函数库很可能依赖此模块的功能。 |
| `Chaos` | Chaos 物理引擎核心模块，被 `ChaosVD` 深度集成。 |

*(注：基于插件功能和 `.uplugin` 中列出的插件依赖 `EditorDataStorage`, `GeometryProcessing` 推断，`ChaosVD` 核心模块可能依赖这些模块。但 `ChaosVDBlueprint` 的直接依赖较少，主要可能依赖 `ChaosVD` 模块。)*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口关联逻辑，优化客户端通知流程。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了某个变更（具体代码未提供）。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 与 `cfb610df` 相同，是对视口关联逻辑的重构提交。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量被截断为浮点数所产生的警告。 |
| 2026-05-12 | `b4158d4d` | Make CVD Perf Analysis Async | 将 CVD 性能分析功能改为异步执行。 |

### 维护评价

- **创建时间**：约1年前（2024年3月），是一个相对较新的插件。
- **近期活跃度**：最近一周（2026年5月）有多次提交，包括功能重构、性能优化和编译警告修复，表明插件**正在被积极维护和开发中**。
- **版本状态**：`.uplugin` 中 `IsBetaVersion` 为 `true`，说明这是一个**测试版**，功能可能不完全稳定，API 未来可能会有变动。
- **推荐度**：作为官方提供的物理调试工具，其设计目标明确，且开发活跃，**强烈推荐**在使用 Chaos 物理引擎的项目中启用，用于诊断和调试复杂的物理问题。但需注意其测试版状态，在生产环境中应谨慎使用，并做好跟进新版本变动的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosVD)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine)（在官方文档站搜索 “Chaos Visual Debugger”）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/ChaosVD/Source) （通常位于插件源码的 Tests 目录下，具体路径需根据仓库结构调整）