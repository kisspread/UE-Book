# Geometry Processing

> Data Structures and Algorithms for Processing 2D and 3D Geometry

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（几何算法、动态网格、网格文件工具） |
| 模块 | `GeometryAlgorithms` (Runtime), `DynamicMesh` (Runtime), `MeshFileUtils` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryProcessing) | |

## 用途

GeometryProcessing 是一个底层的运行时插件，为 Unreal Engine 提供了处理 2D 和 3D 几何图形的核心数据结构和算法库。它不是一个面向最终用户的工具，而是作为其他高级功能（如建模工具、程序化生成、网格修复、几何分析等）的基石。其主要价值在于提供高效、可靠的几何计算原语，例如网格布尔运算、网格简化、空间查询、几何变换等，这些是许多复杂图形和游戏功能的基础。

## 使用场景

-   **程序化内容生成 (PCG)**：你需要动态创建、修改或组合复杂的 3D 网格资产。
-   **网格修复与优化**：你需要清理导入的或程序化生成的网格数据，如修复非流形几何、减少多边形数量、优化 UV 布局。
-   **几何分析**：你需要计算网格的体积、表面积、曲率，或进行碰撞检测、空间查询（如最近点查询）。
-   **自定义建模工具**：你正在开发编辑器内的自定义建模或雕刻工具，需要底层的几何操作支持。
-   **数据转换**：你需要在不同的网格格式（如 OBJ, STL）与引擎内部表示之间进行转换。

## 蓝图用法

此插件主要为 C++ 开发者设计，其核心算法和数据结构通常不直接暴露为蓝图节点。高级功能（如建模工具）会封装这些底层功能并提供蓝图接口。如需在蓝图中使用几何处理功能，通常应使用封装好的上层插件或工具。

## C++ 用法

### 头文件引入

根据你要使用的模块，引入对应的头文件：
```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "GeometryAlgorithms/ConvexHull3.h"
#include "MeshFileUtils/OBJWriter.h"
```

### 基本用法

使用 `DynamicMesh` 模块创建和操作一个简单的网格。
```cpp
// 创建一个动态网格
UE::Geometry::FDynamicMesh3 Mesh;

// 添加顶点
int32 V0 = Mesh.AppendVertex(FVector3d(0, 0, 0));
int32 V1 = Mesh.AppendVertex(FVector3d(100, 0, 0));
int32 V2 = Mesh.AppendVertex(FVector3d(0, 100, 0));

// 添加三角形
Mesh.AppendTriangle(V0, V1, V2);

// 检查网格有效性
bool bIsValid = Mesh.IsCompact(); // 检查是否紧凑（无删除元素）
```

### 进阶用法

结合 `GeometryAlgorithms` 模块计算网格的凸包。
```cpp
#include "GeometryAlgorithms/ConvexHull3.h"

// ... 假设已有一个 FDynamicMesh3 Mesh

// 计算凸包
UE::Geometry::FConvexHull3 ConvexHull;
ConvexHull.Solve(Mesh);
const UE::Geometry::FDynamicMesh3& HullMesh = ConvexHull.GetHull();

// 现在 HullMesh 包含了原始网格的凸包表示
```

## Demo 示例

一个最小示例，演示如何创建一个网格并计算其包围盒。
```cpp
// MyGeometryActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "MyGeometryActor.generated.h"

UCLASS()
class AMyGeometryActor : public AActor
{
    GENERATED_BODY()
public:
    AMyGeometryActor();
    virtual void BeginPlay() override;

private:
    UE::Geometry::FDynamicMesh3 Mesh;
};
```

```cpp
// MyGeometryActor.cpp
#include "MyGeometryActor.h"
#include "DynamicMesh/DynamicMesh3.h"

AMyGeometryActor::AMyGeometryActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyGeometryActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建一个简单的三角形网格
    Mesh.AppendVertex(FVector3d(0, 0, 0));
    Mesh.AppendVertex(FVector3d(100, 0, 0));
    Mesh.AppendVertex(FVector3d(0, 100, 0));
    Mesh.AppendTriangle(0, 1, 2);

    // 计算并打印包围盒
    UE::Geometry::FAxisAlignedBox3d Bounds = Mesh.GetBounds();
    UE_LOG(LogTemp, Log, TEXT("Mesh Bounds: Min=%s, Max=%s"),
        *Bounds.Min.ToString(), *Bounds.Max.ToString());
}
```

## 模块依赖

使用此插件，你的模块通常需要依赖以下模块。具体依赖取决于你使用的功能。

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 插件主模块，聚合依赖 |
| `DynamicMesh` | 核心动态网格数据结构 |
| `GeometryAlgorithms` | 几何算法库（凸包、布尔运算等） |
| `MeshFileUtils` | 网格文件读写工具（OBJ, STL） |

## 维护状态

### 近期更新

（由于创建时间未知，无法提供具体的 git log。此插件作为引擎核心几何处理库，通常随引擎版本同步更新。）

### 维护评价

-   **状态**：**核心基础设施，持续维护**。作为许多高级功能（如建模模式、PCG）的底层依赖，它由 Epic 官方团队维护，更新与引擎版本发布同步。
-   **实验性**：插件标记为 `IsBetaVersion=true`，表明其 API 可能尚未完全稳定，在未来的引擎版本中可能发生变更。
-   **推荐**：**推荐给需要底层几何操作的 C++ 开发者**。对于大多数蓝图用户或只需要高级功能的开发者，建议使用封装好的上层工具（如建模工具插件）。直接使用此插件需要较强的 C++ 和几何算法背景。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryProcessing)
-   [官方文档]() （暂无）
-   [测试用例]() （通常位于 `Engine/Tests/` 目录下，需在源码中查找）