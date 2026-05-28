# MetaHuman Sequencer

> MetaHuman Sequencer integration module.

| 属性 | 值 |
|---|---|
| 中文名 | 定序器集成 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体轨道、音频轨道、自定义通道资产） |
| 模块 | `MetaHumanSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | - |
| 年龄标签 | - |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanSequencer) | |

## 用途

MetaHuman Sequencer 模块专门用于扩展 Unreal Engine 的 Sequencer（定序器），使其能够与 MetaHuman 性能数据无缝协作。它解决了在 Sequencer 时间线上编辑、预览和驱动 MetaHuman 数字人面部动画时的特殊需求。

该模块的核心是处理与排除帧（Excluded Frames，即面捕数据中未使用的视频帧）、媒体缓存和播放同步相关的问题。它提供了自定义的 Sequencer 轨道（Track）、通道（Channel）和节（Section），确保 MetaHuman 动画数据在 Sequencer 中能够正确、高效地进行非线性编辑和播放。

## 使用场景

- 你正在使用 MetaHuman Animator 从视频面捕数据制作数字人动画，并希望在 Sequencer 时间线上精确编辑和预览结果。
- 你需要处理包含排除帧（例如演员转身或面部被遮挡的片段）的媒体源，并在 Sequencer 中直观地看到这些区域。
- 你希望调整 MetaHuman 动画媒体轨道在 Sequencer 中的显示高度，以便更好地预览缩略图或波形。
- 你正在开发需要深度集成 Sequencer 的 MetaHuman 工作流工具。

## 蓝图用法

本模块主要提供的是 Sequencer 编辑器扩展，其核心类（如 `FMetaHumanMovieSceneChannel`、`UMetaHumanSceneSequence`）主要被 Sequencer 系统内部调用，通常不直接通过蓝图节点暴露给用户。用户通过 Sequencer 编辑器的图形界面与这些功能交互。

### 核心交互

| 功能 | 说明 |
|---|---|
| **自定义媒体轨道** | 在 Sequencer 中为 MetaHuman Performance 创建专属的媒体轨道，支持排除帧可视化。 |
| **自定义音频轨道** | 在 Sequencer 中为 MetaHuman Performance 创建专属的音频轨道。 |
| **媒体节高度调整** | 通过轨道编辑器 widget 调整媒体节的高度。 |
| **排除帧过滤/显示** | 自动识别并以特殊方式绘制媒体源中的排除帧区域。 |

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanSequence.h"
#include "MetaHumanMovieSceneChannel.h"
#include "MetaHumanMediaTrackEditor.h"
```

### 基本用法 (创建和使用自定义通道数据)

MetaHuman 动画数据通过 `FMetaHumanMovieSceneChannel` 进行存储和操作。

```cpp
// 来源: Public/MetaHumanMovieSceneChannel.h
// 创建一个自定义的布尔通道，用于表示某帧是否为排除帧
FMetaHumanMovieSceneChannel ExclusionChannel;

// 添加关键帧：第10帧为排除帧（true），第20帧为正常帧（false）
TMovieSceneChannelData<bool> ChannelData = ExclusionChannel.GetData();
ChannelData.AddKey(FFrameNumber(10), true);
ChannelData.AddKey(FFrameNumber(20), false);

// 评估通道在特定时间的值
bool bIsExcludedAtFrame15 = false;
ExclusionChannel.Evaluate(FFrameTime(15), bIsExcludedAtFrame15);
// bIsExcludedAtFrame15 可能为 true，因为10到20帧之间是保持上一个关键帧的值
```

### 进阶用法 (设置序列默认值与排除帧信息)

`UMetaHumanSceneSequence` 是 Sequencer 数据的核心容器。

```cpp
// 来源: Public/MetaHumanSequence.h
// 获取或创建一个 MetaHuman 场景序列
UMetaHumanSceneSequence* MySequence = NewObject<UMetaHumanSceneSequence>();

#if WITH_EDITOR
// 设置序列的默认 Tick Rate，通常关联到面捕素材数据
// UFootageCaptureData* FootageData = ...; // 获取你的面捕数据
// MySequence->SetTickRate(FootageData);

// 绑定一个委托，用于获取排除帧信息（用于UI绘制等）
MySequence->GetExcludedFrameInfo.BindLambda([](FFrameRate& OutSourceRate, FFrameRangeMap& OutExcludedFramesMap, int32& OutMediaStartFrame, TRange<FFrameNumber>& OutProcessingLimit)
{
    // 在这里填充排除帧信息，例如从你的资产中读取
    OutSourceRate = FFrameRate(24, 1);
    // ... 填充其他参数
});
#endif
```

## Demo 示例

以下是一个最小化的示例，演示如何注册一个自定义的 MetaHuman 媒体轨道编辑器（需要在 Editor 模块的 StartupModule 中调用）。

```cpp
// MetaHumanCustomTrackEditor.h
#pragma once
#include "ISequencerModule.h"

// 声明一个简单的自定义媒体轨道编辑器工厂
class FMyCustomMediaTrackEditorFactory : public ISequencerTrackEditorFactory
{
public:
    static void Register(ISequencerModule& SequencerModule)
    {
        // 注册我们的编辑器，使其支持 UMetaHumanMovieSceneMediaTrack 类型
        SequencerModule.RegisterPropertyTrackEditor(
            FOnCreateTrackEditor::CreateStatic(&FMyCustomMediaTrackEditorFactory::CreateTrackEditor),
            FOnGetTrackSupportedTypes::CreateStatic(&FMyCustomMediaTrackEditorFactory::GetSupportedTypes));
    }

    static TSharedRef<ISequencerTrackEditor> CreateTrackEditor(TSharedRef<ISequencer> InOwningSequencer)
    {
        // 复用标准的 MetaHuman 媒体轨道编辑器
        return FMetaHumanMediaTrackEditor::CreateTrackEditor(InOwningSequencer);
    }

    static TArray<TSubclassOf<UMovieSceneTrack>> GetSupportedTypes()
    {
        // 支持 MetaHuman 自定义的媒体轨道类
        return { UMetaHumanMovieSceneMediaTrack::StaticClass() };
    }
};

// MetaHumanCustomTrackEditor.cpp
#include "MetaHumanCustomTrackEditor.h"
// ... (实现，通常注册逻辑放在编辑器模块的 StartupModule)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 核心功能模块 |
| `MetaHumanPerformance` | 处理 MetaHuman 性能（动画）数据 |
| `MetaHumanCaptureDataEditor` | 处理面捕数据的编辑器功能 |
| `MediaAssets` | UE 媒体资产基础模块 |
| `SequencerCore` | Sequencer 核心功能模块 |
| `SequencerWidgets` | Sequencer UI 小部件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 禁用身体追踪时的关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

MetaHuman Sequencer 是 MetaHuman Animator 插件的核心组件之一，专门为 Sequencer 工作流设计。从 git 历史看，该模块持续收到功能更新和错误修复（最近一次更新在 2026 年 5 月），表明 Epic Games 正在积极维护和迭代该功能。

作为 MetaHuman 官方工具链的一部分，该模块与引擎版本紧密同步，可靠性较高。对于使用 MetaHuman Animator 并在 Sequencer 中进行动画编辑的项目，**强烈推荐使用此模块**。它是实现专业级 MetaHuman 动画非线性编辑的关键。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanSequencer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanSequencer) (可能包含内部测试，路径需确认)