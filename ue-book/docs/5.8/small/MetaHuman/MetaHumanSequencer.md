# MetaHuman Sequencer

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画序列器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（序列器自定义轨道、通道、节） |
| 模块 | `MetaHumanSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHumanSequencer 模块为 MetaHuman 性能/动画系统在 UE Sequencer（序列器）中提供深度集成。它解决的核心问题是：MetaHuman 的面部动画流程需要在 Sequencer 中同步播放音频波形、视频素材，并支持按帧标记"排除帧"（excluded frames，即不可用/低质量的捕获数据区间），同时需要自定义的 bool 类型通道来标记每一帧的处理状态。

该模块通过自定义 `UMovieSceneSequence`、音频/媒体轨道编辑器、以及自定义的 `FMetaHumanMovieSceneChannel`（bool 通道），让 MetaHuman Performance 工作流可以完全在 Sequencer 中进行可视化编辑和回放。

## 使用场景

- 你在使用 MetaHuman Animator 捕获面部表演数据后，需要在 Sequencer 中预览音频和视频同步效果 → 此模块提供自定义音频/媒体轨道编辑器
- 你需要在 Sequencer 中查看和标记排除帧（低质量捕获区间），以告知面部动画求解器跳过这些帧 → `FMetaHumanMediaSection` 提供可视化绘制排除帧的功能
- 你需要通过 Sequencer 控制 MetaHuman 动画序列的绑定和回放上下文 → `UMetaHumanSceneSequence` 提供自定义序列管理
- 你需要在 Sequencer 中对每一帧添加或移除"是否参与处理"的 bool 标记 → `FMetaHumanMovieSceneChannel` 提供逐帧 bool 通道

## 蓝图用法

本模块主要面向编辑器内 Sequencer 的 C++ 扩展，公开的蓝图接口较少。以下是从源码中提取的关键可访问接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMetaHumanChannelRef` | 获取 MetaHuman bool 通道的引用 | `UMetaHumanMovieSceneMediaSection` |
| `OnKeyAddedEventDelegate` | 键被添加时的委托 | `UMetaHumanMovieSceneMediaSection` |
| `OnKeyDeletedEventDelegate` | 键被删除时的委托 | `UMetaHumanMovieSceneMediaSection` |
| `AddChannelToMovieSceneSection` | 将 MetaHuman 通道添加到媒体节 | `UMetaHumanMovieSceneMediaSection` |

### 使用示例（蓝图描述）

MetaHumanSequencer 主要在编辑器 Sequencer UI 中自动生效。当你在 MetaHuman Performance 面板中加载一段表演数据时，Sequencer 会自动创建对应的 `UMetaHumanSceneSequence`，其中包含：
1. 一个 `UMetaHumanMovieSceneMediaTrack` 用于播放视频素材
2. 一个 `UMetaHumanAudioTrack` 用于播放音频
3. 媒体节上叠加的排除帧可视化层

开发者通常不需要直接在蓝图中操作这些类，而是通过 MetaHuman Animator 的 UI 面板间接使用。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanSequence.h"
#include "MetaHumanMovieSceneChannel.h"
#include "MetaHumanMovieSceneMediaSection.h"
```

### 基本用法 — 自定义 bool 通道评估

`FMetaHumanMovieSceneChannel` 是一个存储 `bool` 值的 MovieScene 通道，用于标记每一帧是否被排除：

```cpp
// 来源: Public/MetaHumanMovieSceneChannel.h
FMetaHumanMovieSceneChannel MyChannel;

// 设置默认值（无键时使用）
MyChannel.SetDefault(true);

// 在指定时间评估通道
bool bValue = false;
FFrameTime FrameTime(100);  // 第 100 帧
bool bSuccess = MyChannel.Evaluate(FrameTime, bValue);

// 获取所有键的时间和值
TArrayView<const FFrameNumber> Times = MyChannel.GetTimes();
TArrayView<const bool> Values = MyChannel.GetValues();

// 检查是否有数据
if (MyChannel.HasAnyData())
{
    // 通道包含键或默认值
}
```

### 基本用法 — 媒体节中操作排除帧通道

```cpp
// 来源: Public/MetaHumanMovieSceneMediaSection.h
// 获取 MetaHuman 媒体节的通道引用
UMetaHumanMovieSceneMediaSection* MediaSection = /* 获取节的指针 */;
FMetaHumanMovieSceneChannel& Channel = MediaSection->GetMetaHumanChannelRef();

// 监听键添加/删除事件
MediaSection->OnKeyAddedEventDelegate().AddLambda([]() {
    UE_LOG(LogTemp, Log, TEXT("Key added to MetaHuman channel"));
});

MediaSection->OnKeyDeletedEventDelegate().AddLambda([]() {
    UE_LOG(LogTemp, Log, TEXT("Key removed from MetaHuman channel"));
});

// 手动将通道添加到节
MediaSection->AddChannelToMovieSceneSection();
```

### 进阶用法 — 自定义排除帧绘制

```cpp
// 来源: Public/MetaHumanMediaSection.h
// 在自定义 Sequencer Section 的 OnPaint 中绘制排除帧
int32 FMySection::OnPaintSection(FSequencerSectionPainter& InPainter) const
{
    int32 LayerId = FSequencerSection::OnPaintSection(InPainter);

    // 使用 MetaHuman 提供的辅助函数绘制排除帧
    LayerId = MetaHumanSectionPainterHelper::PaintExcludedFrames(
        InPainter,
        LayerId,
        Sequencer.Get(),
        Section
    );

    return LayerId;
}
```

### 进阶用法 — 自定义回放上下文

```cpp
// 来源: Public/MetaHumanSequencerPlaybackContext.h
FMetaHumanSequencerPlaybackContext PlaybackContext;
UObject* Context = PlaybackContext.GetPlaybackContext();
// 返回当前用于 Sequencer 回放的世界上下文
```

## Demo 示例

一个最小示例，展示如何读取 MetaHuman 通道数据：

```cpp
// MyMetaHumanSequenceHelper.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanSequence.h"
#include "MetaHumanMovieSceneMediaSection.h"

class FMyMetaHumanSequenceHelper
{
public:
    /** 检查指定帧是否在排除帧范围内 */
    static bool IsFrameExcluded(UMetaHumanMovieSceneMediaSection* InSection, FFrameNumber InFrame);

    /** 设置指定帧的排除状态 */
    static void SetFrameExcluded(UMetaHumanMovieSceneMediaSection* InSection, FFrameNumber InFrame, bool bExcluded);
};
```

```cpp
// MyMetaHumanSequenceHelper.cpp
#include "MyMetaHumanSequenceHelper.h"
#include "MetaHumanMovieSceneChannel.h"

bool FMyMetaHumanSequenceHelper::IsFrameExcluded(
    UMetaHumanMovieSceneMediaSection* InSection, FFrameNumber InFrame)
{
    if (!InSection)
    {
        return false;
    }

    FMetaHumanMovieSceneChannel& Channel = InSection->GetMetaHumanChannelRef();
    bool bValue = false;
    bool bEvaluated = Channel.Evaluate(InFrame, bValue);
    // false 表示该帧被排除
    return bEvaluated && !bValue;
}

void FMyMetaHumanSequenceHelper::SetFrameExcluded(
    UMetaHumanMovieSceneMediaSection* InSection, FFrameNumber InFrame, bool bExcluded)
{
    if (!InSection)
    {
        return;
    }

    FMetaHumanMovieSceneChannel& Channel = InSection->GetMetaHumanChannelRef();
    TMovieSceneChannelData<bool> Data = Channel.GetData();
    // bExcluded=false 表示排除，bExcluded=true 表示包含
    Data.UpdateOrAddKey(InFrame, !bExcluded);
}
```

## 模块依赖

基于模块内部依赖关系，使用 MetaHumanSequencer 时你的模块应依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanSequencer` | 本模块，提供 Sequencer 集成 |
| `MetaHumanPerformance` | MetaHuman 性能/表演数据资产 |
| `MetaHumanCore` | MetaHuman 核心工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

**活跃维护**：近期（2026 年 5 月）有密集的实质性更新，包括功能增强（身体追踪集成、动画导出）和 Bug 修复（渲染伪影、缓存问题）。作为 Epic Games 官方 MetaHuman 工具链的核心模块，预期会随 Unreal Engine 版本持续更新。

作为 MetaHuman Animator 的子模块，该模块与 MetaHuman 整体产品线深度绑定，不会被独立废弃。推荐在 MetaHuman 面部动画工作流中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/Animating-Characters/MetaHuman/)（MetaHuman 文档）