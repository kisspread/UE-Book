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

该插件提供了一个运行时可渲染的组件 `UProceduralMeshComponent`，以及一系列蓝图和C++工具函数（`UKismetProceduralMeshLibrary`）。它解决的核心问题是：在游戏运行时，通过代码或蓝图动态地创建、修改和显示 3D 网格几何体，而无需依赖预先在编辑器中建模的静态网格体（StaticMesh）资产。

它特别适用于那些形状需要根据程序逻辑、用户输入或实时数据发生变化的场景，例如生成地形、可破坏的环境或动态物体。组件支持多网格段（Section）、碰撞生成、UV 和法线计算等关键功能。

## 使用场景

-   **程序化生成内容**：运行时生成地形、洞穴、随机地图或程序化建筑，例如 Minecraft 风格的体素世界。
-   **可破坏环境**：当物体被破坏时，使用 `SliceProceduralMesh` 函数将其切割成两半，并生成新的网格体。
-   **动态修改网格**：需要实时变形或更新顶点位置、颜色、UV 的场景，如水面波动、角色技能特效。
-   **网格数据提取与转换**：从现有的 `StaticMesh` 或 `SkeletalMesh` 中提取几何数据，并用程序化网格进行二次处理或展示。
-   **工具开发与原型制作**：快速在运行时可视化算法生成的几何体，用于开发工具或游戏原型。

## 蓝图用法

蓝图功能主要集中在两个类：`UProceduralMeshComponent`（组件本身）和 `UKismetProceduralMeshLibrary`（静态函数库）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Mesh Section` | 创建或替换一个网格段（Section）。这是最核心的节点，用于定义网格的几何形状。推荐使用接受 `FLinearColor` 的版本。 | `UProceduralMeshComponent` |
| `Update Mesh Section` | 快速更新一个网格段的顶点数据（位置、法线、颜色等），但不能改变拓扑结构（三角形索引）。 | `UProceduralMeshComponent` |
| `Clear Mesh Section` | 清除指定的网格段。 | `UProceduralMeshComponent` |
| `Set Mesh Section Visible` | 控制一个网格段的可见性。 | `UProceduralMeshComponent` |
| `Get Num Sections` | 获取当前组件中网格段的数量。 | `UProceduralMeshComponent` |
| `Add Collision Convex Mesh` | 为组件添加一个用于简单碰撞检测的凸包网格。 | `UProceduralMeshComponent` |
| `Generate Box Mesh` | 生成一个长方体的顶点、索引、法线、UV 和切线数据。 | `UKismetProceduralMeshLibrary` |
| `Calculate Tangents For Mesh` | 根据顶点、三角形和 UV 信息，自动计算法线和切线。 | `UKismetProceduralMeshLibrary` |
| `Slice Procedural Mesh` | 使用一个平面切割程序化网格，并可选择生成切割面（Cap）和另一半网格。 | `UKismetProceduralMeshLibrary` |
| `Copy Procedural Mesh From Static Mesh Component` | 将一个 `StaticMeshComponent` 的网格数据和材质复制到 `ProceduralMeshComponent`。 | `UKismetProceduralMeshLibrary` |

### 使用示例（蓝图描述）

**示例1：动态生成一个简单的四边形**
1.  向 Actor 添加一个 `ProceduralMeshComponent`。
2.  创建四个 `Vector` 变量定义四边形的四个顶点位置。
3.  创建一个 `Int` 数组 `Triangles`，包含两个三角形的索引（例如: 0, 1, 2, 2, 3, 0）。
4.  调用 `Create Mesh Section (LinearColor)` 节点，将 `SectionIndex` 设为 0，传入 `Vertices` 和 `Triangles` 数组。其他法线、UV、颜色数组可留空或传入等长的默认值数组。
5.  将该节点连接到组件的 `Create Mesh Section` 执行引脚。运行后，将在场景中看到一个白色的四边形。

**示例2：切割一个网格体**
1.  假设场景中已有一个填充了数据的 `ProceduralMeshComponent`（源网格体）。
2.  获取一个世界位置作为切割平面通过点（`PlanePosition`）。
3.  定义切割平面的法线（`PlaneNormal`），通常为（0， 0， 1）用于水平切割。
4.  调用 `Slice ProceduralMesh` 函数库节点，将源组件传入 `InProcMesh`，并设置 `bCreateOtherHalf` 为 `true`。
5.  节点会输出一个新的 `ProceduralMeshComponent`（`OutOtherHalfProcMesh`），它代表被切割掉的那一半。通常需要将新组件 spawn 到世界中。

## C++ 用法

C++ 用法提供了比蓝图更精细的控制和更高的性能，特别是在需要频繁更新网格时。

### 头文件引入

```cpp
#include "ProceduralMeshComponent.h"
#include "KismetProceduralMeshLibrary.h"
```

### 基本用法

以下示例展示了如何用 C++ 创建一个简单的三角形网格段。

```cpp
// 假设在 Actor 的头文件中已声明成员变量
UPROPERTY(VisibleAnywhere)
TObjectPtr<UProceduralMeshComponent> ProceduralMesh;

// 在 Actor 的构造函数中创建组件
AMyActor::AMyActor()
{
    ProceduralMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("ProceduralMesh"));
    RootComponent = ProceduralMesh;
}

// 在某个函数（如BeginPlay）中创建网格数据并设置
void AMyActor::GenerateTriangle()
{
    TArray<FVector> Vertices;
    Vertices.Add(FVector(0.f, 0.f, 0.f)); // 顶点 0
    Vertices.Add(FVector(100.f, 0.f, 0.f)); // 顶点 1
    Vertices.Add(FVector(0.f, 100.f, 0.f)); // 顶点 2

    TArray<int32> Triangles;
    Triangles.Add(0);
    Triangles.Add(1);
    Triangles.Add(2);

    TArray<FVector> Normals;
    Normals.Add(FVector(0.f, 0.f, 1.f)); // 每个顶点的法线
    Normals.Add(FVector(0.f, 0.f, 1.f));
    Normals.Add(FVector(0.f, 0.f, 1.f));

    TArray<FLinearColor> VertexColors;
    VertexColors.Add(FLinearColor::Red);
    VertexColors.Add(FLinearColor::Green);
    VertexColors.Add(FLinearColor::Blue);

    // 创建网格段，Index为0，不创建碰撞
    ProceduralMesh->CreateMeshSection_LinearColor(0, Vertices, Triangles, Normals, TArray<FVector2D>(), VertexColors, TArray<FProcMeshTangent>(), false);

    // 可选：设置材质
    // UMaterial* Mat = LoadObject<UMaterial>(nullptr, TEXT("/Game/Materials/M_ProceduralMesh"));
    // ProceduralMesh->SetMaterial(0, Mat);
}
```
*(来源：基于 `UProceduralMeshComponent::CreateMeshSection_LinearColor` 函数签名编写)*

### 进阶用法

结合 `UKismetProceduralMeshLibrary` 进行更复杂的操作。

```cpp
// 使用库函数生成盒子网格数据，然后应用到组件上
void AMyActor::GenerateBoxWithLibrary()
{
    TArray<FVector> BoxVertices;
    TArray<int32> BoxTriangles;
    TArray<FVector> BoxNormals;
    TArray<FVector2D> BoxUVs;
    TArray<FProcMeshTangent> BoxTangents;

    // 生成一个边长为 (50, 50, 50) 的盒子的数据
    UKismetProceduralMeshLibrary::GenerateBoxMesh(FVector(50.f, 50.f, 50.f), BoxVertices, BoxTriangles, BoxNormals, BoxUVs, BoxTangents);

    // 将生成的数据设置到组件的第0段
    ProceduralMesh->CreateMeshSection(0, BoxVertices, BoxTriangles, BoxNormals, BoxUVs, TArray<FColor>(), BoxTangents, true);
}
```
*(来源：基于 `UKismetProceduralMeshLibrary::GenerateBoxMesh` 和 `UProceduralMeshComponent::CreateMeshSection` 函数签名编写)*

## Demo 示例

一个最小的可编译示例，创建一个有颜色的三角形。

```cpp
// MyProceduralActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ProceduralMeshComponent.h"
#include "MyProceduralActor.generated.h"

UCLASS()
class AMyProceduralActor : public AActor
{
	GENERATED_BODY()

public:
	AMyProceduralActor();

protected:
	virtual void BeginPlay() override;

private:
	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UProceduralMeshComponent> MeshComponent;
};
```

```cpp
// MyProceduralActor.cpp
#include "MyProceduralActor.h"

AMyProceduralActor::AMyProceduralActor()
{
	MeshComponent = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("ProceduralMesh"));
	RootComponent = MeshComponent;
}

void AMyProceduralActor::BeginPlay()
{
	Super::BeginPlay();

	TArray<FVector> Vertices;
	Vertices.Add(FVector(0.f, 0.f, 0.f));
	Vertices.Add(FVector(100.f, 0.f, 0.f));
	Vertices.Add(FVector(0.f, 100.f, 0.f));

	TArray<int32> Triangles = {0, 1, 2};

	TArray<FVector> Normals;
	Normals.Init(FVector(0.f, 0.f, 1.f), 3);

	TArray<FLinearColor> Colors;
	Colors.Add(FLinearColor::Red);
	Colors.Add(FLinearColor::Green);
	Colors.Add(FLinearColor::Blue);

	// 创建带颜色的网格段，不生成碰撞
	MeshComponent->CreateMeshSection_LinearColor(0, Vertices, Triangles, Normals, TArray<FVector2D>(), Colors, TArray<FProcMeshTangent>(), false);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/PhysicsCore 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 宏，属于引擎范围的基础性更新。 |
| 2026-02-06 | `af701dad` | [HWRT] Deprecate public FRayTracingGeometry Initializer. | 废弃了公开的 `FRayTracingGeometry` 初始化器，这与硬件光线追踪（HWRT）相关，属于引擎渲染子系统的维护更新。 |
| 2025-10-03 | `6089b974` | ProceduralMeshComponent: Fix SliceProceduralMesh using incorrect normal in presence of non-uniform s | 修复了 `SliceProceduralMesh` 函数在存在非均匀缩放时使用不正确法线的bug。这是一个对插件核心功能（切割）的重要修复。 |
| 2025-08-26 | `ce867df3` | [HWRT] Refactored FRayTracingInstanceCollector to handle multiple views instead of a single referenc | 重构了 `FRayTracingInstanceCollector` 以支持多视图，这是引擎渲染后端的改动，可能间接影响所有使用渲染的组件。 |
| 2025-07-14 | `8c4cad91` | - Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors, and a few changes to | 修改了 `StaticMesh` 中所有 `WITH_EDITORONLY_DATA` 属性的访问器，这是引擎资产系统的重构，插件代码可能随之进行了适配。 |

### 维护评价

-   **活跃维护**：该插件创建于 2015 年，是一个历史悠久的核心功能插件。从 git 历史看，直到 2026 年初仍有更新，且最近一次功能相关的修复（切割法线 bug）发生在 2025 年 10 月，表明其仍在维护中。
-   **更新内容**：近期更新以引擎范围的底层重构和 bug 修复为主（如光线追踪、日志系统、资产访问器），针对插件自身逻辑的实质性功能添加已较少。最近的实质性更新是修复了一个重要 bug。
-   **推荐使用**：**推荐使用**。作为 Epic 官方提供的程序化网格解决方案，它稳定、功能全面，且已深度集成在 UE5 中。尽管它可能不是性能最优的方案（对于极高频更新的网格，可考虑 `DynamicMeshComponent` 或自定义 MeshComponent），但对于绝大多数程序化网格需求，它仍然是首选和标准方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ProceduralMeshComponent)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/procedural-mesh-component-in-unreal-engine/)（UE5 官方文档）