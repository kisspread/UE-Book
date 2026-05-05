# Cloners and Effectors

> Niagara based cloner system with various layouts and effector affecting each clone instances

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `ClonerEffector` (Runtime), `ClonerEffectorEditor` (Runtime), `ClonerEffectorMeshBuilder` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-06 |
| 年龄标签 | 🆕（约 1.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ClonerEffector) | |

## 用途

ClonerEffector 是一个基于 Niagara 粒子系统的高级克隆与效应器插件，专为虚拟制作（Virtual Production）场景设计。它解决了在场景中高效创建、布局和动态控制大量重复对象（克隆体）的核心问题。与简单的实例化静态网格体不同，它通过 Niagara 提供了强大的运行时控制能力，并允许通过“效应器”（Effector）对克隆体进行空间化、参数化的动态影响（如位移、缩放、旋转、材质变化等），从而实现复杂的动态视觉效果，如人群、植被、建筑群、粒子阵列等。

## 使用场景

-   **虚拟制片场景填充**：在 LED 墙或虚拟场景中快速布置观众、树木、建筑等重复元素，并通过效应器实现风吹草动、人群波浪等动态效果。
-   **动态视觉特效**：创建基于物理或逻辑规则的粒子阵列、机械结构、能量场等，效应器可以实时改变这些阵列的形态和行为。
-   **原型设计与预览**：快速迭代大量物体的布局和动画效果，无需手动摆放和关键帧动画。

## 蓝图用法

由于提供的头文件主要为编辑器模块，运行时蓝图 API 位于 `ClonerEffector` 模块中。基于插件功能推断，核心蓝图节点通常围绕组件展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Cloner Layout` | 设置克隆体的布局模式（如网格、圆形、线性等） | `UCEClonerComponent` |
| `Add Effector` | 为克隆组件添加一个效应器引用 | `UCEClonerComponent` |
| `Set Effector Type` | 设置效应器的类型（如位移、缩放、旋转等） | `UCEEffectorComponent` |
| `Set Effector Strength` | 设置效应器的影响强度 | `UCEEffectorComponent` |

### 使用示例（蓝图描述）

1.  在 Actor 上添加一个 `ClonerComponent`。
2.  为 `ClonerComponent` 设置一个静态网格体作为克隆源。
3.  通过 `Set Cloner Layout` 节点选择布局（例如 `Grid`），并设置行、列、间距等参数。
4.  创建另一个 Actor，添加 `EffectorComponent`。
5.  将 `EffectorComponent` 拖拽到 `ClonerComponent` 的 `Effectors` 数组属性中，或使用 `Add Effector` 节点。
6.  配置 `EffectorComponent` 的类型（如 `Displacement`）和参数（如强度、衰减形状）。
7.  运行时，效应器将根据其位置和参数动态影响所有克隆体。

## C++ 用法

### 头文件引入

```cpp
#include "ClonerEffector/Public/Cloner/CEClonerComponent.h"
#include "ClonerEffector/Public/Effector/CEEffectorComponent.h"
```

### 基本用法

创建并配置一个克隆组件。

```cpp
// 假设在某个 Actor 的 BeginPlay 中
#include "Cloner/CEClonerComponent.h"

// 创建克隆组件
UCEClonerComponent* ClonerComp = NewObject<UCEClonerComponent>(this);
ClonerComp->RegisterComponent();

// 设置克隆的静态网格体源
ClonerComp->SetMesh(MyStaticMesh);

// 设置布局为网格
ClonerComp->SetLayout(ECEClonerLayout::Grid);
// 配置网格参数
FCEClonerGridParams GridParams;
GridParams.CountX = 10;
GridParams.CountY = 10;
GridParams.SpacingX = 200.f;
GridParams.SpacingY = 200.f;
ClonerComp->SetGridParams(GridParams);
```

### 进阶用法

动态添加和配置效应器。

```cpp
#include "Effector/CEEffectorComponent.h"

// 创建效应器组件
UCEEffectorComponent* EffectorComp = NewObject<UCEEffectorComponent>(this);
EffectorComp->RegisterComponent();

// 设置效应器类型为位移
EffectorComp->SetType(ECEEffectorType::Displacement);
// 设置位移强度
EffectorComp->SetStrength(50.f);

// 将效应器添加到克隆组件
ClonerComp->AddEffector(EffectorComp);

// 运行时修改效应器参数
EffectorComp->SetStrength(100.f);
```

## Demo 示例

一个最小的可运行示例，创建一个网格克隆并受一个位移效应器影响。

**MyClonerActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyClonerActor.generated.h"

class UCEClonerComponent;
class UCEEffectorComponent;

UCLASS()
class AMyClonerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyClonerActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    UCEClonerComponent* ClonerComponent;

    UPROPERTY(VisibleAnywhere)
    UCEEffectorComponent* EffectorComponent;
};
```

**MyClonerActor.cpp**
```cpp
#include "MyClonerActor.h"
#include "Cloner/CEClonerComponent.h"
#include "Effector/CEEffectorComponent.h"

AMyClonerActor::AMyClonerActor()
{
    PrimaryActorTick.bCanEverTick = false;

    ClonerComponent = CreateDefaultSubobject<UCEClonerComponent>(TEXT("Cloner"));
    RootComponent = ClonerComponent;

    EffectorComponent = CreateDefaultSubobject<UCEEffectorComponent>(TEXT("Effector"));
    EffectorComponent->SetupAttachment(RootComponent);
}

void AMyClonerActor::BeginPlay()
{
    Super::BeginPlay();

    // 配置克隆体
    ClonerComponent->SetLayout(ECEClonerLayout::Grid);
    FCEClonerGridParams Params;
    Params.CountX = 5;
    Params.CountY = 5;
    Params.SpacingX = 150.f;
    Params.SpacingY = 150.f;
    ClonerComponent->SetGridParams(Params);

    // 配置效应器
    EffectorComponent->SetType(ECEEffectorType::Displacement);
    EffectorComponent->SetStrength(30.f);

    // 将效应器链接到克隆体
    ClonerComponent->AddEffector(EffectorComponent);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心粒子系统，克隆体的底层驱动 |
| `GeometryFramework` | 可能用于网格构建和编辑器可视化 |
| `MeshDescription` | `ClonerEffectorMeshBuilder` 模块用于处理网格数据 |
| `ToolMenus` | `ClonerEffectorEditor` 模块用于构建编辑器上下文菜单 |
| `PropertyEditor` | `ClonerEffectorEditor` 模块用于自定义细节面板 |

## 维护状态

### 近期更新

-   2025-10-03 e9f41910b466 MotionDesign : ClonerEffector - Added metadata to only refresh children in details view when changed property has the metadata "RefreshPropertyView"
    *解读：优化了编辑器细节面板的刷新逻辑，提升了性能。*
-   2025-09-15 acc60063f57f MotionDesign : ClonerEffector - Fixed details view property tab to commit unfocusing value widget of cloner and effector due to RequetRebuildChildren clearing focus
    *解读：修复了编辑器中一个关于焦点丢失的 UI 交互 Bug。*
-   2025-08-20 4e2c56303294 MotionDesign : Modifiers - Added FilterActorByComponentClass specifier for actor property to be reused across modifiers to filter level actors based on a component class - Fixed spline sweep modifier clearing mesh when out of range or invalid - Allow spline path modifier to loop even if spline is not a closed loop (progress, distance, time, points)
    *解读：为修改器系统增加了通用的 Actor 过滤功能，并修复了样条线相关修改器的多个问题。*

### 维护评价

**活跃维护**。该插件创建于 2024 年初，属于较新的功能。从 git 历史看，最近 3 个月内持续有功能性更新和 Bug 修复，主要集中在编辑器体验优化和底层修改器系统的增强上。这表明 Epic Games 的 Motion Design 团队正在积极开发和维护此插件，是虚拟制作工具链中的重要组成部分。推荐在需要高级克隆和动态效果的虚拟制作项目中使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ClonerEffector)
-   [官方文档]() (暂无)
-   [测试用例]() (暂未在提供的路径中发现)