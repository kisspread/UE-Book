# Replay Tracks (Experimental)

> Sequence tracks for playing recorded gameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 回放轨道 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ReplayTracks` (Runtime), `ReplayTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ReplayTracks) | |

## 用途

ReplayTracks 插件是一个**将 Unreal Engine 的 Gameplay Replay（游戏录制回放）系统与 Sequencer（序列器）时间轴集成**的工具。它解决的核心问题是：让设计师和开发者能够在 Sequencer 中精确地控制和编排游戏内录制的回放片段，用于创建过场动画、游戏内事件或回放素材的精确时间线。

**为什么存在？** 虽然引擎的 `DemoNetDriver` 提供了基础的 Gameplay Replay 功能，但将其与 Sequencer 集成需要编写大量自定义代码。此插件封装了这部分逻辑，提供了一个标准化的 Sequencer Track（轨道），使得用户可以将回放事件无缝地编排在其他 Sequencer 动画、镜头和事件的时间线上，实现电影级游戏回放的混合编辑。

## 使用场景

- 你在制作一个需要**游戏回放与过场动画无缝衔接**的游戏，例如体育游戏中的精彩镜头回放，或动作游戏中的技能演示。
- 你希望在 **Sequencer 中编排多个游戏内录制的事件**，并精确控制其播放、暂停和跳转的时间点，用于制作复杂的、基于真实游戏过程的宣传片。
- 你作为技术美术或关卡设计师，需要**将基于 `DemoNetDriver` 录制的游戏回放，像普通动画资产一样放置到 Sequencer 时间线上**进行后期编辑和合成。

## 蓝图用法

该插件主要通过 C++ 进行集成和配置，其核心类未暴露大量 `BlueprintCallable` 节点。蓝图主要用于在 Sequencer 编辑器中创建和配置回放轨道与片段。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddNewReplaySection` | 在回放轨道上指定的时间点添加一个新的回放片段 | `UMovieSceneReplayTrack` |
| 设置 `ReplayName` | 在回放片段的属性中设置要播放的已录制回放的名称 | `UMovieSceneReplaySection` |

### 使用示例（蓝图描述）

1.  在 Sequencer 编辑器中，为你的 Sequence 添加一个 `Replay Track`。
2.  在该轨道上，调用 `Add New Replay Section` 节点或在时间线上右键创建新的 `Replay Section`。
3.  选中创建的回放片段，在其 `Details` 面板中，找到 `Replay` 类别，将 `ReplayName` 属性设置为游戏内已通过 `DemoNetDriver` 录制好的回放文件的名称。
4.  通过拖拽片段的边缘来设置它在时间线上的起止时间。
5.  当 Sequencer 播放到该片段的时间段时，将自动控制指定的 Gameplay Replay 开始、播放、暂停或跳转。

## C++ 用法

核心用法是实现自定义的 `FMovieSceneReplayBroker` 并将其注册到 `FMovieSceneReplayManager` 中，以适配你的游戏特定回放系统。

### 头文件引入

```cpp
#include "MovieSceneReplayManager.h"
#include "Tracks/MovieSceneReplayTrack.h"
#include "Sections/MovieSceneReplaySection.h"
```

### 基本用法

从 `MovieSceneReplayManager.h` 提取的代码示例，展示如何注册一个自定义的 Broker。

```cpp
// 1. 定义你自己的 Replay Broker，继承自 FMovieSceneReplayBroker
class FMyGameReplayBroker : public FMovieSceneReplayBroker
{
public:
    virtual bool SupportsWorld(const UWorld* InWorld) const override
    {
        // 返回此 Broker 是否支持对指定的 World 进行回放控制
        // 通常检查 World 是否具有 DemoNetDriver 等
        return InWorld && InWorld->GetDemoNetDriver();
    }

    virtual bool CanStartReplay(const UWorld* InWorld) const override
    {
        // 根据游戏状态判断是否可以开始回放
        // 例如检查回放数据是否已加载
        return true;
    }

    virtual void OnReplayStarted(UWorld* InWorld) override
    {
        // Sequencer 控制回放开始时调用
        // 可在此处进行游戏逻辑准备
    }

    virtual void OnGoToTime(UWorld* InWorld, float TimeInSeconds) override
    {
        // Sequencer 跳转到回放的特定时间时调用
        // 需要实现跳转到回放记录中对应时间点的逻辑
    }

    virtual void OnReplayPlay(UWorld* InWorld) override
    {
        // Sequencer 恢复回放播放时调用
    }

    virtual void OnReplayPause(UWorld* InWorld) override
    {
        // Sequencer 暂停回放时调用
    }

    virtual void OnReplayStopped(UWorld* InWorld) override
    {
        // Sequencer 控制回放停止时调用
        // 可在此处清理资源
    }
};

// 2. 在合适的时机（例如 GameInstance 初始化后）注册你的 Broker
FMovieSceneReplayBrokerHandle MyBrokerHandle;
MyBrokerHandle = FMovieSceneReplayManager::Get().RegisterBroker<FMyGameReplayBroker>();

// 3. 在对象销毁或模块卸载时注销 Broker
FMovieSceneReplayManager::Get().UnregisterBroker(MyBrokerHandle);
```

### 进阶用法

监控和管理全局回放状态。

```cpp
FMovieSceneReplayManager& ReplayManager = FMovieSceneReplayManager::Get();

// 武装回放系统，表明 Sequencer 即将需要控制回放
ReplayManager.ArmReplay();

// 检查回放是否已武装
if (ReplayManager.IsReplayArmed())
{
    // ... 执行准备逻辑
}

// 查询当前回放状态
EMovieSceneReplayStatus Status = ReplayManager.GetReplayStatus();
switch (Status)
{
    case EMovieSceneReplayStatus::Stopped:
        UE_LOG(LogTemp, Log, TEXT("Replay is stopped."));
        break;
    case EMovieSceneReplayStatus::Loading:
        UE_LOG(LogTemp, Log, TEXT("Replay is loading."));
        break;
    case EMovieSceneReplayStatus::Playing:
        UE_LOG(LogTemp, Log, TEXT("Replay is playing."));
        break;
}

// 根据游戏逻辑解除武装（例如玩家取消了回放播放）
ReplayManager.DisarmReplay();
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何为你的游戏集成 ReplayTracks 插件。

**MyReplayBroker.h**
```cpp
// MyReplayBroker.h
#pragma once

#include "MovieSceneReplayManager.h"

class FMyReplayBroker : public FMovieSceneReplayBroker
{
public:
    virtual ~FMyReplayBroker() {}

    // 你可以根据需要重写各个虚函数，这里使用基类默认行为
    // 虚函数的重写可参考“C++ 用法”章节中的 FMyGameReplayBroker
};
```

**MyGameModule.cpp**
```cpp
// MyGameModule.cpp
#include "Modules/ModuleManager.h"
#include "MovieSceneReplayManager.h"
#include "MyReplayBroker.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        // 在模块启动时注册我们的 Replay Broker
        BrokerHandle = FMovieSceneReplayManager::Get().RegisterBroker<FMyReplayBroker>();
    }

    virtual void ShutdownModule() override
    {
        // 在模块关闭时注销 Broker
        if (BrokerHandle.Value != INDEX_NONE)
        {
            FMovieSceneReplayManager::Get().UnregisterBroker(BrokerHandle);
        }
    }

private:
    FMovieSceneReplayBrokerHandle BrokerHandle;
};

IMPLEMENT_MODULE(FMyGameModule, MyGameModule);
```

## 模块依赖

从插件的构建逻辑和代码引用推断，你的项目模块如果要使用 ReplayTracks 功能，需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心模块，提供 `UMovieSceneTrack`, `UMovieSceneSection`, `UMovieSceneEntitySystem` 等基础类。 |
| `MovieSceneTracks` | 提供 Sequencer 标准轨道（如变换、镜头）的实现，是理解轨道工作方式的参考。 |
| `GameplayReplays` 或你的自定义回放模块 | 提供底层的 `DemoNetDriver` 和回放数据，是本插件控制的目标。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-06-05 | `28030cd1` | Sequencer: remove uses of IMovieScenePlayer | 进行了一次与 Sequencer 核心 API (`IMovieScenePlayer`) 相关的重构或清理。 |
| 2024-02-21 | `33c4fac2` | [Backout] - CL31676435 and 31676432, which restores 31652683 and 31660265 | 回退了部分改动，恢复了之前的一个提交。 |
| 2024-02-21 | `22575fdd` | [Backout] - CL31652683 | 回退了另一个提交。 |
| 2024-02-20 | `4aa3f9f3` | Sequencer: linker/runner refactor | 随 Sequencer 整体的实体链接器/运行器重构而更新。 |
| 2023-11-03 | `bb5b082f` | Sequencer: move evaluation information onto FSharedPlaybackState | 随 Sequencer 将求值信息迁移到共享播放状态的改动而更新。 |

### 维护评价

- **创建时间**：创建于 2021 年 4 月，已有约 4 年历史。
- **维护状态**：**维护不活跃**。最近的实质性更新（移除 `IMovieScenePlayer` 使用）发生在 2024 年 6 月，但这更可能是对 Sequencer 核心 API 变化的被动适配，而非功能增强。在此之前，更新集中于跟随 Sequencer 核心架构的重构。
- **已知限制**：`.uplugin` 明确标记为 `IsBetaVersion: true`，且 `EnabledByDefault: false`。这表明它仍处于**实验性**阶段，API 和功能可能不稳定，且不包含在默认的构建中。
- **推荐使用**：**谨慎推荐**。如果你的需求确实需要 Sequencer 对 Gameplay Replay 的精细控制，并且愿意承担实验性 API 变更的风险，此插件提供了有价值的基础框架。对于生产环境中的关键功能，建议先在原型中充分测试。鉴于其长期处于实验状态且更新多为维护性，它可能不是 Epic 当前重点开发的功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ReplayTracks)
- 官方文档：无
- 测试用例：未在提供信息中明确，可尝试在 `Engine/Tests/` 或插件目录内搜索相关测试文件。