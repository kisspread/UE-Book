# Hair Card Generator

> Procedurally generate hair cards from hair strands

| 属性 | 值 |
|---|---|
| 中文名 | 毛发卡片生成器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器设置、蓝图资产） |
| 模块 | `HairCardGeneratorEditor` (Runtime), `HairCardGeneratorDataflow` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairCardGenerator) | |

## 用途

Hair Card Generator 是一个实验性插件，用于从 Groom 系统中的发丝（strands）数据程序化生成头发卡片（hair cards）。头发卡片是实时渲染中常用的低面数替代模型，用于表现毛发体积和纹理，同时保持高性能。该插件提供了完整的管线：从读取发丝数据、聚类分簇、曲线细分与插值、生成卡片几何体、布局纹理图集、到最终导入资产。它特别适合需要将高精度发丝 Groom 资产转换为适合游戏运行时渲染的 LOD 方案的场景。

## 使用场景

- **游戏毛发 LOD 生成**：在人物或生物的角色创建管线中，高级别的 Groom 使用发丝表现细节，低级别 LOD 使用头发卡片。本插件可自动从发丝数据生成卡片。
- **编辑器内快速试验**：通过蓝图或 Python 脚本调用生成管线，快速迭代头发卡片的外观和参数。
- **自定义毛发资产工具**：利用底层数学工具（曲线细分、样条插值）构建自定义的卡片生成逻辑。

## 蓝图用法

本插件的核心蓝图入口是 `UHairCardGenControllerBase` 蓝图类。它暴露了一系列 `BlueprintImplementableEvent`，您可以在蓝图子类中重写这些事件以实现自定义的生成行为。这些事件对应生成管线的不同步骤。

### 核心蓝图节点（事件）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadGroomData` | 从 `FHairCardGen_GroomData` 结构加载发丝数据到控制器 | `UHairCardGenControllerBase` |
| `LoadSettings` | 加载生成配置（`UHairCardGeneratorPluginSettings`） | `UHairCardGenControllerBase` |
| `GenerateCardsGeometry` | 根据当前状态生成卡片几何体（返回平面点数据） | `UHairCardGenControllerBase` |
| `GenerateClumps` | 将发丝分组为发簇（clumps），返回每个发丝所属的簇 ID | `UHairCardGenControllerBase` |
| `ClusterTextures` | 根据纹理相似度对发簇进行聚类 | `UHairCardGenControllerBase` |
| `GenerateTextureLayout` | 布局纹理图集，返回 UV 坐标 | `UHairCardGenControllerBase` |
| `GenerateTextureAtlases` | 执行实际纹理渲染生成图集 | `UHairCardGenControllerBase` |
| `SetOptimizations` | 设置性能优化标记（如去除飞毛） | `UHairCardGenControllerBase` |

### 蓝图数据结构

| 结构 | 关键字段 | 说明 |
|---|---|---|
| `FHairCardGen_StrandData` | `GroupID` | 单根发丝的数据，包含所属组 ID |
| `FHairCardGen_GroomData` | `BasisType`, `CurveType`, `Strands`, `VertexPositions`, `VertexWidths` | 完整 Groom 数据，去除引导发丝（guides）后的紧凑表示 |

### 使用示例（蓝图描述）

1. 创建一个继承自 `UHairCardGenControllerBase` 的蓝图类。
2. 在事件图表中重写 `LoadGroomData` 事件，从输入的 `FHairCardGen_GroomData` 中读取发丝顶点位置和宽度。
3. 调用 `GenerateClumps` 事件（默认实现为空，需在蓝图中自行编写逻辑）对发丝进行聚类，返回一个整数数组。
4. 调用 `GenerateCardsGeometry` 事件为每个簇生成卡片平面。
5. 后续依次调用纹理相关事件完成图集生成。
6. 最后通过静态工具函数 `FHairCardGeneratorUtils::RunCardsGeneration`（C++）或模块接口触发完整管线。

## C++ 用法

### 头文件引入

```cpp
#include "HairCardGeneratorEditorModule.h"
#include "HairCardGeneratorPluginSettings.h"
#include "HairCardGenControllerBase.h"
```

### 基本用法

使用 `FHairCardGeneratorUtils` 静态工具函数可以构建并运行卡片生成管线。以下示例演示从 `UGroomAsset` 和 `FHairGroupsCardsSourceDescription` 出发，生成 LOD 卡片。

```cpp
// 源文件：Engine/Plugins/Experimental/HairCardGenerator/Source/HairCardGeneratorEditor/Public/HairCardGeneratorEditorModule.h

void GenerateHairCardLOD(UGroomAsset* Groom, FHairGroupsCardsSourceDescription& CardsDesc)
{
    // 1. 构建高级选项
    FCardsGenerationAdvancedOptions AdvancedOptions;
    AdvancedOptions.bReduceCardsFromPreviousLOD = false;
    AdvancedOptions.bGenerateGeometryForAllGroups = true;
    AdvancedOptions.AtlasSize = 12;  // 2048x2048

    // 2. 生成并填充设置对象
    TObjectPtr<UHairCardGeneratorPluginSettings> Settings;
    uint8 GenFlags = 0;
    uint8 PipelineFlags = 0;
    bool bQuerySettings = false;  // 不弹出对话框，使用默认配置
    FHairCardGeneratorUtils::BuildGenerationSettings(
        bQuerySettings, Groom, CardsDesc,
        Settings, GenFlags, PipelineFlags, AdvancedOptions);

    // 3. 加载设置（内部处理缓存等）
    FHairCardGeneratorUtils::LoadGenerationSettings(Settings);

    // 4. 运行完整管线
    auto PipelineFunction = [&](const TObjectPtr<const UHairCardGeneratorPluginSettings>& Settings,
                                int32 FilterIndex, uint8 GenFlags) -> bool
    {
        TArray<int32> StrandsClumps;
        int32 NumClumps = 0;
        // 4a. 聚类
        if (!FHairCardGeneratorUtils::GenerateCardsClumps(Settings, FilterIndex, GenFlags, StrandsClumps, NumClumps))
            return false;

        TArray<TArray<FVector3f>> ClumpsGeometry;
        // 4b. 生成几何体
        if (!FHairCardGeneratorUtils::GenerateCardsGeometry(Settings, FilterIndex, GenFlags, ClumpsGeometry))
            return false;

        // 4c. 纹理聚类、布局和渲染等...
        // 此处省略详细步骤（需完整实现）
        return true;
    };
    FHairCardGeneratorUtils::RunCardsGeneration(Settings, PipelineFlags, PipelineFunction);

    // 5. 构建并保存卡片资产
    FHairCardGeneratorUtils::BuildCardsAssets(Groom, CardsDesc, Settings, GenFlags);
}
```

### 进阶用法

底层数学工具类可用于定制细分和插值逻辑。

```cpp
// 源文件：Engine/Plugins/Experimental/HairCardGenerator/Source/HairCardGeneratorEditor/Private/HairCardGenCardSubdivider.h

// 使用自适应曲线细分
FHairCardGenCardSubdivider Subdivider(1.0f, true, 10);  // 容差 1.0，自适应，最多细分 10 次
MatrixXf InputPoints = ...;  // 2xN 矩阵（每个点为 2D？实际为 3D，请查看源代码）
TArray<float> SubdPoints = Subdivider.GetSubdivisionPoints(InputPoints);

// 自然三次样条插值
TArray<float> Knots = {0.0f, 0.3f, 0.7f, 1.0f};
TArray<float> Values = {0.0f, 0.8f, 0.5f, 0.1f};
FHairCardGenNaturalCubicSplines Spline(Knots, Values);
float InterpolatedValue = Spline(0.5f);  // 在 t=0.5 处插值

// 发丝插值器（基于样条）
TArray<FVector> Positions = { ... };
TArray<float> Widths = { ... };
FHairCardGenStrandNSCInterpolator Interpolator(Positions, Widths);
auto Result = Interpolator.GetInterpolatedStrand(100);  // 插值到 100 个点
```

## Demo 示例

以下是一个最小 C++ 示例，展示如何通过模块接口直接触发卡片生成（假设已有 GroomAsset 和 CardsDesc）。

**MyHairCardGenerator.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "HairCardGeneratorEditorModule.h"

class FMyHairCardGenerator
{
public:
    static bool Generate(UGroomAsset* GroomAsset, FHairGroupsCardsSourceDescription& InOutCardsDesc);
};
```

**MyHairCardGenerator.cpp**

```cpp
#include "MyHairCardGenerator.h"
#include "HairCardGeneratorPluginSettings.h"

bool FMyHairCardGenerator::Generate(UGroomAsset* GroomAsset, FHairGroupsCardsSourceDescription& InOutCardsDesc)
{
    // 使用默认高级选项
    FCardsGenerationAdvancedOptions Options;
    Options.AtlasSize = 12;  // 2048x2048
    Options.bGenerateGeometryForAllGroups = true;

    TObjectPtr<UHairCardGeneratorPluginSettings> Settings = nullptr;
    uint8 GenFlags = 0;
    uint8 PipelineFlags = 0;

    // 构建设置对象
    FHairCardGeneratorUtils::BuildGenerationSettings(
        false, GroomAsset, InOutCardsDesc, Settings, GenFlags, PipelineFlags, Options);

    // 加载设置
    FHairCardGeneratorUtils::LoadGenerationSettings(Settings);

    // 运行完整管线（使用内置的 PipelineFunction 简化处理）
    auto PipeFunc = [](const TObjectPtr<const UHairCardGeneratorPluginSettings>& S,
                       int32 FilterIndex, uint8 GenFlags) -> bool
    {
        // 实际管线需要调用所有步骤，此处为简化示意
        // 真实情况下应调用 GenerateCardsClumps, GenerateCardsGeometry 等
        return true;
    };
    if (!FHairCardGeneratorUtils::RunCardsGeneration(Settings, PipelineFlags, PipeFunc))
    {
        return false;
    }

    // 构建并保存资产
    return FHairCardGeneratorUtils::BuildCardsAssets(GroomAsset, InOutCardsDesc, Settings, GenFlags);
}
```

## 模块依赖

本模块的 Build.cs 中列出了以下独特依赖（省略常见模块）：

| 模块 | 用途 |
|---|---|
| `HairCardGeneratorDataflow` | 数据流节点，提供底层曲线细分/插值算法 |
| `Groom` | Groom 资产数据访问（发丝属性、卡片描述） |
| `GeometryCore` | 几何处理基础库（用于点、向量运算） |
| `Eigen` | 第三方线性代数库（用于矩阵运算和曲线细分） |

> 注：Eigen 以第三方依赖形式引入，需确保项目已包含该库。

## 维护状态

### 近期更新

- 2025-11-18 `1e8eb566` Fix dataflow cards rendering crash when the generate LOD from previous is on
- 2025-10-03 `b863d7a9` Fix card texture rendering + add generation settings + automatic cardsgroups creation
- 2025-09-05 `e6415d8a` Dataflow : fix performance issue when calling SetShadowEnabled  on the dynamic mesh component
- 2025-09-04 `68e03af0` Geometry facade for grooms and cards + new rendering + use of curve selection
- 2025-09-04 `5cb8a8b9` [Backout] - CL45497446 - backout due to Main CIS issue

### 维护评价

- **创建时间**：2025-09-04，属于非常新的插件（不足半年）。
- **更新频率**：频繁，每月有数次功能性修复和更新，最近一次为 2025-11-18。
- **活跃度**：活跃开发中，修复关键渲染崩溃，增加自动创建卡片组等功能。
- **状态**：实验性插件（`.uplugin` 中 `IsExperimentalVersion=true`），但代码质量较高，功能完备。
- **推荐使用**：适用于希望利用程序化卡片管线的团队，但建议关注后续更新以获取稳定版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairCardGenerator)
- [官方文档](https://docs.unrealengine.com/)（当前无专属文档页面，可参考 Groom 系统文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairCardGenerator/Tests)（可能不存在，需本地检索）