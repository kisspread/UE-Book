# Waveform Editor

> Editor tool for waveforms

| 属性 | 值 |
|---|---|
| 中文名 | 波形编辑器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `WaveformEditor` (Editor), `WaveformEditorWidgets` (Runtime), `WaveformTransformations` (Runtime), `WaveformTransformationsWidgets` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WaveformEditor) | |

## 用途

Waveform Editor 是一个 UE5 编辑器内工具，其核心功能远超简单的波形查看。它为 `USoundWave` 资产提供了一个完整的可视化编辑和变换工作空间。开发者可以通过它精确地编辑音频的起始与结束点（淡入/淡出）、设置循环区域、添加标记点（Cue Points）、实时预览变换效果，并将编辑后的音频导出为新的资产。它解决的核心问题是：在编辑器内对游戏音频资产进行非破坏性的、可视化的精细调整，而无需依赖外部数字音频工作站（DAW）。

## 使用场景

-   **音频设计师**：需要精确裁剪音效文件的起始和结束部分，制作平滑的淡入/淡出效果。
-   **游戏开发者**：需要为环境音或背景音乐创建无缝循环区域。
-   **关卡设计师**：需要为事件触发点（如脚步声、门声）在音效上精确添加标记点（Cue Points）。
-   **音频工程师**：需要快速预览对音频应用各种变换（如时间拉伸、音量标准化）后的效果，并批量导出处理后的文件。
-   **项目维护**：使用 `ResaveSoundWaveLoudness` 命令行工具，批量为旧版本引擎创建的音效资产计算并添加响度（LUFS）元数据。

## 蓝图用法

此插件主要作为**编辑器工具**运行，其核心功能（编辑器UI、命令、变换逻辑）未暴露给蓝图系统。分析 `Public` 目录下的头文件，未发现任何标记为 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 的公开蓝图接口。所有操作均在编辑器面板内完成。

## C++ 用法

### 头文件引入

```cpp
#include "WaveformEditor.h"
#include "WaveformEditorModule.h"
```

### 基本用法：打开波形编辑器

通过 `FWaveformEditor` 类可以以编程方式打开一个音效资产的编辑器。这通常由内容浏览器扩展或资产操作触发。

```cpp
// 来源: Private/WaveformEditorInstantiator.h 和 Public/WaveformEditor.h
// 假设你已经有了一个 USoundWave* 指针
USoundWave* MySoundWave = ...; // 获取或加载你的音效资产

// 获取波形编辑器模块
FWaveformEditorModule& WaveformEditorModule = FModuleManager::GetModuleChecked<FWaveformEditorModule>(TEXT("WaveformEditor"));

// 创建一个编辑器实例
// 注意：通常不会直接创建 FWaveformEditor，而是通过模块提供的接口。
// 以下是一个概念性示例，展示了 Init 函数的核心用法。
TSharedRef<FWaveformEditor> Editor = MakeShared<FWaveformEditor>();
Editor->Init(EToolkitMode::Standalone, TSharedPtr<IToolkitHost>(), MySoundWave);
```

### 基本用法：分析音效响度

插件模块提供了一个静态工具函数，用于分析音效资产的 LUFS 和 SamplePeakDB 值。此功能也被用于编辑器内的响度显示。

```cpp
// 来源: Public/WaveformEditorModule.h 中的 WaveformAnalysis 命名空间
// 分析一个 USoundWave 的响度，并将结果（LUFS, SamplePeakDB）写回资产属性
bool bSuccess = WaveformAnalysis::AnalyzeSoundWaveLoudness(MySoundWave, /*bMarkDirty=*/ true);
if (bSuccess)
{
    UE_LOG(LogWaveformEditor, Log, TEXT("Successfully analyzed loudness for: %s"), *MySoundWave->GetName());
}
```

## Demo 示例

以下示例展示了如何在一个编辑器工具按钮或菜单项中，打开指定 `USoundWave` 资产的波形编辑器。

**MyAudioTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"

class USoundWave;
class FSpawnTabArgs;

class FMyAudioTool
{
public:
    static void OpenWaveformEditorForSoundWave(USoundWave* InSoundWave);
};
```

**MyAudioTool.cpp**
```cpp
#include "MyAudioTool.h"
#include "WaveformEditor.h" // 包含 FWaveformEditor
#include "WaveformEditorModule.h" // 包含模块接口
#include "Engine/AssetManager.h"

void FMyAudioTool::OpenWaveformEditorForSoundWave(USoundWave* InSoundWave)
{
    if (!InSoundWave)
    {
        UE_LOG(LogTemp, Error, TEXT("Cannot open Waveform Editor: Provided SoundWave is null."));
        return;
    }

    // 检查并加载波形编辑器模块
    if (FModuleManager::Get().IsModuleLoaded(TEXT("WaveformEditor")))
    {
        // 通常，编辑器实例的创建会通过 IWaveformEditorInstantiator 接口完成，
        // 该接口在模块启动时注册到内容浏览器和资产系统中。
        // 以下是直接操作编辑器的简化示例。
        FWaveformEditor* ExistingEditor = static_cast<FWaveformEditor*>(GEditor->GetEditorSubsystem<UAssetEditorSubsystem>()->FindEditorForAsset(InSoundWave, true));
        if (ExistingEditor)
        {
            ExistingEditor->BringToFront();
            return;
        }

        // 创建新的编辑器实例
        TSharedRef<FWaveformEditor> NewEditor = MakeShared<FWaveformEditor>();
        NewEditor->Init(EToolkitMode::Standalone, TSharedPtr<IToolkitHost>(), InSoundWave);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("WaveformEditor plugin is not loaded. Ensure it is enabled in the Plugins window."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 用于底层的音频渲染和播放控制。 |
| `AudioAnalysis` | 用于音效响度（LUFS）分析功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `40a5c76a` | [Waveform] Performance regression when dragging trimfade extents | 修复了拖拽修剪/淡入淡出区域时出现的性能下降问题。 |
| 2026-05-14 | `1f67ea84` | [Waveform editor] Remove no-op trimfade transform option | 移除了编辑器中一个实际上无效的修剪/淡入淡出变换选项。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量隐式转换为浮点数导致的编译器警告。 |
| 2026-04-28 | `d67c3aa3` | [Waveform editor] - Shift + space returns playhead to start, but playback does not start at beginnin | 修复了使用 Shift+空格 将播放头归位后，播放不会从头开始的错误。 |
| 2026-04-17 | `93be7d91` | [Waveform] Performance regression when dragging trimfade extents | 早期对拖拽修剪/淡入淡出区域性能问题的修复。 |

### 维护评价

该插件**处于活跃维护状态**。虽然创建于 2022 年（约 4 年前），且标记为实验性（`IsBetaVersion=true`，`EnabledByDefault=false`），但从 2026 年 4-5 月的连续提交记录可以看出，Epic 的开发团队仍在持续对其进行 bug 修复和性能优化。这是一个核心的音频内容创作工具，预计未来会继续完善。

**推荐使用**：对于需要在引擎内对音效资产进行可视化编辑和处理的项目，强烈建议启用此插件。尽管是实验性功能，但其功能完整且近期维护积极。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WaveformEditor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Content/Editor/WaveformEditor) (推测路径)