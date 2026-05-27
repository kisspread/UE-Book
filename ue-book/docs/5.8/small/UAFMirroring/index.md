# UAF Mirroring

> Keyframe mirroring for UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 关键帧镜像 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMirroring` (Runtime), `UAFMirroringUncookedOnly` (Runtime), `UAFMirroringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring) | |

## 用途
该插件为 UAF（Unreal Animation Framework）动画框架提供关键帧镜像功能。其核心目的是在动画图表编辑器中，允许用户快速创建动画序列的镜像版本（例如，将角色向右行走的动画镜像为向左行走），从而高效生成对称的动画内容。

## 使用场景
- 你在使用 UAF 动画图系统，需要为角色制作一组左右对称的动画（如行走、攻击、待机）。
- 你希望基于一个已有的动画 Pose 或关键帧数据，快速生成其镜像版本，而无需手动重新制作。
- 你在动画图中需要实现一个镜像操作节点。

## 蓝图用法
根据模块文档，此插件主要提供 UAF 动画图节点和镜像特征。蓝图层面主要通过以下方式使用：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mirror Pose` | 将输入的 UAF Pose 进行镜像处理。 | `UAnimNode_MirrorPose` |

### 使用示例（蓝图描述）
在 UAF 动画图编辑器中，你可以将一个 `Mirror Pose` 节点连接到动画数据流中。将需要镜像的动画 Pose 连接到该节点的输入引脚，节点的输出引脚即为镜像后的 Pose，可用于后续的动画混合或输出。

## C++ 用法
此插件主要通过动画特征（Trait）和动画图节点（AnimNode）在 C++ 层面使用。

### 头文件引入
```cpp
// 包含镜像特征的定义
#include “UAFMirroring/MirrorTrait.h”

// 包含镜像动画节点的定义
#include “UAFMirroring/AnimNodes/AnimNode_MirrorPose.h”
```

### 基本用法
通常，开发者不需要直接调用复杂的镜像函数，而是在定义动画特征时应用镜像特征。
```cpp
// 在创建一个自定义的 UAF 动画特征（Trait）时，可以使其继承或包含镜像功能。
// 示例：定义一个支持镜像的动画特征
class FMyAnimTrait : public FAnimInstanceTrait
{
    // ... 特征的其他实现
    // 使用 UAF 的镜像帮助函数来处理姿态数据
    FUAFMirroringHelper::MirrorPose(PoseToMirror, MirrorSetupData);
};
```

## Demo 示例
一个概念性的最小用例，展示如何在动画特征中集成镜像逻辑。
```cpp
// MyMirrorTrait.h
#pragma once
#include “CoreMinimal.h”
#include “UAF/AnimInstanceTrait.h”
#include “UAFMirroring/MirrorTrait.h”

class UMyMirrorTrait : public UAnimInstanceTrait
{
    GENERATED_BODY()
public:
    virtual void OnUpdate(const FUAFUpdateContext& Context) override
    {
        // 1. 获取当前的 Pose
        FUAFPose CurrentPose = Context.GetPose();

        // 2. 获取镜像配置数据（可能来自资产或设置）
        const FAnimMirrorSetup& MirrorSetup = GetMirrorSetupData();

        // 3. 使用插件提供的帮助函数进行镜像
        FUAFPose MirroredPose;
        FUAFMirroringHelper::MirrorPose(CurrentPose, MirrorSetup, MirroredPose);

        // 4. 将镜像后的 Pose 设置回上下文或用于后续处理
        Context.SetPose(MirroredPose);
    }
};
```

## 模块依赖
要使用此插件，你的项目或模块需要依赖以下特定模块（除通用 Core/Engine 外）：

| 模块 | 用途 |
|---|---|
| `UAF` | 提供核心的 Unreal Animation Framework 运行时和编辑器功能。 |
| `UAFAnimGraph` | 提供 UAF 动画图系统的相关功能，是镜像节点运行的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-10 | `24473b8e` | Fix direct reads of latent SharedData properties in UAF traits | 修复 UAF 特征中延迟读取 SharedData 属性的直接访问问题。 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 为 UAF 插件的构建和低层级测试添加了验证器。 |
| 2026-01-23 | `81bd488d` | UAF fix some incorrect comparison of invalid bone indicies, where 16bit was upcast to 32bit and comp | 修复一些无效骨骼索引的错误比较问题（16位上转32位导致）。 |
| 2026-01-23 | `9735f798` | UAF: Fix rename/move issues | 修复重命名和移动相关的问题。 |

### 维护评价
该插件创建于 2025 年 8 月，至今约一年，目前处于**活跃维护**状态。从提交记录看，近几个月的更新主要集中在底层兼容性修复（如日志宏迁移）和核心 UAF 框架的 bug 修复上，说明其依赖的 UAF 核心仍在不断优化。作为实验性（IsExperimentalVersion=true）插件，其 API 可能尚未稳定。对于正在使用或计划使用 UAF 动画系统的项目，它是实现镜像动画的有效工具，但需注意其“实验性”标签，并关注未来可能的 API 变更。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring)
- [官方文档]() (暂无)