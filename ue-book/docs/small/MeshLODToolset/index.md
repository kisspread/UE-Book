# Mesh LOD Toolset

> A set of modules implementing 3D mesh LOD creation

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | Hidden (需手动启用) |
| 包含内容 | true |
| 模块 | MeshLODToolset (Editor) |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MeshLODToolset) | |

## 用途

MeshLODToolset 是一个**编辑器内 LOD 自动生成与管理工具集**，提供两个核心交互式工具：

1. **AutoLOD 工具（GenerateStaticMeshLODAssetTool）**：从高模 StaticMesh 自动生成低模 LOD 资产。支持多种网格生成策略（Solidify、CleanAndSimplify、ConvexHull），自动计算简化网格、生成法线、UV、烘焙纹理/材质，并可同时生成简单碰撞体。
2. **LOD Manager 工具（LODManagerTool）**：查看和管理 StaticMesh 已有的 LOD 层级信息，包括顶点/三角形数量、Nanite 状态、材质列表，以及 HiRes Source Model 的迁移和清理。

这两个工具基于 UE 的 GeometryFlow 计算图框架，在后台异步执行网格处理管线，用户可以在编辑器中实时预览结果。

## 使用场景

- 你有一个高精度的 StaticMesh（如从 DCC 工具导入），需要快速生成多个 LOD 级别 → 用 **AutoLOD 工具**
- 你需要为移动端优化，将复杂网格简化并自动烘焙法线贴图 → 用 **AutoLOD 工具**（Simplify + Normals + Texture Baking）
- 你需要为网格自动生成简单碰撞体（凸包、胶囊等）→ 用 **AutoLOD 工具**（Collision 设置）
- 你想查看某个 StaticMesh 的 LOD 信息、管理 HiRes Source Model 或清理未引用的材质 → 用 **LOD Manager 工具**
- 你希望保存一组 LOD 生成参数配置，方便在多个资产间复用 → 用 **AutoLOD Settings 预设资产**

> **注意**：此插件标记为 `IsBetaVersion=true` 且 `Hidden=true`，默认不启用。需要在编辑器插件设置中手动启用。

## 编辑器用法

### AutoLOD 工具（Generate Static Mesh LOD Asset）

通过 Mesh Modeling Toolset 的工具面板或 Static Mesh 编辑器启动。工具 UI 分为以下几个区域：

#### Output Options（输出选项）

| 参数 | 说明 |
|---|---|
| **Output Mode** | `CreateNewAsset`（创建新资产）或 `UpdateExistingAsset`（更新现有资产） |
| **New Asset Name** | 新资产的基础名称（仅 CreateNewAsset 模式） |
| **Save Input As HiRes Source** | 是否将输入网格存储为 HiRes Source（仅 UpdateExistingAsset 模式） |
| **Generated Suffix** | 生成资产的后缀，默认 `_AutoLOD` |

#### Preset（预设）

| 参数 | 说明 |
|---|---|
| **Settings Preset** | 指向 `UStaticMeshLODGenerationSettings` 资产，用于保存/加载配置 |
| **Read From Preset** | 从预设资产读取设置 |
| **Write To Preset** | 将当前设置写入预设资产 |

#### Generator Configuration（生成器配置）

**Preprocessing（预处理）**：
- **Detail Filter Group Layer**：用于在处理前过滤细节的多边形组层
- **Thicken Weight Map / Thicken Amount**：加厚网格以修复 Solidify 时的形状侵蚀

**Mesh Generation（网格生成）**：

| 模式 | 说明 |
|---|---|
| **Solidify** | 使用 Marching Cubes + Winding Numbers 从输入形状生成实体网格 |
| **SolidifyAndClose** | 在 Solidify 基础上进行膨胀-收缩操作，消除小孔和尖锐内角（默认） |
| **CleanAndSimplify** | 直接简化输入网格属性并填补小孔 |
| **ConvexHull** | 计算输入形状的凸包 |

- **Voxel Resolution**：Solidify 模式的体素分辨率（8-1024，默认 128）
- **Winding Threshold**：确定内部区域的 Winding Number 阈值
- **Closure Distance**：形态学闭合操作的偏移距离

**Simplification（简化）**：

| 目标类型 | 说明 |
|---|---|
| **Triangle Count** | 指定目标三角形数量 |
| **Vertex Count** | 指定目标顶点数量 |
| **Triangle Percentage** | 指定保留百分比 |
| **Geometric Tolerance** | 指定几何容差（厘米），默认 0.5 |

**Normals（法线）**：

| 方法 | 说明 |
|---|---|
| **From Angle Threshold** | 根据角度阈值自动分割法线（默认，阈值 60°） |
| **Per Vertex** | 逐顶点法线 |
| **Per Triangle** | 逐三角形法线（全平面） |

**UV Generation（UV 生成）**：

| 方法 | 说明 |
|---|---|
| **PatchBuilder** | 基于曲率的自动 UV 分割（默认），支持初始 Patch 数量、合并阈值、角度偏差等参数 |
| **UVAtlas** | 微软 UVAtlas 算法 |
| **XAtlas** | 轻量级自动 UV |

**Texture Baking（纹理烘焙）**：
- **Bake Image Res**：烘焙分辨率（16×16 到 8192×8192，默认 1024）
- **Bake Thickness**：烘焙搜索距离
- **Combine Textures**：是否将多张纹理合并为一张 Atlas

**Simple Collision（简单碰撞）**：

| 类型 | 说明 |
|---|---|
| **AlignedBoxes** | 轴对齐包围盒 |
| **OrientedBoxes** | 有向包围盒 |
| **MinimalSpheres** | 最小包围球 |
| **Capsules** | 胶囊体 |
| **ConvexHulls** | 凸包（默认） |
| **SweptHulls** | 扫掠凸包 |
| **MinVolume** | 最小体积 |
| **None** | 不生成碰撞 |

#### Source Textures Configuration（源纹理配置）

列出源材质和纹理，可以对每个纹理/材质设置烘焙约束（`NoConstraint` 或 `DoNotBake`/`UseExistingTexture`）。

### LOD Manager 工具

在编辑器中选择 StaticMesh Actor 后启动，提供以下功能面板：

#### LOD Information

显示选中网格的所有 LOD 层级信息：
- **Source LODs**：每个 LOD 的顶点数和三角形数
- **HiRes Source**：HiRes 源模型的顶点/三角形数（如有）
- **Render LODs**：渲染数据中每个 LOD 的顶点/三角形数
- **Nanite**：是否启用 Nanite 及保留三角形百分比
- **Materials**：材质列表

#### LOD Preview

| 参数 | 说明 |
|---|---|
| **Show LOD** | 选择预览哪个 LOD 级别 |
| **Show Borders** | 是否显示网格边界线（便于检查 UV 接缝） |

#### HiRes Source Model 操作

| 操作 | 说明 |
|---|---|
| **Move To LOD0** | 将 HiRes Source Model 移动到 LOD0 位置 |
| **Delete** | 删除 HiRes Source Model |

#### Material 操作

| 操作 | 说明 |
|---|---|
| **Clean Materials** | 清除未被任何 LOD 引用的材质 |

## C++ 用法

### 头文件引入

```cpp
#include "Tools/GenerateStaticMeshLODAssetTool.h"
#include "Tools/LODManagerTool.h"
#include "Tools/LODGenerationSettingsAsset.h"
#include "Graphs/GenerateStaticMeshLODProcess.h"
#include "Graphs/GenerateMeshLODGraph.h"
```

### 基本用法：通过 Process 管线生成 LOD

`UGenerateStaticMeshLODProcess` 是核心处理管线，封装了完整的 GeometryFlow 计算图：

```cpp
// 创建 Process 对象
UGenerateStaticMeshLODProcess* Process = NewObject<UGenerateStaticMeshLODProcess>();

// 初始化：读取源网格、提取材质和纹理
Process->Initialize(SourceStaticMesh);

// 配置网格生成模式（Solidify / SolidifyAndClose / CleanAndSimplify / ConvexHull）
FGenerateStaticMeshLODProcessSettings GenSettings;
GenSettings.MeshGenerator = EGenerateStaticMeshLODProcess_MeshGeneratorModes::SolidifyAndClose;
GenSettings.SolidifyVoxelResolution = 256;
Process->UpdateSettings(GenSettings);

// 配置简化参数
FGenerateStaticMeshLODProcess_SimplifySettings SimplifySettings;
SimplifySettings.Method = EGenerateStaticMeshLODProcess_SimplifyMethod::GeometricTolerance;
SimplifySettings.Tolerance = 1.0f;
Process->UpdateSimplifySettings(SimplifySettings);

// 配置法线
FGenerateStaticMeshLODProcess_NormalsSettings NormalsSettings;
NormalsSettings.Method = EGenerateStaticMeshLODProcess_NormalsMethod::FromAngleThreshold;
NormalsSettings.Angle = 60.0f;
Process->UpdateNormalsSettings(NormalsSettings);

// 执行计算
bool bSuccess = Process->ComputeDerivedSourceData(nullptr);

// 获取结果
const FDynamicMesh3& ResultMesh = Process->GetDerivedLOD0Mesh();
const FMeshTangentsd& ResultTangents = Process->GetDerivedLOD0MeshTangents();
const FSimpleShapeSet3d& ResultCollision = Process->GetDerivedCollision();
```

*来源：`GenerateStaticMeshLODProcess.h`*

### 进阶用法：使用 GeometryFlow 图直接控制

`FGenerateMeshLODGraph` 提供更底层的 GeometryFlow 图控制：

```cpp
FGenerateMeshLODGraph Graph;

// 构建计算图（可选传入源网格 hint 以优化）
Graph.BuildGraph(&SourceMesh);

// 设置源网格
Graph.SetSourceMesh(SourceMesh);

// 选择核心生成模式
Graph.UpdateCoreMeshGeneratorMode(FGenerateMeshLODGraph::ECoreMeshGeneratorMode::SolidifyAndClose);

// 配置各阶段参数
Graph.UpdateSolidifySettings(SolidifySettings);
Graph.UpdateMorphologySettings(MorphologySettings);
Graph.UpdateSimplifySettings(SimplifySettings);
Graph.UpdateNormalsSettings(NormalsSettings);
Graph.UpdateAutoUVSettings(UVSettings);

// 执行评估
FDynamicMesh3 ResultMesh;
FMeshTangentsd ResultTangents;
FSimpleShapeSet3d ResultCollision;
FNormalMapImage NormalMap;
TArray<TUniquePtr<FTextureImage>> TextureImages;
FTextureImage MultiTextureImage;

Graph.EvaluateResult(ResultMesh, ResultTangents, ResultCollision,
                     NormalMap, TextureImages, MultiTextureImage, nullptr);
```

*来源：`GenerateMeshLODGraph.h`*

### 保存和加载预设

```cpp
// 创建预设资产（通过 UStaticMeshLODGenerationSettingsFactory 在编辑器中创建）
UStaticMeshLODGenerationSettings* Preset = /* ... */;

// 从预设读取设置到 Process
Process->UpdatePreprocessSettings(Preset->Preprocessing);
Process->UpdateSettings(Preset->MeshGeneration);
Process->UpdateSimplifySettings(Preset->Simplification);
Process->UpdateNormalsSettings(Preset->Normals);
Process->UpdateTextureSettings(Preset->TextureBaking);
Process->UpdateUVSettings(Preset->UVGeneration);
Process->UpdateCollisionSettings(Preset->SimpleCollision);
```

*来源：`LODGenerationSettingsAsset.h`*

## Demo 示例

以下展示如何在编辑器工具中以编程方式启动 AutoLOD 工具：

```cpp
// MyAutoLODHelper.h
#pragma once

#include "CoreMinimal.h"

class UStaticMesh;

class FMyAutoLODHelper
{
public:
    // 为指定 StaticMesh 生成 LOD，使用默认设置
    static bool GenerateLODForMesh(UStaticMesh* Mesh, int32 TargetTriangleCount = 500);
};
```

```cpp
// MyAutoLODHelper.cpp
#include "MyAutoLODHelper.h"
#include "Graphs/GenerateStaticMeshLODProcess.h"

bool FMyAutoLODHelper::GenerateLODForMesh(UStaticMesh* Mesh, int32 TargetTriangleCount)
{
    if (!Mesh) return false;

    UGenerateStaticMeshLODProcess* Process = NewObject<UGenerateStaticMeshLODProcess>();
    if (!Process->Initialize(Mesh))
    {
        return false;
    }

    // 使用 CleanAndSimplify 模式（最简单直接的方式）
    FGenerateStaticMeshLODProcessSettings GenSettings;
    GenSettings.MeshGenerator = EGenerateStaticMeshLODProcess_MeshGeneratorModes::CleanAndSimplify;
    Process->UpdateSettings(GenSettings);

    // 设置简化目标
    FGenerateStaticMeshLODProcess_SimplifySettings SimplifySettings;
    SimplifySettings.Method = EGenerateStaticMeshLODProcess_SimplifyMethod::TriangleCount;
    SimplifySettings.TargetCount = TargetTriangleCount;
    Process->UpdateSimplifySettings(SimplifySettings);

    // 执行生成
    return Process->ComputeDerivedSourceData(nullptr);
}
```

**Build.cs 依赖**（如果你的模块需要直接使用这些类型）：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "GeometryCore",
    "DynamicMesh",
    "MeshConversion",
    "MeshDescription",
    "GeometryFlowCore",
    "GeometryFlowMeshProcessing",
});
```

## 模块依赖

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `GeometryProcessing` | 几何处理基础算法 |
| `GeometryFlow` | 计算图框架，用于构建异步网格处理管线 |
| `MeshModelingToolsetExp` | 网格建模工具集（实验版），提供交互式工具基础设施 |
| `EditorScriptingUtilities` | 编辑器脚本工具 |

### 模块依赖（Build.cs）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心模块 |
| `InteractiveToolsFramework` | 交互式工具框架 |
| `GeometryCore` | 几何核心数据结构（DynamicMesh 等） |
| `DynamicMesh` | 动态网格数据类型 |
| `MeshConversion` / `MeshConversionEngineTypes` | MeshDescription ↔ DynamicMesh 转换 |
| `MeshDescription` / `StaticMeshDescription` | 网格描述数据 |
| `ModelingComponents` / `ModelingComponentsEditorOnly` | 建模组件（预览、工具目标等） |
| `MeshModelingToolsExp` | 网格建模工具（实验版） |
| `GeometryFlowCore` / `GeometryFlowMeshProcessing` / `GeometryFlowMeshProcessingEditor` | GeometryFlow 计算图节点 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `UnrealEd` | 编辑器功能 |
| `EditorScriptingUtilities` | 编辑器脚本 |
| `AssetDefinition` | 资产定义系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-18 | `462ec4ed` | Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created and subsequently destroyed. | 静态分析警告修复，非功能性变更 |
| 2025-07-14 | `8c4cad91` | Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors | 引擎级重构，MeshLODToolset 跟随适配 |
| 2025-05-30 | `8396b185` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars | DLL 导出宏修正，非功能性变更 |

### 维护评价

- **创建时间**：2020-11-24（从 Experimental 分支创建），已存在约 5.4 年
- **最近更新**：最近 3 次提交均为引擎级适配和代码质量修复，**无功能性更新**
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion=true`，`Hidden=true`，始终未毕业为正式功能
- **活跃度**：修改基本由引擎重构驱动（如 WITH_EDITORONLY_DATA 访问器重构、DLL 导出修复），非插件自身功能迭代
- **风险**：作为 Hidden Beta 插件，Epic 可能在未来版本中移除或大幅重构

**综合评价**：⚠️ **维护不活跃的 Beta 插件**。虽然仍能正常编译，但功能层面已长期无更新。如果你需要 AutoLOD 功能，建议优先考虑 UE5 内置的 Nanite 和 HLOD 方案，或者使用 Mesh Reduction 工具。此插件适合需要精细控制 LOD 生成管线（如自定义体素化、烘焙法线/纹理）的高级场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MeshLODToolset)
- [官方文档]()（无）
- [测试用例]()（Plugin 目录内未发现独立测试文件）
