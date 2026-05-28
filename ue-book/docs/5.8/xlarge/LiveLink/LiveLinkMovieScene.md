# Live Link Movie Scene

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接场景录制 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link Movie Scene 是 Live Link 插件的 Sequencer 集成模块，解决了**将实时流式动画数据录制为 Sequencer 关键帧**的问题。

Live Link 本身负责从外部设备（如动捕系统、Maya、MotionBuilder 等）实时接收动画数据。而 LiveLinkMovieScene 模块的核心职责是：

1. **录制（Recording）**：将 Live Link 实时数据流捕获并写入 Sequencer 轨道的关键帧通道
2. **回放（Playback）**：从 Sequencer 轨道读取录制好的关键帧数据，重新注入 Live Link 管线播放
3. **属性绑定（Property Binding）**：通过反射系统将 Live Link 帧数据中的属性映射到 Sequencer 的浮点/整数/布尔/枚举通道

简而言之：这个模块是**动捕录制 → Sequencer 编辑**的桥梁。

## 使用场景

- 你正在用 Live Link 从动捕设备实时接收角色动画 → 需要在 Sequencer 中录制这些动画以供后期编辑
- 你从 Maya/Blender 通过 Live Link 实时预览动画 → 希望将预览动画"烘焙"为 Sequencer 关键帧
- 你需要在 Sequencer 中回放之前通过 Live Link 录制的数据 → LiveLinkMovieScene 提供回放源
- 你正在使用 Virtual Production 工作流 → 需要将实时数据记录到 Timeline 中

## 蓝图用法

LiveLinkMovieScene 模块主要是 C++ / Sequencer 内部使用的模块，公开的蓝图 API 较少。核心交互通过 Sequencer 编辑器 UI 完成。

### 核心类

| 类 | 说明 |
|---|---|
| `UMovieSceneLiveLinkTrack` | Sequencer 中的 Live Link 轨道，存储录制的角色和属性数据 |
| `UMovieSceneLiveLinkSection` | 轨道中的一个片段，对应一个 Live Link 主题的一段时间数据 |
| `UMovieSceneLiveLinkSubSection` | 片段的子节，管理特定类型数据（动画/属性/基本角色） |
| `FLiveLinkStructPropertyBindings` | 反射属性绑定工具，通过属性路径访问 UStruct 中的属性值 |

### Sequencer 工作流

Live Link 数据在 Sequencer 中的组织结构：

```
UMovieSceneLiveLinkTrack（轨道）
  └─ UMovieSceneLiveLinkSection（片段，时间范围）
       ├─ UMovieSceneLiveLinkSubSectionAnimation（动画帧 - Transform 数组）
       ├─ UMovieSceneLiveLinkSubSectionProperties（通用属性）
       └─ UMovieSceneLiveLinkSubSectionBasicRole（基本角色属性）
```

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneLiveLinkTrack.h"
#include "MovieSceneLiveLinkSection.h"
#include "MovieSceneLiveLinkStructPropertyBindings.h"
```

### 基本用法 — 属性绑定

通过 `FLiveLinkStructPropertyBindings` 访问 Live Link 帧数据中的属性值。

```cpp
// 绑定到 Live Link 帧数据中的一个属性
FString PropertyPath = TEXT("MyPropertyName");
FLiveLinkStructPropertyBindings Binding(FName(*PropertyPath), PropertyPath);

// 缓存绑定到具体的 UScriptStruct
Binding.CacheBinding(MyFrameDataStruct);

// 获取属性值（浮点类型）
float Value = Binding.GetCurrentValueAt<float>(0, MyFrameDataStruct, FrameDataPtr);

// 设置属性值
Binding.SetCurrentValueAt<float>(0, MyFrameDataStruct, FrameDataPtr, NewValue);
```

### 基本用法 — 创建 Live Link 轨道

```cpp
// 获取 Sequencer 中的 Live Link 轨道类
TSubclassOf<ULiveLinkRole> TrackRole = ULiveLinkAnimationRole::StaticClass();

// UMovieSceneLiveLinkTrack 通过 Sequencer API 创建
UMovieSceneLiveLinkTrack* LiveLinkTrack = /* 通过 Sequencer API 获取 */;
LiveLinkTrack->SetTrackRole(TrackRole);
```

### 进阶用法 — 录制 Live Link 帧到通道

```cpp
// 录制一帧 Live Link 数据到 Section
UMovieSceneLiveLinkSection* Section = /* 获取或创建 Section */;
FFrameNumber FrameNumber(30); // 当前帧
FLiveLinkFrameDataStruct FrameData; // 从 Live Link 获取的帧数据

// 初始化 Section
FLiveLinkSubjectPreset Preset;
Section->Initialize(Preset, StaticData);

// 录制帧
Section->RecordFrame(FrameNumber, FrameData);

// 完成录制时优化关键帧
FKeyDataOptimizationParams OptParams;
Section->FinalizeSection(true, OptParams);
```

### 进阶用法 — Transform 键值缓冲

`FLiveLinkTransformKeys` 用于增量录制动画变换数据：

```cpp
FLiveLinkTransformKeys TransformKeys;

// 逐帧添加变换
FTransform BoneTransform = /* 当前骨骼变换 */;
FFrameNumber FrameTime(60);
TransformKeys.Add(BoneTransform, FrameTime);

// 录制完成后，将缓冲数据追加到 Float 通道并重置缓冲区
TArray<FMovieSceneFloatChannel> FloatChannels; // 9 个通道（XYZ 位移/旋转/缩放）
TransformKeys.AppendToFloatChannelsAndReset(0, FloatChannels);
```

## Demo 示例

以下示例展示如何通过 C++ 创建一个 Live Link 回放源，将 Sequencer 中录制的数据重新注入 Live Link 管线：

```cpp
// MyLiveLinkPlaybackActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MovieSceneLiveLinkSource.h"
#include "MyLiveLinkPlaybackActor.generated.h"

UCLASS()
class AMyLiveLinkPlaybackActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLiveLinkPlaybackActor();

    /** 开始回放 Sequencer 中的 Live Link 数据 */
    UFUNCTION(BlueprintCallable, Category = "LiveLink|Playback")
    void StartPlayback(const FLiveLinkSubjectPreset& InPreset);

    /** 停止回放 */
    UFUNCTION(BlueprintCallable, Category = "LiveLink|Playback")
    void StopPlayback();

    /** 发布一帧数据到 Live Link */
    void PublishFrameData(FLiveLinkFrameDataStruct& InFrameData);

private:
    TSharedPtr<FMovieSceneLiveLinkSource> LiveLinkSource;
};
```

```cpp
// MyLiveLinkPlaybackActor.cpp
#include "MyLiveLinkPlaybackActor.h"
#include "MovieSceneLiveLinkSource.h"

AMyLiveLinkPlaybackActor::AMyLiveLinkPlaybackActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyLiveLinkPlaybackActor::StartPlayback(const FLiveLinkSubjectPreset& InPreset)
{
    // 创建一个 MovieScene LiveLink 源
    LiveLinkSource = FMovieSceneLiveLinkSource::CreateLiveLinkSource(InPreset);

    if (LiveLinkSource.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Live Link playback source created for subject: %s"),
            *InPreset.Key.SubjectName.ToString());
    }
}

void AMyLiveLinkPlaybackActor::StopPlayback()
{
    if (LiveLinkSource.IsValid())
    {
        FMovieSceneLiveLinkSource::RemoveLiveLinkSource(LiveLinkSource);
        LiveLinkSource.Reset();
    }
}

void AMyLiveLinkPlaybackActor::PublishFrameData(FLiveLinkFrameDataStruct& InFrameData)
{
    if (LiveLinkSource.IsValid() && LiveLinkSource->Client)
    {
        TArray<FLiveLinkFrameDataStruct> FrameDataArray;
        FrameDataArray.Add(MoveTemp(InFrameData));
        LiveLinkSource->PublishLiveLinkFrameData(FrameDataArray);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心运行时，提供 `ILiveLinkClient`、`ILiveLinkSource` 等接口 |
| `LiveLinkInterface` | Live Link 接口定义（角色、帧数据、静态数据结构） |
| `MovieScene` | Sequencer 核心模块，提供轨道、通道、求值模板等基础设施 |
| `MovieSceneTracks` | Sequencer 标准轨道实现 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播组件在子系统未就绪时的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的截断警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复 Python 触发属性变更时 MemberProperty 为空导致的崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | VP 资产分类调整和迁移 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中可能导致的乱码输出 |

### 维护评价

LiveLinkMovieScene 是 Live Link 生态系统中关键的 Sequencer 集成模块，创建于 2018 年（约 8 年历史）。从最近的提交记录来看，该插件仍在**活跃维护**中——最近的更新集中在崩溃修复和代码质量改进上。

**优势**：
- 作为 Epic Games 官方维护的核心动画工具链组件，与 Unreal Engine 版本同步更新
- 是 Virtual Production 工作流中动捕录制的关键基础设施
- 支持多种 Live Link 角色类型（动画、变换、属性）

**注意事项**：
- `EnabledByDefault: false`，需要在项目设置中手动启用
- 依赖 Live Link 核心模块，需要理解 Live Link 的源/主题/角色概念
- 部分 API（如 `GetCurrentValue`、`SetCurrentValue`）已在 4.24 中标记为废弃，应使用带 `At` 后缀的索引版本

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)