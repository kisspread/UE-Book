# UAF Mirroring

> Keyframe mirroring for UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF镜像 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMirroring` (Runtime), `UAFMirroringUncookedOnly` (Runtime), `UAFMirroringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring) | |

## 用途

该插件为 Unreal Animation Framework (UAF) 添加了关键帧镜像功能。它解决的核心问题是：在UAF动画系统中，如何高效地创建动画数据的对称副本。通过提供基础的镜像逻辑和相关的动画图模板（Trait），它允许动画师和开发者快速复制例如左臂动画到右臂的动作，从而极大地提升对称动画（如角色移动、战斗动作）的创建效率和灵活性。

## 使用场景

- 你需要为角色制作一套攻击动画，并快速生成镜像版本用于另一只手或对称的肢体。
- 在制作角色行走、奔跑等循环动画时，需要确保左右肢体的运动完全对称。
- 你正在使用UAF构建动画评估流程，并希望将镜像作为流程中的一个标准步骤。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mirror UAF Pose` | 将一个UAF姿态数据按照指定轴进行镜像，返回新的姿态数据。 | `UMirrorUAFPose` |
| `Create Mirror Trait` | 为一个动画特质（Trait）创建镜像版本，返回一个包含镜像逻辑的新特质。 | `UAnimGraphNode_Mirror` |

### 使用示例（蓝图描述）

在动画蓝图中，可以通过`Create Mirror Trait`节点包裹一个现有的动画特质（如一个播放节点），该节点会输出一个镜像后的特质，连接到后续的动画评估流程中。或者，也可以使用`Mirror UAF Pose`节点直接对输入的姿态数据（Pose）进行处理，实现更细粒度的控制。

## C++ 用法

### 头文件引入

```cpp
#include "UAFMirroringModule.h"
```

### 基本用法

从测试用例 `UAFMirroringTests.cpp` 提取，用于镜像一个姿态数据。

```cpp
// 创建一个镜像操作的参数
FUAFMirroringParams MirrorParams;
MirrorParams.MirrorAxis = EAxis::X; // 沿X轴镜像
MirrorParams.bMirrorRotation = true;

// 对输入的姿态数据进行镜像
FUAFPose MirroredPose = MirrorUAFPose(InputPose, MirrorParams);
```

### 进阶用法

结合镜像特质，在动画图中为现有节点动态添加镜像能力，这通常在构建动画评估规则时使用。

```cpp
// 获取一个已存在的动画图节点（例如一个播放节点）
UAnimGraphNode_Play* PlayNode = GetPlayNode();

// 创建一个镜像特质，包裹该播放节点
UAnimGraphNode_Mirror* MirrorNode = CreateMirrorTrait(PlayNode, MirrorParams);

// 将镜像特质加入到动画评估流程中
AddToEvaluationGraph(MirrorNode);
```

## Demo 示例

**源文件: MyMirrorHelper.h & .cpp**

展示如何在C++中封装一个镜像工具类，用于快速对姿态数据进行对称处理。

```cpp
// MyMirrorHelper.h
#pragma once

#include "CoreMinimal.h"
#include "UAFMirroringModule.h"

class FMyMirrorHelper
{
public:
    // 简化函数，沿X轴镜像一个姿态
    static FUAFPose MirrorPoseAlongX(const FUAFPose& InPose);
};

// MyMirrorHelper.cpp
#include "MyMirrorHelper.h"

FUAFPose FMyMirrorHelper::MirrorPoseAlongX(const FUAFPose& InPose)
{
    FUAFMirroringParams Params;
    Params.MirrorAxis = EAxis::X;
    Params.bMirrorRotation = true;
    return MirrorUAFPose(InPose, Params);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | UAF动画框架的核心模块，提供姿态、特质等基础类型。 |
| `UAFAnimGraph` | UAF的动画图模块，提供动画图节点（Trait）的基础支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏更新为新版格式。 |
| 2026-03-10 | `24473b8e` | Fix direct reads of latent SharedData properties in UAF traits | 修复了UAF特质中延迟共享数据属性的直接读取问题。 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 添加了低级别测试的验证器，确保UAF插件的构建和测试运行。 |
| 2026-01-23 | `81bd488d` | UAF fix some incorrect comparison of invalid bone indicies, where 16bit was upcast to 32bit and comp | 修复了无效骨骼索引比较中16位提升至32位时的错误。 |
| 2026-01-23 | `9735f798` | UAF: Fix rename/move issues | 修复了UAF相关的重命名/移动问题。 |

### 维护评价

该插件处于**活跃维护**状态。创建时间不到一年，且近期（2026年1月至4月）有频繁的更新，涵盖功能迁移、Bug修复和测试基础设施改进。由于它属于实验性插件（IsExperimentalVersion=true），其API和功能可能会发生变化，但持续的提交表明 Epic Games 内部正在积极使用和迭代它。目前没有看到明确的废弃标记，推荐在实验性项目或了解其不稳定性的前提下使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring/Tests)