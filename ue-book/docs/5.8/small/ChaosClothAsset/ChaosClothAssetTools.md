# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Dataflow 图） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

`ChaosClothAsset` 是一个基于 Chaos 物理引擎的布料资产系统，旨在替代旧的 `ClothingAsset` 工作流。它解决了传统布料系统功能有限、难以与编辑器深度集成的问题。该插件提供了一个以物理模拟为核心的、使用 `Dataflow` 图进行程序化驱动的布料资产格式，支持从传统布料资产迁移，并为角色装备实时布料效果提供了一个现代化、功能更丰富的解决方案。

## 使用场景

-   你正在为角色开发真实的、物理驱动的布料、旗帜或飘带效果。
-   你需要使用节点图（Dataflow）程序化地定义和调整布料的模拟参数，而非仅依赖静态属性设置。
-   你需要将旧的、基于 `ClothingAsset` 的布料资产迁移到新的、更强大的 `ChaosClothAsset` 格式。
-   你需要一个功能完善的布料资产编辑器，支持缩略图渲染、预览和转换工具。

## 蓝图用法

该插件的蓝图节点主要集中在 `ChaosClothAssetTools` 模块中，用于资产转换和网格操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Convert` | 将布料资产的单个图案或整个资产转换为动态网格（`FDynamicMesh3`）。 | `FClothPatternToDynamicMesh` |
| `CreateClothAssetFromTemplate` | 从指定的 Dataflow 模板路径创建一个新的布料资产。 | `UChaosClothAssetFactory` |

### 使用示例（蓝图描述）

1.  **获取并转换布料资产网格**：你有一个 `UChaosClothAsset` 对象（例如，通过资产引用获取）。创建一个 `FClothPatternToDynamicMesh` 对象，并调用其 `Convert` 函数，传入布料资产、LOD索引、图案索引以及一个用于输出的 `FDynamicMesh3` 变量。转换完成后，你可以在编辑器或运行时对这个动态网格进行进一步处理或可视化。
2.  **程序化创建布料资产**：在编辑器工具或数据管线蓝图中，调用 `UChaosClothAssetFactory` 的静态函数 `CreateClothAssetFromTemplate`，指定目标包路径、资产名称以及一个 Dataflow 模板资产的路径，即可在无用户交互的情况下批量创建布料资产。

## C++ 用法

### 头文件引入

```cpp
#include “ChaosClothAsset/ClothPatternToDynamicMesh.h”
#include “ChaosClothAsset/ClothAssetFactory.h”
```

### 基本用法

从公开头文件中提取的典型用法，用于将布料资产转换为可操作的网格数据。

```cpp
// 假设已拥有一个 UChaosClothAsset* ClothAsset
using namespace UE::Chaos::ClothAsset;

// 创建转换器
FClothPatternToDynamicMesh Converter;
UE::Geometry::FDynamicMesh3 ResultMesh;

// 将布料资产的 LOD 0 的 Sim3D 顶点数据转换为动态网格
Converter.Convert(ClothAsset, 0, INDEX_NONE, EClothPatternVertexType::Sim3D, ResultMesh);

// 现在可以对 ResultMesh 进行操作，例如应用修改、导出或生成几何体
```
*来源: `ChaosClothAssetTools` 模块公开头文件*

### 进阶用法

结合 `FClothPatternToDynamicMeshMappingSupport` 进行更精细的控制，例如获取原始顶点索引。

```cpp
using namespace UE::Chaos::ClothAsset;

FClothPatternToDynamicMesh Converter;
UE::Geometry::FDynamicMesh3 ResultMesh;

// 转换一个特定的 SimPattern，并获取映射信息
Converter.Convert(ClothCollection, 0, EClothPatternVertexType::Sim2D, ResultMesh);

// 创建映射支持对象
FClothPatternToDynamicMeshMappingSupport MappingSupport(ResultMesh);

// 查询结果网格中某个顶点（vid）对应的原始顶点索引
int32 OriginalVid = MappingSupport.GetOriginalVertexID(vid);
```
*来源: `ChaosClothAssetTools` 模块 `ClothPatternToDynamicMeshMappingSupport.h`*

## Demo 示例

一个在运行时将布料资产转换为动态网格并进行简单操作的 C++ 示例。

```cpp
// MyClothProcessor.h
#pragma once
#include “CoreMinimal.h”
#include “ChaosClothAsset/ClothPatternToDynamicMesh.h”

class UChaosClothAsset;

class FMyClothProcessor
{
public:
    void ProcessClothAsset(UChaosClothAsset* InClothAsset);
    const UE::Geometry::FDynamicMesh3& GetProcessedMesh() const { return ProcessedMesh; }

private:
    UE::Geometry::FDynamicMesh3 ProcessedMesh;
};

// MyClothProcessor.cpp
#include “MyClothProcessor.h”
#include “ChaosClothAsset/ClothAsset.h”

void FMyClothProcessor::ProcessClothAsset(UChaosClothAsset* InClothAsset)
{
    if (!InClothAsset) return;

    UE::Chaos::ClothAsset::FClothPatternToDynamicMesh Converter;
    // 转换整个资产的渲染顶点数据
    Converter.Convert(InClothAsset, 0, INDEX_NONE, UE::Chaos::ClothAsset::EClothPatternVertexType::Render, ProcessedMesh);

    UE_LOG(LogTemp, Log, TEXT(“Processed cloth asset. Resulting mesh has %d vertices and %d triangles.”),
        ProcessedMesh.VertexCount(), ProcessedMesh.TriangleCount());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | 提供底层的 Chaos 布料模拟运行时和组件 |
| `Dataflow` | 支持基于节点图的布料资产定义和程序化工作流 |
| `GeometryFramework` | 用于 `FDynamicMesh3` 数据结构和相关操作 |
| `SkeletalMeshConversion` | 用于 `ChaosClothAssetTools` 中布料资产与骨骼网格体之间的转换 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Bluepri | 修复蓝图中布料组件的模拟和资产属性跨帧保留问题 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 优化并行布料模拟的等待点，提升性能 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为基于骨骼网格体的布料资产实现骨骼映射刷新功能 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 修复编辑器中复制/粘贴 Actor 后资产别名不更新的问题 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理和整理布料资产转换器代码 |

### 维护评价

`ChaosClothAsset` 是一个相对较新的插件（约 2 年），处于从 **Beta** 向正式版本过渡的阶段。根据近期的 Git 记录，该插件正在被**积极维护**，几乎每天都有提交，内容涉及功能实现（如骨骼映射刷新）、性能优化（并行模拟）和关键问题修复（蓝图属性保留）。插件默认禁用（`EnabledByDefault = false`），符合其实验性质。尽管仍在完善中，但其活跃的开发节奏和解决实际问题的更新内容表明它是一个**推荐关注和使用的插件**，尤其对于需要高级布料物理功能的项目。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset/Tests)