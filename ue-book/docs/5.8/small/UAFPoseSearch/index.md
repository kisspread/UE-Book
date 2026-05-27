# UAF Pose Search

> Pose Search integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF姿态搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFPoseSearch` (Runtime), `UAFPoseSearchUncookedOnly` (Runtime), `UAFPoseSearchTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch) | |

## 用途

该插件是 **UAF (Unreal Animation Framework)** 与 **Pose Search** 技术的集成模块。它将 Epic 的动画姿态搜索功能整合到 UAF 的动画图框架中，允许动画师和开发者在基于 UAF 的动画蓝图中直接使用姿态搜索节点，实现更智能、数据驱动的动画过渡与混合。它解决的核心问题是：如何让基于姿态相似性的动画匹配技术与 UAF 的模块化动画工作流协同工作，从而驱动更复杂的角色动画状态机。

## 使用场景

- 你正在使用 UAF 构建一个复杂角色的动画蓝图，并希望在动画状态之间实现基于当前骨骼姿态的自动、平滑过渡。
- 你需要让角色在执行连招或受到攻击时，能自动从姿态库中匹配到最合适的动画片段进行播放。
- 你的项目采用了 UAF 的数据驱动方法，现在需要引入基于机器学习或数据库查询的姿态搜索能力。

## 蓝图用法

基于其作为“集成”插件的定位，其核心蓝图节点主要用于在 UAF 的动画图中接入姿态搜索功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PoseSearch` 相关节点 | 在 UAF 动画图中用于发起姿态搜索、获取匹配结果并驱动动画过渡的节点集合。 | 集成在 UAF 动画图系统中 |
| `DebuggerTrackCreator` 相关 | 用于在动画调试器中创建和可视化姿态搜索相关调试轨道的工具类。 | `FUAFDebuggerTrackCreator` |

### 使用示例（蓝图描述）

1.  在你的 **UAF 动画蓝图** 中，添加一个 `PoseSearch` 节点。
2.  将该节点连接到你的动画状态机或状态树中，通常作为状态切换的触发条件或评估器。
3.  配置该节点，指定要搜索的 **姿态数据库 (Pose Search Database)** 以及搜索参数（如查询姿态、搜索范围等）。
4.  节点的输出（如匹配到的动画片段、时间、成本等）可以连接到其他动画节点或状态机的输入，用于驱动动画播放。

## C++ 用法

该插件主要提供 Runtime 模块和一些未烘焙（UncookedOnly）的工具逻辑，其 C++ API 通常用于在更底层的系统中集成姿态搜索。

### 头文件引入

```cpp
#include "UAFPoseSearch/UAFPoseSearchModule.h"
```

### 基本用法

创建一个继承自 UAF 或 Pose Search 相关基类的 C++ 类，以实现自定义的姿态搜索逻辑或动画节点。

```cpp
// 示例：创建一个自定义的动画节点（需包含必要的 UAF 和 PoseSearch 头文件）
#include "Animation/AnimNodeBase.h"
#include "PoseSearch/PoseSearchResult.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MyCustomPoseSearchNode : public FAnimNode_Base
{
    GENERATED_BODY()

    // 实现节点的初始化、缓存、评估等函数
    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;
    virtual void CacheBones_AnyThread(const FAnimationCacheBonesContext& Context) override;
    virtual void Update_AnyThread(const FAnimationUpdateContext& Context) override;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;

    // 成员变量：可以包含 FPoseSearchResult 等来存储搜索结果
    FPoseSearchResult CurrentSearchResult;
};
```

## Demo 示例

由于缺乏详细的源码示例，以下为概念性代码结构，展示了集成插件可能的 C++ 类声明。

```cpp
// MyUAFPoseSearchNode.h
#pragma once
#include "Animation/AnimNodeBase.h"
#include "PoseSearch/PoseSearchDatabase.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MyUAFPoseSearchNode : public FAnimNode_Base
{
    GENERATED_BODY()

    // 数据库资产
    UPROPERTY(EditAnywhere, Category = "Pose Search")
    TObjectPtr<UPoseSearchDatabase> Database;

    // 查询接口
    // ... 其他成员和函数
};
```

## 模块依赖

该插件作为 UAF 和 Pose Search 的集成点，其模块依赖关系主要位于其源码内部。对于使用该插件的项目模块，通常无需额外添加特殊依赖，只需在 `.uplugin` 或 `.uproject` 中启用本插件即可。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `7b3fe3c2` | Use FPoseValueBundle in AnimOp value bundle evaluator | 在动画操作值包评估器中集成使用FPoseValueBundle |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏，提升日志记录功能 |
| 2026-04-01 | `e9bc431c` | PoseSearch - removing unnecessary MotionMatchingInteraction node | 清理不必要的MotionMatchingInteraction节点 |
| 2026-04-01 | `d6ad87e4` | UAFPoseSearch - consolidating FUAFDebuggerTrackCreator and FDebuggerTrackCreator, since GetTargetTyp... | 统一调试轨道创建器，修复目标类型获取问题 |
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 为单子动画节点添加修改器动画节点数据基类 |

### 维护评价

**活跃维护的实验性插件**。该插件创建于2025年6月，非常年轻。从近期提交记录看，其在2026年4月仍有**频繁的功能性更新**，包括核心功能的迁移、节点优化、代码重构和基类添加。这表明它正在被积极开发和迭代，处于功能扩展和稳定化阶段。

**使用建议**：由于其 **`IsExperimentalVersion=true`** 且 `EnabledByDefault=false`，它明确属于**实验性**插件。目前适合用于**原型开发、内部技术评估和早期项目**，不建议直接在稳定的商业项目中默认启用。开发团队需要关注其API可能随着实验性状态的推进而发生变化。它是一个有前景的、正在积极发展的技术集成点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch/Tests)