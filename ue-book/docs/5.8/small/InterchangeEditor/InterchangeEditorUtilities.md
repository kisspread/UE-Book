# Interchange Editor Utilities

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 交换编辑器工具 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（基于近期更新） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

`InterchangeEditorUtilities` 是 **Interchange 导入框架**的编辑器侧实用工具模块。它主要解决以下问题：

1.  **与操作系统交互**：提供编辑器内打开文件对话框的实现（`UInterchangeFilePickerGeneric`），用于在导入资产时让用户选择源文件（如 FBX、glTF 等）。
2.  **提供编辑器特定功能**：将 Interchange 框架中一些依赖于编辑器环境的操作（如保存资产、检查是否在编辑器中运行、清除编辑器选择）封装成独立的模块，保持核心框架的“引擎无关性”。
3.  **作为模块化架构的一部分**：将编辑器特有的功能（UI、文件操作）从核心的 `Interchange` 框架模块中分离出来，便于维护和降低耦合度。

简而言之，这个模块是 Interchange 框架与 Unreal Editor 之间的“适配层”和“工具箱”。

## 使用场景

-   你正在开发一个需要导入外部3D模型或动画资产的编辑器工具或自定义导入器，希望复用 Interchange 框架，但需要自定义文件选择界面或导入后的处理流程（如自动保存）。
-   你在编写一个编辑器扩展，需要在特定时机（例如导入完成后）执行与编辑器状态相关的操作（如刷新内容浏览器、清除资产选择）。

## 蓝图用法

该模块中的类带有 `BlueprintType` 和 `Blueprintable` 标记，支持在蓝图中继承和使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `File Picker For Translator Asset Type` | 根据翻译器资产类型（如 Static Mesh, Skeletal Mesh）打开相应的文件选择器，返回用户选择的文件路径数组。 | `UInterchangeFilePickerGeneric` |
| `File Picker For Translator Type` | 根据基础翻译器类型（如通用文件、场景）打开文件选择器。 | `UInterchangeFilePickerGeneric` |

### 使用示例（蓝图描述）

1.  **创建自定义文件选择器**：
    *   在蓝图中新建一个类，继承自 `UInterchangeFilePickerGeneric`。
    *   重写 `FilePickerForTranslatorAssetType` 和 `FilePickerForTranslatorType` 函数。
    *   在函数实现中，可以调用父类的默认实现（`Super::...`），也可以在调用前/后添加自定义逻辑（如修改文件过滤器、记录日志）。

2.  **在导入流程中使用**：
    *   当你的自定义导入流程需要用户选择文件时，获取你自定义的文件选择器对象。
    *   调用 `File Picker For Translator Asset Type`，传入对应的 `EInterchangeTranslatorAssetType`（如 `EInterchangeTranslatorAssetType::StaticMesh`）。
    *   将返回的 `OutFilenames` 数组传递给 Interchange 的导入器工厂或管道进行后续处理。

## C++ 用法

### 头文件引入

```cpp
// 使用文件选择器
#include "InterchangeOpenFileDialog.h"

// 使用编辑器工具类
#include "InterchangeEditorUtilities.h"
```

### 基本用法

```cpp
// 1. 使用默认的文件选择器（通常通过模块获取单例）
// 注意：实际使用中，Interchange 框架会通过 Factory 或 Pipeline 间接调用这些类。
// 以下为示例性代码，展示如何直接调用。
#include "InterchangeEditorUtilitiesModule.h"

// 检查模块是否可用
if (IInterchangeEditorUtilitiesModule::IsAvailable())
{
    // 获取模块（通常已在引擎启动时加载）
    IInterchangeEditorUtilitiesModule& EditorUtilsModule = IInterchangeEditorUtilitiesModule::Get();
    // 此处 EditorUtilsModule 本身可能不直接暴露更多API，
    // 更多功能通过其提供的类实例（如 UInterchangeFilePickerGeneric）来使用。
}

// 2. 使用编辑器工具类（通常是基类，需要通过框架获取其派生类实例）
#include "InterchangeEditorUtilities.h"

// 假设你已经通过某种方式（例如从导入上下文）获取了 UInterchangeEditorUtilities 的实例指针 EditorUtils
if (EditorUtils)
{
    // 检查当前是否在编辑器中运行（非PIE游戏实例）
    bool bIsInEditor = !EditorUtils->IsRuntimeOrPIE();

    // 清除编辑器当前选中的资产（例如导入后希望自动选中导入结果）
    EditorUtils->ClearEditorSelection();

    // 尝试保存一个刚导入或修改的资产
    UObject* ImportedAsset = /* ... */;
    bool bSaveSuccess = EditorUtils->SaveAsset(ImportedAsset);
}
```

### 进阶用法

创建自定义的文件选择器以集成第三方文件服务或修改文件过滤逻辑。

```cpp
// MyCustomFilePicker.h
#pragma once
#include "InterchangeOpenFileDialog.h"
#include "MyCustomFilePicker.generated.h"

UCLASS()
class UMyCustomFilePicker : public UInterchangeFilePickerGeneric
{
    GENERATED_BODY()

public:
    // 重写文件选择逻辑，添加自定义后缀过滤或使用系统对话框
    virtual bool FilePickerForTranslatorAssetType(
        const EInterchangeTranslatorAssetType TranslatorAssetType,
        const FInterchangeFilePickerParameters& Parameters,
        TArray<FString>& OutFilenames) override
    {
        // 示例：在调用父类默认对话框前，可以修改 Parameters 的 Title
        FInterchangeFilePickerParameters CustomParams = Parameters;
        CustomParams.Title = FText::FromString(TEXT("请选择要导入的模型文件"));

        // 调用父类默认实现，打开标准文件对话框
        bool bResult = Super::FilePickerForTranslatorAssetType(TranslatorAssetType, CustomParams, OutFilenames);

        // 示例：在文件选择后，对文件路径进行后处理
        if (bResult)
        {
            for (FString& Filename : OutFilenames)
            {
                // 可以在此添加路径验证、转换等逻辑
                UE_LOG(LogTemp, Log, TEXT("Selected file: %s"), *Filename);
            }
        }

        return bResult;
    }
};
```

## Demo 示例

一个最小的自定义文件选择器示例，仅改变对话框标题。

```cpp
// MyMinimalFilePicker.h
#pragma once
#include "InterchangeOpenFileDialog.h"
#include "MyMinimalFilePicker.generated.h"

UCLASS()
class UMyMinimalFilePicker : public UInterchangeFilePickerGeneric
{
	GENERATED_BODY()

public:
	virtual bool FilePickerForTranslatorAssetType(
		const EInterchangeTranslatorAssetType TranslatorAssetType,
		const FInterchangeFilePickerParameters& Parameters,
		TArray<FString>& OutFilenames) override
	{
		// 创建参数副本，修改标题
		FInterchangeFilePickerParameters ModifiedParams = Parameters;
		ModifiedParams.Title = FText::FromString(TEXT("选择模型文件"));
		// 调用父类默认实现
		return Super::FilePickerForTranslatorAssetType(TranslatorAssetType, ModifiedParams, OutFilenames);
	}
};
```

## 模块依赖

根据 `InterchangeEditorUtilities.Build.cs` 的典型内容，其依赖如下：

| 模块 | 用途 |
|---|---|
| `Interchange` | 核心的 Interchange 框架，提供基类、接口和核心功能。 |
| `InterchangeCore` | 可能包含更基础的接口。 |
| `DesktopPlatform` | 提供操作系统原生的文件对话框功能。 |
| `Slate`, `SlateCore`, `UMG` | 用于构建编辑器UI（虽然本模块直接UI不多，但作为编辑器模块通常依赖）。 |

**使用者需注意**：如果你的模块需要使用 `InterchangeEditorUtilities` 中的功能，你的模块（`.Build.cs`）需要添加对 `InterchangeEditorUtilities` 的依赖，并可能间接需要 `Interchange` 和 `DesktopPlatform`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除了动画帧对齐功能和 glTF 翻译器的帧对齐器。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loadi... | 为 InterchangeEditorScriptLibrary 添加了访问器，用于返回关卡实例中的 Actor 而无需加载。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重新设计了静态网格和骨骼网格的导入设置。 |

### 维护评价

- **创建时间**：未知，但从近期活跃的提交记录看，该模块仍在持续开发和迭代中。
- **最近更新频率**：非常活跃，在 2026 年 4 月至 5 月期间有多次功能性提交，包括功能重构和优化。
- **维护状态**：**活跃维护中**。作为 Interchange 框架的关键编辑器组件，随着框架本身的演进（如动画、网格导入设置重构）而持续更新。
- **已知问题或限制**：作为编辑器工具，其功能依赖于特定的编辑器版本和框架状态。动画帧对齐功能的移除可能影响某些特定工作流。
- **推荐使用**：**强烈推荐**。该模块是使用 Interchange 框架进行编辑器资产导入和管理的必备组件。如果你的项目使用了 Interchange 进行资产交换，那么此模块（或其提供的功能）通常是自动加载和使用的。对于开发者而言，了解其提供的工具类（如文件选择器、编辑器工具）有助于进行深度定制和扩展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
- [官方文档]()（暂无）
- [测试用例]()（未在提供的信息中发现独立测试文件，功能通常通过Interchange框架的集成测试覆盖）