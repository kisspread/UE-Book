# ControlRigDynamics

> Support for simple dynamics/cosmetic simulation in control rig

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `ControlRigDynamics` (Runtime), `ControlRigDynamicsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ControlRigDynamics) | |

## 用途

ControlRigDynamics 插件为 Control Rig 动画系统添加了轻量级的动力学模拟功能。它并非一个完整的物理引擎，而是专注于实现“次级动画”效果，例如角色的头发、衣物、尾巴、饰品等附属物的自然摆动和跟随运动。该插件通过在 Control Rig 图表中引入专门的动力学节点，让动画师和开发者能够以程序化、可控的方式为动画添加物理真实感，而无需依赖复杂的物理资产或全身物理模拟。它解决了传统动画系统难以高效、美观地处理这类“装饰性”物理交互的问题。

## 使用场景

- 你在为角色制作头发、辫子或飘带动画，希望它们能随角色移动自然飘动，而不是完全手K动画。
- 你需要为角色的披风、斗篷、裙摆等衣物添加次级动画，使其在行走、奔跑时产生合理的摆动。
- 你想为角色的尾巴、耳朵、翅膀等附属物添加基于物理的跟随和弹跳效果。
- 你正在使用 Control Rig 构建程序化动画，并希望为其集成简单的动力学效果，例如让机械臂的线缆自然下垂。

## 蓝图用法

该插件的核心功能通过 Control Rig 的节点系统暴露。在 Control Rig 图表中，你可以找到并使用以下类型的动力学节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Simulation` | 动力学模拟的主节点，用于驱动一组骨骼或点的物理模拟。 | `URigUnit_Simulation` |
| `Spring` | 弹簧节点，用于在两个点之间创建弹性连接。 | `URigUnit_Spring` |
| `Point Collider` | 点碰撞体节点，为模拟点添加简单的球形碰撞。 | `URigUnit_PointCollider` |
| `Angular Constraint` | 角度约束节点，限制骨骼之间的旋转角度。 | `URigUnit_AngularConstraint` |

### 使用示例（蓝图描述）

1.  **基本头发摆动**：在 Control Rig 图表中，将角色头部骨骼连接到 `Simulation` 节点的 `Root` 引脚。将一系列代表发丝的骨骼链连接到 `Simulation` 节点的 `Points` 引脚。调整 `Simulation` 节点的 `Gravity`、`Damping` 和 `Stiffness` 参数来控制头发的重量和飘动感。
2.  **添加碰撞**：在 `Simulation` 节点之后，连接一个 `Point Collider` 节点。将角色的头部和肩部骨骼设置为碰撞体，防止头发穿入身体。
3.  **创建弹性连接**：使用 `Spring` 节点连接两个相邻的发丝骨骼，可以模拟发丝之间的轻微牵连效果。

## C++ 用法

### 头文件引入

```cpp
#include “ControlRigDynamics.h”
// 如果需要使用特定的动力学单元，可能需要包含更具体的头文件，例如：
#include “Units/Execution/RigUnit_Simulation.h”
```

### 基本用法

在 C++ 中，你通常不会直接实例化动力学节点，而是通过 Control Rig 的反射系统或蓝图来使用它们。但你可以查询和操作相关的控制台变量（CVar）来全局调整模拟行为。

```cpp
// 示例：在代码中启用或禁用动力学步进求解器
IConsoleVariable* CVarEnableStepSolver = IConsoleManager::Get().FindConsoleVariable(TEXT(“ControlRig.Dynamics.EnableStepSolver”));
if (CVarEnableStepSolver)
{
    CVarEnableStepSolver->Set(1); // 启用
    // CVarEnableStepSolver->Set(0); // 禁用
}
```
*（此示例基于 `ControlRigDynamicsCVarBindings.h` 中定义的 CVar 推断）*

### 进阶用法

对于需要深度集成或自定义动力学行为的场景，你可能需要继承并扩展 `URigUnit_Simulation` 或其他相关单元类。这通常涉及重写 `Execute` 方法来实现自定义的积分器或约束求解逻辑。由于这是实验性功能，相关 API 可能发生变化。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在自定义的 Control Rig 单元中引用动力学相关的类型。请注意，实际的动力学模拟通常在蓝图图表中配置。

**MyDynamicsRigUnit.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “Units/RigUnit.h”
#include “MyDynamicsRigUnit.generated.h”

USTRUCT(meta = (DisplayName = “My Custom Dynamics Node”, Category = “Dynamics”))
struct FMyDynamicsRigUnit : public FRigUnit
{
    GENERATED_BODY()

    RIGVM_METHOD()
    virtual void Execute(const FRigUnitContext& Context) override;

    // 输入引脚：要模拟的骨骼链
    UPROPERTY(meta = (Input))
    FRigElementKeyCollection BonesToSimulate;

    // 输出引脚：模拟后的变换结果
    UPROPERTY(meta = (Output))
    TArray<FTransform> SimulatedTransforms;
};
```

**MyDynamicsRigUnit.cpp**
```cpp
#include “MyDynamicsRigUnit.h”
#include “Units/Execution/RigUnit_Simulation.h” // 引用动力学相关头文件

void FMyDynamicsRigUnit::Execute(const FRigUnitContext& Context)
{
    // 这里可以调用底层的动力学模拟函数，或设置参数
    // 例如，获取全局的模拟设置
    // const FControlRigDynamicsSettings& Settings = GetDefault<UControlRigDynamicsSettings>()->Settings;

    // 实际的模拟逻辑通常由内置的 URigUnit_Simulation 处理。
    // 此自定义单元可能用于预处理输入或后处理输出。
    SimulatedTransforms.Reset();
    // ... 填充模拟结果 ...
}
```

## 模块依赖

要使用此插件，你的项目或模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心依赖，提供 Control Rig 动画系统框架。 |
| `PhysicsControl` | 提供底层的物理控制功能，被动力学节点用于实现约束和碰撞。 |

## 维护状态

### 近期更新

- 2026-04-24 `a0e35edd` Control Rig Dynamics - Debugging widget
- 2026-04-23 `c20a96e5` Control Rig Dynamics - Add cvars for visualization and debugging
- 2026-04-23 `f919acb2` Control rig dynamics - remove support for having colliders in the solver itself (an unnecessary comp
- 2026-04-23 `f9267d2f` Control Rig Dynamics - add input to the spawn nodes so the user can specify the default name of comp
- 2026-04-23 `a339e1e7` Control Rig Dynamics - Add support for confiners

### 维护评价

- **状态**: **实验性**。插件明确标记为 `IsExperimentalVersion: true`，且默认未启用 (`Installed: false`)。
- **活跃度**: 作为实验性功能，其 API 和功能集可能在引擎版本更新时发生重大变化或被移除。
- **推荐**: 适用于原型开发、技术预研或对次级动画有特定需求且愿意承担 API 变更风险的项目。不建议在需要长期稳定维护的生产项目中作为核心依赖使用。请密切关注引擎更新日志中关于此插件的状态变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ControlRigDynamics)
- [官方文档]() （暂无）
- [测试用例]() （暂未发现公开的测试用例）