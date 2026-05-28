# Hair Card Generator

> Procedurally generate hair cards from hair strands

| 属性 | 值 |
|---|---|
| 中文名 | 毛发卡生成器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `HairCardGeneratorDataflow` (Runtime), `HairCardGeneratorEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairCardGenerator) | |

## 用途

该插件用于从原始的毛发发丝（Hair Strands）数据中，程序化地生成用于实时渲染的**毛发卡（Hair Cards）** 网格和纹理。

**解决的问题**：在开发具有高精度毛发资产的角色时，直接渲染数以万计的毛发发丝计算量巨大。通常的做法是将这些发丝转换为少量带有透明纹理的网格片（即毛发卡），以实现高性能的视觉效果。手动创建这些卡片非常耗时且难以迭代。`HairCardGenerator` 自动化了这一复杂流程，通过一系列算法步骤（聚类、几何生成、纹理聚类、纹理布局、渲染）将原始毛发数据转换为优化后的静态网格和纹理资产。

**为什么存在**：作为引擎内置的工具链补充，它旨在为艺术家和开发者提供一个从高保真毛发数据到优化渲染资产的标准化、可重复的生成管线，尤其适用于需要为不同LOD级别生成毛发卡的情况。

## 使用场景

- 你在开发一个带有高精度毛发模型（`.groom` 文件）的角色，并需要为其不同LOD级别生成性能优化的毛发卡资产。
- 你希望在不手动建模的情况下，快速从原始毛发数据生成具有合理视觉效果的卡片网格和纹理图集。
- 你的美术流程需要程序化的资产生成工具，以确保不同角色或LOD之间毛发表现的一致性。

## 蓝图用法

该插件的核心逻辑由 Python 脚本驱动，通过 `UHairCardGenControllerBase` 类暴露接口。在蓝图中，你可以调用其`BlueprintCallable`辅助函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateCardsStaticMesh` | 从给定的顶点、面片、法线、UV和组数据，直接构建一个 `UStaticMesh` 资产。 | `UHairCardGenControllerBase` |

### 使用示例（蓝图描述）

虽然生成流程通常由编辑器扩展或 Python 脚本内部调用，但 `CreateCardsStaticMesh` 节点可用于在蓝图中直接从程序化数据创建网格。
1.  使用 `Make Array` 等节点准备顶点坐标、面索引、法线、UV等数据数组。
2.  连接到 `CreateCardsStaticMesh` 节点的相应输入引脚。
3.  指定一个已创建的 `Static Mesh` 对象作为输出目标。

## C++ 用法

插件提供了 `FHairCardGeneratorUtils` 静态工具类，用于在C++中执行生成流程的各个阶段。

### 头文件引入

```cpp
#include “HairCardGeneratorEditorModule.h”
```

### 基本用法

从 `FHairCardGeneratorUtils` 的静态方法中，可以了解生成流程的主要步骤。
*来源：Public/HairCardGeneratorEditorModule.h*

```cpp
// 1. 为指定的毛发资产和卡片描述构建生成设置
TObjectPtr<UHairCardGeneratorPluginSettings> Settings;
uint8 GenFlags, PipelineFlags;
FCardsGenerationAdvancedOptions AdvOptions;
FHairCardGeneratorUtils::BuildGenerationSettings(true, MyGroomAsset, CardsDesc, Settings, GenFlags, PipelineFlags, AdvOptions);

// 2. 生成毛发聚类数据
FHairCardClumpData ClumpData;
FHairCardGeneratorUtils::GenerateCardsClumps(Settings, 0 /*FilterIndex*/, GenFlags, ClumpData);

// 3. 生成卡片几何数据
FHairCardGeomData GeomData;
FHairCardMeshData MeshData;
int32 CardCount;
FHairCardGeneratorUtils::GenerateCardsGeometry(Settings, 0, GenFlags, GeomData, MeshData, CardCount);

// 4. 生成纹理聚类数据
FHairCardTextureClusterData ClusterData;
FHairCardGeneratorUtils::GenerateCardsTexturesClusters(Settings, 0, GenFlags, ClusterData);

// 5. 生成纹理布局和图集
FHairCardAtlasLayoutData LayoutData;
FHairCardAtlasUVData AtlasUVData;
FHairCardGeneratorUtils::GenerateTexturesLayoutAndAtlases(Settings, GenFlags, LayoutData, AtlasUVData);
```

### 进阶用法

可以通过 `UHairCardGeneratorPluginSettings` 对象精细控制生成参数。
*来源：Private/HairCardGeneratorPluginSettings.h*

```cpp
// 获取或创建一个设置对象
UHairCardGeneratorPluginSettings* Settings = NewObject<UHairCardGeneratorPluginSettings>();

// 关联到一个Groom资产和LOD索引
Settings->SetSource(MyGroomAsset, 0 /*LODIndex*/);

// 修改设置
Settings->DestinationPath.Path = “/Game/HairAssets/”;
Settings->BaseFilename = “HeroHair_LOD0”;
Settings->AtlasSize = EHairCardAtlasSize::AtlasSize4096;

// 获取组级设置并进行更细致的控制
TArray<TObjectPtr<UHairCardGeneratorGroupSettings>>& GroupSettings = Settings->GetFilterGroupSettings();
if (GroupSettings.Num() > 0)
{
    GroupSettings[0]->TargetNumberOfCards = 3000;
    GroupSettings[0]->NumberOfTexturesInAtlas = 50;
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在插件模块中触发一次基础的卡片生成流程。
*注意：实际应用中通常需要完整的Groom资产和设置对象。*

```cpp
// MyHairCardGeneratorExample.h
#pragma once
#include “CoreMinimal.h”

class UGroomAsset;
class UHairCardGeneratorPluginSettings;

class FMyHairCardGeneratorExample
{
public:
    static void GenerateHairCardsForGroom(UGroomAsset* GroomAsset);
};
```

```cpp
// MyHairCardGeneratorExample.cpp
#include “MyHairCardGeneratorExample.h”
#include “HairCardGeneratorEditorModule.h”
#include “HairCardGeneratorPluginSettings.h” // 用于 UHairCardGeneratorPluginSettings
#include “GroomAsset.h” // 用于 UGroomAsset

void FMyHairCardGeneratorExample::GenerateHairCardsForGroom(UGroomAsset* GroomAsset)
{
    if (!GroomAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT(“GroomAsset is null.”));
        return;
    }

    // 获取模块接口
    IHairCardGeneratorEditor& HairCardGenModule = IHairCardGeneratorEditor::Get();

    // 准备一个最简单的卡片源描述（实际需要根据Groom资产配置）
    FHairGroupsCardsSourceDescription CardsDesc;
    // ... 配置 CardsDesc ...

    // 调用模块的核心生成函数（内部会创建设置并执行完整流程）
    bool bSuccess = HairCardGenModule.GenerateHairCardsForLOD(GroomAsset, CardsDesc);

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT(“Hair cards generated successfully for %s.”), *GroomAsset->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT(“Failed to generate hair cards for %s.”), *GroomAsset->GetName());
    }
}
```

## 模块依赖

要使用该插件，你的模块需要链接 `HairCardGeneratorEditor` 模块。该插件本身还隐含依赖于 `HairStrandsCore`（Groom资产）和 `GeometryCore`（几何处理）等模块。

| 模块 | 用途 |
|---|---|
| `HairCardGeneratorEditor` | 包含生成逻辑、设置和工具类的主要编辑器运行时模块 |
| `HairStrandsCore` | 处理 `UGroomAsset` 及其底层毛发数据的核心模块 |
| `GeometryCore` | 提供几何处理、网格构建等基础功能 |
| `Dataflow` | 插件的 `HairCardGeneratorDataflow` 模块用于节点图（数据流）集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量到单精度的截断警告。 |
| 2026-04-17 | `49f946b4` | [Dataflow] | （提交信息不完整）推测为数据流相关更新。 |
| 2026-04-14 | `f25ba75e` | Improve cards template + fix terminal rendering | 改进卡片模板并修复终端渲染问题。 |
| 2026-04-14 | `daed62e3` | HairCardGenerator: Update to push load/save functionality to separate ufunctions, support direct wir... | 更新加载/保存逻辑到独立函数，支持直接写入...（信息截断）。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到UE_LOGF。 |

### 维护评价

`HairCardGenerator` 是一个相对较新（2024年创建）且处于 **实验性** 状态的插件。从提交历史看，直至2026年5月仍有活跃的代码更新，主要集中在功能改进（如数据流、模板）、代码质量提升（修复警告、迁移日志宏）和bug修复。这表明该插件仍在积极开发和完善中。

**结论**：
- **状态**：实验性，仍在积极维护和迭代。
- **建议**：可以关注并试用，适用于项目中需要程序化生成毛发卡的工作流。但由于是实验性功能，其API和生成结果可能在未来版本中发生变化，不建议用于需要高度稳定性的生产环境最终管线。
- **风险**：作为实验性插件，启用时需注意其默认是关闭的，并且可能依赖特定的Groom资产格式或数据流上下文。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairCardGenerator)
- [官方文档]()（暂无）
- [测试用例]()（未在提供的源码文件中找到明确的测试文件路径）