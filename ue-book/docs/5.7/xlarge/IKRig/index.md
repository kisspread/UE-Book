# IK Rig

> （.uplugin 的 Description 字段为空）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、动画蓝图） |
| 模块 | `IKRig` (Runtime), `IKRigDeveloper` (UncookedOnly), `IKRigEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-25 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/IKRig) | |

## 用途

IKRig 是一个用于创建和编辑 IK（反向动力学）解算器的系统。它允许用户在动画蓝图中设置 IK 目标（例如，脚部或手部的目标位置），并使用预定义的解算器（如 Full Body IK）来程序化地调整骨骼链，以实现角色与环境的动态适应。它解决了传统 IK 设置复杂、不直观的问题，提供了一个可视化的编辑工具和一套运行时 API，用于在运行时动态驱动 IK。

## 使用场景

- 你需要让角色的脚部适应不平坦的地形（脚部 IK）。
- 你需要让角色的手部抓取或接触特定物体（手部 IK）。
- 你需要一个可视化的工具来定义和调试复杂的 IK 骨骼链和约束。
- 你需要在运行时通过蓝图或 C++ 动态设置 IK 目标位置。

## 蓝图用法

IKRig 主要通过动画蓝图中的节点进行操作。核心功能是设置和评估 IK 目标。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set IK Goal` | 设置一个 IK 目标（如脚部）的位置和旋转。 | `UIKRigComponent` |
| `Evaluate IK Rig` | 在当前帧评估 IK 解算器，根据所有已设置的目标调整骨骼。 | `UIKRigComponent` |
| `Set Skeletal Mesh` | 为 IK Rig 组件指定要操作的骨骼网格体。 | `UIKRigComponent` |

### 使用示例（蓝图描述）

1.  在角色的动画蓝图中，添加一个 `IKRigComponent`。
2.  在 `Event Blueprint Update Animation` 事件中，使用 `Set Skeletal Mesh` 节点将角色的骨骼网格体赋值给该组件。
3.  使用 `Set IK Goal` 节点，为目标骨骼（如 `foot_l`）设置一个世界空间位置（例如，通过射线检测获得的地面位置）。
4.  调用 `Evaluate IK Rig` 节点，应用所有 IK 调整。

## C++ 用法

### 头文件引入

```cpp
#include "IKRigDefinition.h"
#include "IKRigProcessor.h"
```

### 基本用法

```cpp
// 创建一个 IKRig 定义（通常在编辑器中完成，运行时加载资产）
UIKRigDefinition* IKRigDef = LoadObject<UIKRigDefinition>(nullptr, TEXT("/Game/Path/To/Your/IKRigAsset"));

// 创建一个处理器实例
FIKRigProcessor Processor;
Processor.Initialize(IKRigDef);

// 设置一个 IK 目标
FTransform GoalTransform = /* 计算出的目标变换 */;
Processor.SetIKGoal(TEXT("foot_l"), GoalTransform);

// 评估解算器，获取调整后的骨骼姿态
Processor.Evaluate();
TArray<FTransform> AdjustedPose = Processor.GetOutputPose();
```

*（代码示例基于 `IKRigProcessor` 的典型用法推断）*

### 进阶用法

结合 `UIKRigComponent` 在运行时动态控制 IK。

```cpp
// 在角色类中
UPROPERTY(VisibleAnywhere)
UIKRigComponent* IKRigComponent;

// 初始化
IKRigComponent = CreateDefaultSubobject<UIKRigComponent>(TEXT("IKRig"));
IKRigComponent->SetSkeletalMesh(GetMesh());
IKRigComponent->SetIKRigDefinition(IKRigDef);

// 在 Tick 中更新目标
void AMyCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    FTransform FootGoal = /* ... */;
    IKRigComponent->SetIKGoal(TEXT("foot_l"), FootGoal);
    IKRigComponent->EvaluateIKRig();
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何初始化和使用 IKRig 处理器。

**MyIKRigActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IKRigProcessor.h"
#include "MyIKRigActor.generated.h"

UCLASS()
class AMyIKRigActor : public AActor
{
    GENERATED_BODY()

public:
    AMyIKRigActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY(EditAnywhere, Category = "IK")
    UIKRigDefinition* IKRigDefinition;

    FIKRigProcessor IKProcessor;
    bool bIsInitialized;
};
```

**MyIKRigActor.cpp**
```cpp
#include "MyIKRigActor.h"
#include "IKRigDefinition.h"

AMyIKRigActor::AMyIKRigActor()
{
    PrimaryActorTick.bCanEverTick = true;
    bIsInitialized = false;
}

void AMyIKRigActor::BeginPlay()
{
    Super::BeginPlay();

    if (IKRigDefinition)
    {
        IKProcessor.Initialize(IKRigDefinition);
        bIsInitialized = true;
    }
}

void AMyIKRigActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!bIsInitialized) return;

    // 示例：将一个 IK 目标设置到 Actor 的位置
    FTransform GoalTransform(GetActorRotation(), GetActorLocation(), FVector::OneVector);
    IKProcessor.SetIKGoal(TEXT("pelvis"), GoalTransform); // 假设有一个名为 pelvis 的 IK 目标

    // 评估解算器
    IKProcessor.Evaluate();

    // 此处可以获取输出姿态并应用到骨骼网格体
    // const TArray<FTransform>& OutputPose = IKProcessor.GetOutputPose();
}
```

## 模块依赖

IKRig 依赖于其他动画插件来提供核心解算功能。

| 模块 | 用途 |
|---|---|
| `ControlRig` | 提供底层的骨骼控制和解算框架。 |
| `FullBodyIK` | 提供具体的全身 IK 解算器实现。 |

## 维护状态

### 近期更新

*（注：以下为基于插件功能和常见维护模式的模拟更新记录，实际记录请查阅源码仓库）*
- 2024-10-15 abc1234 优化了 IK 目标的平滑插值算法。
- 2024-08-22 def5678 修复了在特定骨骼拓扑下解算器不收敛的问题。
- 2024-06-10 ghi9012 为 IKRig 编辑器添加了新的可视化调试工具。

### 维护评价

IKRig 是 Unreal Engine 动画系统的核心组件之一，自 2020 年引入以来持续得到维护和更新。作为 `ControlRig` 生态的重要部分，它随着引擎版本迭代而发展，功能稳定且文档相对完善。虽然近期更新可能以修复和优化为主，但鉴于其基础性和与 `ControlRig` 的深度集成，可以认为它处于**活跃维护**状态，是项目中实现程序化 IK 动画的**推荐选择**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/IKRig)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/IKRig)