# Geometry Script

> Geometry Script provides a library of functions for creating and editing Meshes in Blueprints and Python

| 属性 | 值 |
|---|---|
| 中文名 | 几何脚本 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产， 材质模板） |
| 模块 | `GeometryScriptingCore` (Runtime), `GeometryScriptingEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryScripting) | |

## 用途

GeometryScripting 插件为 Unreal Engine 提供了一套在蓝图（BluePrint）和 Python 脚本中程序化创建和编辑 **Dynamic Mesh**（动态网格）的函数库。它封装了底层复杂的几何处理算法，将诸如网格布尔运算、细分曲面、网格简化、UV 生成、法线/切线计算等操作转化为蓝图节点，极大地降低了在运行时或编辑器中进行程序化内容生成（PCG）的门槛。其核心目标是让设计师和技术美术无需深入 C++ 代码，就能通过蓝图实现强大的网格生成与修改逻辑。

## 使用场景

- **程序化环境生成**：你需要在运行时根据规则（如瓦片、噪声）动态生成地形、建筑或道具的网格。
- **批量资产处理**：你需要在编辑器中通过脚本批量处理一组静态网格资产，例如统一优化 LOD、重新计算法线或生成简化版本。
- **自定义建模工具**：你想在编辑器中快速开发一个用于特定资产（如管道、树木）的专用生成器原型。
- **数据驱动网格**：你需要从外部数据源（如点云、体素数据）实时构建和更新网格模型。
- **编辑器工具开发**：你需要为关卡设计师创建自定义的编辑器内工具，用于快速放置或修改程序化网格。

## 蓝图用法

Geometry Script 提供了丰富的蓝图节点，主要分布在 `GeometryScript` 分类下。以下按功能分组列出核心节点。

### 核心节点

#### 资产管理与创建 (Asset Management)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Unique New Asset Path Name` | 在指定文件夹下为资产创建一个不重名的路径和名称。 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Create New Static Mesh Asset From Mesh` | 从一个 `UDynamicMesh` 创建并保存一个新的 `UStaticMesh` 资产。 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Create New Static Mesh Asset From Mesh LODs` | 从一组 `UDynamicMesh`（代表不同 LOD 级别）创建并保存一个新的 `UStaticMesh` 资产。 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Create New Skeletal Mesh Asset From Mesh` | 从一个 `UDynamicMesh` 和一个 `USkeleton` 创建并保存一个新的 `USkeletalMesh` 资产。 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Create New Volume From Mesh` | 从一个 `UDynamicMesh` 在世界中创建一个 Volume Actor（如阻挡体积）。 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Create New Texture 2D Asset` | 从一个 `UTexture2D` 创建并保存一个新的纹理资产。 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |

#### 编辑器网格操作与调试 (Editor Mesh Utilities)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Begin Tracked Mesh Change` | 保存 `UDynamicMesh` 的当前状态，用于后续生成可撤销/重做的更改记录。 | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |
| `Emit Tracked Mesh Change` | 在网格被修改后调用，基于之前保存的状态发出更改记录，使其支持撤销操作。 | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |
| `Stash Debug Mesh` | 将当前网格副本保存到全局调试存储中，用于后续分析。 | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |
| `Fetch Debug Mesh` | 从全局调试存储中取回之前保存的网格副本。 | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |

#### 纹理工具 (Texture Utilities)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Channel Pack` | 将最多四个纹理（或常量值）的指定通道（R, G, B, A）打包到一个新的纹理中。 | `UGeometryScriptLibrary_EditorTextureMapFunctions` |

#### 细分曲面 (Subdivision)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Apply Polygroup Catmull Clark SubD` | 对网格应用基于多边形组的 Catmull-Clark 细分曲面。 | `UGeometryScriptLibrary_OpenSubdivFunctions` |
| `Apply Triangle Loop SubD` | 对网格应用基于三角形的 Loop 细分曲面。 | `UGeometryScriptLibrary_OpenSubdivFunctions` |

#### 程序化生成 Actor (Generated Actor)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mark For Mesh Rebuild` | 标记一个 `AGeneratedDynamicMeshActor` 需要重建其网格。 | `AGeneratedDynamicMeshActor` |
| `On Rebuild Generated Mesh` | (蓝图事件) 当 Actor 需要重建其网格时触发，蓝图应在此事件中执行程序化生成逻辑。 | `AGeneratedDynamicMeshActor` |
| `Copy Properties To Static Mesh` | 将动态网格 Actor 的属性复制到一个静态网格 Actor。 | `AGeneratedDynamicMeshActor` |
| `Copy Properties From Static Mesh` | 从一个静态网格 Actor 复制属性到动态网格 Actor。 | `AGeneratedDynamicMeshActor` |

### 使用示例（蓝图描述）

**场景：在蓝图中创建一个程序化网格并保存为静态网格资产。**
1. 使用 `Begin Dynamic Mesh` 节点获取一个 `UDynamicMesh` 对象。
2. 连接一系列 `Append Cube`/`Apply Boolean` 等网格操作节点来构建几何体。
3. 使用 `Create Unique New Asset Path Name` 生成一个在 `/Game/GeneratedMeshes/` 下的唯一资产名。
4. 使用 `Create New Static Mesh Asset From Mesh` 节点，将上一步生成的网格和路径作为输入。
5. 将 `Outcome` 引脚连接到分支节点，根据成功或失败执行不同逻辑。
6. 在蓝图的构造脚本（Construction Script）中调用上述逻辑，并通过 `Mark For Mesh Rebuild` 触发 `OnRebuildGeneratedMesh` 事件以优化编辑器性能。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryScript/GeometryScriptTypes.h" // 核心类型
#include "GeometryScriptingCore.h" // 运行时核心库
#include "GeometryScriptingEditor.h" // 编辑器功能库 (需在 Editor 模块中引入)
```

### 基本用法

以下示例展示如何在 C++ 中使用 Geometry Script 的运行时函数创建一个静态网格资产。
（来源：基于 `UGeometryScriptLibrary_CreateNewAssetFunctions` 的公开接口推断）

```cpp
#include "GeometryScript/GeometryScriptTypes.h"
#include "GeometryScriptingCore.h"
#include "DynamicMesh/DynamicMesh3.h"

void CreateTestStaticMeshAsset()
{
    // 1. 获取或创建一个 UDynamicMesh
    UDynamicMesh* DynamicMesh = NewObject<UDynamicMesh>();
    // ... 此处应有代码向 DynamicMesh 添加几何数据 ...
    // 例如，通过 Geometry Script 的 C++ API 或手动操作 FDynamicMesh3

    // 2. 定义资产保存路径
    FString AssetPath = TEXT("/Game/TestAssets/MyProceduralMesh.MyProceduralMesh");

    // 3. 配置创建选项
    FGeometryScriptCreateNewStaticMeshAssetOptions Options;
    Options.bEnableRecomputeNormals = true;
    Options.bEnableCollision = true;

    // 4. 调用函数创建资产
    UStaticMesh* CreatedMesh = UGeometryScriptLibrary_CreateNewAssetFunctions::CreateNewStaticMeshAssetFromMesh(
        DynamicMesh,
        AssetPath,
        Options,
        EGeometryScriptOutcomePins::Succeeded // 这是一个输出参数，蓝图中通过执行引脚显示
    );

    if (CreatedMesh)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully created Static Mesh asset: %s"), *CreatedMesh->GetName());
    }
}
```

### 进阶用法

以下示例展示如何在编辑器 C++ 代码中，使用 `AGeneratedDynamicMeshActor` 的机制和修改追踪功能，实现一个可撤销的程序化网格编辑操作。

```cpp
#include "GeometryActors/GeneratedDynamicMeshActor.h"
#include "GeometryScript/EditorDynamicMeshUtilityFunctions.h"

void PerformTrackedMeshEditOnActor(AGeneratedDynamicMeshActor* TargetActor)
{
    if (!TargetActor) return;

    UDynamicMesh* Mesh = TargetActor->GetDynamicMeshComponent()->GetDynamicMesh();
    if (!Mesh) return;

    // 1. 开始一个“事务”，这是撤销/重做操作的基础
    FScopedTransaction Transaction(NSLOCTEXT("MyTool", "EditMesh", "Edit Procedural Mesh"));

    // 2. 开始追踪网格变化
    FDynamicMeshChangeContainer ChangeTracker;
    UGeometryScriptLibrary_EditorDynamicMeshFunctions::BeginTrackedMeshChange(Mesh, ChangeTracker);

    // 3. 修改网格 (例如，应用一个平滑操作)
    // ... 调用其他 Geometry Script 函数或直接操作 Mesh->GetMesh() ...

    // 4. 发出变化记录，使其可撤销
    UGeometryScriptLibrary_EditorDynamicMeshFunctions::EmitTrackedMeshChange(Mesh, ChangeTracker);

    // 5. （可选）标记 Actor 需要重建，以更新其显示
    TargetActor->MarkForMeshRebuild(true);
}
```

## Demo 示例

以下是一个完整的、可编译的最小 C++ 示例，展示如何创建一个 `AGeneratedDynamicMeshActor` 的子类，并在其重建事件中生成一个简单的网格。

**MyGeneratedCubeActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GeometryActors/GeneratedDynamicMeshActor.h"
#include "MyGeneratedCubeActor.generated.h"

UCLASS()
class AMyGeneratedCubeActor : public AGeneratedDynamicMeshActor
{
    GENERATED_BODY()

public:
    // 覆写蓝图可实现事件
    virtual void OnRebuildGeneratedMesh_Implementation(UDynamicMesh* TargetMesh) override;

    // 定义一个蓝图可编辑属性来控制立方体大小
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
    float CubeSize = 100.0f;
};
```

**MyGeneratedCubeActor.cpp**
```cpp
#include "MyGeneratedCubeActor.h"
#include "GeometryScript/MeshPrimitiveFunctions.h"

void AMyGeneratedCubeActor::OnRebuildGeneratedMesh_Implementation(UDynamicMesh* TargetMesh)
{
    Super::OnRebuildGeneratedMesh_Implementation(TargetMesh);

    if (!TargetMesh) return;

    // 使用 Geometry Script 节点“Append Box”生成立方体
    FGeometryScriptPrimitiveOptions PrimitiveOptions;
    UGeometryScriptLibrary_MeshPrimitiveFunctions::AppendBox(
        TargetMesh,
        PrimitiveOptions,
        FTransform::Identity, // 变换
        CubeSize, CubeSize, CubeSize // 长宽高
    );
}
```

## 模块依赖

从 Build.cs 分析，要使用此插件的全部功能，你的项目或模块可能需要以下独特依赖：

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供底层的几何处理算法，是此插件的核心依赖。 |
| `MeshModelingToolset` | 提供用于编辑器工具的网格建模基础功能。 |
| `PlanarCut` | 提供平面切割相关的网格操作功能。 |

*注意：此插件还需要标准的 Core/Engine/Slate 等依赖，此处省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `5925f0e4` | GeometryScript: Add validation for DynamicMesh overlay triangle storage coverage to BakeTexture. | 为烘焙纹理功能增加了对动态网格覆盖层三角形存储的验证，提升数据可靠性。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量被截断为浮点数而产生的警告代码。 |
| 2026-05-12 | `6a996b5e` | [Geometry] Fixed auto generated poly group sometimes does not generate subd compatible groups | 修复了自动生成的多边形组有时无法生成兼容细分曲面（SubD）的组的问题。 |
| 2026-04-23 | `9f503464` | Optional rebalance geometry/attribute weight in simplifier | 在网格简化器中增加了可选的几何与属性权重再平衡功能。 |
| 2026-04-15 | `8b93226f` | Add editor-only dynamic mesh processor class, so dataflow geometry script users can access the editor | 添加了仅编辑器的动态网格处理器类，使数据流几何脚本用户能访问编辑器功能。 |

### 维护评价

Geometry Script 是一个 **活跃维护** 的插件。其创建于 2024 年初，相对较新。从 2026 年 4 月至 5 月的近期提交记录来看，更新频率很高（约每月数次），内容涵盖功能新增（如细分兼容性修复、权重平衡选项）、错误修复和 API 扩展。插件由 Epic Games 官方维护，是其几何处理和程序化生成工具链的重要组成部分。

**结论**：该插件功能强大、更新及时，且是官方支持的关键工具，**强烈推荐**在需要进行蓝图或脚本化网格操作的项目中使用。需要注意的是，它默认未启用（`Installed: false`），需要在项目设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryScripting)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/geometry-scripting-in-unreal-engine/) （Unreal Engine 文档搜索关键词 “Geometry Script”）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryScripting/Source/GeometryScriptingCore/Private/Tests) （核心运行时模块测试）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryScripting/Source/GeometryScriptingEditor/Private/Tests) （编辑器模块测试）