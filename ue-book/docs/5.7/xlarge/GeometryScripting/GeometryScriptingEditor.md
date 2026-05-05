# Geometry Script

> Geometry Script provides a library of functions for creating and editing Meshes in Blueprints and Python

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GeometryScriptingCore` (Runtime), `GeometryScriptingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-09-12 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting) | |

## 用途

Geometry Script 是一个强大的运行时和编辑器工具集，其核心目的是**在蓝图和 Python 脚本中提供对 `UDynamicMesh` 的全面程序化操作能力**。它解决了在编辑器内或运行时通过脚本高效、安全地创建和修改网格几何体的问题。

与直接在 Construction Script 中进行昂贵的网格生成不同，Geometry Script 通过其 `EditorGeometryGenerationSubsystem` 提供了受管理的、可节流的生成机制，避免了编辑器交互卡顿。它封装了底层的几何处理算法（如细分、布尔运算、UV 操作等），将其暴露为易于使用的蓝图节点，极大地扩展了 Unreal Engine 的程序化内容创作（PCG）和工具开发能力。

## 使用场景

- **编辑器内程序化建模**：你需要在编辑器中通过蓝图创建复杂的参数化模型（如地形、建筑模块），并希望生成过程不影响编辑器交互性。
- **运行时网格生成**：在游戏运行时，根据玩家输入或游戏逻辑动态生成或修改网格（如可破坏环境、自定义角色部件）。
- **批量资产处理**：使用 Python 脚本批量导入、清理或优化大量静态网格资产。
- **自定义建模工具开发**：作为开发基础，构建特定领域的建模或编辑工具。
- **纹理通道处理**：在编辑器中对纹理的 RGBA 通道进行打包、拆分等操作，用于生成特殊材质贴图。

## 蓝图用法

Geometry Script 的蓝图 API 主要分布在 `GeometryScriptingCore` 和 `GeometryScriptingEditor` 模块中。以下按功能分组列出核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Apply Polygroup Catmull Clark SubD` | 对网格应用基于多边形分组的 Catmull-Clark 细分曲面。 | `UGeometryScriptLibrary_OpenSubdivFunctions` |
| `Apply Triangle Loop SubD` | 对网格应用基于三角形的 Loop 细分曲面。 | `UGeometryScriptLibrary_OpenSubdivFunctions` |
| `Channel Pack` | 将最多四个不同纹理的指定通道（R, G, B, A）打包到一个输出纹理中。 | `UGeometryScriptLibrary_EditorTextureMapFunctions` |
| `Begin Tracked Mesh Change` | 开始追踪对 `UDynamicMesh` 的修改，为后续的撤销/重做操作保存初始状态。 | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |
| `Emit Tracked Mesh Change` | 结束追踪并提交一个可撤销/重做的网格修改操作。必须在事务（Transaction）上下文中调用。 | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |
| `Stash Debug Mesh` | 将当前网格状态以指定名称存储到全局调试存储中，便于调试。 | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |
| `Fetch Debug Mesh` | 从全局调试存储中按名称获取之前存储的网格状态。 | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |
| `Mark For Mesh Rebuild` | 标记一个 `AGeneratedDynamicMeshActor` 需要重新生成其网格。 | `AGeneratedDynamicMeshActor` |
| `Copy Properties To Static Mesh` | 将 `AGeneratedDynamicMeshActor` 的属性复制到一个 `AStaticMeshActor`。 | `AGeneratedDynamicMeshActor` |
| `Copy Properties From Static Mesh` | 从一个 `AStaticMeshActor` 复制属性到 `AGeneratedDynamicMeshActor`。 | `AGeneratedDynamicMeshActor` |

### 使用示例（蓝图描述）

**示例1：在编辑器中生成细分曲面**
1.  创建一个 `AGeneratedDynamicMeshActor` 的蓝图子类。
2.  在蓝图中，实现 `OnRebuildGeneratedMesh` 事件。
3.  在该事件图表中，首先使用 `Begin Tracked Mesh Change` 节点开始追踪。
4.  接着，使用 `Apply Polygroup Catmull Clark SubD` 节点对传入的 `TargetMesh` 进行细分。
5.  最后，使用 `Emit Tracked Mesh Change` 节点提交修改。这样，网格的生成和修改就具备了撤销/重做功能。

**示例2：打包纹理通道**
1.  准备四张纹理（例如：Roughness, Metallic, AO, Emissive）。
2.  创建一个 `Channel Pack` 节点。
3.  为 `RChannelSource`、`GChannelSource`、`BChannelSource`、`AChannelSource` 分别设置对应的纹理和通道（例如，将 Roughness 纹理的 R 通道赋给 RChannelSource）。
4.  设置 `OutputSRGB` 选项。
5.  执行节点，将获得一个打包了四个通道信息的新纹理。

## C++ 用法

### 头文件引入

```cpp
// 使用编辑器模块功能时
#include "GeometryScriptingEditorModule.h"
#include "GeometryScript/OpenSubdivUtilityFunctions.h"
#include "GeometryScript/EditorTextureMapFunctions.h"
#include "GeometryScript/EditorDynamicMeshUtilityFunctions.h"
#include "GeometryActors/GeneratedDynamicMeshActor.h"
```

### 基本用法

以下示例展示了如何在 C++ 中使用 `AGeneratedDynamicMeshActor` 和细分函数。
*（注：由于未提供具体测试用例，以下代码基于头文件中的函数签名和文档注释推断编写，旨在展示典型用法模式。）*

```cpp
// MyProceduralMeshActor.h
#pragma once
#include "GeometryActors/GeneratedDynamicMeshActor.h"
#include "MyProceduralMeshActor.generated.h"

UCLASS()
class AMyProceduralMeshActor : public AGeneratedDynamicMeshActor
{
    GENERATED_BODY()
public:
    // 重写网格重建函数
    virtual void RebuildGeneratedMesh(UDynamicMesh* TargetMesh) override;
};

// MyProceduralMeshActor.cpp
#include "MyProceduralMeshActor.h"
#include "GeometryScript/OpenSubdivUtilityFunctions.h"
#include "DynamicMesh/DynamicMesh3.h"

void AMyProceduralMeshActor::RebuildGeneratedMesh(UDynamicMesh* TargetMesh)
{
    if (!TargetMesh) return;

    // 1. 开始追踪网格变更（用于撤销/重做）
    FGeometryScriptChangeTracker ChangeTracker;
    UGeometryScriptLibrary_EditorDynamicMeshFunctions::BeginTrackedMeshChange(TargetMesh, ChangeTracker);

    // 2. 在网格上执行操作（例如，创建一个基础形状，然后细分）
    // 假设 TargetMesh 已经包含一个基础网格
    int32 SubdivisionLevel = 2;
    FGeometryScriptGroupLayer GroupLayer; // 使用默认分组层
    UGeometryScriptLibrary_OpenSubdivFunctions::ApplyPolygroupCatmullClarkSubD(
        TargetMesh,
        SubdivisionLevel,
        GroupLayer,
        nullptr // Debug
    );

    // 3. 提交变更
    UGeometryScriptLibrary_EditorDynamicMeshFunctions::EmitTrackedMeshChange(TargetMesh, ChangeTracker);
}
```

### 进阶用法

结合资产创建功能，将生成的网格保存为静态网格资产。
*（注：`CreateNewStaticMeshFromDynamicMesh` 函数位于 `GeometryScriptingCore` 模块，此处为演示完整流程。）*

```cpp
// 在某个编辑器工具函数中
#include "GeometryScript/CreateNewAssetUtilityFunctions.h" // 假设此头文件包含资产创建函数
#include "AssetRegistry/AssetRegistryModule.h"

void SaveMeshAsAsset(UDynamicMesh* SourceMesh, const FString& AssetPath, const FString& AssetName)
{
    FGeometryScriptCreateNewStaticMeshAssetOptions Options;
    Options.bEnableNanite = true;
    Options.bEnableCollision = true;

    // 创建静态网格资产
    UStaticMesh* NewStaticMesh = UGeometryScriptLibrary_CreateNewAssetFunctions::CreateNewStaticMeshFromDynamicMesh(
        SourceMesh,
        AssetPath,
        AssetName,
        Options
    );

    if (NewStaticMesh)
    {
        // 通知资产注册表
        FAssetRegistryModule::AssetCreated(NewStaticMesh);
        UE_LOG(LogTemp, Log, TEXT("Successfully created StaticMesh asset: %s"), *NewStaticMesh->GetPathName());
    }
}
```

## Demo 示例

一个最小的编辑器内程序化网格生成器示例。

**1. 头文件 (MyDemoMeshGenerator.h)**
```cpp
#pragma once
#include "GeometryActors/GeneratedDynamicMeshActor.h"
#include "MyDemoMeshGenerator.generated.h"

UCLASS(Blueprintable)
class AMyDemoMeshGenerator : public AGeneratedDynamicMeshActor
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Demo")
    int32 GridSize = 10;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Demo")
    float CellSize = 100.0f;

protected:
    virtual void RebuildGeneratedMesh(UDynamicMesh* TargetMesh) override;
};
```

**2. 源文件 (MyDemoMeshGenerator.cpp)**
```cpp
#include "MyDemoMeshGenerator.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/MeshNormals.h"
#include "Operations/MeshPlaneCut.h"

void AMyDemoMeshGenerator::RebuildGeneratedMesh(UDynamicMesh* TargetMesh)
{
    if (!TargetMesh) return;

    // 获取底层的 FDynamicMesh3 进行操作
    FDynamicMesh3& Mesh = TargetMesh->GetMeshRef();
    Mesh.Clear();

    // 生成一个简单的网格平面
    const int32 VertsX = GridSize + 1;
    const int32 VertsY = GridSize + 1;
    for (int32 y = 0; y < VertsY; ++y)
    {
        for (int32 x = 0; x < VertsX; ++x)
        {
            FVector3d Position(x * CellSize, y * CellSize, 0.0);
            Mesh.AppendVertex(Position);
        }
    }

    // 生成三角形
    for (int32 y = 0; y < GridSize; ++y)
    {
        for (int32 x = 0; x < GridSize; ++x)
        {
            int32 v00 = y * VertsX + x;
            int32 v10 = v00 + 1;
            int32 v01 = (y + 1) * VertsX + x;
            int32 v11 = v01 + 1;

            Mesh.AppendTriangle(v00, v01, v10);
            Mesh.AppendTriangle(v10, v01, v11);
        }
    }

    // 计算法线
    UE::Geometry::FMeshNormals::QuickComputeVertexNormals(Mesh);
}
```

**3. Build.cs 依赖**
```csharp
using UnrealBuildTool;

public class MyGameModule : ModuleRules
{
    public MyGameModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "GeometryScriptingCore", // 核心运行时模块
            "GeometryScriptingEditor" // 编辑器模块（用于AGeneratedDynamicMeshActor）
        });
    }
}
```

## 模块依赖

要使用 Geometry Script 插件，你的项目模块需要依赖以下模块（除了常见的 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `GeometryScriptingCore` | 提供核心的运行时几何脚本函数库（如网格操作、布尔运算等）。 |
| `GeometryScriptingEditor` | 提供编辑器专用的功能，如细分、纹理处理、资产创建、程序化生成管理。 |
| `GeometryProcessing` | 底层的几何处理算法库，被 GeometryScriptingCore 依赖。 |
| `MeshModelingToolset` | 提供网格建模工具集，可能被某些高级功能依赖。 |
| `PlanarCut` | 提供平面切割功能，可能被某些布尔或切割操作依赖。 |

## 维护状态

### 近期更新

1.  **`3fd4df77cad5`** (2024-XX-XX) - `In geometry script asset creation methods, test that the paths for new assets are valid before attempting to use them #jira UE-314488`
    *   **解读**：修复了一个资产创建相关的 Bug。在创建新资产前，现在会验证路径的有效性，避免了因无效路径导致的错误。这是一个稳定性改进。
2.  **`9803c443cfab`** (2024-XX-XX) - `Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files.`
    *   **解读**：代码维护性更新。添加了内联生成宏，可能用于优化编译或代码组织，不影响功能。
3.  **`2739c3d30ebc`** (2024-XX-XX) - `Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n`
    *   **解读**：代码规范性更新。调整了头文件中的 DLL 导出/导入声明，使其符合最新的编码规范，属于底层维护工作。

### 维护评价

- **创建时间**：2021年9月，是一个相对年轻的插件。
- **最近更新**：最近的提交集中在 Bug 修复和代码规范维护上，表明插件仍在被积极维护和改进。
- **活跃度**：作为 Epic Games 官方维护的核心几何脚本工具，其活跃度很高，是 Unreal Engine 程序化内容创作生态的重要组成部分。
- **已知限制**：作为“运行时”插件，其部分高级编辑器功能（如 `GeometryScriptingEditor` 模块中的函数）仅在编辑器环境下可用。
- **推荐使用**：**强烈推荐**。对于任何需要在蓝图或 Python 中进行程序化网格操作的项目，Geometry Script 都是首选工具。它功能强大、文档（通过代码注释）相对完善，并且由 Epic 官方维护，可靠性高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/geometry-script-in-unreal-engine/) (Unreal Engine 官方文档站)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting/Tests) (如果存在)