# MetaHuman Sequencer

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 序列器 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `MetaHumanSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHumanSequencer 模块为 MetaHuman 动画系统提供 **Sequencer 集成**，解决了 MetaHuman Performance 数据在 Sequencer 时间线中的播放、编辑和预览问题。

具体功能包括：

- **自定义媒体轨道**：扩展标准 `UMovieSceneMediaTrack`，为 MetaHuman 面部动画提供专用的媒体轨道，支持排除帧可视化和轨道高度自定义
- **自定义音频轨道**：扩展标准 `UMovieSceneAudioTrack`，为 MetaHuman 口型同步数据提供专用音频轨道
- **布尔值通道**（`FMetaHumanMovieSceneChannel`）：提供一个自定义的 `FMovieSceneChannel<bool>`，用于控制 MetaHuman 动画中的状态切换（如是否启用面部追踪、是否导出等）
- **排除帧管理**：通过 `FGetExcludedFrameInfo` 委托管理不需要处理的帧范围，在 Sequencer UI 中以可视化方式展示
- **播放上下文管理**：提供 Sequencer 播放时的世界上下文管理

## 使用场景

- 你使用 MetaHuman Animator 捕获了面部表演数据 → 在 Sequencer 中预览和编辑 Performance
- 你需要在 Sequencer 中同步预览视频素材和 MetaHuman 面部动画 → 使用自定义媒体轨道
- 你需要在时间线上标记哪些帧需要排除或跳过 → 使用排除帧可视化功能
- 你需要批量导出 MetaHuman 动画到 Sequencer → 配合 MetaHumanBatchProcessor 使用

## 蓝图用法

本模块主要提供编辑器侧的 Sequencer 扩展，蓝图可用的节点较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMetaHumanChannelRef` | 获取 MetaHuman 布尔通道引用 | `UMetaHumanMovieSceneMediaSection` |
| `AddChannelToMovieSceneSection` | 向媒体段添加 MetaHuman 通道 | `UMetaHumanMovieSceneMediaSection` |
| `GetRowHeight` / `SetRowHeight` | 获取/设置轨道行高 | `UMetaHumanMovieSceneMediaTrack` |

### 使用示例（蓝图描述）

本模块的 Sequencer 集成主要通过编辑器 UI 自动完成，无需手动创建蓝图。当使用 MetaHuman Animator 导入 Performance 数据时，系统会自动：

1. 创建 `UMetaHumanSceneSequence` 序列
2. 添加 `UMetaHumanMovieSceneMediaTrack` 媒体轨道（含排除帧高亮）
3. 添加 `UMetaHumanAudioTrack` 音频轨道
4. 在各段（Section）中设置对应的媒体源和布尔通道

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanSequence.h"
#include "MetaHumanMovieSceneMediaTrack.h"
#include "MetaHumanMovieSceneMediaSection.h"
#include "MetaHumanMovieSceneChannel.h"
```

### 基本用法：创建 MetaHuman 场景序列

```cpp
// 创建一个 MetaHuman 专用的场景序列
UMetaHumanSceneSequence* Sequence = NewObject<UMetaHumanSceneSequence>();
UMovieScene* MovieScene = Sequence->GetMovieScene();

// 设置排除帧信息回调
#if WITH_EDITOR
Sequence->GetExcludedFrameInfo.BindLambda(
    [](FFrameRate& OutSourceRate, FFrameRangeMap& OutExcludedFramesMap,
       int32& OutMediaStartFrame, TRange<FFrameNumber>& OutProcessingLimit)
    {
        // 设置源帧率
        OutSourceRate = FFrameRate(30, 1);
        // 设置排除帧范围
        OutMediaStartFrame = 0;
        OutProcessingLimit = TRange<FFrameNumber>(0, 300);
    });
#endif
```

### 基本用法：操作布尔通道

```cpp
// 创建 MetaHuman 布尔通道并添加关键帧
FMetaHumanMovieSceneChannel Channel;

// 设置默认值
Channel.SetDefault(false);

// 添加关键帧
TMovieSceneChannelData<bool> Data = Channel.GetData();
FFrameNumber KeyTime(100);  // 第 100 帧
FKeyHandle Handle = Data.AddKey(KeyTime, true);

// 查询
bool bValue = false;
bool bSuccess = Channel.Evaluate(FFrameNumber(100), bValue);
// bSuccess == true, bValue == true
```

### 进阶用法：自定义媒体段与排除帧

```cpp
// 获取媒体段的排除帧信息并进行可视化绘制
// 来源: MetaHumanMediaSection.h - MetaHumanSectionPainterHelper::PaintExcludedFrames

void MyCustomPaint(FSequencerSectionPainter& InPainter, int32 InLayerId,
                   ISequencer* InSequencer, UMovieSceneSection* InSection)
{
    // 使用内置辅助函数绘制排除帧区域
    int32 NewLayerId = MetaHumanSectionPainterHelper::PaintExcludedFrames(
        InPainter, InLayerId, InSequencer, InSection);
}
```

### 进阶用法：监听通道关键帧变化

```cpp
// 来源: MetaHumanMovieSceneMediaSection.h
UMetaHumanMovieSceneMediaSection* MediaSection = /* 获取或创建 */;

// 监听关键帧添加事件
MediaSection->OnKeyAddedEventDelegate().AddLambda(
    [](const UMovieSceneSection* Section, FKeyHandle KeyHandle)
    {
        // 处理新关键帧被添加的逻辑
    });

// 监听关键帧删除事件
MediaSection->OnKeyDeletedEventDelegate().AddLambda(
    [](const UMovieSceneSection* Section, FKeyHandle KeyHandle)
    {
        // 处理关键帧被删除的逻辑
    });
```

## Demo 示例

### 最小示例：创建 MetaHuman 序列并设置媒体轨道

```cpp
// MetaHumanSequenceDemo.h
#pragma once

#include "CoreMinimal.h"

class FMetaHumanSequenceDemo
{
public:
    /** 创建一个包含媒体轨道的 MetaHuman 序列 */
    static UMetaHumanSceneSequence* CreateDemoSequence(UObject* Outer);

    /** 向序列中添加带排除帧信息的媒体段 */
    static UMetaHumanMovieSceneMediaSection* AddMediaSectionWithExclusions(
        UMetaHumanSceneSequence* Sequence,
        UMediaSource* MediaSource);
};
```

```cpp
// MetaHumanSequenceDemo.cpp
#include "MetaHumanSequenceDemo.h"
#include "MetaHumanSequence.h"
#include "MetaHumanMovieSceneMediaTrack.h"
#include "MetaHumanMovieSceneMediaSection.h"
#include "MetaHumanMovieSceneChannel.h"
#include "MovieScene.h"

UMetaHumanSceneSequence* FMetaHumanSequenceDemo::CreateDemoSequence(UObject* Outer)
{
    // 创建 MetaHuman 场景序列
    UMetaHumanSceneSequence* Sequence = NewObject<UMetaHumanSceneSequence>(Outer);
    UMovieScene* MovieScene = Sequence->GetMovieScene();

    // 设置播放范围（30fps，共 5 秒 = 150 帧）
    MovieScene->SetPlaybackRangeLocked(false);
    MovieScene->SetPlaybackRange(TRange<FFrameNumber>(0, 150));
    MovieScene->SetDisplayRate(FFrameRate(30, 1));

    return Sequence;
}

UMetaHumanMovieSceneMediaSection* FMetaHumanSequenceDemo::AddMediaSectionWithExclusions(
    UMetaHumanSceneSequence* Sequence,
    UMediaSource* MediaSource)
{
    UMovieScene* MovieScene = Sequence->GetMovieScene();

    // 创建自定义媒体轨道
    UMetaHumanMovieSceneMediaTrack* MediaTrack = NewObject<UMetaHumanMovieSceneMediaTrack>(
        MovieScene, NAME_None, RF_Transient);
    MediaTrack->SetRowHeight(50);
    MovieScene->AddTrack(MediaTrack);

    // 添加媒体段
    UMetaHumanMovieSceneMediaSection* Section = Cast<UMetaHumanMovieSceneMediaSection>(
        MediaTrack->AddNewMediaSourceOnRow(*MediaSource, 0, 0));

    // 添加 MetaHuman 布尔通道
    Section->AddChannelToMovieSceneSection();

    // 配置通道：标记某些帧为排除状态
    FMetaHumanMovieSceneChannel& Channel = Section->GetMetaHumanChannelRef();
    Channel.SetDefault(false);  // 默认不排除

    TMovieSceneChannelData<bool> Data = Channel.GetData();
    // 将第 10-20 帧标记为排除
    Data.AddKey(FFrameNumber(10), true);
    Data.AddKey(FFrameNumber(20), false);

    return Section;
}
```

## 模块依赖

从源码分析，本模块的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 核心功能 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器支持 |
| `Sequencer` | Sequencer 编辑器集成 |
| `MovieScene` | 自定义 MovieScene 通道和轨道 |
| `MediaAssets` | 媒体源和媒体纹理支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持对已有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

- **活跃维护**：最近一周内有多次实质性更新（5 次提交），涵盖功能增强和 Bug 修复
- **功能成熟度**：模块结构稳定，提供了完整的 Sequencer 集成方案（自定义轨道、通道、编辑器扩展）
- **依赖关系**：作为 MetaHuman Animator 的子模块，随主插件一起维护
- **推荐程度**：✅ 推荐使用。这是 Epic 官方维护的 MetaHuman 工具链核心组件，更新频繁且持续改进中
- **注意事项**：本模块为 Runtime 类型但大量使用 `#if WITH_EDITOR`，实际使用主要集中在编辑器环境；安装后默认不启用（`Installed: false`），需要在插件设置中手动启用 MetaHuman Animator

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator/)（MetaHuman Animator 官方文档）