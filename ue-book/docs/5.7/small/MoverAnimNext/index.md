# Mover UAF

> This plugin adds UAF support for the Mover plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 移动动画桥接 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MoverAnimNext` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverAnimNext) | |

## 用途

**MoverAnimNext** 是连接 **Mover**（角色移动系统）与 **UAF**（Unreal Animation Framework，即 AnimNext 动画框架）的桥梁插件。它提供了一组在 AnimNext 动画图表中直接使用的轨迹生成与分析节点，使动画逻辑能够实时感知并响应 Mover 组件的历史轨迹和预测轨迹。

**解决的问题**：在基于 AnimNext 的动画系统中，需要根据角色的运动状态（如速度、角速度、未来轨迹）来驱动动画混合。Mover 本身不直接与 AnimNext 打通，本插件通过封装 MoverComponent 的轨迹缓冲区，将其暴露为 AnimNext 的 RigUnit 节点，从而让动画师/程序员可以在动画图表中直接使用这些运动数据，无需手动将 Mover 数据传递给动画蓝图。

## 使用场景

- 你正在使用 **Mover** 插件构建角色移动（如步行、奔跑、游泳、飞行），并同时使用 **AnimNext** 作为动画系统。
- 你需要动画根据角色历史位置（如拐弯时的离心力）或未来预测轨迹（如跳跃前的预压缩）做出姿态调整。
- 你想在动画图表中直接获取 Mover 生成的速度、角速度等运动学量，用于驱动动画参数。

## 蓝图用法

> **注意**：这些节点并非标准的 BlueprintCallable 函数，而是作为 **RigVM** 节点出现在 AnimNext 动画图表中（类似于 Control Rig 的 RigUnit）。在 AnimNext 蓝图编辑器中，可以通过右键菜单添加。以下节点统一继承自 `FRigUnit_AnimNextBase`，具有执行上下文引脚。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Generate Trajectory from Mover` | 从 Mover 组件生成一段历史轨迹和预测轨迹，输出为 `FTransformTrajectory` | `FRigUnit_GenerateMoverTrajectory` |
| `Get Trajectory Sample At Time` | 在轨迹中查询指定时间处的位姿样本（位置、旋转、速度等） | `FRigUnit_GetTrajectorySampleAtTime` |
| `Get Trajectory Velocity` | 计算轨迹中两个时间点之间的线速度 | `FRigUnit_GetTrajectoryVelocity` |
| `Get Trajectory Angular Velocity` | 计算轨迹中两个时间点之间的角速度 | `FRigUnit_GetTrajectoryAngularVelocity` |
| `Mover Component Tick Functions`（依赖 Trait） | 声明模块事件依赖，确保动画图表在 Mover 的指定 tick 阶段之后运行 | `FRigVMTrait_ModuleEventDependency_MoverComponentTickFunctions` |

### 使用示例（蓝图描述）

1. **生成轨迹**：在 AnimNext 图表中放置 `Generate Trajectory from Mover` 节点，连接 `Execute Context` 引脚。将 `MoverComponent` 引脚连接到角色的 Mover 组件引用（或通过 `Get Mover Component` 节点获取）。设置 `DeltaTime`（当前帧增量时间）、`HistorySamplingInterval` 等参数。输出 `InOutTrajectory` 是一个 `FTransformTrajectory`，包含历史部分（负时间）和预测部分（正时间）。

2. **查询轨迹样本**：将上一步的 `OutTrajectory` 连接到 `Get Trajectory Sample At Time` 的 `InTrajectory` 输入。设置 `Time`（秒，例如 0.3 表示未来 0.3 秒），勾选 `bExtrapolate` 可允许在轨迹范围外推算。输出 `OutTrajectorySample` 包含 `Transform`、`LinearVelocity`、`AngularVelocity` 等。

3. **计算速度**：使用 `Get Trajectory Velocity` 或 `Get Trajectory Angular Velocity` 计算任意两个时间点之间的速度，用于驱动动画混合空间。

4. **依赖配置**：在 AnimNext 模块的依赖表中添加 `Mover Component Tick Functions` Trait，并设置 `DependentMoverTickPhase`（例如 `ApplyState`、`SimulationUpdate`），以确保动画图表在 Mover 更新之后执行。

## C++ 用法

### 头文件引入

```cpp
#include "MoverAnimNextModule.h"
#include "Graph/RigUnit_GenerateMoverTrajectory.h"
#include "Graph/RigUnit_TrajectoryAnalysis.h"
#include "Module/RigVMTrait_ModuleEventDependency_MoverComponentTickFunctions.h"
```

### 基本用法

该插件通常只在 AnimNext 图表中通过节点调用，C++ 直接手动执行节点的场景较少。但以下示例展示了如何通过 RigVM 手动调用 `FRigUnit_GenerateMoverTrajectory` 并获取结果。

```cpp
// 来自测试用例（假设路径：Engine/Plugins/Experimental/MoverAnimNext/Tests/...）
// 注意：实际插件暂无公开测试，以下为示意用法

FRigUnit_GenerateMoverTrajectory TrajectoryUnit;
TrajectoryUnit.MoverComponent = MyMoverComponent;
TrajectoryUnit.DeltaTime = 0.016f;
TrajectoryUnit.HistorySamplingInterval = -1.f; // 默认可自动推断
TrajectoryUnit.NumHistorySamples = 30;
TrajectoryUnit.PredictionSamplingInterval = 0.1f;
TrajectoryUnit.NumPredictionSamples = 15;
TrajectoryUnit.MoverSamplingFrameRate = FFrameRate(60, 1);
TrajectoryUnit.InOutTrajectory = FTransformTrajectory();

// 设置执行上下文（通常由 AnimNext 框架提供）
FAnimNextExecuteContext ExecuteContext;
TrajectoryUnit.ExecuteContext = ExecuteContext;

// 执行 RIGVM 方法（内部处理逻辑）
TrajectoryUnit.Execute();

// 获取生成的轨迹
const FTransformTrajectory& GeneratedTrajectory = TrajectoryUnit.InOutTrajectory;
```

### 进阶用法

与 `FRigVMTrait_ModuleEventDependency_MoverComponentTickFunctions` 结合使用，可以在 C++ 代码中通过 UAF 模块依赖系统注册自定义依赖：

```cpp
#include "Module/RigVMTrait_ModuleEventDependency.h"
#include "MoverComponent.h"

void SetupCustomDependency(UMoverComponent* MoverComp)
{
    // 创建一个依赖描述
    FRigVMTrait_ModuleEventDependency_MoverComponentTickFunctions Dependency;
    Dependency.DependentMoverTickPhase = EMoverTickPhase::ApplyState;

    // 在模块上下文中注册（简化写法）
    UE::UAF::FModuleDependencyContext Context;
    Context.MoverComponent = MoverComp;
    Dependency.OnAddDependency(Context);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Mover` | 提供角色移动系统和 `UMoverComponent`，是本插件的数据来源 |
| `UAF`（AnimNext） | 提供动画框架、RigVM 执行环境、模块事件依赖等基础设施 |

## 维护状态

### 近期更新

- 2025-10-15 `9780bd1` Fix crash in RigUnit_GenerateMoverTrajectory
- 2025-10-14 `a57af5c` Allow sampling of mover trajectory at a different (higher frequency) rate than we output to the trajectory
- 2025-10-03 `ff6147e` Updated UAF Trajectory functions to have an execution pin.
- 2025-06-26 `effdabd` UAF: Moved/renamed AnimNext and AnimNextAnimGraph plugins
- 2025-06-25 `bdc91c5` UAF: Namespace renamed

### 维护评价

| 维度 | 评价 |
|---|---|
| 创建时间 | 2025-06-25，不到半年 |
| 更新频率 | 密集，最近一个月内仍有功能性更新和修复 |
| 活跃度 | ✅ 活跃维护中，项目处于早期迭代阶段，持续增加新特性 |
| 已知问题 | 当前仅支持 standalone（非网络）模式，网络环境下 Mover 后端兼容性待验证 |
| 推荐使用 | 适合与 Mover + AnimNext 配合的早期采用者，注意实验性标签，API 可能变动 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverAnimNext)
- [Mover 插件文档](https://docs.unrealengine.com/5.7/en-US/mover-plugin-in-unreal-engine/)（Epic 官方）
- [AnimNext 概述](https://docs.unrealengine.com/5.7/en-US/animnext-overview/)