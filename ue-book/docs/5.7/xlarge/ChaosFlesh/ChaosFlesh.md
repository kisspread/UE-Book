# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 混沌肉体模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产，如骨骼网格体、物理资产配置） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

`ChaosFlesh` 是 Unreal Engine 5 中基于 Chaos 物理系统的软组织模拟插件。它提供了一套数据结构和算法，用于定义、创建和操作可变形人体组织（如肌肉、脂肪、皮肤）的四面体网格模型。

该插件解决了传统骨骼动画无法自然表现物理变形（如肌肉抖动、碰撞挤压）的问题，特别适用于需要高保真角色变形、医学模拟或可破坏软体的场景。核心围绕 `FFleshCollection`（基于四面体网格）和 `FTetrahedralCollection` 构建，支持质量属性、骨骼绑定、碰撞检测等物理交互。

## 使用场景

- **角色肌肉模拟**：为角色添加物理驱动的肌肉系统，实现跑步、跳跃、碰撞时的肌肉颤动和挤压效果。
- **软组织变形**：模拟脂肪、内脏等非刚性组织在受力下的体积保持和动态变形。
- **医学仿真**：用于手术训练或生物力学分析，需要真实软组织行为。
- **可破坏可变形物**：创建易压缩、可撕裂的物体（如海绵、果冻体）并参与物理交互。

## 蓝图用法

`ChaosFlesh` 核心模块（Runtime）主要提供 C++ 数据结构和计算逻辑，并不直接暴露蓝图可调用节点。蓝图集成通过 `ChaosFleshEngine` 模块中的 Actor 组件和 Dataflow 节点实现（详见 ChaosFleshEngine 文档）。以下为相关蓝图可用功能概览：

| 节点（在 ChaosFleshEngine 中） | 说明 | 所在类 |
|---|---|---|
| `Generate Tetrahedral Mesh` | 从静态网格体生成四面体网格 | `UTetrahedralMeshComponent` |
| `Apply Flesh Dynamics` | 激活软组织物理模拟 | `UFleshComponent` |
| `Get Flesh Vertices` | 获取当前帧变形顶点位置 | `UFleshComponent` |

> 详细蓝图节点清单请参考 ChaosFleshEngine 模块文档。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosFlesh/FleshCollection.h"
#include "ChaosFlesh/ChaosFleshCollectionFacade.h"
#include "ChaosFlesh/TetrahedralCollection.h"
#include "ChaosFlesh/FleshCollectionUtility.h"
```

### 基本用法

**创建简单的四面体集合**（来自 `FTetrahedralCollection::NewTetrahedralCollection` 工厂方法）：

```cpp
#include "ChaosFlesh/TetrahedralCollection.h"

// 定义顶点和四面体索引
TArray<FVector> Vertices = {
    FVector(0,0,0),
    FVector(1,0,0),
    FVector(0,1,0),
    FVector(0,0,1)
};
TArray<FIntVector3> SurfaceElements; // 可空
TArray<FIntVector4> Elements = {FIntVector4(0,1,2,3)};

// 创建四面体集合（自动计算表面元素）
FTetrahedralCollection* TetCol = FTetrahedralCollection::NewTetrahedralCollection(Vertices, SurfaceElements, Elements);
```

**使用 Facade 访问和修改集合数据**：

```cpp
#include "ChaosFlesh/ChaosFleshCollectionFacade.h"

FFleshCollection* FleshCol = FFleshCollection::NewFleshCollection(Vertices, SurfaceElements, Elements);
Chaos::FFleshCollectionFacade Facade(*FleshCol);
if (Facade.IsValid() && Facade.IsTetrahedronValid())
{
    // 获取所有顶点（全局坐标）
    TArray<FVector3f> WorldVerts;
    Facade.ComponentSpaceVertices(WorldVerts);
    
    // 修改骨骼名称
    TManagedArray<FString>& BoneNames = Facade.BoneName;
    if (BoneNames.Num() > 0)
    {
        BoneNames[0] = TEXT("Root");
    }
}
```

**从四面体网格提取表面元素**：

```cpp
#include "ChaosFlesh/FleshCollectionUtility.h"

TArray<FIntVector4> Tets = { FIntVector4(0,1,2,3) };
TArray<FIntVector3> SurfaceFaces;
ChaosFlesh::GetSurfaceElements(Tets, SurfaceFaces, /*KeepInteriorFaces*/false, /*InvertFaces*/false);
// SurfaceFaces 包含三个三角形面（假设四面体非退化）
```

### 进阶用法

**创建径向四面体网格**（用于模拟圆柱状软组织，如手臂）：

```cpp
#include "Meshing/ChaosFleshRadialMeshing.h"

TArray<FIntVector4> TetElements;
TArray<FVector> TetVertices;
RadialTetMesh(
    0.5f,           // 内半径
    1.0f,           // 外半径
    3.0f,           // 高度
    4,              // 径向采样
    8,              // 周向采样
    5,              // 垂直采样
    0.0f,           // 凸起距离
    TetElements,
    TetVertices
);

// 用得到的顶点和四面体创建 FFleshCollection
FFleshCollection* FleshCol = FFleshCollection::NewFleshCollection(TetVertices, TetElements);
```

**添加质量属性与骨骼绑定**：

```cpp
// 在 FFleshCollection 上设置顶点质量
FleshCol->Mass.Fill(0.01f); // 每个顶点质量 0.01 单位

// 通过 Facade 操作骨骼层级
TManagedArray<FTransform3f>& Transforms = Facade.Transform;
TManagedArray<int32>& Parents = Facade.Parent;
// 设置根骨骼变换
Transforms[0] = FTransform3f::Identity;
Parents[0] = INDEX_NONE;
```

## Demo 示例

以下是一个完整的 C++ 示例，创建四面体网格并计算其部件空间顶点位置：

**FleshDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "ChaosFlesh/FleshCollection.h"
#include "ChaosFlesh/ChaosFleshCollectionFacade.h"

class FFleshDemo
{
public:
    static void Run();
};
```

**FleshDemo.cpp**
```cpp
#include "FleshDemo.h"
#include "ChaosFlesh/TetrahedralCollection.h"
#include "ChaosFlesh/FleshCollectionUtility.h"

void FFleshDemo::Run()
{
    // 定义一个四面体
    TArray<FVector> Verts = {
        FVector(0,0,0),
        FVector(1,0,0),
        FVector(0,1,0),
        FVector(0,0,1)
    };
    TArray<FIntVector4> Tets = {FIntVector4(0,1,2,3)};
    
    // 创建四面体集合
    TUniquePtr<FTetrahedralCollection> TetCol(
        FTetrahedralCollection::NewTetrahedralCollection(Verts, {}, Tets)
    );
    
    // 升级为 FleshCollection
    TUniquePtr<FFleshCollection> FleshCol(
        FFleshCollection::NewFleshCollection(*TetCol)
    );
    
    // 使用 Facade 访问数据
    Chaos::FFleshCollectionFacade Facade(*FleshCol);
    if (Facade.IsValid())
    {
        // 输出顶点数量和四面体数量
        UE_LOG(LogTemp, Log, TEXT("Vertices: %d, Tets: %d"), 
            Facade.NumVertices(), 
            FleshCol->Tetrahedron.Num());
        
        // 计算部件空间顶点
        TArray<FVector3f> WorldVerts;
        Facade.ComponentSpaceVertices(WorldVerts);
        for (int32 i = 0; i < WorldVerts.Num(); i++)
        {
            UE_LOG(LogTemp, Log, TEXT("Vertex %d: %s"), i, *WorldVerts[i].ToString());
        }
    }
}
```

## 模块依赖

要使用 `ChaosFlesh` 模块，你的模块 `Build.cs` 需添加以下依赖（已省略常见依赖 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `Chaos` | ChaOS 物理引擎核心 |
| `GeometryCollection` | 几何集合数据结构和 ManagedArray 系统 |
| `ChaosFleshEngine` | 提供 Actor 组件和蓝图集成（可选但推荐） |

## 维护状态

### 近期更新

- 2025-10-22 a1039b21 USD: 禁用 Windows 上的 UE 分配器（无关紧要）
- 2025-10-17 be609b71 [Backout] - 撤销某次提交（基础设施）
- 2025-10-17 7ab79237 USD: 禁用 Windows 上的 UE 分配器（重复）
- 2025-10-03 71e223a6 Dataflow: 增加 Dataflow 支持（功能更新）
- 2025-10-01 dca9c2ee 为 Dataflow 编辑器添加隐藏几何缓存属性的方式（功能更新）

### 维护评价

- **创建时间**：2025-10-01（距今约 0 年）
- **近期更新频率**：非常活跃（几乎每周有提交）
- **是否活跃维护**：是，Epic 持续在插件中加入新功能（Dataflow 集成、编辑器扩展）
- **已知问题**：实验性版本，API 可能变化；部分功能待完善（如碰撞检测、材质绑定）
- **推荐使用**：如果项目需要高精度软组织模拟，可以尝试，但需接受不稳定和 API 变动风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/chaos-physics/)（Chaos 物理总览）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh/Tests)（可能包含自动化测试）