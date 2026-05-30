# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 中文名 | 镜头录制器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderEditor` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime), `TakesCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Take Recorder 并非一个简单的数据录制工具，而是一个完整的“镜头”管理管线。它解决了在虚拟制作环境中，如何系统化地设置、录制、审查和回放“镜头”的问题。核心价值在于将实时性能捕获（动画、物理、音频等）数据流记录到 Level Sequence 中，从而为电影、电视和广告制作提供可重复、可管理的拍摄流程。它允许用户配置“拍摄源”（例如：特定的Actor、物理模拟、音频设备），定义“拍摄板”（Slate）和“镜头号”（Take Number），并在录制后将结果保存为带有丰富元数据（如时间码、时长、描述）的 Level Sequence 资产，便于后期审查和挑选。

## 使用场景

-   **虚拟制片片场**：导演需要在虚拟场景中实时预览CGI与真实演员的互动，并录制多条“镜头”供后期选择，每条镜头都自动记录精确的时间码和元数据。
-   **游戏开发与过场动画**：需要录制一段复杂的物理模拟或角色表演动画作为过场动画的基底，使用 Take Recorder 可以确保录制的帧率和时间线准确，并方便地管理不同版本。
-   **建筑可视化与产品展示**：需要录制一段精心设计的相机漫游动画，并希望为客户提供多个不同角度或速度的版本，通过 Take Recorder 可以快速创建和归档这些“镜头”。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Compute Next Take Number` | 根据指定的 Slate 名称计算下一个可用的镜头编号 | `UTakesCoreBlueprintLibrary` |
| `Find Takes` | 查找所有已录制的、匹配指定 Slate 和（可选）镜头号的资产 | `UTakesCoreBlueprintLibrary` |
| `Set On Take Recorder Slate Changed` | 绑定一个委托，当拍摄板（Slate）名称变更时触发 | `UTakesCoreBlueprintLibrary` |
| `Set On Take Recorder Take Number Changed` | 绑定一个委托，当镜头号（Take Number）变更时触发 | `UTakesCoreBlueprintLibrary` |
| `Is Locked` | 查询当前镜头的元数据是否被锁定（只读） | `UTakeMetaData` |
| `Get Slate` | 获取当前镜头的拍摄板名称 | `UTakeMetaData` |
| `Get Take Number` | 获取当前镜头的编号 | `UTakeMetaData` |
| `Get Timestamp` | 获取当前镜头开始录制的时间戳 | `UTakeMetaData` |
| `Get Timecode In` | 获取录制开始时的 Timecode | `UTakeMetaData` |
| `Get Timecode Out` | 获取录制结束时的 Timecode | `UTakeMetaData` |
| `Set Slate` | 设置当前镜头的拍摄板名称（会自动将镜头号重置为1） | `UTakeMetaData` |
| `Set Take Number` | 设置当前镜头的编号（自动限制为 >= 1） | `UTakeMetaData` |
| `Add Source` | 向镜头源列表（`UTakeRecorderSources`）中添加一个指定类型的录制源 | `UTakeRecorderSources` |
| `Remove Source` | 从镜头源列表中移除一个录制源 | `UTakeRecorderSources` |
| `Get Sources (Copy)` | 获取当前镜头源列表的一个副本（用于蓝图） | `UTakeRecorderSources` |

### 使用示例（蓝图描述）

1.  **准备录制**：在蓝图中，首先获取 `UTakeMetaData` 对象（通常来自 `ULevelSequence` 的元数据）。调用 `Set Slate` 设置当前拍摄板名称，例如 “Shot01”。调用 `Set Take Number` 设置或检查镜头编号。
2.  **配置源**：获取 `UTakeRecorderSources` 对象。使用 `Add Source` 节点，选择 `UTakeRecorderSource` 的子类（如 `UTakeRecorderActorSource`）来添加需要录制的Actor。可以多次调用以添加多个源。
3.  **启动录制**：通常这部分逻辑由 `UTakeRecorder` 或相关UI触发。但在蓝图中，你可以配置好所有源和元数据后，通过相应接口启动录制。
4.  **监听变化**：使用 `Set On Take Recorder Slate Changed` 绑定一个自定义事件，以便在运行时Slate名称改变时更新UI或执行其他逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "TakesCore/Public/TakesUtils.h"
#include "TakesCore/Public/TakeRecorderSource.h"
#include "TakesCore/Public/TakeRecorderSources.h"
#include "TakesCore/Public/TakeMetaData.h"
```

### 基本用法

以下示例展示了如何通过C++配置一个镜头的元数据并管理其录制源。

```cpp
// 来源: 测试用例与公共API推断
// 假设我们已经有一个 ULevelSequence* MySequence

// 1. 获取或创建镜头元数据
UTakeMetaData* TakeMetaData = MySequence->FindOrAddMetaData<UTakeMetaData>();
if (TakeMetaData)
{
    // 设置拍摄板和镜头号
    TakeMetaData->SetSlate(TEXT(“CharacterCloseUp”));
    TakeMetaData->SetTakeNumber(1); // 设置为第1条

    // 设置描述
    TakeMetaData->SetDescription(TEXT(“主角正面特写，情绪激动”));

    // 可选：锁定元数据防止误修改
    // TakeMetaData->Lock();
}

// 2. 获取或创建镜头源列表
UTakeRecorderSources* Sources = nullptr;
ITakeRecorderSourcesManager& SourcesManager = ITakeRecorderSourcesManager::GetChecked();
Sources = SourcesManager.FindOrAddSources(MySequence);
if (Sources)
{
    // 清除现有源（如果需要）
    TArray<UTakeRecorderSource*> ExistingSources = Sources->GetSourcesCopy();
    for (UTakeRecorderSource* Src : ExistingSources)
    {
        Sources->RemoveSource(Src);
    }

    // 添加一个新的 Actor 录制源
    if (UClass* ActorSourceClass = UTakeRecorderSource::FindSourceClass(“TakeRecorderActorSource”))
    {
        UTakeRecorderSource* NewSource = Sources->AddSource(ActorSourceClass);
        // 配置新源... (具体配置取决于源类型)
    }
}
```

### 进阶用法：实现自定义录制源

创建一个自定义的录制源来录制特定的游戏数据。

```cpp
// MyCustomTakeRecorderSource.h
#pragma once
#include "TakeRecorderSource.h"
#include "MyCustomTakeRecorderSource.generated.h"

UCLASS(BlueprintType, Blueprintable, EditInlineNew, meta=(DisplayName=“My Custom Data Source”))
class MYGAME_API UMyCustomTakeRecorderSource : public UTakeRecorderSource
{
    GENERATED_BODY()

public:
    virtual bool IsValid() const override;
    virtual void StartRecording(const FTimecode& InSectionStartTimecode, const FFrameNumber& InSectionFirstFrame, ULevelSequence* InSequence) override;
    virtual void TickRecording(const FQualifiedFrameTime& CurrentSequenceTime) override;
    virtual void StopRecording(ULevelSequence* InSequence) override;
    virtual TArray<UTakeRecorderSource*> PostRecording(ULevelSequence* InSequence, ULevelSequence* InRootSequence, const bool bCancelled) override;

    // 覆盖UI显示文本
    virtual FText GetDisplayTextImpl() const override { return NSLOCTEXT(“MyTakeSources”, “CustomSource”, “My Custom Data”); }
    virtual FText GetDescriptionTextImpl() const override { return NSLOCTEXT(“MyTakeSources”, “CustomSourceDesc”, “Records custom game metrics.”); }
    virtual const FSlateBrush* GetDisplayIconImpl() const override { return FAppStyle::GetBrush(“Icons.Info”); }
};

// MyCustomTakeRecorderSource.cpp
#include “MyCustomTakeRecorderSource.h”
#include “LevelSequence.h”

bool UMyCustomTakeRecorderSource::IsValid() const
{
    // 检查录制前置条件，例如世界是否就绪
    return GetWorld() != nullptr;
}

void UMyCustomTakeRecorderSource::StartRecording(const FTimecode& InSectionStartTimecode, const FFrameNumber& InSectionFirstFrame, ULevelSequence* InSequence)
{
    // 初始化录制状态，例如重置数据缓冲区
}

void UMyCustomTakeRecorderSource::TickRecording(const FQualifiedFrameTime& CurrentSequenceTime)
{
    // 在每帧录制时收集自定义数据，例如玩家分数、状态机状态等
    // 可以使用 CurrentSequenceTime 将数据与精确帧对齐
}

void UMyCustomTakeRecorderSource::StopRecording(ULevelSequence* InSequence)
{
    // 结束录制，可能将收集到的数据写入 InSequence 的轨道中
}

TArray<UTakeRecorderSource*> UMyCustomTakeRecorderSource::PostRecording(ULevelSequence* InSequence, ULevelSequence* InRootSequence, const bool bCancelled)
{
    // 清理工作，返回空数组表示无需移除临时源
    return TArray<UTakeRecorderSource*>();
}
```

## Demo 示例

以下示例展示了如何在代码中创建并初始化一个简单的自定义录制源。

```cpp
// MySimpleCounterRecorderSource.h
#pragma once
#include "TakeRecorderSource.h"
#include "MySimpleCounterRecorderSource.generated.h"

UCLASS(BlueprintType, Blueprintable, EditInlineNew, meta=(DisplayName=“Simple Frame Counter”))
class MYGAME_API UMySimpleCounterRecorderSource : public UTakeRecorderSource
{
    GENERATED_BODY()

public:
    virtual void StartRecording(const FTimecode& InSectionStartTimecode, const FFrameNumber& InSectionFirstFrame, ULevelSequence* InSequence) override;
    virtual void TickRecording(const FQualifiedFrameTime& CurrentSequenceTime) override;
    virtual void StopRecording(ULevelSequence* InSequence) override;

    virtual FText GetDisplayTextImpl() const override { return NSLOCTEXT(“Demo”, “FrameCounter”, “Frame Counter”); }
    virtual FText GetDescriptionTextImpl() const override { return NSLOCTEXT(“Demo”, “FrameCounterDesc”, “Logs current frame number.”); }

private:
    int32 CurrentFrame = 0;
};

// MySimpleCounterRecorderSource.cpp
#include “MySimpleCounterRecorderSource.h”
#include “LevelSequence.h”
#include “Misc/OutputDeviceNull.h”

void UMySimpleCounterRecorderSource::StartRecording(const FTimecode& InSectionStartTimecode, const FFrameNumber& InSectionFirstFrame, ULevelSequence* InSequence)
{
    CurrentFrame = 0;
    UE_LOG(LogTemp, Warning, TEXT(“Simple Counter Recorder: Recording Started at Timecode %s”), *InSectionStartTimecode.ToString());
}

void UMySimpleCounterRecorderSource::TickRecording(const FQualifiedFrameTime& CurrentSequenceTime)
{
    CurrentFrame++;
    UE_LOG(LogTemp, Log, TEXT(“Simple Counter Recorder: Frame %d (Sequence Time: %s)”), CurrentFrame, *CurrentSequenceTime.AsSeconds());
}

void UMySimpleCounterRecorderSource::StopRecording(ULevelSequence* InSequence)
{
    UE_LOG(LogTemp, Warning, TEXT(“Simple Counter Recorder: Recording Stopped. Total frames: %d”), CurrentFrame);
    // 在实际应用中，这里可以将 CurrentFrame 数据写入 InSequence 的自定义轨道
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | 底层的 Sequencer 电影场景框架 |
| `LevelSequence` | 高级的关卡序列资产和播放逻辑 |
| `TakeRecorderNamingTokens` | 为 Take Recorder 提供命名令牌（如 `{slate}`, `{take}`）系统，用于动态生成资产路径和名称 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee6722f8` | Take Recorder: Correcting regression where the Attach Track Recorder does not correctly record attac | 修复了附件轨道录制器无法正确记录附件关系的回归问题。 |
| 2026-05-14 | `d17111f0` | Take Recorder: Protecting against crashing on a null sub section sequence. | 增加了对子序列为空情况的保护，防止程序崩溃。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数时产生编译警告的代码。 |
| 2026-05-13 | `0c5ab24a` | Take Recorder: Adding missing WITH_EDITOR guard on log. | 为仅编辑器日志添加了缺失的 WITH_EDITOR 编译守卫。 |
| 2026-05-13 | `6aee158b` | Take Recorder: Fixing possible crash where a weak pointer could trigger an assertion due to a CastCh | 修复了一个可能导致崩溃的问题，该问题源于弱指针在Cast检查期间触发断言。 |

### 维护评价

Take Recorder 是虚幻引擎虚拟制作管线中的核心组件，自2019年创建以来持续维护。从近期的Git提交记录（截至2026年5月）来看，插件仍在**活跃维护**中，主要专注于回归修复、稳定性增强（防止崩溃）和编译兼容性改进。这表明该插件是生产环境中的关键工具，Epic Games持续投入资源保障其可靠性。尽管已存在约7年，但其功能仍在不断打磨和完善。**强烈推荐**用于任何涉及虚拟制片、过场动画录制或需要系统化镜头管理的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes)
- [官方文档]() （未提供）
- [测试用例]() （通常位于 `Engine/Tests/` 目录下，不在插件目录内）