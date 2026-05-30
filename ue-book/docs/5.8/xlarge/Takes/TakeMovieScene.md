# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 中文名 | 录制系统 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderEditor` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime), `TakesCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Takes 插件是 Unreal Engine 虚拟制作（Virtual Production）工作流的核心录制系统。它不仅仅是一个简单的录制工具，而是一个完整的**录制-回放-评审**生态系统，专门用于在 LED 墙、动作捕捉等实时视觉特效环境中进行拍摄管理。

该系统解决的核心问题是：在虚拟制作场景中，如何将引擎内所有相关数据（时间码、板信息、动画、音频、各种自定义数据）同步录制下来，并能够精确回放，以便导演和制片人能够评审每次拍摄（Take）。

## 使用场景

- 你在使用 LED 墙进行虚拟拍摄，需要记录每一帧的精确时间码、场景板信息以及所有相关数据，以便后期合成。
- 你需要在一个时间线上管理多次拍摄，并能够方便地在它们之间切换、比较和选择。
- 你的团队需要回放拍摄结果，并添加注释，以便进行创意评审。
- 你正在开发自定义的虚拟制作工具链，需要将特定数据（如自定义传感器数据）集成到录制流程中。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `开始录制` | 开始一次新的 Take 录制，可指定板（Slate）和场景（Shot）信息 | `UTakeRecorderSubsystem` |
| `停止录制` | 停止当前的 Take 录制 | `UTakeRecorderSubsystem` |
| `录制自定义数据` | 向当前 Take 中写入自定义的帧数据（如 FTimecode、字符串等） | `UTakeRecorderSubsystem` |
| `获取当前录制状态` | 检查 Take Recorder 当前是否正在录制 | `UTakeRecorderSubsystem` |
| `播放 Take` | 通过 Sequencer 播放指定的 Take 资产 | `UTakeSequencerSubsystem` |
| `跳转到 Take` | 在 Sequencer 中定位到指定的 Take 时间点 | `UTakeSequencerSubsystem` |

### 使用示例（蓝图描述）

1.  **录制一次完整的 Take**：
    1.  在蓝图中获取 `Take Recorder` 子系统。
    2.  调用 `开始录制` 节点，传入板名称（Slate）、场景编号（Take Number）等信息。
    3.  在游戏或模拟过程中，引擎会自动录制所有已配置的数据源（动画、音频、自定义数据等）。
    4.  需要时，调用 `停止录制` 节点。录制结果会自动保存为一个 Sequencer 资产。

2.  **在 Sequencer 中评审 Take**：
    1.  使用 `打开 Take 编辑器` 节点，打开一个专门的 Take 评审界面。
    2.  在该界面中，可以浏览所有已录制的 Take，查看其时间码、板信息。
    3.  可以播放、暂停、前后跳转，也可以同时打开多个 Take 进行 A/B 对比。

## C++ 用法

### 头文件引入

```cpp
// 基础录制功能
#include "TakeRecorderSubsystem.h"

// Sequencer 播放控制
#include "TakeSequencerSubsystem.h"

// 自定义数据录制（核心数据结构）
#include "TakeMovieScene/TakeMovieSceneModule.h"
```

### 基本用法：向 Take 中写入自定义时间码

以下代码展示了如何在一次 Take 录制中，手动记录一个自定义的 `FTimecode` 和字符串数据。这对于集成外部设备（如动作捕捉系统）数据非常有用。

**来源文件**：`Engine/Plugins/VirtualProduction/Takes/Source/TakeMovieScene/Public/MovieSceneTakeSection.h`

```cpp
// 假设你正在一个 Tick 函数中，并且 Take Recorder 正在录制
if (UTakeRecorderSubsystem* TakeRecorder = GEditor->GetEditorSubsystem<UTakeRecorderSubsystem>())
{
    // 确保正在录制
    if (TakeRecorder->IsRecording())
    {
        // 准备要录制的数据
        FTimecode CurrentTimecode = FTimecode::FromFrameNumber(/* 当前的帧号 */);
        FString MySlateInfo = TEXT("MySlate_01");

        // 创建一个 SectionData 结构体来打包数据
        UMovieSceneTakeSection::FSectionData SectionData;
        SectionData.Timecode = CurrentTimecode;
        SectionData.Slate = MySlateInfo;
        SectionData.Rate = 24.0f; // 通常与 Sequencer 的帧率一致

        // 将数据写入当前的 Take 轨道中
        // 注意：实际写入是通过 Sequencer 的通道（Channel）完成的，
        // 但 TakeRecorderSubsystem 提供了简化接口。
        // 下面是更底层的写入方式，展示了数据是如何被存储的。
        // 通常，你会使用 TakeRecorderSubsystem 提供的更高层的 API。
        // 这里仅为展示数据结构。
        FMovieSceneIntegerChannel& HoursCurve = /* ... 从当前 Take Section 获取小时通道 ... */;
        HoursCurve.Add(/* 当前时间 */, CurrentTimecode.Hours);
        // ... 类似地写入分钟、秒、帧和字符串 ...
    }
}
```

### 进阶用法：分析录制帧的卡顿（Hitching）

Takes 系统内置了帧卡顿检测功能。它比较目标时间码（引擎应到达的时间点）和实际记录的时间码，差异过大则认为是卡顿。这个数据可以在 Sequencer 中可视化，帮助排查性能问题。

**来源文件**：`Engine/Plugins/VirtualProduction/Takes/Source/TakeMovieScene/Public/Hitching/FrameHitchSceneDecoration.h`

```cpp
// 假设你有一个 UFrameHitchSceneDecoration 对象（通常在录制结束后由系统生成）
UFrameHitchSceneDecoration* HitchDecoration = /* ... 获取 ... */;

// 要检查的时刻
FFrameTime TimeToCheck(100); // 第100帧

// 评估该帧是否发生了卡顿
if (TOptional<UE::TakeMovieScene::FFrameHitchData> HitchData = HitchDecoration->Evaluate(TimeToCheck))
{
    // 如果存在数据，说明该帧可能发生了卡顿
    UE::TakeMovieScene::FFrameHitchData& Data = HitchData.GetValue();

    // 比较目标时间码和实际时间码
    if (Data.TargetTimecode != Data.ActualTimecode)
    {
        // 计算延迟的帧数
        int32 HitchedFrames = /* 计算差值，基于 TimecodeProviderFrameRate */;
        UE_LOG(LogTakes, Warning, TEXT("Hitch detected at frame %d. Target: %s, Actual: %s"),
            TimeToCheck.FrameNumber,
            *Data.TargetTimecode.ToString(),
            *Data.ActualTimecode.ToString());
    }
}
```

## Demo 示例

一个最小的、可编译的示例，展示如何在 C++ 模块中访问 Take Recorder 子系统并查询其状态。

### 头文件 (`DemoTakeAccess.h`)

```cpp
#pragma once

#include "CoreMinimal.h"

class FTakesDemo
{
public:
    /** 初始化并检查 Take Recorder 可用性 */
    static void Initialize();

    /** 打印当前录制状态 */
    static void PrintRecordingStatus();
};
```

### 源文件 (`DemoTakeAccess.cpp`)

```cpp
#include "DemoTakeAccess.h"
#include "TakeRecorderSubsystem.h"
#include "Engine/Engine.h"
#include "Modules/ModuleManager.h"

void FTakesDemo::Initialize()
{
    // 确保 TakeRecorder 模块已加载
    if (FModuleManager::Get().IsModuleLoaded("TakeRecorder"))
    {
        UE_LOG(LogTemp, Log, TEXT("TakeRecorder 模块已加载。"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("TakeRecorder 模块未加载。"));
    }
}

void FTakesDemo::PrintRecordingStatus()
{
    // 在编辑器环境下获取 TakeRecorder 子系统
    if (GEditor)
    {
        if (UTakeRecorderSubsystem* TakeRecorderSubsystem = GEditor->GetEditorSubsystem<UTakeRecorderSubsystem>())
        {
            bool bIsRecording = TakeRecorderSubsystem->IsRecording();
            UE_LOG(LogTemp, Log, TEXT("Take Recorder 当前正在录制: %s"), bIsRecording ? TEXT("是") : TEXT("否"));
        }
    }
}
```

## 模块依赖

要使用 Takes 插件的核心功能，你的模块需要依赖 `TakeRecorder` 和 `TakesCore`。以下是额外的不常见依赖：

| 模块 | 用途 |
|---|---|
| `LevelSequence` | 用于操作 Sequencer（Level Sequence）资产，Takes 的核心播放载体 |
| `MovieScene` | 电影场景轨道和通道的底层框架，`TakeMovieScene` 模块构建于其上 |
| `MovieSceneTools` | 提供 Sequencer 编辑器工具，`TakeRecorderEditor` 依赖它来构建录制 UI |
| `TimeManagement` | 提供 `FTimecode` 等时间码相关类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee6722f8` | Take Recorder: Correcting regression where the Attach Track Recorder does not correctly record attac | 修复了附加轨道录制器不能正确记录的回归性错误 |
| 2026-05-14 | `d17111f0` | Take Recorder: Protecting against crashing on a null sub section sequence. | 修复了当子序列为空时可能导致的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下 double 常量截断为 float 产生的警告 |
| 2026-05-13 | `0c5ab24a` | Take Recorder: Adding missing WITH_EDITOR guard on log. | 为日志输出添加了缺失的编辑器宏保护 |
| 2026-05-13 | `6aee158b` | Take Recorder: Fixing possible crash where a weak pointer could trigger an assertion due to a CastCh | 修复了弱指针在 Cast 检查时可能触发断言导致的崩溃 |

### 维护评价

- **活跃维护**：最近 6 个月内（截至 2026 年 5 月）有多次更新，且均为实质性的功能修复和稳定性提升，表明 Epic 仍在积极维护此插件。
- **核心地位**：作为 Virtual Production 工作流的核心组件，Takes 插件不太可能被废弃。
- **稳定性**：近期的提交主要集中在修复崩溃和回归问题，说明该系统趋于成熟和稳定。
- **建议**：强烈推荐在虚拟制作项目中使用。虽然它是一个功能复杂的“老古董”，但拥有完善的功能和持续的维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/Takes/Source/TakeRecorderTests)