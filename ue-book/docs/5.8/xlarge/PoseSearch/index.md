# Pose Search

> Framework for indexing and searching pose features. Used in techniques such as Motion Matching.

| 属性 | 值 |
|---|---|
| 中文名 | 姿态搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画节点） |
| 模块 | `PoseSearch` (Runtime), `PoseSearchEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-06-16 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PoseSearch) | |

## 用途

PoseSearch 插件的核心是为动画资产（如序列、混合空间）构建高效、可查询的特征索引。它解决的核心问题是：**在海量动画数据中，根据角色当前的运动姿态（如骨骼位置、速度），以近乎实时的速度找到最匹配的动画片段**。这是实现 Motion Matching 技术的关键基础设施。与传统的状态机相比，它通过空间搜索而非硬编码转换来驱动动画，能产生更自然、更响应性的动作。

## 使用场景

- **Motion Matching 动画系统**：为 AAA 级角色动画（如动作游戏、体育游戏）构建无需状态机的流畅动画系统。
- **动画资产检索**：在大量动画片段中快速找到与当前姿态最匹配的片段，用于实现“动画版的数据库查询”。
- **动态动画混合**：根据实时运动数据，动态选择并混合最佳动画，提升角色响应性和动画质量。

## 蓝图用法

### 核心资产

| 资产 | 说明 |
|---|---|
| `UPoseSearchDatabase` | 存储和管理一组动画资产的索引数据，是执行搜索的数据源。 |
| `UPoseSearchSchema` | 定义搜索时需要采样的特征，如哪些骨骼、通道（位置、速度）以及采样频率。 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FAnimNode_PoseMatchingSequencePlayer` | 扩展了标准序列播放器，根据 PoseSearch 的结果自动偏移播放起始点，实现 Motion Matching。 | `UAnimNode_PoseMatchingSequencePlayer` |
| `FAnimNode_PoseSearchHistoryCollector` | 收集一段时间内的角色姿态历史，用于构建搜索查询的上下文（“过去几帧的姿态”）。 | `UAnimNode_PoseSearchHistoryCollector` |

### 使用示例（蓝图描述）

1.  **设置数据库与模式**：创建一个 `UPoseSearchSchema` 资产，指定要分析的骨骼（如根骨、脊柱、四肢）和通道（如平移、速度）。创建一个 `UPoseSearchDatabase` 资产，添加你的动画序列并关联 Schema，然后构建索引。
2.  **在动画蓝图中使用**：
    - 在动画图中添加 `PoseSearchHistoryCollector` 节点，用于记录姿态历史。
    - 替换标准的 `SequencePlayer` 为 `PoseMatchingSequencePlayer` 节点。
    - 将 `PoseMatchingSequencePlayer` 的数据库（Database）属性连接到你创建的 `UPoseSearchDatabase` 资产。
    - 该节点会自动根据当前和历史的姿态，在数据库中搜索并播放最匹配的动画片段。

## C++ 用法

### 头文件引入

```cpp
#include "PoseSearch/PoseSearch.h"
```

### 基本用法

以下代码展示了如何以编程方式构建索引并进行一次搜索查询。

```cpp
// 假设已持有有效的动画序列指针 UAnimSequence* MySequence
// 以及一个定义好的搜索模式 UPoseSearchSchema* MySchema

// 1. 为动画序列构建索引
FPoseSearchIndex SearchIndex;
PoseSearchBuildIndex(MySequence, MySchema, SearchIndex);

// 2. 假设已经通过其他方式获得了当前的姿态查询（FPoseSearchQuery）
// FPoseSearchQuery CurrentQuery = ...;

// 3. 在已索引的序列中搜索最匹配的姿态
FPoseSearchResult SearchResult;
PoseSearch(SearchIndex, CurrentQuery, SearchResult);

// 4. 使用搜索结果（例如，获取最佳匹配的动画时间）
if (Result.IsValid())
{
    float BestTime = Result.GetTime();
    // 使用 BestTime 驱动动画播放...
}
```

### 进阶用法

实际生产中，通常直接使用动画节点 `AnimNode_PoseMatchingSequencePlayer`，它封装了完整的构建查询、执行搜索和应用结果的逻辑。开发者主要工作是配置 `UPoseSearchDatabase` 和 `UPoseSearchSchema` 资产，以及实现自定义的 `FPoseSearchProvider` 接口（如需）来为系统提供当前角色的姿态数据。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimGraph` | 动画蓝图和动画节点的基础设施。 |
| `AnimationCore` | 底层动画数据结构和工具。 |
| `PoseSearch` | 插件的核心运行时模块，提供索引构建、查询和搜索算法。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `314d38e0` | Fixed crash when loading trace file with missing assets in project (specifically a USkinnedAsset) | 修复因项目缺失资产导致的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的编译警告 |
| 2026-05-12 | `1222a3b1` | PoseSearch - fix for Motion Matching Database editor Preview viewport doesn't display static mesh at | 修复编辑器预览窗口中静态网格体不显示的问题 |
| 2026-05-12 | `eddf36ad` | PoseSearch - fix velocity channel debug visualization | 修复速度通道的调试可视化 |
| 2026-05-12 | `b57412ab` | PoseSearch - Expose preview-mesh cap in Pose Search Database editor | 在数据库编辑器中暴露预览网格体上限设置 |

### 维护评价

PoseSearch 插件自 2020 年创建以来持续维护，近期（2026年5月）仍有活跃更新，主要集中在**稳定性修复**和**编辑器工具增强**。尽管其核心搜索算法已相对成熟，但 Epic 仍在积极改进其工具链和修复边缘情况问题。这是一个**推荐使用**的生产级模块，特别是对于追求高品质动画的项目。需要注意的是，它默认未启用，需要手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PoseSearch)
- [子模块文档：PoseSearch](PoseSearch.md)
- [子模块文档：PoseSearchEditor](PoseSearchEditor.md)