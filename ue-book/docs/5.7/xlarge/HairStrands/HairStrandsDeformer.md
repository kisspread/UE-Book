# Groom

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（毛发资产、材质、蓝图） |
| 模块 | `HairCardGeneratorFramework` (Runtime), `HairStrandsCore` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands（Groom）插件是 Unreal Engine 中用于处理高保真毛发和发型（Groom）的完整解决方案。它不仅仅是一个渲染组件，而是一个从资产导入、数据管理、物理模拟、运行时渲染到编辑器工具的全栈系统。其核心目标是解决在实时应用中渲染和模拟数百万根毛发束的性能与视觉质量挑战。它支持从 Alembic (.abc) 等格式导入基于发束（Strand）的毛发数据，并提供多种渲染策略（如发束、卡片、网格体）和物理模拟（如碰撞、风力）。

## 使用场景

- 你正在开发一个需要高度逼真角色毛发的 AAA 级游戏或影视虚拟制片项目。
- 你的角色发型需要复杂的物理模拟效果，例如随风飘动、与角色身体或环境发生碰撞。
- 你需要为不同平台（主机、PC、移动端）优化毛发渲染，使用基于发束的高质量渲染或基于卡片（Hair Cards）的高性能渲染。
- 你希望在编辑器中直观地调整毛发的材质、密度、LOD 等参数。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Hair Strands` | 设置或更新组件的毛发资产（Groom Asset）。 | `UGroomComponent` |
| `Set Enable Simulation` | 启用或禁用该毛发组件的物理模拟。 | `UGroomComponent` |
| `Set Physics Asset` | 为毛发模拟设置用于碰撞检测的物理资产。 | `UGroomComponent` |
| `Set Niagara Components` | 将 Niagara 粒子系统组件绑定到毛发束上，用于驱动次级效果（如发梢飘动）。 | `UGroomComponent` |
| `Set Interpolation Settings` | 设置毛发与骨骼网格体之间的蒙皮插值参数。 | `UGroomComponent` |
| `Get Groom Asset` | 获取当前组件使用的毛发资产引用。 | `UGroomComponent` |
| `Reset Simulation` | 重置毛发的物理模拟状态到初始姿势。 | `UGroomComponent` |

### 使用示例（蓝图描述）

1.  **创建毛发组件**：在角色蓝图中，添加一个 `UGroomComponent`。
2.  **指定资产**：在组件的细节面板中，将 `Groom` 属性设置为你的 `.groom` 资产。或在 BeginPlay 事件中，使用 `Set Hair Strands` 节点动态设置。
3.  **配置模拟**：勾选 `Enable Simulation`，并为其指定一个 `Physics Asset` 以实现与角色身体的碰撞。
4.  **绑定粒子**：如果需要次级动态效果，可以创建一个 Niagara 系统，然后使用 `Set Niagara Components` 节点将其绑定到毛发组件上。

## C++ 用法

### 头文件引入

```cpp
#include "GroomComponent.h"
#include "GroomAsset.h"
```

### 基本用法

创建并配置一个毛发组件。
（来源：基于 `UGroomComponent` 公共接口推断）

```cpp
// 在 Actor 的构造函数或 BeginPlay 中
UGroomComponent* GroomComp = CreateDefaultSubobject<UGroomComponent>(TEXT("HairGroom"));

// 加载毛发资产
static ConstructorHelpers::FObjectFinder<UGroomAsset> GroomAssetFinder(TEXT("/Game/Characters/Hero/Hero_Hair"));
if (GroomAssetFinder.Succeeded())
{
    GroomComp->SetGroomAsset(GroomAssetFinder.Object);
}

// 启用模拟并设置物理资产
GroomComp->SetEnableSimulation(true);
GroomComp->SetPhysicsAsset(PhysicsAssetForHair); // 需要预先加载或创建
```

### 进阶用法

在运行时动态控制毛发模拟。
（来源：基于 `UGroomComponent` 公共接口推断）

```cpp
// 在游戏逻辑中，例如角色进入室内时关闭模拟以提升性能
void AMyCharacter::EnterIndoor()
{
    if (GroomComponent)
    {
        GroomComponent->SetEnableSimulation(false);
    }
}

// 重置模拟，例如角色重生时
void AMyCharacter::Respawn()
{
    if (GroomComponent)
    {
        GroomComponent->ResetSimulation();
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个带有毛发组件的 Actor。

**MyGroomActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyGroomActor.generated.h"

class UGroomComponent;
class UGroomAsset;
class UPhysicsAsset;

UCLASS()
class AMyGroomActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGroomActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Groom")
    UGroomComponent* GroomComponent;

    // 在编辑器中指定资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Groom")
    UGroomAsset* GroomAsset;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Groom")
    UPhysicsAsset* HairPhysicsAsset;
};
```

**MyGroomActor.cpp**
```cpp
#include "MyGroomActor.h"
#include "GroomComponent.h"
#include "GroomAsset.h"
#include "PhysicsEngine/PhysicsAsset.h"

AMyGroomActor::AMyGroomActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建根组件和毛发组件
    USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);

    GroomComponent = CreateDefaultSubobject<UGroomComponent>(TEXT("Groom"));
    GroomComponent->SetupAttachment(Root);
}

void AMyGroomActor::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时应用资产和设置
    if (GroomAsset)
    {
        GroomComponent->SetGroomAsset(GroomAsset);
    }
    if (HairPhysicsAsset)
    {
        GroomComponent->SetPhysicsAsset(HairPhysicsAsset);
        GroomComponent->SetEnableSimulation(true);
    }
}
```

## 模块依赖

要使用此插件的功能，你的模块通常需要依赖以下模块（根据具体使用功能选择）：

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | 核心数据类型和资产定义，是使用任何毛发功能的基础。 |
| `HairStrandsRuntime` | 运行时渲染和模拟逻辑，用于在游戏中显示和模拟毛发。 |
| `HairStrandsSolver` | 物理求解器，用于实现毛发的碰撞和动力学模拟。 |
| `Niagara` | 如果需要将 Niagara 粒子系统绑定到毛发束上，则需要依赖此模块。 |

## 维护状态

### 近期更新

```
- d41996b25d54 Fix dataflow crash when reseting simulation while groom deformers are running
- 9412d5461be4 Fix groom deformers not working and crashing
- cb28d8f41d3d Bending model for groom + geometric collision+ guides solver
```

- `d41996b25d54` (2025-10-03): 修复了在毛发变形器运行时重置模拟导致的数据流崩溃问题。这是一个重要的稳定性修复。
- `9412d5461be4` (2025-09-15): 修复了毛发变形器不工作和崩溃的问题。表明插件在积极修复核心功能缺陷。
- `cb28d8f41d3d` (2025-08-20): 为毛发添加了弯曲模型、几何碰撞和引导线求解器。这是一次显著的功能增强，提升了模拟的真实感和可控性。

### 维护评价

**活跃维护**。该插件创建于2019年，是一个相对成熟的系统。从近期的提交记录看，Epic Games 仍在积极维护和改进它，最近几个月的更新集中在修复关键崩溃和增强物理模拟功能上。作为 Unreal Engine 官方毛发解决方案，它被广泛应用于《黑客帝国：觉醒》等技术演示中，是生产级可用的。虽然默认未启用（`EnabledByDefault: false`），但这通常是因为其较高的性能开销和特定的使用场景，而非质量问题。**推荐在需要高质量毛发渲染和模拟的项目中使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/hair-strands-and-grooms-in-unreal-engine/) (UE5 官方文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands/Tests) (如果存在)

---

# Hair Strands Deformer

> 本模块提供用于驱动和控制毛发（Groom）变形的功能，通常与物理模拟或动画系统结合使用。

## 用途

`HairStrandsDeformer` 模块是 HairStrands 插件中负责毛发变形的部分。它定义了如何将外部输入（如物理模拟结果、动画曲线、蓝图参数）转化为毛发束的最终形态。这使得开发者能够创建更复杂的毛发动态效果，例如基于角色动画的发型摆动、受游戏逻辑控制的发型变化（如“怒发冲冠”），或者将 Niagara 粒子系统的位置数据直接应用到毛发上。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Deformer Graph` | 为毛发组件设置一个数据流图（Dataflow Graph），用于定义复杂的变形逻辑。 | `UGroomComponent` |
| `Set Simulation Cache` | 设置或重置用于存储模拟状态的缓存，影响变形器的连续性。 | `UGroomComponent` |

### 使用示例（蓝图描述）

1.  在 `UGroomComponent` 的细节面板中，找到 “Deformers” 分类。
2.  你可以通过 `Set Deformer Graph` 节点在运行时动态加载和应用一个预先创建好的 Dataflow 资产，该资产定义了变形逻辑。
3.  变形器通常与 `HairStrandsSolver` 模块的模拟结果协同工作，将物理模拟的输出作为变形器的输入之一。

## C++ 用法

### 头文件引入

```cpp
// 通常通过 GroomComponent 间接使用
#include "GroomComponent.h"
// 如果需要直接操作数据流图
#include "Dataflow/DataflowGraph.h"
```

### 基本用法

通过组件接口设置变形器图。
（来源：基于 `UGroomComponent` 公共接口推断）

```cpp
// 加载一个数据流图资产
UDataflowGraph* DeformerGraph = LoadObject<UDataflowGraph>(nullptr, TEXT("/Game/Groom/Deformers/DF_HairWind"));

// 应用到毛发组件
if (GroomComponent && DeformerGraph)
{
    GroomComponent->SetDeformerGraph(DeformerGraph);
}
```

## 模块依赖

本模块是 `HairStrands` 插件的内部模块，其依赖关系由插件的构建系统管理。作为使用者，你通常不需要直接在你的 `.Build.cs` 中添加对 `HairStrandsDeformer` 的依赖。你需要依赖的是上层模块 `HairStrandsRuntime` 或 `HairStrandsCore`。

## 维护状态

### 近期更新

```
- d41996b25d54 Fix dataflow crash when reseting simulation while groom deformers are running
- 9412d5461be4 Fix groom deformers not working and crashing
- cb28d8f41d3d Bending model for groom + geometric collision+ guides solver
```

- `d41996b25d54` (2025-10-03): **直接相关**。修复了在变形器运行期间重置模拟导致的数据流崩溃，提升了该模块的稳定性。
- `9412d5461be4` (2025-09-15): **直接相关**。修复了变形器本身不工作和崩溃的问题，是核心功能的修复。
- `cb28d8f41d3d` (2025-08-20): 引入了弯曲模型等新物理特性，这些特性很可能通过变形器系统进行应用和控制。

### 维护评价

**活跃维护**。`HairStrandsDeformer` 模块作为插件的核心功能组件之一，近期的提交记录显示它正在被积极地修复和增强。最近的两次提交都是针对该模块关键问题的修复，表明 Epic 团队在持续关注其稳定性和功能性。结合整个插件的活跃状态，可以认为该模块是可靠且在持续演进的。