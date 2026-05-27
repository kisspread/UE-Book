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
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch) | |

## 用途

UAFPoseSearch 是 Unreal Animation Framework (UAF) 与 Pose Search 系统之间的集成桥接插件。它的核心作用是在 UAF 的动画图（Animation Graph）节点系统中提供 Motion Matching（运动匹配）能力。

**解决的问题**：UAF 是 Epic 的下一代动画框架，而 Pose Search 是基于数据库驱动的姿态匹配系统。这个插件将两者连接起来，让开发者可以在 UAF 的节点图工作流中直接使用 Pose Search 的运动匹配功能，包括：

- 在 UAF 动画图中添加 Motion Matching 节点
- 自动集成历史轨迹收集器（History Collector）用于姿态预测
- 支持拖放 PoseSearchDatabase 资产到节点图
- 提供混合栈（Blend Stack）和混合平滑器（Blend Smoother）的自动配置

**为什么存在**：UAF 和 Pose Search 分别是独立的动画子系统，没有这个插件，两者无法在 UAF 节点图中协同工作。这是实验性的集成层，旨在让 Pose Search 的运动匹配能力无缝嵌入 UAF 的动画图编辑器体验中。

## 使用场景

- 你在使用 UAF 动画框架开发角色动画系统，需要运动匹配功能 → 用 UAFPoseSearch
- 你需要在 UAF 节点图中通过拖放 PoseSearchDatabase 来配置运动匹配 → 用 UAFPoseSearch
- 你希望运动匹配节点自动集成轨迹预测和平滑混合 → 用 UAFPoseSearch

## 蓝图用法

此插件主要通过 UAF 节点图（RigVM 节点图）操作，不直接暴露标准蓝图函数。核心功能通过节点模板（Graph Node Template）实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| Motion Matching | 在 PoseSearchDatabase 上执行运动匹配，自动集成历史轨迹收集 | `UUAFGraphNodeTemplate_MotionMatching` |

### 使用示例（节点图操作）

1. 在 UAF 动画图编辑器中，从 UAF 类别下找到 **Motion Matching** 节点
2. 将 **PoseSearchDatabase** 资产拖放到节点上，自动连接到 Databases 引脚
3. 节点会自动配置以下 Trait：
   - Blend Stack Core（混合栈核心）
   - Blend Smoother Core（混合平滑器核心）
   - Motion Matching（运动匹配）
   - History Collector（历史轨迹收集器）
4. 配置 Trajectory 引脚以提供轨迹预测数据

## C++ 用法

### 头文件引入

```cpp
#include "UAFPoseSearchModule.h"
```

### 基本用法

此插件主要作为 UAF 与 Pose Search 之间的集成层，C++ 层面的核心是节点模板注册系统。以下是节点模板的结构示意（来自 `Private/UAFGraphNodeTemplate_MotionMatching.h`）：

```cpp
// 节点模板定义了 Motion Matching 节点在 UAF 图编辑器中的行为
// 通常不需要直接创建此类实例，它由系统自动注册
UUAFGraphNodeTemplate_MotionMatching()
{
    // 设置节点标题和提示文本
    Title = LOCTEXT("MotionMatchingTitle", "Motion Matching");
    Category = LOCTEXT("MotionMatchingCategory", "UAF");
    
    // 配置支持拖放的资产类型
    DragDropAssetTypes.Add(UPoseSearchDatabase::StaticClass());
    
    // 自动配置 Trait（混合栈、平滑器、运动匹配、历史收集器）
    Traits =
    {
        TInstancedStruct<FAnimNextBlendStackCoreTraitSharedData>::Make(),
        TInstancedStruct<FAnimNextBlendSmootherCoreTraitSharedData>::Make(),
        TInstancedStruct<FMotionMatchingTraitSharedData>::Make(),
        TInstancedStruct<FAnimNextHistoryCollectorTraitSharedData>::Make()
    };
}
```

## Demo 示例

此插件为集成桥接层，不提供独立的可编译示例。使用方式是在 UAF 动画图编辑器中操作 Motion Matching 节点。如需在代码中使用 Motion Matching，请参考 PoseSearch 插件本身的 API。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PoseSearch` | 核心姿态搜索和运动匹配引擎 |
| `UAF` | Unreal Animation Framework 动画框架 |
| `AnimNext` | 下一代动画系统，提供混合栈和历史收集器 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `7b3fe3c2` | Use FPoseValueBundle in AnimOp value bundle evaluator | 适配动画操作值包的API变更 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 日志宏迁移到新版UE_LOGF |
| 2026-04-01 | `e9bc431c` | PoseSearch - removing unnecessary MotionMatchingInteraction node | 移除不必要的运动匹配交互节点 |
| 2026-04-01 | `d6ad87e4` | UAFPoseSearch - consolidating FUAFDebuggerTrackCreator and FDebuggerTrackCreator, since GetTargetTyp | 合并调试器追踪创建器，统一类型获取逻辑 |
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 添加单子节点动画节点的修改器基类 |

### 维护评价

- **状态**：活跃维护中
- **年龄**：约 1 年，属于较新的实验性插件
- **活跃度**：2026 年 4 月仍有持续更新，包括 API 适配、代码清理和功能整合
- **风险提示**：标记为 `IsExperimentalVersion=true`，API 随时可能发生破坏性变更
- **推荐**：适合早期采用者和实验性项目，生产环境需谨慎评估稳定性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch/Tests)