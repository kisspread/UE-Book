# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 软体模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（物理资产） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 是 Unreal Engine Chaos 物理系统中的**软体物理模拟插件**，用于模拟可变形的有机材质（如肉、肌肉组织、橡胶等）。

该插件的核心是基于**四面体网格（Tetrahedral Mesh）**的体积物理表示，相比传统三角形表面网格，能够：

- **内部体积建模**：通过四面体元素填充物体内部，支持体积保持和内部结构模拟
- **软体变形**：模拟物体受力后的弹性变形、撕裂、破碎效果
- **纤维场生成**：支持材质内部纤维方向定义，用于更真实的肌肉模拟
- **与 Chaos 物理系统集成**：利用 Chaos 的并行求解器进行高性能物理计算

插件设计了清晰的继承层次：`FGeometryCollection` → `FTetrahedralCollection` → `FFleshCollection`，逐步扩展四面体网格和软体物理属性。

## 使用场景

- **角色受击效果**：子弹击中角色时产生肉质凹陷和飞溅效果
- **软体破碎**：模拟木头、橡胶等柔性材质的断裂
- **生物组织模拟**：肌肉、脂肪等有机材质的物理表现
- **医疗可视化**：器官、软组织的物理仿真
- **工业仿真**：橡胶制品、软泡沫等材质的力学分析

## 蓝图用法

### 核心节点

该插件主要通过 Dataflow 节点和资产系统使用，核心类为 C++ 运行时接口。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `NewFleshCollection` | 创建软体物理集合 | `FFleshCollection` |
| `NewTetrahedralCollection` | 创建四面体网格集合 | `FTetrahedralCollection` |
| `RadialTetMesh` | 生成径向四面体网格 | `ChaosFlesh` |
| `RadialHexMesh` | 生成径向六面体网格 | `ChaosFlesh` |

## C++ 用法

### 头文件引入

```cpp
#include "ChaosFlesh/FleshCollection.h"
#include "ChaosFlesh/TetrahedralCollection.h"
#include "ChaosFlesh/ChaosFleshCollectionFacade.h"
#include "Meshing/ChaosFleshRadialMeshing.h"
```

### 基本用法 - 创建四面体网格

```cpp
// 定义四面体网格数据
TArray<FVector> Vertices = {
    FVector(0, 0, 0),      // 顶点 0
    FVector(1, 0, 0),      // 顶点 1
    FVector(0.5, 1, 0),    // 顶点 2
    FVector(0.5, 0.5, 1)   // 顶点 3
};

// 四面体元素（4个顶点索引）
TArray<FIntVector4> Elements = {
    FIntVector4(0, 1, 2, 3)  // 一个四面体
};

// 表面三角形（3个顶点索引）
TArray<FIntVector3> SurfaceElements = {
    FIntVector3(0, 1, 2),
    FIntVector3(0, 1, 3),
    FIntVector3(0, 2, 3),
    FIntVector3(1, 2, 3)
};

// 创建四面体集合
TUniquePtr<FTetrahedralCollection> TetCollection(
    FTetrahedralCollection::NewTetrahedralCollection(Vertices, SurfaceElements, Elements));
```

*来源: Public/ChaosFlesh/TetrahedralCollection.h*

### 基本用法 - 创建软体集合

```cpp
// 方法一：从四面体集合转换
TUniquePtr<FTetrahedralCollection> BaseTet = /* ... */;
TUniquePtr<FFleshCollection> FleshCollection(
    FFleshCollection::NewFleshCollection(*BaseTet));

// 方法二：直接从顶点和元素创建
TArray<FVector> Vertices;
TArray<FIntVector4> Elements;
TUniquePtr<FFleshCollection> FleshCollection(
    FFleshCollection::NewFleshCollection(Vertices, Elements));
```

*来源: Public/ChaosFlesh/FleshCollection.h*

### 进阶用法 - 使用 Facade 访问数据

```cpp
// 获取软体集合引用
FFleshCollection* FleshCollection = /* ... */;

// 创建 Facade 进行便捷访问
FFleshCollectionFacade Facade(*FleshCollection);

// 验证数据完整性
if (Facade.IsValid() && Facade.IsTetrahedronValid())
{
    // 获取顶点数量
    int32 NumVerts = Facade.NumVertices();
    
    // 获取组件空间坐标
    TArray<FVector3f> ComponentSpaceVerts;
    Facade.ComponentSpaceVertices(ComponentSpaceVerts);
    
    // 访问全局变换矩阵
    TArray<FTransform> ComponentTransforms;
    Facade.GlobalMatrices(ComponentTransforms);
    
    // 访问四面体数据
    const TManagedArray<FIntVector4>* Tetrahedron = 
        Facade.FindAttribute<FIntVector4>("Tetrahedron", "Tetrahedral");
    
    // 访问质量属性
    const TManagedArray<float>* Mass = 
        Facade.FindAttribute<float>("Mass", "Vertices");
}
```

*来源: Public/ChaosFlesh/ChaosFleshCollectionFacade.h*

### 进阶用法 - 生成程序化网格

```cpp
// 生成径向四面体网格（适合圆柱形软体）
TArray<FIntVector4> TetElements;
TArray<FVector> TetVertices;

RadialTetMesh(
    0.5,           // 内半径
    2.0,           // 外半径
    3.0,           // 高度
    8,             // 径向采样数
    16,            // 角度采样数
    4,             // 垂直采样数
    0.2,           // 膨胀距离
    TetElements,
    TetVertices
);

// 从六面体网格转换为四面体
TArray<FVector> HexVertices;
TArray<int32> HexElements;
TArray<FVector> ConvertedTetVerts;
TArray<FIntVector4> ConvertedTetElements;

RegularHexMesh2TetMesh(HexVertices, HexElements, 
                       ConvertedTetVerts, ConvertedTetElements);
```

*来源: Public/Meshing/ChaosFleshRadialMeshing.h*

## Demo 示例

### 完整的软体物理初始化示例

**FleshSimulation.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ChaosFlesh/FleshCollection.h"
#include "ChaosFlesh/ChaosFleshCollectionFacade.h"

class FFleshSimulationExample
{
public:
    /** 创建一个简单的球形软体 */
    static TUniquePtr<Chaos::FFleshCollection> CreateSphereFlesh(
        float Radius, int32 Subdivisions);
    
    /** 计算表面并初始化物理属性 */
    static void InitializePhysicsProperties(Chaos::FFleshCollection& Collection);

private:
    /** 生成四面体细分 */
    static void SubdivideTetrahedra(
        const TArray<FVector>& InVertices,
        const TArray<FIntVector4>& InElements,
        TArray<FVector>& OutVertices,
        TArray<FIntVector4>& OutElements,
        int32 Levels);
};
```

**FleshSimulation.cpp**
```cpp
#include "FleshSimulationExample.h"
#include "ChaosFlesh/FleshCollectionUtility.h"
#include "Meshing/ChaosFleshRadialMeshing.h"

TUniquePtr<Chaos::FFleshCollection> FFleshSimulationExample::CreateSphereFlesh(
    float Radius, int32 Subdivisions)
{
    // 使用径向网格生成基础几何体
    TArray<FIntVector4> TetElements;
    TArray<FVector> TetVertices;
    
    RadialTetMesh(
        0.0f,                    // 无内腔
        Radius,                  // 外半径
        Radius * 2.0f,           // 高度
        Subdivisions,            // 径向采样
        Subdivisions * 2,        // 角度采样
        Subdivisions,            // 垂直采样
        0.0f,                    // 无膨胀
        TetElements,
        TetVertices
    );
    
    // 计算表面元素
    TArray<FIntVector3> SurfaceElements;
    ChaosFlesh::GetSurfaceElements(TetElements, SurfaceElements, false, false);
    
    // 压缩未使用的顶点
    TArray<FVector3f> CompactVertices;
    TArray<FIntVector3> CompactSurfaces;
    ChaosFlesh::CompactSurfaceVertices(
        reinterpret_cast<const TArray<FVector3f>&>(TetVertices),
        SurfaceElements,
        CompactVertices,
        CompactSurfaces
    );
    
    // 创建软体集合
    return TUniquePtr<Chaos::FFleshCollection>(
        Chaos::FFleshCollection::NewFleshCollection(
            reinterpret_cast<const TArray<FVector>&>(CompactVertices),
            CompactSurfaces,
            TetElements));
}

void FFleshSimulationExample::InitializePhysicsProperties(
    Chaos::FFleshCollection& Collection)
{
    // 使用 Facade 进行属性访问
    Chaos::FFleshCollectionFacade Facade(Collection);
    
    if (!Facade.IsValid())
    {
        UE_LOG(LogChaosFlesh, Error, TEXT("Invalid FleshCollection"));
        return;
    }
    
    // 设置质量属性（基于体积）
    TManagedArray<float>* MassArray = 
        Collection.FindAttribute<float>(
            Chaos::FFleshCollection::MassAttribute,
            TEXT("Vertices"));
    
    if (MassArray)
    {
        float Density = 1050.0f; // kg/m³，约等于人体组织密度
        int32 NumVertices = Facade.NumVertices();
        
        for (int32 i = 0; i < NumVertices; ++i)
        {
            // 简化质量分配：均匀分布
            (*MassArray)[i] = Density / NumVertices;
        }
    }
    
    // 初始化关联元素（每个顶点关联的四面体）
    Collection.InitIncidentElements();
    
    // 更新包围盒
    Collection.UpdateBoundingBox();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryCollectionEngine` | GeometryCollection 基础框架 |
| `Chaos` | Chaos 物理引擎核心 |
| `ChaosSolverEngine` | Chaos 求解器 |
| `DataflowEngine` | Dataflow 节点系统 |
| `FieldSystem` | 物理场系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-12 | `981bc9da` | Dataflow: | Dataflow 节点相关更新 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理纤维场生成节点的代码 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复掩码缓冲区赋值错误 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃软体资产中的 StaticMesh 属性 |

### 维护评价

**活跃维护** ✅

该插件处于**活跃开发阶段**，近期更新频繁（2026 年 5 月有多次提交），主要涉及：

- **功能完善**：Dataflow 节点系统集成、纤维场生成
- **代码质量**：修复编译警告、清理废弃代码
- **API 演进**：正在废弃旧的 StaticMesh 接口，转向专用的软体资产格式

**注意事项**：
- 作为实验性插件（IsExperimentalVersion=true），API 可能会有 breaking changes
- 默认未启用，需要手动在插件管理器中激活
- 目前主要面向研究和高级用户，文档和示例较少

**推荐**：适合需要高级软体物理效果的项目，但需要准备应对 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- 官方文档（暂无）