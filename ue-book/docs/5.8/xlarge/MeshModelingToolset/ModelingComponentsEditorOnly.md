# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

Mesh Modeling Toolset 是一套为 Unreal Engine 编辑器提供**程序化网格创建和编辑能力**的底层基础设施插件。它不仅仅是几个简单的工具，而是构建于**交互式工具框架**之上的一整套系统，旨在解决在编辑器环境中高效、灵活地创建、修改和管理 3D 网格资产的问题。

它主要提供以下核心能力：
1.  **资产创建 API**：提供统一的接口 (`UModelingObjectsCreationAPI`) 用于在编辑器中创建静态网格、纹理、材质等资产，支持自定义路径和创建后回调。
2.  **工具目标 (Tool Target) 系统**：定义了一套抽象接口（如 `IMeshDescriptionProvider`, `IDynamicMeshCommitter`），将不同来源的网格数据（静态网格、骨骼网格、体积、动态网格组件等）标准化为建模工具可以操作的统一数据源和提交器。
3.  **几何操作与转换**：包含细分 (`FSubdividePoly`)、网格到体积的转换 (`DynamicMeshToVolume`) 等算法。
4.  **选择与状态管理**：为编辑器中的几何体选择 (`IGeometrySelector`) 提供支持。

它的存在是为了让诸如 **Modeling Tools (建模模式)** 这样的上层应用能够专注于具体的建模逻辑，而无需关心资产是如何创建、网格数据如何从不同源获取以及修改如何提交回引擎等底层问题。

## 使用场景

-   **你正在开发一个自定义的编辑器建模工具** → 使用此插件提供的 `ModelingComponents` 和 `ModelingOperators` 模块来构建你的工具，利用其标准化的工具目标接口处理网格数据。
-   **你需要在蓝图或 C++ 中程序化创建网格、材质资产** → 使用 `UEditorModelingObjectsCreationAPI` 或 `UE::AssetUtils` 命名空间下的工具函数。
-   **你希望你的工具能够支持编辑静态网格、骨骼网格、体积等多种几何体类型** → 使用工具目标系统 (`UStaticMeshToolTarget`, `USkeletalMeshToolTarget` 等) 来抽象化底层数据源。
-   **你在开发一个需要处理编辑器中 Actor 添加/删除事件的工具** → 使用 `FLevelObjectsObserver`。

## 蓝图用法

核心的资产创建功能暴露给了蓝图系统，主要集中在 `UEditorModelingObjectsCreationAPI` 类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMeshObject` | 根据参数创建一个新的网格对象（静态网格资产、体积或动态网格 Actor） | `UEditorModelingObjectsCreationAPI` |
| `CreateTextureObject` | 创建一个新的 UTexture2D 资产 | `UEditorModelingObjectsCreationAPI` |
| `CreateMaterialObject` | 创建一个新的 UMaterial 资产 | `UEditorModelingObjectsCreationAPI` |
| `CreateNewActor` | 创建一个新的 Actor | `UEditorModelingObjectsCreationAPI` |
| `CreateNewComponentOnActor` | 在现有 Actor 上创建一个新组件 | `UEditorModelingObjectsCreationAPI` |
| `Register` | 将此 API 实例注册到工具上下文 | `UEditorModelingObjectsCreationAPI` (静态) |
| `Find` | 在工具上下文中查找已注册的 API 实例 | `UEditorModelingObjectsCreationAPI` (静态) |
| `Deregister` | 从工具上下文中注销 API 实例 | `UEditorModelingObjectsCreationAPI` (静态) |

### 使用示例（蓝图描述）

1.  **获取 API 实例**：在你的工具或蓝图中，通常需要在开始时调用 `UEditorModelingObjectsCreationAPI::Find` 从当前的 `UInteractiveToolsContext` 中获取已注册的实例。在编辑器模式下，这个实例通常已经存在。
2.  **创建资产**：
    *   配置 `FCreateMeshObjectParams` 结构体，指定要创建的对象类型（如 `EMeshType::StaticMesh`）、网格数据、材质、变换、目标包路径等。
    *   将参数传递给 `CreateMeshObject` 节点。节点会返回一个结果结构体 (`FCreateMeshObjectResult`)，其中包含创建的资产或 Actor 的引用。
3.  **自定义行为**：蓝图可以通过绑定 `OnModelingMeshCreated` 等委托来监听资产创建事件，或覆盖 `GetNewAssetPathNameCallback` 委托来自定义资产保存路径。

## C++ 用法

### 头文件引入

```cpp
#include "EditorModelingObjectsCreationAPI.h" // 用于资产创建
#include "AssetUtils/CreateStaticMeshUtil.h"  // 静态网格创建工具
#include "AssetUtils/CreateSkeletalMeshUtil.h"// 骨骼网格创建工具
#include "ToolTargets/StaticMeshToolTarget.h" // 工具目标相关
#include "ConversionUtils/DynamicMeshToVolume.h" // 转换工具
#include "Selection/StaticMeshSelector.h"     // 选择器
```

### 基本用法

**创建静态网格资产** (来源: `Public/AssetUtils/CreateStaticMeshUtil.h`)
```cpp
using namespace UE::AssetUtils;

// 1. 准备网格数据 (FDynamicMesh3* 或 FMeshDescription*)
const UE::Geometry::FDynamicMesh3* MyDynamicMesh = ...;

// 2. 配置选项
FStaticMeshAssetOptions Options;
Options.NewAssetPath = TEXT("/Game/MyModels/MyFirstSM");
Options.NumSourceModels = 1;
Options.bCreatePhysicsBody = true;
Options.SourceMeshes.DynamicMeshes.Add(MyDynamicMesh);

// 3. 执行创建
FStaticMeshResults Results;
ECreateStaticMeshResult ResultCode = CreateStaticMeshAsset(Options, Results);

if (ResultCode == ECreateStaticMeshResult::Ok)
{
    UStaticMesh* NewMesh = Results.StaticMesh;
    // 成功，使用新网格...
}
```

**获取和使用工具目标** (来源: `Public/ToolTargets/StaticMeshComponentToolTarget.h`)
```cpp
// 假设有一个 UStaticMeshComponent* InComponent
UStaticMeshComponentToolTargetFactory Factory;
FToolTargetTypeRequirements Requirements; // 配置你需要的能力接口

if (Factory.CanBuildTarget(InComponent, Requirements))
{
    UToolTarget* Target = Factory.BuildTarget(InComponent, Requirements);
    
    // 将目标转换为特定接口
    if (IMeshDescriptionProvider* MeshProvider = Cast<IMeshDescriptionProvider>(Target))
    {
        const FMeshDescription* MeshDesc = MeshProvider->GetMeshDescription();
        // 使用 MeshDescription 进行操作...
    }

    // 使用完毕后删除目标
    delete Target;
}
```

### 进阶用法

**组合资产创建与编辑** (来源: 多个 `AssetUtils` 和 `ToolTargets` 类)
```cpp
// 场景：从一个已有的动态网格组件创建新的静态网格资产，并为其应用自定义材质。
using namespace UE::AssetUtils;

// 1. 从组件获取动态网格数据
UDynamicMeshComponent* DynMeshComp = ...;
FDynamicMesh3 SourceMesh = DynMeshComp->GetDynamicMesh(); // 假设存在此方法或类似方法

// 2. 创建材质资产
FMaterialAssetOptions MatOptions;
MatOptions.NewAssetPath = TEXT("/Game/Materials/MyNewMat");
FMaterialAssetResults MatResults;
ECreateMaterialResult MatResult = CreateDuplicateMaterial(BaseMaterial, MatOptions, MatResults);

// 3. 创建静态网格资产并应用材质
if (MatResult == ECreateMaterialResult::Ok)
{
    FStaticMeshAssetOptions SMOptions;
    SMOptions.NewAssetPath = TEXT("/Game/Models/MyModelFromDyn");
    SMOptions.AssetMaterials.Add(MatResults.NewMaterial);
    SMOptions.SourceMeshes.DynamicMeshes.Add(&SourceMesh);
    
    FStaticMeshResults SMResults;
    CreateStaticMeshAsset(SMOptions, SMResults);
}
```

## Demo 示例

以下示例展示如何在 C++ 中创建一个简单的静态网格资产。

**MyMeshCreationActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMeshCreationActor.generated.h"

UCLASS()
class AMyMeshCreationActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMeshCreationActor();

protected:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Demo")
    void CreateSimpleBoxMesh();
};
```

**MyMeshCreationActor.cpp**
```cpp
#include "MyMeshCreationActor.h"
#include "AssetUtils/CreateStaticMeshUtil.h"
#include "DynamicMesh/DynamicMesh3.h"

using namespace UE::Geometry;
using namespace UE::AssetUtils;

AMyMeshCreationActor::AMyMeshCreationActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMeshCreationActor::BeginPlay()
{
    Super::BeginPlay();
    // 可以选择在 BeginPlay 中自动调用创建函数
    // CreateSimpleBoxMesh();
}

void AMyMeshCreationActor::CreateSimpleBoxMesh()
{
    // 1. 创建一个简单的立方体动态网格
    FDynamicMesh3 BoxMesh;
    // ... (此处省略了构建立方体顶点和三角形的代码) ...

    // 2. 配置创建选项
    FStaticMeshAssetOptions Options;
    Options.NewAssetPath = TEXT("/Game/Generated/MySimpleBox");
    Options.NumSourceModels = 1;
    Options.NumMaterialSlots = 1;
    Options.bCreatePhysicsBody = true;
    Options.bGenerateLightmapUVs = true;
    // 将动态网格指针添加到源网格数组
    Options.SourceMeshes.DynamicMeshes.Add(&BoxMesh);

    // 3. 创建资产
    FStaticMeshResults Results;
    ECreateStaticMeshResult Result = CreateStaticMeshAsset(Options, Results);

    if (Result == ECreateStaticMeshResult::Ok)
    {
        UE_LOG(LogTemp, Warning, TEXT("Successfully created static mesh: %s"), *Results.StaticMesh->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create static mesh. Error code: %d"), (int32)Result);
    }
}
```

## 模块依赖

根据 `ModelingComponentsEditorOnly` 模块的 `Build.cs` 文件，使用此插件中的模块时，你的模块可能需要依赖以下不常见的模块：

| 模块 | 用途 |
|---|---|
| `ModelingComponents` | 提供核心的建模组件、工具目标和基础几何数据结构。 |
| `MeshDescription` | UE 的网格描述标准格式，用于网格数据的交换和持久化。 |
| `GeometryCore` | UE 的核心几何库，提供 `FDynamicMesh3` 等基础几何算法和数据结构。 |
| `GeometryFramework` | 提供几何体在场景中的交互式操作框架，如选择、变换等。 |
| `MeshConversion` | 用于在 `FMeshDescription` 和 `FDynamicMesh3` 等不同网格表示之间进行转换。 |
| `DynamicMesh` | 提供 `UDynamicMesh` 等资产和组件，用于运行时可编辑的动态网格。 |
| `SkeletalMeshModifiers` | 用于修改骨骼网格的骨骼和蒙皮数据。 |

**注意**：具体依赖取决于你使用的具体子模块（如 `MeshModelingTools` 还是 `ModelingOperators`）以及你调用的具体功能。请参考对应模块的 `Build.cs` 文件以获取精确列表。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `2cd4fab7` | SReferenceSkeletonTree: preserve selection across RefreshTreeView so unrelated | 优化骨骼树控件，刷新时保持选择状态，避免无关操作影响选择。 |
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 为顶点属性绘制和蒙皮权重绘制工具添加跨编辑模式同步笔刷半径的功能。 |
| 2026-05-26 | `1b791587` | [SkeletalMeshModelingTools] Edit Skeleton tool: route deleted-bone weights to root instead of droppi | 修复骨骼编辑工具中删除骨骼后，其权重正确路由到根骨骼而非丢失的问题。 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构顶点属性绘制工具的笔划累加器，以支持放松笔刷的累加，并修复相关问题。 |
| 2026-05-22 | `27bc20e6` | [GeometrySelection] Skip GroupTopology rebuild on vertex-only edits | 优化几何选择逻辑，当只编辑顶点时跳过组拓扑的重建，提升性能。 |

### 维护评价

**活跃维护**。该插件创建于 2021 年，至今约 3 年历史，从近期提交记录（2026年5月）可见仍在**持续、积极地开发和维护中**。更新内容涵盖功能增强（如笔刷同步）、重要 Bug 修复（如骨骼权重路由）以及性能优化（如跳过不必要的拓扑重建）。由于它是 Unreal Engine **建模模式 (Modeling Tools)** 的核心底层支撑，其稳定性和功能完善度至关重要。Epic Games 显然在持续投入。

**推荐使用**：对于需要在编辑器中进行程序化网格资产创建、修改或开发自定义建模工具的开发者，此插件是强大且可靠的基础。尽管插件本身标记为实验性 (`IsBetaVersion=true`) 且默认未启用，但这通常意味着其 API 可能随着建模模式的迭代而演进，但其核心功能已被证明是可用且必要的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset/Source/MeshModelingTools/Tests) (位于 `MeshModelingTools` 模块内)
- [官方文档 - 建模模式](https://docs.unrealengine.com/5.0/en-US/modeling-mode-in-unreal-engine/) (本插件是其底层实现)