# UAF Pose Search

> Pose Search integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 姿态搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFPoseSearch` (Runtime), `UAFPoseSearchUncookedOnly` (Runtime), `UAFPoseSearchTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch) | |

## 用途

UAFPoseSearch 是一个集成插件，其主要功能是将 UE 的 PoseSearch（姿态搜索/运动匹配）系统与 UAF（统一动画框架）连接起来。它为 UAF 提供了一个“姿态数据库访问器组件”，使得基于 UAF 的动画逻辑能够方便地查询和使用 PoseSearch 数据库，从而利用运动匹配技术来优化动画混合与过渡。

此插件解决的核心问题是：让开发者能够在 UAF 这种更结构化、更面向未来的动画框架中，无缝地使用引擎内置的高性能运动匹配能力。

## 使用场景

- 你正在使用 UAF 框架构建角色动画逻辑，并希望利用 PoseSearch 来实现更流畅、更物理真实的角色移动和动画过渡。
- 你在开发一个开放世界或高动态性游戏，其中角色的动作混合（如走、跑、跳、交互）需要基于当前运动状态进行智能匹配，而你的动画系统基于 UAF。

## 蓝图用法

根据提供的源码文件列表，该插件主要通过 `UPoseSearchDatabaseAccessorComponent` 暴露功能给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UPoseSearchDatabaseAccessorComponent` | 提供对 PoseSearch 数据库的访问，可作为 Actor 组件使用。 | `UAnimOpsSubsystem` (推测) |

*注意：由于提供的文件列表未包含具体头文件内容，以上为基于组件名称的合理推测。实际可用的蓝图节点需查阅 `PoseSearchDatabaseAccessorComponent.h` 中的 `UFUNCTION` 宏定义。*

## C++ 用法

### 头文件引入

```cpp
#include "UAFPoseSearch/PoseSearchDatabaseAccessorComponent.h" // 核心组件
```

### 基本用法

由于未提供具体测试用例代码，以下为基于组件命名的推测性示例。

**来源: `PoseSearchDatabaseAccessorComponent.h` (推测)**
```cpp
// 在需要访问姿态搜索数据库的 Actor 中
UPoseSearchDatabaseAccessorComponent* PoseSearchAccessor = NewObject<UPoseSearchDatabaseAccessorComponent>(this, TEXT("PoseSearchDBAccessor"));
// 假设存在一个方法来设置数据库
// PoseSearchAccessor->SetDatabase(MyPoseSearchDatabaseAsset);
```

### 进阶用法

在 UAF 的 AnimNode 或 AnimOp 中集成姿态搜索功能。

**来源: 推测与 AnimOps 相关**
```cpp
// 在一个自定义的 UAF AnimOp 或 AnimNode 中，使用 PoseSearch 数据库进行查询
// 假设通过某种方式获取到了 PoseSearchAccessor
// FSearchResult Result = PoseSearchAccessor->Search(CurrentMotionParameters);
// 然后根据 Result 来驱动动画混合或选择
```

## Demo 示例

*由于该插件为运行时集成模块，本身不包含可独立运行的完整示例。其使用依赖于 UAF 框架和 PoseSearch 系统的配置。一个最小示例通常涉及：*
1.  *在 Actor 上添加 `UPoseSearchDatabaseAccessorComponent`。*
2.  *将一个 PoseSearch 数据库资产赋值给该组件。*
3.  *在 UAF 动画逻辑（如 AnimOp/AnimNode）中调用该组件进行搜索。*

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PoseSearch` | 核心的姿态搜索/运动匹配运行时库。 |
| `UAF` (或 `UAFCore`) | 提供统一动画框架的基础结构和接口。 |
| `AnimationCore` | 动画系统核心工具库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `7b3fe3c2` | Use FPoseValueBundle in AnimOp value bundle evaluator | 将 AnimOp 的值包求值器迁移至使用 FPoseValueBundle 结构体 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF |
| 2026-04-01 | `e9bc431c` | PoseSearch - removing unnecessary MotionMatchingInteraction node | 移除 PoseSearch 中不必要的 MotionMatchingInteraction 节点 |
| 2026-04-01 | `d6ad87e4` | UAFPoseSearch - consolidating FUAFDebuggerTrackCreator and FDebuggerTrackCreator, since GetTargetTyp... | 合并 UAFPoseSearch 的调试轨道创建器类，简化目标类型获取逻辑 |
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 为单子节点的动画节点添加修改器动画节点数据基类 |

### 维护评价

- **状态**: 活跃维护中。
- **创建时间**: 2025年6月创建，是一个非常新的插件。
- **最近更新**: 在2026年4月有多次功能性更新和重构，表明该插件正在积极开发和集成中。
- **实验性**: 作为实验性插件，其API和功能可能尚未稳定，且 `EnabledByDefault=false`，需要开发者手动启用。
- **推荐**: 对于正在使用或评估 UAF 框架的团队，如果计划集成运动匹配技术，这是一个**值得关注和跟进**的插件。但在生产环境中使用需谨慎，因其处于实验阶段，接口可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch)
- 官方文档: 暂无
- 测试用例: `Tests/UAFPoseSearchTests`