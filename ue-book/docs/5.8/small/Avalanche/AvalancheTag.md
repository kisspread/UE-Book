# Avalanche

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（Motion Design）是 UE5 虚拟制片工具链中的核心合成、设计和广播工具。它提供了一套完整的运动图形（Motion Graphics）工作流程，集成了场景管理、形状创建、文本排版、材质设计、遮罩系统、动画控制、媒体合成、远程控制等功能，面向虚拟制片和实时广播场景。AvalancheTag 模块为整个插件提供了一套基于 GUID 的标签（Tag）系统，用于在 Motion Design 的各个子系统中标识、分类和引用资产与对象。

## 使用场景

- 你需要为虚拟制片场景中的元素打标签并按标签分类管理 → 使用 AvalancheTag
- 你需要在蓝图中通过标签引用一组对象，且标签集合可能动态变化 → 使用 Tag Alias 机制
- 你需要软引用标签（不立即加载源资产）用于跨关卡或资产引用 → 使用 FAvaTagSoftHandle
- 你正在构建 Motion Design 工作流，需要统一的对象标识系统 → 集成 AvalancheTag

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResolveTagHandle` | 将单个 Tag Handle 解析为 Tag 数组（支持 Alias 展开） | `UAvaTagLibrary` |
| `ResolveTagHandles` | 将 Tag Handle 容器解析为 Tag 数组 | `UAvaTagLibrary` |
| `ResolveTagSoftHandle` | 将软引用 Tag Handle 解析为硬引用 Tag Handle | `UAvaTagLibrary` |

以上节点均为 `BlueprintPure`，并标记为 `BlueprintAutocast`，支持自动类型转换（CompactNodeTitle = "->"）。

### 使用示例（蓝图描述）

1. **解析单个标签**：获取一个 `FAvaTagHandle` 变量，拖拽连接到 `ResolveTagHandle` 节点，输出的 `TArray<FAvaTag>` 即为解析后的标签数组（若为 Alias 则返回多个标签）。
2. **解析标签容器**：将 `FAvaTagHandleContainer` 变量连接到 `ResolveTagHandles`，输出解析后的所有标签。
3. **软引用转硬引用**：将 `FAvaTagSoftHandle` 连接到 `ResolveTagSoftHandle`，获得可直接使用的 `FAvaTagHandle`（注意会触发资产加载）。

## C++ 用法

### 头文件引入

```cpp
#include "AvaTagLibrary.h"
#include "AvaTagHandle.h"
#include "AvaTagHandleContainer.h"
#include "AvaTagSoftHandle.h"
#include "AvaTagSoftHandleContainer.h"
#include "AvaTagCollection.h"
```

### 基本用法

```cpp
// 创建一个 Tag Collection 资产引用
const UAvaTagCollection* TagCollection = /* 从资产加载或编辑器中获取 */;

// 创建 Tag Handle 指向某个 Tag
FAvaTagId TagId; // 从 TagCollection 获取
FAvaTagHandle TagHandle(TagCollection, TagId);

// 检查 Handle 是否有效
if (TagHandle.IsValid())
{
    // 获取解析后的 Tag 列表（若为 Alias 则返回多个）
    FAvaTagList Tags = TagHandle.GetTags();
    for (const FAvaTag* Tag : Tags)
    {
        UE_LOG(LogTemp, Log, TEXT("Tag: %s"), *Tag->ToString());
    }
}
```

### 进阶用法

```cpp
// 使用 Tag Handle Container 管理多个标签
FAvaTagHandleContainer HandleContainer;
HandleContainer.AddTagHandle(FAvaTagHandle(Collection1, TagId1));
HandleContainer.AddTagHandle(FAvaTagHandle(Collection2, TagId2));

// 检查容器是否包含某个标签
if (HandleContainer.ContainsTag(SomeTagHandle))
{
    // 处理逻辑
}

// 解析容器中所有标签
TArray<FAvaTag> AllTags = HandleContainer.ResolveTags();

// 使用软引用（适用于跨资产引用场景）
FAvaTagSoftHandle SoftHandle(TSoftObjectPtr<UAvaTagCollection>(CollectionPath), TagId);

// 软引用转硬引用（会加载资产）
FAvaTagHandle HardHandle = SoftHandle.MakeTagHandle();

// 使用 Soft Handle Container
FAvaTagSoftHandleContainer SoftContainer(HardHandle);
SoftContainer.AddTagHandle(AnotherHardHandle);

// 检查软引用容器是否包含某个标签（比较 Tag 值而非 ID）
bool bContains = SoftContainer.ContainsTag(SomeHandle);

// 使用 Tag Alias
// 在 UAvaTagCollection 中定义 Alias，一个 Alias 可以映射到多个 TagId
// 通过 Alias TagId 解析时会返回 Alias 下所有标签
```

## Demo 示例

```cpp
// AvaTagDemo.h
#pragma once

#include "CoreMinimal.h"
#include "AvaTagHandle.h"
#include "AvaTagHandleContainer.h"
#include "AvaTagCollection.h"

class FAvaTagDemo
{
public:
    /** 演示基本的标签系统用法 */
    static void DemoBasicUsage(const UAvaTagCollection* InTagCollection)
    {
        if (!InTagCollection)
        {
            return;
        }

        // 获取所有 Tag IDs（不含别名）
        TArray<FAvaTagId> TagIds = InTagCollection->GetTagIds(false);

        for (const FAvaTagId& TagId : TagIds)
        {
            // 获取 Tag 名称
            FName TagName = InTagCollection->GetTagName(TagId);

            // 创建 Handle
            FAvaTagHandle Handle(InTagCollection, TagId);

            // 检查有效性并获取标签
            if (Handle.IsValid())
            {
                FAvaTagList Tags = Handle.GetTags();
                UE_LOG(LogTemp, Log, TEXT("Tag '%s' resolved to %d tags"), 
                    *TagName.ToString(), Tags.Tags.Num());
            }
        }
    }

    /** 演示标签容器的使用 */
    static void DemoContainerUsage(const UAvaTagCollection* InTagCollection, 
                                    const TArray<FAvaTagId>& InTagIds)
    {
        FAvaTagHandleContainer Container;

        // 批量添加标签
        for (const FAvaTagId& TagId : InTagIds)
        {
            Container.AddTagHandle(FAvaTagHandle(InTagCollection, TagId));
        }

        // 检查某个标签是否存在
        if (InTagIds.Num() > 0)
        {
            FAvaTagHandle TestHandle(InTagCollection, InTagIds[0]);
            
            // 按 Tag 值匹配
            bool bContainsTag = Container.ContainsTag(TestHandle);
            
            // 按精确 Handle 匹配（同一 Source + TagId）
            bool bContainsExact = Container.ContainsTagHandle(TestHandle);
        }

        // 解析所有标签
        TArray<FAvaTag> ResolvedTags = Container.ResolveTags();
    }

    /** 演示 Tag 比较 */
    static void DemoTagComparison(const UAvaTagCollection* InCollection, 
                                   const FAvaTagId& InId1, 
                                   const FAvaTagId& InId2)
    {
        FAvaTagHandle Handle1(InCollection, InId1);
        FAvaTagHandle Handle2(InCollection, InId2);

        // 检查两个 Handle 是否指向相同的标签值（允许不同 Source）
        bool bOverlaps = Handle1.Overlaps(Handle2);

        // 检查两个 Handle 是否完全相同（同一 Source + TagId）
        bool bExactMatch = Handle1.MatchesExact(Handle2);
    }
};
```

## 模块依赖

AvalancheTag 为独立的标签系统模块，无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲视图标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用节目单页面设置时增加 MRQ 分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 节目控制工具栏新增页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置可强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制 |

### 维护评价

Avalanche（Motion Design）是 2025 年 5 月从 Experimental 迁移至 VirtualProduction 的大型插件，拥有约 2060 个源文件和 43 个模块。从近期 git 历史来看，插件处于**活跃维护**状态，每周都有功能性更新，包括 UI 改进、分析功能和新选项。作为 Epic Games 官方维护的虚拟制片核心工具，长期支持有保障。AvalancheTag 作为其标签子系统，为整个插件提供统一的标识能力，架构设计合理（支持 Alias、软引用、容器化管理）。

**推荐使用**：如果你的项目涉及虚拟制片或运动图形工作流，此插件及其标签系统是可靠的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [源码 - AvalancheTag 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheTag)