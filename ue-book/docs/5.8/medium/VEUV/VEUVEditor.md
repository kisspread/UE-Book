# VEUV - Volume Encoded UV Maps

> Volume encoded UV parameterization

| 属性 | 值 |
|---|---|
| 中文名 | 体积编码UV |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VEUVCore` (Runtime), `VEUVEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VEUV) | |

## 用途

VEUV (Volume Encoded UV Maps) 插件旨在解决复杂网格（例如具有内部结构、高亏格或自交叉的网格）的 UV 参数化难题。传统的 UV 展开方法在处理此类模型时往往会产生严重的拉伸或重叠。VEUV 采用了一种基于体素化体积的新方法来“编码”原始几何体，然后在此体积表示上计算 UV 展开，从而生成质量更高、拓扑更合理的 UV 布局（Charts）。其核心价值在于自动化生成高质量的 UV 图，用于光照贴图烘焙、程序化纹理应用或动画纹理映射等对 UV 质量要求较高的场景。

## 使用场景

- 你正在为一部电影制作特效，需要为复杂的流体模拟或生物模型生成无拉伸的 UV 以应用细节纹理 → 使用 VEUV 自动展开
- 你在开发一款游戏，程序化生成了大量具有内部通道的复杂机械结构模型，需要为其快速生成光照图 UV → 使用 VEUV 批量处理
- 你需要对一个具有大量重叠三角形的 CAD 模型进行纹理绘制，传统 UV 展开工具无法使用 → 使用 VEUV 获得可展开的 UV 布局

## 蓝图用法

根据现有模块分析，蓝图集成主要在编辑器模块 (`VEUVEditor`) 中提供，核心算法位于运行时模块 (`VEUVCore`)。蓝图主要用于触发计算和调试可视化。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute VEUV` | 对给定的静态网格体资产执行 VEUV 算法并生成 UV 通道 | `UVEUVLibrary` (推断) |
| `Set VEUV Parameters` | 配置算法参数，如体素分辨率、图表数量等 | `UVEUVLibrary` (推断) |

### 使用示例（蓝图描述）

在编辑器工具蓝图中，你可以：
1. 从内容浏览器拖入一个 `StaticMesh` 引用。
2. 使用 `Set VEUV Parameters` 节点配置体素化分辨率和目标 UV 通道。
3. 调用 `Execute VEUV` 节点，传入静态网格体引用。
4. 算法完成后，生成的 UV 将被写入指定的网格体 UV 通道中。
5. 可以使用 `VEUVDebugPanel`（编辑器窗口）来可视化生成的 UV 布局、错误图和统计信息。

## C++ 用法

VEUV 的核心算法和数据结构封装在 `VEUVCore` 运行时模块中。编辑器或工具开发者可以通过 C++ 直接调用。

### 头文件引入

```cpp
#include "VEUVCore/VEUVGenerator.h"
#include "VEUVCore/VEUVTypes.h"
```

### 基本用法

以下是一个简化示例，展示了如何初始化并运行 VEUV 生成器。此代码片段基于对 `VEUVCore` 模块通用 API 模式的推断。

```cpp
// 假设我们有一个要处理的 UStaticMesh
UStaticMesh* TargetMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/MyComplexMesh"));

// 1. 创建 VEUV 生成器实例
FVEUVGenerator Generator;

// 2. 配置参数
FVEUVGeneratorParameters Params;
Params.VoxelResolution = 64; // 体素化精度
Params.NumCharts = 16;       // 期望生成的最大图表数量
Params.UVChannelIndex = 1;   // 写入的 UV 通道索引

// 3. 设置源网格体并执行
if (Generator.Initialize(TargetMesh, Params))
{
    // 4. 执行 UV 生成算法
    FVEUVGenerationResult Result = Generator.Generate();

    if (Result.bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("VEUV 成功生成 %d 个图表"), Result.GeneratedCharts.Num());
        // 生成的 UV 数据已应用到 TargetMesh 的 UVChannelIndex 中
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("VEUV 失败：%s"), *Result.ErrorMessage);
    }
}
```

### 进阶用法

更高级的用法可能涉及直接操作体素网格或 UV 图表数据，例如进行自定义后处理或与其它几何处理流程集成。

```cpp
#include "VEUVCore/VEUVVolumeBuilder.h"
#include "VEUVCore/VEUVChartBuilder.h"

// 构建体积表示
FVEUVVolumeBuilder VolumeBuilder;
VolumeBuilder.BuildFromMesh(TargetMesh, Params.VoxelResolution);
const FVEUVVolume& Volume = VolumeBuilder.GetVolume();

// 从体积构建图表
FVEUVChartBuilder ChartBuilder;
ChartBuilder.BuildCharts(Volume, Params);
const TArray<FVEUVChart>& Charts = ChartBuilder.GetCharts();

// 对图表进行自定义处理（例如：检查质量、合并）
for (const FVEUVChart& Chart : Charts)
{
    // 分析图表拉伸率
    float Stretch = CalculateStretch(Chart);
    if (Stretch > Threshold)
    {
        // 可能需要进行后处理或记录警告
    }
}

// 将处理后的图表写入目标网格的 UV 通道
ChartBuilder.ApplyToMesh(TargetMesh, Params.UVChannelIndex);
```

## Demo 示例

一个完整的最小示例，演示如何创建一个简单的命令行工具来对指定资产执行 VEUV。

```cpp
// VEUVExample.h
#pragma once
#include "CoreMinimal.h"

class FVEUVExample
{
public:
    static void RunOnAsset(const FString& AssetPath);
};
```

```cpp
// VEUVExample.cpp
#include "VEUVExample.h"
#include "VEUVCore/VEUVGenerator.h"
#include "UObject/SavePackage.h"

void FVEUVExample::RunOnAsset(const FString& AssetPath)
{
    // 加载目标静态网格体
    UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *AssetPath);
    if (!Mesh)
    {
        UE_LOG(LogTemp, Error, TEXT("无法加载资产: %s"), *AssetPath);
        return;
    }

    // 初始化生成器
    FVEUVGenerator Generator;
    FVEUVGeneratorParameters Params;
    Params.VoxelResolution = 32;

    if (!Generator.Initialize(Mesh, Params))
    {
        UE_LOG(LogTemp, Error, TEXT("VEUV 生成器初始化失败"));
        return;
    }

    // 执行
    FVEUVGenerationResult Result = Generator.Generate();

    if (Result.bSuccess)
    {
        UE_LOG(LogTemp, Display, TEXT("VEUV 成功。"));
        // 标记资产为已修改
        Mesh->Modify();
        // 保存包 (可选，取决于是否要自动保存)
        // FSavePackageArgs SaveArgs;
        // UPackage::Save(Mesh->GetPackage(), SaveArgs);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("VEUV 失败: %s"), *Result.ErrorMessage);
    }
}
```

## 模块依赖

从 `VEUVCore` 和 `VEUVEditor` 模块的通用模式推断，该插件可能依赖以下模块。由于这是一个几何处理插件，其依赖关系相对标准。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

基于提供的 git 历史记录，该插件自创建以来（2026年5月12日）有密集的初期开发活动。

```
- 2026-05-14 5d715960 Volume Encoded UVs, temporarily disabled injectivity term and moved to dense initial R78 solve (算法调整：临时禁用注入性约束，切换到密集求解策略)
- 2026-05-13 df17886a VEUV: fail out with an empty chart rather than crash if the grid ends up with nothing allocated (错误处理：避免崩溃，优雅地处理空图表)
- 2026-05-12 e76e4ca8 Volume Encoded UVs, disabled forced injectivity on refinement (too prone to exploding) (算法调整：禁用细化阶段的强制注入性约束，以提高稳定性)
- 2026-05-12 cd2e1403 VEUV: add failure reporting -- detect failed packing, empty charts, inf/nan entries, inverted tris i (功能增强：添加详细的失败报告和检测机制)
- 2026-05-12 34b3773a VEUV: distribute complexity sample budget remainder across bins so low-budget voxels are not silentl (算法优化：改进复杂度采样预算分配策略)
```

### 维护评价

- **活跃维护**：插件创建于 2026 年 5 月 12 日，距今非常年轻。最近一次提交在 2026 年 5 月 14 日，表明处于积极的初期开发阶段。
- **当前状态**：这是一个**实验性**插件（`IsExperimentalVersion=true`，默认禁用）。从提交信息看，开发团队正在快速迭代核心算法，解决稳定性（崩溃、注入性约束爆炸）和功能性（失败报告）问题。
- **注意事项**：作为实验性功能，其 API 可能发生变化，算法在处理极端情况时可能不稳定。提交历史中多次出现“temporarily disabled”和“fail out rather than crash”的调整，说明它仍处于一个需要调试和完善的阶段。
- **推荐使用**：**谨慎推荐**。如果你的工作流迫切需要解决复杂模型的 UV 展开问题，并且愿意接受实验性功能可能带来的不稳定性和 API 变动，可以尝试使用。不建议在需要高度稳定性的生产环境主流程中依赖它。建议密切关注其更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VEUV)
- [官方文档]() (暂无)
- [测试用例]() (未在所提供的路径中明确找到，可能位于 `Engine/Tests/` 下或插件内部未列出)