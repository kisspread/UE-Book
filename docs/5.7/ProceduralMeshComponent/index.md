# Procedural Mesh Component

> A renderable component and library of utilities for creating and modifying mesh geometry procedurally.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | ProceduralMeshComponent (Runtime), ProceduralMeshComponentEditor (Editor) |
| 创建时间 | 2015-04-17 |
| 年龄标签 | 🏛️ 文物（约11年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ProceduralMeshComponent) | |

## 用途

ProceduralMeshComponent 提供一个可在运行时动态创建和修改三角形网格几何体的渲染组件。它解决的核心问题是：**在没有预制 StaticMesh 资源的情况下，通过代码（C++ 或蓝图）实时构建 3D 几何体**。

从源码看，`UProceduralMeshComponent` 继承自 `UMeshComponent` 和 `IInterface_CollisionDataProvider`，这意味着它同时具备渲染和物理碰撞能力。组件将网格按 **Section**（段）组织，每个 Section 对应一个独立的材质槽，可以单独创建、更新、清除和控制可见性。

插件还附带 `UKismetProceduralMeshLibrary` 工具类，提供网格生成（盒体、网格平面）、切线计算、StaticMesh 数据提取、网格切割等实用功能。

> ⚠️ 源码注释中标注此功能为 **experimental**，Epic 可能在未来版本中进行重大更改。UE5 中已有 `UDynamicMeshComponent`（GeometryFramework 模块）作为更现代的替代方案。

## 使用场景

- **运行时地形生成**：你需要根据噪声函数或高度图在游戏运行时生成地形网格 → 使用 `CreateGridMeshWelded` + `CreateMeshSection_LinearColor`
- **可破坏物体**：你需要将物体沿平面切割成两半 → 使用 `SliceProceduralMesh`
- **程序化建筑/关卡**：需要在运行时根据算法生成墙壁、地板等几何体 → 使用 `GenerateBoxMesh` 或自定义顶点数据
- **从 StaticMesh 提取数据**：需要在蓝图中读取 StaticMesh 的顶点/三角形数据用于自定义处理 → 使用 `GetSectionFromStaticMesh`
- **动态网格变形**：需要每帧更新顶点位置（如水面波浪、布料模拟）→ 使用 `UpdateMeshSection_LinearColor`（比重建 Section 更快）
- **编辑器中快速原型**：在蓝图中快速搭建几何原型，之后可转换为 StaticMesh → 使用编辑器的 "Convert to StaticMesh" 按钮

## 蓝图用法

### 网格创建与更新

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Mesh Section` | 创建/替换一个网格 Section，支持 4 组 UV 通道和 LinearColor 顶点色 | `UProceduralMeshComponent` |
| `Create Mesh Section FColor` | ⚠️ **已废弃**，使用 FColor 类型，改用上方的 LinearColor 版本 | `UProceduralMeshComponent` |
| `Update Mesh Section` | 更新已有 Section 的顶点数据（不改变拓扑结构），比 Create 更快 | `UProceduralMeshComponent` |
| `Update Mesh Section FColor` | ⚠️ **已废弃**，使用 FColor 类型，改用上方的 LinearColor 版本 | `UProceduralMeshComponent` |

### 网格管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Clear Mesh Section` | 清除指定 Section，其他 Section 索引不变 | `UProceduralMeshComponent` |
| `Clear All Mesh Sections` | 清除所有 Section，重置为空状态 | `UProceduralMeshComponent` |
| `Set Mesh Section Visible` | 控制指定 Section 的可见性 | `UProceduralMeshComponent` |
| `Is Mesh Section Visible` | 查询指定 Section 是否可见 | `UProceduralMeshComponent` |
| `Get Num Sections` | 获取当前 Section 数量 | `UProceduralMeshComponent` |

### 碰撞

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Collision Convex Mesh` | 添加简单凸碰撞几何体 | `UProceduralMeshComponent` |
| `Clear Collision Convex Meshes` | 清除所有凸碰撞几何体 | `UProceduralMeshComponent` |

### 网格生成工具（KismetProceduralMeshLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Generate Box Mesh` | 生成盒体的顶点/索引/法线/UV/切线数据 | `UKismetProceduralMeshLibrary` |
| `Calculate Tangents For Mesh` | 根据顶点、三角形和 UV 自动计算法线和切线 | `UKismetProceduralMeshLibrary` |
| `Convert Quad To Triangles` | 将四边形（4个顶点索引）转换为两个三角形加入索引缓冲 | `UKismetProceduralMeshLibrary` |
| `Create Grid Mesh Triangles` | 生成网格平面的索引缓冲 | `UKismetProceduralMeshLibrary` |
| `Create Grid Mesh Welded` | 生成焊接网格（共享顶点），带 UV | `UKismetProceduralMeshLibrary` |
| `Create Grid Mesh Split` | 生成分离网格（每四边形独立顶点），带 UV0 和 UV1 | `UKismetProceduralMeshLibrary` |
| `Get Section From Static Mesh` | 从 StaticMesh 资源提取指定 Section 的几何数据 | `UKismetProceduralMeshLibrary` |
| `Copy Procedural Mesh From Static Mesh Component` | 将 StaticMeshComponent 的几何数据复制到 ProceduralMeshComponent | `UKismetProceduralMeshLibrary` |
| `Get Section From Procedural Mesh` | 从 ProceduralMeshComponent 提取指定 Section 的几何数据 | `UKismetProceduralMeshLibrary` |
| `Slice Procedural Mesh` | 用平面切割 ProceduralMeshComponent，可选生成截面和另一半 | `UKismetProceduralMeshLibrary` |

### 使用示例（蓝图描述）

**创建一个简单的三角形：**

1. 在 Actor 蓝图中添加 `ProceduralMeshComponent`
2. 使用 `Make Array` 节点创建 3 个 `Vector`（顶点位置），如 `(0,0,0)`, `(100,0,0)`, `(0,100,0)`
3. 使用 `Make Array` 创建索引数组 `(0, 1, 2)`
4. 调用 `Create Mesh Section`，SectionIndex = 0，传入顶点和索引数组，其他参数留空，bCreateCollision = false
5. 创建一个 `Material` 并赋给 ProceduralMeshComponent 的 Element 0

**生成盒体并创建网格：**

1. 调用 `Generate Box Mesh`，BoxRadius = `(50, 50, 50)`，获取输出的 Vertices、Triangles、Normals、UVs、Tangents
2. 将这些数据传入 `Create Mesh Section`

**切割物体：**

1. 对已有的 ProceduralMeshComponent 调用 `Slice ProceduralMesh`
2. 设置 PlanePosition = 切割点世界坐标，PlaneNormal = 切割方向
3. bCreateOtherHalf = true，CapOption = `CreateNewSectionForCap`
4. 获取 OutOtherHalfProcMesh 作为被切下的另一半

## C++ 用法

### 头文件引入

```cpp
#include "ProceduralMeshComponent.h"
#include "KismetProceduralMeshLibrary.h"
```

### 模块依赖

在你的模块 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "ProceduralMeshComponent"
});
```

### 基本用法 — 动态创建网格

```cpp
// 创建组件
UProceduralMeshComponent* ProcMeshComp = NewObject<UProceduralMeshComponent>(this);
ProcMeshComp->RegisterComponent();
ProcMeshComp->AttachToComponent(RootComponent, FAttachmentTransformRules::KeepRelativeTransform);

// 准备顶点数据（一个简单的三角形）
TArray<FVector> Vertices;
Vertices.Add(FVector(0.f, 0.f, 0.f));
Vertices.Add(FVector(100.f, 0.f, 0.f));
Vertices.Add(FVector(0.f, 100.f, 0.f));

// 准备索引数据（逆时针绕序）
TArray<int32> Triangles;
Triangles.Add(0);
Triangles.Add(1);
Triangles.Add(2);

// 创建网格 Section
ProcMeshProcMeshComp->CreateMeshSection_LinearColor(
    0,              // SectionIndex
    Vertices,
    Triangles,
    TArray<FVector>(),          // Normals（空 = 自动生成）
    TArray<FVector2D>(),        // UV0
    TArray<FLinearColor>(),     // VertexColors
    TArray<FProcMeshTangent>(), // Tangents
    false,                      // bCreateCollision
    false                       // bSRGBConversion
);
```

### 进阶用法 — 运行时更新网格

```cpp
// 假设已经创建了 Section 0
// 只更新顶点位置，不改变拓扑（索引不变）
TArray<FVector> NewVertices;
// ... 填充新顶点数据（数量必须与原始相同）

TArray<FVector> Normals;
// ... 重新计算法线

ProcMeshComp->UpdateMeshSection_LinearColor(
    0,              // SectionIndex
    NewVertices,
    Normals,
    TArray<FVector2D>(),        // UV0
    TArray<FLinearColor>(),     // VertexColors
    TArray<FProcMeshTangent>(), // Tangents
    true                        // bSRGBConversion
);
```

### 进阶用法 — 从 StaticMesh 提取数据

```cpp
#include "KismetProceduralMeshLibrary.h"

UStaticMesh* SourceMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Meshes/MyMesh"));

TArray<FVector> Vertices;
TArray<int32> Triangles;
TArray<FVector> Normals;
TArray<FVector2D> UVs;
TArray<FProcMeshTangent> Tangents;

UKismetProceduralMeshLibrary::GetSectionFromStaticMesh(
    SourceMesh,
    0,          // LODIndex
    0,          // SectionIndex
    Vertices,
    Triangles,
    Normals,
    UVs,
    Tangents
);

// 然后用于创建 ProceduralMesh
ProcMeshComp->CreateMeshSection_LinearColor(0, Vertices, Triangles, Normals, UVs,
    TArray<FLinearColor>(), Tangents, false);
```

### 进阶用法 — 网格切割

```cpp
// 切割一个 ProceduralMeshComponent
UProceduralMeshComponent* OtherHalf = nullptr;

UKismetProceduralMeshLibrary::SliceProceduralMesh(
    ProcMeshComp,                   // 要切割的组件
    FVector(0.f, 0.f, 50.f),       // 平面上一点（世界坐标）
    FVector(0.f, 0.f, 1.f),        // 平面法线（保留正方向的几何体）
    true,                           // 生成另一半
    OtherHalf,                      // 输出：另一半组件
    EProcMeshSliceCapOption::CreateNewSectionForCap,  // 截面选项
    CapMaterial                     // 截面材质
);
```

## Demo 示例

### 完整示例 — 运行时生成带碰撞的地形网格

**MyProceduralActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ProceduralMeshComponent.h"
#include "MyProceduralActor.generated.h"

UCLASS()
class MYPROJECT_API AMyProceduralActor : public AActor
{
    GENERATED_BODY()

public:
    AMyProceduralActor();

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UProceduralMeshComponent> ProcMeshComp;

    UPROPERTY(EditAnywhere, Category = "Terrain")
    int32 GridSizeX = 32;

    UPROPERTY(EditAnywhere, Category = "Terrain")
    int32 GridSizeY = 32;

    UPROPERTY(EditAnywhere, Category = "Terrain")
    float GridSpacing = 100.f;

    UPROPERTY(EditAnywhere, Category = "Terrain")
    float HeightScale = 50.f;

protected:
    virtual void BeginPlay() override;
    virtual void OnConstruction(const FTransform& Transform) override;

private:
    void GenerateTerrain();
    float GetHeightAtPoint(float X, float Y) const;
};
```

**MyProceduralActor.cpp**

```cpp
#include "MyProceduralActor.h"
#include "KismetProceduralMeshLibrary.h"

AMyProceduralActor::AMyProceduralActor()
{
    ProcMeshComp = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("ProcMesh"));
    RootComponent = ProcMeshComp;
    ProcMeshComp->bUseComplexAsSimpleCollision = true;
}

void AMyProceduralActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    GenerateTerrain();
}

void AMyProceduralActor::BeginPlay()
{
    Super::BeginPlay();
    GenerateTerrain();
}

float AMyProceduralActor::GetHeightAtPoint(float X, float Y) const
{
    // 简单的正弦波地形
    return FMath::Sin(X * 0.01f) * FMath::Cos(Y * 0.01f) * HeightScale;
}

void AMyProceduralActor::GenerateTerrain()
{
    TArray<FVector> Vertices;
    TArray<int32> Triangles;
    TArray<FVector2D> UVs;
    TArray<FVector> Normals;
    TArray<FProcMeshTangent> Tangents;
    TArray<FLinearColor> VertexColors;

    // 生成顶点和 UV
    for (int32 y = 0; y <= GridSizeY; ++y)
    {
        for (int32 x = 0; x <= GridSizeX; ++x)
        {
            float XPos = x * GridSpacing;
            float YPos = y * GridSpacing;
            float ZPos = GetHeightAtPoint(XPos, YPos);

            Vertices.Add(FVector(XPos, YPos, ZPos));
            UVs.Add(FVector2D((float)x / GridSizeX, (float)y / GridSizeY));
            VertexColors.Add(FLinearColor(1.f, 1.f, 1.f));
        }
    }

    // 生成索引
    for (int32 y = 0; y < GridSizeY; ++y)
    {
        for (int32 x = 0; x < GridSizeX; ++x)
        {
            int32 BottomLeft = y * (GridSizeX + 1) + x;
            int32 BottomRight = BottomLeft + 1;
            int32 TopLeft = BottomLeft + (GridSizeX + 1);
            int32 TopRight = TopLeft + 1;

            UKismetProceduralMeshLibrary::ConvertQuadToTriangles(
                Triangles, BottomLeft, BottomRight, TopRight, TopLeft);
        }
    }

    // 自动计算法线和切线
    UKismetProceduralMeshLibrary::CalculateTangentsForMesh(
        Vertices, Triangles, UVs, Normals, Tangents);

    // 创建网格 Section（启用碰撞）
    ProcMeshComp->CreateMeshSection_LinearColor(
        0, Vertices, Triangles, Normals, UVs,
        TArray<FVector2D>(), TArray<FVector2D>(), TArray<FVector2D>(),
        VertexColors, Tangents, true);
}
```

**MyProject.Build.cs 依赖配置：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "ProceduralMeshComponent"
});
```

## 模块依赖

要使用 ProceduralMeshComponent，你的模块需要在 Build.cs 中声明依赖：

| 模块 | 用途 |
|---|---|
| `ProceduralMeshComponent` | 插件核心模块，包含 `UProceduralMeshComponent` 和 `UKismetProceduralMeshLibrary` |

插件自身依赖的底层模块（通常无需直接引用）：

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `MeshDescription` | 网格数据描述格式 |
| `RenderCore` | 渲染核心 |
| `RHI` | 渲染硬件接口 |
| `StaticMeshDescription` | StaticMesh 数据描述 |
| `PhysicsCore` | 物理核心（碰撞支持） |

## 维护状态

### 基本信息

- **创建时间**: 2014-03-14
- **年龄**: 约 12 年
- **年龄标签**: 🏛️ 文物

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-03 | `a39bf545dd29` | Fix SliceProceduralMesh using incorrect normal in presence of non-uniform scale |
| 2025-08-26 | `ce867df381b7` | [HWRT] Refactored FRayTracingInstanceCollector to handle multiple views |
| 2025-07-14 | `8c4cad918a59` | Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors |

**解读：**

- `a39bf545dd29`（2025-10-03）：**实质性修复**。修复了 `SliceProceduralMesh` 在非均匀缩放（non-uniform scale）下使用错误法线的 bug。这是一个针对核心功能的 bug 修复，说明 Epic 仍在维护该插件的正确性。
- `ce867df381b7`（2025-08-26）：**间接改动**。这是硬件光线追踪的全局重构，涉及 ProceduralMeshComponent 的场景代理（SceneProxy）代码适配，不是针对该插件的功能性更新。
- `8c4cad918a59`（2025-07-14）：**间接改动**。StaticMesh 属性访问器重构，对 ProceduralMeshComponent 无直接影响。

### 维护评价

**综合评价：维护中 — 低活跃度**

- **年龄**：插件创建于 2015 年 4 月，超过 10 年历史
- **最近更新**：最近一次实质性修复在 2025-10-03（非均匀缩放下的切割 bug），距今约 6 个月，说明 Epic 仍在处理 bug 报告
- **活跃程度**：低活跃度。该插件功能已趋于稳定，近期更新均为 bug 修复和引擎级适配，无新功能添加
- **已知限制**：
  - 源码注释中标注为 **experimental**，但已使用多年，实际稳定性良好
  - 不支持 LOD 系统
  - 性能不如原生 StaticMesh（无 Nanite、无 GPU 驱动渲染）
  - UE5 中 `UDynamicMeshComponent`（GeometryFramework）功能更强大，是更现代的替代方案
- **推荐程度**：**推荐用于简单场景**。对于原型制作、简单的程序化几何体、运行时网格修改等场景仍然可靠。对于高性能需求或复杂程序化几何，建议考虑 GeometryFramework 的 DynamicMeshComponent

## 相关链接

- [源码（plugin 目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ProceduralMeshComponent)
- [ProceduralMeshComponent.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/ProceduralMeshComponent/Source/ProceduralMeshComponent/Public/ProceduralMeshComponent.h)
- [KismetProceduralMeshLibrary.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/ProceduralMeshComponent/Source/ProceduralMeshComponent/Public/KismetProceduralMeshLibrary.h)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：引擎中未找到针对该插件的专用测试文件
