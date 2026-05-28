# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、预制件） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD (Universal Scene Description) Importer 插件是 Unreal Engine 与 Pixar USD 生态系统集成的关键组件。它不仅仅是一个简单的文件导入器，而是一个**完整的 USD 资产转换和实例化管线**。

该插件的核心职责是将 USD Stage（包含几何体、材质、动画、变体等信息的复杂场景描述）解析并转换为 Unreal Engine 可识别的原生资产（如 `AStaticMeshActor`、`UMaterial`、`UAnimSequence`、`ALevelSequenceActor` 等），并将其放置到关卡中。它解决了影视和工业设计领域使用 USD 作为通用交换格式，并需要将其无缝引入游戏引擎进行实时渲染和交互的难题。

## 使用场景

*   **影视动画资产管线**：将使用 Maya、Houdini 等 DCC 工具以 USD 格式导出的复杂场景、角色、动画序列导入 Unreal Engine 进行实时预览、影视级渲染（Virtual Production）或过场动画制作。
*   **工业数字孪生**：将 CAD 软件（如 Alias、Catia）或 DCC 工具创建的精密工程模型（如汽车、飞机）通过 USD 导入引擎，用于数字孪生、配置器或培训模拟器。
*   **大规模场景复用**：利用 USD 的变体（Variant）和实例化（Instancing）功能，高效导入和管理包含大量重复资产的复杂场景（如城市、工厂）。
*   **资产更新与迭代**：当 DCC 工具中的原始资产发生变化时，可以通过该插件的重新导入功能，增量更新 Unreal 项目中的资产，保持上下游同步。

## 蓝图用法

该插件主要提供导入设置和过程的蓝图控制。核心控制类是 `UUsdStageImportOptions`，其大部分属性均可在蓝图中读写。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PrimsToImport` | 设置要导入的 USD Prim 路径列表。留空或包含根路径 (`/`) 将导入整个 Stage。 | `UUsdStageImportOptions` |
| `bImportGeometry` | 是否导入几何体（网格体、相机、灯光等）。 | `UUsdStageImportOptions` |
| `bImportMaterials` | 是否导入材质和纹理。 | `UUsdStageImportOptions` |
| `bImportLevelSequences` | 是否将 USD 动画导入为关卡序列资产。 | `UUsdStageImportOptions` |
| `bInterpretLODs` | 是否将命名为“LOD0”、“LOD1”等的 USD 变体集解析为单个静态网格体的不同细节级别。 | `UUsdStageImportOptions` |
| `ExistingAssetPolicy` | 当导入的资产与现有资产冲突时的处理策略（追加、替换、忽略）。 | `UUsdStageImportOptions` |
| `ExistingActorPolicy` | 当导入的 Actor 与现有 Actor 冲突时的处理策略（追加、替换、更新变换、忽略）。 | `UUsdStageImportOptions` |
| `ShowImportOptions` | 弹出一个模态窗口，让用户交互式地设置 `UUsdStageImportOptions` 并预览要导入的 Prim 树。 | `SUsdOptionsWindow` |

### 使用示例（蓝图描述）

1.  **控制导入内容**：在执行导入操作前，获取或创建 `UUsdStageImportOptions` 对象。将其 `PrimsToImport` 属性设置为一个仅包含你想要导入的子树路径的数组（例如 `["/Root/Character", "/Root/Props/Chair"]`）。设置 `bImportGeometry` 和 `bImportMaterials` 为 `true` 或 `false` 来精确控制导入的资产类型。
2.  **处理资产冲突**：在重新导入更新后的 USD 文件前，将 `ExistingAssetPolicy` 设置为 `EReplaceAssetPolicy::Replace`，这样新的网格体和材质会覆盖旧的，保持资产路径不变。
3.  **交互式导入**：调用 `SUsdOptionsWindow::ShowImportOptions` 节点，并传入一个 `UUsdStageImportOptions` 对象和 USD Stage 的引用。这将打开一个窗口，让用户勾选想要导入的 Prim，并实时预览选项。

## C++ 用法

### 头文件引入

```cpp
#include "USDStageImporterModule.h"
#include "USDStageImportOptions.h"
#include "USDStageImportContext.h"
```

### 基本用法

通过模块接口获取 `UUsdStageImporter` 实例，并设置导入上下文来执行文件导入。

```cpp
// 基本用法示例
#include "USDStageImporterModule.h"
#include "USDStageImportOptions.h"
#include "USDStageImportContext.h"

void ImportUsdFile(const FString& UsdFilePath, UWorld* TargetWorld)
{
    // 1. 获取导入器模块
    IUsdStageImporterModule& ImporterModule = IUsdStageImporterModule::Get();
    if (!ImporterModule.IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("USD Stage Importer module is not available."));
        return;
    }
    UUsdStageImporter* Importer = ImporterModule.GetImporter();
    if (!Importer)
    {
        return;
    }

    // 2. 准备导入选项 (UUsdStageImportOptions)
    UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();
    Options->bImportGeometry = true;
    Options->bImportMaterials = true;
    Options->bImportLevelSequences = false;
    Options->PrimsToImport = { TEXT("/MyPrimToImport") }; // 指定要导入的Prim
    Options->ExistingActorPolicy = EReplaceActorPolicy::Append; // Actor冲突策略

    // 3. 构建导入上下文
    FUsdStageImportContext ImportContext;
    ImportContext.ImportOptions = Options;
    ImportContext.World = TargetWorld;
    ImportContext.FilePath = UsdFilePath;
    ImportContext.bIsAutomated = true; // 跳过对话框
    ImportContext.ImportObjectFlags = RF_Transient; // 设置生成对象的标志

    // 4. 初始化上下文并执行导入
    if (ImportContext.Init(
            FPaths::GetBaseFilename(UsdFilePath),
            UsdFilePath,
            TEXT("/Game/Imported/Path"),
            RF_Transient,
            true /* bInIsAutomated */))
    {
        Importer->ImportFromFile(ImportContext);
    }
}
```

### 进阶用法：控制导入过程与利用工具类

```cpp
// 进阶用法：临时禁用Actor导入，并分析Stage
#include "USDStageImportOptions.h"
#include "USDOptionsWindow.h"
#include "Widgets/SUSDStagePreviewTree.h"

void AdvancedImportWorkflow(const FString& UsdFilePath, UWorld* World)
{
    UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();

    // 使用 RAII 类在特定作用域内临时禁用Actor导入
    {
        UsdUtils::FScopedSuppressActorImport SuppressActorImport(Options);
        // 此处 Options->bImportActors 为 false
        // ... 执行一些仅需资产导入的操作，如材质分析 ...
    }
    // 离开作用域后，Options->bImportActors 恢复为之前的值

    // 弹出选项窗口让用户选择 Prim
    bool bUserAccepted = SUsdOptionsWindow::ShowImportOptions(*Options, nullptr);
    if (bUserAccepted)
    {
        // 用户点击了确认，此时Options已被用户修改
        // 可以根据Options中的PrimsToImport进行后续操作
        UE_LOG(LogTemp, Log, TEXT("User chose to import %d prims."), Options->PrimsToImport.Num());

        // ... 构建ImportContext并调用Importer->ImportFromFile(ImportContext); ...
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何通过C++代码触发一次USD文件的导入。

```cpp
// MyUSDImportAction.h
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyUSDImportAction.generated.h"

UCLASS()
class UMyUSDImportAction : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /** 通过代码导入指定的USD文件到游戏关卡中 */
    UFUNCTION(BlueprintCallable, Category = "USD")
    static void ImportUSDFileToLevel(const FString& USDFilePath, UWorld* TargetWorld);
};

// MyUSDImportAction.cpp
#include "MyUSDImportAction.h"
#include "USDStageImporterModule.h"
#include "USDStageImportOptions.h"
#include "USDStageImportContext.h"

void UMyUSDImportAction::ImportUSDFileToLevel(const FString& USDFilePath, UWorld* TargetWorld)
{
    if (!TargetWorld || !FPaths::FileExists(USDFilePath))
    {
        return;
    }

    // 获取导入器
    IUsdStageImporterModule& Module = IUsdStageImporterModule::Get();
    UUsdStageImporter* Importer = Module.GetImporter();
    if (!Importer)
    {
        UE_LOG(LogTemp, Warning, TEXT("USD Importer not available"));
        return;
    }

    // 配置导入选项
    UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();
    Options->bImportGeometry = true;
    Options->bImportMaterials = true;
    Options->bShareAssetsForIdenticalPrims = true; // 合并相同资产

    // 构建导入上下文
    FUsdStageImportContext Context;
    Context.ImportOptions = Options;
    Context.World = TargetWorld;
    Context.FilePath = USDFilePath;
    Context.bIsAutomated = true;
    Context.ImportObjectFlags = RF_Transient;

    // 初始化并导入
    if (Context.Init(FPaths::GetBaseFilename(USDFilePath), USDFilePath, TEXT("/Game/USDImport"), RF_Transient, true))
    {
        Importer->ImportFromFile(Context);
        UE_LOG(LogTemp, Log, TEXT("USD import initiated for: %s"), *USDFilePath);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize USD import context for: %s"), *USDFilePath);
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 分析，该插件具有以下独特依赖：

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | 底层 USD SDK 的 C++ 封装，提供 Stage、Prim、Attribute 等核心类型。 |
| `USDClasses` | 定义了 USD 与 Unreal 之间资产转换的核心类，如 `UUsdAssetCache`、`FUsdInfoCache`。 |
| `USDConverter` | 包含将 USD 资产（几何体、材质等）转换为 Unreal 原生资产的实际逻辑。 |
| `Groom` | 支持将 USD 中的 Groom 数据（毛发、羽毛）转换为 Unreal 的 Groom 资产。 |
| `HairStrandsCore` | Groom 模块依赖的底层毛发渲染系统。 |
| `SparseVolumeTexture` | 支持导入 OpenVDB 体积数据为稀疏体积纹理。 |

**注意**：由于插件包含编辑器相关模块（如 `USDStageEditor`、`USDClassesEditor`），其 `PrivateDependencyModuleNames` 中会包含 `UnrealEd`、`EditorStyle` 等编辑器模块，这些在开发编辑器工具时会用到。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量被截断为浮点数导致的编译警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 新增对分配不依赖于蓝图的 Control Rig 的支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | USD: 修复升级至 USD 26.03 后，当存在 LOD 变体时 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 32 位格式说明符与 64 位参数不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 在烘焙动画轨迹时，现在会处理所有曝光动画帧。 |

### 维护评价

**活跃维护**。尽管插件创建于 2018 年（“老古董”），但其维护状态非常活跃。从最近的提交记录可以看出：
1.  **持续更新**：2026 年内有多次功能性更新和 bug 修复，紧跟上游 USD SDK（如 26.03）的变更。
2.  **功能增强**：不断添加新功能，如对 Control Rig 的支持、对动画烘焙的改进等。
3.  **质量改进**：主动修复编译警告和潜在的数据截断问题，表明对代码质量的关注。
4.  **实验性状态**：`.uplugin` 中 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明 Epic 仍将其视为高级/测试功能，但这恰恰意味着它受到持续关注和投入。

**推荐使用**。对于需要 USD 集成的专业项目（影视、汽车可视化、工业仿真），该插件是不可或缺的核心工具。虽然它是实验性的，但已被 Epic 自身的许多项目（如《黑客帝国：觉醒》技术演示）验证过。使用者应保持对更新日志的关注，因为接口和行为可能随版本迭代而变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/USD-Importer-in-Unreal-Engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)