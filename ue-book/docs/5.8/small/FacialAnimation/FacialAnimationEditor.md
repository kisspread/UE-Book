# Facial Animation Bulk Importer

> Bulk importer for facial animation curves and audio. Imports facial animation curve tables (from FBX) into sound waves.

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画批量导入 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `FacialAnimation` (Runtime), `FacialAnimationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation) | |

## 用途

该插件为动画师提供了一个自动化工作流，用于**批量导入面部动画曲线数据和与之配套的音频文件**。它解决了在大型项目中，手动将大量包含在 FBX 文件中的面部动画曲线导入到 UE5 的 `CurveTable` 资产中，并将其与对应的 `.wav` 音频文件关联并打包到 `SoundWave` 资产中的繁琐、易错过程。通过自动化这个流程，可以极大提升内容生产管线效率。

## 使用场景

- 你是一位动画师或技术美术，拥有一批来自外部 DCC 软件（如 Maya、3ds Max）导出的、包含唇形同步曲线和音频文件的资产。
- 你需要将这些 `.fbx`（内含动画曲线）和 `.wav` 文件批量导入到 UE5 项目中，并将曲线数据烘焙到声音资产里，以便用于对话系统或面部动画。
- 你希望避免为每个文件手动执行导入和配置操作，希望有一个统一的工具来处理整个目录的资产。

## 蓝图用法

该插件主要通过**编辑器扩展界面**而非蓝图节点提供功能。其核心是一个编辑器窗口，用于配置和执行批量导入任务。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `无` | 该插件的功能主要通过编辑器菜单和窗口实现，未暴露直接的蓝图可调用函数。 | `SFacialAnimationBulkImporter` |

### 使用示例（编辑器界面描述）

1.  在 UE5 编辑器中，通过主菜单找到 `Animation` -> `Facial Animation Bulk Importer` 打开导入工具窗口。
2.  在打开的窗口中，设置 `Source Import Path`（包含 `.fbx` 和 `.wav` 文件的源目录）和 `Target Import Path`（导入后的资产存放目标目录）。
3.  指定 `Curve Node Name`，这是 FBX 文件中包含动画曲线的节点名称。
4.  点击 `Import` 按钮，插件将自动扫描源目录，将找到的 FBX 和 WAV 文件配对，导入动画曲线并创建包含曲线数据的 `SoundWave` 资产。

## C++ 用法

该插件的 Runtime 模块 (`FacialAnimation`) 提供了数据结构，Editor 模块 (`FacialAnimationEditor`) 提供了导入逻辑和 UI。

### 头文件引入

```cpp
// 用于配置导入设置
#include "FacialAnimationBulkImporterSettings.h"

// 用于表示单个导入项
#include "FacialAnimationImportItem.h"
```

### 基本用法

通过 C++ 操作批量导入设置和单个导入项。`UFacialAnimationBulkImporterSettings` 是一个 `UPROPERTY` 驱动的配置类，其属性会保存在用户的编辑器配置文件中。

```cpp
// 来源：Private/FacialAnimationBulkImporterSettings.h
// 创建或获取导入设置对象
UClass* SettingsClass = UFacialAnimationBulkImporterSettings::StaticClass();
UFacialAnimationBulkImporterSettings* ImportSettings = GetMutableDefault<UFacialAnimationBulkImporterSettings>();

// 配置导入路径（通常在构造函数或初始化代码中）
ImportSettings->SourceImportPath.Path = TEXT("/Game/Characters/Dialog/FBX_Audio/");
ImportSettings->TargetImportPath.Path = TEXT("/Game/Characters/Dialog/Imported/");
ImportSettings->CurveNodeName = TEXT("CurveSource"); // FBX中包含曲线的节点名
```

### 进阶用法

构建一个 `FFacialAnimationImportItem` 并执行导入。这模拟了插件批量导入器内部对单个文件对的操作逻辑。

```cpp
// 来源：Public/FacialAnimationImportItem.h
// 假设已有一组配对的FBX和WAV文件路径
FString FbxFilename = TEXT("/path/to/Dialog_01.fbx");
FString WavFilename = TEXT("/path/to/Dialog_01.wav");
FString AssetBaseName = TEXT("Dialog_01");

// 创建导入项
FFacialAnimationImportItem ImportItem;
ImportItem.FbxFile = FbxFilename;
ImportItem.WaveFile = WavFilename;
ImportItem.TargetPackageName = TEXT("/Game/Characters/Dialog/Imported/");
ImportItem.TargetAssetName = AssetBaseName;

// 执行导入
bool bSuccess = ImportItem.Import();
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("成功导入: %s"), *AssetBaseName);
}
else
{
    UE_LOG(LogTemp, Error, TEXT("导入失败: %s"), *AssetBaseName);
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何配置和使用导入项。

**FacialAnimationDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "FacialAnimationImportItem.h" // 包含导入项结构体

class FFacialAnimationDemo
{
public:
    /** 演示如何导入单个文件对 */
    static void ImportSingleDialogItem(
        const FString& InFbxFilename,
        const FString& InWavFilename,
        const FString& InAssetName,
        const FString& InTargetPath);
};
```

**FacialAnimationDemo.cpp**
```cpp
#include "FacialAnimationDemo.h"
#include "FacialAnimationImportItem.h"

void FFacialAnimationDemo::ImportSingleDialogItem(
    const FString& InFbxFilename,
    const FString& InWavFilename,
    const FString& InAssetName,
    const FString& InTargetPath)
{
    // 创建导入项结构体
    FFacialAnimationImportItem ImportItem;
    ImportItem.FbxFile = InFbxFilename;
    ImportItem.WaveFile = InWavFilename;
    ImportItem.TargetPackageName = InTargetPath; // e.g., TEXT("/Game/Dialog/Audio/")
    ImportItem.TargetAssetName = InAssetName;

    // 执行导入，该函数内部会处理FBX曲线提取和SoundWave创建
    bool bImported = ImportItem.Import();

    if (bImported)
    {
        UE_LOG(LogTemp, Display, TEXT("Demo: 成功导入对话资产 '%s'"), *InAssetName);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Demo: 导入对话资产 '%s' 失败"), *InAssetName);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FacialAnimation` | 提供 `FFacialAnimationImportItem` 等核心数据结构 |
| `AssetTools` | 用于在编辑器中创建和管理资产 |
| `AssetRegistry` | 用于在导入过程中查询和操作资产注册表 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applies to…) | 为源文件添加内联生成宏，统一代码风格，提升编译一致性。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i… | 使用新构建目标转换源文件，调整符号导出声明以适应新的构建系统要求。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件目录结构的通用性调整或更新。 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty… | 为未来的代码修改预先添加必要的头文件包含，属于前瞻性准备。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件中供应商链接更新为更安全的 HTTPS 协议。 |

### 维护评价

- **创建时间**：2016 年，距今约 9 年。
- **最近更新**：最后一次有意义的提交记录在 2022 年。2025 年的更新均为底层代码构建和格式的适配，没有功能性改进或 Bug 修复。
- **活跃度**：**维护不活跃**。该插件长期处于“实验性/Beta”状态，且近年几乎没有功能性更新。最近的提交表明 Epic 可能在进行大规模的代码库现代化（如统一符号导出），该插件只是被动地随着更新。
- **已知问题/限制**：标记为 `IsBetaVersion: true`，且未包含内容资产（`CanContainContent: false`）。意味着它可能未经充分测试，且不提供示例数据。
- **推荐使用**：**谨慎使用**。对于有明确批量导入面部动画需求的团队，该工具的逻辑仍然有效。但由于它长期处于 Beta 状态，且依赖项（如 `FacialAnimation` 运行时模块）的维护状态不明确，建议在新项目中评估更现代的替代方案（如 MetaHuman Animator 或自定义 Python/蓝图工具链）。在老项目维护中如果已有工作流依赖它，则可以继续使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）
- 测试用例：未在提供的信息中发现明确的自动化测试文件。其功能主要通过编辑器交互验证。