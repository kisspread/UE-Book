# Pose Search

> Framework for indexing and searching pose features. Used in techniques such as Motion Matching.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 姿态搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `PoseSearch` (Runtime), `PoseSearchEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-16 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PoseSearch) | |

## 用途

PoseSearch 插件提供了一个用于高效索引和搜索动画姿态特征的框架，其核心应用场景是 **Motion Matching（运动匹配）**。该插件解决了在大型动画数据库中快速找到与当前角色状态最匹配的动画片段的问题。它通过离线预计算动画序列的关键姿态特征（如骨骼位置、速度等），并构建索引，使得运行时能够以极高的效率进行相似性搜索。这使得游戏角色能够根据其当前的运动状态（如速度、轨迹）流畅、自然地过渡到最合适的动画，避免了传统的基于状态机或混合树的动画系统可能出现的僵硬或跳帧现象，常用于实现高品质的动作游戏或需要高保真动画的角色控制系统。

## 使用场景

- **动作游戏**：你正在开发一个需要丰富、连贯且反应灵敏的角色动画的动作游戏（如格斗、冒险游戏），使用 Motion Matching 来根据玩家的输入和角色的物理状态（速度、朝向）自动选择并混合最佳的动画片段，实现无缝的动作过渡。
- **高品质角色动画**：你需要为电影或高品质游戏角色制作逼真的动画，希望角色的动画能根据其运动轨迹和环境（如上下坡、急转弯）进行精确匹配，而不是依赖人工设置的过渡规则。
- **动画编辑器调试**：你在 UE 动画编辑器中工作，需要可视化、检查和调试 Motion Matching 数据库、搜索查询以及匹配结果，以优化动画资产和算法参数。

## 蓝图用法

由于 PoseSearch 插件的主要功能（创建和搜索索引）是通过 C++ API 进行的，且编辑器模块提供了复杂的交互界面，因此蓝图中直接暴露的节点主要集中在**编辑器工具**的控制和信息查看上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Database Editor` | 打开指定 `UPoseSearchDatabase` 资产的专用编辑器。 | `FDatabaseEditor` (编辑器工具) |
| `Preview Backward / Forward / Pause` | 控制数据库编辑器预览窗口中的动画播放（后退、前进、暂停）。 | `FDatabaseViewModel` |
| `Build Search Index` | 为指定的数据库构建或重建搜索索引（通常在编辑器或打包前执行）。 | `FDatabaseViewModel` |
| `Get Pose Search Database Statistics` | 获取数据库的统计信息（如动画序列数、总姿态数、内存占用等）。 | `UPoseSearchDatabaseStatistics` |

### 使用示例（蓝图描述）

1.  **编辑数据库资产**：
    - 在内容浏览器中，右键单击 `UPoseSearchDatabase` 资产。
    - 选择 “编辑” (Edit)，即可打开 PoseSearch Database 编辑器。在该编辑器中，你可以：
        - 添加/移除动画资产（序列、混合空间等）。
        - 调整采样率、范围等配置。
        - 在预览视口中实时查看动画播放，并使用工具栏按钮控制播放（前进、后退、暂停）。
        - 查看数据库的详细统计信息和内存占用。
        - 调试当前选择的动画姿态。

2.  **调试 Motion Matching 状态**：
    - 在游戏运行时（PIE），通过 “窗口” -> “开发者工具” -> “动画” -> “Rewind Debugger” 打开倒带调试器。
    - 选择你的角色骨骼网格体，在时间轴上添加 “Pose Search” 轨道。
    - 暂停游戏并拖动时间轴，你将看到一个详细面板，显示当前帧的 Motion Matching 状态，包括：
        - 当前选择的动画片段、姿态索引、匹配代价（Cost）。
        - 查询向量（用于搜索的特征）、轨迹信息。
        - 可以展开查看各个特征通道（如骨骼位置、速度）对最终匹配代价的贡献。
    - 点击某个匹配结果行，编辑器中对应的动画资产会自动打开并定位到该姿态的时间点。

## C++ 用法

PoseSearch 的核心功能通过 C++ 暴露，主要用于运行时动画逻辑。以下是从公开头文件推断的基本用法。

### 头文件引入

```cpp
#include "PoseSearch/PoseSearchDatabase.h"
#include "PoseSearch/PoseSearchSchema.h"
#include "PoseSearch/PoseSearchFeatureChannel.h"
#include "PoseSearch/PoseSearchResult.h"
```

### 基本用法（基于公开头文件推断）

核心流程分为 **离线索引构建** 和 **运行时查询搜索**。

```cpp
// 1. 离线阶段：在编辑器或打包工具中，为动画资产构建搜索索引
// （这通常由 UPoseSearchDatabase 资产的编辑器或工厂在内部完成）
UPoseSearchDatabase* MyDatabase = ...; // 你的动画数据库资产
MyDatabase->BuildSearchIndex();

// 2. 运行时阶段：构建查询并搜索
// 假设你已经有了一个 FPoseSearchPoseHistory 来记录当前角色姿态历史
FPoseSearchPoseHistory PoseHistory;
// ... 填充 PoseHistory ...

// 定义一个搜索查询，描述你要找什么（例如：当前速度、轨迹未来点等）
FPoseSearchQuery MyQuery;
// 根据你的 PoseSearch Schema 填充查询向量
// MyQuery.FeatureVector = ...;

// 在数据库中搜索最匹配的姿态
FPoseSearchResult SearchResult = MyDatabase->Search(MyQuery, PoseHistory);

// 3. 使用搜索结果
if (SearchResult.IsValid())
{
    // SearchResult 包含了匹配到的动画资产、时间点等信息
    UAnimationAsset* FoundAsset = SearchResult.GetAnimationAsset();
    float FoundTime = SearchResult.GetTime();
    bool bIsMirrored = SearchResult.IsMirrored();
    FVector BlendParameters = SearchResult.GetBlendParameters();

    // 应用到你的动画图节点或动画实例
    // MyAnimInstance->PlayAnimation(FoundAsset, FoundTime, ...);
}
```

### 进阶用法

进阶用法涉及自定义姿态特征通道 (`UPoseSearchFeatureChannel`)、定义搜索模式（如 PCABruteForce, PCAKDTree）、以及使用交互资产 (`UPoseSearchInteractionAsset`) 来处理多个角色之间的协调动画匹配。这些通常需要深入理解插件的内部架构和数据结构。

## Demo 示例

以下是一个最小的、概念性的 C++ 示例，展示如何在自定义动画节点中集成 PoseSearch 查询。

```cpp
// MyAnimNode_MotionMatching.h
#pragma once
#include "PoseSearch/PoseSearchDatabase.h"
#include "AnimNodes/AnimNode_BlendStack.h"
#include "MyAnimNode_MotionMatching.generated.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MotionMatching : public FAnimNode_BlendStack_Base
{
    GENERATED_BODY()

    // 数据库资产引用
    UPROPERTY(EditAnywhere, Category = "Motion Matching")
    TObjectPtr<UPoseSearchDatabase> Database;

    // 这是一个示例性运行时搜索逻辑
    virtual void OnUpdate(const FAnimationUpdateContext& Context) override
    {
        // 1. 构建查询（简化版，实际需根据 Schema 和当前状态计算特征向量）
        FPoseSearchQuery Query;
        // ... 填充 Query.FeatureVector ...

        // 2. 执行搜索（假设 Database 已索引）
        if (Database && Database->IsSearchIndexValid())
        {
            FPoseSearchResult Result = Database->Search(Query, PoseHistory);
            if (Result.IsValid())
            {
                // 3. 根据结果切换混合栈播放的动画
                // FAnimNode_BlendStack_Base::PlayAnimation(Result.GetAnimationAsset(), Result.GetTime(), ...);
            }
        }
    }

private:
    FPoseSearchPoseHistory PoseHistory;
};
```

## 模块依赖

从插件的性质（Animation）和常见模式推断，使用 PoseSearch 插件时，你的模块可能需要依赖以下内容（已在插件内部依赖）：
- `AnimationCore`
- `Engine`
- `AnimationBlueprintLibrary` (可能)

**无特殊依赖（仅标准 Core/Engine/Slate 等）**。插件主要通过 `UPoseSearchDatabase` 和 `UPoseSearchSchema` 等 UObject 资产与外部交互，核心依赖已由插件自身处理。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `314d38e0` | Fixed crash when loading trace file with missing assets in project (specifically a USkinnedAsset) | 修复加载跟踪文件时，因项目资产缺失（特别是 USkinnedAsset）导致的崩溃问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，代码产生的双精度常量截断为浮点数的警告。 |
| 2026-05-12 | `1222a3b1` | PoseSearch - fix for Motion Matching Database editor Preview viewport doesn't display static mesh at | PoseSearch - 修复运动匹配数据库编辑器预览视口无法显示静态网格体的问题。 |
| 2026-05-12 | `eddf36ad` | PoseSearch - fix velocity channel debug visualization | PoseSearch - 修复速度通道的调试可视化功能。 |
| 2026-05-12 | `b57412ab` | PoseSearch - Expose preview-mesh cap in Pose Search Database editor | PoseSearch - 在姿态搜索数据库编辑器中暴露预览网格体上限设置。 |

### 维护评价

- **创建时间**：插件于 2020 年 6 月创建，已有约 6 年历史。
- **近期更新频率**：最近有多次提交集中在 2026 年 5 月，内容均为 **Bug 修复和功能改进**（如修复崩溃、可视化问题、编辑器功能），表明插件仍在被积极维护和改进。
- **维护状态**：**活跃维护**。尽管是一个 “老” 插件，但近期提交活跃，解决了实际使用中遇到的问题。
- **已知问题/限制**：`.uplugin` 中的 `EnabledByDefault` 为 `false`，这意味着该插件**不会默认启用**，需要在项目设置中手动开启。同时，部分高级功能（如 Interaction Asset）被明确标记为实验性的。
- **推荐使用**：**推荐**。对于需要实现高质量 Motion Matching 的项目，PoseSearch 是 Epic Games 官方提供的强大且仍在维护的框架。虽然需要手动启用并投入时间学习其工作流，但它能带来显著的动画质量提升。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PoseSearch)
- [官方文档]() (无链接)
- [测试用例]() (未在提供的文件列表中发现独立测试文件，可能集成在其他测试套件中)