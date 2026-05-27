# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 混沌软体 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（实验性代码） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 是 Unreal Engine 中 Chaos 物理引擎的一个实验性扩展模块，其核心目的是为游戏和模拟提供基于四面体网格的**可控软体（Flesh）物理**能力。它并非一个独立的物理模拟器，而是 Chaos 物理框架的一部分，专注于处理可变形体（如角色肌肉、果冻、布料等）的体积保持、弹性变形和实时物理反馈。

该插件解决了传统刚体或表面布料模拟无法真实表现的柔软物体变形和次表面细节问题，为需要高级软体交互的项目提供了底层数据结构和物理模拟接口。

## 使用场景

- 你需要实现一个角色在受到冲击时，身体部位（如腹部、脸颊）产生符合物理的凹陷和回弹效果。
- 你正在开发一个需要实时物理交互的果冻或史莱姆类游戏。
- 你需要模拟一个布娃娃在跌落或碰撞时，其内部结构（如肌肉、脂肪）产生形变。
- 你正在研究或开发基于物理的次表面散射（Subsurface Scattering）效果，需要物理模拟驱动表面形变。

## 蓝图用法

根据对 `ChaosFlesh` 核心模块源码的分析，该模块主要提供 C++ 底层数据结构和物理计算接口，**未直接暴露蓝图可调用（BlueprintCallable）的函数**。蓝图层面的节点和可视化脚本集成，很可能封装在 `ChaosFleshNodes` 和 `ChaosFleshEditor` 等其他模块中（当前分析未包含这些模块的头文件）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无） | 本模块（ChaosFlesh）未提供蓝图接口 | - |

## C++ 用法

`ChaosFlesh` 模块的核心是定义了软体物理模拟所需的基础数据结构，如 `FFleshCollection`，以及用于访问和操作这些数据的工具类 `FFleshCollectionFacade`。

### 头文件引入

```cpp
#include "ChaosFlesh/ChaosFlesh.h" // 主模块头文件，引入日志分类
#include "ChaosFlesh/FleshCollection.h" // 核心数据结构
#include "ChaosFlesh/ChaosFleshCollectionFacade.h" // 便捷访问器
#include "ChaosFlesh/TetrahedralCollection.h" // 四面体集合基类
#include "Meshing/ChaosFleshRadialMeshing.h" // 网格生成工具
```

### 基本用法

以下示例展示了如何创建一个 `FFleshCollection` 并填充四面体网格数据，这是使用 ChaosFlesh 进行物理模拟的第一步。

*（来源：`Public/ChaosFlesh/FleshCollection.h`, `Public/ChaosFlesh/TetrahedralCollection.h`）*

```cpp
// 1. 定义一个简单的四面体网格
TArray<FVector> Vertices = {
    FVector(0, 0, 0),
    FVector(100, 0, 0),
    FVector(0, 100, 0),
    FVector(0, 0, 100)
};
TArray<FIntVector4> Elements = {
    FIntVector4(0, 1, 2, 3) // 一个四面体，连接上述四个顶点
};

// 2. 创建 FFleshCollection 实例
// FFleshCollection 继承自 FTetrahedralCollection，后者继承自 FGeometryCollection
Chaos::FFleshCollection* FleshCollection = Chaos::FFleshCollection::NewFleshCollection(
    Vertices,
    Elements,
    true,  // bReverseVertexOrder
    false, // KeepInteriorFaces
    false  // InvertFaces
);

if (FleshCollection)
{
    // 3. 使用 Facade 访问和检查数据
    Chaos::FFleshCollectionFacade Facade(*FleshCollection);
    if (Facade.IsValid())
    {
        UE_LOG(LogChaosFlesh, Log, TEXT("创建了包含 %d 个顶点的 FleshCollection"), Facade.NumVertices());
        // Facade.Vertex -> TManagedArrayAccessor<FVector3f> 可直接访问顶点数据
        const TManagedArray<FVector3f>* Verts = Facade.FindAttribute<FVector3f>("Vertex", "Vertices");
        if (Verts)
        {
            // 操作顶点数据...
        }
    }
}
```

### 进阶用法

结合网格生成工具 `ChaosFleshRadialMeshing`，可以程序化生成复杂的四面体/六面体网格，并将其转换为 `FleshCollection` 所需的格式。

*（来源：`Public/Meshing/ChaosFleshRadialMeshing.h`, `Public/ChaosFlesh/FleshCollection.h`）*

```cpp
// 1. 使用径向网格生成工具创建一个圆柱形的四面体网格
TArray<FIntVector4> TetElements;
TArray<FVector> TetVertices;
RadialTetMesh(
    50.0f, // InnerRadius
    100.0f, // OuterRadius
    200.0f, // Height
    8,      // RadialSample
    16,     // AngularSample
    4,      // VerticalSample
    0.0f,   // BulgeDistance
    TetElements,
    TetVertices
);

// 2. 从生成的四面体数据创建 FFleshCollection
// 由于 RadialTetMesh 只输出四面体元素，没有表面，我们让函数自动计算表面
Chaos::FFleshCollection* ComplexFlesh = Chaos::FFleshCollection::NewFleshCollection(
    TetVertices,
    TetElements,
    true,  // bReverseVertexOrder
    true,  // KeepInteriorFaces: 保留内部面，用于可视化或碰撞
    false  // InvertFaces
);

// 3. 使用 Facade 进行复杂的属性查询和修改
if (ComplexFlesh)
{
    Chaos::FFleshCollectionFacade Facade(*ComplexFlesh);
    // 获取所有顶点在组件空间的位置
    TArray<FVector3f> ComponentSpaceVerts;
    Facade.ComponentSpaceVertices(ComponentSpaceVerts);
    
    // 检查数据完整性
    if (Facade.IsTetrahedronValid() && Facade.IsHierarchyValid())
    {
        // 数据可用于物理模拟或渲染
    }
}
```

## Demo 示例

以下是一个完整的、可编译的最小 C++ 示例，演示如何创建和操作一个 `FFleshCollection`。

**FleshDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

// 前置声明
namespace Chaos { class FFleshCollection; }

class FFleshDemo
{
public:
    static void CreateAndInspectFlesh();
};
```

**FleshDemo.cpp**
```cpp
#include "FleshDemo.h"
#include "ChaosFlesh/FleshCollection.h"
#include "ChaosFlesh/ChaosFleshCollectionFacade.h"
#include "ChaosFlesh/ChaosFlesh.h"

void FFleshDemo::CreateAndInspectFlesh()
{
    // 1. 准备一个八面体的顶点和四面体数据（两个金字塔拼接）
    TArray<FVector> Vertices;
    Vertices.Add(FVector(0, 0, 50)); // 顶部
    Vertices.Add(FVector(50, 0, 0)); // 右前
    Vertices.Add(FVector(0, 50, 0)); // 左后
    Vertices.Add(FVector(-50, 0, 0)); // 左前
    Vertices.Add(FVector(0, -50, 0)); // 右后
    Vertices.Add(FVector(0, 0, -50)); // 底部

    TArray<FIntVector4> Elements;
    // 上半部
    Elements.Add(FIntVector4(0, 1, 2, 5));
    Elements.Add(FIntVector4(0, 2, 3, 5));
    Elements.Add(FIntVector4(0, 3, 4, 5));
    Elements.Add(FIntVector4(0, 4, 1, 5));

    // 2. 创建 FleshCollection
    Chaos::FFleshCollection* DemoCollection = Chaos::FFleshCollection::NewFleshCollection(
        Vertices,
        Elements,
        true,
        false,
        false
    );

    if (!DemoCollection)
    {
        UE_LOG(LogChaosFlesh, Error, TEXT("创建 FleshCollection 失败"));
        return;
    }

    // 3. 使用 Facade 检查
    Chaos::FFleshCollectionFacade Facade(*DemoCollection);
    UE_LOG(LogChaosFlesh, Log, TEXT("--- FleshCollection 创建成功 ---"));
    UE_LOG(LogChaosFlesh, Log, TEXT("有效性检查: %s"), Facade.IsValid() ? TEXT("通过") : TEXT("失败"));
    UE_LOG(LogChaosFlesh, Log, TEXT("顶点数: %d"), Facade.NumVertices());
    UE_LOG(LogChaosFlesh, Log, TEXT("面数: %d"), Facade.NumFaces());
    UE_LOG(LogChaosFlesh, Log, TEXT("几何体数: %d"), Facade.NumGeometry());

    // 4. 可以在此处将 DemoCollection 传递给物理模拟系统或渲染器

    // 注意：实际使用中，FleshCollection 的生命周期管理需要根据上下文决定（如由资产或组件持有）。
    // 在此演示中，我们创建后仅用于检查，不进行销毁。
}
```

## 模块依赖

要使用 `ChaosFlesh` 模块，你的项目模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心模块 |
| `ChaosSolverEngine` | Chaos 求解器引擎 |
| `GeometryCollectionEngine` | 几何集合引擎，`FFleshCollection` 的基类 `FGeometryCollection` 所在模块 |
| `ChaosFlesh` | （目标模块本身） |
| `GeometryCollectionCore` | 几何集合核心数据类型 |

*（注：已省略 Core, CoreUObject, Engine 等几乎每个插件都依赖的常见模块）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-12 | `981bc9da` | Dataflow: | Dataflow（数据流）相关更新。 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理了用于生成纤维场的 Dataflow 节点。 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复从 OffsetsBuffer 到 MaskBuffer 的 NumMaskBuffer 赋值错误。 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃了 Flesh 资产上的 StaticMesh 属性。 |

### 维护评价

- **创建时间**：约 4 年前（2022-03-26）。
- **最近更新频率**：近期（2026-05月）有连续的提交，说明仍在积极开发中。
- **维护状态**：**活跃维护中**。从最近的提交记录看，团队正在持续修复问题、清理代码、重构节点（如废弃旧属性）并集成 Dataflow 系统。
- **已知问题/限制**：该插件仍标记为 `Experimental`（实验性）且 `EnabledByDefault=false`，表明其 API 和功能可能尚未稳定，不建议用于生产环境。需要手动在插件设置中启用。
- **推荐**：如果你是 UE 物理开发的研究者或需要早期探索 Chaos 软体模拟，可以启用并研究。对于商业项目，建议等待其转为正式支持或评估其他成熟方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- 官方文档：（无）
- 测试用例：（当前分析未提供具体测试文件路径）