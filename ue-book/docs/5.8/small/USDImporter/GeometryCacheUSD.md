# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、测试资源） |
| 模块 | `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `GeometryCacheUSD` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USDImporter 插件为 Unreal Engine 提供了对 Pixar Universal Scene Description (USD) 格式的全面支持。它不仅仅是一个简单的文件导入器，而是一个完整的 USD 资产流水线集成方案。该插件的核心功能是：

1.  **USD 文件导入**：能够将 `.usd`, `.usda`, `.usdc`, `.usdz` 格式的文件直接导入到 UE 中，将其转换为引擎可以理解和渲染的资产（如静态网格体、动画序列、材质等）。
2.  **USD Stage 编辑器**：提供了一个专用的编辑器窗口（USD Stage），允许用户在 UE 中可视化地查看、浏览和编辑 USD Stage（即一个 USD 文件中的完整场景树和属性）。这实现了 USD 与 UE 资产的实时双向同步。
3.  **USD 到几何缓存**：能够将 USD 中的动画网格体序列导入为 GeometryCache 资产，用于高效的逐帧网格体播放。
4.  **USD 导出**：允许用户将 UE 中的场景或资产导出为 USD 格式，实现与其它 DCC 工具（如 Maya, Houdini, Katana）的无缝数据交换。

该插件的存在是为了解决影视、动画、虚拟制片和复杂游戏项目中，跨软件协作和资产管理标准化的需求。

## 使用场景

-   **影视和虚拟制片项目**：你需要将从 Maya、Houdini 或其它 DCC 工具中创建的复杂场景（包含模型、动画、灯光、摄像机）导入到 UE 中进行实时渲染或虚拟制片。
-   **大规模场景协作**：多个团队（如建模、动画、特效）使用不同的软件，需要通过 USD 作为中间格式进行资产传递和场景组装，确保数据一致性和非破坏性编辑。
-   **程序化内容生成 (PCG)**：使用 USD 作为程序化场景描述的输入格式，然后导入 UE 进行进一步处理。
-   **需要高质量动画回放**：将 USD 中的角色或物体动画导入为 GeometryCache，以获得精确的逐帧网格体变形效果，用于过场动画或预览。

## 蓝图用法

USDImporter 插件主要通过编辑器交互使用，但部分模块（如 `USDStage`）暴露了蓝图可调用的接口用于查询 USD Stage 状态。`GeometryCacheUSD` 模块提供了蓝图可用的组件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `创建 USD 几何缓存组件` | 向一个 Actor 添加一个从 USD 文件驱动几何缓存的组件。 | `UGeometryCacheUsdComponent` |

### 使用示例（蓝图描述）

1.  **在 Actor 中使用 USD 几何缓存**：
    *   在 Actor 蓝图中，通过 `Add Component` 节点添加一个 `USD Geometry Cache` 组件。
    *   为该组件设置一个 `USD 文件路径` 和 `Prim 路径`（即 USD Stage 中特定几何体的路径）。
    *   组件将自动从指定的 USD 路径加载动画网格体数据并进行播放，其行为类似于标准的 GeometryCacheComponent，但数据源是 USD 文件。

## C++ 用法

插件的主要 C++ 功能集中在 `USDStage` 和 `USDClasses` 模块中，用于编程式地与 USD Stage 交互。`GeometryCacheUSD` 模块则提供了从 USD 驱动几何缓存的能力。

### 头文件引入

```cpp
// 使用 USD Stage 相关功能
#include "USDStage.h"
#include "USDSchemaConversion.h"

// 使用 USD 几何缓存功能
#include "GeometryCacheUSD.h"
```

### 基本用法

以下示例展示如何使用 `FUsdStage` 类打开并查询一个 USD Stage。

```cpp
// 来源: 基于 USDStage 模块通用用法推断
#include "USDStage.h"

void AMyActor::ReadFromUsdFile()
{
    // 创建一个指向本地 USD 文件的 Stage
    FString StagePath = TEXT("C:/MyProject/Content/MyScene.usda");
    UE::FUsdStage Stage = UE::FUsdStage::Open(StagePath);

    if (Stage)
    {
        // 获取 Stage 的根 Prim
        UsdToUnreal::FUsdPrim RootPrim = Stage.GetPseudoRoot();

        // 遍历 Stage 中的所有 Prims
        for (const UsdToUnreal::FUsdPrim& ChildPrim : Stage.TraverseAll())
        {
            UE_LOG(LogTemp, Log, TEXT("USD Prim: %s"), *ChildPrim.GetPrimPath().ToString());
            
            // 检查 Prim 是否是一个可导入的网格体
            if (UsdToUnreal::IsMesh(ChildPrim))
            {
                UE_LOG(LogTemp, Log, TEXT("  Found a Mesh!"));
                // 此处可以调用转换函数将 USD Mesh 转换为 UStaticMesh* 等 UE 资产
            }
        }

        // 关闭 Stage，释放资源
        Stage.Close();
    }
}
```

### 进阶用法

结合 `FUsdStage` 和 `UsdToUnreal` 命名空间中的函数，可以读取和设置 USD Prim 的属性。

```cpp
// 来源: 基于 USDSchemaConversion 模块通用用法推断
#include "USDStage.h"
#include "USDSchemaConversion.h"

void AMyActor::ManipulateUsdAttributes()
{
    UE::FUsdStage Stage = UE::FUsdStage::Open(TEXT("C:/MyProject/Content/Box.usda"));
    if (!Stage) return;

    // 通过路径获取一个具体的 Prim
    UsdToUnreal::FUsdPrim BoxPrim = Stage.GetPrimAtPath(TEXT("/World/MyBox"));
    if (BoxPrim.IsValid())
    {
        // 读取 Prim 的“可见性”属性
        bool bVisible = true;
        if (UsdToUnreal::GetAttribute<bool>(BoxPrim, TEXT("visibility"), bVisible))
        {
            UE_LOG(LogTemp, Log, TEXT("Box visibility: %s"), bVisible ? TEXT("visible") : TEXT("invisible"));
        }

        // 读取一个变换矩阵（世界变换）
        FTransform WorldTransform;
        if (UsdToUnreal::GetWorldTransform(BoxPrim, WorldTransform))
        {
            UE_LOG(LogTemp, Log, TEXT("Box world location: %s"), *WorldTransform.GetLocation().ToString());
        }
    }
}
```

## Demo 示例

一个从 USD Stage 中读取特定 Prim 名称并打印出来的最小控制台应用程序示例。

### USDStageReader.h
```cpp
// MyUSDStageReader.h
#pragma once

#include "CoreMinimal.h"

class FMyUSDStageReader
{
public:
    void ReadAndPrintPrimNames(const FString& UsdFilePath, const FString& PrimPathPrefix);
};
```

### USDStageReader.cpp
```cpp
// MyUSDStageReader.cpp
#include "MyUSDStageReader.h"
#include "USDStage.h"
#include "USDSchemaConversion.h"
#include "Misc/Paths.h"

void FMyUSDStageReader::ReadAndPrintPrimNames(const FString& UsdFilePath, const FString& PrimPathPrefix)
{
    // 将相对路径转换为完整路径
    const FString FullPath = FPaths::ConvertRelativePathToFull(UsdFilePath);
    
    UE_LOG(LogTemp, Display, TEXT("Opening USD Stage: %s"), *FullPath);
    UE::FUsdStage Stage = UE::FUsdStage::Open(FullPath);
    
    if (!Stage)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open USD Stage."));
        return;
    }

    UE_LOG(LogTemp, Display, TEXT("Scanning for prims under: %s"), *PrimPathPrefix);
    
    // 使用 Stage 的遍历器查找匹配前缀的 Prims
    for (const UsdToUnreal::FUsdPrim& Prim : Stage.TraverseAll())
    {
        const FString PrimPath = Prim.GetPrimPath().ToString();
        if (PrimPath.StartsWith(PrimPathPrefix))
        {
            // 获取 Prim 的类型名称
            const UsdToUnreal::FUsdPrimType& PrimType = Prim.GetPrimTypeInfo().GetPrimType();
            UE_LOG(LogTemp, Display, TEXT("Found Prim: %s (Type: %s)"), *PrimPath, *PrimType.GetUsdTypeName().ToString());
        }
    }

    UE_LOG(LogTemp, Display, TEXT("USD Stage scan complete."));
    Stage.Close();
}
```

**如何使用**：
```cpp
// 在游戏模块的某个地方（如 GameInstance 初始化）
FMyUSDStageReader Reader;
Reader.ReadAndPrintPrimNames(TEXT("Content/MyScene.usda"), TEXT("/World/Characters/"));
```

## 模块依赖

要使用 USDImporter 插件的功能，你的模块需要依赖以下独特的模块（Core, Engine, GeometryCache 等常见依赖已省略）：

| 模块 | 用途 |
|---|---|
| `USDStage` | 提供 `FUsdStage` 类，用于打开、查询和操作 USD Stage。这是与 USD 数据交互的核心运行时模块。 |
| `USDSchemas` | 提供 USD Schema 转换函数（如 `UsdToUnreal` 命名空间下的函数），用于在 USD Prim 属性和 UE 资产/对象之间进行转换。 |
| `USDClasses` | 提供 USD 相关的 UE 类型定义，如 `FUsdPrim`, `FUsdAttribute` 等，是 `USDStage` 和 `USDSchemas` 的基础。 |
| `USDClassesEditor` | 编辑器专用的 USD 类型和工具，用于 USD Stage 编辑器窗口。 |
| `USDStageImporter` | 实现具体的 USD 文件导入逻辑，将 USD 场景转换为 UE 资产。 |
| `GeometryCacheUSD` | 提供 `UGeometryCacheUsdComponent` 和 `UGeometryCacheTrackUsd`，用于将 USD 动画网格体作为 GeometryCache 进行播放。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数导致编译警告的代码。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD功能：添加了对蓝图无关控制绑定（Control Rig）赋值的支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | USD功能：针对26.03版本更新导致AnimQuery内部引用在LOD变化时失效的问题进行了规避。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式说明符：当参数为64位时，将32位格式符改为64位，反之亦然。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD功能：烘焙曝光动画轨道的所有帧。 |

### 维护评价

-   **创建时间**：插件创建于2018年底，已有相当长的历史。
-   **活跃度**：基于提供的 Git 历史，该插件**仍在活跃维护和开发中**。最近的提交（2026年5月）显示团队正在修复编译问题并添加新功能（如 Control Rig 支持）。这表明它是一个重要的、持续发展的功能模块。
-   **已知问题**：`.uplugin` 中明确标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，这意味着该插件**目前处于测试阶段**，可能还未完全稳定，不建议在需要高度稳定性的生产项目中默认启用。它可能包含实验性 API 和未完成的功能。
-   **推荐**：对于影视、虚拟制片或需要 USD 工作流的前沿项目，**强烈推荐使用和评估**。对于追求稳定性的传统游戏开发项目，建议仅在需要且经过充分测试后启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)