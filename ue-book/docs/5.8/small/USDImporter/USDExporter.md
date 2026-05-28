# USD Exporter

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导出器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、USD相关的资产用户数据、测试资源） |
| 模块 | `USDExporter` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDExporter) | |

## 用途

`USDExporter` 是 `USDImporter` 插件的组成部分，它解决了 Unreal Engine 内容到 USD (Universal Scene Description) 格式的**导出**问题。它弥补了原生 UE 工作流与 USD 生态之间的缺口，使用户能够将场景、资产和动画从 UE 导出为 USD 文件，从而实现与 Maya、Houdini、Blender 等支持 USD 的 DCC 工具以及影视管线的无缝对接。该模块是 Epic 推出的 USD 互操作方案中的关键一环。

## 使用场景

-   你的美术团队在 UE 中搭建了完整的场景或编辑了资产（如地形、材质），需要将其导出回 Maya 或 Houdini 进行进一步加工。
-   你构建了一个基于 UE 的实时影视预览管线，并需要将场景和镜头动画以 USD 格式输出给下游的灯光和渲染环节。
-   你需要利用 USD 的图层 (Layer)、引用 (Reference) 和变体 (Variant) 等高级特性来组织复杂的资产或场景。
-   你希望通过脚本（Python/蓝图）自动化资产导出流程，将 UE 资产发布到公司内部的资产库或流水线中。

## 蓝图用法

该模块通过 `UUsdConversionBlueprintLibrary` 和 `UUsdConversionBlueprintContext` 等类暴露了大量蓝图节点，主要分为以下几组：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStageRootLayer` | 设置要写入的 USD Stage 根层文件路径，并创建或打开它 | `UUsdConversionBlueprintContext` |
| `ConvertLightComponent` / `ConvertDirectionalLightComponent` 等 | 将对应的 UE 灯光组件转换为 USD Prim 并写入当前 Stage | `UUsdConversionBlueprintContext` |
| `ConvertMeshComponent` | 将网格组件转换为 USD Prim | `UUsdConversionBlueprintContext` |
| `ConvertMaterialOverrides` | 将网格资产的材质覆盖信息写入到指定的 Prim 路径 | `UUsdConversionBlueprintContext` |
| `InsertSubLayer` | 向指定的父层文件中插入一个子层 | `UUsdConversionBlueprintLibrary` |
| `AddReference` / `AddPayload` | 为 Prim 添加外部 USD 文件的引用或负载 | `UUsdConversionBlueprintLibrary` |
| `GetUniqueFilePathForExport` | 获取一个保证在当前作用域内唯一的、可用于导出资产的文件路径 | `UUsdConversionBlueprintLibrary` |
| `GetPrimPathForObject` | 根据 UE Actor 或 Component 推断出其对应的 USD Prim 路径 | `UUsdConversionBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **导出一个静态网格**：
    *   创建一个 `UUsdConversionBlueprintContext` 对象。
    *   调用 `SetStageRootLayer`，指向一个新的 `.usda` 文件。
    *   获取要导出的 `UStaticMesh` 资产。
    *   调用 `ConvertMeshComponent`（如果导出的是场景中的网格体实例）或结合 `SetPrimPathForObject` 和材质转换函数，将数据写入 Context 所持有的 Stage。
    *   完成后调用 `Cleanup` 释放资源。

2.  **设置复杂的 USD 层结构**：
    *   使用 `GetNumLevelsToExport` 和 `StreamInRequiredLevels` 确保所有需要的子关卡都已加载。
    *   使用 `MakePathRelativeToLayer` 和 `InsertSubLayer` 在蓝图中动态构建 USD 的 Sublayer 结构。
    *   使用 `AddReference` 或 `AddPayload` 将外部资产组合到当前场景中。

## C++ 用法

### 头文件引入

```cpp
#include "USDExporterModule.h"
#include "USDConversionBlueprintLibrary.h"
#include "USDConversionBlueprintContext.h"
```

### 基本用法

以下示例展示了如何在 C++ 中使用 `UUsdConversionBlueprintContext` 导出一个静态网格到 USD 文件。

```cpp
// 假设我们有一个 UStaticMesh* MeshToExport
void ExportStaticMeshToUSD(UStaticMesh* MeshToExport, const FString& OutputPath)
{
    // 创建上下文对象
    UUsdConversionBlueprintContext* Context = NewObject<UUsdConversionBlueprintContext>();
    
    // 设置输出 Stage 的根层
    FFilePath StagePath;
    StagePath.FilePath = OutputPath;
    Context->SetStageRootLayer(StagePath);
    
    // 为了导出单个网格，我们通常为其创建一个默认的 Prim
    FString PrimPath = TEXT("/Root/ExportedMesh");
    
    // 注意：直接转换网格组件需要场景中的实例，这里我们使用静态函数进行资产级导出。
    // 更常见的做法是结合 `GetPrimPathForObject` 和材质转换函数。
    // 此处仅为演示上下文的基本生命周期。
    
    // 导出完成后清理上下文，非常重要，否则会持续持有 Stage 的引用
    Context->Cleanup();
}
```

### 进阶用法

该模块的函数库 (`UUsdConversionBlueprintLibrary`) 提供了许多底层工具，可用于构建复杂的导出流水线。

```cpp
// 示例：使用唯一路径作用域批量导出资产
void BatchExportAssets(TArray<UObject*> AssetsToExport)
{
    // 开始一个唯一路径作用域，确保生成的路径不重复
    UUsdConversionBlueprintLibrary::BeginUniquePathScope();
    
    for (UObject* Asset : AssetsToExport)
    {
        // 为每个资产生成一个唯一的 USD 文件路径
        FString AssetName = Asset->GetName();
        FString DesiredPath = FPaths::Combine(TEXT("C:/Exports/"), AssetName + TEXT(".usda"));
        FString UniqueUSDPath = UUsdConversionBlueprintLibrary::GetUniqueFilePathForExport(DesiredPath);
        
        // ... 根据资产类型调用对应的导出逻辑 ...
        // 例如，如果是 UMaterialInterface，则可能调用 UMaterialExporterUsd::ExportMaterial
    }
    
    // 结束作用域，清理内部路径缓存
    UUsdConversionBlueprintLibrary::EndUniquePathScope();
}

// 示例：检查是否可以向目标层导出
bool bCanExport = UUsdConversionBlueprintLibrary::CanExportToLayer(TEXT("C:/MyStage.usda"));
```

## Demo 示例

一个最小的 C++ 示例，演示如何导出一个静态网格到 `.usda` 文件。

```cpp
// MyUSDExporter.h
#pragma once

#include "CoreMinimal.h"

class FMyUSDExporter
{
public:
    static bool ExportStaticMeshToUSD(UStaticMesh* Mesh, const FString& OutputUSDPath);
};

// MyUSDExporter.cpp
#include "MyUSDExporter.h"
#include "USDConversionBlueprintContext.h"
#include "MeshExporterUSD.h" // 实际的导出器，位于 Public/MeshExporterUSD.h

bool FMyUSDExporter::ExportStaticMeshToUSD(UStaticMesh* Mesh, const FString& OutputUSDPath)
{
    if (!Mesh)
    {
        return false;
    }

    // 1. 创建并设置导出上下文
    UUsdConversionBlueprintContext* Context = NewObject<UUsdConversionBlueprintContext>();
    FFilePath StagePath;
    StagePath.FilePath = OutputUSDPath;
    Context->SetStageRootLayer(StagePath);

    // 2. 调用静态网格的导出函数
    // 注意：实际的导出逻辑封装在UStaticMeshExporterUsd或相关的静态函数中，
    // 这里为了演示目的，使用一个简化的转换调用。
    // 实际使用时，你可能需要设置更多选项。
    bool bSuccess = Context->ConvertMeshComponent(
        nullptr, // 导出单个资产时，组件可以为nullptr
        TEXT("/Root/MyStaticMesh"), // 目标 Prim 路径
        Mesh
    );

    // 3. 清理上下文
    Context->Cleanup();

    return bSuccess;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `USDUtilities` | 提供底层的 USD 数据类型转换、Stage 管理和工具函数 |
| `USDClasses` | 提供 USD 相关的 UObject 类、组件和数据结构（如 `UUsdAssetUserData`） |
| `USD` | Epic Games 提供的 USD 核心库封装 |
| `UnrealUSDWrapper` | Epic Games 对 OpenUSD C++ API 的包装层 |
| `MeshDescription` | 用于网格数据在导入导出过程中的中间表示和操作 |
| `MeshUtilities` | 提供网格处理（如 LOD）相关的工具函数 |
| `Landscape` | 用于导出 Landscape（地形）资产 |
| `Foliage` | 用于导出 Instanced Foliage（植被实例） |

*注意：以上列表基于插件通常的依赖关系推断。具体的 Build.cs 依赖应以源码为准。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数产生的警告代码。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 新增支持分配独立于蓝图的控制绑定(Control Rig)。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD values change. | USD: 规避了 USD 库升级至 26.03 后，当 LOD 级别变化时 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串中 32/64 位说明符与参数不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 烘焙曝光(Exposure)动画轨道的所有帧。 |

### 维护评价

`USDExporter` 模块是 Unreal Engine 官方 USD 工作流的核心组件，**处于非常活跃的维护状态**。
- **更新频率**：从近期提交记录看，近两个月内有多次功能性更新和错误修复（如控制烘焙、LOD 动画规避、格式化修复），表明开发团队正在积极维护和增强该功能。
- **稳定性**：最新修复针对的是 USD 库版本升级带来的兼容性问题，说明团队在跟进上游库的更新。
- **功能完整性**：该模块是 `USDImporter` 的组成部分，整个插件包含导入、导出、编辑器交互等多个模块，表明这是一个功能完备、持续演进的解决方案。
- **推荐使用**：**强烈推荐**。尽管插件标记为 `Beta`，但其核心导出功能已相当成熟，并且有 Epic 官方的持续投入，是 UE 与 USD 互操作的首选官方方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDExporter)
- [官方文档]( ) （`.uplugin` 中未提供 DocsURL）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)