# Dataprep Editor

> A tool to simplify creation and execution of data preparation pipelines from within the Unreal Editor.

| 属性 | 值 |
|---|---|
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `DataprepCore` (Runtime), `DataprepEditor` (Runtime), `DataprepEditorScriptingUtilities` (Runtime), `DataprepLibraries` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-11-22 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor) | |

## 用途

Dataprep Editor 是一个企业级插件，旨在为 Unreal Editor 提供一个可视化的、基于节点的数据准备（Data Preparation）工作流。它解决的核心问题是：在将外部资产（如 CAD、BIM 模型）导入 UE 或进行大规模场景优化时，需要执行一系列重复、复杂的清理、转换和优化操作。该插件允许用户通过创建“数据准备管道”（Dataprep Pipeline）来自动化这些流程，从而提高资产导入和场景准备的效率与一致性。

**DataprepLibraries 模块**是该插件的核心组件库，它提供了大量预制的、可复用的“操作”（Operations）和“选择器”（Fetchers）。这些组件是构建数据准备管道的基本积木，涵盖了从资产属性查询（如获取网格体三角形数、材质信息）到资产修改（如合并网格体、替换材质）的广泛功能。

## 使用场景

- **建筑/工程可视化**：从 Revit、SketchUp 等软件导入大量模型后，需要批量移除隐藏几何体、合并相同材质的网格体、优化 LOD 设置。
- **汽车设计**：导入高精度 CAD 模型后，需要自动简化网格、生成碰撞体、清理冗余的材质实例。
- **游戏开发**：在大型开放世界项目中，需要对从外部购买的资产包进行标准化处理，例如统一命名规范、设置正确的碰撞通道、移除不必要的组件。
- **任何需要批量、自动化处理 UE 资产的场景**。

## 蓝图用法

DataprepLibraries 模块主要提供用于数据准备流程的“Fetcher”（数据获取器）和“Operation”（操作）类。这些类通常在 Dataprep Editor 的节点图中使用，但其基类也支持蓝图扩展。

### 核心节点（Fetcher 示例）

以下 Fetcher 类用于从对象中提取特定信息，常用于数据准备流程中的条件判断和筛选。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Fetch (Bounding Volume)` | 获取对象的包围盒体积。对于 Actor，仅计算启用碰撞的组件。 | `UDataprepFloatBoundingVolumeFetcher` |
| `Fetch (Is Class Of)` | 判断对象是否属于指定的类（可选包含子类）。 | `UDataprepIsClassOfFetcher` |
| `Fetch (Object Name)` | 获取对象的名称（`GetName()`）。 | `UDataprepStringObjectNameFetcher` |
| `Fetch (Actor Label)` | 获取 Actor 的显示标签（`GetActorLabel()`）。 | `UDataprepStringActorLabelFetcher` |
| `Fetch (Triangle Count)` | 获取静态网格体的三角形数量。 | `UDataprepTriangleCountFetcher` |
| `Fetch (Vertex Count)` | 获取静态网格体的顶点数量。 | `UDataprepVertexCountFetcher` |
| `Fetch (Tag Value)` | 获取 Actor 身上所有标签的值（`Tags` 数组）。 | `UDataprepStringActorTagsFetcher` |
| `Fetch (Actor Layer)` | 获取 Actor 所属的图层名称。 | `UDataprepStringActorLayersFetcher` |

### 使用示例（蓝图描述）

在 Dataprep Editor 的节点图中，你可以这样使用一个 Fetcher：

1.  从一个“对象选择器”节点（如“选择所有静态网格体”）的输出引脚，连接到一个 `Fetch (Triangle Count)` 节点的输入。
2.  将 `Fetch (Triangle Count)` 节点的输出（一个整数）连接到一个“条件”节点（如“大于”）的一个输入。
3.  在“条件”节点的另一个输入中设置一个阈值（例如 10000）。
4.  将“条件”节点的布尔输出连接到后续操作的“执行条件”输入。这样，只有三角形数大于 10000 的网格体才会执行后续的优化操作。

## C++ 用法

DataprepLibraries 模块不仅提供蓝图可用的类，还提供了一些用于底层静态网格体操作的 C++ 工具类和函数。

### 头文件引入

```cpp
#include "DataprepOperationsLibraryUtil.h"
```

### 基本用法

以下示例展示了如何使用 `DataprepOperationsLibraryUtil` 命名空间中的工具函数来查询和操作静态网格体。

```cpp
// 来源: Engine/Plugins/Enterprise/DataprepEditor/Source/DataprepLibraries/Public/DataprepOperationsLibraryUtil.h

// 假设你有一个 UObject 数组，可能是从编辑器选择或数据准备流程中获得的
TArray<UObject*> SelectedObjects = ...;

// 1. 获取选中对象引用的所有唯一静态网格体
TSet<UStaticMesh*> Meshes = DataprepOperationsLibraryUtil::GetSelectedMeshes(SelectedObjects);

// 2. 获取这些网格体使用的所有材质
TArray<UMaterialInterface*> Materials = DataprepOperationsLibraryUtil::GetUsedMaterials(SelectedObjects);

// 3. 构建（编译）这些网格体的渲染数据（如果缺失或强制构建）
TArray<UStaticMesh*> BuiltMeshes = DataprepOperationsLibraryUtil::BuildStaticMeshes(Meshes, true /* bForceBuild */);

// 4. 使用作用域编辑器安全地修改网格体材质（避免触发自动构建）
if (UStaticMesh* MyMesh = ...)
{
    // 使用 FScopedStaticMeshEdit 在作用域内临时禁用自动构建
    DataprepOperationsLibraryUtil::FScopedStaticMeshEdit ScopedEdit(MyMesh);
    
    // 安全地设置材质，不会触发 UStaticMesh::Build
    DataprepOperationsLibraryUtil::SetMaterial(MyMesh, 0, NewMaterial);
    
} // ScopedEdit 析构时，会自动恢复网格体的构建设置
```

### 进阶用法

结合多个工具函数，可以实现一个完整的资产处理流程。

```cpp
// 场景：批量替换所有使用特定材质的网格体的该材质
void ReplaceMaterialOnMeshes(const TArray<UObject*>& Objects, UMaterialInterface* OldMaterial, UMaterialInterface* NewMaterial)
{
    // 获取所有相关网格体
    TSet<UStaticMesh*> AllMeshes = DataprepOperationsLibraryUtil::GetSelectedMeshes(Objects);
    
    // 使用 FStaticMeshBuilder 批量开始编辑（内部会处理构建状态）
    DataprepOperationsLibraryUtil::FStaticMeshBuilder MeshBuilder(AllMeshes);
    
    for (UStaticMesh* Mesh : AllMeshes)
    {
        // 遍历网格体的所有材质槽
        for (int32 i = 0; i < Mesh->GetStaticMaterials().Num(); ++i)
        {
            if (Mesh->GetMaterial(i) == OldMaterial)
            {
                // 使用作用域编辑器进行安全修改
                DataprepOperationsLibraryUtil::FScopedStaticMeshEdit ScopedEdit(Mesh);
                DataprepOperationsLibraryUtil::SetMaterial(Mesh, i, NewMaterial);
            }
        }
    }
    // MeshBuilder 析构时，会处理所有网格体的最终构建
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建一个自定义的 Dataprep Fetcher。

```cpp
// MyCustomFetcher.h
#pragma once

#include "SelectionSystem/DataprepStringFetcher.h"
#include "MyCustomFetcher.generated.h"

UCLASS(BlueprintType, NotBlueprintable, Meta = (DisplayName="Custom Asset Path", ToolTip="Fetches the asset path of an object."))
class UMyCustomAssetPathFetcher : public UDataprepStringFetcher
{
    GENERATED_BODY()

public:
    // 实现核心的 Fetch 逻辑
    virtual FString Fetch_Implementation(const UObject* Object, bool& bOutFetchSucceeded) const override
    {
        if (Object)
        {
            bOutFetchSucceeded = true;
            return Object->GetPathName();
        }
        bOutFetchSucceeded = false;
        return FString();
    }

    // 声明此 Fetcher 是线程安全的（如果确实如此）
    virtual bool IsThreadSafe() const override { return true; }

    // 提供在节点图中显示的名称
    virtual FText GetNodeDisplayFetcherName_Implementation() const override
    {
        return NSLOCTEXT("MyFetchers", "AssetPathFetcherName", "Custom Asset Path");
    }
};
```

```cpp
// MyCustomFetcher.cpp
#include "MyCustomFetcher.h"

// 无需额外实现，逻辑已在头文件中。
```

## 模块依赖

要使用 `DataprepLibraries` 模块，你的模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DataprepCore` | Dataprep 插件的核心运行时模块，定义了基础的 Fetcher、Operation 等基类。 |
| `SelectionSystem` | 提供了对象选择和过滤的框架，是 Fetcher 系统的基础。 |

## 维护状态

### 近期更新

```
- 2c158c4d0766 Change GetUsedTextures MaterialInterface to use TOptional parameters instead of Enum+bool pairs OverrideNumericParameterDefault functions refactored into a Set/Clear pair instead of passing a bool #jira UE-297260
- 8c4cad918a59 - Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors, and a few changes to SkeletalMesh to match (like making an accessor for NaniteSettings)
- 9ea3ad2a8d40 Fixed issue with output folder path containing '/' character - Reported by a user on UDN
```

**解读**：
1.  `2c158c4d0766`：对材质接口和参数覆盖函数进行了重构，属于代码质量改进和 API 优化。
2.  `8c4cad918a59`：与引擎核心的 `StaticMesh` 属性访问器重构保持同步，确保插件兼容性。
3.  `9ea3ad2a8d40`：修复了一个用户报告的路径处理 Bug，表明插件仍在接收社区反馈并进行修复。

### 维护评价

- **创建时间**：2019年，已有约5年历史。
- **最近更新**：最近的提交集中在代码重构、兼容性修复和 Bug 修复上，表明插件仍在积极维护中，以适应引擎核心的变化。
- **活跃度**：作为 Epic Games 官方维护的企业级插件，其更新节奏与引擎版本发布周期绑定，属于**稳定维护**状态。
- **已知限制**：该插件默认未启用（`EnabledByDefault: false`），表明它可能针对特定工作流（如建筑可视化、工业设计）优化，并非所有项目都需要。
- **推荐使用**：如果你的项目涉及**大规模、重复性的资产导入和处理流程**，特别是来自 CAD/BIM 等专业软件的数据，那么 Dataprep Editor 及其核心的 DataprepLibraries 模块是一个强大且官方支持的工具，**强烈推荐**。对于简单的游戏资产导入，可能略显复杂。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor)
- 官方文档：暂无公开链接
- 测试用例：暂无公开链接