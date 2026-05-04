# Geometry Processing

> Data Structures and Algorithms for Processing 2D and 3D Geometry

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（几何处理算法、动态网格、网格文件工具） |
| 模块 | `GeometryAlgorithms` (Runtime), `DynamicMesh` (Runtime), `MeshFileUtils` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-18 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryProcessing) | |

## 用途

GeometryProcessing 是一个核心的运行时几何处理插件，提供了一套用于处理 2D 和 3D 几何体的底层数据结构和算法。它并非面向最终用户的蓝图工具，而是为引擎内部功能（如建模工具、程序化生成、物理模拟）和其他插件提供基础的几何计算能力。其核心是 `DynamicMesh` 模块，它定义了一种灵活、可编辑的网格表示形式 (`FDynamicMesh3`)，并在此基础上构建了丰富的几何操作算法（如布尔运算、网格简化、UV 展开等）。

## 使用场景

- 你需要在运行时动态创建、修改或分析网格数据（例如程序化生成地形、建筑或角色部件）。
- 你需要在 C++ 中实现自定义的网格处理算法，需要一个高效且功能丰富的网格数据结构作为基础。
- 你需要在开发或测试阶段，快速加载或保存标准的 OBJ 格式网格文件进行调试。
- 你正在开发一个需要复杂几何计算（如凸包分解、网格布尔运算）的插件或游戏功能。

## 蓝图用法

此插件主要为 C++ 设计，其核心类和算法通常不直接暴露给蓝图。蓝图层面的使用通常通过封装了这些底层功能的更高级插件（如 Modeling Tools Editor Mode）来实现。直接在此插件中搜索 `UFUNCTION(BlueprintCallable)` 可能找不到面向设计师的节点。

## C++ 用法

### 头文件引入

根据你要使用的模块引入相应的头文件。

```cpp
// 使用动态网格
#include "DynamicMesh/DynamicMesh3.h"
// 使用几何算法（如布尔运算）
#include "Operations/MeshBoolean.h"
// 使用 OBJ 文件工具
#include "OBJMeshUtil.h"
```

### 基本用法 (DynamicMesh)

`FDynamicMesh3` 是插件的核心数据结构，代表一个可编辑的三角网格。

```cpp
// 来源: DynamicMesh 模块的典型用法
#include "DynamicMesh/DynamicMesh3.h"

void CreateSimpleMesh()
{
    UE::Geometry::FDynamicMesh3 Mesh;
    
    // 添加顶点
    int32 V0 = Mesh.AppendVertex(FVector3d(0, 0, 0));
    int32 V1 = Mesh.AppendVertex(FVector3d(100, 0, 0));
    int32 V2 = Mesh.AppendVertex(FVector3d(0, 100, 0));
    
    // 添加三角形
    Mesh.AppendTriangle(V0, V1, V2);
    
    // 现在可以对 Mesh 进行各种操作...
}
```

### 基本用法 (OBJ 文件)

`MeshFileUtils` 模块提供了简单的 OBJ 文件读写功能，主要用于开发和测试。

```cpp
// 来源: MeshFileUtils/Public/OBJMeshUtil.h
#include "OBJMeshUtil.h"
#include "DynamicMesh/DynamicMesh3.h"

void LoadAndSaveOBJ()
{
    UE::Geometry::FDynamicMesh3 Mesh;
    UE::MeshFileUtils::FLoadOBJSettings LoadSettings;
    LoadSettings.bLoadUVs = true; // 同时加载 UV
    
    // 加载 OBJ 文件
    UE::MeshFileUtils::ELoadOBJStatus Status = UE::MeshFileUtils::LoadOBJ("C:/test.obj", Mesh, LoadSettings);
    
    if (Status == UE::MeshFileUtils::ELoadOBJStatus::Success)
    {
        // 对网格进行一些处理...
        
        // 保存修改后的网格
        UE::MeshFileUtils::FWriteOBJSettings SaveSettings;
        SaveSettings.bWritePerVertexColors = true;
        UE::MeshFileUtils::WriteOBJ("C:/modified.obj", Mesh, SaveSettings);
    }
}
```

### 进阶用法 (几何算法)

使用 `GeometryAlgorithms` 模块中的算法对 `FDynamicMesh3` 进行操作。

```cpp
// 来源: GeometryAlgorithms 模块的典型用法
#include "DynamicMesh/DynamicMesh3.h"
#include "Operations/MeshBoolean.h"

void PerformBooleanOperation()
{
    UE::Geometry::FDynamicMesh3 MeshA, MeshB;
    // ... 假设已经填充了 MeshA 和 MeshB ...
    
    UE::Geometry::FMeshBoolean::EBooleanOp OpType = UE::Geometry::FMeshBoolean::EBooleanOp::Union;
    UE::Geometry::FMeshBoolean BooleanOp(&MeshA, &MeshB, OpType);
    
    // 执行布尔运算
    bool bSuccess = BooleanOp.Compute();
    
    if (bSuccess)
    {
        // 结果存储在 BooleanOp.ResultMesh 中
        UE::Geometry::FDynamicMesh3& ResultMesh = BooleanOp.ResultMesh;
        // ... 使用结果网格 ...
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何创建一个动态网格并将其保存为 OBJ 文件。

```cpp
// MyGeometryActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyGeometryActor.generated.h"

UCLASS()
class AMyGeometryActor : public AActor
{
    GENERATED_BODY()
public:
    AMyGeometryActor();
    virtual void BeginPlay() override;
    
    UFUNCTION(BlueprintCallable, Category = "Geometry")
    void GenerateAndSaveMesh(const FString& FilePath);
};

// MyGeometryActor.cpp
#include "MyGeometryActor.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "OBJMeshUtil.h"

AMyGeometryActor::AMyGeometryActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyGeometryActor::BeginPlay()
{
    Super::BeginPlay();
    // 可以在 BeginPlay 中生成网格
    GenerateAndSaveMesh(FPaths::ProjectSavedDir() / TEXT("GeneratedMesh.obj"));
}

void AMyGeometryActor::GenerateAndSaveMesh(const FString& FilePath)
{
    // 1. 创建一个动态网格
    UE::Geometry::FDynamicMesh3 Mesh;
    
    // 2. 构建一个简单的四面体
    int32 V0 = Mesh.AppendVertex(FVector3d(0, 0, 0));
    int32 V1 = Mesh.AppendVertex(FVector3d(100, 0, 0));
    int32 V2 = Mesh.AppendVertex(FVector3d(50, 100, 0));
    int32 V3 = Mesh.AppendVertex(FVector3d(50, 50, 100));
    
    Mesh.AppendTriangle(V0, V1, V2);
    Mesh.AppendTriangle(V0, V1, V3);
    Mesh.AppendTriangle(V1, V2, V3);
    Mesh.AppendTriangle(V0, V2, V3);
    
    // 3. 保存为 OBJ 文件
    UE::MeshFileUtils::FWriteOBJSettings Settings;
    Settings.bReverseOrientation = false; // 根据需要调整方向
    bool bSaved = UE::MeshFileUtils::WriteOBJ(TCHAR_TO_UTF8(*FilePath), Mesh, Settings);
    
    if (bSaved)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully saved mesh to: %s"), *FilePath);
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，以下是使用此插件时需要考虑的依赖关系。

| 模块 | 用途 |
|---|---|
| `DynamicMesh` | 提供核心的 `FDynamicMesh3` 数据结构和基础网格操作。使用 `GeometryAlgorithms` 或 `MeshFileUtils` 时通常需要依赖此模块。 |
| `GeometryAlgorithms` | 提供高级几何处理算法（布尔、简化、细分等）。依赖 `DynamicMesh`。 |
| `MeshFileUtils` | 提供 OBJ 文件读写工具。依赖 `DynamicMesh`。 |

**注意**：由于 `GeometryProcessing` 是一个运行时插件，你的项目或模块需要在 `.Build.cs` 文件中显式添加对所需模块的依赖。例如，要使用 `DynamicMesh`，你需要添加：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "DynamicMesh" });
```

## 维护状态

### 近期更新

```
- 2025-04-15 73ebd10 为 OBJMeshUtil 的方法添加了 API 导出，以便其他模块可以调用。
- 2025-03-28 bc63a88 将旧的 CppCompileWarning 属性重定向到新的 *.CppCompileWarningSettings。
- 2025-03-15 5c57892 添加了一个几何处理命令行程序，以支持几何处理算法的命令行执行；并添加了导航驱动的近似凸分解作为第一个支持的算法。
```

### 维护评价

**综合评价：活跃维护的核心基础设施插件。**

- **创建时间**：插件于 2019 年左右创建，已有约 6 年历史，属于引擎中较为成熟的模块。
- **更新频率**：从近期提交记录看，插件仍在持续更新和改进。最近的提交（2025年4月）涉及功能增强（API导出）和新算法（凸分解）的添加，表明其处于**活跃维护**状态。
- **功能定位**：作为底层几何处理库，其稳定性至关重要。Epic 将其标记为 `IsBetaVersion: true`，可能意味着其 API 尚未完全稳定，未来可能有变动，但核心功能已广泛用于引擎内部。
- **推荐使用**：**推荐**在需要进行底层、高性能几何处理的 C++ 项目中使用。对于蓝图用户，建议通过更上层的插件（如 Modeling Tools）间接使用。由于其“实验性”标签，在生产环境中使用时应关注版本更新日志，以应对可能的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryProcessing)
- [官方文档]() (无)
- [测试用例]() (可能位于 `Engine/Tests/` 目录下，需进一步查找)