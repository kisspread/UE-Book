# Custom Mesh Component

> A new renderable Component class that allows you to specify custom geometry via C++ or Blueprint.

| 属性 | 值 |
|---|---|
| 中文名 | 自定义网格组件 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CustomMeshComponent` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CustomMeshComponent) | |

## 用途

提供一个运行时可渲染组件，允许开发者在 C++ 或蓝图中通过**三角形顶点列表**动态构建自定义网格几何体。该插件解决的核心问题是：当你需要程序化生成几何形状（如特效、调试可视化、动态生成的地形等），但又不想依赖完整的 Mesh 资产时，可以用代码直接传入三角形顶点来渲染任意形状。

`UCustomMeshComponent` 继承自 `UMeshComponent`，内部将三角形数据转换为渲染所需的场景代理（Scene Proxy），是 UE 提供的最轻量级的自定义几何渲染方案。

## 使用场景

- 你需要在运行时程序化生成简单的 3D 几何体（如线框、平面、自定义多边形）
- 你正在做程序化建筑或地形，需要动态构建可见网格
- 你需要快速渲染调试几何体（如碰撞区域可视化）
- 你需要在蓝图中通过顶点数据绘制自定义形状，不想写自定义渲染器
- 你希望用最少代码获得自定义网格的材质渲染能力（而非仅 DrawDebugLine）

## 蓝图用法

该插件提供了 3 个 `BlueprintCallable` 节点和 1 个 `BlueprintType` 结构体。

### 核心结构体

| 结构体 | 字段 | 说明 |
|---|---|---|
| `FCustomMeshTriangle` | `Vertex0`, `Vertex1`, `Vertex2` (FVector) | 定义一个三角形的三个顶点 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCustomMeshTriangles` | 设置整个网格的三角形数据（替换现有几何体），返回 `bool` 表示成功与否 | `UCustomMeshComponent` |
| `AddCustomMeshTriangles` | 追加三角形数据到现有几何体（可能导致内存重新分配） | `UCustomMeshComponent` |
| `ClearCustomMeshTriangles` | 清除所有几何体数据，但不释放内存以便复用 | `UCustomMeshComponent` |

### 使用示例（蓝图描述）

**绘制一个三角形：**

1. 在 Actor 上添加 `CustomMeshComponent` 组件
2. 创建一个 `FCustomMeshTriangle` 变量，设置三个顶点：
   - `Vertex0 = (0, 0, 0)`
   - `Vertex1 = (100, 0, 0)`
   - `Vertex2 = (0, 100, 0)`
3. 将该结构体放入数组（`TArray<FCustomMeshTriangle>`）
4. 调用 `SetCustomMeshTriangles` 传入该数组
5. 在组件上设置材质（通过材质槽 0）

**追加更多三角形：**

1. 准备新的 `FCustomMeshTriangle` 数组
2. 调用 `AddCustomMeshTriangles` 追加到已有几何体
3. 注意：频繁追加会导致内存重新分配，尽量一次设置所有数据

## C++ 用法

### 头文件引入

```cpp
#include "CustomMeshComponent.h"
```

### 基本用法

创建组件并设置三角形几何体：

```cpp
// 创建自定义网格组件
UCustomMeshComponent* MeshComp = NewObject<UCustomMeshComponent>(this);
MeshComp->RegisterComponent();

// 定义一个三角形
TArray<FCustomMeshTriangle> Triangles;
FCustomMeshTriangle Tri;
Tri.Vertex0 = FVector(0.f, 0.f, 0.f);
Tri.Vertex1 = FVector(100.f, 0.f, 0.f);
Tri.Vertex2 = FVector(0.f, 100.f, 0.f);
Triangles.Add(Tri);

// 设置网格几何体
MeshComp->SetCustomMeshTriangles(Triangles);

// 设置材质
MeshComp->SetMaterial(0, MyMaterial);
```

### 进阶用法

批量追加几何体并管理材质：

```cpp
// 先设置初始几何体
TArray<FCustomMeshTriangle> BaseTriangles;
// ... 填充数据 ...
MeshComp->SetCustomMeshTriangles(BaseTriangles);

// 运行时追加更多三角形
TArray<FCustomMeshTriangle> ExtraTriangles;
FCustomMeshTriangle Extra;
Extra.Vertex0 = FVector(100.f, 0.f, 0.f);
Extra.Vertex1 = FVector(200.f, 0.f, 0.f);
Extra.Vertex2 = FVector(100.f, 100.f, 0.f);
ExtraTriangles.Add(Extra);
MeshComp->AddCustomMeshTriangles(ExtraTriangles);

// 需要完全替换时，先清除再设置
MeshComp->ClearCustomMeshTriangles();
MeshComp->SetCustomMeshTriangles(NewTriangles);
```

## Demo 示例

### MyCustomMeshActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CustomMeshComponent.h"
#include "MyCustomMeshActor.generated.h"

UCLASS()
class AMyCustomMeshActor : public AActor
{
	GENERATED_BODY()

public:
	AMyCustomMeshActor();

	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere)
	UCustomMeshComponent* MeshComponent;

	UPROPERTY(EditAnywhere, Category = "Rendering")
	UMaterialInterface* MeshMaterial;
};
```

### MyCustomMeshActor.cpp

```cpp
#include "MyCustomMeshActor.h"

AMyCustomMeshActor::AMyCustomMeshActor()
{
	MeshComponent = CreateDefaultSubobject<UCustomMeshComponent>(TEXT("CustomMesh"));
	RootComponent = MeshComponent;
}

void AMyCustomMeshActor::BeginPlay()
{
	Super::BeginPlay();

	// 构建一个四边形（两个三角形）
	TArray<FCustomMeshTriangle> Triangles;

	// 三角形 1
	FCustomMeshTriangle Tri1;
	Tri1.Vertex0 = FVector(0.f, -50.f, 0.f);
	Tri1.Vertex1 = FVector(100.f, -50.f, 0.f);
	Tri1.Vertex2 = FVector(100.f, 50.f, 0.f);
	Triangles.Add(Tri1);

	// 三角形 2
	FCustomMeshTriangle Tri2;
	Tri2.Vertex0 = FVector(0.f, -50.f, 0.f);
	Tri2.Vertex1 = FVector(100.f, 50.f, 0.f);
	Tri2.Vertex2 = FVector(0.f, 50.f, 0.f);
	Triangles.Add(Tri2);

	MeshComponent->SetCustomMeshTriangles(Triangles);

	if (MeshMaterial)
	{
		MeshComponent->SetMaterial(0, MeshMaterial);
	}
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加内联生成宏以改善编译性能 |
| 2025-06-18 | `08316dbb` | Cache the ShaderPlatform inside MaterialResource, derive the FeatureLevel from that ShaderPlatform. | 材质资源中缓存 Shader 平台，优化特性级别查询 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar. | 为方法和静态变量添加 DLL 导出声明，适配构建系统更新 |
| 2024-10-30 | `f2983507` | Replaced include SceneManagement.h with PrimitiveDrawingUtils.h in files that only need primitive drawing utilities. | 更新头文件引用，替换为更精确的 PrimitiveDrawingUtils.h |
| 2024-10-30 | `1be846b4` | Fixed non unity compile errors | 修复非 Unity 编译模式下的编译错误 |

### 维护评价

该插件创建于 2014 年，是 UE4 早期就存在的官方插件，至今已有约 11 年历史。近期提交均为**构建系统适配和编译修复**（DLL 导出、头文件替换、内联宏等），没有功能性变更。这说明插件功能早已稳定，但仍在跟随引擎主分支保持编译兼容性。

**优点**：代码极其精简（仅 4 个源文件），API 简单明确，经过 10+ 年验证，稳定可靠。

**局限**：仅支持三角形列表（无索引缓冲、无 UV、无法线输入），适用于简单几何体，不适合复杂网格渲染。每个三角形需要 3 个独立顶点，无法共享顶点，大数据量时效率较低。

**推荐使用**：✅ 适合需要快速程序化生成简单几何体的场景。如果需要更高级的自定义网格功能（UV、法线、切线等），应考虑自定义 `FMeshBatch` 或使用 `ProceduralMeshComponent`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CustomMeshComponent)