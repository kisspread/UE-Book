# Facial Animation Bulk Importer

> Bulk importer for facial animation curves and audio. Imports facial animation curve tables (from FBX) into sound waves.

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画批量导入器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `FacialAnimation` (Runtime), `FacialAnimationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation) | |

## 用途

这是一个用于面部动画工作流的批量导入工具。核心功能是将 FBX 文件中的面部动画曲线数据（morph target / blend shape 曲线）批量导入为 UE 的 Curve Table，并将其嵌入到 SoundWave 资产中。

**解决的问题**：面部动画通常以曲线（curves）形式存储面部表情的变化，同时配有对应的语音音频文件。该插件将 FBX 中的曲线数据与 WAV 音频文件批量打包，使面部动画曲线与音频绑定在同一个 SoundWave 资产内，方便运行时同步播放嘴型动画和语音。

插件还提供了曲线源接口（`ICurveSourceInterface`），允许任意实现了该接口的 Actor 或 Component 来驱动曲线数据，实现灵活的动画驱动架构。

## 使用场景

- 你正在制作一个带有配音的角色对话系统，需要将面部表情曲线和语音音频批量导入并绑定 → 用此插件
- 你的美术团队从 DCC 工具（Maya/3ds Max）导出大量 FBX 面部动画和 WAV 音频文件，需要快速批量导入 → 用此插件
- 你需要在 Persona 中预览音频与面部曲线同步播放效果 → 用此插件提供的 Audio Preview 功能

## 蓝图用法

该插件主要是编辑器工具，暴露给蓝图的 API 较少。核心 UI 功能通过 Slate 编辑器窗口提供。

### 核心节点

该插件未暴露 `BlueprintCallable` 函数。导入功能通过编辑器 UI（批量导入器窗口）操作。

### 设置项

导入行为由 `UFacialAnimationBulkImporterSettings` 控制，可在 **项目设置 > 编辑器** 中配置：

| 属性 | 说明 |
|---|---|
| `SourceImportPath` | FBX 和 WAV 源文件所在目录 |
| `TargetImportPath` | 导入后的资产输出目录 |
| `CurveNodeName` | FBX 场景中包含曲线数据的节点名称 |

### 使用示例（编辑器操作描述）

1. 打开批量导入器窗口
2. 设置 `SourceImportPath` 指向包含 FBX 和 WAV 文件的目录
3. 设置 `TargetImportPath` 指向 Content Browser 中的目标位置
4. 填写 `CurveNodeName`（FBX 中存放面部曲线的节点名）
5. 点击"导入"按钮，批量生成包含曲线数据的 SoundWave 资产

## C++ 用法

### 头文件引入

```cpp
#include "FacialAnimationImportItem.h"
```

### 基本用法

单个导入项的结构与导入流程：

```cpp
#include "FacialAnimationImportItem.h"

// 创建导入项
FFacialAnimationImportItem ImportItem;
ImportItem.FbxFile = TEXT("/path/to/face_anim.fbx");
ImportItem.WaveFile = TEXT("/path/to/dialogue.wav");
ImportItem.TargetPackageName = TEXT("/Game/Audio/Dialogue/Dialogue_001");
ImportItem.TargetAssetName = TEXT("Dialogue_001");

// 执行导入：会将 FBX 曲线数据导入 SoundWave
bool bSuccess = ImportItem.Import();
```

> 来源：`Engine/Plugins/Editor/FacialAnimation/Source/FacialAnimationEditor/Public/FacialAnimationImportItem.h`

### 进阶用法

通过 `Import()` 内部流程，插件会执行两步操作：

1. **`ImportSoundWave()`**：将 WAV 文件导入为 `USoundWave` 资产
2. **`ImportCurvesEmbeddedInSoundWave()`**：将 FBX 中的曲线数据嵌入到该 SoundWave 中

```cpp
// ImportItem 内部调用示意（基于头文件接口推断）
FFacialAnimationImportItem ImportItem;
ImportItem.FbxFile = TEXT("C:/Animations/Character_A/face_001.fbx");
ImportItem.WaveFile = TEXT("C:/Audio/Character_A/dialogue_001.wav");
ImportItem.TargetPackageName = TEXT("/Game/Characters/Character_A/Dialogue/A_Dialogue_001");
ImportItem.TargetAssetName = TEXT("A_Dialogue_001");

// Import() 内部会：
// 1. 调用 ImportSoundWave() 创建 SoundWave
// 2. 调用 ImportCurvesEmbeddedInSoundWave() 嵌入 FBX 曲线
if (ImportItem.Import())
{
    // 导入成功，SoundWave 已包含面部动画曲线
}
```

## Demo 示例

该插件主要是编辑器批处理工具，无运行时组件可演示。以下展示设置类的典型用法：

```cpp
// MyFacialAnimTool.h
#pragma once

#include "CoreMinimal.h"

class FMyFacialAnimTool
{
public:
    /** 批量导入目录下所有 FBX + WAV 对 */
    void BatchImport(const FString& InSourceDir, const FString& InTargetDir, const FString& InCurveNodeName);

    /** 匹配同名的 FBX 和 WAV 文件并导入 */
    void ImportMatchedPairs(const TArray<TPair<FString, FString>>& InFbxWavPairs,
                            const FString& InTargetBasePath,
                            const FString& InCurveNodeName);
};
```

```cpp
// MyFacialAnimTool.cpp
#include "MyFacialAnimTool.h"
#include "FacialAnimationImportItem.h"
#include "HAL/FileManager.h"
#include "Misc/Paths.h"

void FMyFacialAnimTool::BatchImport(const FString& InSourceDir, const FString& InTargetDir, const FString& InCurveNodeName)
{
    // 扫描源目录中的 FBX 文件
    TArray<FString> FbxFiles;
    IFileManager::Get().FindFilesRecursive(FbxFiles, *InSourceDir, TEXT("*.fbx"), true, false);

    TArray<TPair<FString, FString>> Pairs;
    for (const FString& FbxFile : FbxFiles)
    {
        // 查找同名 WAV 文件
        FString BaseName = FPaths::GetBaseFilename(FbxFile);
        FString WavFile = FPaths::GetPath(FbxFile) / BaseName + TEXT(".wav");

        if (FPaths::FileExists(WavFile))
        {
            Pairs.Add({FbxFile, WavFile});
        }
    }

    ImportMatchedPairs(Pairs, InTargetDir, InCurveNodeName);
}

void FMyFacialAnimTool::ImportMatchedPairs(const TArray<TPair<FString, FString>>& InFbxWavPairs,
                                            const FString& InTargetBasePath,
                                            const FString& InCurveNodeName)
{
    for (const auto& Pair : InFbxWavPairs)
    {
        FFacialAnimationImportItem ImportItem;
        ImportItem.FbxFile = Pair.Key;
        ImportItem.WaveFile = Pair.Value;

        FString BaseName = FPaths::GetBaseFilename(Pair.Key);
        ImportItem.TargetPackageName = InTargetBasePath / BaseName;
        ImportItem.TargetAssetName = BaseName;

        if (ImportItem.Import())
        {
            UE_LOG(LogTemp, Log, TEXT("Successfully imported: %s"), *BaseName);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Failed to import: %s"), *BaseName);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加内联宏以优化编译 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 修改 DLL 导出符号 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件级别批量改动 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 预添加头文件包含 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新为 HTTPS 链接 |

### 维护评价

该插件自 2016 年创建以来标记为 **Beta/Experimental**，至今未脱离实验状态。最近的提交均为编译维护性改动（DLL 导出、宏添加、头文件整理），**无任何功能性更新**。

⚠️ **该插件可能已处于事实废弃状态**。超过 8 年未有任何功能增强，且仍标记为实验性。Epics 可能已将面部动画功能整合到其他系统（如 MetaHuman 工具链）。建议仅作为历史参考，生产环境使用需谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation)