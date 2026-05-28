# USD Exporter

> Adds support for exporting Unreal Engine data to the USD file format.

| 属性 | 值 |
|---|---|
| 中文名 | USD 导出器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、导出配置选项） |
| 模块 | `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDClassesEditor` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime), `GeometryCacheUSD` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

`USDExporter` 模块是 Unreal Engine USD 工具链中的核心导出组件。它并非简单的格式转换器，而是一套完整的系统，旨在将 Unreal Engine 中的各类资产和场景数据高效、可控地导出为 Pixar 的通用场景描述 (USD) 格式。

该模块解决了以下核心问题：
1. **数据互通**：为 Unreal Engine 与支持 USD 的 DCC 工具（如 Houdini、Maya、Nuke 等）及渲染器之间搭建了数据交换的桥梁，支持非破坏性的资产迭代。
2. **场景保真度**：提供丰富的导出选项，确保 Unreal 中的几何体、材质、动画、光照、场景层级等信息在 USD 中得到准确还原。
3. **工作流集成**：支持将 Unreal 的关卡（Level）和关卡序列（Level Sequence）导出为 USD Stage，包含子层（Sublayer）、引用（Reference）、负载（Payload）等高级 USD 概念，便于构建模块化的复杂场景。
4. **元数据传递**：能够将 Unreal 资产上的自定义元数据（通过 `UUsdAssetUserData`）导出为 USD 的自定义属性，实现引擎间的额外信息传递。

它之所以存在，是因为现代影视和游戏制作流程越来越依赖于 USD 作为核心交换格式，Unreal Engine 需要深度集成 USD 以成为生产管线中的关键一环。

## 使用场景

- 你在开发一款面向影视制作的虚拟制片项目，需要将 Unreal 中搭建的虚拟场景和动画导出给后期合成团队使用 → 用 `USDExporter` 导出整个关卡或动画序列。
- 你为一个开放世界游戏准备资产，美术在 Unreal 中调试好材质和光照后，需要将带有完整材质定义的网格体导出回 Maya 进行最终优化 → 用 `USDExporter` 导出静态网格体并烘焙材质。
- 你需要将 Unreal 中一个复杂的植被系统（Foliage）实例导出到 Houdini 中进行程序化处理或分析 → 用 `USDExporter` 和相关的蓝图工具函数。
- 你希望将某个 SkeletalMesh 及其动画数据导出为一个 USD 文件，供其他 DCC 工具编辑 → 用 `USDExporter` 导出 SkeletalMesh 并设置相应选项。

## 蓝图用法

`USDExporter` 模块通过 `UUsdConversionBlueprintLibrary` 提供了大量静态蓝图函数，涵盖了从世界管理到细粒度 USD 操作的方方面面。以下是按功能分组的核心节点。

### 核心节点

#### 世界与关卡工具 (`USD|World utils`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumLevelsToExport` | 计算将要导出的关卡总数（持久关卡+所有子关卡）。 | `UUsdConversionBlueprintLibrary` |
| `StreamInRequiredLevels` | 根据需要流式加载所有将要导出的子关卡。 | `UUsdConversionBlueprintLibrary` |
| `RevertSequencerAnimations` | 撤销已打开的 Sequencer 对关卡中 Actor/组件的影响，恢复其原始状态。 | `UUsdConversionBlueprintLibrary` |
| `ReapplySequencerAnimations` | 在导出后重新应用 Sequencer 的动画状态。 | `UUsdConversionBlueprintLibrary` |
| `GetActorsToConvert` | 获取需要被导出的 Actor 集合。 | `UUsdConversionBlueprintLibrary` |
| `GenerateObjectVersionString` | 生成一个唯一版本标识字符串，用于追踪导出资产的版本，避免重复导出。 | `UUsdConversionBlueprintLibrary` |

#### 层操作工具 (`USD|Layer utils`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `InsertSubLayer` | 在指定父层的指定位置插入一个子层引用。 | `UUsdConversionBlueprintLibrary` |
| `AddReference` | 为某个 Prim 添加对另一个 USD 层或 Prim 的**引用 (Reference)**。 | `UUsdConversionBlueprintLibrary` |
| `AddPayload` | 为某个 Prim 添加对另一个 USD 层或 Prim 的**负载 (Payload)**。 | `UUsdConversionBlueprintLibrary` |
| `MakePathRelativeToLayer` | 将一个绝对路径转换为相对于某个锚点层的相对路径。 | `UUsdConversionBlueprintLibrary` |

#### Prim 操作工具 (`USD|Prim utils`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPrimPathForObject` | 根据一个 Actor 或 Component 对象，推断其在 USD 层级结构中的 Prim 路径。 | `UUsdConversionBlueprintLibrary` |
| `RemoveAllPrimSpecs` | 从指定层中移除某个 Prim 的所有规格（包括变体集内的）。 | `UUsdConversionBlueprintLibrary` |
| `CutPrims` / `CopyPrims` / `PastePrims` | 对 USD Prim 进行剪切、复制和粘贴操作，支持跨层操作。 | `UUsdConversionBlueprintLibrary` |
| `DuplicatePrims` | 复制 Prim，支持指定复制类型（浅拷贝、深拷贝等）。 | `UUsdConversionBlueprintLibrary` |

#### 元数据工具 (`USD|Metadata utils`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetUsdAssetUserData` / `SetUsdAssetUserData` | 获取或设置对象上的 `UUsdAssetUserData` 组件。 | `UUsdConversionBlueprintLibrary` |
| `SetMetadataField` / `GetMetadataField` | 便捷地设置或获取 `UUsdAssetUserData` 中的元数据键值对。 | `UUsdConversionBlueprintLibrary` |

#### 导出上下文 (`Export context`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStageRootLayer` | 设置导出上下文使用的 USD Stage 根层路径。 | `UUsdConversionBlueprintContext` |
| `Convert...Component` | 将各种 Unreal 组件（灯光、网格体、音频、相机等）转换为对应的 USD Prim 数据。 | `UUsdConversionBlueprintContext` |
| `AuthorUnrealMaterialBinding` | 为 USD Mesh Prim 编写指向 Unreal 材质的材质绑定关系。 | `UUsdConversionBlueprintContext` |
| `Cleanup` | 关闭并清理内部打开的 USD Stage，释放资源。 | `UUsdConversionBlueprintContext` |

#### 字符串转换工具 (`USD|Stringify utils`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `StringifyAs...` / `UnstringifyAs...` | 一系列函数，用于将 Unreal 的基础类型（如 `FVector`, `FQuat`, `int32`）序列化为 USD 属性值所要求的字符串格式，或反序列化。 | `UUsdConversionBlueprintLibrary` |

### 使用示例（蓝图描述）

**示例1：导出整个关卡到 USD**
1.  创建一个 `ULevelExporterUSDOptions` 对象（或使用其 CDO）并设置属性：设置 `StageOptions`（如格式为 `usda` 或 `usdc`），配置 `AssetFolder`，决定是否 `bExportSublayers`，设置 `LevelsToIgnore` 等。
2.  调用 `CanExportToLayer` 检查目标路径是否可写。
3.  使用 `GetNumLevelsToExport` 和 `StreamInRequiredLevels` 确保所有需要导出的关卡数据都已加载。
4.  通过文件对话框或指定路径，创建一个 `UAssetExportTask`，将其 `Options` 设置为上一步创建的选项对象，并设置 `Object` 为要导出的 `UWorld`。
5.  调用 `UExporter::RunAssetExport` 执行任务。完成后，使用 `StreamOutLevels` 恢复关卡流状态。

**示例2：批量导出场景中的灯光到新的 USD Stage**
1.  创建一个 `UUsdConversionBlueprintContext` 对象。
2.  调用 `SetStageRootLayer` 并传入一个新文件路径（如 `C:/Exports/Lights.usda`），这会创建一个新的 USD Stage。
3.  使用 `GetActorsToConvert` 获取当前关卡中的 Actor，过滤出 `ALight` 类型的 Actor。
4.  遍历这些灯光 Actor，对其 `LightComponent` 调用 `ConvertLightComponent` 或具体的 `ConvertSpotLightComponent` 等函数，指定 Prim 路径（如 `/SpotLights/Spot1`）。
5.  完成所有转换后，务必调用 `Cleanup` 释放 Stage 引用。

## C++ 用法

### 头文件引入

```cpp
#include "USDExporter/USDConversionBlueprintLibrary.h"
#include "USDExporter/USDConversionBlueprintContext.h"
#include "USDExporter/LevelExporterUSDOptions.h"
#include "USDExporter/USDAssetOptions.h"
```

### 基本用法

**代码来源**: `Public/USDConversionBlueprintContext.h` 及 `Public/LevelExporterUSDOptions.h`。

**1. 使用转换上下文导出组件**
```cpp
// 创建转换上下文对象
UUsdConversionBlueprintContext* ConversionContext = NewObject<UUsdConversionBlueprintContext>();

// 设置要写入的 USD Stage 根层路径
FFilePath StagePath;
StagePath.FilePath = TEXT("C:/Export/MyScene.usda");
ConversionContext->SetStageRootLayer(StagePath);

// 假设我们有一个指向场景中光源组件的指针
UPointLightComponent* PointLight = ...; // 获取或创建
FString PrimPath = TEXT("/Root/Lights/PointLight1");

// 将 Unreal 点光源转换为 USD 数据
bool bSuccess = ConversionContext->ConvertPointLightComponent(PointLight, PrimPath);

// 使用完毕后清理，防止内存泄漏和 Stage 锁定
ConversionContext->Cleanup();
```

**2. 配置并使用导出选项**
```cpp
// 获取关卡导出选项的 CDO (Class Default Object) 进行配置
ULevelExporterUSDOptions* ExportOptions = GetMutableDefault<ULevelExporterUSDOptions>();

// 配置 Stage 选项
ExportOptions->StageOptions.FileFormat = TEXT("usdc"); // 二进制格式，通常更快
ExportOptions->StageOptions.UpAxis = EUsdUpAxis::ZAxis; // 根据目标软件设置轴向

// 配置内部选项
ExportOptions->Inner.AssetFolder.Path = TEXT("C:/Export/Assets");
ExportOptions->Inner.bExportSublayers = true; // 导出子关卡为单独层
ExportOptions->Inner.bExportActorFolders = true; // 使用 Actor 文件夹作为 Prim 组织

// 配置网格体资产选项
ExportOptions->Inner.AssetOptions.bBakeMaterials = true; // 烘焙材质
ExportOptions->Inner.AssetOptions.bUsePayload = true;    // 使用 Payload 优化
ExportOptions->Inner.AssetOptions.MaterialBakingOptions.DefaultTextureSize = FIntPoint(2048, 2048);

// 此时，ExportOptions 可以被传递给 UAssetExportTask 以执行导出
```

### 进阶用法

**1. 处理植被 (Foliage) 导出**
```cpp
// 获取指定关卡的 InstancedFoliageActor
ULevel* TargetLevel = ...; // 目标关卡
AInstancedFoliageActor* FoliageActor = UUsdConversionBlueprintLibrary::GetInstancedFoliageActorForLevel(false, TargetLevel);
if (FoliageActor)
{
    // 获取该 Actor 管理的所有植被类型
    TArray<UFoliageType*> FoliageTypes = UUsdConversionBlueprintLibrary::GetUsedFoliageTypes(FoliageActor);
    for (UFoliageType* Type : FoliageTypes)
    {
        // 获取某植被类型的所有实例变换
        TArray<FTransform> Instances = UUsdConversionBlueprintLibrary::GetInstanceTransforms(FoliageActor, Type, TargetLevel);
        // 这里可以将 Instances 数据手动转换为 USD 的 PointInstancer 等格式
    }
}
```

**2. 管理元数据与版本控制**
```cpp
// 为要导出的资产生成唯一的版本字符串，用于智能增量导出
const UObject* AssetToExport = ...; // 例如一个 UStaticMesh
FString VersionHash = UUsdConversionBlueprintLibrary::GenerateObjectVersionString(AssetToExport, ExportOptions);
// 可以将此 VersionHash 与已导出 USD 文件中的自定义属性进行比较，决定是否需要重新导出

// 设置资产的 USD 元数据
UUsdAssetUserData* AssetUserData = UUsdConversionBlueprintLibrary::GetUsdAssetUserData(AssetToExport);
if (AssetUserData)
{
    UUsdConversionBlueprintLibrary::SetMetadataField(
        AssetUserData,
        TEXT("custom:version"),
        VersionHash,
        TEXT("string"), // 值的类型名
        TEXT(""),       // StageIdentifier，通常自动填充
        TEXT(""),       // PrimPath，通常自动填充
        true           // 触发属性更改事件
    );
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何从 C++ 调用 USDExporter 的 API 导出一个静态网格体。

**USDExporterDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "USDExporterDemo.generated.h"

class UStaticMesh;
class UStaticMeshExporterUSDOptions;

UCLASS()
class UUSDExporterDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    // 子系统初始化
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    // 执行导出的入口函数
    UFUNCTION(BlueprintCallable, Category = "USD Demo")
    bool ExportStaticMeshToUSD(UStaticMesh* Mesh, const FString& OutputFilePath);
};
```

**USDExporterDemo.cpp**
```cpp
#include "USDExporterDemo.h"

// 引入所需的 USD 导出模块头文件
#include "USDExporter/StaticMeshExporterUSD.h"
#include "USDExporter/StaticMeshExporterUSDOptions.h"
#include "USDExporter/USDAssetOptions.h"
#include "Exporters/ExportTask.h"

void UUSDExporterDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // 确保 USD 导出器模块已加载
    FModuleManager::Get().LoadModuleChecked(TEXT("USDExporter"));
}

bool UUSDExporterDemoSubsystem::ExportStaticMeshToUSD(UStaticMesh* Mesh, const FString& OutputFilePath)
{
    if (!Mesh || OutputFilePath.IsEmpty())
    {
        return false;
    }

    // 1. 准备导出选项 (可以预先配置好默认选项)
    UStaticMeshExporterUSDOptions* Options = GetMutableDefault<UStaticMeshExporterUSDOptions>();
    Options->StageOptions.FileFormat = FPaths::GetExtension(OutputFilePath).ToLower() == TEXT("usda") ? TEXT("usda") : TEXT("usdc");
    Options->MeshAssetOptions.bBakeMaterials = true; // 选择烘焙材质
    Options->MeshAssetOptions.bExportStaticMeshSourceData = true; // 优先导出源数据

    // 2. 创建导出任务
    UAssetExportTask* ExportTask = NewObject<UAssetExportTask>();
    ExportTask->Object = Mesh;
    ExportTask->Filename = OutputFilePath;
    ExportTask->Exporter = NewObject<UStaticMeshExporterUsd>();
    ExportTask->bSelected = false;
    ExportTask->bReplaceIdentical = true;
    ExportTask->bAutomated = true; // 自动化模式，不显示UI
    ExportTask->Options = Options; // 将选项附加到任务

    // 3. 执行导出
    UExporter* Exporter = ExportTask->Exporter;
    bool bSuccess = Exporter->RunAssetExport(ExportTask);

    // 清理任务 (UAssetExportTask 是 UObjects，会由 GC 管理，但可以提前清理引用)
    ExportTask->MarkAsGarbage();

    return bSuccess;
}
```

## 模块依赖

要使用 `USDExporter` 模块，你的模块需要在 `Build.cs` 中添加以下依赖项：

| 模块 | 用途 |
|---|---|
| `USDClasses` | 提供 USD 核心类和接口（如 `UUsdAssetUserData`）。 |
| `USDSchemas` | 提供 USD Schema 类型映射（如 `UsdGeomMesh`）。 |
| `USDStage` | 提供 USD Stage 管理核心功能（如 `FUsdStage`）。 |

其他依赖如 `Core`, `CoreUObject`, `Engine`, `UnrealEd`, `Exporters` 等是隐含的或常见的，无需特别列出。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数产生的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 添加对分配独立于蓝图的 Control Rig 的支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD var... | USD: 解决更新到 26.03 版本后，当 LOD 变体切换时 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了当参数为 64 位时格式说明符仍使用 32 位的问题，反之亦然。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 烘焙曝光动画轨道的所有帧。 |

### 维护评价

`USDExporter` 模块自 **2018 年** 创建以来，至今（2026年）仍处于**活跃维护**状态。最近的 Git 提交记录显示，在 2026 年 4 月至 5 月期间有多次重要的功能增强（如 Control Rig 支持）和错误修复（如浮点精度、格式说明符、动画帧烘焙）。这些更新表明 Epic Games 持续投入资源完善 USD 导出功能，以应对不断变化的生产需求。

该模块标记为**实验性**（`IsBetaVersion: true`）且**默认未启用**，这意味着其 API 和功能在未来版本中可能发生变化。然而，鉴于其复杂的特性集和持续的维护，它已是一个相对成熟且用于生产的工具。

**综合评价：推荐使用**。对于需要将 Unreal 数据导出到 USD 管线的用户，这是一个必不可少且不断改进的模块。尽管标记为实验性，但其稳定性和功能完整性已足以支持实际项目。建议关注版本更新日志，以了解 API 的潜在变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)（内部自动化测试）