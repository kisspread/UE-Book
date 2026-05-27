# USD Importer

> Adds support for importing the USD file format into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

这个插件为虚幻引擎添加了对 Pixar USD (Universal Scene Description) 文件格式的导入支持。它不仅仅是一个简单的文件导入器，而是一个**完整的 USD 资产管线集成工具**。

核心功能包括：
- **资产导入**：将 USD 文件中的几何体（网格）、材质、纹理、动画（骨骼动画、级别序列）、Groom（毛发）、音频和 OpenVDB 体积（稀疏体积纹理）等资产转换为虚幻引擎原生资产。
- **实时同步**：作为编辑器扩展，允许用户在 UE 编辑器中预览、浏览和选择 USD 阶段（Stage）内的 Prim，并进行导入。
- **管线集成**：支持自定义导入策略、资产缓存、Prim 折叠与合并等高级功能，适配复杂的影视和游戏制作流程。

它的存在是为了填补虚幻引擎与影视级制作工具（如 Maya, Houdini, Katana 等）之间的数据鸿沟，使游戏开发者能够无缝地利用影视资产，或实现跨平台（游戏/影视）的资产共享。

## 使用场景

- 你的美术团队在 Maya 或 Houdini 中创建了复杂的角色、场景或特效，并以 USD 格式导出，你需要将这些资产导入到 UE 的游戏项目中。
- 你需要在虚幻引擎中预览和编辑由 USD 定义的复杂场景层级结构，并选择性地导入部分 Prim。
- 你的项目涉及影视过场动画制作，需要将 USD 格式的场景、动画和摄像机数据导入 UE 的 Sequencer 中进行最终渲染或实时预览。
- 你需要管理不同用途（如代理、渲染）和不同材质上下文（如 Unreal, glTF）下的 USD 资产，并希望在导入时自动处理这些差异。

## 蓝图用法

此插件主要通过 `UUsdStageImportOptions` 类和 `SUsdOptionsWindow` 窗口提供蓝图和编辑器交互接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ShowImportOptions` | 弹出 USD 导入选项窗口，允许用户交互式配置并选择要导入的 Prim。 | `SUsdOptionsWindow` (Static) |
| `GetImporter` | 获取 `UUsdStageImporter` 实例，用于以编程方式执行导入。 | `IUsdStageImporterModule` |
| `GetSelectedFullPrimPaths` | 从预览树控件中获取用户选中的 Prim 完整路径列表。 | `SUsdStagePreviewTree` |

### 使用示例（蓝图描述）

1.  **调用导入选项窗口**：
    创建一个 `UUsdStageImportOptions` 对象。然后调用 `SUsdOptionsWindow::ShowImportOptions` 静态函数，传入该选项对象和要导入的 USD 阶段的引用。函数将弹出一个模态窗口，用户可在其中勾选要导入的数据类型（几何体、材质、动画等）、设置高级选项、并在 USD 阶段树中选择特定的 Prim。窗口关闭后，用户的选择会保存回传入的选项对象中。
2.  **编程式导入**：
    通过 `IUsdStageImporterModule::Get().GetImporter()` 获取导入器。构建一个 `FUsdStageImportContext`，设置好文件路径、导入选项（可以使用刚才配置过的 `UUsdStageImportOptions`）和目标世界。最后调用 `UUsdStageImporter::ImportFromFile` 执行导入。

## C++ 用法

### 头文件引入

```cpp
#include "USDStageImporterModule.h"
#include "USDStageImportOptions.h"
#include "USDStageImporter.h"
#include "USDStageImportContext.h"
```

### 基本用法

以下示例展示了如何以编程方式导入一个 USD 文件到当前关卡。
（来源文件：`Source/USDTests/Private/USDImporterTests.cpp` 中的测试用例逻辑）

```cpp
void ImportUSDToLevel(const FString& UsdFilePath, UWorld* TargetWorld)
{
    // 1. 确保USD导入器模块可用
    if (!IUsdStageImporterModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("USD Importer module is not loaded."));
        return;
    }

    // 2. 配置导入选项
    UUsdStageImportOptions* ImportOptions = NewObject<UUsdStageImportOptions>();
    ImportOptions->bImportGeometry = true;
    ImportOptions->bImportMaterials = true;
    ImportOptions->bImportLevelSequences = true;

    // 3. 初始化导入上下文
    FUsdStageImportContext ImportContext;
    if (!ImportContext.Init(TEXT("MyUSDAsset"), UsdFilePath, TEXT("/Game/USDImports"), RF_Public | RF_Standalone, false))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize USD import context."));
        return;
    }
    ImportContext.ImportOptions = ImportOptions;
    ImportContext.World = TargetWorld;

    // 4. 获取导入器并执行导入
    UUsdStageImporter* Importer = IUsdStageImporterModule::Get().GetImporter();
    if (Importer)
    {
        Importer->ImportFromFile(ImportContext);

        // 导入完成后，ImportContext.ImportedAssets 包含所有新创建的资产
        UE_LOG(LogTemp, Log, TEXT("USD import completed. Imported %d assets."), ImportContext.ImportedAssets.Num());
    }
}
```

### 进阶用法

**使用资产缓存加速重复导入**：
（来源：`UUsdStageImportOptions::ExistingAssetCache` 属性设计）

```cpp
// 假设你已经有一个管理USD资产的缓存对象 UUsdAssetCache3* MyAssetCache
UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();
Options->bUseExistingAssetCache = true;
Options->ExistingAssetCache = MyAssetCache->GetPathName();

// 将此Options对象用于导入上下文，导入器会尝试从MyAssetCache中复用已存在的资产，
// 只有不存在或发生变化的资产才会重新生成。
```

**自定义导入过程中的冲突策略**：
（来源：`UUsdStageImportOptions` 中的 `EReplaceActorPolicy` 和 `EReplaceAssetPolicy`）

```cpp
// 在重新导入时，希望更新已有Actor的变换，但不替换资产
Options->ExistingActorPolicy = EReplaceActorPolicy::UpdateTransform;
Options->ExistingAssetPolicy = EReplaceAssetPolicy::Ignore;
```

## Demo 示例

一个最小的编辑器工具示例，用于在点击按钮时导入USD文件。

**USDImportTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FUSDImportTool
{
public:
    static void RegisterMenus();
    static void ExecuteImportAction();
};
```

**USDImportTool.cpp**
```cpp
#include "USDImportTool.h"
#include "USDStageImporterModule.h"
#include "USDStageImportOptions.h"
#include "USDStageImporter.h"
#include "USDStageImportContext.h"
#include "Misc/Paths.h"

void FUSDImportTool::RegisterMenus()
{
    // 注册到编辑器菜单的逻辑（此处省略）
}

void FUSDImportTool::ExecuteImportAction()
{
    const FString UsdFile = FPaths::ProjectContentDir() / TEXT("TestAssets/MyScene.usda");

    // 创建并配置选项
    UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();
    Options->bImportGeometry = true;
    Options->bImportMaterials = false; // 此次只导入几何体

    // 设置要导入的特定Prim（可选）
    Options->PrimsToImport = { TEXT("/Root/Character") };

    // 初始化上下文
    FUsdStageImportContext Context;
    Context.Init(TEXT("MyImportedCharacter"), UsdFile, TEXT("/Game/Characters/USD"), RF_Public | RF_Standalone, false);
    Context.ImportOptions = Options;

    // 执行导入
    UUsdStageImporter* Importer = IUsdStageImporterModule::Get().GetImporter();
    if (Importer)
    {
        Importer->ImportFromFile(Context);
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，以下模块是 `USDImporter` 插件及其使用者可能需要依赖的非标准模块：

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | 底层的 USD C++ API 封装库，所有 USD 功能的基础。 |
| `USDClasses` | 定义了 USD 相关的核心 UE 类，如 `UUsdAssetCache3`。 |

**注意**：此插件本身由 9 个运行时模块组成，相互之间存在依赖关系。对于二次开发或仅想使用导入功能的插件，通常只需依赖 `USDStageImporter` 模块，它会自动链接所需的核心模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增支持分配独立于蓝图的控制装备，增强了动画绑定的灵活性。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | 解决了 USD 26.03 版本更新导致 LOD 变体集中的 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了 32 位和 64 位格式说明符与参数不匹配的问题，提升了数据正确性。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 改进了曝光动画轨道的处理，现在会烘焙所有帧而非关键帧。 |

### 维护评价

- **年龄与版本**：插件创建于 2018 年，已超过 5 年。`.uplugin` 中 `IsBetaVersion: true`，表明它仍处于 **Beta 测试阶段**。
- **活跃度**：**非常活跃**。从提交记录看，在 2026 年 4 月至 5 月期间有多次实质性功能增强和 bug 修复，表明 Epic 内部仍在积极开发和维护。
- **功能完整性**：功能非常全面，覆盖了 USD 导入、导出、材质解析、动画、物理、Groom 等众多方面，是一个**生产可用级**的工具。
- **已知限制**：作为 Beta 版本，其 API 和功能在不同 UE 版本间可能发生变化。部分功能（如某些 USD 模式）可能还不完全稳定。
- **推荐度**：**强烈推荐**用于任何需要 USD 管线集成的项目。尽管标记为 Beta，但其功能深度和维护强度表明它是虚幻引擎中 USD 支持的核心方案。在生产环境中使用时，建议锁定引擎版本并密切关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)