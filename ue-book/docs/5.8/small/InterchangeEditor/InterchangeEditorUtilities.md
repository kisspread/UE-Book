# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 互换编辑器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-01（估算） |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

Interchange Editor 是 Unreal Editor 与 Interchange 运行时导入框架之间的**桥梁层**。Interchange 本身是 UE5 的新一代资产导入管线，旨在替换旧的 FBX Importer 等硬编码导入器，提供可扩展、可自定义的导入流程。

本插件的存在目的：

1. **将 Interchange 导入流程暴露给编辑器**：提供文件选择器对话框、导入设置 UI、资产保存等编辑器专属功能
2. **提供编辑器上下文工具**：判断当前是否在 PIE/运行时模式、管理编辑器选择状态、保存资产等
3. **加载编辑器专用 Pipeline**：将翻译器（Translator）解析的数据通过编辑器 Pipeline 转换为实际资产（静态网格体、骨骼网格体、动画、材质等）

简单来说：**Interchange Core 定义了"怎么导入"，Interchange Editor 决定了"在编辑器里怎么触发和管理这个导入"**。

## 使用场景

- 你在编辑器中拖拽或通过文件对话框导入 glTF / FBX / USD 等格式的资产 → 背后走的就是这个插件的文件选择器和导入流程
- 你需要自定义导入 Pipeline，让导入的网格体自动应用特定材质或 LOD 设置 → 通过 InterchangeEditorPipelines 配置
- 你需要在编辑器脚本中程序化触发 Interchange 导入，并管理导入后的资产保存 → 使用 InterchangeEditorUtilities 的工具函数
- 你正在构建自定义的资产导入工具，需要统一处理多种文件格式 → 继承 `UInterchangeFilePickerGeneric` 实现自定义文件选择逻辑

## 蓝图用法

`InterchangeEditorUtilities` 模块提供了可蓝图子类化的类，用于自定义导入行为。

### 核心类

| 类 | 说明 | 蓝图可见性 |
|---|---|---|
| `UInterchangeFilePickerGeneric` | 通用文件选择器，弹出文件对话框让用户选择导入文件 | `BlueprintType`, `Blueprintable` |

`UInterchangeFilePickerGeneric` 继承自 `UInterchangeFilePickerBase`，可被蓝图子类化以实现自定义的文件选择逻辑。

### 可重写函数

| 函数 | 说明 |
|---|---|
| `FilePickerForTranslatorAssetType` | 根据翻译器资产类型（如静态网格体、纹理等）弹出文件选择对话框，返回选中的文件路径列表 |
| `FilePickerForTranslatorType` | 根据翻译器类型（如 glTF、FBX 等）弹出文件选择对话框，返回选中的文件路径列表 |

### 使用示例（蓝图描述）

1. 创建 `UInterchangeFilePickerGeneric` 的蓝图子类
2. 重写 `FilePickerForTranslatorAssetType` 函数
3. 在函数体中，根据 `TranslatorAssetType` 参数设置文件过滤器（例如静态网格体只显示 `.fbx`、`.gltf`）
4. 弹出系统文件对话框，让用户选择文件
5. 将选中的文件路径填入 `OutFilenames` 数组，返回 `true` 表示成功
6. 在项目设置中将此蓝图类注册为默认文件选择器

## C++ 用法

### 头文件引入

```cpp
// 模块接口
#include "InterchangeEditorUtilitiesModule.h"

// 文件选择器
#include "InterchangeOpenFileDialog.h"

// 编辑器工具函数
#include "InterchangeEditorUtilities.h"
```

### 基本用法 — 检查模块可用性并获取引用

```cpp
// 来源: Public/InterchangeEditorUtilitiesModule.h

// 检查模块是否已加载
if (IInterchangeEditorUtilitiesModule::IsAvailable())
{
    // 获取模块单例引用
    IInterchangeEditorUtilitiesModule& EditorUtilitiesModule = IInterchangeEditorUtilitiesModule::Get();
    // 可以通过 EditorUtilitiesModule 访问模块提供的服务
}
```

### 基本用法 — 自定义文件选择器

```cpp
// 来源: Public/InterchangeOpenFileDialog.h

// UInterchangeFilePickerGeneric 已提供默认的文件对话框实现。
// 要自定义文件选择行为，创建子类：

UCLASS()
class UMyCustomFilePicker : public UInterchangeFilePickerGeneric
{
    GENERATED_BODY()

protected:
    virtual bool FilePickerForTranslatorAssetType(
        const EInterchangeTranslatorAssetType TranslatorAssetType,
        const FInterchangeFilePickerParameters& Parameters,
        TArray<FString>& OutFilenames) override
    {
        // 根据资产类型定制文件选择逻辑
        if (TranslatorAssetType == EInterchangeTranslatorAssetType::StaticMesh)
        {
            // 只允许选择 FBX 和 glTF 文件
            // 使用 IDesktopPlatform 弹出文件对话框
            // 将结果写入 OutFilenames
        }
        return true;
    }
};
```

### 基本用法 — 编辑器工具函数

```cpp
// 来源: Public/InterchangeEditorUtilities.h

// UInterchangeEditorUtilities 提供编辑器上下文相关的工具方法：
// - SaveAsset(UObject* Asset): 保存导入后的资产
// - IsRuntimeOrPIE(): 判断当前是否处于运行时或 PIE 模式
// - ClearEditorSelection(): 清除编辑器中的当前选择

// 这些是内部虚函数，由 Interchange 导入管线自动调用。
// 通常不需要直接调用，除非你正在实现自定义导入管线。
```

## Demo 示例

以下示例展示如何创建自定义文件选择器，限制特定资产类型的文件格式：

```cpp
// MyCustomInterchangeFilePicker.h
#pragma once

#include "InterchangeOpenFileDialog.h"
#include "MyCustomInterchangeFilePicker.generated.h"

UCLASS()
class MYPROJECT_API UMyCustomInterchangeFilePicker : public UInterchangeFilePickerGeneric
{
	GENERATED_BODY()

public:
	// 自定义允许的文件扩展名
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interchange")
	TArray<FString> AllowedExtensions;

protected:
	virtual bool FilePickerForTranslatorAssetType(
		const EInterchangeTranslatorAssetType TranslatorAssetType,
		const FInterchangeFilePickerParameters& Parameters,
		TArray<FString>& OutFilenames) override;

	virtual bool FilePickerForTranslatorType(
		const EInterchangeTranslatorType TranslatorType,
		const FInterchangeFilePickerParameters& Parameters,
		TArray<FString>& OutFilenames) override;

private:
	bool OpenFileDialog(const FString& Title, const FString& DefaultPath,
		const FString& FileTypes, TArray<FString>& OutFilenames);
};
```

```cpp
// MyCustomInterchangeFilePicker.cpp
#include "MyCustomInterchangeFilePicker.h"
#include "DesktopPlatformModule.h"
#include "Framework/Application/SlateApplication.h"

bool UMyCustomInterchangeFilePicker::FilePickerForTranslatorAssetType(
	const EInterchangeTranslatorAssetType TranslatorAssetType,
	const FInterchangeFilePickerParameters& Parameters,
	TArray<FString>& OutFilenames)
{
	// 根据资产类型决定允许的文件格式
	FString FileTypes;
	switch (TranslatorAssetType)
	{
	case EInterchangeTranslatorAssetType::StaticMesh:
		FileTypes = TEXT("FBX Files (*.fbx)|*.fbx|glTF Files (*.gltf;*.glb)|*.gltf;*.glb");
		break;
	case EInterchangeTranslatorAssetType::Texture:
		FileTypes = TEXT("Image Files (*.png;*.jpg;*.tga;*.exr)|*.png;*.jpg;*.tga;*.exr");
		break;
	default:
		FileTypes = TEXT("All Files (*.*)|*.*");
		break;
	}

	return OpenFileDialog(TEXT("选择要导入的文件"), Parameters.DefaultPath, FileTypes, OutFilenames);
}

bool UMyCustomInterchangeFilePicker::FilePickerForTranslatorType(
	const EInterchangeTranslatorType TranslatorType,
	const FInterchangeFilePickerParameters& Parameters,
	TArray<FString>& OutFilenames)
{
	// 通用后备方案
	return OpenFileDialog(TEXT("选择文件"), Parameters.DefaultPath, TEXT("All Files (*.*)|*.*"), OutFilenames);
}

bool UMyCustomInterchangeFilePicker::OpenFileDialog(
	const FString& Title,
	const FString& DefaultPath,
	const FString& FileTypes,
	TArray<FString>& OutFilenames)
{
	IDesktopPlatform* DesktopPlatform = FDesktopPlatformModule::Get();
	if (!DesktopPlatform)
	{
		return false;
	}

	TSharedPtr<SWindow> ParentWindow;
	if (FSlateApplication::IsInitialized())
	{
		ParentWindow = FSlateApplication::Get().GetActiveTopLevelWindow();
	}

	void* ParentWindowHandle = ParentWindow.IsValid()
		? ParentWindow->GetNativeWindow()->GetOSWindowHandle()
		: nullptr;

	TArray<FString> SelectedFiles;
	const bool bSelected = DesktopPlatform->OpenFileDialog(
		ParentWindowHandle,
		Title,
		DefaultPath,
		TEXT(""),  // DefaultFile
		FileTypes,
		EFileDialogFlags::None,
		SelectedFiles
	);

	if (bSelected && SelectedFiles.Num() > 0)
	{
		OutFilenames = MoveTemp(SelectedFiles);
		return true;
	}

	return false;
}
```

## 模块依赖

从代码中可推断的模块依赖关系（Build.cs 原文未提供，以下基于继承关系和 API 推断）：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | 提供基类 `UInterchangeFilePickerBase`、`UInterchangeEditorUtilitiesBase` 等 Interchange 核心接口 |
| `InterchangeCommon` | 提供 `EInterchangeTranslatorAssetType`、`EInterchangeTranslatorType`、`FInterchangeFilePickerParameters` 等共享类型定义 |
| `DesktopPlatform` | 提供操作系统级文件对话框（`IDesktopPlatform::OpenFileDialog`） |

其余依赖为标准 Core/Engine/Slate 等常见模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `fb1426e8` | [PackageAutoSaver] Add the ability to temporarily suspend the autosaver. | 包自动保存器新增临时暂停功能，改善导入流程中的自动保存干扰 |
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除动画帧对齐和 glTF 翻译器帧对齐器，简化动画导入流程 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loading | Interchange 脚本库新增不加载子关卡即可获取 Level Instance 内 Actor 的访问器 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，统一日志格式 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重构静态网格体和骨骼网格体的导入设置，优化导入配置体验 |

### 维护评价

**活跃维护中** ✅

- **最近 1 个月内有多次实质性功能更新**（动画帧对齐清理、导入设置重构、脚本库增强）
- 作为 UE5 新一代导入框架的编辑器集成层，**Epic 持续投入开发**
- 该插件是 Interchange 替换旧导入器战略的核心组件之一，长期维护有保障
- `EnabledByDefault=true`、`IsBetaVersion=false`，已从实验状态毕业为正式功能
- **推荐使用**：对于需要自定义导入流程或扩展导入管线的项目，这是官方推荐的扩展点
- 无已知废弃标记或重大限制

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/interchange-editor-plugin-in-unreal-engine/)（无 `.uplugin` DocsURL，参考 UE 官网 Interchange 文档）