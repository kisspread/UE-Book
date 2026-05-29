# Procedural Mesh Component

> A renderable component and library of utilities for creating and modifying mesh geometry procedurally.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化网格组件 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ProceduralMeshComponent` (Runtime), `ProceduralMeshComponentEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2015-04-17 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ProceduralMeshComponent) | |

## 用途

此插件提供 `UProceduralMeshComponent`，用于在运行时完全通过代码或蓝图构建、修改和优化网格（Mesh）几何体。它解决的核心问题是：当游戏内容需要根据逻辑动态生成（而非预先制作）时，为开发者提供一种直接、高效地创建三维模型的底层工具。它比使用 `UStaticMesh` 更灵活，因为所有顶点、法线、UV、颜色和三角形索引都可由程序实时控制。

## 使用场景

- **动态地形与环境生成**：在程序化生成的关卡（如洞穴、随机地形）中，实时创建匹配玩法逻辑的网格。
- **建造与编辑系统**：允许玩家或系统在游戏内动态拼接、修改结构（如《我的世界》风格的游戏），并立即生成对应碰撞体。
- **程序化资产**：创建独特的、由算法生成的模型，例如低面风格的生物、建筑或载具。
- **可变形物体**：在物理模拟或交互中，实时修改网格顶点以实现“橡皮泥”或破碎效果。

## 蓝图用法

详细 API 请参阅各模块文档，以下为核心功能节点概览。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Mesh Section` | 使用顶点、三角形、法线等数组数据创建一个新的网格段。 | `UProceduralMeshComponent` |
| `Update Mesh Section` | 更新一个已有网格段的顶点等数据，支持仅更新位置以提高性能。 | `UProceduralMeshComponent` |
| `Clear Mesh Section` | 清除指定索引的网格段。 | `UProceduralMeshComponent` |
| `Set Mesh Section Visible` | 控制某个网格段的可见性。 | `UProceduralMeshComponent` |

### 使用示例（蓝图描述）

1. 向 Actor 添加一个 `ProceduralMeshComponent`。
2. 准备数据：在蓝图中构建 `Vertices`（顶点位置）、`Triangles`（三角形索引）、`Normals` 等数组。通常以三个索引描述一个三角形面。
3. 调用 `Create Mesh Section` 节点，将上述数组填入对应输入引脚（如 `Section Index` 设为 0，`Vertices` 填入位置数组，`Triangles` 填入索引数组）。
4. （可选）设置 `Create Collision` 为 true 以自动生成碰撞。
5. 运行游戏，组件将根据你提供的数据渲染出三维模型。

## C++ 用法

核心类是 `UProceduralMeshComponent`，其功能通过特定方法暴露给 C++。

### 头文件引入

```cpp
#include "ProceduralMeshComponent.h"
```

### 基本用法

创建并填充一个简单的网格平面。
（来源参考：测试用例思想）

```cpp
// 在 Actor 的 BeginPlay 中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建动态组件
    UProceduralMeshComponent* ProcMeshComp = NewObject<UProceduralMeshComponent>(this);
    ProcMeshComp->RegisterComponent();

    // 定义数据：一个由两个三角形组成的四边形
    TArray<FVector> Vertices;
    Vertices.Add(FVector(0, 0, 0));
    Vertices.Add(FVector(100, 0, 0));
    Vertices.Add(FVector(100, 100, 0));
    Vertices.Add(FVector(0, 100, 0));

    TArray<int32> Triangles;
    Triangles.Add(0); Triangles.Add(1); Triangles.Add(2); // 三角形 1
    Triangles.Add(0); Triangles.Add(2); Triangles.Add(3); // 三角形 2

    // 创建网格段
    ProcMeshComp->CreateMeshSection(0, Vertices, Triangles, TArray<FVector>(), TArray<FVector2D>(), TArray<FColor>(), TArray<FProcMeshTangent>(), true);
}
```

### 进阶用法

动态更新网格（如实现水面波纹）。
（来源参考：测试用例思想）

```cpp
// 假设 ProcMeshComp 和初始的 Vertices 数组已经存在
void AMyActor::UpdateWave()
{
    static float Time = 0.0f;
    Time += GetWorld()->GetDeltaSeconds();

    // 修改顶点Z坐标产生波纹效果
    for (FVector& Vertex : Vertices)
    {
        Vertex.Z = FMath::Sin(Time * 2.0f + Vertex.X * 0.1f) * 20.0f;
    }

    // 高效更新：仅更新顶点位置，不重建索引、法线等
    TArray<FVector> EmptyNormals;
    TArray<FColor> EmptyColors;
    ProcMeshComp->UpdateMeshSection(0, Vertices, EmptyNormals, TArray<FVector2D>(), EmptyColors);
}
```

## Demo 示例

一个生成静态网格的最小 Actor 示例。
```cpp
// MyProcMeshActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyProcMeshActor.generated.h"

class UProceduralMeshComponent;

UCLASS()
class AMyProcMeshActor : public AActor
{
    GENERATED_BODY()
public:
    AMyProcMeshActor();
protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    UProceduralMeshComponent* ProcMesh;
};

// MyProcMeshActor.cpp
#include "MyProcMeshActor.h"
#include "ProceduralMeshComponent.h"

AMyProcMeshActor::AMyProcMeshActor()
{
    PrimaryActorTick.bCanEverTick = false;
    ProcMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("ProcMesh"));
    RootComponent = ProcMesh;
}

void AMyProcMeshActor::BeginPlay()
{
    Super::BeginPlay();

    TArray<FVector> Vertices = {
        FVector(0, 0, 0), FVector(100, 0, 0),
        FVector(100, 100, 0), FVector(0, 100, 0)
    };
    TArray<int32> Triangles = {0, 1, 2, 0, 2, 3};

    ProcMesh->CreateMeshSection(0, Vertices, Triangles, {}, {}, {}, {}, true);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PhysicsCore` | （Runtime 模块可能依赖）用于创建物理资产和碰撞形状。 |

*注：其他依赖如 Core, CoreUObject, Engine, RenderCore 等均为标准依赖，故省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新宏。 |
| 2026-02-06 | `af701dad` | [HWRT] Deprecate public FRayTracingGeometry Initializer. | 弃用公共的光线追踪几何初始化器。 |
| 2025-10-03 | `6089b974` | ProceduralMeshComponent: Fix SliceProceduralMesh using incorrect normal in presence of non-uniform s... | 修复在非均匀缩放时切片网格使用错误法线的 Bug。 |
| 2025-08-26 | `ce867df3` | [HWRT] Refactored FRayTracingInstanceCollector to handle multiple views instead of a single referenc... | 重构光线追踪实例收集器以支持多视图。 |
| 2025-07-14 | `8c4cad91` | - Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors, and a few changes to ... | 为StaticMesh的编辑器专用属性添加访问器。 |

### 维护评价

**评级：维护中**

ProceduralMeshComponent 是一个历史悠久的“文物级”插件（11年），但作为运行时程序化生成网格的核心工具，它仍然被广泛使用和维护。从近期提交看，维护活动持续存在，但主要集中在底层引擎重构（如光线追踪子系统变更）、小Bug修复和编译器/日志现代化上，而非添加新功能。这表明该插件功能已经稳定成熟。**由于其底层渲染结构相对固定，且新的 Mesh Description API 可能提供更优的方案，此插件对于新项目可能并非首选，但对于已有项目和特定需求（如简单快速的程序化网格生成）依然是可靠的选择。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ProceduralMeshComponent)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Tests/RuntimeTests/ProceduralMeshComponent)
- [模块文档：ProceduralMeshComponent](ProceduralMeshComponent.md)
- [模块文档：ProceduralMeshComponentEditor](ProceduralMeshComponentEditor.md)