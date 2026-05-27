# Facial Animation Bulk Importer

> Bulk importer for facial animation curves and audio. Imports facial animation curve tables (from FBX) into sound waves.

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画批量导入 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `FacialAnimation` (Runtime), `FacialAnimationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation) | |

## 用途

这个插件解决的是面部动画（Facial Animation）工作流中的批量导入问题。在对话驱动的游戏（如 RPG、互动电影）中，美术通常会使用 DCC 工具（如 Maya）导出大量的面部表情曲线（FBX）和对应的语音音频（WAV）。手工逐个导入到 UE 并将曲线数据嵌入到 SoundWave 资产中是一项繁琐且易出错的工作。

FacialAnimation 插件提供了：
1. **批量导入工具**：从指定目录批量读取 FBX（包含面部动画曲线）和 WAV 文件，自动创建或更新 SoundWave 资产
2. **曲线嵌入**：将 FBX 中的面部动画曲线表（Curve Table）直接嵌入到 SoundWave 资产中，实现音频与口型动画的精确同步
3. **曲线源接口**（IcurveSourceInterface）：允许任何实现该接口的组件或 Actor 驱动曲线，实现灵活的面部动画回放

插件的核心思路是将"音频 + 面部曲线"打包为一个 SoundWave 资产，运行时可以通过自定义音频组件同步播放音频和驱动 Morph Target。

## 使用场景

- 你在做一个对话密集型游戏，有数百条配音 + 对应的面部动画 FBX 需要批量导入
- 你需要将面部动画曲线（如 Morph Target 权重曲线）与音频精确同步
- 你的美术流水线使用 DCC 工具导出 FBX 曲线和 WAV 音频，需要自动化的导入方案
- 你需要在 Persona 编辑器中预览音频播放并同步查看面部动画曲线

## 蓝图用法

此插件主要是编辑器工具，不暴露大量 Blueprint 可调用的运行时 API。核心功能通过编辑器 UI（批量导入窗口）和编辑器设置面板操作。

### 可配置属性

`UFacialAnimationBulkImporterSettings` 中的属性可在 **编辑器偏好设置** 中找到：

| 属性 | 类型 | 说明 |
|---|---|---|
| `SourceImportPath` | `FDirectoryPath` | FBX/WAV 源文件所在目录 |
| `TargetImportPath` | `FDirectoryPath` | 导入后的 SoundWave 资产输出目录（内容目录） |
| `CurveNodeName` | `FString` | FBX 场景中包含曲线数据的节点名称 |

### 导入操作

插件会在编辑器中注册一个 Slate 面板（`SFacialAnimationBulkImporter`），提供：
- **Import 按钮**：根据设置路径批量导入所有 FBX + WAV 文件对
- 自动将 FBX 中的曲线数据嵌入到对应的 SoundWave 资产中

## C++ 用法

### 核心类

| 类 | 说明 |
|---|---|
| `FFacialAnimationEditorModule` | 编辑器模块入口，处理模块加载/卸载、预览场景创建 |
| `UFacialAnimationBulkImporterSettings` | 导入配置（源路径、目标路径、曲线节点名） |
| `FFacialAnimationImportItem` | 单个导入项，封装 FBX + WAV 文件对的导入逻辑 |
| `SFacialAnimationBulkImporter` | 批量导入 Slate UI 面板 |

### 基本用法：程序化导入单个文件对

```cpp
#include "FacialAnimationImportItem.h"

// 构建一个导入项
FFacialAnimationImportItem ImportItem;
ImportItem.FbxFile = TEXT("/Path/To/character_face.fbx");
ImportItem.WaveFile = TEXT("/Path/To/dialogue_line_001.wav");
ImportItem.TargetPackageName = TEXT("/Game/Audio/Dialogues/Line001");
ImportItem.TargetAssetName = TEXT("Line001");

// 执行导入：创建 SoundWave 并嵌入曲线数据
bool bSuccess = ImportItem.Import();
```

### 进阶用法：自定义导入设置

```cpp
#include "FacialAnimationBulkImporterSettings.h"

// 获取导入设置（编辑器偏好设置中的单例）
UFacialAnimationBulkImporterSettings* Settings = GetMutableDefault<UFacialAnimationBulkImporterSettings>();

// 配置路径和 FBX 节点名
Settings->SourceImportPath.Path = TEXT("/Users/artist/facial_capture/batch_01");
Settings->TargetImportPath.Path = TEXT("/Game/Audio/FacialAnimation");
Settings->CurveNodeName = TEXT("FacialCurves");

// 保存设置
Settings->SaveConfig();
```

## Demo 示例

### 最小批量导入示例

**FacialAnimBatchImport.h**

```cpp
#pragma once

#include "CoreMinimal.h"

class FFacialAnimBatchImporter
{
public:
    /** 批量导入指定目录下的所有 FBX+WAV 文件对 */
    static int32 BatchImportFromDirectory(
        const FString& InSourceDir,
        const FString& InTargetDir,
        const FString& InCurveNodeName);

private:
    /** 查找目录中成对的 FBX 和 WAV 文件 */
    static void FindFilePairs(
        const FString& InDirectory,
        TArray<TPair<FString, FString>>& OutFilePairs);
};
```

**FacialAnimBatchImport.cpp**

```cpp
#include "FacialAnimBatchImport.h"
#include "FacialAnimationImportItem.h"
#include "HAL/FileManager.h"

int32 FFacialAnimBatchImporter::BatchImportFromDirectory(
    const FString& InSourceDir,
    const FString& InTargetDir,
    const FString& InCurveNodeName)
{
    TArray<TPair<FString, FString>> FilePairs;
    FindFilePairs(InSourceDir, FilePairs);

    int32 ImportedCount = 0;
    for (const auto& Pair : FilePairs)
    {
        // 提取资产名称（去掉扩展名）
        FString AssetName = FPaths::GetBaseFilename(Pair.Key);
        FString PackageName = InTargetDir / AssetName;

        FFacialAnimationImportItem ImportItem;
        ImportItem.FbxFile = Pair.Key;
        ImportItem.WaveFile = Pair.Value;
        ImportItem.TargetPackageName = PackageName;
        ImportItem.TargetAssetName = AssetName;

        if (ImportItem.Import())
        {
            ++ImportedCount;
            UE_LOG(LogTemp, Log, TEXT("Imported: %s"), *AssetName);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Failed to import: %s"), *AssetName);
        }
    }

    return ImportedCount;
}

void FFacialAnimBatchImporter::FindFilePairs(
    const FString& InDirectory,
    TArray<TPair<FString, FString>>& OutFilePairs)
{
    // 查找所有 FBX 文件
    TArray<FString> FbxFiles;
    IFileManager::Get().FindFiles(FbxFiles, *(InDirectory / TEXT("*.fbx")), true, false);

    for (const FString& FbxFile : FbxFiles)
    {
        // 尝试匹配同名的 WAV 文件
        FString BaseName = FPaths::GetBaseFilename(FbxFile);
        FString WavFile = InDirectory / (BaseName + TEXT(".wav"));

        if (FPaths::FileExists(WavFile))
        {
            OutFilePairs.Add(TPair<FString, FString>(
                InDirectory / FbxFile, WavFile));
        }
    }
}
```

## 模块依赖

由于未获取到 Build.cs 的完整内容，以下为基于源码分析推断的依赖关系。实际使用时请以源码中 Build.cs 为准。

无特殊依赖（仅标准 Core/Engine/Slate 等）。插件可能隐式依赖 FBX 导入模块和音频模块，但这些通常作为 Engine 的一部分自动可用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏，属于编译优化改动 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 统一修改为 DLL 导出声明格式，构建系统批量调整 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | Engine/Plugins 范围的批量改动，无具体描述 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 为未来改动预先添加头文件引用 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接为 HTTPS 安全协议 |

### 维护评价

**⚠️ 维护不活跃 / 可能废弃**

- **创建时间**：2016 年 11 月，至今约 9 年
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，从创建起就标记为实验性，从未正式发布
- **更新情况**：近 3 年的所有 commit 均为全局批量改动（宏更新、构建系统调整、链接修复），**没有任何功能性更新或 Bug 修复**
- **最后实质性更新**：约在 2017-2018 年前后（推断），之后仅有编译兼容性维护
- **已知限制**：自 2016 年创建以来一直是 Beta 状态，从未毕业为正式功能
- **推荐程度**：**不推荐在新项目中使用**。该插件属于 Epic 内部实验性工具，长期未被积极维护。如果需要面部动画导入功能，建议考虑：
  - 使用 UE 原生的曲线表（Curve Table）导入功能
  - 通过 Python 脚本或编辑器脚本自建导入管线
  - 考虑 MetaHuman 等更现代的面部动画方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：未发现（插件源码仅 12 个文件，无自动化测试）