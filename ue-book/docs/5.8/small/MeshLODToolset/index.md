# Mesh LOD Toolset

> A set of modules implementing 3D mesh LOD creation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 网格LOD工具集 |
| 分类 | 建模工具 |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshLODToolset` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/MeshLODToolset) | |

## 用途

MeshLODToolset 是一套面向编辑器的工具集，用于创建和管理静态网格（Static Mesh）的LOD（Level of Detail）版本。它解决的核心问题是**为复杂高面数网格自动生成用于远距离渲染的、面数更少的简化版本（LOD）**，以提升运行时性能。插件提供了两种主要方式：1. **LOD管理器**：用于查看、编辑和操作现有静态网格资产上已有的LOD层级。2. **自动生成LOD工具**：通过基于体素（Voxel）的网格生成算法（如固化、凸包等）和简化算法，从高分辨率源网格（HiRes Source）自动生成全新的LOD0网格，并可烘焙法线贴图和纹理，最终创建新的静态网格资产或更新现有资产。

## 使用场景

- 你是一名技术美术师，需要为场景中的复杂高模角色或道具自动生成一套优化的LOD链。
- 你正在制作一个开放世界游戏，需要批量处理大量静态网格资产，为它们快速创建LOD以提升GPU渲染性能。
- 你需要管理现有网格资产的LOD设置，例如查看不同LOD层级的顶点/面数、检查Nanite状态、清理未引用的材质等。
- 你希望将高分辨率扫描模型（HiRes Source）转换为适用于游戏引擎的优化LOD0网格。

## 蓝图用法

此插件主要提供编辑器模式下的交互式工具（Tool），其功能通过工具操作面板暴露，而非通过运行时蓝图节点。以下是工具内部的核心可调用操作：

### 核心节点（工具内部操作）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MoveToLOD0` | 将高分辨率源模型移动到LOD0位置。 | `ULODManagerHiResSourceModelActions` |
| `Delete` | 删除高分辨率源模型。 | `ULODManagerHiResSourceModelActions` |
| `CleanMaterials` | 清除任何未被任何LOD引用的材质。 | `ULODManagerMaterialActions` |
| `ReadFromPreset` | 从预设资产读取当前工具设置。 | `UGenerateStaticMeshLODAssetToolPresetProperties` |
| `WriteToPreset` | 将当前工具设置保存到预设资产。 | `UGenerateStaticMeshLODAssetToolPresetProperties` |

### 使用示例（工具操作描述）

1.  **LOD管理器**：在编辑器中选择一个或多个静态网格资产，进入建模模式，从工具栏中选择“LOD管理器”。在细节面板中，你可以查看所选网格的LOD信息（顶点/面数、材质等），并可以选择“显示LOD”来预览不同LOD级别的网格边界。通过“高分辨率源模型操作”和“材质操作”面板，可以执行移动HiRes到LOD0、删除HiRes或清理材质等操作。
2.  **自动生成LOD**：选择静态网格资产后，进入建模模式，选择“生成静态网格LOD资产”工具。在详细面板中配置“网格生成器”（如固化、凸包）、简化目标（三角形数量、几何公差）、法线生成、UV生成、纹理烘焙以及碰撞设置。配置完毕后，可以选择“创建新资产”或“更新现有资产”，然后接受工具以生成LOD网格及相关资产。

## C++ 用法

### 头文件引入

```cpp
#include "MeshLODToolsetModule.h"
#include "Tools/LODManagerTool.h"
#include "Tools/GenerateStaticMeshLODAssetTool.h"
#include "Graphs/GenerateStaticMeshLODProcess.h"
```

### 基本用法

```cpp
// 来源: 基于 Source/MeshLODToolset/Public/Tools/GenerateStaticMeshLODAssetTool.h 分析
// 通过工具构建器创建并设置生成LOD的工具
UGenerateStaticMeshLODAssetToolBuilder* ToolBuilder = NewObject<UGenerateStaticMeshLODAssetToolBuilder>();
// 设置工具进入资产编辑器模式 (在细节面板中不显示输出模式选项)
ToolBuilder->bUseAssetEditorMode = true;

// 在工具管理器环境中，创建工具实例
FToolBuilderState SceneState; // 此结构体由工具管理器上下文提供
UMultiSelectionMeshEditingTool* NewTool = ToolBuilder->CreateNewTool(SceneState);
```

### 进阶用法

```cpp
// 来源: 基于 Source/MeshLODToolset/Public/Graphs/GenerateStaticMeshLODProcess.h 分析
// 编程式地使用 UGenerateStaticMeshLODProcess 来生成LOD，无需启动交互式工具。
UStaticMesh* SourceMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/MyAssets/HighPolyMesh"));

UGenerateStaticMeshLODProcess* GenerateProcess = NewObject<UGenerateStaticMeshLODProcess>();
// 初始化过程，传入源网格
bool bInitialized = GenerateProcess->Initialize(SourceMesh);

if (bInitialized)
{
    // 配置生成参数
    FGenerateStaticMeshLODProcessSettings GenSettings;
    GenSettings.MeshGenerator = EGenerateStaticMeshLODProcess_MeshGeneratorModes::SolidifyAndClose;
    GenSettings.SolidifyVoxelResolution = 256;
    GenerateProcess->UpdateSettings(GenSettings);

    FGenerateStaticMeshLODProcess_SimplifySettings SimplifySettings;
    SimplifySettings.Method = EGenerateStaticMeshLODProcess_SimplifyMethod::GeometricTolerance;
    SimplifySettings.Tolerance = 0.5f; // 几何公差(厘米)
    GenerateProcess->UpdateSimplifySettings(SimplifySettings);

    // 执行计算
    FProgressCancel Progress;
    bool bComputed = GenerateProcess->ComputeDerivedSourceData(&Progress);

    if (bComputed)
    {
        // 获取生成的LOD0网格和切线
        const FDynamicMesh3& DerivedMesh = GenerateProcess->GetDerivedLOD0Mesh();
        const FMeshTangentsd& DerivedTangents = GenerateProcess->GetDerivedLOD0MeshTangents();

        // 可选：将生成的资产写入磁盘（创建新静态网格、材质和纹理）
        GenerateProcess->WriteDerivedAssetData();
        // 或者更新源网格资产
        GenerateProcess->UpdateSourceAsset(true); // true 表示将原始网格保存为 HiRes Source
    }
}
```

## Demo 示例

```cpp
// MyLODGenerator.h
#pragma once

#include "CoreMinimal.h"
#include "Graphs/GenerateStaticMeshLODProcess.h"

class FMyLODGenerator
{
public:
    /** 为一个给定的 UStaticMesh 自动生成LOD并保存为新资产 */
    static bool GenerateLODForAsset(UStaticMesh* SourceMesh, const FString& NewAssetSuffix = TEXT("_AutoLOD"));
};

// MyLODGenerator.cpp
#include "MyLODGenerator.h"
#include "Graphs/GenerateStaticMeshLODProcess.h"

bool FMyLODGenerator::GenerateLODForAsset(UStaticMesh* SourceMesh, const FString& NewAssetSuffix)
{
    if (!SourceMesh)
    {
        UE_LOG(LogMeshLODToolset, Error, TEXT("FMyLODGenerator::GenerateLODForAsset: SourceMesh is null."));
        return false;
    }

    UGenerateStaticMeshLODProcess* GenerateProcess = NewObject<UGenerateStaticMeshLODProcess>();
    if (!GenerateProcess->Initialize(SourceMesh))
    {
        UE_LOG(LogMeshLODToolset, Error, TEXT("Failed to initialize LOD generation process for %s."), *SourceMesh->GetName());
        return false;
    }

    // 使用默认简化设置（几何公差）
    FGenerateStaticMeshLODProcess_SimplifySettings SimplifySettings;
    GenerateProcess->UpdateSimplifySettings(SimplifySettings);

    // 配置输出名称
    GenerateProcess->UpdateDerivedPathName(SourceMesh->GetName(), NewAssetSuffix);

    // 执行生成
    FProgressCancel Progress;
    if (!GenerateProcess->ComputeDerivedSourceData(&Progress))
    {
        UE_LOG(LogMeshLODToolset, Error, TEXT("LOD computation failed for %s."), *SourceMesh->GetName());
        return false;
    }

    // 将结果写入新的静态网格资产
    if (!GenerateProcess->WriteDerivedAssetData())
    {
        UE_LOG(LogMeshLODToolset, Error, TEXT("Failed to write derived asset for %s."), *SourceMesh->GetName());
        return false;
    }

    UE_LOG(LogMeshLODToolset, Log, TEXT("Successfully generated LOD asset for %s."), *SourceMesh->GetName());
    return true;
}
```

## 模块依赖

要使用此插件，你的项目模块通常需要依赖以下模块（除了标准的Core, Engine等）：

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 提供动态网格（FDynamicMesh3）、几何处理算法等核心几何数据结构。 |
| `GeometryFramework` | 提供交互式工具（Interactive Tools）框架和预览网格（PreviewMesh）等组件。 |
| `ModelingComponents` | 提供建模模式下的通用工具组件，如多选网格编辑工具构建器（UMultiSelectionMeshEditingToolBuilder）。 |
| `GeometryFlow` | 提供节点图（Graph）架构，用于构建和执行复杂的几何处理流程（LOD生成的核心引擎）。 |
| `StaticMeshDescription` | 用于处理和操作静态网格的 MeshDescription 数据。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量被截断为浮点数时产生的编译警告。 |
| 2026-04-27 | `8b508596` | Modeling Mode AutoLOD: defend against a crash when a MeshDescription's PolygonGroupID does not corre... | 建模模式AutoLOD：防止在MeshDescription的PolygonGroupID不匹配时发生崩溃。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到UE_LOGF。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了之前一次错误的“查找替换”后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | [回退] - 变更列表51314860。 |

### 维护评价

- **创建时间**：2024年1月30日，插件年龄约2年，属于较新的工具。
- **近期活跃度**：从2026年2月至5月有持续的提交记录，主要集中在错误修复、代码健壮性提升和代码现代化方面，表明插件仍处于**积极维护和迭代**中。
- **状态**：该插件在 `.uplugin` 中标记为 `IsBetaVersion: true` 和 `Hidden: true`，表明它目前仍处于**实验性/Beta测试阶段**，功能和接口可能在正式发布前发生变动。
- **推荐程度**：**推荐关注和试用**。作为Epic官方提供的工具集，它在生成LOD方面的算法和流程具有权威性。虽然仍在Beta阶段，但其近期持续的维护表明Epic对其投入持续关注，适合用于探索和评估先进的网格LOD生成流程。不建议在需要高度稳定的生产环境中依赖其所有功能。