# Hair Card Generator

> Procedurally generate hair cards from hair strands

| 属性 | 值 |
|---|---|
| 中文名 | 毛发卡片生成器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流节点） |
| 模块 | `HairCardGeneratorDataflow` (Runtime), `HairCardGeneratorEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairCardGenerator) | |

## 用途

HairCardGenerator 是一个基于 **Dataflow（数据流）** 框架的程序化工具，用于将基于发丝（strand）的 Groom 资产转换为可用于实时渲染的 **Hair Cards（毛发卡片）**。

毛发渲染是实时图形中的性能瓶颈之一。直接渲染数万根发丝（strands）开销极大，而 Hair Cards 是一种经典的优化手段：将成簇的发丝烘焙为带透明纹理的几何卡片，在大幅降低渲染开销的同时保持视觉效果。该插件将整个转换流程拆分为 Dataflow 节点，形成完整的程序化管线：

1. **配置构建**（BuildCardsSettings）：从 Groom 资产读取数据，生成各 LOD/分组的卡片设置
2. **属性提取/回写**（Extract/ReportCardsAttributes）：在 Groom 资产与数据集合之间传递卡片属性
3. **发丝分簇**（GenerateCardsClumps）：将数千根发丝聚合为少量簇（clumps），每簇生成一张卡片
4. **几何生成**（GenerateCardsGeometry）：为每簇生成四边形卡片网格
5. **纹理渲染**（GenerateCardsTextures）：渲染覆盖纹理（coverage texture）用于最终着色
6. **终端输出**（CardsAssetTerminal）：将结果写回资产

该插件目前处于实验阶段，源自 Epic 内部工具（从 Restricted 文件夹迁移而来），主要服务于 Groom/Chaos 毛发系统的工作流。

## 使用场景

- 你正在使用 UE5 的 **Groom/Chaos 毛发系统**，需要将高密度 strand groom 转换为适用于移动端或低配平台的 hair cards
- 你需要为不同 LOD 级别自动生成不同密度的 hair cards（通过 LODIndex/FilterSettings 配置）
- 你想在 **Dataflow 图编辑器**中可视化和调试毛发卡片的生成流程，逐步调整分簇数量、三角形数、纹理尺寸等参数
- 你的美术管线需要程序化地批量处理多个 Groom 资产的卡片生成

## 蓝图用法

该插件**不提供传统蓝图节点**。所有功能均通过 **Dataflow 节点**暴露，需在 Dataflow 图编辑器中使用。Dataflow 节点的元数据标记为 `meta = (Experimental, DataflowGroom)`。

### 核心节点

| 节点 | 说明 | 所在结构体 |
|---|---|---|
| `BuildCardsSettings` | 从 Groom 资产构建卡片生成配置（LOD、分组、高级选项） | `FBuildCardsSettingsNode` |
| `ExtractCardsAttributes` | 从 Groom 资产提取卡片属性到数据集合 | `FExtractCardsAttributesNode` |
| `ReportCardsAttributes` | 将数据集合中的卡片属性写回 Groom 资产 | `FReportCardsAttributesNode` |
| `GenerateCardsClumps` | 将发丝聚合为簇（clumps），决定卡片数量和飞散发丝数量 | `FGenerateCardsClumpsNode` |
| `GenerateCardsGeometry` | 为每个簇生成卡片几何体（顶点、三角形、UV） | `FGenerateCardsGeometryNode` |
| `GenerateCardsTextures` | 渲染卡片覆盖纹理和纹理图集 | `FGenerateCardsTexturesNode` |
| `CardsAssetTerminal` | 终端节点，将生成结果输出为资产 | `FCardsAssetTerminalNode` |

### 使用示例（Dataflow 图描述）

典型的 Dataflow 图连线顺序：

```
GroomAsset（输入）
    │
    ▼
BuildCardsSettings ──→ CardsSettings
    │                      │
    ▼                      ▼
GenerateCardsClumps ──→ GenerateCardsGeometry ──→ GenerateCardsTextures ──→ CardsAssetTerminal
    │                       │                         │
    ▼                       ▼                         ▼
Collection (Clumps)     Collection (Geometry)     Collection (Texture)    → 输出资产
```

1. 从 Groom 输入节点拖出 `GroomAsset` 引脚连接到 `BuildCardsSettings`
2. 配置 `GenerationSettings`（LOD 索引、分组、过滤器列表、高级选项）
3. `CardsSettings` 输出传递给后续三个生成节点
4. `Collection` 通过 DataflowPassthrough 在各节点间传递（逐步累积数据）
5. 最终连接到 `CardsAssetTerminal` 生成可用资产

### 关键配置结构体

#### FGroomFilterSettings（过滤器设置）

| 属性 | 说明 | 默认值 |
|---|---|---|
| `FilterName` | 过滤器组名称 | — |
| `NumClumps` | 卡片簇总数 | `NumClumps` |
| `NumFlyaways` | 飞散发丝卡片数上限 | `NumFlyaways` |
| `NumTriangles` | 三角形总数上限 | `NumTriangles` |
| `NumTextures` | 纹理数量 | `NumTextures` |
| `CardGroups` | 属于该过滤器的卡片组名列表 | — |
| `AdvancedOptions` | 高级选项（多卡片簇、自适应细分等） | — |

#### FGroomAdvancedGenerationSettings（高级生成设置）

| 属性 | 说明 | 默认值 |
|---|---|---|
| `bReduceCardsFromPreviousLOD` | 基于上一级 LOD 的卡片减少三角形数 | `false` |
| `bGenerateGeometryForAllGroups` | 在 group 0 上为所有 groom 组生成几何体 | `true` |
| `RandomSeed` | 随机种子（可复现结果） | `0` |
| `AtlasSize` | 纹理图集尺寸 | `AtlasSize4096` |
| `ReserveTextureSpaceLOD` | 为更高 LOD 预留的纹理空间百分比 | `0` |
| `bUseGroomAssetStrandWidth` | 使用 Groom 资产中的发丝宽度 | `true` |

## C++ 用法

该插件的核心功能通过 Dataflow 节点暴露，C++ 用法主要围绕创建和连接这些节点。

### 头文件引入

```cpp
// Dataflow 节点定义
#include "BuildCardsSettingsNode.h"
#include "GenerateCardsClumpsNode.h"
#include "GenerateCardsGeometryNode.h"
#include "GenerateCardsTexturesNode.h"
#include "CardsAssetTerminalNode.h"
#include "ModifyCardsAttributesNode.h"
```

### 基本用法

以编程方式构建卡片设置（参考 `FBuildCardsSettingsNode` 的属性）：

```cpp
// 来源: Public/BuildCardsSettingsNode.h

// 构建一个过滤器设置
FGroomFilterSettings FilterSettings;
FilterSettings.FilterName = FName("DefaultFilter");
FilterSettings.NumClumps = 1000;
FilterSettings.NumFlyaways = 50;
FilterSettings.NumTriangles = 50000;
FilterSettings.NumTextures = 4;

// 构建生成设置
FGroomGenerationSettings GenSettings;
GenSettings.LODIndex = 0;
GenSettings.GroupIndex = 0;
GenSettings.FilterSettings.Add(FilterSettings);
GenSettings.AdvancedOptions.RandomSeed = 42;
GenSettings.AdvancedOptions.AtlasSize = EHairCardAtlasSize::AtlasSize4096;

// 构建卡片设置
FGroomCardsSettings CardsSettings;
CardsSettings.GenerationSettings = YourPluginSettings;  // UHairCardGeneratorPluginSettings*
CardsSettings.GroomAsset = YourGroomAsset;              // UGroomAsset*
CardsSettings.GenerationFlags = 0;
CardsSettings.PipelineFlags = 0;
```

### 进阶用法

Dataflow 节点通过 `FManagedArrayCollection` 在管线中传递数据，每个节点向集合写入特定属性：

```cpp
// 来源: Public/GenerateCardsClumpsNode.h
// GenerateCardsClumps 节点写入的属性:
//   - CurveClumpIndicesAttribute: 每根发丝所属的簇索引
//   - ObjectNumClumpsAttribute:   每个对象的簇数量
//   - CurveFilterIndicesAttribute: 每根发丝所属的过滤器索引

// 来源: Public/GenerateCardsGeometryNode.h
// GenerateCardsGeometry 节点写入的属性:
//   - VertexClumpPositionsAttribute: 顶点位置
//   - FaceVertexIndicesAttribute:    面-顶点索引
//   - VertexCardIndicesAttribute:    顶点所属卡片索引
// 分组:
//   - CardsVerticesGroup: 卡片顶点数据
//   - CardsFacesGroup:    卡片面数据

// 来源: Public/GenerateCardsTexturesNode.h
// GenerateCardsTextures 节点写入的属性:
//   - ObjectTextureIndicesAttribute: 对象纹理索引
//   - VertexTextureUVsAttribute:     顶点纹理UV坐标
// 分组:
//   - CardsObjectsGroup: 卡片对象数据
```

分簇节点的覆盖设置（`FCardsClumpsSettings`）可按过滤器名称单独控制：

```cpp
// 来源: Public/GenerateCardsClumpsNode.h
FCardsClumpsSettings Override;
Override.FilterName = FName("HighDetail");
Override.NumCards = 2000;
Override.NumFlyaways = 100;
// 在 Dataflow 节点的 ClumpsSettings 数组中添加此项即可覆盖
```

## Demo 示例

该插件没有传统意义上的独立可运行 Demo，因为它完全基于 Dataflow 图编辑器工作流。以下展示如何在 C++ 中创建并配置一个 Dataflow 节点：

```cpp
// HairCardGeneratorDemo.h
#pragma once

#include "CoreMinimal.h"
#include "BuildCardsSettingsNode.h"
#include "GenerateCardsClumpsNode.h"

class FHairCardGeneratorDemo
{
public:
    /** 构建完整的 Hair Card 生成设置 */
    static FGroomCardsSettings BuildSettings(
        UHairCardGeneratorPluginSettings* InPluginSettings,
        UGroomAsset* InGroomAsset,
        int32 InLODIndex = 0)
    {
        // 创建过滤器
        FGroomFilterSettings Filter;
        Filter.FilterName = FName("Main");
        Filter.NumClumps = 500;
        Filter.NumFlyaways = 30;
        Filter.NumTriangles = 20000;
        Filter.NumTextures = 2;

        // 创建生成设置
        FGroomGenerationSettings GenSetting;
        GenSetting.LODIndex = InLODIndex;
        GenSetting.GroupIndex = 0;
        GenSetting.FilterSettings.Add(Filter);
        GenSetting.AdvancedOptions.bGenerateGeometryForAllGroups = true;
        GenSetting.AdvancedOptions.RandomSeed = 12345;
        GenSetting.AdvancedOptions.AtlasSize = EHairCardAtlasSize::AtlasSize2048;

        // 创建最终卡片设置
        FGroomCardsSettings Result;
        Result.GenerationSettings = InPluginSettings;
        Result.GroomAsset = InGroomAsset;
        Result.GenerationFlags = 0;
        Result.PipelineFlags = 0;

        return Result;
    }
};
```

```cpp
// HairCardGeneratorDemo.cpp
#include "HairCardGeneratorDemo.h"
```

## 模块依赖

从源码结构推断，该插件依赖以下非标准模块（Dataflow 和 Groom 相关）：

| 模块 | 用途 |
|---|---|
| `Dataflow` | Dataflow 框架（FDataflowNode、FManagedArrayCollection 等） |
| `Groom` | Groom 资产类型（UGroomAsset） |
| `HairCardGenerator` | 基础插件设置（UHairCardGeneratorPluginSettings） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double 到 float 截断警告 |
| 2026-04-17 | `49f946b4` | [Dataflow] | Dataflow 框架相关更新 |
| 2026-04-14 | `f25ba75e` | Improve cards template + fix terminal rendering | 改进卡片模板并修复终端渲染问题 |
| 2026-04-14 | `daed62e3` | HairCardGenerator: Update to push load/save functionality to separate ufunctions, support direct wir | 将加载/保存功能拆分为独立 UFunction，支持直接连线 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 到新 UE_LOGF 宏 |

### 维护评价

该插件**仍处于活跃维护中**。最近的更新集中在 2026 年 4-5 月，内容包括：
- 功能改进（卡片模板优化、直接连线支持）
- 渲染修复（终端渲染、图集布局）
- 代码质量改进（浮点精度警告、日志宏迁移）

**需要注意的限制**：
- ⚠️ **实验性插件**（`IsExperimentalVersion: true`），API 可能在未来版本中发生破坏性变更
- ⚠️ **默认未启用**（`EnabledByDefault: false`），需在项目设置中手动启用
- 依赖 Chaos Groom 系统，不适用于旧版 Hair 系统
- 功能完全通过 Dataflow 图暴露，无传统蓝图或编辑器菜单集成

**推荐程度**：如果你正在使用 UE5 的 Groom 系统并需要生成 hair cards，这是目前唯一的官方实验性工具。鉴于仍在活跃维护，可以谨慎使用，但需做好 API 变更的心理准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairCardGenerator)
- 官方文档（暂无）