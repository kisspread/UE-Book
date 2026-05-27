# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 肉体模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、网格模板） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 是基于 Chaos 物理引擎的**软体/肉体物理模拟**插件。它使用四面体网格（Tetrahedral Mesh）来表示可变形的三维物体，实现肌肉、软组织等有机物体的物理模拟效果。

核心概念：
- **四面体化（Tetrahedralization）**：将表面网格转化为由四面体单元组成的体积网格，这是有限元方法（FEM）的基础数据结构
- **FleshCollection**：基于 GeometryCollection 扩展的数据容器，存储顶点、表面三角形、内部四面体、质量等物理属性
- **面片网格生成**：提供径向四面体/六面体网格生成工具，用于程序化创建可模拟的肉体几何体

与传统刚体模拟不同，ChaosFlesh 专注于**可变形体**的物理表现——物体在受力后会发生形变而不是保持刚性。

## 使用场景

- 你需要模拟角色的**肌肉变形**效果（如战斗中受到打击时的身体形变）
- 你在制作需要**软体物理**的物体（如果冻、内脏等有机物）
- 你需要基于**有限元方法**的物理模拟来实现可变形物体
- 你要程序化生成四面体网格用于物理模拟

## 蓝图用法

当前 `ChaosFlesh` 核心模块的公共头文件中未暴露 `BlueprintCallable` 函数。蓝图节点功能主要分布在以下子模块中：

| 子模块 | 预期功能 |
|---|---|
| `ChaosFleshNodes` | Dataflow 蓝图节点（肉体模拟相关） |
| `ChaosFleshDeprecatedNodes` | 已废弃的蓝图节点 |
| `ChaosFleshEditor` | 编辑器工具节点 |

### 核心概念（蓝图层面）

通过 Dataflow 图表进行肉体模拟配置，主要包括：
- 纤维场（Fiber Field）生成节点
- 静态网格到肉体资产的转换

## C++ 用法

### 头文件引入

```cpp
#include "ChaosFlesh/ChaosFleshCollectionFacade.h"
#include "ChaosFlesh/TetrahedralCollection.h"
#include "ChaosFlesh/FleshCollection.h"
```

### 基本用法 — 创建四面体集合

从顶点和四面体元素创建一个基础的四面体网格。

```cpp
// 来源: Public/ChaosFlesh/TetrahedralCollection.h
#include "ChaosFlesh/TetrahedralCollection.h"

// 定义顶点和四面体单元
TArray<FVector> Vertices = {
    FVector(0, 0, 0),
    FVector(1, 0, 0),
    FVector(0, 1, 0),
    FVector(0, 0, 1)
};

// 表面三角形（表面网格）
TArray<FIntVector3> SurfaceElements = {
    FIntVector3(0, 1, 2),
    FIntVector3(0, 1, 3),
    FIntVector3(0, 2, 3),
    FIntVector3(1, 2, 3)
};

// 四面体单元（体积网格）
TArray<FIntVector4> Elements = {
    FIntVector4(0, 1, 2, 3)
};

// 创建四面体集合
FTetrahedralCollection* TetCollection = FTetrahedralCollection::NewTetrahedralCollection(
    Vertices, SurfaceElements, Elements, true /*bReverseVertexOrder*/
);

// 初始化关联元素（每个顶点关联的四面体列表）
TetCollection->InitIncidentElements();
```

### 基本用法 — 创建 FleshCollection

`FFleshCollection` 继承自 `FTetrahedralCollection`，添加了物理模拟所需的额外属性（如质量）。

```cpp
// 来源: Public/ChaosFlesh/FleshCollection.h
#include "ChaosFlesh/FleshCollection.h"

// 方式1：从现有的 TetrahedralCollection 创建
FFleshCollection* Flesh = FFleshCollection::NewFleshCollection(*TetCollection);

// 方式2：直接从顶点和四面体创建
FFleshCollection* Flesh = FFleshCollection::NewFleshCollection(
    Vertices, SurfaceElements, Elements
);

// 方式3：仅从顶点和四面体创建，自动生成表面
FFleshCollection* Flesh = FFleshCollection::NewFleshCollection(
    Vertices, Elements,
    true  /*bReverseVertexOrder*/,
    false /*KeepInteriorFaces*/,
    false /*InvertFaces*/
);
```

### 进阶用法 — Facade 模式访问属性

`FFleshCollectionFacade` 提供了便捷的接口来读取和修改集合中的各种属性。

```cpp
// 来源: Public/ChaosFlesh/ChaosFleshCollectionFacade.h
#include "ChaosFlesh/ChaosFleshCollectionFacade.h"

// 创建 Facade 用于便捷访问
Chaos::FFleshCollectionFacade Facade(*Flesh);

if (Facade.IsValid())
{
    // 获取元素数量
    int32 NumTransforms = Facade.NumTransforms();
    int32 NumVertices   = Facade.NumVertices();
    int32 NumFaces      = Facade.NumFaces();
    int32 NumGeometry   = Facade.NumGeometry();

    // 访问顶点数据
    TManagedArrayAccessor<FVector3f>& VertexAccessor = Facade.Vertex;
    
    // 将顶点转换到组件空间
    TArray<FVector3f> ComponentSpaceVerts;
    Facade.ComponentSpaceVertices(ComponentSpaceVerts);

    // 获取全局变换矩阵
    TArray<FTransform> GlobalTransforms;
    Facade.GlobalMatrices(GlobalTransforms);

    // 获取单个全局矩阵
    FTransform3f Matrix = Facade.GlobalMatrix3f(0);

    // 检查特定数据是否有效
    bool bHasTetrahedron = Facade.IsTetrahedronValid();
    bool bHasHierarchy   = Facade.IsHierarchyValid();
    bool bHasGeometry    = Facade.IsGeometryValid();
}
```

### 进阶用法 — 程序化生成网格

使用径向网格生成工具创建四面体或六面体网格。

```cpp
// 来源: Public/Meshing/ChaosFleshRadialMeshing.h
#include "Meshing/ChaosFleshRadialMeshing.h"

// 生成径向四面体网格（如圆柱形物体）
TArray<FIntVector4> TetElements;
TArray<FVector> TetVertices;
RadialTetMesh(
    0.5,   // InnerRadius
    1.0,   // OuterRadius
    2.0,   // Height
    4,     // RadialSample
    8,     // AngularSample
    4,     // VerticalSample
    0.1,   // BulgeDistance
    TetElements,
    TetVertices
);

// 从生成的网格创建 FleshCollection
FFleshCollection* Flesh = FFleshCollection::NewFleshCollection(
    TetVertices, TetElements
);
```

### 进阶用法 — 表面元素提取

```cpp
// 来源: Public/ChaosFlesh/FleshCollectionUtility.h
#include "ChaosFlesh/FleshCollectionUtility.h"

// 从四面体集合中提取表面三角形
TArray<FIntVector3> SurfaceElements;
ChaosFlesh::GetSurfaceElements(
    TetElements,
    SurfaceElements,
    false /*KeepInteriorFaces*/,
    false /*InvertFaces*/
);

// 压缩表面顶点（移除未使用的顶点）
TArray<FVector3f> CompactVertices;
TArray<FIntVector3> CompactSurface;
TArray<int32> OldToNewMap = ChaosFlesh::CompactSurfaceVertices(
    Vertices, SurfaceElements, CompactVertices, CompactSurface
);
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何创建并验证一个简单的肉体物理集合。

### FleshDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "FleshDemo.generated.h"

class FFleshCollection;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UFleshDemo : public UActorComponent
{
    GENERATED_BODY()

public:
    UFleshDemo();

    virtual void BeginPlay() override;

    /** 创建一个简单的四面体肉体集合 */
    void CreateSimpleFlesh();

private:
    TUniquePtr<FFleshCollection> FleshData;
};
```

### FleshDemo.cpp

```cpp
#include "FleshDemo.h"

#include "ChaosFlesh/FleshCollection.h"
#include "ChaosFlesh/ChaosFleshCollectionFacade.h"
#include "ChaosFlesh/FleshCollectionUtility.h"
#include "Meshing/ChaosFleshRadialMeshing.h"

DEFINE_LOG_CATEGORY_STATIC(LogFleshDemo, Log, All);

UFleshDemo::UFleshDemo()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UFleshDemo::BeginPlay()
{
    Super::BeginPlay();
    CreateSimpleFlesh();
}

void UFleshDemo::CreateSimpleFlesh()
{
    // 1. 程序化生成一个径向四面体网格
    TArray<FIntVector4> TetElements;
    TArray<FVector> TetVertices;
    RadialTetMesh(
        0.25,   // InnerRadius
        0.5,    // OuterRadius
        1.0,    // Height
        3,      // RadialSample
        6,      // AngularSample
        3,      // VerticalSample
        0.05,   // BulgeDistance
        TetElements,
        TetVertices
    );

    // 2. 提取表面三角形
    TArray<FIntVector3> SurfaceElements;
    ChaosFlesh::GetSurfaceElements(TetElements, SurfaceElements, false);

    // 3. 创建 FleshCollection
    FFleshCollection* RawFlesh = FFleshCollection::NewFleshCollection(
        TetVertices, SurfaceElements, TetElements
    );

    if (!RawFlesh)
    {
        UE_LOG(LogFleshDemo, Error, TEXT("Failed to create FleshCollection"));
        return;
    }

    FleshData = TUniquePtr<FFleshCollection>(RawFlesh);

    // 4. 通过 Facade 验证数据
    Chaos::FFleshCollectionFacade Facade(*FleshData);

    UE_LOG(LogFleshDemo, Log, TEXT("Flesh created: %d vertices, %d faces, %d geometry"),
        Facade.NumVertices(),
        Facade.NumFaces(),
        Facade.NumGeometry()
    );

    if (Facade.IsTetrahedronValid())
    {
        UE_LOG(LogFleshDemo, Log, TEXT("Tetrahedral data is valid"));
    }

    // 5. 获取组件空间顶点用于后续处理
    TArray<FVector3f> ComponentSpaceVerts;
    Facade.ComponentSpaceVertices(ComponentSpaceVerts);
    UE_LOG(LogFleshDemo, Log, TEXT("Component space vertices: %d"),
        ComponentSpaceVerts.Num());
}
```

## 模块依赖

由于 Build.cs 未提供详细内容，以下基于源码推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心（FChaosArchive 等） |
| `GeometryCollectionEngine` | 几何体集合基础（FGeometryCollection 基类） |
| `GeometryCollectionCore` | 几何体集合核心数据结构 |
| `ChaosSolverEngine` | Chaos 求解器 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度截断为单精度的编译警告 |
| 2026-05-12 | `981bc9da` | Dataflow: | Dataflow 相关更新 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 纤维场生成节点代码清理 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复 MaskBuffer 的 NumMaskBuffer 赋值问题 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃 Flesh 资产中的 StaticMesh 属性 |

### 维护评价

- **状态**：🟢 活跃维护中
- **创建时间**：2022 年 3 月，至今约 4 年
- **更新频率**：非常活跃，最近一次更新仅在 1 天前（2026-05-13），多为功能改进和 Bug 修复
- **实验性标记**：仍标记为 `IsExperimentalVersion: true`，API 可能在未来版本中发生变化
- **已知注意事项**：
  - 需要手动启用（`EnabledByDefault: false`）
  - 正在废弃 StaticMesh 属性，转向新的资产格式
  - 属于 Chaos 物理生态的一部分，需要 Chaos 模块支持
- **推荐使用**：适合需要软体物理模拟的项目。由于仍为实验性版本，**生产环境使用需谨慎**，建议关注 API 变更。适合研究原型和实验性项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- 官方文档：无
- [FleshCollection 源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFlesh/Public/ChaosFlesh/FleshCollection.h)
- [TetrahedralCollection 源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFlesh/Public/ChaosFlesh/TetrahedralCollection.h)
- [Meshing 工具源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFlesh/Public/Meshing/ChaosFleshRadialMeshing.h)