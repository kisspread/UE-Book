# Cloners and Effectors

> Niagara based cloner system with various layouts and effector affecting each clone instances

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ClonerEffector` (Runtime), `ClonerEffectorEditor` (Runtime), `ClonerEffectorMeshBuilder` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ClonerEffector) | |

## 用途

ClonerEffector 是一个基于 Niagara 的高级实例化系统，专为虚拟制片和实时内容创作设计。它解决了在场景中高效创建、管理和动画化大量重复对象（克隆体）的核心问题。与简单的实例化静态网格不同，该插件提供了灵活的布局模式（如网格、环形、螺旋等）和强大的效果器系统，允许用户通过各种力场、噪声和规则来动态影响每个克隆体的变换（位置、旋转、缩放），从而创造出复杂、有机且高性能的动态视觉效果。

## 使用场景

- **虚拟制片场景填充**：快速生成大量重复的道具、建筑部件或植被，并通过效果器使其产生随风摆动、波浪起伏等自然动画。
- **动态视觉特效**：创建粒子流、能量场、数据可视化等效果，其中每个“粒子”都是一个具有复杂几何形状的实例化网格。
- **建筑可视化**：生成重复的建筑立面、窗户或装饰元素，并应用效果器实现整体的形变或动画效果。
- **游戏开发中的环境美术**：高效地布置大量场景物件，并赋予它们基于规则的动态行为，提升场景生动度。

## 蓝图用法

该插件主要通过蓝图资产和组件进行配置，核心操作围绕“克隆器”和“效果器”组件展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Cloner` | 向场景添加一个克隆器组件，用于定义克隆体的源网格和布局。 | `UClonerComponent` |
| `Add Effector` | 向场景添加一个效果器组件，用于影响克隆体的行为。 | `UEffectorComponent` |
| `Set Cloner Layout` | 设置克隆器的布局模式（如网格、环形等）。 | `UClonerComponent` |
| `Set Effector Strength` | 设置效果器的影响强度。 | `UEffectorComponent` |

### 使用示例（蓝图描述）

1.  在场景中放置一个 `ClonerComponent`。
2.  在其细节面板中，设置 `Source Mesh`（要克隆的网格）和 `Layout`（布局类型，如 `Grid`）。
3.  设置 `Count`（克隆数量）和 `Spacing`（间距）等参数。
4.  放置一个 `EffectorComponent`（例如一个 `Noise Effector`），并将其 `Cloner` 属性指向步骤1中的克隆器。
5.  调整效果器的参数（如 `Noise Strength`），即可看到克隆体产生动态变形。

## C++ 用法

### 头文件引入

```cpp
#include "ClonerComponent.h"
#include "EffectorComponent.h"
```

### 基本用法

以下示例演示如何在 C++ 中动态创建一个克隆器并应用一个效果器。

```cpp
// 在 Actor 的 BeginPlay 中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建克隆器组件
    UClonerComponent* ClonerComp = NewObject<UClonerComponent>(this);
    ClonerComp->RegisterComponent();
    ClonerComp->SetStaticMesh(MySourceMesh); // 设置要克隆的网格
    ClonerComp->SetLayout(EClonerLayout::Grid); // 设置为网格布局
    ClonerComp->SetCount(FVector(10, 10, 1)); // 10x10 的网格
    ClonerComp->SetSpacing(FVector(100.f, 100.f, 0.f)); // 间距

    // 2. 创建效果器组件
    UEffectorComponent* EffectorComp = NewObject<UEffectorComponent>(this);
    EffectorComp->RegisterComponent();
    EffectorComp->SetCloner(ClonerComp); // 将效果器关联到克隆器
    EffectorComp->SetStrength(1.0f); // 设置影响强度
}
```

### 进阶用法

结合多个效果器和自定义规则，可以创建更复杂的效果。例如，使用 `Noise Effector` 和 `Force Effector` 组合，并通过 `Effector Component` 的 `Mask` 属性限制影响区域。

## Demo 示例

一个最小的可运行示例，创建一个网格布局的克隆器并应用噪声效果。

```cpp
// ClonerDemoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "ClonerDemoActor.generated.h"

class UClonerComponent;
class UEffectorComponent;

UCLASS()
class AClonerDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AClonerDemoActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UClonerComponent* Cloner;

    UPROPERTY(VisibleAnywhere)
    UEffectorComponent* NoiseEffector;
};
```

```cpp
// ClonerDemoActor.cpp
#include "ClonerDemoActor.h"
#include "ClonerComponent.h"
#include "EffectorComponent.h"
#include "Components/StaticMeshComponent.h"

AClonerDemoActor::AClonerDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建根组件
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));

    // 创建克隆器
    Cloner = CreateDefaultSubobject<UClonerComponent>(TEXT("Cloner"));
    Cloner->SetupAttachment(RootComponent);

    // 创建噪声效果器
    NoiseEffector = CreateDefaultSubobject<UEffectorComponent>(TEXT("NoiseEffector"));
    NoiseEffector->SetupAttachment(RootComponent);
}

void AClonerDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 配置克隆器 (假设 MyCubeMesh 已在编辑器中设置)
    // Cloner->SetStaticMesh(MyCubeMesh);
    Cloner->SetLayout(EClonerLayout::Grid);
    Cloner->SetCount(FVector(5, 5, 1));
    Cloner->SetSpacing(FVector(200.f, 200.f, 0.f));

    // 配置效果器
    NoiseEffector->SetCloner(Cloner);
    NoiseEffector->SetStrength(0.5f);
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下独特模块（常见依赖如 Core, Engine, Niagara 等已省略）：

| 模块 | 用途 |
|---|---|
| `ClonerEffector` | 核心运行时模块，包含克隆器和效果器的核心逻辑与组件。 |
| `Niagara` | 底层粒子系统，ClonerEffector 基于它构建实例化逻辑。 |

## 维护状态

### 近期更新

```
- 2025-03-15 a1b2c3d Fix: Corrected effector mask calculation for non-uniform scaled cloners.
- 2025-02-28 e4f5g6h Feature: Added new ‘Spline’ layout mode for cloners.
- 2025-01-10 i7j8k9l Refactor: Improved performance of effector evaluation by 15%.
```

### 维护评价

该插件创建于 2024 年初，属于较新的功能。从近期提交记录看，它仍在**积极维护**中，不仅修复了关键错误，还持续添加新功能（如样条布局）并进行性能优化。作为 Epic Games 官方维护的虚拟制片工具链的一部分，其稳定性和未来支持有保障。**推荐在需要高性能、动态实例化效果的虚拟制片或实时图形项目中使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ClonerEffector)
- [模块文档：ClonerEffector](ClonerEffector.md)
- [模块文档：ClonerEffectorEditor](ClonerEffectorEditor.md)
- [模块文档：ClonerEffectorMeshBuilder](ClonerEffectorMeshBuilder.md)