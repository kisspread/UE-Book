# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（导入配置文件、选项窗口 UI、预览树资源） |
| 模块 | `USDStageImporter` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Stage Importer 模块是 USD Importer 插件的一部分，负责将通用场景描述（USD）文件或舞台数据导入到 Unreal Engine 中。它提供：

- **导入上下文管理** – 通过 `FUsdStageImportContext` 保存导入过程中的全部状态，包括舞台引用、导入选项、资产缓存等。
- **工厂模式支持** – 提供 `UUsdStageAssetImportFactory`（内容浏览器导入）和 `UUsdStageImportFactory`（File > Import into Level）两种工厂，分别处理不同的导入入口。
- **导入选项配置** – 通过 `UUsdStageImportOptions` 控制导入内容（Actor、几何体、材质、动画、Groom、体积纹理、音频等）以及合并策略（替换/追加/忽略）。
- **导入流程核心** – `UUsdStageImporter` 类驱动实际导入逻辑，同时支持重新导入单一资产。
- **导入预览 UI** – `SUsdOptionsWindow` 显示选项窗口，内嵌 `SUsdStagePreviewTree` 以树图形式预览阶段 prim 结构，并允许用户勾选要导入的 prim。
- **自定义细节面板** – `FUsdStageImportOptionsCustomization` 为导入选项提供自定义布局，包含渲染上下文选择、材质用途选择等。

本模块是整个 USD 导入管线的核心编排者，解决了将复杂 USD 文件高效、灵活地转换为 UE 资源的问题。

## 使用场景

- **专业工作室导入管线的搭建** – 动画、VFX、产品设计团队需要定期将 USD 场景、资产、动画导入 Unreal。
- **需要精细控制导入内容** – 仅导入部分 prim、选择材质用途、控制碰撞、导入动画序列等。
- **作为其他工具的数据输入** – 在自定义编辑器工具模块中调用 `UUsdStageImporter::ImportFromFile` 进行批量导入。
- **配合 USD Stage Editor** – 与 `USDStageEditor` 模块协同，允许用户先预览层级再决定导入内容。

## 蓝图用法

该模块的核心功能在 C++ 侧，蓝图可通过 `UUsdStageImportOptions` 以配置方式参与导入流程。

### 导入选项配置

以下属性均为 `BlueprintReadWrite`，可在 `UUsdStageImportOptions` 对象上设置，并会被导入流程读取。

| 属性 | 类型 | 说明 |
|------|------|------|
| `bImportActors` | bool | 是否导入 Actor 层级 |
| `bImportGeometry` | bool | 是否导入几何体 |
| `bImportSkeletalAnimations` | bool | 是否导入骨骼动画（依赖于几何体） |
| `bImportLevelSequences` | bool | 是否导入关卡序列 |
| `bImportMaterials` | bool | 是否导入材质与纹理 |
| `bImportGroomAssets` | bool | 是否导入毛发资产 |
| `bImportSparseVolumeTextures` | bool | 是否导入稀疏体积纹理 |
| `bImportSounds` | bool | 是否导入声音资产 |
| `bImportOnlyUsedMaterials` | bool | 仅导入被使用的材质 |
| `PrimsToImport` | `TArray<FString>` | 要导入的 prim 路径列表，空表示导入全部 |
| `bOverrideStageOptions` | bool | 是否覆盖舞台选项（如起点帧、终点帧） |

> **注意**：蓝图无法直接调用导入动作，但可以在编辑器工具蓝图或脚本中创建 `UUsdStageImportOptions` 实例，然后通过 C++ 插件函数传入。

### 示例（蓝图事件图）

1. 调用 `(CallFunction) 创建 USDStageImportOptions 对象`
2. 设置 `Set Import Geometry = true`、`Set Import Materials = true`
3. 将选项对象作为参数传递给 C++ 函数（如通过蓝图函数库或自定义节点）

## C++ 用法

### 头文件引入

```cpp
#include "USDStageImporter.h"
#include "USDStageImportContext.h"
#include "USDStageImporterModule.h"
#include "USDStageImportOptions.h"
```

### 基本用法 – 导入 USD 文件

使用 `UUsdStageImporter` 对给定的上下文执行导入。通常在编辑器模块中使用。

```cpp
// 参考 USDStageImporter.cpp 中的实现，这里给出典型用法
#include "USDStageImporterModule.h"
#include "USDStageImporter.h"
#include "USDStageImportContext.h"
#include "USDStageImportOptions.h"
#include "Editor.h"

void ImportUsdFile(const FString& FilePath, UWorld* World)
{
    IUsdStageImporterModule& Module = IUsdStageImporterModule::Get();
    UUsdStageImporter* Importer = Module.GetImporter();
    if (!Importer)
    {
        return;
    }

    // 1. 创建导入上下文
    FUsdStageImportContext Context;
    Context.World = World;
    Context.FilePath = FilePath;
    Context.bIsAutomated = false;  // 显示选项窗口
    Context.ImportObjectFlags = RF_Public | RF_Standalone | RF_Transactional;

    // 2. 设置导入选项（可选，若不设置会自动显示选项窗口让用户配置）
    UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();
    Options->bImportGeometry = true;
    Options->bImportMaterials = true;
    Options->bImportActors = true;
    Context.ImportOptions = Options;

    // 3. 执行导入
    Importer->ImportFromFile(Context);

    // 4. 使用导入的资产
    UObject* ImportedAsset = Context.ImportedAsset;
    AActor* SceneActor = Context.SceneActor;  // 场景中生成的 Actor
}
```

**来源**：Engine/Plugins/Importers/USDImporter/Source/USDStageImporter/Private/USDStageImporter.cpp

### 基本用法 – 重新导入单一资产

```cpp
#include "USDStageImporter.h"

void ReimportSingleAsset(UObject* OriginalAsset, const FString& PrimPath)
{
    IUsdStageImporterModule& Module = IUsdStageImporterModule::Get();
    UUsdStageImporter* Importer = Module.GetImporter();

    FUsdStageImportContext Context;
    Context.World = GEditor->GetEditorWorldContext().World();
    // 设置原始资产的文件路径等...

    UObject* OutReimportedAsset = nullptr;
    bool bSuccess = Importer->ReimportSingleAsset(
        Context,
        OriginalAsset,
        PrimPath,
        OutReimportedAsset
    );
}
```

**来源**：Engine/Plugins/Importers/USDImporter/Source/USDStageImporter/Private/USDStageImporter.cpp

### 进阶用法 – 自定义导入选项窗口

```cpp
// 在自定义工具中显示导入选项窗口
#include "USDOptionsWindow.h"

void ShowImportDialog(UObject& OptionsObject)
{
    bool bAccepted = SUsdOptionsWindow::ShowImportOptions(OptionsObject);
    if (bAccepted)
    {
        // 用户确认，继续导入
    }
}
```

**来源**：Engine/Plugins/Importers/USDImporter/Source/USDStageImporter/Public/USDOptionsWindow.h

### 进阶用法 – 预览并选择 prim

```cpp
#include "Widgets/SUSDStagePreviewTree.h"

void SetupPreviewTree(const UE::FUsdStage& Stage)
{
    SUsdStagePreviewTree::FArguments Args;
    TSharedRef<SUsdStagePreviewTree> PreviewTree = SNew(SUsdStagePreviewTree, Stage);
    
    // 通过 PreviewTree->GetSelectedFullPrimPaths() 获取用户勾选的 prim 路径
    TArray<FString> SelectedPrims = PreviewTree->GetSelectedFullPrimPaths();
}
```

**来源**：Engine/Plugins/Importers/USDImporter/Source/USDStageImporter/Public/Widgets/SUSDStagePreviewTree.h

## Demo 示例

以下是一个最小化的控制台/编辑器模块示例，演示如何通过 C++ 导入 USD 文件。假设你有自己的编辑器模块并已依赖 `USDStageImporter`。

### DemoTest.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FUsdImportDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RunImportTest();
};
```

### DemoTest.cpp

```cpp
#include "DemoTest.h"
#include "USDStageImporterModule.h"
#include "USDStageImporter.h"
#include "USDStageImportContext.h"
#include "USDStageImportOptions.h"
#include "Editor.h"

void FUsdImportDemoModule::StartupModule()
{
    // 延迟执行以等待编辑器世界创建
    FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([this](float) -> bool
    {
        RunImportTest();
        return false; // 只执行一次
    }), 1.0f);
}

void FUsdImportDemoModule::ShutdownModule()
{
}

void FUsdImportDemoModule::RunImportTest()
{
    // 获取导入器
    IUsdStageImporterModule& Module = IUsdStageImporterModule::Get();
    UUsdStageImporter* Importer = Module.GetImporter();
    if (!Importer)
    {
        UE_LOG(LogTemp, Error, TEXT("USDStageImporter module not available."));
        return;
    }

    // 准备上下文
    FUsdStageImportContext Context;
    Context.World = GEditor->GetEditorWorldContext().World();
    Context.FilePath = TEXT("C:/MyScene.usd");
    Context.bIsAutomated = true;  // 不显示选项窗口

    // 创建默认选项
    UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();
    Options->bImportActors = true;
    Options->bImportGeometry = true;
    Options->bImportMaterials = true;
    Context.ImportOptions = Options;

    // 执行导入
    Importer->ImportFromFile(Context);

    if (Context.SceneActor)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully imported scene actor: %s"), *Context.SceneActor->GetName());
    }
    if (Context.ImportedAsset)
    {
        UE_LOG(LogTemp, Log, TEXT("Imported asset: %s"), *Context.ImportedAsset->GetName());
    }
}
```

**说明**：此示例依赖 `USDStageImporter` 模块的正确加载（需要启用该插件）。适用于编辑器启动后的自动化测试或工具。

## 模块依赖

`USDStageImporter` 的 `Build.cs` 中需添加以下独特依赖（省略标准 Core/Engine/Slate/UnrealEd 等）：

| 模块 | 用途 |
|---|---|
| `USDSchemas` | 提供 USD 原始数据到 UE 数据类型的转换（几何体、材质、动画等） |
| `USDStage` | 底层 USD 舞台封装，包括舞台打开、保存、prim 访问等 |
| `USDStageEditorViewModels` | 提供预览树等 UI 视图模型（可选，仅编辑器使用） |
| `UnrealUSDWrapper` | USD C++ API 的 UE 封装层 |

> **注意**：若仅使用 `USDStageImporter` 运行时导入功能（非编辑器），仍需依赖 `USDSchemas` 和 `USDStage`。  
> 完整依赖列表通常在 `USDStageImporter.Build.cs` 中，包括 `Core, CoreUObject, Engine, InputCore, Slate, SlateCore, UnrealEd, EditorStyle, PropertyEditor, Projects, DeveloperSettings` 等，因常见已省略。

## 维护状态

### 近期更新

- 2025-10-22 `a1039b21` – USD: Disabled UE allocator in USD for Windows.
- 2025-10-17 `be609b71` – [Backout] - CL47041219
- 2025-10-17 `7ab79237` – USD: Disabled UE allocator in USD for Windows.
- 2025-10-03 `d887bd60` – USD: Use the default collision profile for generated static meshes.
- 2025-10-01 `b4449c58` – Anim In Engine: Fix broken linked anim sequences.

### 维护评价

- **创建时间**：2025-10-01，至今不足一个月，属于全新模块。
- **更新频率**：截至当前仍保持高频率更新（每几天一次 commit），包含功能性修复与改进。
- **活跃度**：非常活跃，由 Epic Games 官方维护。
- **已知问题**：由于处于 Beta 阶段（`IsBetaVersion=true`），API 可能调整，部分功能（如 Groom、音频导入）仍在完善。
- **推荐使用**：✅ 强烈推荐用于需要 USD 工作流的项目，但注意其实验性质，建议在 UE 5.7+ 中使用，并关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Importers/USDImporter/Source/USDTests) (插件内 `USDTests` 模块)
- [官方文档 – USD 导入](https://docs.unrealengine.com/5.7/en-US/importing-usd-files-in-unreal-engine/)