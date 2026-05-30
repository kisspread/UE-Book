# Geometry Processing

> Data Structures and Algorithms for Processing 2D and 3D Geometry（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 几何处理 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `GeometryAlgorithms` (Runtime), `DynamicMesh` (Runtime), `MeshFileUtils` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-26 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryProcessing) | |

## 用途

Geometry Processing 插件是 UE5 中处理 2D 和 3D 几何数据的核心底层库。它解决的核心问题是为引擎和编辑器工具提供一套高性能、可扩展的几何数据结构（如 `FDynamicMesh3`）和算法（如网格简化、布尔运算、空间查询、几何优化）。该插件是 **MeshModelingToolset** 等高级建模工具和 **Procedural Content Generation (PCG)** 框架等系统的基石，提供了它们所需的底层几何操作能力。

## 使用场景

- **程序化内容生成 (PCG)**：在运行时或编辑器中动态创建和修改网格体，例如地形、建筑构件等，需要用到 `DynamicMesh` 模块进行高效网格构建和操作。
- **优化关卡或资产**：使用 `GeometryAlgorithms` 中的算法对导入的静态网格进行简化、重拓扑、UV 展开或修复非流形几何，以提升渲染性能和物理模拟效率。
- **自定义建模工具开发**：基于 `FDynamicMesh3` 和相关算法构建自定义的几何操作节点或编辑器工具，实现特定的几何变换、分析或修复逻辑。
- **几何文件处理**：使用 `MeshFileUtils` 模块进行网格文件的导入/导出（支持 OBJ, STL 等格式），或进行网格数据的序列化。

## 蓝图用法

该插件主要面向 C++ 和编辑器工具开发，直接暴露给蓝图的高级接口较少。核心交互通常通过封装了此插件功能的更上层模块（如 ModelingToolsEditorMode）或 C++ 接口进行。

## C++ 用法

该插件主要为其他引擎模块和插件提供底层支持，使用者通常是其他插件的开发者。

### 头文件引入

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/MeshTransforms.h"
#include "Util/ProgressCancel.h"
```

### 基本用法 (DynamicMesh 创建与操作)

```cpp
// 来源：Engine/Plugins/Runtime/GeometryProcessing/Source/DynamicMesh/Private/DynamicMeshAttribute.cpp 相关测试推导
using namespace UE::Geometry;

// 1. 创建一个空的动态网格
FDynamicMesh3 Mesh;

// 2. 添加顶点
int32 V0 = Mesh.AppendVertex(FVector3d(0, 0, 0));
int32 V1 = Mesh.AppendVertex(FVector3d(100, 0, 0));
int32 V2 = Mesh.AppendVertex(FVector3d(0, 100, 0));

// 3. 添加三角形
int32 TriangleID = Mesh.AppendTriangle(V0, V1, V2);

// 4. 检查三角形是否有效
if (Mesh.IsTriangle(TriangleID))
{
    // 获取三角形顶点
    FIndex3i TriVerts = Mesh.GetTriangle(TriangleID);
    // ...
}
```

### 进阶用法 (几何算法应用)

```cpp
// 来源：Engine/Plugins/Runtime/GeometryProcessing/Source/GeometryAlgorithms/Private/Intersection/IntersectionUtil.cpp 相关逻辑
#include "Spatial/PointSetHashTable.h"
#include "Util/IndexUtil.h"

// 使用空间哈希表加速最近点查询
TPointSetHashTable3d PointHash;
PointHash.Initialize(Vertices, 0.1f); // 初始化，0.1为单元格大小

// 查找点 (50,50,50) 附近的最近点索引
FVector3d QueryPoint(50, 50, 50);
int32 NearestIdx = -1;
float MaxDist = 10.0f;
PointHash.FindNearestInRadius(QueryPoint, MaxDist, NearestIdx);
```

## Demo 示例

```cpp
// MyGeometryActor.h
#pragma once
#include "CoreMinimal.h"
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
    UE::Geometry::FDynamicMesh3 DynamicMesh;
};

// MyGeometryActor.cpp
#include "MyGeometryActor.h"
#include "DynamicMesh/MeshTransforms.h"

AMyGeometryActor::AMyGeometryActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyGeometryActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建一个简单的立方体动态网格
    DynamicMesh.Clear();
    FVector3d Verts[8] = {
        FVector3d(-50,-50,-50), FVector3d(50,-50,-50),
        FVector3d(50,50,-50), FVector3d(-50,50,-50),
        FVector3d(-50,-50,50), FVector3d(50,-50,50),
        FVector3d(50,50,50), FVector3d(-50,50,50)
    };
    for (const FVector3d& V : Verts) DynamicMesh.AppendVertex(V);

    // 添加12个三角形构成一个立方体（此处省略具体添加代码）
    // ...

    // 对网格应用一个变换
    UE::Geometry::FTransformSRT3d Transform(FRotator3d(45, 0, 0), FVector3d(100, 0, 0));
    UE::Geometry::MeshTransforms::ApplyTransform(DynamicMesh, Transform);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshConversion` | 在 `FDynamicMesh3` 与 `FMeshDescription` / `UStaticMesh` 之间进行转换 |
| `MeshDescription` | UE 的标准网格描述格式，是与引擎资产交互的桥梁 |
| `MeshUtilitiesCommon` | 网格处理相关的通用工具和类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `35f4c4a4` | Fix float overflow warning for arm64 build | 修复在ARM64架构编译时的浮点数溢出警告 |
| 2026-05-15 | `35f66cf1` | Guard against INDEX_NONE / invalid edge id in hole fill util's fill color method | 在孔洞填充工具的颜色填充方法中增加对无效边ID的防护 |
| 2026-05-13 | `2c7d172e` | Clamp UV values to max float when invalid value is in returned as double (max double). | 当UV值以双精度（最大double值）返回时，将其钳制到单精度最大值，防止溢出 |
| 2026-05-12 | `64deb517` | Hook up AttributeAwareV2 simplifier in MeshTerrainStaticMeshTransformer | 在网格地形静态网格变换器中启用AttributeAwareV2简化器 |
| 2026-05-12 | `68fbe22e` | [SkeletalMeshModelingTools] clamp smooth strength to 0 - 1 | [骨骼网格建模工具] 将平滑强度钳制在0-1之间 |

### 维护评价

- **创建时间**：约5年前（2021年）。
- **近期更新**：最近更新非常频繁（2026年5月），且提交内容均为**实质性bug修复、算法优化和功能适配**，而非简单的编译修复。
- **活跃状态**：**活跃维护中**。作为引擎核心的底层几何库，持续有新的功能集成（如新的简化算法）和问题修复。
- **已知限制**：标记为 `IsBetaVersion`，意味着API可能在未来有变动，但鉴于其已被广泛使用，核心结构已趋于稳定。
- **推荐使用**：**强烈推荐**。对于需要直接进行底层网格操作的C++开发者或插件开发者，这是必备且可靠的工具集。对于蓝图开发者，建议通过上层工具或插件间接使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryProcessing)
- [DynamicMesh 模块文档](DynamicMesh.md)
- [GeometryAlgorithms 模块文档](GeometryAlgorithms.md)
- [MeshFileUtils 模块文档](MeshFileUtils.md)