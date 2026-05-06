# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 导入编辑器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor) | |

## 用途

Interchange Editor 插件是 Interchange 资产导入框架的编辑器扩展，为美术和策划人员提供可视化的导入对话框、管道配置和资产后处理工具。它解决了以下问题：

- 传统导入流程缺乏统一的 UI 集成，用户无法直观地选择导入设置、指定文件类型过滤器。
- 导入管道（Pipeline）的自定义和保存需要编写 C++ 代码，不利于迭代和团队协作。
- 导入过程中无法在编辑器内实时预览或调整参数。

通过此插件，用户可以在编辑器中直接调用标准导入对话框（支持按资产类型或翻译器类型筛选），使用蓝图或细节面板配置导入管道，并在导入前保存、清除选区等操作。

## 使用场景

- **美术资产导入**：你需要导入 FBX、GLTF、USD 等格式的模型、材质、动画 → 使用 Interchange 框架时，通过此插件提供的 UI 选择文件并应用自定义管道。
- **导入管道定制**：你需要为项目定义默认的导入预设（如始终合并骨骼、调整纹理压缩） → 通过 InterchangeEditorPipelines 在蓝图中配置 Pipeline 并将其绑定到特定文件类型。
- **自动化导入流程**：编写编辑器脚本或 Python 命令时，需要调用文件选择对话框并自动执行导入 → 使用 `UInterchangeFilePickerGeneric` 的蓝图节点获取文件路径，再调用 `UInterchangeEditorUtilities` 的方法保存导入的资产。

## 蓝图用法

插件中暴露的蓝图类（当前模块 `InterchangeEditorUtilities`）主要用于文件选择及编辑器辅助操作。所有节点均为 `BlueprintCallable`，可直接在蓝图编辑器中放置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FilePickerForTranslatorAssetType` | 打开文件对话框，按导入的资产类型（静态网格、骨骼网格、材质等）筛选文件。参数可设置标题、默认路径、是否允许多选。返回选择的文件路径列表。 | `UInterchangeFilePickerGeneric` |
| `FilePickerForTranslatorType` | 打开文件对话框，按翻译器类型（Source、Mesh、Animation 等）筛选文件。适用于需要精确控制翻译器的场景。 | `UInterchangeFilePickerGeneric` |
| `SaveAsset` | 保存指定的资产到磁盘。通常在导入、修改资产后调用，确保改动持久化。 | `UInterchangeEditorUtilities` |
| `IsRuntimeOrPIE` | 判断当前是否处于运行时或在编辑器内运行（PIE）状态。用于导入逻辑中阻止非编辑状态下的操作。返回布尔值。 | `UInterchangeEditorUtilities` |
| `ClearEditorSelection` | 清空当前编辑器世界/内容浏览器中的选中状态。常用于导入开始前重置选区。 | `UInterchangeEditorUtilities` |

### 使用示例（蓝图）

**示例：使用文件选择器导入静态网格并保存**

1. 从 `InterchangeFilePickerGeneric` 类获取一个节点 `FilePickerForTranslatorAssetType`。
2. 设置 `TranslatorAssetType` 为 `StaticMesh`，在 `Parameters` 中设置 `Title` 为“选择静态网格文件”，`bAllowMultipleFiles` 为 `false`。
3. 连接执行线：开始 → `FilePickerForTranslatorAssetType` → (成功分支) → 将输出的 `OutFilenames` 传递给 Interchange 导入管理器（如 `UInterchangeManager::ImportAsset`）→ 导入完成后调用 `SaveAsset`，传入生成的资产对象 → 完成。
4. 若用户取消选择，走失败分支（通常不做操作）。

## C++ 用法

插件以模块形式提供，C++ 开发可通过模块接口和暴露的类直接调用。

### 头文件引入

```cpp
#include "InterchangeEditorUtilitiesModule.h"      // 获取模块接口
#include "InterchangeEditorUtilities.h"            // 使用 UInterchangeEditorUtilities
#include "InterchangeOpenFileDialog.h"             // 使用 UInterchangeFilePickerGeneric
```

### 基本用法

**获取模块实例并调用辅助方法**

```cpp
// Source: Engine/Plugins/Interchange/Editor/Source/Utilities/Private/InterchangeEditorUtilitiesModule.cpp
IInterchangeEditorUtilitiesModule& Module = IInterchangeEditorUtilitiesModule::Get();

// 获取 UInterchangeEditorUtilities 对象（通常是模块创建的 CDO，或通过 GetDefault 获得）
UInterchangeEditorUtilities* Utilities = Cast<UInterchangeEditorUtilities>(UInterchangeEditorUtilities::StaticClass()->GetDefaultObject());
if (Utilities)
{
    bool bIsRuntime = Utilities->IsRuntimeOrPIE();  // 检查当前上下文
    if (!bIsRuntime)
    {
        // 保存某资产
        UObject* MyAsset = ...;  // 假设已导入
        Utilities->SaveAsset(MyAsset);
    }
}
```

**使用文件选择器打开对话框**

```cpp
// Source: Engine/Plugins/Interchange/Editor/Source/Utilities/Private/InterchangeOpenFileDialog.cpp
UInterchangeFilePickerGeneric* FilePicker = NewObject<UInterchangeFilePickerGeneric>();
FInterchangeFilePickerParameters Params;
Params.Title = FText::FromString("选择导入文件");
TArray<FString> OutFiles;
bool bSuccess = FilePicker->FilePickerForTranslatorAssetType(EInterchangeTranslatorAssetType::StaticMesh, Params, OutFiles);
if (bSuccess && OutFiles.Num() > 0)
{
    // 使用 OutFiles[0] 进行后续导入
}
```

### 进阶用法

**结合 Interchange Manager 完成导入流程**

```cpp
#include "InterchangeManager.h"

// 配置管道
UInterchangePipelineBase* MyPipeline = ...;

// 使用文件选择器获取文件
UInterchangeFilePickerGeneric* Picker = NewObject<UInterchangeFilePickerGeneric>();
FInterchangeFilePickerParameters Params;
Params.Title = FText::FromString("选择 FBX 文件");
TArray<FString> Files;
if (Picker->FilePickerForTranslatorType(EInterchangeTranslatorType::Scenes, Params, Files))
{
    UInterchangeManager& Manager = UInterchangeManager::GetInterchangeManager();
    FImportParameters ImportParams;
    ImportParams.bIsAutomated = false; // 手动导入
    for (const FString& File : Files)
    {
        UInterchangeSourceData* SourceData = UInterchangeSourceData::CreateSourceData(File);
        UObject* ImportedAsset = Manager.ImportAsset(*GWorld->GetPackage(), SourceData, ImportParams, { MyPipeline });
        if (ImportedAsset)
        {
            // 保存资产
            UInterchangeEditorUtilities* Utils = Cast<UInterchangeEditorUtilities>(UInterchangeEditorUtilities::StaticClass()->GetDefaultObject());
            Utils->SaveAsset(ImportedAsset);
        }
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 编辑器模块示例，演示如何通过 InterchangeEditorUtilities 的文件选择器触发导入并保存资产。

### Demo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FInterchangeDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    
private:
    void OnTestImport();
};
```

### Demo.cpp

```cpp
#include "Demo.h"
#include "InterchangeEditorUtilities.h"
#include "InterchangeOpenFileDialog.h"
#include "InterchangeManager.h"
#include "InterchangeSourceData.h"
#include "AssetRegistry/AssetRegistryModule.h"

void FInterchangeDemoModule::StartupModule()
{
    // 在菜单或其他地方绑定触发函数，这里直接延迟执行用于测试
    FTimerHandle Handle;
    GEditor->GetTimerManager()->SetTimer(Handle, FTimerDelegate::CreateRaw(this, &FInterchangeDemoModule::OnTestImport), 1.0f, false);
}

void FInterchangeDemoModule::ShutdownModule()
{
}

void FInterchangeDemoModule::OnTestImport()
{
    // 1. 构建文件选择器
    UInterchangeFilePickerGeneric* Picker = NewObject<UInterchangeFilePickerGeneric>();
    FInterchangeFilePickerParameters Params;
    Params.Title = FText::FromString("Demo 导入");
    Params.DefaultPath = FPaths::ProjectContentDir() / TEXT("Imports");
    Params.bAllowMultipleFiles = false;
    TArray<FString> Files;
    if (!Picker->FilePickerForTranslatorAssetType(EInterchangeTranslatorAssetType::StaticMesh, Params, Files) || Files.Num() == 0)
    {
        return;
    }

    // 2. 使用 InterchangeManager 导入
    UInterchangeManager& Manager = UInterchangeManager::GetInterchangeManager();
    UInterchangeSourceData* SourceData = UInterchangeSourceData::CreateSourceData(Files[0]);
    TStrongObjectPtr<UInterchangePipelineBase> Pipeline = ...; // 根据需求创建或使用默认
    UObject* ImportedAsset = Manager.ImportAsset(GetTransientPackage(), SourceData, FImportParameters(), { Pipeline.Get() });
    
    if (ImportedAsset)
    {
        // 3. 保存到内容目录
        UInterchangeEditorUtilities* Utils = Cast<UInterchangeEditorUtilities>(UInterchangeEditorUtilities::StaticClass()->GetDefaultObject());
        Utils->SaveAsset(ImportedAsset);
        UE_LOG(LogTemp, Log, TEXT("Imported asset saved: %s"), *ImportedAsset->GetName());
    }
}

IMPLEMENT_MODULE(FInterchangeDemoModule, InterchangeDemo)
```

**注意**：实际使用中需要将资产迁移到正式包，而非 `GetTransientPackage()`。此处仅作演示。

## 模块依赖

InterchangeEditorUtilities 的 Build.cs 需要添加以下依赖（非标准通用模块）：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架核心定义、描述符、翻译器注册等 |
| `InterchangeEngine` | Interchange 管理器、导入参数、管道执行 |
| `InterchangeFilePickerBase` | 文件选择器的基类接口（在 InterchangePipelines 模块中） |
| `LevelEditor` | 编辑器环境，用于访问 GEditor、世界等 |
| `ContentBrowser` | 内容浏览器的选中状态清除等（若需 ClearEditorSelection） |
| `AssetRegistry` | 资产注册表，用于 SaveAsset 后刷新（可选，但常见） |

其他依赖（Core, Engine, Slate 等均为标准项，不重复列出）。

## 维护状态

### 近期更新

- 2025-10-02 `35b266d6` [Interchange UI] - 在导入对话框的详细信息视图设置中添加分隔线章节标题。
- 2025-09-24 `d2b213b6` Interchange - 导入性能改进尝试。
- 2025-09-24 `c5a21eff` [BUGFIX][Interchange] 修复 FBX Python 级别导入测试失败。
- 2025-09-23 `dcd0cb0d` 临时修复用户关闭导入对话框时的闪退问题。
- 2025-09-23 `24638fbb` [Interchange] 临时修复 Interchange 日志输出。

### 维护评价

插件创建于 2025 年 9 月，属于 UE5.7 中较新的模块。最近一次实质性更新（UI 分隔符）在 2025 年 10 月，距今约 6 个月。更新内容包含性能改进、Bug 修复和 UI 增强，表明团队仍在积极维护。没有发现废弃或停止开发的迹象。插件质量稳定，适合在生产项目中使用。如果后续长时间无更新，需关注 UE 官方是否将其迁移至其他框架。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/importing-assets-via-interchange-in-unreal-engine/) （若存在）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Tests)