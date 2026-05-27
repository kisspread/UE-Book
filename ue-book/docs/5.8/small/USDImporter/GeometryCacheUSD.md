# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，测试资产） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Importer 并非一个简单的文件导入工具。它是一个**深度集成的双向数据交换框架**，为 Unreal Engine 提供了完整的 Universal Scene Description (USD) 支持。其核心价值在于：

1.  **场景层级与资产管理**：通过 `USDStage` 模块，它将 USD 的舞台 (Stage)、图层 (Layer)、图元 (Prim) 等概念映射到 UE 的资产和 Actor 体系中，允许用户以非破坏性的方式导入、浏览和管理复杂的 USD 资产。
2.  **实时流式加载与渲染**：通过 `GeometryCacheUSD` 模块，它可以将 USD 几何体数据流式传输到 UE，并通过专用的 `UGeometryCacheUsdComponent` 进行高效渲染，适用于动画或动态数据的实时预览。
3.  **双向工作流**：通过 `USDExporter` 模块，它支持将 UE 场景或特定资产导出为 USD 格式，实现了与 DCC 工具（如 Maya, Houdini, Blender）的无缝协作流程。
4.  **高度可扩展性**：`USDSchemas` 模块定义了基础的 USD 类型和转换逻辑，为自定义属性和复杂数据类型（如动画、材质）的映射提供了扩展点。

因此，该插件是构建**虚拟制片 (Virtual Production)、大型开放世界、模块化建筑以及需要与外部数字内容创作 (DCC) 工具链紧密集成**的现代游戏和实时体验项目的基础设施。

## 使用场景

*   你在使用 Houdini 或 Maya 制作大型场景或程序化资产，并希望在 UE 中实时预览和迭代 → 使用 `USDStage` 导入 USD 资产，并利用其实时更新功能。
*   你需要在 UE 中播放由外部 DCC 工具生成的复杂角色动画或变形体动画 → 使用 `GeometryCacheUSD` 模块和 `UGeometryCacheUsdComponent` 组件进行流式加载和播放。
*   你的团队需要建立一个以 USD 为中心的资产管线，实现资产在 UE 和多个 DCC 工具之间的无损传递 → 同时使用 `USDImporter`（导入）和 `USDExporter`（导出）模块。
*   你正在开发虚拟制片项目，需要实时加载和组合来自不同部门的 USD 布景、角色和灯光 → `USDStage` 的图层合成 (Composition) 功能是关键。

## 蓝图用法

以下节点主要来源于 `USDStage` 和 `USDStageImporter` 模块提供的蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Stage` | 将一个 USD 文件作为舞台 (Stage) 导入到 UE 项目中，生成对应的资产。 | `UUsdStageImporterBlueprintLibrary` |
| `Create Stage Actor` | 在场景中创建一个 `AUsdStageActor`，用于实时管理和渲染一个 USD 舞台。 | `UUsdStageBlueprintLibrary` |
| `Add Asset References` | 为 `AUsdStageActor` 添加额外的 USD 资产引用，实现多资产组合。 | `UUsdStageBlueprintLibrary` |
| `Get Prim Info` | 获取指定 USD 图元 (Prim) 的基础信息（如类型、名称）。 | `UUsdBlueprintLibrary` |
| `Set Prim Visibility` | 设置 USD 图元在场景中的可见性。 | `UUsdStageBlueprintLibrary` |
| `Export To USD` | 将场景或选定的 Actor 导出为 USD 文件。 | `UUsdExporterBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **导入并创建舞台 Actor**：
    *   创建一个 `File` 变量，指向你的 USD 文件。
    *   从 `UUsdStageImporterBlueprintLibrary` 调用 `Import Stage` 节点，输入 `File` 变量，获得导入后的 `UUsdStageAsset`。
    *   从 `UUsdStageBlueprintLibrary` 调用 `Create Stage Actor` 节点，输入之前获得的 `Stage Asset`，在场景中生成一个 `AUsdStageActor`。
2.  **动态加载和切换 USD 图层**：
    *   获取场景中的 `AUsdStageActor` 引用。
    *   使用 `AUsdStageActor` 自身的 `Set Root Layer` 函数，传入新的 USD 文件路径，即可动态替换或合成舞台内容。
3.  **流式动画播放**：
    *   在场景中添加一个 `UGeometryCacheUsdComponent` 组件。
    *   为其 `Geometry Cache` 属性指定一个通过 USD 导入流程生成的 `UGeometryCacheUsdAsset`。
    *   像使用普通 `UGeometryCacheComponent` 一样调用 `Play` 和 `Stop` 函数来控制动画播放。

## C++ 用法

### 头文件引入

根据你使用的模块引入相应头文件：
```cpp
// 操作 USD 舞台和图元
#include "UsdStage/UsdStageActor.h"
#include "UsdBlueprintLibrary.h"

// 使用 USD 几何缓存
#include "GeometryCacheUSDComponent.h"
#include "GeometryCacheTrackUSD.h"

// 导入和导出功能
#include "UsdStageImporterBlueprintLibrary.h"
#include "UsdExporterBlueprintLibrary.h"
```

### 基本用法

从测试用例中提取的常见操作模式。

**1. 创建并管理 USD 舞台 Actor** (来源: `USDTests` 模块测试)
```cpp
// 在场景中动态生成一个 USD 舞台 Actor
AUsdStageActor* StageActor = GetWorld()->SpawnActor<AUsdStageActor>();
if (StageActor)
{
    // 设置要打开的 USD 文件路径
    StageActor->SetRootLayerPath(TEXT("path/to/your/scene.usd"));
    
    // 获取舞台引用，进行更底层的操作
    UE::FUsdStage Stage = StageActor->GetStage();
    if (Stage)
    {
        // 例如，获取根图元
        UE::FUsdPrim RootPrim = Stage.GetPseudoRoot();
    }
}
```

**2. 读取 USD 几何缓存数据** (来源: `GeometryCacheUSD` 模块)
```cpp
// 假设你有一个 UGeometryCacheTrackUsd 的实例
UGeometryCacheTrackUsd* UsdTrack = ...;
if (UsdTrack && UsdTrack->LoadUsdStage())
{
    FGeometryCacheMeshData MeshData;
    // 在指定时间点获取网格数据
    if (UsdTrack->GetMeshDataAtTime(0.5f /*时间*/, MeshData))
    {
        // 成功获取，使用 MeshData 进行渲染或其他处理
        const TArray<FVector3f>& VertexPositions = MeshData.Positions;
        // ...
    }
    // 使用完毕后释放舞台引用
    UsdTrack->UnloadUsdStage();
}
```

### 进阶用法

结合多个模块实现复杂工作流。

**监听 USD 舞台变化并更新 UE 场景** (组合 `USDStage` 与 `USDSchemas`)
```cpp
// 自定义一个 USchema 派生类来处理特定类型的 Prim (例如，自定义灯光类型)
class UMyLightSchema : public USchema
{
public:
    virtual void UpdatePrim(UPrimitiveComponent* PrimComponent, const UE::FUsdPrim& Prim, const USchema::FUpdateContext& Context) override
    {
        // 从 USD Prim 读取自定义灯光属性
        if (const auto& IntensityAttr = Prim.GetAttribute(TEXT("myLight:intensity")))
        {
            float Intensity = 1.0f;
            IntensityAttr.Get(&Intensity);
            
            // 更新对应的 UE 组件
            if (ULightComponent* LightComp = Cast<ULightComponent>(PrimComponent))
            {
                LightComp->SetIntensity(Intensity);
            }
        }
    }
};

// 在模块启动时注册你的 Schema
UUsdSchemasModule* SchemasModule = FModuleManager::GetModulePtr<UUsdSchemasModule>(TEXT("USDSchemas"));
if (SchemasModule)
{
    SchemasModule->RegisterSchema<UMyLightSchema>();
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个能动态更换 USD 文件的 `AUsdStageActor`。

```cpp
// MyUsdActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "UsdStageActor.h"
#include "MyUsdActor.generated.h"

UCLASS()
class AMyUsdActor : public AActor
{
    GENERATED_BODY()

public:
    AMyUsdActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "USD")
    FFilePath UsdFile;

    UPROPERTY(Transient)
    AUsdStageActor* StageActor;
};

// MyUsdActor.cpp
#include "MyUsdActor.h"
#include "UObject/ConstructorHelpers.h"

AMyUsdActor::AMyUsdActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyUsdActor::BeginPlay()
{
    Super::BeginPlay();

    if (UsdFile.FilePath.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("No USD file specified."));
        return;
    }

    // 在自身位置生成一个 USD Stage Actor
    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = this;
    StageActor = GetWorld()->SpawnActor<AUsdStageActor>(GetActorLocation(), GetActorRotation(), SpawnParams);

    if (StageActor)
    {
        // 设置其根层文件，这会触发加载和场景生成
        StageActor->SetRootLayerPath(UsdFile.FilePath);
        UE_LOG(LogTemp, Log, TEXT("USD Stage Actor created and loading: %s"), *UsdFile.FilePath);
    }
}
```

## 模块依赖

要使用此插件，你的项目模块通常需要依赖以下插件提供的独特模块：

| 模块 | 用途 |
|---|---|
| `USDImporter` | 提供核心的 USD 资产工厂和导入流程入口点。 |
| `USDStage` | 提供 `AUsdStageActor`、舞台管理和实时更新逻辑。 |
| `USDSchemas` | 提供基础 USD 类型定义和数据转换框架。 |
| `GeometryCacheUSD` | 提供 USD 几何体流式加载和 `UGeometryCacheUsdComponent`。 |
| `USDExporter` | 提供将 UE 内容导出为 USD 的功能。 |

（注意：`USDStageEditor`、`USDClassesEditor` 等为编辑器模块，在运行时代码中无需依赖。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量转换为单精度浮点数时产生的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD 功能更新：支持分配独立于蓝图的控制绑定 (Control Rig)。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD values change. | USD 功能更新：绕过 USD 26.03 版本更新导致的动画查询内部引用在 LOD 值变化时失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式说明符：当参数是 64 位时，将 32 位格式符改为 64 位，反之亦然。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD 功能更新：烘焙曝光动画轨道的所有帧。 |

### 维护评价

*   **活跃维护**：该插件**处于积极开发和维护中**。从 2026 年的提交记录可以看出，Epic 团队仍在持续为其添加新功能（如 Control Rig 支持）并修复与 USD SDK 新版本兼容性的问题。
*   **功能成熟**：尽管 .uplugin 标记为 `IsBetaVersion: true`，但从其庞大的模块规模（9个模块）和丰富的功能（双向交换、流式缓存、自定义 Schema）来看，它已是一个相当成熟和复杂的系统，是 Epic 内部众多大型项目（如《黑客帝国：觉醒》）的技术基础。
*   **实验性标签**：`IsBetaVersion: true` 和 `EnabledByDefault: false` 标签表明，虽然功能强大，但其 API 和行为在未来版本中仍可能发生变化，且需要用户手动启用。
*   **推荐使用**：**强烈推荐**用于任何需要与 USD 工作流深度集成、处理大型动态场景或追求好莱坞级别生产管线的严肃项目。对于简单的一次性模型导入，UE 自带的 FBX/OBJ 导入器可能更直接。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)