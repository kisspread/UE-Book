# UAF Mirroring

> Keyframe mirroring for UAF（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | UAF镜像插件 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMirroring` (Runtime), `UAFMirroringUncookedOnly` (Runtime), `UAFMirroringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring) | |

## 用途

该插件为 **UAF (Unreal Animation Framework)** 动画系统提供了**关键帧镜像**功能。它解决的核心问题是：如何高效、准确地将一个动画姿态（Pose）进行镜像，以生成角色左侧或右侧的对称动画，而无需为每一侧都单独制作动画。

具体来说，插件实现了一个名为“Mirroring Task”的评估任务，能够从UAF的虚拟机（VM）关键帧栈中取出一个姿态，根据配置的**镜像数据表 (Mirror Data Table)** 和**镜像轴**进行变换，然后将镜像后的姿态推回栈中。这为在运行时或编辑器中动态生成镜像动画提供了底层支持。

## 使用场景

- **角色动画制作**：为左右对称的角色（如人类）制作行走、奔跑、攻击等动画时，只需制作一侧，另一侧通过该插件镜像生成，节省50%以上的动画资产制作时间。
- **非对称动画混合**：在镜像动画的基础上，可以混合原始动画，用于实现角色受伤后跛行等非对称表现。
- **动画资源优化**：在游戏包体优化中，可以只存储单侧动画，在运行时通过插件进行镜像，减少内存和磁盘占用。

## 蓝图用法

该插件的核心逻辑通过C++ Trait和任务实现，没有直接暴露`BlueprintCallable`函数供蓝图调用。其主要接口是在UAF动画图（AnimGraph）中作为节点（Trait）使用。蓝图或编辑器用户可以通过配置以下数据结构来使用镜像功能：

### 核心参数结构体

| 结构体 | 说明 | 所在类/文件 |
|---|---|---|
| `FUAFMirroringTraitSetupParams` | **镜像设置参数**。包含是否启用镜像以及指定镜像数据表 (`UMirrorDataTable`)。 | `MirroringTask.h` |
| `UFAFMirroringTraitApplyToParams` | **应用通道参数**。控制镜像操作会影响哪些动画通道：骨骼变换、动画曲线、自定义属性。 | `MirroringTask.h` |

### 在UAF动画图中使用

1.  在UAF动画图编辑器中，添加一个“Mirroring”节点（对应 `FMirroringTrait`）。
2.  将该节点连接到需要镜像的输入动画姿态上。
3.  在节点的细节面板中，配置上述两个参数结构体：
    -   设置 `Setup.Mirror` 为 `true`。
    -   指定一个预定义的 `MirrorDataTable`。
    -   根据需要勾选 `ApplyTo` 下的 `Bones`, `Curves`, `Attributes` 选项。

## C++ 用法

### 头文件引入

```cpp
#include "MirroringTask.h"
#include "MirroringTrait.h"
// 用于底层镜像操作
#include "Mirroring.h"
```

### 基本用法：使用底层镜像函数

这些函数位于 `UE::UAF` 命名空间下，提供了对姿态镜像的底层控制。

**来源文件: `Private/Mirroring.h`**

```cpp
// 1. 构建骨骼索引镜像映射表
TArray<FBoneIndexType> MeshBoneMirrorMap;
MeshBoneMirrorMap.SetNumZeroed(GetNumOfBonesForMirrorData(MyReferencePose));
UE::UAF::BuildMeshBoneIndexMirrorMap(MyReferencePose, *MyMirrorDataTable, MeshBoneMirrorMap);

// 2. (可选) 构建绑定姿态数据，用于更精确的镜像计算
TArray<FQuat> RefPoseRotations, RefPoseRotationCorrections;
RefPoseRotations.SetNumZeroed(MeshBoneMirrorMap.Num());
RefPoseRotationCorrections.SetNumZeroed(MeshBoneMirrorMap.Num());
UE::UAF::BuildReferencePoseMirrorData(
    MyReferencePose,
    EAxis::X, // 镜像轴
    MeshBoneMirrorMap,
    RefPoseRotations,
    RefPoseRotationCorrections
);

// 3. 镜像一个姿态
FLODPose PoseToMirror = /* ... 从某个来源获取的LOD姿态 ... */;
// 方式A：使用数据表（内部会构建映射）
UE::UAF::MirrorPose(PoseToMirror, *MyMirrorDataTable);
// 方式B：使用预计算的映射和绑定姿态数据（性能更优，适合缓存场景）
UE::UAF::MirrorPose(
    PoseToMirror,
    EAxis::X,
    MeshBoneMirrorMap,
    RefPoseRotations,
    RefPoseRotationCorrections
);
```

### 进阶用法：使用Trait和任务系统

这是在UAF框架内集成镜像功能的高级方式，涉及Trait的实例化和任务的提交。

**来源文件: `Public/MirroringTask.h`, `Private/MirroringTrait.h`**

```cpp
// 假设在一个UAF Trait的PostEvaluate上下文中
// 1. 准备镜像任务的配置参数
FUAFMirroringTraitSetupParams SetupParams;
SetupParams.bShouldMirror = true;
SetupParams.MirrorDataTable = GetMirrorDataTable(); // 获取你的镜像数据表

FUAFMirroringTraitApplyToParams ApplyToParams;
ApplyToParams.bShouldMirrorBones = true;
ApplyToParams.bShouldMirrorCurves = true;

// 2. 创建并配置镜像任务
TSharedPtr<FAnimNextEvaluationMirroringTask> MirrorTask = MakeShared<FAnimNextEvaluationMirroringTask>();
MirrorTask->Setup = SetupParams;
MirrorTask->ApplyTo = ApplyToParams;

// 3. 任务会在其Execute方法中自动从VM栈顶取出姿态，镜像，再放回。
//    你需要确保它被正确提交到评估流程中。
//    通常，Trait的FInstanceData会持有这个任务的智能指针。
```

**缓存管理**：`FAnimNextEvaluationMirroringTask` 内部包含一个 `FMirroringTraitCache`，用于缓存骨骼映射和绑定姿态数据，以避免每帧重复计算。你也可以在外部使用 `FMirroringTraitCache` 来管理自己的缓存。

## Demo 示例

一个最小化的C++示例，展示如何在独立函数中镜像一个LOD姿态。

```cpp
// MyMirrorDemo.h
#pragma once

#include "CoreMinimal.h"
#include "LODPose.h"

class UMirrorDataTable;

namespace MyDemo
{
    /** 镜像一个LOD姿态 */
    void MirrorLODPoseInPlace(FLODPose& InOutPose, const UMirrorDataTable& MirrorTable, const FReferencePose& RefPose);
}
```

```cpp
// MyMirrorDemo.cpp
#include "MyMirrorDemo.h"
#include "Mirroring.h" // UE::UAF 命名空间下的函数

void MyDemo::MirrorLODPoseInPlace(FLODPose& InOutPose, const UMirrorDataTable& MirrorTable, const FReferencePose& RefPose)
{
    // 直接调用底层的镜像函数，该函数会根据数据表构建映射并执行镜像
    UE::UAF::MirrorPose(InOutPose, MirrorTable);
}
```

## 模块依赖

从 `UAFMirroring.Build.cs` 分析，使用该插件的主要模块需要依赖：

| 模块 | 用途 |
|---|---|
| `UAF` | 核心动画框架，提供姿态、任务、虚拟机等基础设施 |
| `UAFAnimGraph` | 提供动画图（AnimGraph）和Trait系统，用于在动画图中创建镜像节点 |
| `AnimationCore` | 提供动画核心数学和数据类型，如四元数操作、骨骼索引类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至UE_LOGF，统一日志格式。 |
| 2026-03-10 | `24473b8e` | Fix direct reads of latent SharedData properties in UAF traits | 修复了UAF Trait中直接读取延迟共享数据的潜在问题。 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 为UAF插件添加了构建和运行低级测试的验证器。 |
| 2026-01-23 | `81bd488d` | UAF fix some incorrect comparison of invalid bone indicies, where 16bit was upcast to 32bit and comp | 修复了无效骨骼索引比较的错误（16位到32位的隐式转换问题）。 |
| 2026-01-23 | `9735f798` | UAF: Fix rename/move issues | 修复了重命名和文件移动引入的问题。 |

### 维护评价

- **创建时间**：插件创建于2025年8月，非常年轻（约1年）。
- **近期活跃度**：从2026年1月至4月有持续的提交，主要集中在**缺陷修复**（骨骼索引比较、Trait数据读取）和**工程改进**（测试验证、日志规范化），表明插件正在被积极调试和稳定化。
- **当前状态**：**实验性**且**未默认启用**。它作为UAF动画框架的扩展功能，尚处于开发完善阶段。
- **推荐度**：对于**正在使用或评估UAF动画系统**的项目，此插件是实现动画镜像功能的**官方参考实现和直接选择**。对于不使用UAF的传统项目，则无需关注。由于其实验性，建议在引入前进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring/Tests)