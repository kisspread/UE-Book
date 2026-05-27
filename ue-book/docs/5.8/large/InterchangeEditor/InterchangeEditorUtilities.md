# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 交换编辑器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-05（估算） |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

Interchange Editor 是 UE5 全新资产导入框架 **Interchange** 在编辑器侧的实现层。它解决的核心问题是：将 Interchange 运行时翻译/管线/节点图体系与 Unreal Editor 的 UI 交互（文件选择对话框、资产保存、编辑器选区管理等）桥接起来。

与传统的 FBX Importer 硬编码导入流程不同，Interchange 采用模块化的 **Translator → Node Container → Pipeline → Factory** 架构，而本插件正是为这套架构提供编辑器集成能力：

- **文件选择**：根据翻译器类型（如 FBX、glTF、纹理等）弹出正确的文件选择对话框
- **资产保存**：在导入完成后将生成的资产保存到 Content 目录
- **编辑器状态管理**：在导入过程中清除/恢复编辑器选区，判断是否处于 PIE 运行状态
- **管线暴露**：将 Import/Export Pipeline 暴露给编辑器的导入导出 UI

简单来说：**Interchange 是引擎的通用导入后端，InterchangeEditor 是它的编辑器前端。**

## 使用场景

- 你需要在编辑器中通过 **File → Import** 导入 FBX、glTF、OBJ 等 3D 资产 → Interchange Editor 负责弹出文件对话框并驱动管线
- 你需要自定义导入流程（例如自定义管线处理特定材质规则）→ 通过本插件注册的 Pipeline 机制扩展
- 你需要在 C++ 或蓝图中程序化触发资产导入 → 使用 `UInterchangeFilePickerGeneric` 选择文件，配合 Interchange Manager 完成导入
- 你需要为新格式编写 Translator → 本插件提供编辑器侧的注册和 UI 集成入口

## 蓝图用法

InterchangeEditorUtilities 模块中的类标记为 `BlueprintType` 和 `Blueprintable`，但核心功能以 C++ 虚函数重写为主。以下是可暴露的蓝图接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FilePickerForTranslatorAssetType` | 根据资产类型弹出文件选择对话框，返回选中的文件路径列表 | `UInterchangeFilePickerGeneric` |
| `FilePickerForTranslatorType` | 根据翻译器类型弹出文件选择对话框，返回选中的文件路径列表 | `UInterchangeFilePickerGeneric` |

### 使用示例（蓝图描述）

1. 在蓝图中 Spawn 一个 `UInterchangeFilePickerGeneric` 对象
2. 调用 `FilePickerForTranslatorAssetType`，传入目标资产类型（如 `EInterchangeTranslatorAssetType::Meshes`）
3. 从 `OutFilenames` 获取用户选择的文件路径数组
4. 将路径传给 Interchange Manager 执行实际导入

> **注意**：`UInterchangeEditorUtilities` 类主要为内部使用，重写了 `SaveAsset`、`ClearEditorSelection` 等编辑器操作，不建议直接在蓝图中调用。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeEditorUtilitiesModule.h"
#include "InterchangeOpenFileDialog.h"
#include "InterchangeEditorUtilities.h"
```

### 基本用法 — 检查模块可用性

```cpp
// 来源: Public/InterchangeEditorUtilitiesModule.h
// 在使用任何功能前检查模块是否已加载
if (IInterchangeEditorUtilitiesModule::IsAvailable())
{
    IInterchangeEditorUtilitiesModule& Module = IInterchangeEditorUtilitiesModule::Get();
    // 模块已就绪，可以安全使用
}
```

### 基本用法 — 文件选择对话框

```cpp
// 创建文件选择器实例
UInterchangeFilePickerGeneric* FilePicker = NewObject<UInterchangeFilePickerGeneric>();

FInterchangeFilePickerParameters Params;
// 配置参数（如对话框标题、是否多选等）

TArray<FString> SelectedFiles;
bool bSuccess = FilePicker->FilePickerForTranslatorAssetType(
    EInterchangeTranslatorAssetType::Meshes,
    Params,
    SelectedFiles
);

if (bSuccess && SelectedFiles.Num() > 0)
{
    // 使用选中的文件路径进行导入
    for (const FString& FilePath : SelectedFiles)
    {
        // 传递给 Interchange Manager 执行导入...
    }
}
```

### 进阶用法 — 自定义文件选择器

```cpp
// 继承 UInterchangeFilePickerGeneric 实现自定义文件选择逻辑
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
        // 自定义文件过滤逻辑
        // 例如：只允许从特定目录导入
        // 或集成项目特定的资产管理系统
        return Super::FilePickerForTranslatorAssetType(TranslatorAssetType, Parameters, OutFilenames);
    }
};
```

### 进阶用法 — 自定义编辑器工具集

```cpp
// 继承 UInterchangeEditorUtilities 自定义编辑器行为
UCLASS()
class UMyInterchangeUtilities : public UInterchangeEditorUtilities
{
    GENERATED_BODY()

protected:
    virtual bool SaveAsset(UObject* Asset) const override
    {
        // 自定义资产保存逻辑（例如添加额外验证）
        return Super::SaveAsset(Asset);
    }

    virtual bool ClearEditorSelection() const override
    {
        // 自定义选区清除逻辑
        return Super::ClearEditorSelection();
    }
};
```

## Demo 示例

以下示例展示如何在编辑器工具中程序化触发 Interchange 文件导入：

```cpp
// MyInterchangeImporter.h
#pragma once

#include "CoreMinimal.h"

class FMyInterchangeImporter
{
public:
    /** 弹出文件对话框并导入选中的资产 */
    static bool ImportAssetsWithDialog();
};
```

```cpp
// MyInterchangeImporter.cpp
#include "MyInterchangeImporter.h"
#include "InterchangeEditorUtilitiesModule.h"
#include "InterchangeOpenFileDialog.h"
#include "InterchangeEditorUtilities.h"

bool FMyInterchangeImporter::ImportAssetsWithDialog()
{
    // 1. 检查模块可用性
    if (!IInterchangeEditorUtilitiesModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("InterchangeEditorUtilities module is not available."));
        return false;
    }

    // 2. 创建文件选择器
    UInterchangeFilePickerGeneric* FilePicker = NewObject<UInterchangeFilePickerGeneric>();
    if (!FilePicker)
    {
        return false;
    }

    // 3. 弹出文件选择对话框
    FInterchangeFilePickerParameters Params;
    TArray<FString> SelectedFiles;

    bool bPicked = FilePicker->FilePickerForTranslatorType(
        EInterchangeTranslatorType::StaticMesh,
        Params,
        SelectedFiles
    );

    if (!bPicked || SelectedFiles.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No files selected."));
        return false;
    }

    // 4. 获取编辑器工具实例处理保存等操作
    UInterchangeEditorUtilities* EditorUtils = NewObject<UInterchangeEditorUtilities>();

    // 5. 通过 InterchangeManager 执行导入（伪代码）
    // UInterchangeManager& Manager = UInterchangeManager::GetInterchangeManager();
    // Manager.ImportAsset(...);

    UE_LOG(LogTemp, Log, TEXT("Selected %d files for import."), SelectedFiles.Num());
    return true;
}
```

## 模块依赖

本插件有 3 个模块，均声明为 Runtime 类型（实际仅在编辑器中使用）。

当前模块 `InterchangeEditorUtilities` 的独特依赖（基于类继承关系推断）：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | 提供 `UInterchangeEditorUtilitiesBase`、`UInterchangeFilePickerBase` 等基类 |
| `InterchangeImport` | 导入框架核心，Translator/Pipeline/Factory 等基础设施 |
| `DesktopPlatform` | 提供文件对话框（`IDesktopPlatform::OpenFileDialog`）等桌面平台功能 |

> 无其他特殊依赖，其余均为标准 Core/Engine/Slate 等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `fb1426e8` | [PackageAutoSaver] Add the ability to temporarily suspend the autosaver. | 新增暂停自动保存器功能，间接影响导入流程 |
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除动画帧对齐和 glTF 翻译器帧对齐器 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loading | 新增脚本库访问器，获取关卡实例中的 Actor 而不触发加载 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重构静态网格和骨骼网格的导入设置 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐

- **活跃度**：最近 1 个月内有多次实质性更新（导入设置重构、动画对齐移除等），表明 Interchange 框架仍在积极演进
- **发展方向**：Epic 正在持续推进 Interchange 以替代传统 FBX 导入管线，本插件作为编辑器集成层会持续受益于上游更新
- **稳定性**：标记为非 Beta、默认启用，说明已达到生产可用状态
- **注意事项**：当前 3 个模块均声明为 Runtime 类型，但实际仅在编辑器中使用，这是一个已知的架构选择（避免编辑器插件对运行时模块的依赖问题）
- **推荐度**：✅ 推荐使用。Interchange 是 UE5 资产导入的未来方向，本插件是其不可或缺的编辑器集成层

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
- [Interchange 主框架](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Framework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Tests)