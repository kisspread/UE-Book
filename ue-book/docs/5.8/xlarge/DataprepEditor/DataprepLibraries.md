# Dataprep Editor

> A tool to simplify creation and execution of data preparation pipelines from within the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 数据准备库 |
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataprepCore` (Runtime), `DataprepEditor` (Runtime), `DataprepEditorScriptingUtilities` (Runtime), `DataprepLibraries` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-11-22 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor) | |

## 用途

Dataprep Editor 插件是一个面向企业/大规模项目的资产管理与优化工具。它并非一个简单的编辑器扩展，而是一个**可编程、可复用的数据处理流水线框架**。它解决的核心问题是：如何在将外部资产（如从 CAD、BIM 软件通过 Datasmith 导入的原始数据）正式用于项目前，通过一系列可配置、可回溯的“操作步骤”（Operations）自动清理、优化、转换这些数据。

这个插件存在的意义在于将复杂且重复的资产预处理工作（如面数优化、碰撞体设置、材质替换、场景图清理）从手动的、易出错的编辑器操作，转变为一个可保存、可分享、可批量执行的“配方”（Dataprep Asset）。这极大地提高了工作流效率和数据一致性。

**核心功能模块：**
1.  **DataprepCore**: 定义数据准备流水线的核心框架，包括 `UDataprepOperation` 基类、`UDataprepAsset`（保存流水线配方的资产）等。
2.  **DataprepEditor**: 提供用于创建和编辑这些数据准备配方的专用编辑器界面。
3.  **DataprepLibraries**: **本模块**。提供了大量的、开箱即用的 `UDataprepOperation` 实现和 `UBlueprintFunctionLibrary` 工具函数，涵盖了网格、材质、碰撞、LOD、场景图等多方面的常见操作。
4.  **DataprepEditorScriptingUtilities**: 为蓝图或 Python 脚本提供额外的编辑器交互工具。

## 使用场景

-   **建筑/工程可视化 (AEC)**：从 Revit、ArchiCAD 等软件导入大型 BIM 模型后，自动简化模型、合并构件、设置合适的碰撞体和 LOD。
-   **汽车设计**：处理从 CATIA、Alias 导入的高精度 CAD 模型，自动生成简化版的碰撞网格、统一命名规范、批量替换材质。
-   **游戏关卡设计 (AAA)**：在将外部艺术家提供的大型场景资产合入项目前，执行标准化处理流程，如清除冗余数据、优化纹理尺寸、为所有静态网格生成 Nanite 数据。
-   **任何需要批量、标准化处理导入资产的流程**。

## 蓝图用法

`DataprepLibraries` 模块提供了两个主要的蓝图函数库：`UDataprepOperationsLibrary` 用于操作，`UDataprepFilterLibrary` 用于筛选。这些函数是 Dataprep 流水线中“操作”步骤的基石，也可以在独立的蓝图中调用。

### 核心节点 - 操作 (`UDataprepOperationsLibrary`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLods` | 为一组静态网格生成并设置 LOD | `UDataprepOperationsLibrary` |
| `SetSimpleCollision` | 为静态网格设置简单碰撞体（如盒体、球体） | `UDataprepOperationsLibrary` |
| `SetConvexDecompositionCollision` | 为静态网格设置凸分解碰撞体 | `UDataprepOperationsLibrary` |
| `SubstituteMaterial` | 在指定对象中查找并替换材质 | `UDataprepOperationsLibrary` |
| `SubstituteMaterialsByTable` | 使用数据表批量替换材质 | `UDataprepOperationsLibrary` |
| `SetMaterial` | 将指定材质应用到所有输入对象的网格元素 | `UDataprepOperationsLibrary` |
| `SetMobility` | 设置静态网格 Actor 的移动性（静态/可移动等） | `UDataprepOperationsLibrary` |
| `SetMesh` | 将输入 Actor 的静态网格组件替换为指定的网格 | `UDataprepOperationsLibrary` |
| `SubstituteMesh` | 在指定对象中查找并替换静态网格 | `UDataprepOperationsLibrary` |
| `AddTags` | 为 Actor 添加标签 | `UDataprepOperationsLibrary` |
| `AddMetadata` | 为支持资产用户数据的对象添加元数据 | `UDataprepOperationsLibrary` |
| `ConsolidateObjects` | 合并资产引用，用列表中的第一个资产替换后续所有资产的引用 | `UDataprepOperationsLibrary` |
| `RandomizeTransform` | 随机偏移 Actor 的变换（位置、旋转、缩放） | `UDataprepOperationsLibrary` |
| `FlipFaces` | 翻转静态网格的面 | `UDataprepOperationsLibrary` |
| `SetSubOuputLevel` | 为 Actor 设置输出子级别名称（用于场景分层输出） | `UDataprepOperationsLibrary` |
| `SetSubOuputFolder` | 为资产设置输出子文件夹路径 | `UDataprepOperationsLibrary` |
| `AddToLayer` | 将 Actor 添加到指定的编辑器层 | `UDataprepOperationsLibrary` |
| `SetCollisionComplexity` | 设置网格的碰撞复杂度 | `UDataprepOperationsLibrary` |
| `ResizeTextures` | 调整纹理尺寸（可强制为2的幂） | `UDataprepOperationsLibrary` |
| `SetNaniteSettings` | 设置网格的 Nanite 设置 | `UDataprepOperationsLibrary` |
| `SetLODGroup` | 为网格应用预设的 LOD 组 | `UDataprepOperationsLibrary` |

### 核心节点 - 筛选 (`UDataprepFilterLibrary`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FilterByClass` | 按对象类型筛选 | `UDataprepFilterLibrary` |
| `FilterByName` | 按对象名称筛选（支持通配符） | `UDataprepFilterLibrary` |
| `FilterBySize` | 按对象的包围盒体积筛选 | `UDataprepFilterLibrary` |
| `FilterByTag` | 按 Actor 标签筛选 | `UDataprepFilterLibrary` |

### 使用示例（蓝图描述）

1.  **批量设置碰撞体**：
    在一个蓝图函数中，首先使用 `FilterByClass` 从一组导入的对象中筛选出所有 `StaticMesh`。然后将结果连入 `SetSimpleCollision` 节点的 `SelectedObjects` 引脚，并在 `ShapeType` 参数中选择 `EScriptCollisionShapeType::Box`。执行后，所有选中的网格都会被设置为盒体碰撞。

2.  **创建材质替换规则**：
    在一个自定义的 `DataprepOperation` 蓝图中，重写 `OnExecution` 事件。在其中使用 `SubstituteMaterial` 节点，将 `MaterialSearch` 设为 `"*Glass*"`，`StringMatch` 设为 `Contains`，并指定一个新的玻璃材质 `MaterialSubstitute`。这样，执行此操作时，所有名称中包含“Glass”的材质都会被替换。

## C++ 用法

### 头文件引入

要使用 `DataprepLibraries` 模块提供的工具函数，需要包含对应的头文件。

```cpp
#include "DataprepOperationsLibrary.h"
#include "DataprepOperationsLibraryUtil.h"
```

### 基本用法

`UDataprepOperationsLibrary` 提供的函数是静态的，可以直接调用，非常适合在自定义的 `UDataprepOperation` 子类中使用。

**示例1：在自定义操作中调用库函数** (来源: 模拟 `UDataprepSetLODsOperation::OnExecution_Implementation`)
```cpp
#include "DataprepOperationsLibrary.h"
#include "UDataprepAsset.h" // 假设的资产头文件

void UMyCustomDataprepOperation::OnExecution_Implementation(const FDataprepContext& InContext)
{
    // 从上下文中获取要处理的对象列表（通常由流水线上游的筛选器提供）
    TArray<UObject*> ObjectsToProcess = InContext.GetObjects();

    // 创建输出数组，用于记录哪些对象被修改
    TArray<UObject*> ModifiedObjects;

    // 准备LOD设置
    FStaticMeshReductionOptions ReductionOptions;
    // ... 配置 ReductionOptions ...

    // 调用库函数，为所有对象生成LOD
    UDataprepOperationsLibrary::SetLods(ObjectsToProcess, ReductionOptions, ModifiedObjects);

    // 可选：在流水线日志中记录被修改的对象
    // UE_LOG(LogDataprep, Log, TEXT("Modified %d objects."), ModifiedObjects.Num());
}
```

**示例2：使用工具函数获取网格和材质** (来源: `DataprepOperationsLibraryUtil.h`)
```cpp
#include "DataprepOperationsLibraryUtil.h"

void AnalyzeSceneAssets(const TArray<UObject*>& SelectedObjects)
{
    // 从混合对象列表中提取出所有唯一的静态网格（包括 Actor 引用的）
    TSet<UStaticMesh*> UniqueMeshes = DataprepOperationsLibraryUtil::GetSelectedMeshes(SelectedObjects);
    UE_LOG(LogTemp, Log, TEXT("Found %d unique static meshes."), UniqueMeshes.Num());

    // 获取这些对象使用的所有材质
    TArray<UMaterialInterface*> UsedMaterials = DataprepOperationsLibraryUtil::GetUsedMaterials(SelectedObjects);
    UE_LOG(LogTemp, Log, TEXT("Found %d materials in use."), UsedMaterials.Num());
}
```

### 进阶用法

**使用 RAII 工具类进行安全的网格编辑** (来源: `DataprepOperationsLibraryUtil.h`)
直接修改网格资源（如材质槽、LOD）可能会触发自动重新构建，导致意外的性能开销或副作用。`DataprepOperationsLibraryUtil` 提供了 RAII 风格的辅助类来管理这个过程。

```cpp
#include "DataprepOperationsLibraryUtil.h"

void SafeMaterialAssignment(UStaticMesh* MyMesh, int32 MaterialIndex, UMaterialInterface* NewMaterial)
{
    // 方法1：使用 FScopedStaticMeshEdit (推荐)
    // 在此作用域内，网格的自动构建被暂时禁用。
    {
        DataprepOperationsLibraryUtil::FScopedStaticMeshEdit EditGuard(MyMesh);
        // 安全地设置材质，不会触发 MeshBuild
        DataprepOperationsLibraryUtil::SetMaterial(MyMesh, MaterialIndex, NewMaterial);
        // 退出作用域后，EditGuard 的析构函数会恢复网格的构建设置。
    }

    // 方法2：批量构建一组网格
    TSet<UStaticMesh*> MeshesToBuild;
    // ... 向 MeshesToBuild 中添加多个网格 ...
    
    // 生成一个新的构建器，它会在析构时自动调用 BuildStaticMeshes
    DataprepOperationsLibraryUtil::FStaticMeshBuilder MeshBuilder(MeshesToBuild);
    
    // 对 MeshesToBuild 中的网格进行一系列修改...
    // 例如：调用上面的 SafeMaterialAssignment 循环处理多个网格...
    
    // MeshBuilder 在此作用域结束时自动构建所有网格。
}
```

## Demo 示例

以下是一个最小的自定义 `DataprepOperation` 示例，演示如何组合使用 `DataprepLibraries` 中的筛选和操作函数。

**MyOptimizationOperation.h**
```cpp
#pragma once
#include "DataprepOperation.h"
#include "MyOptimizationOperation.generated.h"

UCLASS(Category = ObjectOperation, Meta = (DisplayName = "Optimize Large Meshes", ToolTip = "Simplify meshes larger than a threshold and set simple collision"))
class UMyOptimizationOperation : public UDataprepOperation
{
    GENERATED_BODY()

public:
    UMyOptimizationOperation();

    // 指定体积阈值（单位：立方厘米）
    UPROPERTY(EditAnywhere, Category = Settings, meta = (UIMin = "10000"))
    float VolumeThresholdCm3 = 100000.0f;

protected:
    virtual void OnExecution_Implementation(const FDataprepContext& InContext) override;
};
```

**MyOptimizationOperation.cpp**
```cpp
#include "MyOptimizationOperation.h"
#include "DataprepOperationsLibrary.h"
#include "DataprepFilterLibrary.h"

UMyOptimizationOperation::UMyOptimizationOperation()
{
}

void UMyOptimizationOperation::OnExecution_Implementation(const FDataprepContext& InContext)
{
    // 1. 获取上下文中所有对象
    TArray<UObject*> AllObjects = InContext.GetObjects();

    // 2. 使用过滤器筛选出体积大于阈值的对象
    TArray<UObject*> LargeObjects = UDataprepFilterLibrary::FilterBySize(
        AllObjects,
        EDataprepSizeSource::BoundingBoxVolume,
        EDataprepSizeFilterMode::BiggerThan,
        VolumeThresholdCm3
    );

    if (LargeObjects.Num() == 0)
    {
        return; // 没有需要处理的对象
    }

    // 3. 对这些大对象执行操作序列
    TArray<UObject*> ModifiedObjects;

    // 3a. 生成LOD
    FStaticMeshReductionOptions LODOptions;
    // 简化配置：保留50%面数，生成一级LOD
    LODOptions.ReductionSettings.Add(FStaticMeshReductionOptions::FLODLevelSettings(0.5f, 0.5f));
    UDataprepOperationsLibrary::SetLods(LargeObjects, LODOptions, ModifiedObjects);

    // 3b. 设置盒体碰撞（假设针对的是网格或包含网格的Actor）
    UDataprepOperationsLibrary::SetSimpleCollision(
        ModifiedObjects, // 使用上一步可能修改过的对象
        EScriptCollisionShapeType::Box,
        ModifiedObjects
    );

    UE_LOG(LogTemp, Log, TEXT("Optimized %d large objects."), ModifiedObjects.Num());
}
```

## 模块依赖

要在你的模块中使用 `DataprepLibraries` 的功能（例如，调用 `UDataprepOperationsLibrary` 中的函数），你的模块需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `DataprepCore` | 定义 `UDataprepOperation`, `FDataprepContext` 等核心基类和结构体。 |
| `DataprepLibraries` | 本模块，包含具体的库函数和操作实现。 |
| `EditorScriptingUtilities` | 提供 `EEditorScriptingStringMatchType` 等编辑器脚本工具类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 UE_LOG 迁移为新式 UE_LOGF。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 废弃了接受 `bIncludeNestedObjects` 布尔参数的 `GetObjects*/ForEachObjectWithOuter` 函数。 |
| 2026-03-23 | `42dfe52f` | -Consolidate PreviewFeatureLevelChanged and PreviewPlatformChanged into a single PreviewShaderPlatfo... | 将预览特性级别和预览平台变更合并为单一的预览着色器平台变更事件。 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now... | 移除受 `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5` 保护的包含文件。删除现已无用的头文件。 |

### 维护评价

该插件**创建于2019年**，是 Epic 为解决特定行业（AEC/制造）需求而开发的成熟工具。
- **近期活动**：最近的提交（截至2026年）均为**维护性更新**，包括代码清理、日志迁移、废弃API标记、编译警告修复等，没有引入重大的新功能。
- **活跃度**：**维护不活跃**。它已经是一个功能完整且稳定的产品，处于“仅维护”状态，主要目标是确保与新版引擎的兼容性并清理技术债务。
- **推荐度**：**推荐使用**，特别是对于需要标准化处理大量导入资产的企业或大型项目。尽管没有活跃的功能开发，但其核心功能（数据准备流水线）稳定可靠。对于新的、小规模的独立游戏项目，其学习曲线和设置成本可能较高，需根据实际需求权衡。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/dataprep-in-unreal-engine/)（通用Dataprep文档，非特定于此库模块）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor/Tests)（如有）