# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 资产导入编辑器集成 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

InterchangeEditor 是 Unreal Engine 5 新一代资产导入系统（Interchange）的编辑器集成模块。其主要作用是将底层的、模块化的 Interchange 导入框架和各种格式的导入管线（如 FBX、glTF、OBJ 等）以用户友好的方式暴露给虚幻编辑器。它负责处理编辑器中与资产导入相关的 UI 交互（如文件选择对话框）、资产保存、编辑器选择清理等特定于编辑器的操作，从而让用户能够通过标准的编辑器工作流（如拖放、菜单导入）无缝地使用 Interchange 系统。

## 使用场景

- 你正在使用 UE5 的编辑器，并希望通过新的 Interchange 系统导入 FBX、glTF 或其他格式的 3D 模型、动画、材质等资产。
- 你需要自定义文件选择器或导入行为（例如，限制文件类型或改变选择器界面）。
- 你的插件或工具需要以编程方式触发 Interchange 导入流程，并希望利用编辑器已有的 UI 和管理功能。

## 蓝图用法

本插件主要提供编辑器工具类和模块接口，可蓝图继承的类有限。核心的可继承类用于自定义导入行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FilePickerForTranslatorAssetType` | （可重写）根据指定的翻译器资产类型（如静态网格、骨骼网格）弹出文件选择对话框并返回文件路径 | `UInterchangeFilePickerGeneric` |
| `FilePickerForTranslatorType` | （可重写）根据指定的翻译器类型（如通用FBX、glTF）弹出文件选择对话框并返回文件路径 | `UInterchangeFilePickerGeneric` |

### 使用示例（蓝图描述）

要自定义文件选择器，可以创建一个 `UInterchangeFilePickerGeneric` 的蓝图子类。
1.  在蓝图编辑器中创建新蓝图，父类选择 `InterchangeFilePickerGeneric`。
2.  在事件图表中，重写 `FilePickerForTranslatorAssetType` 或 `FilePickerForTranslatorType` 函数。
3.  在重写的函数内，使用 “Open File Dialog” 节点或其他 UI 逻辑来构建你自己的文件选择界面，并将选择的文件路径填充到输出的 `OutFilenames` 数组中。
4.  将该蓝图类设置为项目中 Interchange 系统使用的默认文件选择器（通常通过项目设置或模块初始化逻辑）。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeEditorUtilitiesModule.h"
#include "InterchangeOpenFileDialog.h"
#include "InterchangeEditorUtilities.h"
```

### 基本用法

从提供的头文件中，我们可以看到模块的单例访问方式和几个可继承的工具类。

**1. 检查和获取模块实例**
（来源：`Public/InterchangeEditorUtilitiesModule.h`）

```cpp
// 检查模块是否可用（已加载）
if (IInterchangeEditorUtilitiesModule::IsAvailable())
{
    // 获取模块单例，用于调用其提供的功能（如果有的话）
    IInterchangeEditorUtilitiesModule& EditorUtilModule = IInterchangeEditorUtilitiesModule::Get();
    // ... 使用模块
}
```

**2. 继承和使用文件选择器**
（来源：`Public/InterchangeOpenFileDialog.h`）

```cpp
// 自定义一个文件选择器，例如用于特定格式
class UMyCustomFilePicker : public UInterchangeFilePickerGeneric
{
    GENERATED_BODY()

protected:
    // 重写此函数以自定义基于资产类型的文件选择行为
    virtual bool FilePickerForTranslatorAssetType(const EInterchangeTranslatorAssetType TranslatorAssetType, 
                                                  const FInterchangeFilePickerParameters& Parameters, 
                                                  TArray<FString>& OutFilenames) override
    {
        // 示例：当导入静态网格时，使用自定义逻辑
        if (TranslatorAssetType == EInterchangeTranslatorAssetType::StaticMesh)
        {
            // 实现自定义的文件选择逻辑，如弹出特定对话框
            // 填充 OutFilenames
            return true;
        }
        // 否则，回退到父类（默认）行为
        return UInterchangeFilePickerGeneric::FilePickerForTranslatorAssetType(TranslatorAssetType, Parameters, OutFilenames);
    }
};
```

**3. 继承和使用编辑器工具类**
（来源：`Public/InterchangeEditorUtilities.h`）

```cpp
// 自定义编辑器实用工具，例如在导入后执行特定操作
class UMyEditorUtilities : public UInterchangeEditorUtilities
{
    GENERATED_BODY()

protected:
    // 重写资产保存逻辑
    virtual bool SaveAsset(UObject* Asset) const override
    {
        // 在保存前添加自定义逻辑，如日志记录、校验等
        UE_LOG(LogTemp, Log, TEXT("Interchange: Pre-saving asset %s"), *Asset->GetName());
        // 调用父类默认保存逻辑
        return UInterchangeEditorUtilities::SaveAsset(Asset);
    }
};
```

### 进阶用法

通常，这些工具类不会被直接实例化和使用，而是作为 Interchange 框架中的可替换组件。你需要通过 Interchange 核心模块的设置或项目设置，将你的自定义子类（如 `UMyCustomFilePicker` 或 `UMyEditorUtilities`）注册为框架使用的实现。

## Demo 示例

以下是一个最小化的自定义文件选择器实现，它过滤掉非 FBX 文件。

**MyCustomFilePicker.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "InterchangeOpenFileDialog.h"
#include "MyCustomFilePicker.generated.h"

UCLASS()
class UMyCustomFilePicker : public UInterchangeFilePickerGeneric
{
    GENERATED_BODY()

protected:
    virtual bool FilePickerForTranslatorAssetType(const EInterchangeTranslatorAssetType TranslatorAssetType,
                                                  const FInterchangeFilePickerParameters& Parameters,
                                                  TArray<FString>& OutFilenames) override;
};
```

**MyCustomFilePicker.cpp**
```cpp
#include "MyCustomFilePicker.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

bool UMyCustomFilePicker::FilePickerForTranslatorAssetType(const EInterchangeTranslatorAssetType TranslatorAssetType,
                                                           const FInterchangeFilePickerParameters& Parameters,
                                                           TArray<FString>& OutFilenames)
{
    // 假设只处理静态网格的导入
    if (TranslatorAssetType == EInterchangeTranslatorAssetType::StaticMesh)
    {
        // 使用默认的文件对话框，但只允许FBX文件
        TArray<FString> DefaultFilenames;
        // 这里需要调用平台相关的文件对话框API，为简化，假设调用了父类的默认逻辑
        bool bSuccess = Super::FilePickerForTranslatorAssetType(TranslatorAssetType, Parameters, DefaultFilenames);

        if (bSuccess)
        {
            // 过滤结果，只保留.fbx文件
            for (const FString& Filename : DefaultFilenames)
            {
                if (FPaths::GetExtension(Filename).Equals(TEXT("fbx"), ESearchCase::IgnoreCase))
                {
                    OutFilenames.Add(Filename);
                }
            }
            return OutFilenames.Num() > 0;
        }
    }
    // 其他类型或失败时，回退到父类
    return Super::FilePickerForTranslatorAssetType(TranslatorAssetType, Parameters, OutFilenames);
}
```

## 模块依赖

基于模块名称和 Interchange 系统的结构推断，此插件依赖以下核心模块。

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 导入框架的核心接口和数据结构 |
| `InterchangeImport` | Interchange 的默认导入管线实现 |
| `InterchangeNodes` | 定义导入过程中使用的资产节点图 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `fb1426e8` | [PackageAutoSaver] Add the ability to temporarily suspend the autosaver. | 为自动保存器添加临时挂起能力，可能影响导入后保存流程。 |
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除了动画帧对齐和glTF翻译器帧对齐器，简化了动画导入逻辑。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loadi | 向InterchangeEditorScriptLibrary添加访问器，可返回关卡实例中的Actor，无需加载。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF，更新日志系统。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重构静态和骨骼网格体的导入设置，改进导入配置。 |

### 维护评价

Interchange Editor 是 Unreal Engine 5 中处于**活跃维护和积极开发**状态的核心导入系统插件。
- **创建时间**：作为UE5的新增系统，其历史较短。
- **近期更新**：从最近提交记录（2026年4月至5月）来看，更新非常频繁。改动涉及核心功能移除（动画帧对齐）、架构重构（网格体导入设置）、以及编辑器集成改进（脚本库访问器、日志系统迁移）。这表明 Epic 正在持续打磨和完善 Interchange 系统。
- **状态**：属于官方主力维护的插件，是未来资产导入的标准。
- **推荐使用**：**强烈推荐**用于新的UE5项目。虽然仍在发展中，但已是默认启用且功能基本完善的系统。建议关注其与旧FBX导入器的兼容性差异。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
- 官方文档：暂无（.uplugin 中 DocsURL 为空）
- 测试用例：未在提供的源码信息中明确指定路径，通常位于 `Engine/Tests/` 或插件自身的 `Tests/` 目录下。