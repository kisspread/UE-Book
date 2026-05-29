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
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ProceduralMeshComponent) | |

## 用途

此插件提供 `UProceduralMeshComponent` 类及其配套工具库，允许开发者在**运行时**或**编辑器**中，通过代码或蓝图**程序化地生成和修改网格几何体**。与功能更复杂、数据结构更庞大的 `UStaticMesh` 或 `URuntimeMeshComponent` 相比，本插件更轻量，主要面向**快速原型开发、动态地形生成、建筑系统以及需要频繁更新网格拓扑的场景**。它解决了在游戏运行时动态创建3D模型（如地形、建筑、工具生成的形状）的核心需求。

## 使用场景

- 你在开发一个需要**动态生成地形**的游戏，地形形状由代码实时计算得出。
- 你需要一个**建筑建造系统**，允许玩家在游戏中放置墙体、地板等基础网格构件。
- 游戏包含**物理破坏系统**，需要在物体被破坏后生成碎片网格。
- 你需要从程序化数据（如噪声、点云）中快速生成3D可视化模型。
- 在快速原型阶段，你需要不依赖外部建模工具就能创建临时性的3D几何体。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Mesh Section` | 创建一个新的网格段，并填充顶点、三角形等基础数据。 | `UProceduralMeshComponent` |
| `Update Mesh Section` | 动态更新已有网格段的顶点位置、法线、UV等数据，无需重建三角形。 | `UProceduralMeshComponent` |
| `Clear All Mesh Sections` | 清除组件上所有的网格段，清空几何体。 | `UProceduralMeshComponent` |
| `Set Mesh Section Visible` | 设置特定网格段的可见性。 | `UProceduralMeshComponent` |
| `Set Proc Mesh Material` | 为指定的网格段设置材质。 | `UProceduralMeshComponent` |
| `Get Proc Mesh Section` | 获取指定网格段的详细几何数据（顶点、三角形等），用于后续修改。 | `UProceduralMeshComponent` |
| `Add Collision Convex Mesh` | 为程序化网格添加一个凸包碰撞体。 | `UProceduralMeshComponent` |

### 使用示例（蓝图描述）

要生成一个简单的平面：
1. 创建一个 `UProceduralMeshComponent` 并添加到 Actor。
2. 构造顶点数组（`Vertices`），例如四个角点。
3. 构造三角形索引数组（`Triangles`），定义两个三角形（6个索引）。
4. 构造UV坐标数组（`UVs`）。
5. （可选）构造法线数组（`Normals`）。
6. 调用 `Create Mesh Section` 节点，将 Section Index 设为 0，并将上述数组连入对应的输入引脚。
7. 调用 `Set Proc Mesh Material` 为该 Section 指定一个材质。

要动态更新网格（例如让平面波浪起伏）：
1. 获取当前顶点数据：使用 `Get Proc Mesh Section`。
2. 在蓝图中循环修改顶点数组中每个点的 Z 坐标（根据时间等计算）。
3. 调用 `Update Mesh Section` 节点，传入修改后的顶点数组和相同的 Section Index。

## C++ 用法

### 头文件引入

```cpp
#include "ProceduralMeshComponent.h"
```

### 基本用法

创建并填充一个网格段。
```cpp
// 在 Actor 的 .cpp 文件中
#include "ProceduralMeshComponent.h"

void AMyProceduralActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建或获取 ProceduralMeshComponent
    ProceduralMeshComp = NewObject<UProceduralMeshComponent>(this);
    ProceduralMeshComp->RegisterComponent();
    ProceduralMeshComp->AttachToComponent(GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);

    // 定义几何数据
    TArray<FVector> Vertices;
    Vertices.Add(FVector(0.f, 0.f, 0.f));
    Vertices.Add(FVector(100.f, 0.f, 0.f));
    Vertices.Add(FVector(100.f, 100.f, 0.f));
    Vertices.Add(FVector(0.f, 100.f, 0.f));

    TArray<int32> Triangles;
    Triangles.Append({0, 1, 2, 0, 2, 3});

    TArray<FVector> Normals;
    Normals.Append({FVector::UpVector, FVector::UpVector, FVector::UpVector, FVector::UpVector});

    TArray<FVector2D> UVs;
    UVs.Append({FVector2D(0,0), FVector2D(1,0), FVector2D(1,1), FVector2D(0,1)});

    TArray<FColor> VertexColors;
    VertexColors.Append({FColor::White, FColor::White, FColor::White, FColor::White});

    TArray<FProcMeshTangent> Tangents;
    Tangents.Append({FProcMeshTangent(FVector::ForwardVector, false), ...});

    // 创建网格段
    ProceduralMeshComp->CreateMeshSection(0, Vertices, Triangles, Normals, UVs, VertexColors, Tangents, true);

    // 设置材质 (假设已有 MaterialInstance)
    ProceduralMeshComp->SetMaterial(0, MyMaterialInstance);
}
```

### 进阶用法

动态更新网格顶点。
```cpp
// 修改网格，例如让顶点随时间上下移动
void AMyProceduralActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (ProceduralMeshComp && ProceduralMeshComp->GetNumSections() > 0)
    {
        // 获取当前网格段数据
        FProcMeshSection* Section = ProceduralMeshComp->GetProcMeshSection(0);
        if (Section && Section->ProcVertexBuffer.Num() > 0)
        {
            // 复制并修改顶点
            TArray<FVector> NewVertices;
            NewVertices.Reserve(Section->ProcVertexBuffer.Num());
            for (const FProcMeshVertex& Vertex : Section->ProcVertexBuffer)
            {
                FVector NewPos = Vertex.Position;
                NewPos.Z += FMath::Sin(GetGameTimeSinceCreation() * 2.0f) * 10.0f; // 简单的正弦波动
                NewVertices.Add(NewPos);
            }

            // 更新网格段 (只更新顶点位置，其他数据如法线、UV不变，因此传入空数组或原数据)
            // 注意：直接修改顶点会改变法线，更合理的做法是同时更新法线。
            ProceduralMeshComp->UpdateMeshSection(0, NewVertices, Section->ProcVertexBuffer[0].Normal, ...);
        }
    }
}
```

## Demo 示例

一个在 Actor 中生成并动态更新程序化平面的完整示例。

```cpp
// MyProceduralActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyProceduralActor.generated.h"

class UProceduralMeshComponent;

UCLASS()
class MYPROJECT_API AMyProceduralActor : public AActor
{
    GENERATED_BODY()

public:
    AMyProceduralActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY(VisibleAnywhere)
    UProceduralMeshComponent* ProceduralMeshComp;

    void GenerateSimplePlane();
    void UpdateWaves();
};
```

```cpp
// MyProceduralActor.cpp
#include "MyProceduralActor.h"
#include "ProceduralMeshComponent.h"

AMyProceduralActor::AMyProceduralActor()
{
    PrimaryActorTick.bCanEverTick = true;
    ProceduralMeshComp = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("ProceduralMesh"));
    RootComponent = ProceduralMeshComp;
}

void AMyProceduralActor::BeginPlay()
{
    Super::BeginPlay();
    GenerateSimplePlane();
}

void AMyProceduralActor::GenerateSimplePlane()
{
    TArray<FVector> Vertices;
    TArray<int32> Triangles;
    TArray<FVector> Normals;
    TArray<FVector2D> UVs;
    TArray<FColor> VertexColors;
    TArray<FProcMeshTangent> Tangents;

    // 生成一个 10x10 的网格平面
    const int32 GridSize = 10;
    const float Spacing = 100.0f;

    for (int32 y = 0; y <= GridSize; ++y)
    {
        for (int32 x = 0; x <= GridSize; ++x)
        {
            Vertices.Add(FVector(x * Spacing, y * Spacing, 0.0f));
            UVs.Add(FVector2D(x / (float)GridSize, y / (float)GridSize));
            Normals.Add(FVector::UpVector);
            VertexColors.Add(FColor::White);
            Tangents.Add(FProcMeshTangent(FVector::ForwardVector, false));
        }
    }

    for (int32 y = 0; y < GridSize; ++y)
    {
        for (int32 x = 0; x < GridSize; ++x)
        {
            int32 BottomLeft = y * (GridSize + 1) + x;
            int32 BottomRight = BottomLeft + 1;
            int32 TopLeft = BottomLeft + (GridSize + 1);
            int32 TopRight = TopLeft + 1;

            Triangles.Append({BottomLeft, TopLeft, TopRight, BottomLeft, TopRight, BottomRight});
        }
    }

    ProceduralMeshComp->CreateMeshSection(0, Vertices, Triangles, Normals, UVs, VertexColors, Tangents, true);

    // 设置一个基础材质
    static ConstructorHelpers::FObjectFinder<UMaterial> MaterialFinder(TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    if (MaterialFinder.Succeeded())
    {
        ProceduralMeshComp->SetMaterial(0, MaterialFinder.Object);
    }
}

void AMyProceduralActor::UpdateWaves()
{
    FProcMeshSection* Section = ProceduralMeshComp->GetProcMeshSection(0);
    if (!Section) return;

    const int32 GridSize = 10; // 必须与 GenerateSimplePlane 中一致
    TArray<FVector> NewVertices;
    NewVertices.Reserve(Section->ProcVertexBuffer.Num());

    float Time = GetGameTimeSinceCreation();

    for (int32 i = 0; i < Section->ProcVertexBuffer.Num(); ++i)
    {
        FVector OriginalPos = Section->ProcVertexBuffer[i].Position;
        // 基于网格索引和时间创建波浪效果
        int32 X = i % (GridSize + 1);
        int32 Y = i / (GridSize + 1);
        float Z = FMath::Sin((X * 0.5f + Time) * 0.5f) * FMath::Cos((Y * 0.5f + Time * 0.3f) * 0.5f) * 50.0f;

        NewVertices.Add(FVector(OriginalPos.X, OriginalPos.Y, Z));
    }

    // 更新网格段顶点
    ProceduralMeshComp->UpdateMeshSection(0, NewVertices, {}, {}, {}, {}, {});
}

void AMyProceduralActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    UpdateWaves();
}
```

## 模块依赖

从 `Build.cs` 分析，使用此插件时，你的模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 提供基础几何算法和数据结构支持。 |
| `MeshConversion` | 用于将程序化网格数据转换为引擎内部格式。 |
| `PhysicsCore` | 用于为程序化网格生成和管理物理碰撞体。 |

*注：插件自身依赖更多模块，如 `RenderCore`, `RHI` 等，但这些是图形渲染的核心，通常无需用户直接管理。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧式 `UE_LOG` 迁移到新的 `UE_LOGF` 格式。 |
| 2026-02-06 | `af701dad` | [HWRT] Deprecate public FRayTracingGeometry Initializer. | 废弃了 `FRayTracingGeometry` 的一个公共初始化接口。 |
| 2025-10-03 | `6089b974` | ProceduralMeshComponent: Fix SliceProceduralMesh using incorrect normal in presence of non-uniform scale. | 修复了在非均匀缩放下，`SliceProceduralMesh` 函数使用错误法线的 Bug。 |
| 2025-08-26 | `ce867df3` | [HWRT] Refactored FRayTracingInstanceCollector to handle multiple views instead of a single reference. | 重构了硬件光线追踪实例收集器以支持多视图。 |
| 2025-07-14 | `8c4cad91` | - Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors, and a few changes to ... | 调整了 `StaticMesh` 中编辑器专属数据的属性访问方式，可能影响相关编辑器工具。 |

### 维护评价

- **创建时间**: 2015年，是一个非常成熟的插件。
- **活跃度**: 截至2026年4月仍有更新。更新内容显示它仍在跟随引擎的核心渲染（如硬件光线追踪）和日志系统进行适配与维护，同时修复了特定功能（如切片）的 Bug。
- **状态**: **仍在积极维护的成熟插件**。它作为引擎原生的一部分，随着引擎版本迭代而更新，保证了兼容性。
- **推荐**: **强烈推荐使用**。对于标准的程序化网格生成需求，它是引擎官方提供的、稳定且高效的选择。虽然创建时间早，但持续的维护证明其仍有价值。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ProceduralMeshComponent)