# UAF Pose Search

> Pose Search integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF姿态搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFPoseSearch` (Runtime), `UAFPoseSearchUncookedOnly` (Runtime), `UAFPoseSearchTests` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch) | |

## 用途

该插件是 Unreal Animation Framework (UAF) 与 Pose Search 动画系统之间的桥梁。其核心目的是在 UAF 的动画图 (AnimNext) 系统中无缝集成运动匹配 (Motion Matching) 功能。它通过提供特定的动画图节点和配套的编辑器工具，允许开发者在 UAF 的图形化动画逻辑中方便地使用 Pose Search 数据库进行高效的动画混合与匹配，解决了在 UAF 框架内接入和驱动运动匹配工作流的问题。

## 使用场景

- **动态动画混合游戏**：正在使用 UAF 框架开发需要根据角色实时状态（如速度、方向、输入）动态选择并混合动画片段的游戏，例如体育竞技、动作冒险游戏。
- **简化运动匹配集成**：希望在 UAF 提供的高级动画图编辑器中直接使用运动匹配功能，而不是在 C++ 或蓝图底层手动管理 Pose Search 查询和过渡。
- **需要轨迹历史收集的动画**：运动匹配节点集成了历史轨迹收集器 (`FAnimNextHistoryCollectorTraitSharedData`)，适用于需要精确预测角色未来移动路径以选择最佳匹配动画的场景。

## 蓝图用法

该插件主要提供编辑器内的图形节点，其蓝图可调用函数通常用于自定义或扩展这些节点的行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| **Motion Matching** | 核心节点。在 UAF 动画图中执行运动匹配，基于输入的轨迹和 Pose Search 数据库选择最匹配的动画。 | `UUAFGraphNodeTemplate_MotionMatching` (编辑器模板) |

### 使用示例（蓝图描述）

在 UAF 动画图编辑器中：
1.  创建一个新的 UAF 动画图。
2.  从节点菜单的 “UAF” 分类下拖拽出 “Motion Matching” 节点。
3.  将 “Databases” 引脚连接到你已创建的 `UPoseSearchDatabase` 资产。
4.  将 “Trajectory” 引脚连接到提供角色历史与未来轨迹数据的输入（通常来自历史收集器节点）。
5.  该节点会输出匹配到的动画片段，连接到后续的动画混合或播放节点。

## C++ 用法

该插件的集成主要发生在动画图节点配置层面，开发者通常需要通过 C++ 来创建和配置这些节点的数据。

### 头文件引入

```cpp
#include "UAFPoseSearch.h"
#include "UAFGraphNodeTemplate_MotionMatching.h" // 如果需要直接操作模板类
```

### 基本用法

配置运动匹配节点所需的特性数据 (Trait)。这是节点行为的底层驱动逻辑。

```cpp
// 来源: Private/UAFGraphNodeTemplate_MotionMatching.h
// 创建一个运动匹配节点所需的核心特性数据实例
TInstancedStruct<FMotionMatchingTraitSharedData> MotionMatchingTrait = TInstancedStruct<FMotionMatchingTraitSharedData>::Make();

// 配置运动匹配特性，例如关联 Pose Search 数据库
// FMotionMatchingTraitSharedData 的具体成员需查看其头文件
// MotionMatchingTrait.GetMutable<FMotionMatchingTraitSharedData>().Databases = ...;

// 通常，这些特性会组合在一起设置到动画图节点模板中
TArray<TInstancedStruct<FAnimNextTraitSharedData>> Traits =
{
    TInstancedStruct<FAnimNextBlendStackCoreTraitSharedData>::Make(),
    TInstancedStruct<FAnimNextBlendSmootherCoreTraitSharedData>::Make(),
    MotionMatchingTrait, // 包含运动匹配逻辑
    TInstancedStruct<FAnimNextHistoryCollectorTraitSharedData>::Make() // 包含轨迹收集
};
```

### 进阶用法

在编辑器扩展中，自定义运动匹配节点的模板或行为。`UUAFGraphNodeTemplate_MotionMatching` 定义了节点的外观、类别和默认特性。

```cpp
// 继承 UUAFGraphNodeTemplate 可以创建自定义的 UAF 动画节点模板
UCLASS()
class UMyCustomMotionMatchingNodeTemplate : public UUAFGraphNodeTemplate
{
    GENERATED_BODY()
public:
    UMyCustomMotionMatchingNodeTemplate()
    {
        Title = LOCTEXT("MyNodeTitle", "Custom Motion Match");
        // 设置不同的颜色、图标、菜单描述等
        Color = FLinearColor::Red;
        // 配置默认的特性，例如只包含运动匹配，不包含平滑器
        Traits = { TInstancedStruct<FMotionMatchingTraitSharedData>::Make() };
        // 设置引脚分类，影响节点在编辑器中的引脚布局
        SetCategoryForPinsInLayout(
            { GET_PIN_PATH_STRING_CHECKED(FMotionMatchingTraitSharedData, Databases) },
            FRigVMPinCategory::GetDefaultCategoryName(),
            NodeLayout,
            true);
    }
};
```

## Demo 示例

一个创建和配置运动匹配动画节点的最小 C++ 示例。注意，这主要在编辑器上下文中使用。

**MyMotionMatchingAnimLayer.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "AnimNext/AnimNode_AnimNext.h"
#include "MyMotionMatchingAnimLayer.generated.h"

USTRUCT(BlueprintInternalUseOnly)
struct FMyMotionMatchingAnimLayer : public FAnimNode_AnimNext
{
    GENERATED_BODY()

    // 在此定义动画层的输入输出引脚
    // UPROPERTY(...)
    // FPoseLink TrajectoryInput;

    // 运动匹配节点内部使用的特性数据通常由框架管理，此处仅作示意
    // FMotionMatchingTraitSharedData MotionMatchingTrait;

    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;
    virtual void CacheBones_AnyThread(const FAnimationCacheBonesContext& Context) override;
    virtual void Update_AnyThread(const FAnimationUpdateContext& Context) override;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
};
```

**MyMotionMatchingAnimLayer.cpp**
```cpp
#include "MyMotionMatchingAnimLayer.h"
#include "UAFPoseSearch.h" // 引入插件头文件以访问其内部类型或工具

void FMyMotionMatchingAnimLayer::Initialize_AnyThread(const FAnimationInitializeContext& Context)
{
    FAnimNode_AnimNext::Initialize_AnyThread(Context);
    // 初始化逻辑，例如重置运动匹配状态
}

void FMyMotionMatchingAnimLayer::Update_AnyThread(const FAnimationUpdateContext& Context)
{
    // 更新轨迹历史等
    // 更新运动匹配查询参数
    FAnimNode_AnimNext::Update_AnyThread(Context);
}

void FMyMotionMatchingAnimLayer::Evaluate_AnyThread(FPoseContext& Output)
{
    // 核心评估逻辑：执行运动匹配查询，选择最佳动画并输出姿态
    // 此过程通常由插件提供的 Trait（如 FMotionMatchingTraitSharedData）封装并自动处理
    FAnimNode_AnimNext::Evaluate_AnyThread(Output);
}
```

## 模块依赖

从 Build.cs 分析得出，使用此插件需要以下非标准模块依赖：

| 模块 | 用途 |
|---|---|
| `PoseSearch` | 提供核心的运动匹配功能、数据库资产 (`UPoseSearchDatabase`) 和查询逻辑。 |
| `UAF` | 提供 Unreal Animation Framework 的基础框架、动画图节点系统 (`UAnimNext`) 和特性 (`FAnimNextTraitSharedData`)。 |
| `PoseSearchDatabaseEditor` | 提供用于编辑和预览 `UPoseSearchDatabase` 资产的编辑器工具。 |
| `AnimNext` | UAF 动画图的核心运行时模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `7b3fe3c2` | Use FPoseValueBundle in AnimOp value bundle evaluator | 在动画操作求值器中采用新的 FPoseValueBundle 类型。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-01 | `e9bc431c` | PoseSearch - removing unnecessary MotionMatchingInteraction node | 移除了 PoseSearch 中不必要的 MotionMatchingInteraction 节点。 |
| 2026-04-01 | `d6ad87e4` | UAFPoseSearch - consolidating FUAFDebuggerTrackCreator and FDebuggerTrackCreator, since GetTargetTyp | 合并 UAFPoseSearch 中的调试器轨道创建器类。 |
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 添加了用于单子节点动画节点的修改器动画节点数据基类。 |

### 维护评价

该插件创建于 2025 年 6 月，历史约一年。从最近的提交（2026年4月）来看，插件仍在**活跃维护**中，更新内容涉及功能优化（如类型迁移、节点整合）和代码质量改进（日志标准化）。它被明确标记为 `IsExperimentalVersion: true`，意味着其 API 和功能仍处于实验阶段，未来可能发生不兼容的更改。考虑到其集成了两个复杂系统（UAF 和 Pose Search），且更新仍在进行，推荐对动画系统有深度定制需求且能接受实验性风险的项目使用。普通项目建议观望，或仅在开发环境中试用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch/Tests) （路径推断，通常在 Tests 子目录下）