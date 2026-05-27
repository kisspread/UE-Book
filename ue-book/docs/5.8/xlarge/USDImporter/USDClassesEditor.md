# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

此插件为 Unreal Engine 提供了对 **Universal Scene Description (USD)** 文件格式的完整支持。USD 是由皮克斯创建的开放标准，用于在不同数字内容创建 (DCC) 应用程序之间交换复杂的 3D 场景、几何体、动画和材质数据。该插件不仅仅是一个简单的导入器，它还提供了一个完整的**运行时 USD Stage** 概念，允许用户在编辑器中实时查看、编辑和操控 USD 资产的层次结构，就像在其他 DCC 软件中一样。此外，它还包含了用于导出 UE 资产到 USD 格式的功能，以及将 USD 数据缓存为引擎内部资产以优化性能的系统。

## 使用场景

- **影视与虚拟制片**：将 USD 格式的复杂场景、灯光和摄像机设置从 Maya、Houdini 或 Nuke 导入到 UE 中进行实时渲染和虚拟制片。
- **游戏开发**：导入由美术团队在 DCC 软件中制作的角色、道具和环境资产，并利用运行时 Stage 功能在编辑器中调整层次和预览。
- **动画工作流**：通过 USD 导入复杂的角色动画、骨骼绑定和动画曲线，并利用 `GeometryCacheUSD` 模块缓存动画数据。
- **跨平台资产交换**：作为标准化的资产交换管道，与使用 USD 的其他工作室或软件进行协作。
- **程序化内容生成**：在 C++ 中利用 USD 库直接读取或生成 USD 文件，用于程序化内容创作。

## 蓝图用法

USD Importer 插件的核心功能（如解析 USD Stage、处理 Schemas）主要在 C++ 层实现。其公开的蓝图 API 主要集中在**资产编辑器和内容浏览器交互**上。通过 `USDClassesEditor` 模块，该插件扩展了编辑器行为。

### 核心节点

由于该插件专注于底层资产导入和编辑器集成，公开的蓝图节点较少。主要功能通过**编辑器上下文菜单**（如“导入”）和**资产编辑器**访问。用户可以通过蓝图调用标准的 `UKismetSystemLibrary::ImportAsset` 或在 C++ 中使用 `UAssetImportTask` 来触发导入，但具体解析逻辑由 USDImporter 内部处理。

### 使用示例（蓝图描述）

1.  **导入 USD 文件**：在“内容浏览器”中右键单击，选择“导入”，在文件类型中选择 `*.usd`, `*.usda`, `*.usdc`, `*.usdz` 文件，然后配置导入选项。
2.  **编辑 USD 资产**：双击一个已导入的 USD 资产（如 `UUsdAssetCache3`），将打开一个属性编辑器面板（由 `FUsdAssetCacheAssetEditorToolkit` 提供），允许您查看和修改缓存的资产引用。
3.  **查看 USD Stage**：USDStage 模块会提供“USD Stage”编辑器窗口，用于可视化和交互式浏览 USD 文件的 Prim 层次结构。

## C++ 用法

该插件的深度使用和集成通常通过 C++ 完成，涉及对 USD 库和 UE 反射系统的交互。

### 头文件引入

```cpp
#include "USDImporter.h" // 插件主模块
#include "UsdStageActor.h" // 如果操作 USD Stage Actor
#include "UsdAssetCache3.h" // 如果使用资产缓存
```

### 基本用法

以下代码展示了如何在 C++ 中程序化地创建一个资产导入任务来导入 USD 文件。

```cpp
// 假设已包含必要头文件
void ImportUsdFile(const FString& UsdFilePath, const FString& DestinationPath)
{
    // 创建导入任务
    UAssetImportTask* ImportTask = NewObject<UAssetImportTask>();
    ImportTask->Filename = UsdFilePath;
    ImportTask->DestinationPath = DestinationPath;
    ImportTask->bReplaceExisting = true;
    ImportTask->bAutomated = true; // 在自动化流程中设置为 true

    // 获取 USD Importer 工厂（FAssetToolsModule 负责查找正确的工厂）
    FAssetToolsModule& AssetToolsModule = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools");
    AssetToolsModule.Get().ImportAssetTasks({ImportTask});

    // 检查导入结果
    if (ImportTask->Result == EImportResult::Succeeded)
    {
        UE_LOG(LogTemp, Log, TEXT("USD 导入成功: %s"), *ImportTask->ImportedObjectPaths[0]);
    }
}
```

*此示例展示了如何利用引擎的资产导入框架，USDImporter 插件注册了 `.usd` 等扩展名对应的工厂类（如 `UUsdAssetCacheFactory`）来处理具体的解析工作。*

### 进阶用法

更高级的用法涉及直接操作 USD Stage Actor 和管理资产缓存，这在动画和程序化工作流中很常见。

```cpp
#include "UsdStageActor.h"
#include "UsdAssetCache3.h"

void SetupUsdStageAndCache(UWorld* World, const FSoftObjectPath& UsdAssetPath)
{
    // 1. 在场景中生成一个 USD Stage Actor
    AUsdStageActor* StageActor = World->SpawnActor<AUsdStageActor>();

    // 2. 加载并设置 USD Stage 资产
    StageActor->SetStageRootPath(UsdAssetPath);

    // 3. 创建并关联一个资产缓存，用于存储导入过程中产生的子资产（如网格、材质）
    UUsdAssetCache3* AssetCache = NewObject<UUsdAssetCache3>(GetTransientPackage(), TEXT("MyUsdCache"));
    StageActor->SetAssetCache(AssetCache);

    // 4. 触发 Stage 重建（将导入 USD 文件内容）
    StageActor->RebuildStage();

    // 此时，StageActor 的世界场景中应该包含了 USD 文件描述的几何体。
    // 所有导入的资产引用（如 UStaticMesh）都存储在 AssetCache 中，便于查找和管理。
}
```

## Demo 示例

以下是一个最小的 C++ 示例，演示如何通过 `FUsdAssetCacheAssetEditorToolkit` 在编辑器中打开一个已存在的 `UUsdAssetCache3` 资产进行编辑。

```cpp
// MyUsdEditor.h
#pragma once
#include "CoreMinimal.h"

class UUsdAssetCache3;
class FUsdAssetCacheAssetEditorToolkit;

class FMyUsdEditor
{
public:
    static void OpenAssetCacheEditor(UUsdAssetCache3* AssetCacheToEdit);
};

// MyUsdEditor.cpp
#include "MyUsdEditor.h"
#include "USDAssetCacheAssetEditorToolkit.h"
#include "UsdAssetCache3.h"

void FMyUsdEditor::OpenAssetCacheEditor(UUsdAssetCache3* AssetCacheToEdit)
{
    if (!AssetCacheToEdit)
    {
        return;
    }

    // 创建编辑器工具包实例
    TSharedRef<FUsdAssetCacheAssetEditorToolkit> Editor = MakeShareable(new FUsdAssetCacheAssetEditorToolkit());

    // 以独立编辑器模式打开
    Editor->Initialize(EToolkitMode::Standalone, TSharedPtr<IToolkitHost>(), AssetCacheToEdit);
}
```

## 模块依赖

从 USDClassesEditor 模块的 `USDClassesEditor.Build.cs` 可以推断其依赖关系。要使用此插件，你的模块可能需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `USDClasses` | 提供核心的 USD 类型定义和反射支持（很可能依赖此模块）。 |
| `USDSchemas` | 提供 USD Schema 到 UE 类型的映射和转换逻辑。 |
| `USDStage` | 提供运行时 USD Stage Actor 和场景表示。 |
| `UnrealEd` | 用于构建编辑器工具包（如资产编辑器）。 |
| `PropertyEditor` | 用于在编辑器中创建属性面板（Details View）。 |

**注意**：由于这是一个大型插件，实际依赖可能更复杂。建议在模块的 `.Build.cs` 文件中显式添加对 `USDClasses`, `USDSchemas`, `USDStage` 等模块的依赖，以访问完整的 USD API。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数导致的警告代码。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD：新增支持分配独立于蓝图的控制绑定（Control Rig）。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD varies. | USD：针对 USD 26.03 版本更新导致的动画查询（AnimQuery）内部引用在LOD变化时失效的问题进行了规避。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串中位宽说明符与参数位宽不匹配的问题（32位用64位，反之亦然）。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：烘焙曝光动画轨道的所有帧。 |

### 维护评价

该插件处于**活跃维护**状态。尽管 `.uplugin` 标记为实验性（`IsBetaVersion: true`）且默认禁用（`EnabledByDefault: false`），但从近期提交记录可以看出，Epic Games 团队仍在持续为其添加新功能（如支持新的绑定系统）、修复底层问题（如 USD 版本兼容性、浮点精度、动画烘焙）并进行优化。最后一次实质性更新在 2026 年初，表明它是一个被积极开发但尚未标记为“稳定”的关键管线工具。

**推荐使用**：对于任何需要与 USD 工作流深度集成的项目，该插件是不可或缺的。用户应意识到其“实验性”状态可能意味着 API 在未来版本中存在变动风险，并确保其使用的 USD 库版本与目标 USD 文件兼容。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/USD/“) (通常可在 Unreal Engine 官网搜索 “USD” 找到)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests) (该插件包含专门的测试模块 `USDTests`)