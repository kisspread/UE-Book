# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 录制器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderEditor` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime), `TakesCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes) | |

## 用途
这个插件是虚拟制作流程中用于自动化录制、回放和管理 “Take”（一条拍摄或一次数据记录）的核心工具。它解决了传统手动创建和操作 Level Sequence 的繁琐问题，提供了一套完整的系统，允许用户一键式地将场景中的各种动态数据（如角色动画、相机移动、音频、Live Link 数据、缓存轨道等）同步记录到 Level Sequence 中。其核心价值在于**精确的帧同步**和**自动化数据收集**，特别适用于需要反复尝试和挑选最佳表演的影视动画、游戏过场动画及虚拟制片流程。

## 使用场景
- **虚拟制片（Virtual Production）**：在实时拍摄过程中，一键录制演员表演（通过 Live Link）、摄像机运动、场景变化和后期参数，为后期编辑提供完整的、帧对齐的原始数据。
- **游戏过场动画制作**：反复录制和调整由 Sequencer 控制的过场动画，快速迭代，并将最终满意的版本保存为 Take。
- **精确缓存数据录制**：例如，需要精确录制 Niagara 粒子系统在特定时间段内的状态数据（缓存轨道），用于后续分析或精确回放，此时插件可以接管编辑器时钟以保证帧精度。
- **多源数据同步录制**：同时录制来自不同来源的数据（如动画蓝图、物理模拟、音频），并将它们整合到一个 Level Sequence 中。

## 蓝图用法
此插件提供了强大的蓝图 API，主要围绕 `UCacheTrackRecorder` 类和相关参数结构体，用于控制录制过程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Active Recorder` | 获取当前正在活动的录制器实例（如果有的话） | `UCacheTrackRecorder` (静态) |
| `Record Cache Track` | 录制单个缓存轨道（IMovieSceneCachedTrack） | `UCacheTrackRecorder` (静态) |
| `Record Cache Tracks` | 录制多个缓存轨道 | `UCacheTrackRecorder` (静态) |
| `Record Selected Tracks` | 录制 Sequencer 中当前选中的所有缓存轨道 | `UCacheTrackRecorder` (静态) |
| `Get Sequence` | 获取当前录制器正在写入的目标 Level Sequence 资产 | `UCacheTrackRecorder` |
| `Get State` | 获取录制器的当前状态（如：Starting, Started, Stopped） | `UCacheTrackRecorder` |
| `Initialize` | 使用给定的参数初始化一个新的录制会话 | `UCacheTrackRecorder` |
| `Stop` | 正常停止当前的录制 | `UCacheTrackRecorder` |
| `Cancel` | 取消当前的录制 | `UCacheTrackRecorder` |

### 使用示例（蓝图描述）
1. **基本录制**：
   - 在蓝图中，通过 `Create Object` 节点创建 `FCacheRecorderParameters` 结构体变量，并根据需要配置其 `User` 和 `Project` 成员（例如，设置 `DefaultSlate`，勾选 `bMaximizeViewport`）。
   - 获取一个对 `ISequencer` 的引用（通常来自 Sequencer 编辑器工具）。
   - 调用 `Record Cache Tracks` 静态节点，传入要录制的缓存轨道数组、Sequencer 引用和配置好的参数。
   - 调用后，录制自动开始。之后可通过 `Get State` 节点轮询或通过事件监听录制完成。

2. **在 Sequencer 中触发录制**：
   - 在 Sequencer 工具栏按钮的点击事件中，首先调用 `Record Selected Tracks`（如果希望只录制选中的轨道）或 `Record Cache Tracks`（录制所有已知的缓存轨道）。
   - 该调用会处理所有初始化、UI 提示（如果启用）和录制流程的启动。

## C++ 用法
此插件的 C++ API 主要面向需要深度集成或扩展录制功能的开发者。

### 头文件引入
```cpp
#include "CacheTrackRecorder.h"
```

### 基本用法
以下示例展示了如何通过 C++ 代码启动一次缓存轨道的录制。
（来源参考：`UCacheTrackRecorder` 静态方法设计及参数结构体定义）
```cpp
// 假设你已经有一个指向目标 Sequencer 的 TSharedPtr<ISequencer> SequencerPtr
// 假设你已经有了一个包含要录制轨道的 TArray<IMovieSceneCachedTrack*> TracksToRecord

// 1. 配置录制参数
FCacheRecorderParameters Params;
Params.User.bMaximizeViewport = false; // 不强制最大化视口
Params.User.EngineTimeDilation = 1.0f; // 正常时间流速
Params.Project.DefaultSlate = TEXT("MyTake"); // 设置一个名称
Params.Project.bCacheTrackRecorderControlsClockTime = true; // 让录制器控制时钟，保证帧精度
Params.Project.bStartAtCurrentTimecode = true; // 从当前时间码开始

// 2. 开始录制
// 方法一：录制指定的轨道
UCacheTrackRecorder::RecordCacheTracks(TracksToRecord, SequencerPtr, Params);

// 方法二：录制 Sequencer 中所有选中的轨道
// UCacheTrackRecorder::RecordSelectedTracks(SequencerPtr, Params);

// 3. 后续监控状态（可选）
UCacheTrackRecorder* ActiveRecorder = UCacheTrackRecorder::GetActiveRecorder();
if (ActiveRecorder)
{
    ECacheTrackRecorderState State = ActiveRecorder->GetState();
    if (State == ECacheTrackRecorderState::Started)
    {
        // 录制已开始...
    }
    // 也可以监听完成事件（需要查看是否有委托暴露）
}
```

### 进阶用法
对于需要更精细控制的场景（例如，自定义轨道录制器），可以继承 `UMovieSceneTrackRecorder` 并在 `TakeTrackRecorders` 模块中注册。然后，通过 `TakeRecorderSources` 模块的接口，将自定义数据源添加到 Take Recorder 的面板中，使其成为可录制的选项之一。这通常涉及实现 `ITakeRecorderSource` 或其变体接口。

## Demo 示例
一个演示如何使用 `UCacheTrackRecorder` 录制任意 Sequencer 中选中缓存轨道的最小 C++ 类。
```cpp
// MyTakeRecordTest.h
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyTakeRecordTest.generated.h"

UCLASS()
class MYPROJECT_API UMyTakeRecordTest : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    // 蓝图可调用的函数，用于测试录制选中的缓存轨道
    UFUNCTION(BlueprintCallable, Category = "Take Test")
    static void TestRecordSelectedCacheTracks();
};

// MyTakeRecordTest.cpp
#include "MyTakeRecordTest.h"
#include "CacheTrackRecorder.h"
#include "ISequencer.h"
#include "SequencerTools.h"

void UMyTakeRecordTest::TestRecordSelectedCacheTracks()
{
    // 获取活动的 Sequencer（这通常需要更复杂的逻辑来找到正确的 Sequencer 实例）
    // 这里假设通过全局方式或编辑器工具获取到了一个有效的 Sequencer 指针
    TSharedPtr<ISequencer> Sequencer = /* ... 获取 Sequencer 的方法 ... */;
    if (!Sequencer.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("无法找到有效的 Sequencer 实例。"));
        return;
    }

    // 配置参数
    FCacheRecorderParameters Parameters;
    Parameters.User.bMaximizeViewport = true; // 例如，最大化视口以专注于录制
    Parameters.Project.DefaultSlate = TEXT("TestSlate");
    Parameters.Project.bCacheTrackRecorderControlsClockTime = true; // 启用精确帧控制

    // 调用静态方法开始录制选中的轨道
    UCacheTrackRecorder::RecordSelectedTracks(Sequencer, Parameters);

    UE_LOG(LogTemp, Log, TEXT("已启动对选中缓存轨道的录制。"));
}
```

## 模块依赖
基于插件的 `Build.cs` 文件分析，使用此插件需要依赖以下关键模块（省略了通用核心模块如 `Core`, `Engine`）：

| 模块 | 用途 |
|---|---|
| `LevelSequence` | 核心依赖，用于操作 Level Sequence 资产和序列化录制的数据。 |
| `Sequencer` | 核心依赖，提供 Sequencer 编辑器、播放控制和 `ISequencer` 接口。 |
| `MovieScene` | 核心依赖，包含 Movie Scene 的基础数据结构，如轨道、片段、评价器。 |
| `MovieSceneTools` | 提供用于操作和录制 Movie Scene 数据的工具类。 |
| `TakeCore` | 本插件内部模块，提供 Takes 系统的核心定义和接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee6722f8` | Take Recorder: Correcting regression where the Attach Track Recorder does not correctly record attac | 修复了一个回归问题：Attach Track Recorder 不能正确记录附件信息。 |
| 2026-05-14 | `d17111f0` | Take Recorder: Protecting against crashing on a null sub section sequence. | 修复当子片段序列为空时可能导致的崩溃。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-13 | `0c5ab24a` | Take Recorder: Adding missing WITH_EDITOR guard on log. | 添加了缺失的 `WITH_EDITOR` 编译守卫以修复日志输出。 |
| 2026-05-13 | `6aee158b` | Take Recorder: Fixing possible crash where a weak pointer could trigger an assertion due to a CastCh | 修复了一个可能的崩溃，该崩溃由弱指针在 Cast 检查时触发断言导致。 |

### 维护评价
- **维护状态**：**积极维护**。
- **分析**：
    1. **创建时间**：该插件创建于 2019 年初，已有约 7 年历史，是虚拟制作工具链中的成熟组件。
    2. **近期活动**：从提交记录看，在 2026 年 5 月仍有频繁的、高质量的 Bug 修复和稳定性改进提交。这表明 Epic Games 的开发团队仍在积极维护此插件，并快速响应发现的回归问题和崩溃。
    3. **功能定位**：作为虚拟制作流程的核心录制工具，其重要性决定了它大概率会持续维护。
    4. **已知问题**：近期提交集中于修复回归和崩溃，表明在复杂使用场景下可能偶发稳定性问题，但团队正在积极解决。
- **推荐**：**强烈推荐使用**。该插件是 UE 虚拟制作功能栈中不可或缺的一部分，功能成熟，且处于活跃维护中，能够满足专业影视和游戏制作的需求。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/Takes/Source/TakeRecorder/Tests)