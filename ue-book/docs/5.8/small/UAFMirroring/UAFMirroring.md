# UAF Mirroring

> Keyframe mirroring for UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 帧镜像 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMirroring` (Runtime), `UAFMirroringUncookedOnly` (Runtime), `UAFMirroringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring) | |

## 用途

UAFMirroring 是 Unified Animation Framework（UAF）的关键帧镜像系统。它解决的核心问题是：在 UAF 动画求值管线中，将动画 Pose（姿态）沿指定轴进行镜像翻转。

该插件存在的原因：角色动画中经常需要"左→右"的对称动作（如左手挥拳的镜像即为右手挥拳）。传统做法需要美术手动制作镜像动画资产，而 UAFMirroring 通过运行时镜像求值，允许只制作一侧动画，另一侧自动翻转，大幅减少动画资产数量。

具体功能包括：
- 提供基础镜像 Trait（`FMirroringTrait`）和叠加镜像 Trait（`FMirroringAdditiveTrait`），集成到 UAF 的 Trait 系统中
- 支持镜像骨骼变换、动画曲线和自定义属性三个通道
- 使用 `UMirrorDataTable` 定义骨骼名称的左右映射关系
- 内置缓存系统（`FMirroringTraitCache`），避免每帧重建镜像映射表
- 提供底层 Pose 镜像函数，可独立于 Trait 系统使用

## 使用场景

- 你使用 UAF 动画系统，需要为角色自动镜像左右对称动画 → 使用 `FMirroringTrait`
- 你有一个叠加动画层需要镜像（如镜像的 addtive 呼吸动画）→ 使用 `FMirroringAdditiveTrait`
- 你只需要镜像骨骼，不需要镜像曲线和属性 → 通过 `FUAFMirroringTraitApplyToParams` 精细控制
- 你有自定义的 UAF 求值管线，需要手动镜像一个 LODPose → 使用 `UE::UAF::MirrorPose()` 工具函数

## 蓝图用法

本插件主要面向 C++ 层面的 UAF Trait 系统，不直接暴露 `BlueprintCallable` 函数。蓝图层面的配置通过 Trait 的 SharedData 属性在动画图编辑器中完成。

### 核心配置结构

| 结构体 | 说明 | 所在类 |
|---|---|---|
| `FUAFMirroringTraitSetupParams` | 镜像开关 + 数据表引用 | `Public/MirroringTask.h` |
| `FUAFMirroringTraitApplyToParams` | 控制镜像哪些通道（骨骼/曲线/属性） | `Public/MirroringTask.h` |
| `FMirroringTraitSharedData` | 基础镜像 Trait 的图节点配置 | `Internal/MirroringTraitData.h` |
| `FMirroringAdditiveTraitSharedData` | 叠加镜像 Trait 的图节点配置 | `Internal/MirroringTraitData.h` |

### 使用示例（UAF 动画图编辑器）

在 UAF 动画图中添加 **Mirroring** 节点后：
1. **Setup** 分类下：设置 `Mirror = true`，指定 `MirrorDataTable` 资产
2. **Apply To** 分类下：根据需要勾选 `Bones`、`Curves`、`Attributes`
3. 将上游动画节点的输出连接到 Mirroring 节点的 `Input` 引脚
4. Mirroring 节点的输出即为镜像后的 Pose

## C++ 用法

### 头文件引入

```cpp
// 镜像任务和配置结构体
#include "MirroringTask.h"

// 底层镜像工具函数（Private，仅模块内部可用）
#include "Mirroring.h"

// Trait 定义（UAF Trait 系统内部使用）
#include "MirroringTrait.h"
```

### 基本用法

直接使用底层工具函数镜像一个 Pose：

```cpp
#include "Private/Mirroring.h"
#include "LODPose.h"

void MirrorAnimationPose(FLODPose& InOutPose, const UMirrorDataTable& MirrorTable)
{
    // 简单接口：传入 Pose 和镜像数据表，原地镜像
    UE::UAF::MirrorPose(InOutPose, MirrorTable);
}
```

### 使用预计算数据的高级镜像

当需要批量镜像多个 Pose 或每帧镜像时，可预计算绑定姿态数据以提升性能：

```cpp
#include "Private/Mirroring.h"

void MirrorPoseWithPrecomputedData(
    const UE::UAF::FReferencePose& RefPose,
    const UMirrorDataTable& MirrorTable,
    FLODPose& InOutPose)
{
    const int32 NumBones = UE::UAF::GetNumOfBonesForMirrorData(RefPose);

    // 1. 构建骨骼镜像映射表
    TArray<FBoneIndexType> MirrorMap;
    MirrorMap.SetNum(NumBones);
    UE::UAF::BuildMeshBoneIndexMirrorMap(RefPose, MirrorTable, MirrorMap);

    // 2. 构建绑定姿态镜像数据
    TArray<FQuat> RefRotations;
    TArray<FQuat> RefCorrections;
    RefRotations.SetNum(NumBones);
    RefCorrections.SetNum(NumBones);
    UE::UAF::BuildReferencePoseMirrorData(
        RefPose, EAxis::X, MirrorMap,
        RefRotations, RefCorrections);

    // 3. 使用预计算数据执行镜像（高效路径）
    UE::UAF::MirrorPose(
        InOutPose, EAxis::X,
        MirrorMap, RefRotations, RefCorrections);
}
```

### Trait 系统中的缓存使用

`FMirroringTraitCache` 管理预计算的镜像数据，自动检测资产变更并重建：

```cpp
// Trait 内部通过 EnsureCache 自动管理缓存
// 开发者通常不直接操作缓存，但可理解其工作方式：

UE::UAF::FMirroringTraitCache Cache;

// 检查缓存是否有效（骨架或镜像表变更时需要重建）
bool bValid = Cache.IsValid(RefPose, MirrorTableWeakPtr, 
                            bMirrorBones, bMirrorAttributes);

// 缓存无效时清空并重建
if (!bValid)
{
    Cache.Clear();
    // 重建逻辑在 FAnimNextEvaluationMirroringTask::EnsureCache 中处理
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | Unified Animation Framework 核心（Trait 系统、Pose 定义、求值 VM） |
| `UAFAnimGraph` | UAF 动画图模板系统（用于镜像节点的图模板注册） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移为新格式 |
| 2026-03-10 | `24473b8e` | Fix direct reads of latent SharedData properties in UAF traits | 修复 Trait 延迟属性直接读取问题 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 添加 UAF 插件构建验证和低级测试 |
| 2026-01-23 | `81bd488d` | UAF fix some incorrect comparison of invalid bone indicies, where 16bit was upcast to 32bit and comp | 修复骨骼索引比较时 16 位到 32 位的隐式转换问题 |
| 2026-01-23 | `9735f798` | UAF: Fix rename/move issues | 修复文件重命名/移动后的引用问题 |

### 维护评价

- **状态**：活跃维护中
- 创建于 2025 年 8 月，属于较新的实验性插件
- 近期（2026 年 1-4 月）持续有更新，包括 bug 修复、基础设施改进和代码质量提升
- 作为 UAF 生态系统的一部分，与 UAF 核心一同迭代
- **⚠️ 注意**：`IsExperimentalVersion = true`，API 可能随版本变更而不兼容
- 依赖 UAF 和 UAFAnimGraph 两个同为实验性的插件，需确保它们已启用
- **推荐使用**：如果你已在使用 UAF 动画系统，这是镜像功能的标准实现；如果是新项目，建议关注 UAF 的整体成熟度

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring)
- [官方文档]()（暂无）
- [UAF 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF)
- [UAFAnimGraph 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph)