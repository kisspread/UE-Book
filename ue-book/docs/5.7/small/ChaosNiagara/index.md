# Chaos Niagara

> Import destruction data from Chaos into Niagara to generate secondary destruction effects.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌尼亚加拉 |
| 分类 |  |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosNiagara` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosNiagara) | |

## 用途

Chaos Niagara 插件提供了将 Chaos 破坏系统（Geometry Collection 破碎、碰撞、拖尾事件）产生的数据无缝导入到 Niagara 粒子系统中的能力。它通过一组专门的 Niagara Data Interface（数据接口）让粒子系统能够访问并驱动基于物理事件的二次特效（如碎片飞溅、烟尘、火花轨迹等）。

主要解决以下问题：
- 在破碎发生时，实时捕获每个碎块的变换矩阵、边界、速度等信息，供 Niagara 驱动粒子行为。
- 将 Chaos 求解器产生的碰撞、拖尾事件数据（位置、法线、速度、旋转等）暴露给 Niagara，用于生成跟随特效。
- 支持物理场（Physics Field）数据接口，允许将自定义力场（如涡旋、噪声）应用到 Niagara 粒子模拟中。

该插件是实验性特性，旨在将高级破坏物理与 Niagara 特效系统深度整合，减少手动搬运数据的开销。

## 使用场景

- **破坏碎片后效**：当 Geometry Collection 物体被击碎后，每个碎片的位置、旋转、速度可用于生成飘落、爆炸或消散粒子。
- **碰撞特效**：在碎片与其他物体碰撞的瞬间，从碰撞事件中提取碰撞点、法线、速度，生成火花、烟雾或碎片溅射。
- **拖尾轨迹**：捕捉碎片飞行过程中的拖尾事件（Trailing Event），用粒子系统绘制运动轨迹。
- **物理场驱动特效**：利用 Chaos 物理场（如风力、重力修改）直接影响 Niagara 粒子的运动，实现与环境交互的动态效果。

## 蓝图用法

该插件核心功能通过 Niagara 数据接口（Data Interface）暴露。在 Niagara 编辑器中选择发射器，添加相应数据接口后，即可在粒子模块中访问其属性。

| 节点（数据接口） | 说明 | 所在类 |
|---|---|---|
| `Chaos Destruction Event` | 提供 Chaos 破坏事件的集合（位置、法线、速度、角速度、范围、粒子ID、时间、类型），支持对事件进行遍历。 | `UNiagaraDataInterfaceChaosDestruction` |
| `Geometry Collection` | 提供 Geometry Collection 中每个碎块的变换矩阵（当前帧/上一帧）、边界、组件初始变换、元素索引映射等。 | `UNiagaraDataInterfaceGeometryCollection` |
| `Physics Field` | 提供基于 Chaos 物理场的标的资源数据，可在 GPU 粒子模拟中查询场强。 | `UNiagaraDataInterfacePhysicsField` |

### 使用示例（蓝图描述）

1. **创建 Chaos 破坏粒子系统**：
   - 新建 Niagara 系统，添加一个 GPU 或 CPU 发射器。
   - 在发射器属性 → Data Interfaces 中点击“+”，选择 “Chaos Destruction Event”。
   - 在粒子 Spawn 或 Update 模块中，使用 `Get Chaos Destruction Event` 节点获取事件属性（如 Position、Velocity），驱动粒子初始位置和初速度。
   - 将发射器绑定到场景中的 ChaosSolverActor 或 GeometryCollectionActor（通过蓝图设置数据接口的 Source 对象）。

2. **使用 Geometry Collection 数据**：
   - 添加 “Geometry Collection” 数据接口。
   - 在粒子模块中使用 `Get Geometry Collection Transform`、`Get Geometry Collection Bounds` 等节点（具体节点名以实际版本为准）获取碎块信息，使粒子附着于碎块运动。

3. **使用 Physics Field**：
   - 添加 “Physics Field” 数据接口。
   - 在 GPU 粒子中启用外部力场，通过 Niagara 的 `Sample Physics Field` 节点采样场值，修改粒子的加速度。

此类数据接口通常不在蓝图中暴露直接调用函数，而是在 Niagara 系统内部作为输入源使用，因此无需额外的蓝图节点连接。

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraDataInterfaceGeometryCollection.h"
#include "NiagaraDataInterfaceChaosDestruction.h"
#include "NiagaraDataInterfacePhysicsField.h"
```

### 基本用法

以下示例演示如何在 C++ 中创建并配置一个 `UNiagaraDataInterfaceGeometryCollection` 并将其与一个 `UGeometryCollectionComponent` 关联：

```cpp
// 来源：NiagaraDataInterfaceGeometryCollection.h + 常见用法

// 在 Actor 中获取 Niagara 组件
UNiagaraComponent* NiagaraComp = CreateDefaultSubobject<UNiagaraComponent>(TEXT("DestructionVFX"));
NiagaraComp->SetAsset(MyNiagaraSystem);

// 找到 Geometry Collection Data Interface 实例（假设系统已有）
// 注意：实际使用中需要通过 NiagaraSystem 的编辑器数据获取 DataInterface 句柄
// 这里为伪代码，展示思路
UNiagaraDataInterfaceGeometryCollection* GC_Interface = GetGeometryCollectionDataInterface(NiagaraComp);

// 设置要追踪的 GeometryCollectionActor
if (GC_Interface)
{
    AGeometryCollectionActor* GCActor = ...;
    GC_Interface->SetGeometryCollectionActor(GCActor); // 非官方API，仅示意
}
```

真实情况下，在运行时通过代码修改数据接口的绑定对象需要使用 `FNiagaraSystemInstance` 的私有方法，推荐使用蓝图方式或在 `FNiagaraDataInterface` 子类中暴露自定义函数。更常见的用法是直接在 Niagara 编辑器中绑定数据接口的源对象。

### 进阶用法

监听 Chaos 破坏事件并手动触发 Niagara 粒子：

```cpp
// 来源：NiagaraDataInterfaceChaosDestruction.h + ChaosSolver集成
// 在 ChaosSolverActor 的碰撞/破坏事件回调中，将事件数据传递给 Niagara 数据接口

void ADestructionFXManager::OnChaosBreakEvent(const FChaosBreakEvent& BreakEvent)
{
    // 获取对应的 Niagara 组件
    if (UNiagaraComponent* NiagaraComp = GetRelevantNiagaraComponent(BreakEvent.Location))
    {
        // 通过 Niagara 系统自定义事件触发粒子
        // 注意：Chaos Destruction Event DataInterface 自动监听 Chaos 事件，
        // 无需手动传递数据，只需确保数据接口的 Source 设置为正确的 ChaosSolverActor
        NiagaraComp->SetVariableVec3(FName("User.BreakPosition"), BreakEvent.Location);
        NiagaraComp->SetVariableFloat(FName("User.BreakMass"), BreakEvent.Mass);
        // 然后调用 Niagara 的“触发Spawn”功能
    }
}
```

更推荐的做法是直接使用数据接口的内置事件泵，无需手动转发。例如在 Niagara 发射器的初始化模块中直接使用 `Chaos Destruction Event` 数据接口的“Event Count”和“Get Event Data”节点。

## Demo 示例

以下是一个最小 C++ 示例，创建带有 Geometry Collection 和 Niagara 系统的 Actor，并在物体破碎时激活粒子。依赖已通过插件自动满足，无需额外模块依赖。

```cpp
// DestructionFXActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DestructionFXActor.generated.h"

class UGeometryCollectionComponent;
class UNiagaraComponent;
class AChaosSolverActor;

UCLASS()
class ADestructionFXActor : public AActor
{
    GENERATED_BODY()

public:
    ADestructionFXActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UGeometryCollectionComponent* GeometryCollectionComp;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UNiagaraComponent* NiagaraComp;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    AChaosSolverActor* ChaosSolverActor;

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// DestructionFXActor.cpp
#include "DestructionFXActor.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "NiagaraComponent.h"
#include "ChaosSolverActor.h"

ADestructionFXActor::ADestructionFXActor()
{
    PrimaryActorTick.bCanEverTick = false;

    GeometryCollectionComp = CreateDefaultSubobject<UGeometryCollectionComponent>(TEXT("GeometryCollection"));
    RootComponent = GeometryCollectionComp;

    NiagaraComp = CreateDefaultSubobject<UNiagaraComponent>(TEXT("DestructionVFX"));
    NiagaraComp->SetupAttachment(RootComponent);
}

void ADestructionFXActor::BeginPlay()
{
    Super::BeginPlay();

    // 将Chaos求解器绑定到Geometry Collection（蓝图亦可）
    if (ChaosSolverActor && GeometryCollectionComp)
    {
        GeometryCollectionComp->SetChaosSolverActor(ChaosSolverActor);
    }

    // 确保Niagara系统已加载并包含Chaos Destruction Event数据接口
    // 该接口会在内部监听GeometryCollectionComp的破坏事件
    // 因此Niagara用户无需额外代码即可获取事件数据
}
```

使用步骤：
1. 在编辑器中创建继承自 `ADestructionFXActor` 的蓝图，指定 `ChaosSolverActor` 和 `GeometryCollectionComp` 的碰撞体。
2. 配置 `NiagaraComp` 的 `NiagaraSystem` 资产，该资产必须包含 `Chaos Destruction Event` 数据接口，并在粒子模块中消费事件数据。
3. 运行游戏，破坏 Geometry Collection，粒子将自动触发。

## 模块依赖

要使用 Chaos Niagara 插件，你的模块（或项目）需要在 `Build.cs` 中添加以下依赖。注意，这些依赖已通过插件配置文件自动添加，但若你在C++代码中直接引用相关类，仍需添加。

| 模块 | 用途 |
|---|---|
| `Niagara` | 提供 Niagara 核心框架及数据接口基类。 |
| `ChaosSolverPlugin` | 提供 Chaos 求解器及事件回调结构。 |
| `GeometryCollectionEngine` | (间接依赖) 提供 Geometry Collection 组件所需类型。 |

## 维护状态

### 近期更新

- 2025-08-01 `ad3d996e` — Chaos Niagara interface : Perf / memory and trailing event not play from a chaos cache fixes
- 2025-04-23 `6ae57335` — Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i
- 2025-03-14 `7ce30a02` — Fix simple cases of unreachable code for loops that terminate after one iteration
- 2024-12-17 `c5c637aa` — - Remove passing in LWC tile to various data interface and use Engine.Owner.LWCTile instead
- 2024-11-12 `6de2fe53` — * Added element index output to geometry collection DI

### 维护评价

- **创建时间**：2024年11月（约1年），相对较新。
- **最近更新**：2025年8月仍有功能性修复（性能和缓存播放问题），表明尚在积极维护。
- **插件状态**：标记为实验性（IsBetaVersion=true），版本号0.1，属于早期开发阶段。
- **已知限制**：功能可能不完整，API可能变更；依赖 Chaos 求解器的新特性，需要相应版本支持。
- **推荐使用**：适合愿意尝试前沿特性的项目，或在受到 Epic 官方支持的情况下使用。生产环境中建议自行测试并做好回退准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosNiagara)
- [官方文档](https://docs.unrealengine.com/5.7/chaos-physics-overview/)（Chaos 物理总览）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosNiagara/Source/ChaosNiagara)（无独立测试目录，核心源码即主要参考）