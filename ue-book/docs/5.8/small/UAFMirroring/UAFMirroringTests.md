# UAF Mirroring

> Keyframe mirroring for UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF镜像 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMirroring` (Runtime), `UAFMirroringUncookedOnly` (Runtime), `UAFMirroringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring) | |

## 用途

本插件为 UE5 的动画框架 (UAF) 添加了镜像支持。其核心功能是在 UAF 的动画系统中，通过配置骨骼映射和镜像设置，对动画姿态（Pose）进行镜像计算。这解决了动画资产复用和对称性问题，例如，一个角色左手拿剑的动画可以通过镜像快速生成右手版本，无需制作新的动画资产。

## 使用场景

- **双角色格斗游戏**：为左撇子或右撇子角色镜像复用相同的攻击、受击动画。
- **VR 应用**：镜像左/右手的交互动画，以提供一致的交互反馈。
- **动画编辑器**：在编辑器内快速为动画序列生成镜像版本，提升动画资产制作效率。

## 蓝图用法

本插件的蓝图功能主要集中在动画实例和动画镜像设置上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mirror Pose` | 根据配置对传入的动画姿态进行镜像计算，并返回结果。 | `UMirrorAnimInstance` |
| `Get Mirror Settings` | 获取当前动画实例中用于镜像计算的设置。 | `UMirrorAnimInstance` |
| `Set Mirror Settings` | 设置当前动画实例中用于镜像计算的设置。 | `UMirrorAnimInstance` |

### 使用示例（蓝图描述）

1.  创建一个继承自 `UMirrorAnimInstance` 的动画蓝图。
2.  在动画图表中，获取 `Mirror Settings` 属性并连接到一个 `Mirror Pose` 节点。
3.  将需要镜像的源姿态（例如，来自动画序列的输出）输入到 `Mirror Pose` 节点。
4.  `Mirror Pose` 节点的输出即为镜像后的姿态，可用于驱动骨骼网格体。

## C++ 用法

### 头文件引入

```cpp
#include “UAFMirroring/Public/MirrorAnimInstance.h”
```

### 基本用法

以下示例展示了如何在 C++ 中使用镜像功能计算姿态。

```cpp
// 假设已有一个有效的 FMirrorSettings 和 UMirrorAnimInstance* MirrorAnimInst
// FMirrorSettings MirrorSettings;
// UMirrorAnimInstance* MirrorAnimInst;

// 配置镜像设置 (通常从资产加载或蓝图配置)
// MirrorSettings.BoneMapping = ...

// 计算镜像姿态
FAnimPose MirrorPose = MirrorAnimInst->MirrorPose(SourcePose, MirrorSettings);
```

### 进阶用法

结合测试用例，展示如何在动画节点或特性（Trait）中集成镜像功能。

```cpp
// 在自定义的 UAF 特性（Trait）中使用镜像
// 假设你正在编写一个处理动画姿态的特性
void UMyAnimTrait::ProcessPose(const FAnimPose& InputPose)
{
    // 获取或创建镜像设置
    FMirrorSettings CurrentMirrorSettings = GetMirrorSettings();

    // 使用动画实例的镜像功能
    if (UMirrorAnimInstance* MirrorAnimInst = Cast<UMirrorAnimInstance>(GetAnimInstance()))
    {
        FAnimPose MirroredPose = MirrorAnimInst->MirrorPose(InputPose, CurrentMirrorSettings);
        // ... 使用镜像后的姿态
    }
}
```

## Demo 示例

一个展示如何在自定义动画实例中使用镜像功能的最小化示例。

### MyMirrorAnimInstance.h

```cpp
#pragma once

#include “UAFMirroring/Public/MirrorAnimInstance.h”
#include “MyMirrorAnimInstance.generated.h”

UCLASS()
class UMyMirrorAnimInstance : public UMirrorAnimInstance
{
    GENERATED_BODY()

public:
    // 蓝图可调用的函数，用于测试镜像
    UFUNCTION(BlueprintCallable, Category = “Mirror”)
    FAnimPose TestMirrorPose(const FAnimPose& InPose);
};
```

### MyMirrorAnimInstance.cpp

```cpp
#include “MyMirrorAnimInstance.h”

FAnimPose UMyMirrorAnimInstance::TestMirrorPose(const FAnimPose& InPose)
{
    // 使用基类的 MirrorSettings 属性
    return MirrorPose(InPose, MirrorSettings);
}
```

## 模块依赖

本插件依赖于 UAF 动画生态系统的核心模块，这是其功能实现的基础。

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 动画框架的核心运行时模块，提供基础的动画实例、姿态、特性等类型和系统。 |
| `UAFAnimGraph` | UAF 动画图表支持模块，为在动画蓝图和编辑器中使用 UAF 节点提供支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧版 UE_LOG 迁移至新版 UE_LOGF。 |
| 2026-03-10 | `24473b8e` | Fix direct reads of latent SharedData properties in UAF traits | 修复 UAF 特性中直接读取延迟共享数据属性的问题。 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 为 UAF 插件添加构建和运行低级测试的验证器。 |
| 2026-01-23 | `81bd488d` | UAF fix some incorrect comparison of invalid bone indicies, where 16bit was upcast to 32bit and comp | 修复 UAF 中无效骨骼索引比较错误的问题（16位提升至32位比较时）。 |
| 2026-01-23 | `9735f798` | UAF: Fix rename/move issues | 修复 UAF 中的重命名和移动问题。 |

### 维护评价

**UAF Mirroring** 是一个年轻的实验性插件，创建于 2025 年 8 月。从最近的 git 历史来看，该插件在过去一年内获得了持续的维护和改进，包括功能修复、日志系统升级和测试基础设施的增强。最近的提交（2026年4月）表明其仍在活跃开发中。

由于它是 **实验性 (`IsExperimentalVersion=true`)** 且 **默认未启用**，建议仅在开发和测试环境中使用，或在明确了解其可能存在的限制和变动风险后，在生产项目中谨慎使用。它为 UAF 生态系统提供了有价值的镜像功能，是构建复杂动画系统的有力工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring/Tests)