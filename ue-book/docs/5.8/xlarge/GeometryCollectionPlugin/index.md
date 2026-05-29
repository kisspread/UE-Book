# Geometry Collection

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何集合 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

GeometryCollectionPlugin 是 **Chaos Destruction 系统**的核心资产和数据管理组件。它定义并管理 `UGeometryCollection` 资产，该资产是一个容器，用于存储用于物理模拟和破坏效果的几何体层次结构（如建筑、岩石、木制障碍物）。

这个插件存在的根本原因是为 UE5 的 Chaos 物理系统提供一套完整的工具链，用于：
1.  **存储与管理**：将复杂的、可破坏的网格体分解为带有层次关系（父-子骨骼）的几何片段集合。
2.  **编辑与预处理**：在编辑器内对几何集合进行切割、分层、设置破坏阈值等操作。
3.  **驱动破坏效果**：通过蓝图、Sequencer 或数据流（Dataflow）节点，在运行时或编辑器内触发布料的破坏、碎片飞溅等效果。
4.  **与多个子系统集成**：与 Niagara（粒子）、Sequencer（过场动画）、材质系统等深度集成，实现复杂的视觉效果。

简而言之，它是构建电影级实时破坏场景的“数据库”和“操作台”。

## 使用场景

-   **建筑坍塌**：你需要在游戏中实现一栋建筑被炸毁或自然倒塌的效果，需要精确控制每个楼层的碎片。
-   **岩石破碎**：角色攻击一块巨石，巨石碎裂成大小不一的碎片，且碎片具有物理交互。
-   **木制障碍物破坏**：车辆撞毁木栅栏，木板碎裂并飞溅。
-   **过场动画中的破坏**：在 Sequencer 中精确编排一个物体的破碎过程和时间点。
-   **程序化破坏**：通过 Dataflow 节点，根据游戏逻辑（如爆炸伤害范围）动态生成破坏效果。

## 蓝图用法

此插件提供的核心功能主要通过 `GeometryCollectionEditor` 和 `GeometryCollectionNodes` 模块中的资产与节点暴露给蓝图。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `UGeometryCollection` | 核心资产，存储可破坏几何体的网格、变换、层次关系、材质和物理模拟参数。 |
| `AGeometryCollectionActor` | 挂载 `UGeometryCollection` 资产的 Actor，用于在场景中放置和驱动破坏效果。 |
| `UGeometryCollectionComponent` | `AGeometryCollectionActor` 的核心组件，负责管理模拟和渲染状态。 |

### 核心操作节点（蓝图中可用）

| 节点 | 说明 | 所在模块 |
|---|---|---|
| `Apply External Strain` | 对指定位置的几何集合施加外部应变，用于启动破坏。 | `GeometryCollectionNodes` |
| `Apply Kinematic Field` | 施加运动场（如爆炸波），影响附近碎片的速度和方向。 | `GeometryCollectionNodes` |
| `Reset Geometry Collection` | 重置破坏状态，将几何集合恢复为初始状态（用于游戏重启等）。 | `GeometryCollectionNodes` |
| `Set Dynamic State` | 设置几何集合片段的动态状态（静态、睡眠、动态）。 | `GeometryCollectionNodes` |

### 使用示例（蓝图描述）

1.  **基本破坏设置**：
    *   在场景中拖入 `AGeometryCollectionActor`。
    *   在其 `Details` 面板中，指定一个预先创建好的 `UGeometryCollection` 资产。
    *   为角色或子弹的命中事件添加蓝图逻辑。
    *   在命中事件中，获取命中点信息（`Hit Result`）。
    *   使用 `Apply External Strain` 节点，将命中点（`Hit Location`）作为输入，为 `UGeometryCollectionComponent` 施加一个应变值（`Magnitude`）。应变值超过该区域设置的阈值时，物体开始破坏。

2.  **与 Sequencer 配合**：
    *   在 Sequencer 轨道中添加 `GeometryCollectionTracks` 提供的专用轨道。
    *   在时间线上关键帧记录 `Apply External Strain` 或 `Reset` 等操作，实现电影中精准控制的破坏时机。

## C++ 用法

在 C++ 中，你主要通过操作 `UGeometryCollection`, `UGeometryCollectionComponent` 和 Chaos 物理接口来实现高级功能。

### 头文件引入

```cpp
#include "GeometryCollection/GeometryCollection.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
// 如果使用数据流节点
#include "Dataflow/DataflowCore.h"
```

### 基本用法

```cpp
// 获取场景中的几何集合组件
UGeometryCollectionComponent* GCComp = GeometryCollectionActor->GetGeometryCollectionComponent();

// 通过 Chaos 的物理接口施加破坏
if (GCComp)
{
    // 构建一个模拟外部冲击的破坏请求
    FChaosBreakEvent BreakEvent;
    BreakEvent.Location = ImpactPoint;
    BreakEvent.Velocity = ImpactVelocity;
    BreakEvent.Mass = 1.0f;
    
    // 将破坏事件传递给组件的 Chaos 物理模拟器
    GCComp->OnChaosBreakEvent(BreakEvent);
}
```
*(示例基于 Chaos 物理接口和 `GeometryCollectionComponent` 的通用模式)*

### 进阶用法

结合 `GeometryCollectionNodes` 中的数据流节点，在编辑器工具或运行时脚本中程序化生成和操作几何集合。

```cpp
// 概念性示例：在编辑器中通过 C++ 编写一个数据流节点来切割几何体
class FMyCutNode : public FDataflowNode
{
    // ... 节点输入输出定义 ...
    
    virtual void Evaluate(FDataflowContext& Context) override
    {
        UGeometryCollection* GC = Context.GetInput<UGeometryCollection>(TEXT("GeometryCollection"));
        FPlane CutPlane = Context.GetInput<FPlane>(TEXT("CutPlane"));
        
        // 调用插件提供的算法，沿平面切割几何集合
        UGeometryCollection* NewGC = UGeometryCollectionEdit::SplitGeometryCollection(GC, CutPlane);
        
        Context.SetOutput<UGeometryCollection>(TEXT("CutGeometryCollection"), NewGC);
    }
};
```

## Demo 示例

以下是一个最简 C++ 示例，演示如何在一个自定义 Actor 中触发现有几何集合的破坏。

**MyDestructibleActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDestructibleActor.generated.h"

class UGeometryCollectionComponent;

UCLASS()
class AMyDestructibleActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyDestructibleActor();

protected:
    virtual void BeginPlay() override;

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UGeometryCollectionComponent* GeometryCollectionComp;

    UFUNCTION(BlueprintCallable)
    void BreakAtPoint(FVector Point, float ForceMagnitude);
};
```

**MyDestructibleActor.cpp**
```cpp
#include "MyDestructibleActor.h"
#include "GeometryCollection/GeometryCollectionComponent.h"

AMyDestructibleActor::AMyDestructibleActor()
{
    PrimaryActorTick.bCanEverTick = false;
    
    GeometryCollectionComp = CreateDefaultSubobject<UGeometryCollectionComponent>(TEXT("GeoCollection"));
    RootComponent = GeometryCollectionComp;
}

void AMyDestructibleActor::BeginPlay()
{
    Super::BeginPlay();
}

void AMyDestructibleActor::BreakAtPoint(FVector Point, float ForceMagnitude)
{
    if (GeometryCollectionComp)
    {
        // 构建破坏事件
        FChaosBreakEvent Event;
        Event.Location = Point;
        Event.Velocity = (Point - GetActorLocation()).GetSafeNormal() * ForceMagnitude;
        
        // 触发破坏
        GeometryCollectionComp->OnChaosBreakEvent(Event);
    }
}
```

## 模块依赖

要使用此插件的功能，你的项目或模块除了依赖 Core， Engine 等基础模块外，通常需要显式依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GeometryCollection` | 核心数据资产定义，**必须依赖**。 |
| `Chaos` | Chaos 物理引擎底层接口，进行高级物理控制时需要。 |
| `ChaosSolverEngine` | Chaos 求解器，运行时模拟需要。 |
| `Niagara` | 用于与粒子系统集成，创建破坏时的灰尘、火花效果。 |
| `LevelSequence`, `MovieScene` | 用于 Sequencer 集成，在过场动画中控制破坏。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 本地化警告，确保插件与新版本兼容。 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | 数据流模块更新（具体提交信息不完整）。 |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 撤回了一项更改，可能是为了修复引入的问题。 |
| 2026-05-14 | `88fb5004` | Dataflow: | 数据流模块更新（具体提交信息不完整）。 |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | **重要更新**：新增数据流节点，用于在几何集合上创建外部碰撞体。 |

### 维护评价

该插件创建于 2018 年，历史悠久。虽然它仍被标记为 `IsBetaVersion` 和 `EnabledByDefault=false`，但从近期的提交记录（2026年5月）来看，**它仍在被 Epic Games 积极维护和更新**。最新的更新集中在“数据流”（Dataflow）功能上，这是用于程序化生成和控制破坏效果的核心工具。

**优势**：
-   作为 Chaos 破坏系统的核心，不可或缺。
-   持续获得功能更新和兼容性修复。
-   与 Niagara、Sequencer 等现代 UE 子系统深度集成。

**注意**：
-   **实验性状态**：尽管维护活跃，其 API 和用法仍可能在版本间发生变化。
-   **复杂性高**：完全掌握需要理解 Chaos 物理和几何处理的基本概念。
-   **默认禁用**：必须在项目的 `.uproject` 文件或编辑器设置中手动启用。

**结论**：**强烈推荐用于需要实现高质量、可控物理破坏的项目**。虽然是实验性插件，但它是 Epic 官方破坏方案的核心，且维护活跃，值得投入学习。

## 相关链接

-   [插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin)
-   [GeometryCollectionDepNodes 模块文档](GeometryCollectionDepNodes.md)
-   [GeometryCollectionEditor 模块文档](GeometryCollectionEditor.md)
-   [GeometryCollectionNodes 模块文档](GeometryCollectionNodes.md)
-   [GeometryCollectionSequencer 模块文档](GeometryCollectionSequencer.md)
-   [GeometryCollectionTracks 模块文档](GeometryCollectionTracks.md)