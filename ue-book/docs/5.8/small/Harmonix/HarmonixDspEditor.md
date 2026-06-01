# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频工具包 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（FusionPatch 资产类型定义） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime), `HarmonixEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 插件是由 Harmonix GenTech 团队（《Guitar Hero》《Rock Band》开发商）移植到 UE5 的音乐音频技术工具包。它解决的核心问题是：**在游戏引擎中实现专业级的音乐采样器、MIDI 处理和音乐感知音频处理**。

插件的实际功能远超 .uplugin 描述的"音乐相关音频功能"，具体包括：

1. **FusionSampler / FusionPatch**：一套完整的采样器乐器系统，支持键区（Keyzone）映射、力度分层、ADSR 包络、LFO、滤波器、时间拉伸、滑音（Portamento）、多模式声像控制和变调。类似于 Kontakt 或 Logic Pro 的 EXS24，但运行在 UE5 内部。
2. **MIDI 文件支持**：完整的 MIDI 文件解析与播放能力。
3. **MetaSound 集成**：为 UE5 的 MetaSound 系统提供音乐相关的自定义节点。
4. **DSP 工具**：底层音频信号处理工具集。
5. **格式导入**：支持 JSON 和 DTA 格式的 FusionPatch 导入，兼容 Harmonix 既有的音乐制作工具链。

**默认禁用且标记为实验性**，说明该插件仍在快速迭代中，API 可能发生变化。

## 使用场景

- 你正在开发**节奏音乐游戏**（如 Guitar Hero 风格），需要在游戏中播放和控制 MIDI 乐器 → 使用 FusionSampler 和 MIDI 模块
- 你需要在 UE5 中实现**动态音乐系统**，根据游戏状态实时控制采样器乐器的参数 → 使用 FusionPatch 的 ADSR/LFO/滤波器控制
- 你有一批来自**Harmonix 旧工具链的 JSON/DTA 格式采样器配置**，需要导入到 UE5 → 使用 FusionPatch Json/DTA 导入器
- 你需要通过 **MetaSound 图表**实现音乐感知的音频处理节点 → 使用 HarmonixMetasound 模块
- 你需要解析和播放**标准 MIDI 文件**用于游戏配乐 → 使用 HarmonixMidi 模块

## 蓝图用法

该插件主要提供**编辑器侧的资产创建和导入工具**，运行时蓝图 API 通过 FusionPatch 资产和 MetaSound 节点暴露。以下为编辑器中可直接使用的核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| FusionPatch 创建对话框 | 弹出对话框配置采样器乐器的键区映射、根音、力度分层等参数 | `UFusionPatchCreateOptions` |
| FusionPatch 导入对话框 | 弹出对话框配置采样导入路径、加载行为、压缩类型 | `UFusionPatchImportOptions` |

### FusionPatch 创建流程（编辑器描述）

1. 在 Content Browser 中右键 → Audio 分类下选择 **Create Fusion Patch**
2. 弹出 `UFusionPatchCreateOptions` 对话框，配置：
   - **Destination**：FusionPatch 保存目录
   - **Asset Name**：资产名称
   - **Assign Notes By**：音符解析方式（按音名、音高数字、索引或字母顺序）
   - **Keyzone Layout**：键区布局方式（单音 / 分布 / 层叠）
   - **Scale Mapping**：是否按音阶分布（大调音阶或等距）
   - **Note Alignment**：根音对齐方式（对齐最小/最大/居中）
   - **Min/Max Note**：音高范围（0-127）
   - **Octave Adjust**：八度偏移调整
3. 配置完成后可拖入 SoundWave 资产，系统自动解析文件名中的音高信息并分配键区

### FusionPatch 导入流程

1. 将 `.json` 或 `.dt` 格式的 FusionPatch 文件拖入 Content Browser
2. 弹出 `UFusionPatchImportOptions` 对话框，配置：
   - **Sound Waves Import Folder**：采样文件保存目录
   - **Sound Wave Loading Behavior**：加载行为（RetainOnLoad 等）
   - **Sound Wave Compression Type**：压缩格式（BinkAudio 等）
3. 系统自动解析 JSON/DTA 并创建 FusionPatch 资产及关联的 SoundWave

## C++ 用法

### 头文件引入

```cpp
// FusionPatch 资产
#include "HarmonixDsp/FusionPatch/FusionPatch.h"

// MIDI 文件处理
#include "HarmonixMidi/MidiFile.h"

// MetaSound 节点
#include "HarmonixMetasound/..."

// 编辑器工具
#include "HarmonixDspEditorModule.h"
#include "HarmonixDspEditorUtils.h"
```

### 基本用法 — ADSR 包络生成

来自 `HarmonixDspEditorUtils.h`，生成 ADSR 包络波形数据用于可视化或分析。

```cpp
#include "HarmonixDspEditorUtils.h"
#include "HarmonixDsp/Modulators/Settings/AdsrSettings.h"
#include "DSP/AlignedBuffer.h"

void GenerateAdsrVisualization()
{
    // 配置 ADSR 参数
    FAdsrSettings AdsrSettings;
    AdsrSettings.AttackTime = 0.01f;   // 10ms 起音
    AdsrSettings.DecayTime = 0.1f;     // 100ms 衰减
    AdsrSettings.SustainLevel = 0.7f;  // 持续电平 70%
    AdsrSettings.ReleaseTime = 0.5f;   // 500ms 释音

    const float SustainTime = 1.0f;    // 持续阶段持续 1 秒
    const float SampleRate = 48000.0f;

    // 生成包络缓冲区
    Audio::FAlignedFloatBuffer EnvelopeBuffer;
    Harmonix::Dsp::Editor::GenerateAdsrEnvelope(AdsrSettings, SustainTime, SampleRate, EnvelopeBuffer);
    
    // EnvelopeBuffer 中现在包含完整的 ADSR 包络波形数据
    // 可用于 UI 绘制、音频分析等用途
}
```

### 基本用法 — 键区音符解析

来自 `FusionPatchImportOptions.h` 中的 `FKeyzoneNoteParser`，从采样文件名中解析音高信息。

```cpp
#include "FusionPatchImportOptions.h"

void ParseSampleNames()
{
    FKeyzoneNoteParser::FParseResult Result;

    // 解析 "piano_C3_E3_G3" 格式（最小_根_最大）
    if (FKeyzoneNoteParser::ParseMinRootMax(TEXT("piano_C3_E3_G3"), Result))
    {
        // Result.MinNote = C3 对应的 MIDI 编号
        // Result.RootNote = E3 对应的 MIDI 编号
        // Result.MaxNote = G3 对应的 MIDI 编号
    }

    // 解析 "snare_48_60" 格式（最小_最大）
    if (FKeyzoneNoteParser::ParseMinMax(TEXT("snare_48_60"), Result))
    {
        // Result.MinNote = 48, Result.MaxNote = 60
    }

    // 解析音名格式 "Eb1", "G#3"
    if (FKeyzoneNoteParser::ParseNoteName(TEXT("G#3"), Result))
    {
        // Result.RootNote = G#3 对应的 MIDI 编号 (56)
    }
}
```

### 进阶用法 — JSON 导入 FusionPatch

来自 `FusionPatchJsonImporter.h`，解析 JSON 格式的 FusionPatch 配置。

```cpp
#include "FusionPatchJsonImporter.h"
#include "HarmonixDsp/FusionPatch/FusionPatch.h"

bool ImportFusionPatchFromJson(const FString& JsonString, const FString& DestPath)
{
    // 1. 验证 JSON 格式
    if (!FJsonImporter::CanImportJson(JsonString))
    {
        UE_LOG(LogFusionPatchJsonImporter, Error, TEXT("Invalid JSON format"));
        return false;
    }

    // 2. 解析 JSON 对象
    FString ErrorMessage;
    TSharedPtr<FJsonObject> JsonObject = FJsonImporter::ParseJsonString(JsonString, ErrorMessage);
    if (!JsonObject.IsValid())
    {
        UE_LOG(LogFusionPatchJsonImporter, Error, TEXT("Parse error: %s"), *ErrorMessage);
        return false;
    }

    // 3. 配置导入参数
    FFusionPatchJsonImporter::FImportArgs ImportArgs;
    ImportArgs.Name = FName("MyFusionPatch");
    ImportArgs.SourcePath = TEXT("/Path/To/Source");
    ImportArgs.DestPath = DestPath;
    ImportArgs.SamplesDestPath = DestPath / TEXT("Samples");
    ImportArgs.ReplaceExistingSamples = false;
    ImportArgs.SampleLoadingBehavior = ESoundWaveLoadingBehavior::RetainOnLoad;
    ImportArgs.SampleCompressionType = ESoundAssetCompressionType::BinkAudio;

    // 4. 创建 FusionPatch 资产并解析
    UFusionPatch* FusionPatch = NewObject<UFusionPatch>();
    TArray<UObject*> AdditionalObjects;
    TArray<FString> Errors;

    bool bSuccess = FFusionPatchJsonImporter::TryParseJson(
        JsonObject, FusionPatch, AdditionalObjects, ImportArgs, Errors);

    if (!bSuccess)
    {
        for (const FString& Err : Errors)
        {
            UE_LOG(LogFusionPatchJsonImporter, Warning, TEXT("%s"), *Err);
        }
    }

    return bSuccess;
}
```

### 进阶用法 — DTA 格式转换

来自 `DtaParser.h`，将 Harmonix 旧工具链的 DTA 格式转为 JSON。

```cpp
#include "Dta/DtaParser.h"

bool ConvertDtaToJson(const FString& DtaFilePath)
{
    // 读取 DTA 文件
    FString DtaContent;
    if (!FFileHelper::LoadFileToString(DtaContent, *DtaFilePath))
    {
        return false;
    }

    // 将 DTA 格式转为 JSON
    FString JsonString;
    FString ErrorMessage;
    if (!FDtaParser::DtaStringToJsonString(DtaContent, JsonString, ErrorMessage))
    {
        UE_LOG(LogDtaParser, Error, TEXT("DTA parse failed: %s"), *ErrorMessage);
        return false;
    }

    // JsonString 现在可直接传给 FFusionPatchJsonImporter::TryParseJson
    return true;
}
```

## Demo 示例

以下示例展示如何在编辑器插件中注册自定义菜单项来批量导入 FusionPatch：

### FusionPatchBatchImporter.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FFusionPatchBatchImporterModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterMenus();
    void OnBatchImportClicked();
    void ImportAllJsonInDirectory(const FString& Directory);
};
```

### FusionPatchBatchImporter.cpp

```cpp
#include "FusionPatchBatchImporterModule.h"
#include "FusionPatchJsonImporter.h"
#include "FusionPatchImportOptions.h"
#include "ToolMenus.h"
#include "ContentBrowserModule.h"
#include "Misc/Paths.h"

void FFusionPatchBatchImporterModule::StartupModule()
{
    UToolMenus::RegisterStartupCallback(
        FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FFusionPatchBatchImporterModule::RegisterMenus));
}

void FFusionPatchBatchImporterModule::ShutdownModule()
{
    UToolMenus::UnRegisterStartupCallback(this);
    UToolMenus::UnregisterOwner(this);
}

void FFusionPatchBatchImporterModule::RegisterMenus()
{
    UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("ContentBrowser.AssetContextMenu");
    FToolMenuSection& Section = Menu->FindOrAddSection("GetAssetActions");
    Section.AddMenuEntry(
        "BatchImportFusionPatch",
        FText::FromString(TEXT("Batch Import FusionPatches")),
        FText::FromString(TEXT("Import all JSON FusionPatch files from a directory")),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateRaw(this, &FFusionPatchBatchImporterModule::OnBatchImportClicked))
    );
}

void FFusionPatchBatchImporterModule::OnBatchImportClicked()
{
    // 获取导入选项
    UFusionPatchImportOptions::FArgs Args;
    Args.PatchName = FName("BatchImport");
    Args.Directory = FPaths::ProjectContentDir();

    bool bWasOkayPressed = false;
    const UFusionPatchImportOptions* Options = 
        UFusionPatchImportOptions::GetWithDialog(MoveTemp(Args), bWasOkayPressed);

    if (bWasOkayPressed && Options)
    {
        ImportAllJsonInDirectory(Options->SamplesImportDir.Path);
    }
}

void FFusionPatchBatchImporterModule::ImportAllJsonInDirectory(const FString& Directory)
{
    TArray<FString> JsonFiles;
    IFileManager::Get().FindFilesRecursive(
        JsonFiles, *Directory, TEXT("*.json"), true, false);

    for (const FString& JsonFile : JsonFiles)
    {
        FString JsonContent;
        if (FFileHelper::LoadFileToString(JsonContent, *JsonFile))
        {
            if (FJsonImporter::CanImportJson(JsonContent))
            {
                UE_LOG(LogTemp, Log, TEXT("Importing FusionPatch: %s"), *JsonFile);
                // 实际导入逻辑...
            }
        }
    }
}
```

## 模块依赖

从各模块的 Build.cs 提取的**非标准依赖**如下（已省略 Core、CoreUObject、Engine、Slate 等常见依赖）：

| 模块 | 用途 | 使用者 |
|---|---|---|
| `AssetRegistry` | 资产注册与发现 | HarmonixDsp, HarmonixMetasound, HarmonixMidi |
| `UnrealEd` | 编辑器功能（工厂、资产定义等） | HarmonixDsp, HarmonixMetasound, HarmonixMidi |
| `MetasoundEngine` | MetaSound 系统集成 | HarmonixMetasound |
| `MetasoundFrontend` | MetaSound 前端图表系统 | HarmonixMetasound |
| `SignalProcessing` | 底层 DSP 信号处理 | HarmonixDsp |
| `AudioMixer` | 音频混音器接口 | HarmonixDsp |

**注意**：该插件的 Runtime 模块依赖了 `UnrealEd`，这是非典型的设计，可能是因为某些运行时类型注册需要编辑器类型。使用时需注意模块加载顺序。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 FusionVoice 键区排序 bug，增加空值防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃重构的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ... | 为 FusionPatch 代理添加用户对象，支持活动追踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化说明符不匹配的问题 |

### 维护评价

- **创建时间**：2024 年 1 月（从 Harmonix 内部仓库移入 UE5 5.4 发行）
- **更新频率**：**非常活跃**——2026 年 5 月有多次功能性更新和 bug 修复，几乎每天都有提交
- **维护状态**：**活跃维护中**——持续有新功能添加（如 FusionPatch 代理的用户对象追踪）和核心 bug 修复（键区排序、API 兼容性）
- **已知限制**：
  - 标记为 **IsExperimentalVersion=true**，API 可能随版本变化
  - **EnabledByDefault=false**，需手动在项目设置中启用
  - Runtime 模块依赖 UnrealEd，打包时需注意模块配置
- **推荐程度**：⭐⭐⭐⭐ —— 如果你正在开发音乐/节奏类游戏，这是目前 UE5 中最专业的音乐工具链。但需注意实验性状态，做好应对 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- [测试用例 — DSP](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspTests)
- [测试用例 — MetaSound](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests)
- [测试用例 — MIDI](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests)