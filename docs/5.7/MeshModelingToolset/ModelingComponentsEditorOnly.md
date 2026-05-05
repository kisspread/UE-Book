# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（工具目标接口、资产创建工具） |
| 模块 | `ModelingComponentsEditorOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

`ModelingComponentsEditorOnly` 模块是 Mesh Modeling Toolset 插件的核心组成部分，专门为 **UE 编辑器环境** 提供底层支持。它解决的核心问题是：**让建模工具能够以统一、抽象的方式与各种不同类型的网格资产（静态网格、骨骼网格、体积等）进行交互**。

这个模块的存在是为了将编辑器特有的功能（如资产创建、撤销/重做支持、LOD 管理）与通用的建模逻辑分离。它提供了一套“工具目标”（Tool Target）接口和工厂，使得上层的建模工具（如雕刻、布尔运算、细分等）无需关心操作对象的具体类型（是 `UStaticMeshComponent` 还是 `USkeletalMeshComponent`），只需通过统一的接口获取网格数据、提交修改、管理材质即可。这极大地简化了工具开发，并确保了编辑器集成（如资产保存、事务支持）的一致性。

## 使用场景

- **你在编辑器中使用建模工具（Modeling Mode）编辑一个静态网格资产**：工具通过 `UStaticMeshComponentToolTarget` 或 `UStaticMeshToolTarget` 获取网格的 `FMeshDescription` 或 `FDynamicMesh3`，进行修改后，再通过同一接口提交回资产。
- **你在编辑器中编辑一个骨骼网格的 LOD**：工具通过 `USkeletalMeshComponentToolTarget` 指定要编辑的 LOD 级别，获取该 LOD 的网格数据进行操作。
- **你创建了一个新的建模工具，需要支持编辑关卡中的体积（Volume）Actor**：你可以使用 `UVolumeComponentToolTarget` 作为操作目标，它会自动处理体积与动态网格之间的转换。
- **你的工具需要在编辑器中创建新的网格、材质或纹理资产**：可以使用 `UE::AssetUtils` 命名空间下的工具函数（如 `CreateDuplicateMaterial`、`SaveGeneratedTexture2DAsset`）来安全地创建和保存资产。

## 蓝图用法

本模块主要提供 C++ 接口和底层服务，**没有直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 节点**。其功能主要被上层的建模工具（如 `MeshModelingTools` 模块中的工具）在 C++ 层面调用。蓝图用户通常通过编辑器中的“建模”模式（Modeling Mode）UI 间接使用这些功能。

## C++ 用法

### 头文件引入

```cpp
#include "ModelingComponentsEditorOnlyModule.h"
// 以及具体的工具目标头文件，例如：
#include "ToolTargets/StaticMeshComponentToolTarget.h"
#include "AssetUtils/CreateMaterialUtil.h"
```

### 基本用法：使用工具目标接口

工具目标（Tool Target）是本模块的核心抽象。以下示例展示了如何获取一个 `UDynamicMeshComponent` 的工具目标，并通过它读取和修改网格数据。

```cpp
// 假设你有一个 UDynamicMeshComponent* MyMeshComponent
// 来源：ToolTargets/DynamicMeshComponentToolTarget.h

// 1. 获取工具目标（通常由工具框架自动管理，此处为演示原理）
UDynamicMeshComponentToolTarget* ToolTarget = NewObject<UDynamicMeshComponentToolTarget>();
ToolTarget->SetComponent(MyMeshComponent);

if (ToolTarget->IsValid())
{
    // 2. 通过工具目标获取动态网格数据
    UE::Geometry::FDynamicMesh3 DynamicMesh = ToolTarget->GetDynamicMesh();
    
    // 3. 对网格进行一些操作（例如，移动顶点）
    for (int VertexID : DynamicMesh.VertexIndicesItr())
    {
        FVector3d Position = DynamicMesh.GetVertex(VertexID);
        Position.Z += 10.0; // 向上移动10个单位
        DynamicMesh.SetVertex(VertexID, Position);
    }
    
    // 4. 将修改后的网格提交回组件
    FDynamicMeshCommitInfo CommitInfo;
    ToolTarget->CommitDynamicMesh(DynamicMesh, CommitInfo);
}
```

### 进阶用法：创建材质资产副本

当工具需要基于现有材质创建新材质时，可以使用资产创建工具。

```cpp
// 来源：AssetUtils/CreateMaterialUtil.h
#include "AssetUtils/CreateMaterialUtil.h"

// 假设 BaseMaterial 是一个 UMaterialInterface*
UMaterialInterface* BaseMaterial = ...; // 例如，从某个组件获取

// 配置创建选项
UE::AssetUtils::FMaterialAssetOptions Options;
Options.NewAssetPath = TEXT("/Game/MyNewMaterial");
Options.bDeferPostEditChange = false; // 立即触发编辑变更

// 准备结果结构
UE::AssetUtils::FMaterialAssetResults Results;

// 创建材质副本
UE::AssetUtils::ECreateMaterialResult Result = UE::AssetUtils::CreateDuplicateMaterial(
    BaseMaterial,
    Options,
    Results
);

if (Result == UE::AssetUtils::ECreateMaterialResult::Ok)
{
    // 成功，Results.NewMaterial 指向新创建的 UMaterial 资产
    UMaterial* NewMaterial = Results.NewMaterial;
    // ... 可以进一步修改新材质的属性
}
```

## Demo 示例

以下是一个最小化的示例，演示如何在编辑器工具中使用 `ModelingComponentsEditorOnly` 模块提供的接口来操作一个静态网格组件。

**MyModelingTool.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "ToolTargets/StaticMeshComponentToolTarget.h"

class FMySimpleModelingTool
{
public:
    void Execute(UStaticMeshComponent* TargetComponent);

private:
    TUniquePtr<UStaticMeshComponentToolTarget> ToolTarget;
};
```

**MyModelingTool.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MyModelingTool.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"

void FMySimpleModelingTool::Execute(UStaticMeshComponent* TargetComponent)
{
    if (!TargetComponent) return;

    // 1. 为目标组件创建工具目标
    ToolTarget = NewObject<UStaticMeshComponentToolTarget>();
    ToolTarget->SetComponent(TargetComponent);

    if (!ToolTarget->IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid tool target"));
        return;
    }

    // 2. 获取网格描述（MeshDescription）
    const FMeshDescription* MeshDescription = ToolTarget->GetMeshDescription();
    if (!MeshDescription) return;

    // 3. 创建一个可修改的副本
    FMeshDescription MeshCopy(*MeshDescription);

    // 4. 简单操作：将所有顶点的 Z 坐标乘以 2
    FStaticMeshAttributes Attributes(MeshCopy);
    TVertexAttributesRef<FVector3f> VertexPositions = Attributes.GetVertexPositions();
    for (FVertexID VertexID : MeshCopy.Vertices().GetElementIDs())
    {
        FVector3f Pos = VertexPositions[VertexID];
        Pos.Z *= 2.0f;
        VertexPositions[VertexID] = Pos;
    }

    // 5. 将修改后的网格提交回资产
    FCommitter Committer;
    ToolTarget->CommitMeshDescription(Committer, MeshCopy);

    UE_LOG(LogTemp, Log, TEXT("Mesh modification committed."));
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2025-10-03 d0354c094658 ModelingTools: Fixed StaticMeshSelector only working on exactly StaticMeshComponents.
- 2025-09-15 107f4ba7df54 Static Mesh LOD: add clamping by MAX_STATIC_MESH_LODS in a few places where static meshes are modified, where it wasn't present. Goal is to close off all code pathways that could allow content to be created that exceeds the LOD count, leading to runtime asserts.
- 2025-08-20 125416b20d77 [SKM ModelingTools] fixed tool target not inheriting LOD from tool target factory

### 维护评价

该模块仍在**积极维护**中。最近的提交（2025年10月）修复了选择器兼容性问题，并加强了LOD数量的验证，以防止运行时断言。这表明 Epic 团队仍在持续改进和稳定建模工具集的基础设施。虽然插件标记为实验性（`IsBetaVersion=true`），但其核心组件（如工具目标）已被广泛用于编辑器建模模式，是相对成熟和可靠的。推荐在开发编辑器内建模工具时使用此模块提供的接口。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset/Source/ModelingComponentsEditorOnly)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset/Tests)