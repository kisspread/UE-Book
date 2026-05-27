# Tet Meshing

> Adds Module for Generating and Refining Tetrahedral Meshes.

| 属性 | 值 |
|---|---|
| 中文名 | 四面体网格生成器 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TetMeshing` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TetMeshing) | |

## 用途

该插件的核心功能是提供**四面体网格生成**算法，特别是实现了一种名为 **Isosurface Stuffing** 的算法。它的作用是将一个由隐式函数（如符号距离场 SDF 或快速缠绕数 FWN）定义的三维几何体，转换成由大量小四面体组成的体积网格。

这种技术主要用于：
- **物理模拟**：为有限元分析（FEA）准备高质量的四面体网格，用于模拟物体的形变、破碎等物理效果。
- **碰撞检测**：生成精确的体积碰撞体，适用于需要复杂物理交互的场景。
- **几何处理**：作为更高级几何处理算法（如网格变形、拓扑优化）的基础数据结构。

该插件目前处于实验阶段，主要包含一个基础的网格生成器基类和一个具体算法的实现，是物理和几何处理领域的底层工具。

## 使用场景

- **你需要为游戏中的物体创建物理破坏效果** → 使用该插件将物体网格转换为四面体网格，然后输入物理引擎进行破碎模拟。
- **你正在开发一个基于有限元方法的软体物理系统** → 用该插件生成用于模拟的体网格。
- **你有一个复杂的隐式几何（例如程序化生成的洞穴、器官模型），需要转换成可用于物理计算的网格格式** → 使用 `IsosurfaceStuffing` 算法进行转换。

## 蓝图用法

该插件目前**没有暴露任何蓝图可调用函数或属性**。它的核心功能以 C++ 模板类的形式提供，主要用于底层的物理和几何处理模块，不直接面向蓝图设计师。相关的用法需要通过 C++ 接口进行。

## C++ 用法

### 头文件引入

```cpp
#include "Generate/IsosurfaceStuffing.h"
```

### 基本用法

`IsosurfaceStuffing` 是一个模板类，需要指定浮点类型（通常是 `float` 或 `double`）。其使用流程是：设置参数，然后调用 `Generate()`。

**基础示例：为一个球体生成四面体网格**
（参考 `IsosurfaceStuffing.h` 中的参数定义）

```cpp
#include "Generate/IsosurfaceStuffing.h"

using namespace UE::Geometry;

void GenerateSphereTetMesh()
{
    // 1. 定义一个 SDF 隐式函数（这里是一个简单的球体）
    TFunction<float(const FVector&)> SphereImplicit = [](const FVector& P) -> float
    {
        // 返回点到原点的距离减去半径，内部为正值，外部为负值
        return P.Size() - 50.0f; // 50 单位半径的球
    };

    // 2. 创建生成器实例
    TIsosurfaceStuffing<float> Generator;

    // 3. 配置生成器参数
    Generator.Bounds = FBox(FVector(-100.f), FVector(100.f)); // 设置采样包围盒
    Generator.CellSize = 5.0f; // 设置网格单元大小，值越小网格越密
    Generator.Implicit = SphereImplicit; // 传入隐式函数
    Generator.IsoValue = 0.0f; // 等值面值，通常为0（表面）

    // 4. 执行生成
    Generator.Generate();

    // 5. 获取结果
    const TArray<FVector>& Vertices = Generator.Vertices; // 生成的顶点
    const TArray<FIntVector4>& Tets = Generator.Tets; // 生成的四面体（每个元素为4个顶点索引）
}
```

### 进阶用法

可以通过继承 `TTetMeshGenerator` 基类来创建自定义的四面体网格生成算法，例如生成简单的规则形状（如球、圆柱）。基类提供了通用的数据存储结构和辅助函数。

**自定义生成器示例框架**
（参考 `TetMeshGenerator.h` 中的基类结构）

```cpp
#include "Generate/TetMeshGenerator.h"

class FMyCustomTetGenerator : public TTetMeshGenerator<float>
{
public:
    // 自定义参数
    float Radius;
    int32 Subdivisions;

    virtual TTetMeshGenerator<float>& Generate() override
    {
        Reset(); // 清除旧数据

        // 在这里实现你的生成逻辑
        // 1. 使用 Vertices.Add() 添加顶点
        // 2. 使用 AppendTet(A, B, C, D) 添加四面体
        // 例如，生成一个简单的四面体：
        Vertices.Add(FVector(0, 0, 0)); // 0
        Vertices.Add(FVector(10, 0, 0)); // 1
        Vertices.Add(FVector(0, 10, 0)); // 2
        Vertices.Add(FVector(0, 0, 10)); // 3
        AppendTet(0, 1, 2, 3); // 生成第一个四面体

        return *this;
    }
};
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何在 `UObject` 或 `ActorComponent` 中使用 `IsosurfaceStuffing` 生成四面体网格。

**TetMeshDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Generate/IsosurfaceStuffing.h"
#include "TetMeshDemo.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UTetMeshDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UTetMeshDemoComponent();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "TetMesh")
    void GenerateDebugMesh();

private:
    // 存储生成结果
    TArray<FVector> CachedVertices;
    TArray<FIntVector4> CachedTets;
};
```

**TetMeshDemo.cpp**
```cpp
#include "TetMeshDemo.h"

using namespace UE::Geometry;

UTetMeshDemoComponent::UTetMeshDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UTetMeshDemoComponent::BeginPlay()
{
    Super::BeginPlay();
    GenerateDebugMesh(); // 游戏开始时自动生成，用于调试
}

void UTetMeshDemoComponent::GenerateDebugMesh()
{
    // 定义一个球体SDF
    auto SphereSDF = [](const FVector& P) -> float
    {
        return P.Size() - 30.0f;
    };

    // 配置并生成
    TIsosurfaceStuffing<float> MeshGenerator;
    MeshGenerator.Bounds = FBox(FVector(-50.f), FVector(50.f));
    MeshGenerator.CellSize = 3.0f;
    MeshGenerator.Implicit = SphereSDF;
    MeshGenerator.IsoValue = 0.0f;

    MeshGenerator.Generate();

    // 缓存结果
    CachedVertices = MoveTemp(MeshGenerator.Vertices);
    CachedTets = MoveTemp(MeshGenerator.Tets);

    UE_LOG(LogTemp, Log, TEXT("Generated Tet Mesh: %d Vertices, %d Tets"), CachedVertices.Num(), CachedTets.Num());

    // 注意：此处仅缓存数据。要可视化，你可能需要将四面体转换为三角面（例如使用每个四面体的4个三角面）并添加到 ProceduralMeshComponent 中。
}
```

## 模块依赖

要使用该插件，你的模块需要在 `Build.cs` 中添加以下依赖。该插件本身依赖 `GeometryProcessing` 插件中的几何算法。

| 模块 | 用途 |
|---|---|
| `TetMeshing` | 本插件，提供四面体网格生成功能 |
| `GeometryProcessing` | 提供底层的几何处理工具（网格操作、距离场计算等），是本插件的核心依赖 |

```csharp
// 你的模块的 Build.cs 文件中需要添加:
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "TetMeshing", // 引用本插件模块
    "GeometryProcessing" // 引用其依赖的几何处理模块
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-11-20 | `763a6119` | Fix C4072 warnings | 修复了编译时的 C4072 类型转换警告，无功能变化。 |
| 2023-02-17 | `73c74eaf` | Removing redundant include paths: | 清理了代码中多余的头文件包含路径。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了插件文档链接为 HTTPS 协议，与功能无关。 |
| 2022-09-17 | `73159497` | CIS fix for PVS studio warning in IsosurfaceStuffing.h | 修复了 PVS Studio 代码分析工具在 `IsosurfaceStuffing.h` 中发出的警告。 |
| 2022-09-16 | `b13eab1b` | fix CIS issue: PVS Studio warnings in IsosurfaceStuffing.h | 同上，修复静态代码分析警告。 |

### 维护评价

- **创建时间**：2022年9月首次提交，历史约3年。
- **更新频率**：最近一次实质性更新停留在**2023年2月**（仅清理代码）。自创建以来，大部分提交是针对编译警告、代码分析工具报告的修复，**没有添加新功能或算法改进**。
- **活跃度**：处于**实验性且维护不活跃**的状态。作为 `Experimental` 文件夹下的插件，并且被标记为 `IsBetaVersion=true` 和 `EnabledByDefault=false`，表明它是 Epic 用于内部研发或概念验证的代码，尚未准备好用于生产环境。
- **已知问题**：代码中存在多个 `TODO` 注释，表明其功能（如多标签处理、更高效的生成策略）尚未完善。
- **推荐使用**：**谨慎使用**。该插件适合对四面体网格生成有基础需求，且不介意使用实验性、可能不完整代码的开发者。**不建议**直接用于商业项目的生产环境。如果你需要稳定、完整的四面体网格解决方案，可能需要寻找其他更成熟的库或等待 Epic 将其正式发布。

**警告：** 该插件超过1年没有功能性更新，且标记为实验性。其API和实现可能在未来版本中发生重大变化或被移除。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TetMeshing)
- [官方文档]（暂无）
- [测试用例]（暂无，插件目录内未包含公开的测试文件）