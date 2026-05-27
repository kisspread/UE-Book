# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD 阶段编辑器 UI、导入/导出逻辑、各种视图模型） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

`USDImporter` 插件为 Unreal Engine 提供了对 Universal Scene Description (USD) 的全面支持。它不仅是一个简单的文件导入器，而是一个完整的工作流程集成套件。其核心目标是解决以下问题：

1.  **资产预览与编辑**：提供一个内置的“USD 阶段编辑器”窗口，允许艺术家和开发者在导入资产前，在 Unreal 内部直接检查、导航和编辑 USD 文件的层次结构、原语 (Prim)、属性 (Attribute) 和变体 (Variant)。
2.  **非破坏性工作流**：通过 `AUsdStageActor` 实现 USD 阶段 (Stage) 的动态加载。用户可以将 USD 文件加载到世界中，并实时切换变体、有效负载 (Payload)、参考 (Reference) 等，而无需每次都执行完整的资产导入。
3.  **双向交换**：除了导入，插件还包含 `USDExporter` 模块，支持将 Unreal 中的关卡、资产导出为 USD 格式，促进了与其他 DCC 工具（如 Maya、Houdini、Blender）的协作。
4.  **管线集成**：通过蓝图和 C++ API 提供深度控制，允许在自动化管线中脚本化 USD 的打开、编辑、导入和导出过程。

简单来说，它是 Unreal 在影视、虚拟制片和大型复杂场景资产管线中与 USD 生态系统对接的关键基础设施。

## 使用场景

-   你正在参与一个使用 Houdini 或 Maya 进行场景布局和建模的电影级项目，需要将 USD 场景导入 Unreal 进行最终渲染和虚拟制片审查。
-   你的资产管线以 USD 为核心，需要频繁地在不同软件间交换资产，并希望保持材质、绑定和动画的完整性。
-   你需要为关卡设计一个基于 USD 的程序化内容生成（PCG）工作流，动态加载和卸载不同的场景组件。
-   你需要通过蓝图脚本批量处理数百个 USD 文件的导入、检查或格式转换。

## 蓝图用法

蓝图功能主要通过 `UUsdStageEditorBlueprintLibrary` 提供，该库封装了 USD 阶段编辑器的全部核心操作。

### 编辑器控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Stage Editor` | 打开或聚焦 USD 阶段编辑器窗口。 | `UUsdStageEditorBlueprintLibrary` |
| `Close Stage Editor` | 关闭已打开的编辑器窗口。 | `UUsdStageEditorBlueprintLibrary` |
| `Is Stage Editor Opened` | 检查编辑器窗口是否已打开。 | `UUsdStageEditorBlueprintLibrary` |

### 阶段演员 (Stage Actor) 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Attached Stage Actor` | 获取当前附加到编辑器的 `AUsdStageActor`。 | `UUsdStageEditorBlueprintLibrary` |
| `Set Attached Stage Actor` | 将一个 `AUsdStageActor` 设置到编辑器中。传入 `None` 可清除。 | `UUsdStageEditorBlueprintLibrary` |

### 选择操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Selected Layer Identifiers` | 获取编辑器中当前选中的图层标识符列表。 | `UUsdStageEditorBlueprintLibrary` |
| `Set Selected Layer Identifiers` | 设置编辑器的图层选择。 | `UUsdStageEditorBlueprintLibrary` |
| `Get Selected Prim Paths` | 获取编辑器中当前选中的原语路径列表。 | `UUsdStageEditorBlueprintLibrary` |
| `Set Selected Prim Paths` | 设置编辑器的原语选择。 | `UUsdStageEditorBlueprintLibrary` |
| `Get Selected Property Names` | 获取右侧属性面板中选中的属性名列表。 | `UUsdStageEditorBlueprintLibrary` |
| `Set Selected Property Names` | 设置属性面板的选择。 | `UUsdStageEditorBlueprintLibrary` |

### 文件与菜单动作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `File New` | 创建一个新的内存图层并将其作为根打开一个 USD 阶段。 | `UUsdStageEditorBlueprintLibrary` |
| `File Open` | 从磁盘文件打开一个 USD 阶段。路径为空时将弹出文件选择对话框。 | `UUsdStageEditorBlueprintLibrary` |
| `File Save` | 保存当前阶段到磁盘。对于未保存的阶段，可指定输出路径。 | `UUsdStageEditorBlueprintLibrary` |
| `File Export All Layers` | 将当前阶段的所有图层导出到新位置。 | `UUsdStageEditorBlueprintLibrary` |
| `File Export Flattened Stage` | 将当前阶段导出为单个“扁平化”的 USD 图层。 | `UUsdStageEditorBlueprintLibrary` |
| `File Reload` | 重新加载当前阶段的所有图层。 | `UUsdStageEditorBlueprintLibrary` |
| `File Close` | 通过清除附加 Stage Actor 的根图层属性来关闭当前阶段。 | `UUsdStageEditorBlueprintLibrary` |
| `Actions Import` | 将当前打开的 USD 阶段导入为持久化的 UE 资产、Actor 和组件。可传入选项对象。 | `UUsdStageEditorBlueprintLibrary` |
| `Export Selected Layers` | 将编辑器中当前选中的图层导出到新位置。 | `UUsdStageEditorBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **自动打开并检查 USD 文件**：
    -   调用 `Open Stage Editor` 确保编辑器窗口打开。
    -   调用 `File Open` 并传入一个 USD 文件路径（如 `"D:/Project/scene.usda"`）。
    -   调用 `Get Selected Prim Paths` 获取根原语路径，或使用 `Set Selected Prim Paths` 定位到某个特定原语（如 `["/Root/Character"]`）。
    -   调用 `Get Selected Property Names` 来检查该原语上有哪些属性。
2.  **编程式导入**：
    -   首先，确保有一个 `AUsdStageActor` 存在于关卡中（可通过 `SpawnActor` 创建）。
    -   调用 `Set Attached Stage Actor` 将该 Actor 附加到编辑器。
    -   调用 `File Open` 打开目标 USD 文件。
    -   （可选）使用选择函数预先检查内容。
    -   最后，调用 `Actions Import`，传入内容浏览器的输出路径（如 `"/Game/Imports"`）和一个 `UUsdStageImportOptions` 对象来配置导入选项。

## C++ 用法

通过 `IUsdStageEditorModule` 接口可以在 C++ 中实现与蓝图相同的功能，但提供了更底层的控制。

### 头文件引入

```cpp
#include "USDStageEditorModule.h"
#include "USDStageEditorBlueprintLibrary.h" // 如需使用蓝图库函数
#include "USDStage/USDStageActor.h"
```

### 基本用法

**获取模块并操作编辑器** (来源: `USDStageEditorBlueprintLibrary.h` 及模块接口推断)

```cpp
// 获取 USD Stage Editor 模块
IUsdStageEditorModule& StageEditorModule = FModuleManager::GetModuleChecked<IUsdStageEditorModule>("USDStageEditor");

// 打开编辑器并检查状态
if (StageEditorModule.OpenStageEditor())
{
    UE_LOG(LogTemp, Log, TEXT("USD Stage Editor 已打开。"));
}

// 获取当前附加的 Stage Actor
AUsdStageActor* CurrentActor = StageEditorModule.GetAttachedStageActor();
if (CurrentActor)
{
    UE_LOG(LogTemp, Log, TEXT("当前 Stage Actor: %s"), *CurrentActor->GetName());
}

// 通过 C++ 打开一个文件（路径为空则弹出对话框）
StageEditorModule.FileOpen(TEXT("C:/MyAssets/Character.usd"));
```

**监听选择变化** (来源: `SUSDStage.h` 事件委托模式)

```cpp
// 假设你有一个对 SUsdStage Widget 的引用 (TSharedPtr<SUsdStage> StageWidget)
// 这通常通过自定义编辑器模块或 Slate Widget 获取。
if (StageWidget.IsValid())
{
    // 绑定原语选择变化的委托
    StageWidget->OnPrimSelectionChanged.BindLambda([this](const TArray<FString>& NewSelection)
    {
        for (const FString& Path : NewSelection)
        {
            UE_LOG(LogTemp, Log, TEXT("选中的原语: %s"), *Path);
        }
    });
}
```

### 进阶用法

**自动化导入流程** (综合使用模块接口和蓝图库)

```cpp
void AutomateUsdImport(const FString& UsdFilePath, const FString& OutputContentFolder)
{
    // 1. 确保编辑器打开
    UUsdStageEditorBlueprintLibrary::OpenStageEditor();

    // 2. 加载文件
    UUsdStageEditorBlueprintLibrary::FileOpen(UsdFilePath);

    // 3. 创建或设置导入选项
    UUsdStageImportOptions* ImportOptions = NewObject<UUsdStageImportOptions>();
    // ... 配置 ImportOptions 的属性 ...

    // 4. 执行导入
    UUsdStageEditorBlueprintLibrary::ActionsImport(OutputContentFolder, ImportOptions);

    // 5. （可选）关闭编辑器
    // UUsdStageEditorBlueprintLibrary::CloseStageEditor();
}
```

**直接操作 USD 数据** (来源: `USDStage` 和 `USDSchemas` 模块)

```cpp
// 需要链接 USDStage 和 USDSchemas 模块
#include "UsdWrappers/SdfLayer.h"
#include "UsdWrappers/UsdStage.h"

void AccessUsdDataDirectly(const FString& UsdFilePath)
{
    // 打开一个 USD 阶段（内存中）
    UE::FUsdStage UsdStage = UE::FUsdStage::Open(UsdFilePath);
    if (UsdStage)
    {
        // 获取默认编辑目标层
        UE::FSdfLayer EditTarget = UsdStage.GetEditTarget().GetLayer();
        UE_LOG(LogTemp, Log, TEXT("编辑目标层: %s"), *EditTarget.GetIdentifier());

        // 获取根原语
        UE::FUsdPrim RootPrim = UsdStage.GetDefaultPrim();
        // ... 遍历原语树、读取属性等 ...
    }
}
```

## Demo 示例

这是一个展示如何通过 C++ 代码打开 USD 阶段编辑器并加载文件的最小示例。

**MyUsdEditorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyUsdEditorTool.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API UMyUsdEditorTool : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "USD")
    void OpenUsdInEditor(const FString& UsdFilePath);
};
```

**MyUsdEditorTool.cpp**
```cpp
#include "MyUsdEditorTool.h"
#include "USDStageEditorModule.h"
#include "USDStageEditorBlueprintLibrary.h"

void UMyUsdEditorTool::OpenUsdInEditor(const FString& UsdFilePath)
{
    // 方法一：通过模块接口
    IUsdStageEditorModule* StageEditorModule = FModuleManager::GetModulePtr<IUsdStageEditorModule>("USDStageEditor");
    if (StageEditorModule)
    {
        StageEditorModule->OpenStageEditor();
        StageEditorModule->FileOpen(UsdFilePath);
    }

    // 方法二：通过蓝图库（更简单，但间接）
    UUsdStageEditorBlueprintLibrary::OpenStageEditor();
    UUsdStageEditorBlueprintLibrary::FileOpen(UsdFilePath);
}
```

## 模块依赖

要使用此插件，你的模块（例如上面 Demo 中的 `MYPROJECT`）需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `USDStageEditor` | 提供 `IUsdStageEditorModule` 接口，用于 C++ 代码控制编辑器。 |
| `USDStageEditorBlueprintLibrary` | 提供 `UUsdStageEditorBlueprintLibrary`，用于蓝图或简单的 C++ 调用。 |
| `USDStage` | 提供 `AUsdStageActor` 和 USD 阶段的核心运行时表示。 |
| `USDSchemas` | 提供 USD 数据类型、属性和原语的 C++ 包装器（`UE::FUsdPrim` 等）。 |
| `USDClasses` | 提供 USD 相关的基础类和资产类型。 |
| `UnrealUSDWrapper` | 封装了底层 USD SDK（OpenUSD）的库。 |

注意：由于此插件默认未启用 (`EnabledByDefault: false`)，你还需要在 `.uproject` 文件或项目设置中手动启用它。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数时产生警告的代码。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD：新增支持分配不依赖蓝图的 Control Rigs（控制绑定）。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD values change. | USD：解决 26.03 版本更新导致当 LOD 值变化时，AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了当参数为 64 位时使用 32 位格式说明符，以及反之亦然的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：烘焙曝光动画轨道的所有帧。 |

### 维护评价

-   **活跃维护**：最近更新日期为 2026 年 5 月（相对于当前文档编写时间 2025 年），表明该插件仍在被 Epic Games 积极开发和维护。更新内容包括新功能（如 Control Rig 支持）、兼容性修复和底层错误修正。
-   **状态**：尽管 `.uplugin` 标记为 `IsBetaVersion: true`，但从长期的提交历史（始于 2018 年）和持续的功能更新来看，它已是一个成熟且关键的功能套件。 “Beta” 标签可能意味着其 API 或功能细节在未来版本中仍有调整的可能。
-   **推荐使用**：**强烈推荐**。对于任何需要深度集成 USD 工作流的影视、虚拟制片或大型复杂项目，此插件是必不可少的基础设施工具。由于它默认未启用，用户需要主动在项目中开启并配置所需的模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/usd-importer-unreal-engine-plugin/) (链接根据常见实践提供，具体以 Epic 官方文档站点为准)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests) (位于插件内部的 USDTests 模块)