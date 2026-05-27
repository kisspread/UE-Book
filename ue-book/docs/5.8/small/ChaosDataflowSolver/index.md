# ChaosDataflowSolver

> 

| 属性 | 值 |
|---|---|
| 中文名 | 混沌数据流求解器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosDataflowSolver` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosDataflowSolver) | |

## 用途

该插件提供了一个基于 Dataflow 图的 Chaos 物理求解器 Actor，允许用户通过 Dataflow 框架驱动物理模拟流程。它解决的核心问题是：将 Chaos 物理引擎的刚体模拟与 Unreal 的 Dataflow 系统整合，使用户能够使用节点图方式定义和控制物理模拟的进阶逻辑。

插件的主要工作流程是：
1. 创建一个 `AChaosDataflowSolverActor` 作为独立的物理求解器
2. 将场景中的 Primitive Component（静态网格、实例化静态网格等）绑定到该求解器
3. 求解器根据指定的 Dataflow Simulation Asset 驱动物理模拟
4. 模拟结果回写到绑定的组件上（更新变换）

目前骨骼网格组件（Skeletal）和地形组件（Landscape）的接口为空桩，尚未实现。

## 使用场景

- 你需要在 Dataflow 图中定义自定义的物理模拟逻辑，而不是使用默认的 Chaos 物理场景
- 你想将多个物体的物理模拟集中到一个自定义求解器中管理，独立于主物理世界
- 你需要对物理模拟的读写时机进行精确控制（通过 `WriteToSimulation` / `ReadFromSimulation` 回调）
- 你在开发基于节点图的程序化物理效果系统

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSolverActive` | 启用或禁用求解器的模拟能力 | `AChaosDataflowSolverActor` |

### 使用示例（蓝图描述）

1. **设置求解器 Actor**：在场景中放置一个 `AChaosDataflowSolverActor`，在 Details 面板中指定 `SimulationAsset`（Dataflow Simulation Asset）。

2. **绑定物理组件**：在需要参与模拟的 Actor 上添加 `UChaosSolverBindingComponent`，将其 `SimulationActor` 属性指向场景中的 `AChaosDataflowSolverActor`。可设置 `bKeepKinematicInOriginal` 控制是否保留原始运动学状态。

3. **控制模拟开关**：在运行时通过 `SetSolverActive(false)` 暂停模拟，或 `SetSolverActive(true)` 恢复模拟。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosDataflowSolverActor.h"
#include "ChaosSolverBindingComponent.h"
#include "RigidAssetUserData.h"
```

### 基本用法

创建并使用 Dataflow 物理求解器 Actor：

```cpp
// 在世界中 Spawn 求解器 Actor
FActorSpawnParameters SpawnParams;
AChaosDataflowSolverActor* SolverActor = GetWorld()->SpawnActor<AChaosDataflowSolverActor>(
    AChaosDataflowSolverActor::StaticClass(), FTransform::Identity, SpawnParams);

// 配置 Dataflow Simulation Asset（通过 FDataflowSimulationAsset）
// SolverActor->SimulationAsset = ...;

// 注册物理组件到求解器
SolverActor->RegisterPhysicsComponent(MyPrimitiveComponent);

// 控制模拟状态
SolverActor->SetSolverActive(true);
```

（基于 `ChaosDataflowSolverActor.h` 中的接口）

### 进阶用法

自定义求解器行为——通过继承 `AChaosDataflowSolverActor` 并实现 `IDataflowPhysicsSolverInterface` 的虚函数来控制模拟流程：

```cpp
// IDataflowPhysicsSolverInterface 的关键回调：
// WriteToSimulation()  - 将游戏线程数据写入模拟线程
// ReadFromSimulation() - 从模拟线程读取结果到游戏线程
// BuildSimulationProxy() - 构建模拟代理
// ResetSimulationProxy() - 重置模拟代理
```

对于实例化静态网格，`InstancedRigidComponentInterface` 会为每个实例创建独立的刚体，但设为 Static 类型。对于普通 Primitive Component，`PrimitiveRigidComponentInterface` 会根据原始 BodyInstance 的设置创建 Kinematic 或 Dynamic 刚体，并在每帧结束时将模拟变换回写到组件。

（基于 `PrimitiveRigidComponentInterface.h` 和 `InstancedRigidComponentInterface.h`）

## Demo 示例

```cpp
// MySolverActor.h
#pragma once
#include "CoreMinimal.h"
#include "ChaosDataflowSolverActor.h"
#include "MySolverActor.generated.h"

UCLASS()
class AMySolverActor : public AChaosDataflowSolverActor
{
    GENERATED_BODY()

public:
    AMySolverActor();
};
```

```cpp
// MySolverActor.cpp
#include "MySolverActor.h"

AMySolverActor::AMySolverActor()
{
    PrimaryActorTick.bCanEverTick = true;
}
```

## 模块依赖

该插件对 Chaos 物理 API 和 Dataflow 系统有较深的依赖，但具体依赖项需要查看 `Build.cs` 文件（未提供完整内容）。从源码分析可推断以下依赖：

| 模块 | 用途 |
|---|---|
| `DataflowSimulation` | Dataflow 模拟资产和上下文（`FDataflowSimulationAsset`, `FDataflowSimulationContext`） |
| `Chaos` | Chaos 物理引擎核心（`FRigidSceneHandle`, `FRigidBodyHandle`, 刚体创建和管理） |
| `PhysicsCore` | 物理核心（`FBodyInstance`, `UBodySetup`, 碰撞数据构建） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-09 | `f167027d` | Fix a deprecation warning in ChaosDataFlowSolver. | 修复弃用警告 |
| 2026-04-08 | `6d6dbc44` | Chaos API: Adding PhysicsService and removing the dependecy of the async plugin on dataflow. | 重构物理服务，解除异步插件对 dataflow 的依赖 |
| 2026-03-04 | `3c8f6206` | Chaos API: Shape Instance Part 1 | Chaos API 形状实例功能第一部分 |
| 2026-02-27 | `7a513cdb` | Chaos API: Fixing an issue where rigid object pointers could be casted to unrelated context types. | 修复刚体指针类型转换错误 |
| 2026-02-26 | `70865526` | Include Rigid Headers | 添加刚体头文件引用 |

### 维护评价

- **状态**：🆕 全新插件（创建于 2026-02-25，约 2 个月前）
- **实验性**：标记为 `IsExperimentalVersion=true`，且 `Installed=false`，属于 Chaos 物理系统正在开发中的新功能
- **活跃度**：创建后持续有更新，属于活跃开发阶段
- **完整度**：骨骼网格和地形组件接口为空桩，说明该插件仍处于早期开发阶段
- **已知限制**：
  - `GetSimulationProxy()` 固定返回 `nullptr`，说明模拟代理机制尚未完善
  - 实例化网格组件创建的刚体固定为 Static 类型，不支持动态模拟
  - 需要手动启用（`Installed=false`）

⚠️ **该插件为实验性功能，API 可能发生重大变化，不建议在生产项目中使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosDataflowSolver)
- [Actor 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/ChaosDataflowSolver/Source/ChaosDataflowSolver/Public/ChaosDataflowSolverActor.h)
- [绑定组件头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/ChaosDataflowSolver/Source/ChaosDataflowSolver/Public/ChaosSolverBindingComponent.h)