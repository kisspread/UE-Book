# Relative IK Op

> Experimental Retarget Op for Relative IK goal setting

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | 否（`IsExperimentalVersion: true`） |
| 包含内容 | 是（`CanContainContent: true`） |
| 模块 | RelativeIKOp (Runtime), RelativeBodyAnimInfo (Runtime), BodyIntersectIKOp (Runtime), RelativeBodyAnimUtils (Editor) |
| 创建时间 | 2025-07-23 |
| 年龄标签 | 🆕 |
| 依赖插件 | IKRig |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/RelativeIKOp) | |

## 用途

RelativeIKOp 是一个基于物理体（Physics Body）空间关系的 IK 重定向操作（Retarget Op）。它解决的核心问题是：**在不同骨架之间重定向动画时，如何根据源骨骼的物理体之间的空间相对关系，自动计算目标骨骼的 IK Goal 位置**。

传统 IK 重定向只关注骨骼变换的映射，而 RelativeIKOp 进一步利用 PhysicsAsset 中定义的碰撞体形状，烘焙源动画中身体部位之间的接触点相对位置关系，并在运行时将这些关系投射到目标骨架上，从而生成更准确的 IK 目标位置。这使得动画重定向能够保持"手放在桌上""脚踩地面"这类基于身体部位空间关系的语义信息。

插件包含 4 个模块：
- **RelativeIKOp** — 核心 Retarget Op，计算相对 IK 目标
- **RelativeBodyAnimInfo** — 数据定义层，包含烘焙数据的 AnimNotify 类型
- **BodyIntersectIKOp** — 附加的 Retarget Op，用于物理体与 IK 目标的交叉检测
- **RelativeBodyAnimUtils**（Editor）— 离线烘焙工具，将身体相对关系写入动画序列

## 使用场景

- 你需要将一个角色的动画重定向到体型差异较大的另一个角色，同时保持手脚等部位的相对空间关系（如手掌放置位置）
- 你需要基于物理体碰撞关系来约束 IK 目标位置，避免手/脚穿模
- 你已经在使用 IKRig 进行动画重定向，需要一个额外的 Op 来根据身体部位接触关系动态调整 IK Goal
- 你需要 Body Intersect 检测：当 IK effector 进入目标角色的物理体内部时，自动修正位置以避免穿插

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSettings` | 获取当前 Relative IK Op 的设置 | `UIKRetargetRelativeIKController` |
| `SetSettings` | 设置 Relative IK Op 的参数 | `UIKRetargetRelativeIKController` |
| `GetSettings` | 获取 Body Intersect Op 的设置 | `UIKRetargetBodyIntersectController` |
| `SetSettings` | 设置 Body Intersect Op 的参数 | `UIKRetargetBodyIntersectController` |

### Settings 结构体：FIKRetargetRelativeIKOpSettings

该结构体通过 IKRetargeter 编辑器中的 Op 面板配置，关键参数如下：

**Physics（物理体）**
- `SourcePhysicsAssetOverride` — 源网格的物理资产，用于身体对测试
- `TargetPhysicsAssetOverride` — 目标网格的物理资产，用于重定向
- `BodyMapping` — 源到目标的物理体名称映射（TMap）

**Parameters（参数）**
- `DistanceThreshold`（默认 50）— 身体对之间信息烘焙的最大距离
- `DistanceFade`（默认 200）— 距离权重衰减范围
- `FeasibilityLengthBias`（默认 0）— 可行性距离偏置
- `ContributionSumWeight`（默认 1.0）— IK Goal 归一化权重
- `TemporalSmoothingRadius`（默认 15）— 时间平滑帧数（0 = 不平滑，最大 60）
- `bIgnoreSourceScale`（默认 true）— 计算相对距离时忽略源缩放
- `RetargetContactAlpha`（默认 0.5）— 接触体到次要体的混合比例
- `RetargetSpringAlpha`（默认 0.5）— 主/次对距离关系的混合比例

**Debug（调试）**
- `bDebugDrawBodyPairs` — 绘制源/目标身体对关系
- `bDebugDrawGoalContributions` — 绘制每个对的目标贡献
- `bDebugDrawPhysicsBodies` — 绘制物理体
- `bDryRun` — 执行但不更新 IK Goals（仅调试）

### 使用示例（蓝图描述）

1. 打开 **IKRetargeter** 资产
2. 在 Op Stack 中添加 **Run IK Rig** Op（作为父 Op，提供 IK Rig 定义）
3. 在其下添加 **Relative IK Goals** Op
4. 设置 `SourcePhysicsAssetOverride` 和 `TargetPhysicsAssetOverride`
5. 如果源/目标物理体名称不同，在 `BodyMapping` 中配置映射关系
6. 调整 `DistanceThreshold` 和 `TemporalSmoothingRadius` 控制行为

## C++ 用法

### 头文件引入

```cpp
#include "Retargeter/IKRetargetOps.h"
#include "Retargeter/IKRetargetSettings.h"
```

### 基本用法

RelativeIKOp 作为 IKRetarget Op Stack 的一部分使用，不能独立运行。它需要一个父 Op（`FIKRetargetRunIKRigOp`）提供 IK Rig 定义。

关键的工作流程：

```cpp
// 1. 获取 Retargeter 资产中的 Op（通过 Controller）
UIKRetargetRelativeIKController* Controller = ...; // 从 Retargeter 获取

// 2. 获取/设置参数
FIKRetargetRelativeIKOpSettings Settings = Controller->GetSettings();
Settings.SourcePhysicsAssetOverride = SourcePhysAsset;
Settings.TargetPhysicsAssetOverride = TargetPhysAsset;
Settings.DistanceThreshold = 50.0;
Settings.TemporalSmoothingRadius = 15;
Controller->SetSettings(Settings);
```

### 核心运行流程（源码分析）

Op 的 `Run` 方法执行逻辑（来自 `RelativeIKOp.cpp`）：

1. **获取烘焙数据**：从 `URelativeBodyBakeAnimNotify` 中读取身体对的烘焙顶点位置
2. **时间平滑**：通过 `ApplyTemporalSmoothing` 对烘焙点应用时间域平滑
3. **逐对计算**：对每个身体对（BodyPair）：
   - 将烘焙的局部顶点位置变换到源骨架的世界空间
   - 计算源空间中两个顶点之间的距离，得出权重
   - 将顶点位置通过物理体的 oriented scale 变换到目标骨架
   - 使用 `RetargetSpringAlpha` 和 `RetargetContactAlpha` 混合直接接触与相对关系
   - 计算可行性范围（Feasibility Range）避免目标骨架链长不足
4. **加权平均**：对影响同一个 IK Goal 的所有身体对贡献进行加权平均
5. **更新 Goal**：将计算出的位置写入 `FIKRigGoal`（Component Space）

### BodyIntersectIKOp

这是一个独立的 Retarget Op，用于检测 IK effector 是否穿透了目标物理体：

```cpp
// Settings 配置
FIKRetargetBodyIntersectIKOpSettings IntersectSettings;
IntersectSettings.TargetPhysicsAssetOverride = TargetPhysAsset;
IntersectSettings.IntersectGoals = { FName("LeftHandGoal"), FName("RightHandGoal") };
IntersectSettings.IntersectBodies = { FName("spine_01"), FName("spine_02") };
```

### 离线烘焙（Animation Modifier）

使用 `URelativeBodyAnimModifier`（Editor 模块）将身体关系烘焙到动画序列中：

```cpp
// 在编辑器中通过 Animation Modifier 面板使用
// 配置项：
// - SkeletalMeshAsset: 源骨骼网格
// - PhysicsAssetOverride: 物理资产覆盖
// - DomainBodyNames: 域体名称列表
// - ContactBodyNames: 接触体名称列表
// - SampleRate: 采样率（默认 30 Hz）
// - ContactThreshold: 接触阈值（默认 150）
// - NotifyClass: 输出的 Notify 类型
```

## Demo 示例

```cpp
// MyRelativeIKModule.Build.cs
using UnrealBuildTool;

public class MyRelativeIKModule : ModuleRules
{
    public MyRelativeIKModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "IKRig",
            "RelativeIKOp",
            "RelativeBodyAnimInfo"
        });
    }
}
```

```cpp
// MyRetargetHelper.h
#pragma once

#include "CoreMinimal.h"
#include "Retargeter/IKRetargetOps.h"
#include "RelativeIKOp.h"

class FMyRetargetHelper
{
public:
    // 配置 RelativeIKOp 参数的辅助函数
    static void ConfigureRelativeIKOp(
        UIKRetargetRelativeIKController* Controller,
        UPhysicsAsset* SourcePhysAsset,
        UPhysicsAsset* TargetPhysAsset,
        float DistanceThreshold = 50.0f)
    {
        if (!Controller) return;

        FIKRetargetRelativeIKOpSettings Settings = Controller->GetSettings();
        Settings.SourcePhysicsAssetOverride = SourcePhysAsset;
        Settings.TargetPhysicsAssetOverride = TargetPhysAsset;
        Settings.DistanceThreshold = DistanceThreshold;
        Settings.TemporalSmoothingRadius = 15;
        Settings.bIgnoreSourceScale = true;
        Controller->SetSettings(Settings);
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 反射系统 |
| `Engine` | 引擎核心（SkeletalMeshComponent, PhysicsAsset 等） |
| `AnimationCore` | 动画核心类型 |
| `MeshDescription` | 网格描述（顶点/面数据访问） |
| `StaticMeshDescription` | 静态网格描述扩展 |
| `SkeletalMeshDescription` | 骨骼网格描述扩展 |
| `Renderer` | 渲染器（DebugDraw 使用） |
| `IKRig` | IK 骨架定义和求解（核心依赖） |
| `RelativeBodyAnimInfo` | 本插件内部模块，AnimNotify 数据定义 |
| `AnimationModifiers` | 动画修改器框架（仅 RelativeBodyAnimUtils） |
| `AnimationBlueprintLibrary` | 动画蓝图工具库（仅 RelativeBodyAnimUtils） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-26 | `ce2f996e` | Fix possible crash, use per-relik op memory for runtime smoothing | 修复运行时平滑的内存崩溃问题，改用每个 Op 独立的内存 |
| 2025-09-24 | `c10417d2` | Fix crash when switching from montage -> anim with baked data | 修复从 Montage 切换到 AnimSequence 时的崩溃 |
| 2025-09-02 | `6ee457ff` | Allow no-copy codepath when smoothing=0, move smoothing to standard params | 性能优化：平滑为0时跳过拷贝，平滑参数移至标准分类 |

### 维护评价

- **创建时间**: 2025-07-23，至今约 10 个月，属于 🆕 新模块
- **维护状态**: 活跃维护 — 最近 3 个月有连续的功能修复和优化（2025-09）
- **实验性标记**: `IsExperimentalVersion: true`，`Installed: false`，需要手动启用
- **已知限制**:
  - 依赖烘焙的 AnimNotify 数据，必须先用 `URelativeBodyAnimModifier` 离线烘焙
  - 源码中多处 TODO 标记表明部分功能仍在开发中（如旋转不变烘焙、双向距离加权等）
  - 没有官方文档（`DocsURL` 为空）
- **推荐**: 适合对 IK 重定向有高级需求的开发者，但需注意实验性状态，生产环境使用需谨慎

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/RelativeIKOp)
- [IKRig 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/IKRig)（核心依赖）
