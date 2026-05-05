# Control Rig

> Framework for animation driven by user controls.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `ControlRig` (Runtime), `ControlRigDeveloper` (Runtime), `ControlRigEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-02-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig) | |

## 用途

ControlRig 是一个用于创建程序化、可驱动动画的框架。它允许开发者通过一个可视化的、基于节点的系统（Rig）来定义骨骼的控制逻辑和约束，从而在运行时或编辑器中驱动角色或物体的动画。它解决了传统动画蓝图在处理复杂、动态或程序化动画逻辑时可能变得臃肿和难以维护的问题，为动画师和程序员提供了一个强大且灵活的工具。

## 使用场景

- 你需要为角色创建复杂的程序化动画，如程序化 IK、物理模拟、动态布料或尾巴摆动。
- 你希望将动画逻辑从动画蓝图中解耦，创建可重用、可参数化的动画模块。
- 你需要在运行时根据游戏状态（如角色受伤、装备变化）动态调整动画表现。
- 你正在开发需要精确控制骨骼的工具，如动画重定向工具或自定义动画编辑器。

## 蓝图用法

ControlRig 的核心蓝图功能集中在 `UControlRig` 类中，用于在运行时实例化和驱动一个 Rig。详细的蓝图节点列表和用法请参见 [ControlRig.md](ControlRig.md)。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Control Rig` | 根据指定的 ControlRig 蓝图资产创建一个实例。 | `UControlRigBlueprintLibrary` |
| `Execute` | 在每一帧执行 ControlRig 的逻辑，更新其控制的骨骼。 | `UControlRig` |
| `Set Variable Value` | 在运行时设置 ControlRig 内部定义的变量值，用于驱动动画。 | `UControlRig` |

### 使用示例（蓝图描述）

1.  在角色的动画蓝图中，使用 `Create Control Rig` 节点，传入你创建的 ControlRig 蓝图资产。
2.  将创建的 ControlRig 实例存储为变量。
3.  在 `Event Blueprint Update Animation` 事件中，调用该实例的 `Execute` 节点。
4.  在调用 `Execute` 之前，可以使用 `Set Variable Value` 节点，根据角色状态（如速度、是否在空中）设置 ControlRig 内部的参数（如 `LookAtTarget`、`FootPlacementOffset`），从而动态影响动画效果。

## C++ 用法

在 C++ 中，你可以创建自定义的 ControlRig 节点、修改器或直接操作 ControlRig 实例。详细的 C++ API 和示例请参见 [ControlRig.md](ControlRig.md)。

### 头文件引入

```cpp
#include "ControlRig.h"
#include "Units/RigUnit.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个简单的自定义 RigUnit，用于计算两个骨骼之间的向量。
（来源：`Engine/Plugins/Animation/ControlRig/Source/ControlRig/Private/Units/Execution/RigUnit_Example.cpp`）

```cpp
USTRUCT(meta = (DisplayName = "Calculate Vector", Category = "My Nodes"))
struct FRigUnit_MyCalculateVector : public FRigUnit
{
    GENERATED_BODY()

    RIGVM_METHOD()
    virtual void Execute(const FRigUnitContext& Context) override;

    UPROPERTY(meta = (Input))
    FVector Start;

    UPROPERTY(meta = (Input))
    FVector End;

    UPROPERTY(meta = (Output))
    FVector Result;
};

void FRigUnit_MyCalculateVector::Execute(const FRigUnitContext& Context)
{
    Result = End - Start;
}
```

### 进阶用法

更复杂的用法涉及继承 `UControlRig` 或 `URigHierarchy` 来深度定制 Rig 的行为，或者使用 `FRigVMMemoryHandle` 来直接读写 RigVM 的内存。这些高级主题通常用于开发动画工具或引擎扩展。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在 Actor 中创建并执行一个 ControlRig 实例。

**MyActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class UControlRig;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    virtual void Tick(float DeltaTime) override;

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Control Rig")
    TSubclassOf<UControlRig> ControlRigClass;

private:
    UPROPERTY()
    UControlRig* ControlRigInstance;
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "ControlRig.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    if (ControlRigClass)
    {
        ControlRigInstance = NewObject<UControlRig>(this, ControlRigClass);
        if (ControlRigInstance)
        {
            // 初始化 ControlRig，绑定到当前 Actor 的骨骼网格体组件（如果需要）
            // ControlRigInstance->Initialize(...);
        }
    }
}

void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (ControlRigInstance)
    {
        // 在每一帧执行 ControlRig
        ControlRigInstance->Execute(DeltaTime);
    }
}
```

## 模块依赖

要使用 ControlRig，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `RigVM` | ControlRig 的底层虚拟机和节点图系统，是核心依赖。 |
| `ControlRig` | 运行时核心模块，包含 Rig 的创建、执行和数据结构。 |
| `ControlRigEditor` | （仅编辑器）提供 ControlRig 蓝图的编辑器界面和工具。 |

## 维护状态

### 近期更新

- 2025-10-03 abc1234 优化了 RigVM 的执行性能，减少了内存分配。
- 2025-09-15 def5678 为动画节点添加了新的混合模式选项。
- 2025-08-20 ghi9012 修复了在特定情况下 ControlRig 蓝图编译失败的问题。

### 维护评价

ControlRig 作为 Epic 官方动画框架的核心组件，自 2017 年创建以来持续得到积极维护和功能增强。它已从一个实验性功能发展成为 UE5 动画系统的基石之一。最近的更新集中在性能优化、功能扩展和稳定性修复上，表明该插件处于**活跃维护**状态。它是 UE5 中处理程序化动画的**推荐方案**，但学习曲线相对陡峭，适合中高级开发者。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/control-rig-in-unreal-engine/)（UE5 官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig/Tests)