# ControlRigDynamics

> Support for simple dynamics/cosmetic simulation in control rig

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ControlRigDynamics` (Runtime), `ControlRigDynamicsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ControlRigDynamics) | |

## 用途

ControlRigDynamics 插件为 ControlRig 框架添加了轻量级的动力学模拟功能。它并非用于替代完整的物理引擎，而是专注于实现角色动画中的“次级动画”（Secondary Animation）效果，例如头发、布料、尾巴、饰品等的物理摆动和跟随运动。该插件通过在 ControlRig 内部集成简单的动力学节点，让动画师能够在熟悉的 ControlRig 环境中直接为骨骼添加物理驱动的动态效果，无需切换到复杂的物理资产或蓝图系统，从而简化工作流程并提升动画的真实感。

## 使用场景

- 你需要为角色的头发、披风、尾巴等部件添加自然的物理摆动效果。
- 你正在使用 ControlRig 制作动画，并希望为其添加简单的物理反馈，如武器挥舞后的惯性、角色跳跃落地时的缓冲等。
- 你希望在不引入完整物理模拟系统开销的情况下，为动画增添动态细节。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `ControlRigDynamics` | Runtime | 提供核心的动力学模拟功能、节点和组件，可在运行时执行。 |
| `ControlRigDynamicsEditor` | Editor | 提供编辑器内的工具、自定义节点和资产类型，用于在 ControlRig 编辑器中设置和调试动力学效果。 |

## 蓝图用法

该插件主要通过 ControlRig 的图表节点进行操作。核心功能封装在 `UControlRigDynamicsComponent` 和相关的 ControlRig 节点中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Dynamics Component` | 为 ControlRig 实例添加一个动力学组件，用于管理模拟状态。 | `UControlRigDynamicsComponent` |
| `Set Dynamics Parameters` | 设置动力学模拟的参数，如刚度、阻尼、重力等。 | `UControlRigDynamicsComponent` |
| `Solve Dynamics` | 在 ControlRig 的求值链中执行一次动力学模拟步骤。 | `UControlRigDynamicsNode` |

### 使用示例（蓝图描述）

1.  在你的 ControlRig 资产中，从节点面板拖入 `Add Dynamics Component` 节点，并将其连接到 `Construction Script` 或 `Forward Solve` 事件。
2.  使用 `Set Dynamics Parameters` 节点配置模拟参数（如刚度、阻尼），并将目标骨骼链连接到该节点。
3.  在动画求值流程中，将 `Solve Dynamics` 节点放置在需要应用物理效果的位置，通常在动画输入之后、最终输出之前。

## C++ 用法

### 头文件引入

```cpp
#include "ControlRigDynamicsComponent.h"
// 用于访问动力学相关的 ControlRig 节点
#include "ControlRigDynamicsNodes.h"
```

### 基本用法

在 C++ 中，通常通过获取或创建 `UControlRigDynamicsComponent` 来与动力学系统交互。

```cpp
// 假设你有一个 AActor* MyActor 和一个 UControlRig* MyControlRig
// 获取或添加动力学组件
UControlRigDynamicsComponent* DynComp = MyActor->FindComponentByClass<UControlRigDynamicsComponent>();
if (!DynComp)
{
    DynComp = NewObject<UControlRigDynamicsComponent>(MyActor);
    DynComp->RegisterComponent();
}

// 将组件与 ControlRig 实例关联
DynComp->SetControlRig(MyControlRig);

// 在每帧或动画更新时，手动触发模拟（如果组件未设置为自动更新）
DynComp->SolveDynamics(MyControlRig->GetDeltaTime());
```

### 进阶用法

可以继承 `UControlRigDynamicsComponent` 来创建自定义的动力学行为，或通过 `FControlRigDynamicsSettings` 结构体精细控制模拟参数。

```cpp
// 自定义动力学组件
class UMyCustomDynamicsComponent : public UControlRigDynamicsComponent
{
    // 重写 SolveDynamics 以添加自定义逻辑
    virtual void SolveDynamics(float DeltaTime) override
    {
        // 在模拟前应用自定义力
        ApplyCustomForces();
        Super::SolveDynamics(DeltaTime);
    }
};

// 配置模拟参数
FControlRigDynamicsSettings Settings;
Settings.Stiffness = 100.0f;
Settings.Damping = 0.5f;
Settings.Gravity = FVector(0, 0, -980.0f);
DynComp->SetDynamicsSettings(Settings);
```

## Demo 示例

以下是一个最小化的 Actor 示例，展示如何在 C++ 中设置和使用 ControlRigDynamics。

**MyDynamicCharacter.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyDynamicCharacter.generated.h"

class UControlRigComponent;
class UControlRigDynamicsComponent;

UCLASS()
class AMyDynamicCharacter : public AActor
{
    GENERATED_BODY()

public:
    AMyDynamicCharacter();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
    UControlRigComponent* ControlRigComp;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
    UControlRigDynamicsComponent* DynamicsComp;
};
```

**MyDynamicCharacter.cpp**
```cpp
#include "MyDynamicCharacter.h"
#include "ControlRigComponent.h"
#include "ControlRigDynamicsComponent.h"

AMyDynamicCharacter::AMyDynamicCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    ControlRigComp = CreateDefaultSubobject<UControlRigComponent>(TEXT("ControlRig"));
    RootComponent = ControlRigComp;

    DynamicsComp = CreateDefaultSubobject<UControlRigDynamicsComponent>(TEXT("Dynamics"));
}

void AMyDynamicCharacter::BeginPlay()
{
    Super::BeginPlay();
    // 关联动力学组件与 ControlRig
    if (DynamicsComp && ControlRigComp)
    {
        DynamicsComp->SetControlRig(ControlRigComp->GetControlRig());
    }
}

void AMyDynamicCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 动力学组件通常会自动更新，但也可以手动触发
    // if (DynamicsComp) DynamicsComp->SolveDynamics(DeltaTime);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心依赖，提供 ControlRig 框架和动画求值系统。 |
| `PhysicsControl` | 提供底层的物理控制功能，可能被动力学节点用于更复杂的物理交互。 |

## 维护状态

### 近期更新

- 2026-04-24 `a0e35edd` Control Rig Dynamics - 调试控件
- 2026-04-23 `c20a96e5` Control Rig Dynamics - 为可视化与调试添加控制台变量
- 2026-04-23 `f919acb2` Control rig dynamics - 移除求解器自身包含碰撞体的支持（一项不必要的复杂性）
- 2026-04-23 `f9267d2f` Control Rig Dynamics - 为生成节点添加输入，以便用户指定组件的默认名称
- 2026-04-23 `a339e1e7` Control Rig Dynamics - 添加对约束器的支持

### 维护评价

该插件近期提交频率高，时间集中，表明处于**活跃开发**阶段。提交内容主要集中在功能增强（如添加约束器支持、自定义组件名称）和开发体验优化（调试工具、可视化变量），显示出明确的迭代方向。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ControlRigDynamics)
- [ControlRig 官方文档](https://docs.unrealengine.com/5.7/en-US/control-rig-in-unreal-engine/)（父框架文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ControlRigDynamics/Tests)（如果存在）