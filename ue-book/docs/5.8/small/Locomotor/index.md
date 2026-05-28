# Locomotor

> Procedural animation for Control Rig.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化移动器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Locomotor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/Locomotor) | |

## 用途

Locomotor 插件为 Unreal Engine 的 **Control Rig** 框架提供了一个**程序化的脚步动画模拟器**。它的核心目的是解决角色在移动时，脚步位置与方向需要动态适应不同地形和移动状态的问题，从而减少对预烘焙动画或复杂手动调整的依赖。

该插件的核心功能是模拟一个具有多组脚（如两足、四足或更多）的生物体的行走、小跑或奔跑。通过给定目标位置、移动速度和一组脚的设置，模拟器会计算出每只脚的预期落地位置、抬起时机、步高以及脚掌朝向。它可以自动处理以下问题：
*   **脚步碰撞**：防止脚部重叠或交叉。
*   **地形适应**：通过射线检测将脚部贴合到不平整的地面。
*   **骨盆与身体运动**：根据脚步的节奏和地形，平滑地移动和旋转角色的骨盆（髋部）。

简而言之，它是一个“行走逻辑引擎”，与 Control Rig 结合，可以为角色的 IK（反向动力学）骨骼链提供程序化生成的脚部目标变换。

## 使用场景

- 你需要一个能**自动在崎岖地形上行走**的角色，例如在开放世界游戏或模拟游戏中。
- 你正在制作一个**四足或多足生物**，需要一个能处理复杂步态逻辑的系统。
- 你希望快速原型化角色的移动，而不想为每种地形和速度都制作大量动画。
- 你正在使用 Control Rig 构建角色动画，并需要一个**智能的、基于物理的脚部目标生成器**。

## 蓝图用法

Locomotor 的蓝图接口主要是通过 Control Rig 图表中的 **`Locomotor`** 节点（`FRigUnit_Locomotor`）来实现的。该节点是一个可变（Mutable）的高级 Rig 单元。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Locomotor` | 核心模拟节点。输入目标位置、移动设置和脚部配置，输出最终的脚部变换数组。 | `FRigUnit_Locomotor` |

### 使用示例（蓝图描述）

1.  **在你的 Control Rig 蓝图中**，添加一个 `Locomotor` 节点（位于 “Simulation” 类别下）。
2.  **连接输入**：
    *   **`RootControl`**：连接到角色根骨骼或某个控制体的 `FName`，用于确定模拟的“目标”位置（通常由移动组件驱动）。
    *   **`Movement`**：创建或连接一个 `FMovementSettings` 结构体。设置 `SpeedMax`、`Acceleration`、`Deceleration` 等参数来控制移动速度和加速度。
    *   **`FootSets`**：这是关键配置。你需要创建一个 `TArray<FFootSet>` 数组。
        *   对于两足生物：创建一个 `FFootSet`，其 `Feet` 数组包含两个 `FFootSettings`（分别对应左脚和右脚），设置它们的 `AnkleBone`（脚踝骨骼）和 `CollisionRadius`。
        *   对于四足生物：可以创建两个 `FFootSet`。第一个 `PhaseOffset` 设为 0（如左前、右后），第二个 `PhaseOffset` 设为 0.5（如右前、左后），以实现对角步态。
    *   **`Stepping`**：连接或配置 `FStepSettings`，控制步高 (`StepHeight`)、脚在空中的时间比例 (`PercentOfStrideInAir`)、地形检测等。
    *   **`Pelvis`**：连接或配置 `FPelvisSettings`，将 `PelvisBone` 设置为角色的髋部骨骼，用于让骨盆跟随脚步自然摆动。
3.  **连接输出**：
    *   **`FeetTransforms`**：这是一个 `TArray<FTransform>` 数组，其顺序与你输入的 `FootSets` 中脚的定义顺序一致（扁平化后的顺序）。你需要将这些变换连接到对应脚部的 IK 节点（如 TwoBoneIK、FullBodyIK 的脚部目标）。

## C++ 用法

虽然主要通过 Control Rig 节点使用，但也可以直接在 C++ 中使用 `FLomotor` 结构体进行模拟。

### 头文件引入

```cpp
#include "LocomotorCore.h" // 包含 FLocomotor 结构体定义
```

### 基本用法

以下示例展示了如何初始化并运行一次 Locomotor 模拟。
```cpp
// (示例，非完整项目代码)
#include "LocomotorCore.h"
#include "RigUnit_Locomotor.h" // 如果需要访问 Settings 结构体

void SimulateOneFrame()
{
    // 1. 创建 FLocomotor 实例
    FLocomotor Locomotor;

    // 2. 初始化
    FTransform InitialRootGoal = FTransform(FVector(0, 0, 0)); // 初始目标位置
    FTransform InitialPelvis = FTransform(FVector(0, 0, 100)); // 初始骨盆位置
    Locomotor.Reset(InitialRootGoal, InitialPelvis);

    // 3. 添加一组脚（例如，两足）
    FFootSettings LeftFootSettings, RightFootSettings;
    LeftFootSettings.AnkleBone = FRigElementKey(TEXT("foot_l"), ERigElementType::Bone);
    LeftFootSettings.CollisionRadius = 10.f;
    RightFootSettings.AnkleBone = FRigElementKey(TEXT("foot_r"), ERigElementType::Bone);
    RightFootSettings.CollisionRadius = 10.f;

    // 在一个 FootSet 中添加双脚（它们会交替相位）
    int32 FootSetIndex = Locomotor.AddFootSet(0.0f); // 相位偏移为 0
    Locomotor.AddFootToSet(FootSetIndex, FTransform(FVector(0, -20, 0)), LeftFootSettings);
    Locomotor.AddFootToSet(FootSetIndex, FTransform(FVector(0, 20, 0)), RightFootSettings);

    // 4. 准备模拟输入
    FLocomotorInputSettings InputSettings;
    InputSettings.Movement.SpeedMax = 300.f;
    InputSettings.Movement.Acceleration = 200.f;
    InputSettings.Stepping.StepHeight = 8.f;
    // ... 根据需要设置其他参数

    // 5. 运行模拟
    Locomotor.RunSimulation(InputSettings);

    // 6. 获取结果
    TArray<FTransform> FinalFootTransforms;
    Locomotor.GetFeetCurrent(FinalFootTransforms);
    // FinalFootTransforms[0] 是左脚的目标变换
    // FinalFootTransforms[1] 是右脚的目标变换

    // 7. 获取更新后的骨盆变换
    FTransform NewPelvisTransform = Locomotor.GetPelvisCurrent();
}
```
*来源参考: `Source/Locomotor/Public/LocomotorCore.h`*

## Demo 示例

一个最小的控制台测试示例，演示如何创建和运行 Locomotor。

**LocomotorTest.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "LocomotorCore.h"

class FLocomotorTest
{
public:
    void RunTest();
    void SimulateMultipleFrames(int32 NumFrames, float DeltaTime);

private:
    FLocomotor Locomotor;
};
```

**LocomotorTest.cpp**
```cpp
#include "LocomotorTest.h"
#include "RigUnit_Locomotor.h"

void FLocomotorTest::RunTest()
{
    UE_LOG(LogTemp, Warning, TEXT("--- Starting Locomotor Basic Test ---"));

    // 初始化
    Locomotor.Reset(FTransform::Identity, FTransform(FVector(0, 0, 100)));

    // 添加一只脚（用于演示单脚逻辑）
    FFootSettings TestFootSettings;
    TestFootSettings.AnkleBone = FRigElementKey(TEXT("TestFoot"), ERigElementType::Bone);
    TestFootSettings.CollisionRadius = 15.f;

    int32 SetIndex = Locomotor.AddFootSet(0.0f);
    int32 FootIndex = Locomotor.AddFootToSet(SetIndex, FTransform(FVector(50, 0, 0)), TestFootSettings);

    if (FootIndex != -1)
    {
        UE_LOG(LogTemp, Warning, TEXT("Successfully added foot %d to set %d"), FootIndex, SetIndex);
    }

    // 配置并运行一帧模拟
    FLocomotorInputSettings Settings;
    Settings.Movement.SpeedMax = 150.f;
    Settings.Movement.Acceleration = 50.f;
    Settings.Movement.bTeleport = false;

    Locomotor.RunSimulation(Settings);

    // 输出结果
    TArray<FTransform> FootTransforms;
    Locomotor.GetFeetCurrent(FootTransforms);
    if (!FootTransforms.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("Foot Goal Location: %s"), *FootTransforms[0].GetLocation().ToString());
    }

    UE_LOG(LogTemp, Warning, TEXT("Current Pelvis Location: %s"), *Locomotor.GetPelvisCurrent().GetLocation().ToString());
    UE_LOG(LogTemp, Warning, TEXT("--- Test Completed ---"));
}

void FLocomotorTest::SimulateMultipleFrames(int32 NumFrames, float DeltaTime)
{
    // 假设已经通过 Reset 和 AddFoot... 完成了初始化
    for (int32 i = 0; i < NumFrames; ++i)
    {
        // 在实际应用中，RootGoal 会随时间移动
        FTransform NewRootGoal = FTransform(FVector(i * DeltaTime * 100.f, 0, 0));
        // Locomotor 内部会根据新旧 RootGoal 计算移动速度和方向
        // (注意：实际需要在每帧更新前调用 Reset 或类似方法设置新目标，此处简化逻辑)
        Locomotor.Reset(NewRootGoal, Locomotor.GetPelvisCurrent());

        FLocomotorInputSettings FrameSettings;
        FrameSettings.Movement.SpeedMax = 200.f;
        Locomotor.RunSimulation(FrameSettings);

        UE_LOG(LogTemp, Verbose, TEXT("Frame %d: Pelvis Z = %.2f"), i, Locomotor.GetPelvisCurrent().GetLocation().Z);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心依赖。`FRigUnit_Locomotor` 继承自 Control Rig 的 `FRigUnit_HighlevelBaseMutable`。 |
| `Core` | `FLomotor` 模块的基本类型和日志系统依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 时产生的编译器警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到更新的 `UE_LOGF`。 |
| 2026-02-11 | `64824357` | [Control Rig] Fix for volatile feet pointers in Locomotor node. | [Control Rig] 修复 Locomotor 节点中脚部指针不稳定的问题。 |
| 2025-11-07 | `2c4d26aa` | [Locomotor] Fixed uninitialized member variables in FStepSettings | [Locomotor] 修复 `FStepSettings` 中未初始化的成员变量。 |
| 2025-10-14 | `f0ed5774` | Control Rig: Apply strict documentation policy to ... nodes | Control Rig: 对...节点应用严格的文档策略。 |

### 维护评价

Locomotor 是一个**较新的实验性插件**，创建于 2024 年 10 月。从提交记录来看，它在创建后的一段时间内（至 2026 年 5 月）**持续有维护更新**，但主要集中在**错误修复、编译器警告消除和代码规范统一**上，没有看到重大的功能增强。

*   **优点**：代码仍在维护中，没有被标记为废弃。
*   **风险**：作为标记为 `IsBetaVersion` 和 `IsExperimentalVersion` 的插件，其 API 可能不稳定，未来版本可能会发生 breaking changes。功能上相对基础（Spine 和 Head 设置在代码中被注释为 TODO），可能需要用户自行扩展。
*   **建议**：适用于需要基础程序化移动功能的**原型开发或研究项目**。如果计划用于生产环境，需要做好应对 API 变化和自行修复潜在问题的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/Locomotor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/Locomotor/Tests) (如果存在)