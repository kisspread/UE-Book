# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、导入器） |
| 模块 | `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `GeometryCacheUSD` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

此插件为 Unreal Engine 提供了完整的 USD (Universal Scene Description) 文件格式导入支持。它不仅仅是一个简单的模型导入器，而是一个复杂的系统，能够将 USD 阶段（Stage）中定义的完整场景层级、几何体、材质、动画、毛发资产、体素体积等数据解析并转换为 Unreal Engine 的原生资产（如 StaticMesh、SkeletalMesh、Material、AnimSequence、LevelSequence、GroomAsset 等）和 Actor 层级。

其核心价值在于建立 DCC 工具（如 Maya, Houdini）与 Unreal Engine 之间高效、准确、可定制的资产交换桥梁。通过精细控制导入过程（如材质解析上下文、LOD 处理、网格合并、冲突策略），用户能够获得符合项目规范的导入结果，是影视、游戏、建筑可视化等领域工作流中处理复杂场景资产的关键组件。

## 使用场景

-   你需要将一个包含复杂材质、动画和场景结构的 USD 文件（例如从 Maya 或 Houdini 导出的）完整导入到 UE5 关卡中。
-   你需要在导入时精确控制哪些资产（几何体、动画、材质等）应该被导入，并可以指定特定的 Prim 路径。
-   你希望导入的资产能够与关卡中已有的 Actor 和资产共存，并能通过策略（替换、忽略、更新变换）处理冲突。
-   你需要利用 USD 的强大特性，如变体集（Variant Sets）、目的（Purposes）、模型层级（Kinds），并将其映射到 UE 的概念（如 LOD 变体、导入目的、网格合并）。
-   你希望建立一个可重用的导入配置（`UUsdStageImportOptions`），并可能将其用于自动化导入流程。

## 蓝图用法

此插件主要通过 `UUsdStageImportOptions` 对象在蓝图中进行配置，并通过 `UUsdStageImporter` 或编辑器操作触发导入过程。

### 核心配置节点（`UUsdStageImportOptions` 属性）

这些属性可以通过蓝图进行读写，通常在显示导入选项窗口前进行设置。

| 属性/函数 | 说明 | 所在类 |
|---|---|---|
| `bImportActors` | 是否在场景中生成 Actor | `UUsdStageImportOptions` |
| `bImportGeometry` | 是否导入几何体（网格、曲线等） | `UUsdStageImportOptions` |
| `bImportSkeletalAnimations` | 是否导入骨骼动画序列 | `UUsdStageImportOptions` |
| `bImportLevelSequences` | 是否导入关卡序列动画 | `UUsdStageImportOptions` |
| `bImportMaterials` | 是否导入材质和纹理 | `UUsdStageImportOptions` |
| `bImportGroomAssets` | 是否导入毛发资产 | `UUsdStageImportOptions` |
| `PrimsToImport` | 指定要导入的 Prim 路径数组。空或包含根路径“/”则导入整个阶段 | `UUsdStageImportOptions` |
| `PurposesToImport` | 位掩码，指定导入具有哪些目的（Purpose）的 Prim | `UUsdStageImportOptions` |
| `NaniteTriangleThreshold` | 面数超过此阈值的静态网格将尝试启用 Nanite | `UUsdStageImportOptions` |
| `RenderContextToImport` | 指定解析材质时使用的渲染上下文 | `UUsdStageImportOptions` |
| `bInterpretLODs` | 是否将名为 “LOD0”, “LOD1”... 的变体集解释为单一 UStaticMesh 的不同 LOD | `UUsdStageImportOptions` |
| `bUsePrimKindsForCollapsing` | 是否根据 Prim 的 Kind 属性决定是否合并子层级 | `UUsdStageImportOptions` |
| `ExistingActorPolicy` | 当导入的 Actor 与现有 Actor 冲突时的策略（追加、替换等） | `UUsdStageImportOptions` |
| `ExistingAssetPolicy` | 当导入的资产与现有资产冲突时的策略 | `UUsdStageImportOptions` |

### 使用示例（蓝图描述）

1.  **显示导入选项窗口**：通常通过调用 `SUsdOptionsWindow::ShowImportOptions` 的蓝图包装节点（如果存在），或直接实例化一个 `UUsdStageImportOptions` 对象，设置其属性，然后将其传递给一个显示选项对话框的函数。
2.  **程序化导入**：可以创建一个 `UUsdStageImporter` 实例，创建并填充 `FUsdStageImportContext` 结构体（包含文件路径、选项等），然后调用 `ImportFromFile` 函数。

## C++ 用法

### 头文件引入

```cpp
#include "USDStageImporter.h"
#include "USDStageImportOptions.h"
#include "USDStageImportContext.h"
```

### 基本用法

以下代码展示了如何通过 C++ 接口触发一次 USD 文件导入。

**来源参考**: `Public/USDStageImporter.h`, `Public/USDStageImportContext.h`

```cpp
// 1. 获取导入器模块实例
IUsdStageImporterModule& ImporterModule = IUsdStageImporterModule::Get();
UUsdStageImporter* Importer = ImporterModule.GetImporter();

// 2. 准备导入上下文
FUsdStageImportContext ImportContext;
bool bSuccess = ImportContext.Init(
    TEXT("MyImportedStage"),      // 对象名称
    TEXT("/Path/To/MyFile.usd"),   // USD文件路径
    TEXT("/Game/ImportedAssets"),  // 包路径
    RF_Public | RF_Standalone,    // 对象标志
    false,                        // 是否为自动化导入
    false,                        // 是否为重新导入
    true                          // 是否允许导入Actor
);

if (bSuccess)
{
    // 3. (可选) 修改导入选项
    if (ImportContext.ImportOptions)
    {
        ImportContext.ImportOptions->bImportMaterials = true;
        ImportContext.ImportOptions->bImportSkeletalAnimations = false;
        // ... 设置其他选项
    }

    // 4. 执行导入
    Importer->ImportFromFile(ImportContext);
}
```

### 进阶用法

可以利用 `UUsdStageImportOptions` 的蓝图可读写特性，在导入前进行精细控制，并在导入后检查结果。

```cpp
// ... (接上文，在成功初始化 ImportContext 后)

// 动态获取并修改选项
if (UUsdStageImportOptions* Options = ImportContext.ImportOptions)
{
    // 仅导入根 Prim 下的特定子树
    Options->PrimsToImport = {TEXT("/Root/Character"), TEXT("/Root/Props")};

    // 设置冲突策略
    Options->ExistingActorPolicy = EReplaceActorPolicy::Replace;
    Options->ExistingAssetPolicy = EReplaceAssetPolicy::Ignore;

    // 根据平台调整Nanite阈值
    if (IsNaniteSupportedPlatform())
    {
        Options->NaniteTriangleThreshold = 50000;
    }
}

Importer->ImportFromFile(ImportContext);

// 导入完成后，可以从上下文中获取结果
AActor* SpawnedSceneActor = ImportContext.SceneActor;
TArray<TObjectPtr<UObject>>& AllImportedAssets = ImportContext.ImportedAssets;

// 用于重新导入单个资产
UObject* AssetToReimport = /* 某个之前导入的资产 */;
UObject* ReimportedAsset = nullptr;
bool bReimportSuccess = Importer->ReimportSingleAsset(
    ImportContext,
    AssetToReimport,
    TEXT("/Root/MyMesh"), // 原始Prim路径
    ReimportedAsset
);
```

## Demo 示例

以下是一个最小的控制台命令示例，用于在编辑器中通过代码导入一个 USD 文件。

**USDImporterDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FUSDImporterDemo
{
public:
    static void ImportUSDFile(const FString& FilePath);
};
```

**USDImporterDemo.cpp**
```cpp
#include "USDImporterDemo.h"
#include "USDStageImporter.h"
#include "USDStageImportContext.h"
#include "Misc/Paths.h"

void FUSDImporterDemo::ImportUSDFile(const FString& FilePath)
{
    if (!IUsdStageImporterModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("USD Stage Importer module is not loaded."));
        return;
    }

    UUsdStageImporter* Importer = IUsdStageImporterModule::Get().GetImporter();
    if (!Importer)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get USD Stage Importer instance."));
        return;
    }

    FUsdStageImportContext ImportContext;
    // 使用文件名作为资产名，导入到与文件相同目录下的一个子文件夹
    FString BaseName = FPaths::GetBaseFilename(FilePath);
    FString PackagePath = FPaths::GetPath(FilePath) / TEXT("Imported");

    if (ImportContext.Init(
        BaseName,
        FilePath,
        PackagePath,
        RF_Public | RF_Transient,
        true, // 自动化，不显示选项窗口
        false,
        true
    ))
    {
        // 自定义一些选项
        ImportContext.ImportOptions->bImportMaterials = true;
        ImportContext.ImportOptions->bImportGeometry = true;
        ImportContext.ImportOptions->bImportActors = true;

        UE_LOG(LogTemp, Log, TEXT("Starting import of: %s"), *FilePath);
        Importer->ImportFromFile(ImportContext);

        if (ImportContext.SceneActor)
        {
            UE_LOG(LogTemp, Log, TEXT("Import completed. Scene Actor: %s"), *ImportContext.SceneActor->GetName());
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize import context for: %s"), *FilePath);
    }
}
```

## 模块依赖

本插件依赖于多个内部 USD 相关模块。

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | 提供对 USD SDK 的底层 C++ 封装和核心类型（如 `FUsdStage`） |
| `USDClasses` | 包含 USD 与 UE 之间的核心资产类型（如 `UUsdAssetCache3`、`UUsdSkelAnimation`）和工具类 |
| `USDGeometry` | 处理 USD 几何体（Mesh）到 UE Mesh 的转换逻辑 |
| `USDSchemas` | 定义并解析 USD Schema（如 `UsdSkel`、`UsdGeom`），并将其映射到 UE 数据 |
| `USDStage` | 管理 USD Stage 的加载、查询和数据提取 |
| `MeshDescription` | (Engine 模块) 用于构建和操作 Mesh 数据，是几何体转换的核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，代码中双精度常量截断为浮点数导致的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 新增对分配独立于蓝图的 Control Rig 的支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | USD: 解决了升级到 26.03 版本后，当处理 LOD 变体时 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化字符串中 32 位与 64 位格式说明符不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 现在可以烘焙曝光动画轨道的所有帧。 |

### 维护评价

USD Importer 是一个**活跃维护**的核心功能插件。创建于 2018 年，至今已有约 6 年历史，但从未停止更新。从近期的提交记录看（截至 2026 年 4-5 月），Epic 团队仍在持续为其添加新功能（如新的 Control Rig 支持）、修复兼容性问题（适配新版 USD 库）、以及优化现有功能（动画烘焙、格式化修复）。

其 `IsBetaVersion = true` 和 `EnabledByDefault = false` 的状态表明，虽然功能强大，但可能仍存在一些边缘情况或 API 会变动，不建议在追求绝对稳定的最终发布版本中未经充分测试就使用。对于开发阶段、内部工具链或对 USD 有强需求的项目，**强烈推荐使用**。它提供了比其他格式（如 FBX）更强大和标准化的场景描述能力。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/USDImporter/) (注：此为示例链接，实际文档请查阅 Epic 官网)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)