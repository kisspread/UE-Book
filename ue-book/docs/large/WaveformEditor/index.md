# Waveform Editor

> Editor tool for waveforms（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WaveformEditor` (Editor), `WaveformEditorWidgets` (Editor), `WaveformTransformations` (Editor), `WaveformTransformationsWidgets` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/WaveformEditor) | |

## 用途

Waveform Editor 是一个内置于 UE5 编辑器中的音频波形可视化编辑工具。它允许音频设计师直接在编辑器中查看、裁剪、淡入淡出、归一化和标记 USoundWave 资产，无需借助外部音频编辑软件。

核心价值在于将音频编辑工作流集成到引擎内部：你可以在编辑器中直接调整音频的起止点、添加循环标记、应用音源效果链，并将变换后的结果导出为新资产。所有变换操作都以非破坏性方式附加在 USoundWave 上，支持撤销/重做。

## 使用场景

- **裁剪音频素材**：你导入了一段 10 秒的环境音效，只需要中间 3 秒 → 在波形编辑器中拖拽裁剪手柄，设置淡入淡出
- **设置循环区域**：你需要一段无缝循环的背景音乐 → 在波形上创建标记，设置循环区域并预览
- **归一化响度**：多个音频素材响度不一致 → 添加 Normalize 变换，设置目标 LUFS
- **应用音效**：需要给音效添加混响/延迟等效果 → 添加 EffectChain 变换，挂载 Source Effect Preset
- **批量处理**：通过 DeveloperSettings 配置默认变换链，新打开的音频自动获得预设变换

## 蓝图用法

Waveform Editor 是纯编辑器工具，不暴露 BlueprintCallable 接口。所有操作通过编辑器 UI 完成。

## C++ 用法

### 头文件引入

```cpp
#include "WaveformEditorModule.h"           // FWaveformEditorModule
#include "WaveformEditor.h"                 // FWaveformEditor (主编辑器类)
#include "WaveformTransformationsModule.h"  // FWaveformTransformationsModule
```

### 打开波形编辑器

通过编辑器的资产编辑器框架打开：

```cpp
// FWaveformEditor 通过 FAssetEditorToolkit 框架管理
// 通常由内容浏览器右键菜单或双击触发
// 示例（在 WaveformEditorInstantiator 中）：
TSharedPtr<FWaveformEditor> Editor = MakeShared<FWaveformEditor>();
Editor->Init(EToolkitMode::Standalone, ToolkitHost, SoundWave);
```

### 注册自定义变换渲染器

如果你实现了自定义的 `UWaveformTransformationBase`，可以为其注册渲染器：

```cpp
// Source/WaveformTransformationsWidgets
#include "WaveformTransformationRendererMapper.h"

// 在模块 StartupModule() 中注册
FWaveformTransformationRendererMapper::Get()
    .RegisterRenderer<FMyCustomRenderer>(UMyCustomTransformation::StaticClass());
```

### 使用音频分析函数

```cpp
#include "WaveformAudioAnalysisFunctions.h"

// 计算 LUFS 响度
float LUFS = WaveformAudioAnalysis::GetLUFS(AudioBuffer, SampleRate, NumChannels);

// 获取峰值
float Peak = WaveformAudioAnalysis::GetPeakSampleValue(AudioBuffer);

// 获取 RMS
float RMS = WaveformAudioAnalysis::GetRMSPeak(AudioBuffer, SampleRate, NumChannels);
```

## 模块架构

```
┌─────────────────────────────────────────────────────┐
│  WaveformEditor (核心编辑器)                          │
│  FWaveformEditor, TransportController, Commands      │
├──────────────┬──────────────────────────────────────┤
│              │                                       │
│  WaveformEditorWidgets    WaveformTransformations    │
│  (UI 组件层)                (变换算法层)               │
│  STransformedWaveformViewPanel                      │
│  ZoomController, GridData    TrimFade, Normalize     │
│  SequenceDataProvider        Markers, EffectChain    │
│              │               AudioAnalysis           │
│              │                                       │
├──────────────┴──────────────────────────────────────┤
│  WaveformTransformationsWidgets (变换渲染层)          │
│  IWaveformTransformationRenderer                    │
│  TrimFadeRenderer, MarkerRenderer                   │
│  RendererMapper, RendererBase                       │
└─────────────────────────────────────────────────────┘
```

### 子模块文档

| 模块 | 说明 | 文档 |
|---|---|---|
| WaveformEditor | 核心编辑器框架、工具栏、播放控制 | [WaveformEditor.md](WaveformEditor.md) |
| WaveformEditorWidgets | 波形显示 UI 组件、缩放、网格 | [WaveformEditorWidgets.md](WaveformEditorWidgets.md) |
| WaveformTransformations | TrimFade/Normalize/Markers/EffectChain 变换 | [WaveformTransformations.md](WaveformTransformations.md) |
| WaveformTransformationsWidgets | 变换的可视化渲染器和交互系统 | [WaveformTransformationsWidgets.md](WaveformTransformationsWidgets.md) |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioExtensions` | 音频扩展接口（IWaveTransformation） |
| `AudioSynesthesiaCore` | 音频分析核心 |
| `AudioWidgets` | 音频 Slate 控件 |
| `SignalProcessing` | 信号处理（DSP） |
| `UnrealEd` | 编辑器框架（FAssetEditorToolkit） |
| `ToolMenus` | 工具菜单系统 |
| `Slate` / `SlateCore` | UI 框架 |
| `PropertyEditor` | 属性面板自定义 |
| `AssetDefinition` | 资产定义注册 |
| `AudioEditor` | 音频编辑器集成 |
| `EditorScriptingUtilities` | 编辑器脚本工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-17 | `e8ade2e` | [Mac only] Editor Crashes when exporting a Sound Wave | 平台特定 bug 修复：macOS 导出崩溃 |
| 2025-10-03 | `72872c9` | Playhead stutters when adjusting Trim values; Redoing Start Time adjustment; Transport state consistency | 播放头抖动修复、撤销重做修复、传输状态一致性改进 |
| 2025-10-01 | `dc046a7` | Editor crashes when Trim Fade goes across a Cue Point | 裁剪淡出跨越标记点时崩溃修复 |

### 维护评价

- **活跃维护** ✅ — 2025 年 10 月仍有持续的功能修复和 bug 修复
- **标记为 Beta** — `IsBetaVersion=true`，`EnabledByDefault=false`，需要手动启用
- 5.7 版本中大量 API 标记为 `UE_DEPRECATED(5.7, ...)`，说明正在经历 API 重构（PropertyHandles 废弃，转向直接 UObject 访问）
- 创建于 2022 年，约 4 年历史，仍属于较新的插件
- 近期更新集中在稳定性和用户体验修复（崩溃、播放头抖动、撤销重做）
- **推荐使用**：对于需要在编辑器内进行音频裁剪和标记的项目，该插件功能完整且持续维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/WaveformEditor)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 依赖插件：[AudioSynesthesia](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioSynesthesia)、[AudioWidgets](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioWidgets)、[EditorScriptingUtilities](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/EditorScriptingUtilities)
