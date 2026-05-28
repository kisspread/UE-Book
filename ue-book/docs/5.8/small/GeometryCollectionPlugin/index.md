# Geometry Collection Plugin

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何体集合 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码资产） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

`GeometryCollectionPlugin` 是一个用于创建、管理和模拟可破碎几何体（Geometry Collection）的**综合性框架**。它提供了一套完整的运行时与编辑器工具集，核心目标是将静态网格体（Static Mesh）分解为可独立模拟物理的几何体碎片（Geometry Collection），并支持基于数据流（Dataflow）的程序化破碎和破坏效果。

该插件解决了传统破坏系统碎片管理复杂、难以与引擎深度集成的问题。它通过一个中心化的 `GeometryCollection` 资产来存储破碎前后的几何数据、层次结构、材质以及物理属性，使得破坏效果的制作、预览和优化变得系统化。

## 使用场景

- **游戏中的可破坏环境**：制作可被武器、爆炸或玩家互动摧毁的建筑物、墙体、栏杆等。
- **载具与道具的破碎**：创建车辆碰撞后解体、木箱被击碎等效果。
- **程序化破坏与建造**：结合 Dataflow 图，实现动态计算破坏轨迹、局部破坏等复杂逻辑。
- **电影与动画预览**：在编辑器内快速预览并调整复杂的破碎动画序列。

## 模块列表

- **`GeometryCollectionDepNodes`**: 包含用于 Dataflow 图中操作 Geometry Collection 的输入/输出节点。
- **`GeometryCollectionEditor`**: 提供编辑器内的资产查看器、破碎工具和工作流集成。
- **`GeometryCollectionNodes`**: 提供核心的 Dataflow 节点，用于程序化创建和修改 Geometry Collection。
- **`GeometryCollectionSequencer`**: 集成 Sequencer，允许在时间轴上控制 Geometry Collection Actor 的破坏状态和动画。
- **`GeometryCollectionTracks`**: 为 Sequencer 提供专门的轨道类型，以编辑 Geometry Collection 的关键帧数据。

## 蓝图用法

本插件主要通过 Dataflow 图和编辑器工具进行操作。蓝图中可通过以下核心类进行交互：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Geometry Collection` | 从一组静态网格体或 Dataflow 输出创建几何体集合资产。 | `UGeometryCollection` |
| `Apply Damage` | 对 Geometry Collection Actor 施加冲击力，触发局部或全部破坏。 | `UGeometryCollectionComponent` |
| `Set Rest Collection` | 设置组件的原始（静止状态）几何体集合。 | `UGeometryCollectionComponent` |
| `Get Dynamic Collection` | 获取当前模拟状态的动态几何体集合（包含实时变换和破碎信息）。 | `UGeometryCollectionComponent` |

### 使用示例（蓝图描述）

要创建一个可破坏的墙体：
1. 使用 `Create Geometry Collection` 节点，输入代表墙体砖块的静态网格体数组，生成一个 `UGeometryCollection` 资产。
2. 在场景中放置一个 `AGeometryCollectionActor`，将其组件的 `RestCollection` 属性设置为上一步创建的资产。
3. 当需要破坏时，调用 `Apply Damage` 节点，指定冲击位置和力的大小。

## C++ 用法

核心操作围绕 `UGeometryCollection` 和 `UGeometryCollectionComponent` 进行。

### 头文件引入

```cpp
#include "GeometryCollection/GeometryCollectionObject.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
```

### 基本用法

```cpp
// 动态创建一个简单的几何体集合组件并设置资产
UGeometryCollectionComponent* GCComp = NewObject<UGeometryCollectionComponent>(SomeActor);
GCComp->SetRestCollection(MyGeometryCollectionAsset);
GCComp->RegisterComponent();

// 在运行时施加破坏力
FVector ImpactPoint = FVector(100, 50, 200);
FVector ImpactVelocity = FVector(0, 0, -500);
GCComp->ApplyExternalStrain(0, ImpactPoint, ImpactVelocity);
```

## Demo 示例

一个最小的可编译 C++ Actor 示例，包含一个几何体集合组件。

**GeometryCollectionDemoActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "GeometryCollectionDemoActor.generated.h"

class UGeometryCollectionComponent;
class UGeometryCollection;

UCLASS()
class AGeometryCollectionDemoActor : public AActor
{
    GENERATED_BODY()
public:
    AGeometryCollectionDemoActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UGeometryCollectionComponent* GeometryCollectionComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Destruction")
    UGeometryCollection* GeometryCollectionAsset;

    UFUNCTION(BlueprintCallable, Category = "Destruction")
    void ApplyDamageAtPoint(const FVector& Location, float Strength);
};
```

**GeometryCollectionDemoActor.cpp**
```cpp
#include "GeometryCollectionDemoActor.h"
#include "GeometryCollection/GeometryCollectionComponent.h"

AGeometryCollectionDemoActor::AGeometryCollectionDemoActor()
{
    GeometryCollectionComponent = CreateDefaultSubobject<UGeometryCollectionComponent>(TEXT("GCComponent"));
    RootComponent = GeometryCollectionComponent;
}

void AGeometryCollectionDemoActor::ApplyDamageAtPoint(const FVector& Location, float Strength)
{
    if (GeometryCollectionComponent)
    {
        // 施加一个指向“下方”的冲击力来模拟坍塌
        FVector ImpactDir = FVector(0, 0, -1);
        GeometryCollectionComponent->ApplyExternalStrain(0, Location, ImpactDir * Strength);
    }
}
```

## 模块依赖

要使用本插件的完整功能，你的模块需要依赖以下核心模块（常见依赖如 `Core`, `Engine` 等已省略）：

| 模块 | 用途 |
|---|---|
| `GeometryCollectionEngine` | 几何体集合的核心运行时引擎逻辑 |
| `Chaos` | Chaos 物理求解器，用于模拟破坏 |
| `PhysicsInterface` | Chaos 物理接口层 |
| `Dataflow` | 数据流编辑器与运行时框架 |
| `Sequencer` | 时间轴与关键帧系统集成 |
| `PropertyEditor` | 自定义编辑器属性面板 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 版本的本地化警告问题。 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | Dataflow 功能更新（具体内容未在提交信息中说明）。 |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 回退了某个特定的更改（CL53945814）。 |
| 2026-05-14 | `88fb5004` | Dataflow: | Dataflow 功能更新（具体内容未在提交信息中说明）。 |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | 新增一个 Dataflow 节点，用于在几何体集合上创建外部碰撞体。 |

### 维护评价

该插件**仍处于活跃维护状态**。尽管标记为 `Experimental` 和 `IsBetaVersion`，但近期的提交记录（2026年5月）显示 Epic 仍在持续进行功能迭代（尤其是 Dataflow 相关节点）和适配新版引擎（5.8）。主要功能在 Chaos 物理系统稳定后已经较为成熟，但仍建议在正式项目中谨慎使用，并密切关注后续的稳定性更新和版本迁移说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [子模块文档：GeometryCollectionDepNodes](GeometryCollectionDepNodes.md)
- [子模块文档：GeometryCollectionEditor](GeometryCollectionEditor.md)
- [子模块文档：GeometryCollectionNodes](GeometryCollectionNodes.md)
- [子模块文档：GeometryCollectionSequencer](GeometryCollectionSequencer.md)
- [子模块文档：GeometryCollectionTracks](GeometryCollectionTracks.md)