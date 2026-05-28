# Mover AnimNext

> This plugin adds UAF support for the Mover plugin.

| 属性 | 值 |
|---|---|
| 中文名 | Mover 动画桥接 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MoverAnimNext` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverAnimNext) | |

## 用途

MoverAnimNext 插件是连接 Unreal Engine 的 **Mover 运动系统**与下一代动画框架 **UAF** 的桥梁。

Mover 负责角色的物理运动模拟（移动、跳跃等），而 UAF (Universal Animation Framework) 是一个基于图（Graph）的新动画系统。该插件的核心功能是：

1.  **轨迹生成与预测**：允许在 UAF 的动画图（AnimNext 图）中，基于 Mover 组件的当前状态和历史数据，生成和预测角色的未来运动轨迹。这对于动画预测、融合和姿态生成至关重要。
2.  **模块事件依赖管理**：提供一种结构化的方式，让 UAF 模块能够声明对 Mover 特定更新阶段（Tick Phase）的依赖，从而精确控制动画更新与物理模拟的先后顺序。
3.  **根运动切换**：提供在运行时从动画图中切换 Mover 根运动（Root Motion）状态的功能。

简而言之，这个插件解决了让基于物理的运动系统（Mover）能够与高级、灵活的新动画系统（UAF）协同工作的问题，使动画能实时响应并预测物理运动。

## 使用场景

-   你正在使用 **Mover** 插件处理角色运动（如行走、跑步、跳跃），并希望使用 **UAF (AnimNext)** 来驱动角色的动画，且需要动画能够感知和预测物理运动结果。
-   你需要根据角色的运动历史（过去几帧的位置、速度）和未来预测（计划执行的动作）来生成更精准、连贯的动画。
-   你需要确保动画的播放（例如脚踩地的时机）与物理模拟严格同步，避免“滑步”等穿帮现象。
-   你希望在运行时根据游戏逻辑（例如是否进入空中）动态地从动画蓝图中切换角色的根运动开关。

## 蓝图用法

该插件主要通过 **RigVM 节点**（在 UAF 动画图中使用）和 **USTRUCT** 来提供蓝图接口。

### 核心节点 (RigVM)

这些节点可以在 UAF 的动画图编辑器中搜索并使用。

| 节点 | 说明 | 所在结构体 |
|---|---|---|
| `Generate Trajectory from Mover` | 根据 Mover 组件、历史和预测参数生成一个 `FTransformTrajectory`（变换轨迹）。这是该插件最核心的节点。 | `FRigUnit_GenerateMoverTrajectory` |
| `Get Trajectory Sample At Time` | 从输入的轨迹中，在指定时间点采样，返回该点的位置、旋转等信息。 | `FRigUnit_GetTrajectorySampleAtTime` |
| `Get Trajectory Velocity` | 计算轨迹上两个时间点之间的线速度。 | `FRigUnit_GetTrajectoryVelocity` |
| `Get Trajectory Angular Velocity` | 计算轨迹上两个时间点之间的角速度。 | `FRigUnit_GetTrajectoryAngularVelocity` |
| `Mover Toggle Root Motion` | 切换指定 Mover 组件的根运动启用状态。 | `FRigUnit_MoverToggleRootMotion` |

### 模块事件依赖 (USTRUCT)

用于在 UAF 模块的设置中声明依赖关系，确保正确的更新顺序。

| 结构体 | 说明 |
|---|---|
| `Mover Component Tick Functions` | 表示对当前 Actor 上首个 `MoverComponent` 特定更新阶段（`DependentMoverTickPhase`）的依赖。用于控制动画模块在 Mover 的某个阶段之前或之后执行。 |

### 使用示例（蓝图描述）

**场景：在动画图中生成并使用运动轨迹**

1.  在你的 UAF 动画图（如 `PrePhysics` 或 `Update` 图）中，添加一个 `Generate Trajectory from Mover` 节点。
2.  将 `MoverComponent` 输入引脚连接到角色身上对应的 `MoverComponent`（可通过 `Get Component By Class` 节点获取）。
3.  根据需求设置 `DeltaTime`、`NumHistorySamples` 和 `NumPredictionSamples` 等参数。
4.  节点的 `InOutTrajectory` 输出引脚将包含生成的完整轨迹。
5.  将这个轨迹输出连接到后续的 `Get Trajectory Sample At Time` 等节点，以获取未来某个时间点的预测位置或速度，用于驱动动画混合、IK 等。

**场景：切换根运动并调整依赖**

1.  在 `PrePhysics` 图中，添加一个 `Mover Toggle Root Motion` 节点，并连接一个 `Branch` 节点。
2.  `Branch` 条件（`bRootMotionEnabled`）为真时：
    -   使用一个 `Add Dependency` 节点，依赖类型选择 `Mover Component Tick Functions`，`DependentMoverTickPhase` 设为 `SimulateMovement`，依赖方式设为 `Before`。
    -   使用一个 `Remove Dependency` 节点，依赖类型同样选择 `Mover Component Tick Functions`，`DependentMoverTickPhase` 设为 `SimulateMovement`，依赖方式设为 `After`。
3.  `Branch` 条件为假时，执行相反操作（移除 `Before` 依赖，添加 `After` 依赖）。
    *（注：此示例为伪代码描述，展示了节点连接逻辑，具体实现需在动画图中完成）*

## C++ 用法

该插件主要面向在 UAF 动画图中进行蓝图/脚本化设计，C++ 侧使用较少，主要用于集成和扩展。

### 头文件引入

```cpp
#include "MoverAnimNextModule.h" // 模块接口
// 通常通过 UAF 的模块系统来使用，而非直接 include 私有头文件。
```

### 基本用法

该插件的核心是 RigVM 节点，这些节点在动画图中被实例化和执行。作为插件使用者，你通常不需要直接实例化这些 C++ 类。

然而，如果你需要编写自定义的 RigVM 节点来与 Mover 交互，你可以参考 `FRigUnit_GenerateMoverTrajectory` 的结构。其关键部分在于：
1.  通过 `TObjectPtr<UMoverComponent>` 获取 Mover 组件。
2.  调用 Mover 组件的相关接口（如历史记录、预测）来生成轨迹数据。
3.  将结果写回 `FTransformTrajectory` 等数据结构。

一个简化的、示意性的数据流如下（基于 `FRigUnit_GenerateMoverTrajectory::Execute` 的推断逻辑）：
```cpp
// 伪代码示例，展示核心逻辑流程
if (MoverComponent && InOutTrajectory)
{
    // 1. 从 MoverComponent 获取历史运动数据
    TArray<FMovementRecord> History = MoverComponent->GetMovementHistory();
    
    // 2. 对历史数据进行采样和插值，填充轨迹的 “历史” 部分
    // ...（使用 HistorySamplingInterval, NumHistorySamples 参数）
    
    // 3. 基于当前状态和预期输入，预测未来运动，填充轨迹的 “预测” 部分
    // ...（使用 PredictionSamplingInterval, NumPredictionSamples 参数）
    
    // 4. 将处理后的数据存入 InOutTrajectory
    // InOutTrajectory->SetSamples(...);
}
```

### 进阶用法

**创建自定义轨迹分析节点：**
你可以继承 `FRigUnit_AnimNextBase` 并参考 `FRigUnit_GetTrajectoryVelocity` 的实现，来创建新的轨迹分析节点。例如，一个计算“到达某点所需时间”的节点。

**扩展模块事件依赖：**
`FRigVMTrait_ModuleEventDependency_MoverComponentTickFunctions` 的设计展示了如何为 UAF 模块系统创建自定义的依赖类型。你可以创建依赖于其他游戏系统（如能力系统）的更新阶段的 Trait。

## 模块依赖

从插件的 `.uplugin` 和功能分析，使用此插件需要以下依赖：

| 模块 | 用途 |
|---|---|
| `Mover` | 核心运动系统，提供 `UMoverComponent` 和运动模拟功能。这是此插件主要对接的目标。 |
| `UAF` | Universal Animation Framework，提供动画图（AnimNext）、模块化事件系统等基础设施。 |
| `RigVM` | 提供可视化脚本（RigVM 图）的运行时，所有动画图节点在此基础上执行。 |
| `AnimationCore` | 动画核心数据结构，可能包含 `FTransformTrajectory` 等轨迹类型。 |

**注意**：`Mover` 和 `UAF` 均为实验性或插件，使用前需在项目中启用它们。常见的 Core、Engine 等模块依赖已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-11-27 | `dbd97e08` | UAF: Add more logging to areas that could be important to users | 为关键用户操作区域添加了更多日志记录，便于调试。 |
| 2025-10-23 | `91139bd4` | Fix for broken trajectories on Mover UAF characters | 修复了 Mover UAF 角色轨迹生成错误的问题。 |
| 2025-10-16 | `5d05a2c4` | AnimSandbox: Fix system compilation error | 修复了动画沙盒示例系统的编译错误。 |
| 2025-10-15 | `3a0a2485` | Fix crash in RigUnit_GenerateMoverTrajectory | 修复了 `GenerateMoverTrajectory` 节点导致的崩溃。 |
| 2025-10-14 | `88e6c8e8` | Allow sampling of mover trajectory at a different (higher frequency) rate than we output to the traj | 允许以比输出轨迹更高的频率对 Mover 轨迹进行采样，提升了预测精度。 |

### 维护评价

该插件创建于 **2024年11月**，属于较新的实验性功能。
- **活跃维护**：从最近提交记录看，直到 **2025年11月** 仍有功能性更新和问题修复（如轨迹修复、崩溃修复、采样频率改进），说明 Epic 团队仍在积极维护和迭代此插件。
- **实验性状态**：标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明其 API 和功能在未来版本中可能发生变化，不建议在需要长期稳定性的生产项目中深度依赖。
- **功能完整**：实现了核心的轨迹生成、分析和依赖管理功能，能够满足 Mover 与 UAF 集成的基本需求。

**建议**：此插件适合进行 **原型开发、技术预研或内部项目**，以便利用最新的动画-运动集成技术。在正式发布项目中使用前，需密切关注其 API 变更并评估稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverAnimNext)
- [官方文档]( ) （暂无）
- [相关插件：Mover](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover)
- [相关插件：UAF](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF)