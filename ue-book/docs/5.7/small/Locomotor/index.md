# Locomotor

> Procedural animation for Control Rig.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | false (IsBetaVersion=true, IsExperimentalVersion=true) |
| 包含内容 | false |
| 模块 | Locomotor (Runtime, LoadingPhase=PreDefault) |
| 创建时间 | 2024-10-09 |
| 年龄标签 | 🆕 (≈1.5 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/Locomotor) | |

## 用途

Locomotor 是一个基于 Control Rig 的**程序化步态动画系统**。它解决的核心问题是：在不依赖传统动画状态机和骨骼动画资产的情况下，根据目标位置自动生成角色的脚步移动动画。

这个 plugin 的核心思想是**基于相位的步态模拟**（phase-based gait simulation）：

1. 给定一个目标位置（Root Control），系统根据距离自动计算加速度/减速度
2. 用一个全局相位（Global Phase）驱动所有脚的交替运动
3. 每只脚在"摆动"（swing）和"支撑"（planted）两个状态间切换
4. 脚步落地位置通过弹簧阻尼器（spring damper）平滑过渡
5. 骨盆（pelvis）根据脚的位置自动调整高度（bob）、倾斜（lean）、引导（lead）

它使用 Daniel Holden 的 "Exact Damper" 算法进行平滑插值，参考自 [theorangeduck.com/page/spring-roll-call](https://theorangeduck.com/page/spring-roll-call)。

**为什么存在？** 适用于程序化生成的生物、动态大小的生物、或者需要根据运行时数据驱动脚步的场景，例如巨大 Boss 的脚步落点需要精确匹配地形的场景。

## 使用场景

- 你正在做一个有大量不同体型生物的游戏（恐龙、怪兽等），不想为每种体型制作完整动画 → 用 Locomotor
- 你需要程序化生成的四足/双足行走动画，脚必须精确踩在地面上 → 用 Locomotor
- 你有一个 Control Rig 工作流，想在运行时动态驱动脚步位置 → 用 Locomotor
- 你需要精确控制步态的相位、步高、骨盆弹跳等细节 → 用 Locomotor

## 蓝图用法

Locomotor 作为 Control Rig RigUnit 暴露，不是传统蓝图节点。它在 Control Rig 蓝图编辑器中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Locomotor` | 程序化步态模拟主节点（RigUnit） | `FRigUnit_Locomotor` |

### 节点输入参数

在 Control Rig 图表中添加 `Locomotor` 节点后，可配置以下参数分组：

**Root Control** — 目标位置控制
- `RootControl` (FName): 控制骨骼名称，角色会朝此控制目标移动

**Movement** — 移动设置 (`FMovementSettings`)
- `MinimumStepLength`: 最小步长 (cm)，默认 10
- `SpeedMax` / `SpeedMin`: 最大/最小移动速度 (cm/s)，默认 80/50
- `PhaseSpeedMax` / `PhaseSpeedMin`: 最大/最小相位速度 (cycles/s)，默认 4/1
- `Acceleration` / `Deceleration`: 加/减速度 (cm/s²)，默认 100/30
- `GlobalTimeScale`: 全局时间缩放，默认 1
- `bTeleport`: 传送模式（立即移动到目标），默认 false
- `Styles`: 移动风格数组 (Walk/Trot/Gallop)

**Stepping** — 步伐设置 (`FStepSettings`)
- `PercentOfStrideInAir`: 脚在空中的时间比例，默认 0.35
- `AirExtensionAtMaxSpeed`: 最速时的额外空中时间，默认 0.2
- `StepHeight`: 最大步高 (cm)，默认 6
- `StepEaseIn` / `StepEaseOut`: 起步/落步缓动，0=瞬时，1=缓入缓出
- `bEnableFootCollision`: 脚部碰撞检测（防止交叉），默认 true
- `FootCollisionGlobalScale`: 脚部碰撞全局缩放，默认 1
- `bEnableGroundCollision`: 地面碰撞检测（球形射线），默认 true
- `MaxCollisionHeight`: 最大碰撞高度 (cm)，默认 30
- `TraceChannel`: 射线通道
- `OrientFootToGroundPitch` / `OrientFootToGroundRoll`: 脚部跟随地面倾斜，默认 0.8/0.5

**Pelvis** — 骨盆设置 (`FPelvisSettings`)
- `PelvisBone`: 骨盆骨骼 (FRigElementKey)
- `PositionDampingHalfLife`: 位置阻尼半衰期 (s)，默认 0.1
- `RotationStiffness` / `RotationDamping`: 旋转弹簧刚度/阻尼，默认 40/0.9
- `LeadAmount`: 骨盆超前量，默认 2
- `LeadDampingHalfLife`: 超前阻尼半衰期，默认 0.1
- `BobOffset`: 骨盆上下弹跳偏移 (cm)，默认 -8
- `BobStiffness` / `BobDamping`: 弹跳刚度/阻尼，默认 40/0.9
- `OrientToGroundPitch` / `OrientToGroundRoll`: 骨盆跟随地面倾斜，默认 -0.3/-0.3

**FootSets** — 脚组 (`TArray<FFootSet>`) (Constant)
- 每个 `FFootSet` 包含:
  - `Feet`: 脚列表 (`TArray<FFootSettings>`)
  - `PhaseOffset`: 该组的相位偏移 (0-1)
- 每个 `FFootSettings` 包含:
  - `AnkleBone`: 踝部骨骼 (FRigElementKey)
  - `CollisionRadius`: 碰撞半径 (cm)，默认 10
  - `MaxHeelPeel`: 抬脚时脚跟剥离最大旋转，默认 (0, 0, 50)
  - `StaticLocalOffset`: 静态局部空间偏移

**输出**
- `FeetTransforms` (`TArray<FTransform>`): 脚部最终世界变换数组

### 使用示例（Control Rig 描述）

在 Control Rig 图表中：
1. 添加 `Locomotor` 节点
2. 将 `RootControl` 连接到你的目标控制骨骼名称
3. 设置 `FootSets`：为双足角色添加一个 FootSet，包含 2 个 FFootSettings（左脚踝 + 右脚踝）
4. 设置 `Pelvis`：指定骨盆骨骼名称
5. `FeetTransforms` 输出可用于 Two Bone IK 节点驱动腿部
6. 骨盆变换会由节点自动写入骨骼层级

## C++ 用法

### 头文件引入

```cpp
#include "LocomotorCore.h"
```

### 基本用法（纯 C++ 模拟）

来源: `LocomotorCore.h` + `LocomotorCore.cpp`

```cpp
#include "LocomotorCore.h"

// 创建 Locomotor 实例
FLocomotor Locomotor;

// 初始化：传入初始目标位置和骨盆位置
FTransform InitialRootGoal = FTransform(FVector(0, 0, 0));
FTransform InitialPelvis = FTransform(FVector(0, 0, 100));
Locomotor.Reset(InitialRootGoal, InitialPelvis);

// 添加一组脚（双足：左右脚各 0.0/0.5 相位偏移）
int32 FootSetIndex = Locomotor.AddFootSet(0.0f);

FLocomotorFootSettings LeftFootSettings;
LeftFootSettings.CollisionRadius = 10.f;
Locomotor.AddFootToSet(FootSetIndex, FTransform(FVector(-20, 0, 0)), LeftFootSettings);

FLocomotorFootSettings RightFootSettings;
RightFootSettings.CollisionRadius = 10.f;
Locomotor.AddFootToSet(FootSetIndex, FTransform(FVector(20, 0, 0)), RightFootSettings);

// 每帧运行模拟
FLocomotorInputSettings Settings;
Settings.DeltaTime = GetWorld()->GetDeltaSeconds();
Settings.CurrentWorldRootGoal = FTransform(TargetLocation);
Settings.Movement.SpeedMax = 200.f;
Settings.Movement.Acceleration = 150.f;
Settings.Stepping.StepHeight = 10.f;
Settings.Stepping.bEnableGroundCollision = true;
Settings.Stepping.World = GetWorld();
Settings.Stepping.IgnoredActor = GetOwner();
Settings.Stepping.TraceChannel = ETraceTypeQuery::TraceTypeQuery1;

Locomotor.RunSimulation(Settings);

// 读取结果
const TArray<FLocomotorFoot*>& Feet = Locomotor.GetFeet();
for (int32 i = 0; i < Feet.Num(); ++i)
{
    FTransform FootTransform = Feet[i]->CurrentWorld;
    // 用此变换驱动 IK ...
}

FTransform PelvisTransform = Locomotor.GetPelvisCurrent();
FTransform BodyTransform = Locomotor.GetBodyCurrent();
```

### 进阶用法（四足生物）

```cpp
FLocomotor Locomotor;
Locomotor.Reset(InitialRootGoal, InitialPelvis);

// 前脚组：相位偏移 0（先迈前脚）
int32 FrontFootSet = Locomotor.AddFootSet(0.0f);
Locomotor.AddFootToSet(FrontFootSet, FrontLeftFoot, FrontSettings);
Locomotor.AddFootToSet(FrontFootSet, FrontRightFoot, FrontSettings);

// 后脚组：相位偏移 0.5（与前脚交替）
int32 RearFootSet = Locomotor.AddFootSet(0.5f);
Locomotor.AddFootToSet(RearFootSet, RearLeftFoot, RearSettings);
Locomotor.AddFootToSet(RearFootSet, RearRightFoot, RearSettings);
```

### 辅助结构体

```cpp
// 精确阻尼器（Daniel Holden 算法）
FVectorDamper Damper;
Damper.Reset(FVector::ZeroVector);
FVector SmoothedValue = Damper.Update(TargetValue, DeltaTime, HalfLife);

// 弹簧
FFloatSpring FloatSpring;
float SmoothFloat = FloatSpring.Update(DeltaTime, TargetFloat, Stiffness, Damping);

FVectorSpring VecSpring;
FVector SmoothVec = VecSpring.Update(DeltaTime, TargetVec, Stiffness, Damping);

FQuatSpring QuatSpring;
FQuat SmoothQuat = QuatSpring.Update(DeltaTime, TargetQuat, Stiffness, Damping);
```

## Demo 示例

最小 Control Rig 设置（双足行走）：

```cpp
// Build.cs 依赖
PublicDependencyModuleNames.AddRange(new string[] { "Core", "RigVM", "ControlRig" });
```

在 Control Rig 中：
1. 创建 Control Rig 资产
2. 在 Forward Solve 中添加 `Locomotor` 节点
3. 配置：
   - `RootControl` = "RootControl"（你的控制骨骼名）
   - `FootSets[0].Feet[0].AnkleBone` = "foot_l"
   - `FootSets[0].Feet[1].AnkleBone` = "foot_r"
   - `Pelvis.PelvisBone` = "pelvis"
4. 将 `FeetTransforms` 连接到 Two Bone IK 节点的 Goal 输入
5. 运行时移动 Root Control，角色会自动产生行走步态

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础模块 |
| `RigVM` | Control Rig 虚拟机 |
| `ControlRig` | Control Rig 框架（运行时依赖） |
| `CoreUObject` | UObject 系统（私有） |
| `Engine` | 引擎核心（私有） |
| `Slate` / `SlateCore` | UI 框架（私有） |

使用此 plugin 的模块需要依赖: `Core`, `RigVM`, `ControlRig`

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `72b908c2` | Fixed possible non-normalized rotation in foot simulation | Bug 修复：脚部模拟中旋转未归一化的问题，数值稳定性改进 |
| 2025-09-11 | `198424aa` | Support for teleportation | 新功能：传送模式支持（`bTeleport`），可跳过动画直接移动到目标 |
| 2024-10-09 | `b5a253db` | Adding new experimental procedural locomotion plugin | 初始提交，创建 plugin |

### 维护评价

- **创建时间**: 2024-10-09，约 1.5 年历史
- **维护状态**: **活跃维护** — 最近更新距今约 6 个月，且为实质性功能更新
- **实验性标记**: IsBetaVersion=true, IsExperimentalVersion=true, EnabledByDefault=false — 需手动启用
- **已知限制**:
  - Spine 和 Head 功能在头文件中已定义结构体，但 RigUnit 中被注释为 `TODO`，尚未接入
  - `GetPhaseOffsetForSetFromMovementStyle()` 函数体为 `//TODO`，MovementStyle 功能未完全实现
  - 没有自动化测试用例
- **推荐度**: 适合早期实验和原型开发，但 API 可能变动。如果你需要程序化步态且能接受实验性 API，推荐尝试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/Locomotor)
- [官方文档]()（无）
- [测试用例]()（无）
