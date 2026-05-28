# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD导入支持与UI） |
| 模块 | `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `GeometryCacheUSD` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

该插件为虚幻引擎提供了对 **USD (Universal Scene Description)** 文件格式的完整导入支持。其核心目的不仅仅是加载USD文件，而是将USD场景的层级结构（Prims）、几何体、材质、动画、毛发（Groom）等复杂数据，智能地转换并映射为虚幻引擎中对应的资产和Actor。它解决的关键问题是**专业级、复杂的数字资产交换与协作**，确保从DCC（Digital Content Creation）工具链（如Maya, Houdini, Blender）或游戏引擎导出的USD数据能够高效、准确地进入虚幻引擎，并保留其结构、材质绑定和动画数据。

`USDStageImporter`模块是该插件的**核心导入执行器**，负责处理实际的导入流程、用户选项配置以及与编辑器UI的集成。

## 使用场景

-   **影视与虚拟制片**：你需要导入一个包含复杂场景、灯光、相机和动画的USD场景文件（如由Pixar RenderMan或Apple USD工具生成）。
-   **跨引擎资产管道**：你的团队使用USD作为资产交换格式，需要将其它引擎（如Unity）或自定义工具生成的资产批量、可控地导入虚幻。
-   **复杂资产导入**：导入包含大量细分几何体、LOD变体（LOD Variant Sets）、骨骼动画、毛发系统的USD资产，并需要精细控制LOD解析、材质合并和动画根运动。
-   **程序化内容生成**：在运行时或通过蓝图/脚本，以非交互方式（自动化）导入USD阶段，并需要精确控制导入哪些子树（Prims）以及如何处理冲突。
-   **产品设计与建筑可视化**：导入由CAD软件转换而来的高精度USD模型，并希望利用Nanite、细分曲面（Subdivision）等虚幻高级渲染特性。

## 蓝图用法

大部分蓝图功能通过配置`UUsdStageImportOptions`对象以及触发导入流程来实现。

### 核心配置节点 (`UUsdStageImportOptions`)

这些属性均可在蓝图中读写，用于在导入前配置参数。

| 属性分组 | 节点/属性 | 说明 | 所在类 |
|---|---|---|---|
| **数据导入选择** | `bImportActors`, `bImportGeometry`, `bImportLevelSequences`, `bImportMaterials`, `bImportGroomAssets`, `bImportSounds`, `bImportSparseVolumeTextures` | 勾选要导入的数据类型（演员、几何体、序列、材质、毛发、音效、稀疏体积纹理）。 | `UUsdStageImportOptions` |
| **数据导入选择** | `PrimsToImport` | 要导入的Prim路径列表。导入一个Prim将导入其整个子树。列表包含根路径`"/"`则导入整个阶段。 | `UUsdStageImportOptions` |
| **冲突处理策略** | `ExistingActorPolicy` | 枚举，决定当导入的Actor与现有Actor冲突时的行为：`Append`（新增）、`Replace`（替换）、`UpdateTransform`（仅更新变换）、`Ignore`（忽略）。 | `UUsdStageImportOptions` |
| **冲突处理策略** | `ExistingAssetPolicy` | 枚举，决定当导入的资产（如静态网格体）与现有资产冲突时的行为：`Append`（创建带后缀的新资产）、`Replace`（替换）、`Ignore`（忽略）。 | `UUsdStageImportOptions` |
| **处理选项** | `bInterpretLODs` | 是否将名为“LOD0”、“LOD1”等的LOD变体集解释为单个UStaticMesh的不同LOD级别。 | `UUsdStageImportOptions` |
| **处理选项** | `bMergeIdenticalMaterialSlots` | 在网格体合并或解析LOD变体集时，是否合并相同的材质槽。 | `UUsdStageImportOptions` |
| **USD特定选项** | `PurposesToImport` | 位掩码，指定导入具有哪些“用途”（Purpose）的Prim，例如仅导入代理几何体（Proxy）或渲染几何体（Render）。 | `UUsdStageImportOptions` |
| **USD特定选项** | `RenderContextToImport` | 指定解析USD材质时，除通用渲染上下文外使用的着色器集。 | `UUsdStageImportOptions` |
| **USD特定选项** | `NaniteTriangleThreshold` | 静态网格体三角形数超过此阈值时，尝试为其启用Nanite。 | `UUsdStageImportOptions` |
| **USD特定选项** | `bOverrideStageOptions`, `StageOptions` | 是否使用自定义的阶段设置（单位、朝向等）覆盖USD文件自身的设置。 | `UUsdStageImportOptions` |

### 核心功能节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ShowImportOptions` | 静态函数，弹出一个标准的USD导入选项窗口。用户在此窗口中配置选项并选择要导入的Prim子树。返回`true`表示用户点击了“导入”。 | `SUsdOptionsWindow` |
| `GetSelectedFullPrimPaths` | 在用户通过`ShowImportOptions`窗口的预览树选择Prim后，此函数返回用户选中的完整Prim路径列表。 | `SUsdOptionsWindow` |

### 使用示例（蓝图描述）

1.  **显示导入选项并获取用户选择**：
    *   创建一个`UUsdStageImportOptions`对象（例如，使用`Construct Object from Class`节点）。
    *   调用`SUsdOptionsWindow::ShowImportOptions`，将创建的选项对象和一个USD阶段（Stage）引用传入。
    *   该节点会弹出UI。节点执行完成意味着窗口已关闭。
    *   如果`ShowImportOptions`返回`True`，则使用`GetSelectedFullPrimPaths`获取用户在预览树中勾选的Prim路径。
    *   然后，你可以将这些路径设置回`OptionsObject`的`PrimsToImport`属性。

2.  **在蓝图中执行自动化导入**：
    *   创建并配置一个`UUsdStageImportOptions`对象，根据需要设置各项属性（如`bImportActors = false`仅导入资产，`ExistingAssetPolicy = EReplaceAssetPolicy::Replace`等）。
    *   设置`PrimsToImport`为一个特定的子树路径数组，例如`["/Root/Environment"]`。
    *   调用`UUsdStageImporter::ImportFromFile`（需通过`IUsdStageImporterModule::Get().GetImporter()`获取实例），传入一个配置好的`FUsdStageImportContext`（包含文件路径、选项、目标世界等信息）。

## C++ 用法

### 头文件引入

```cpp
#include "USDStageImporter/Public/USDStageImporterModule.h"
#include "USDStageImporter/Public/USDStageImportOptions.h"
#include "USDStageImporter/Public/USDStageImportContext.h"
#include "USDSchemas/Public/UsdStage.h" // 用于 FUsdStage
```

### 基本用法：显示导入窗口并导入

以下代码演示了如何调用标准的导入选项UI，然后根据用户的选择执行导入。

```cpp
// 文件: Source/MyProject/MyUSDImportUtils.cpp
// 假设你已经有一个 UUsdStage* 或 UE::FUsdStage
UE::FUsdStage Stage; // ... 初始化阶段

// 1. 创建导入选项对象 (通常由工厂或上下文持有)
UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();
// 可以在这里设置一些默认选项
Options->bImportGeometry = true;
Options->ExistingAssetPolicy = EReplaceAssetPolicy::Append;

// 2. 弹出导入选项窗口
bool bUserAccepted = SUsdOptionsWindow::ShowImportOptions(
    *Options,
    FText::FromString(TEXT("Import USD Stage")),
    FText::FromString(TEXT("Import")),
    &Stage // 传入阶段以便预览树能展示Prim
);

if (bUserAccepted)
{
    // 3. 用户点击了导入，准备导入上下文
    FUsdStageImportContext ImportContext;
    // 设置导入上下文的关键信息
    ImportContext.FilePath = TEXT("C:/MyScene.usd");
    ImportContext.World = GWorld; // 目标世界
    ImportContext.ImportOptions = Options;
    ImportContext.bIsAutomated = false;
    ImportContext.bReadFromStageCache = true;
    // ... 设置其他需要的上下文成员

    // 4. 获取导入器并执行导入
    IUsdStageImporterModule& ImporterModule = IUsdStageImporterModule::Get();
    UUsdStageImporter* Importer = ImporterModule.GetImporter();
    if (Importer)
    {
        Importer->ImportFromFile(ImportContext);
    }

    // ImportContext 现在包含了导入结果，如 ImportContext.ImportedAssets 数组
}
```

*代码逻辑参考自 `UUsdStageAssetImportFactory::FactoryCreateFile` 和 `UUsdStageImportFactory::FactoryCreateFile`。*

### 进阶用法：自定义回调与处理导入后事件

在更复杂的应用中，你可能需要监控导入过程或对导入的资产进行后处理。可以通过扩展或监听`FUsdStageImportContext`和相关委托来实现。虽然USDStageImporter模块本身未直接暴露大量自定义委托，但导入过程会通过`FUsdStageImportContext`产生各种结果，你可以检查`ImportedAssets`、`TokenizedErrorMessages`等成员。

一个更实际的进阶场景是**重新导入（Reimport）**。你可以利用`UUsdStageImporter::ReimportSingleAsset`函数来更新已导入的单个资产。

```cpp
// 假设我们有一个之前通过USD导入的 UStaticMesh* OriginalMesh
UStaticMesh* OriginalMesh = ...;
FString OriginalPrimPath = TEXT("/Root/Mesh");
FUsdStageImportContext ReimportContext;
// 配置 ReimportContext，与初次导入类似，但 FilePath 可能相同或更新

UUsdStageImporter* Importer = IUsdStageImporterModule::Get().GetImporter();
UObject* ReimportedAsset = nullptr;
bool bSuccess = Importer->ReimportSingleAsset(
    ReimportContext,
    OriginalMesh,
    OriginalPrimPath,
    ReimportedAsset
);

if (bSuccess && ReimportedAsset)
{
    // 处理重新导入成功的资产
    UE_LOG(LogTemp, Log, TEXT("Successfully reimported asset: %s"), *ReimportedAsset->GetName());
}
```

## Demo 示例

以下是一个完整的、可编译的最小C++示例，展示如何在编辑器工具或自定义窗口中触发USD文件的导入。

```cpp
// 文件: Source/MyEditorTool/USDImporterWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SUSDImporterWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SUSDImporterWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    FReply OnImportButtonClicked();
    void OnFileDialogClosed(const TArray<FString>& SelectedFiles, bool bSucceeded);
    void ImportUSDFile(const FString& FilePath);

    // 存储导入选项，可以绑定到UI控件
    UPROPERTY()
    UUsdStageImportOptions* ImportOptions;
};

// 文件: Source/MyEditorTool/USDImporterWidget.cpp
#include "USDImporterWidget.h"
#include "USDStageImporterModule.h"
#include "USDStageImportOptions.h"
#include "USDStageImportContext.h"
#include "USDOptionsWindow.h"
#include "Widgets/Input/SButton.h"
#include "DesktopPlatformModule.h"

void SUSDImporterWidget::Construct(const FArguments& InArgs)
{
    ImportOptions = NewObject<UUsdStageImportOptions>();
    // 可以在这里用Slate代码绑定 ImportOptions 的属性到UI控件

    ChildSlot
    [
        SNew(SButton)
        .Text(FText::FromString(TEXT("Import USD File")))
        .OnClicked(this, &SUSDImporterWidget::OnImportButtonClicked)
    ];
}

FReply SUSDImporterWidget::OnImportButtonClicked()
{
    IDesktopPlatform* DesktopPlatform = FDesktopPlatformModule::Get();
    if (DesktopPlatform)
    {
        void* ParentWindowHandle = FSlateApplication::Get().FindBestParentWindowHandleForDialogs(nullptr);
        TArray<FString> OpenedFiles;
        DesktopPlatform->OpenFileDialog(
            ParentWindowHandle,
            TEXT("Import USD File"),
            TEXT(""),
            TEXT(""),
            TEXT("USD Files (*.usd; *.usda; *.usdc)|*.usd;*.usda;*.usdc"),
            EFileDialogFlags::None,
            OpenedFiles
        );
        if (OpenedFiles.Num() > 0)
        {
            ImportUSDFile(OpenedFiles[0]);
        }
    }
    return FReply::Handled();
}

void SUSDImporterWidget::ImportUSDFile(const FString& FilePath)
{
    // 显示导入选项窗口（带预览树）
    bool bUserAccepted = SUsdOptionsWindow::ShowImportOptions(
        *ImportOptions,
        FText::FromString(TEXT("Import USD")),
        FText::FromString(TEXT("Import")),
        nullptr // 这里没有预先加载的Stage，窗口会自行加载文件
    );

    if (bUserAccepted)
    {
        FUsdStageImportContext ImportContext;
        ImportContext.FilePath = FilePath;
        ImportContext.World = GEditor->GetEditorWorldContext().World();
        ImportContext.ImportOptions = ImportOptions;
        ImportContext.bIsAutomated = false;
        ImportContext.bReadFromStageCache = false; // 因为是全新导入

        IUsdStageImporterModule& ImporterModule = IUsdStageImporterModule::Get();
        UUsdStageImporter* Importer = ImporterModule.GetImporter();
        if (Importer)
        {
            Importer->ImportFromFile(ImportContext);
            // 导入完成，ImportContext.ImportedAssets 包含了所有导入的对象
        }
    }
}
```

## 模块依赖

要使用`USDStageImporter`模块，你的模块需要在`Build.cs`中添加以下依赖。这些是该插件独特且不常见的依赖项。

| 模块 | 用途 |
|---|---|
| `USDStageImporter` | 核心的USD阶段导入功能。 |
| `USDSchemas` | 定义与USD Schema（如UsdGeom, UsdShade等）对应的虚幻类型和解析逻辑。 |
| `USDClasses` | 提供USD相关的基础类，如`UUsdAssetCache2/3`。 |
| `USDStage` | 管理USD Stage在虚幻中的状态和操作。 |
| `UnrealUSDWrapper` | 虚幻对底层USD C++库（如pxr）的包装层。 |
| `USDExporter` | 通常与导入器一同存在，可能共享某些基础类型或数据。 |
| `HairStrandsCore` | 如果你需要支持毛发资产导入，则需要依赖此模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD导入：新增支持分配独立于蓝图的Control Rig。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | USD导入：解决更新到26.03后，当LOD变体...时AnimQuery内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了当参数为64位时使用32位格式说明符，反之亦然的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD导入：烘焙曝光动画轨道的所有帧。 |

### 维护评价

USDImporter插件目前处于**活跃维护**状态。

1.  **创建时间**：插件创建于2018年11月，已有约7年历史，是虚幻引擎USD支持的早期核心组件。
2.  **近期活跃度**：从2026年4月至5月有多次提交，内容涉及功能增强（Control Rig支持）、兼容性修复（USD版本更新）和代码质量改进（警告修复），表明仍在持续更新以适应新特性和USD生态变化。
3.  **实验性状态**：插件`.uplugin`文件中标记为`IsBetaVersion: true`，且`EnabledByDefault: false`。这意味着它**尚未被视为完全稳定**，默认不启用，用户需要手动在项目设置中勾选“USD Importer”插件来开启。API和功能在未来版本中可能发生变化。
4.  **已知限制**：作为实验性功能，可能在处理极端复杂的USD场景或特定第三方DCC工具导出的USD文件时遇到兼容性问题。其依赖的底层USD库版本更新也可能带来短期适配挑战。
5.  **推荐使用**：对于**专业级的USD管线、虚拟制片项目或需要高质量资产交换的工作流**，该插件是目前虚幻引擎官方提供的最完整解决方案，**强烈推荐使用**，但应以实验性功能的心态进行评估和测试。对于简单的资产导入，UE的原生FBX导入可能更直接。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档]()（暂无专门文档链接，可参考UE官方USD概览）
- [测试用例]()（测试用例位于插件内部的`USDTests`模块，路径：`Engine/Plugins/Importers/USDImporter/Source/USDTests/`）