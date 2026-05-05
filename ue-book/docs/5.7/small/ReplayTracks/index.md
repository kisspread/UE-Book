# Replay Tracks (Experimental)

> Sequence tracks for playing recorded gameplay

| 属性 | 值 |
|---|---|
| 分类 | MovieScene |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ❌ `CanContainContent: false` |
| 模块 | `ReplayTracks` (Runtime), `ReplayTracksEditor` (Editor) |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/ReplayTracks) | |

> ⚠️ **实验性插件**：`IsBetaVersion: true`，API 可能在未来版本中变动。需手动在 Edit → Plugins 中启用。

## 用途

ReplayTracks 将 UE 的 **Demo Replay（游戏录像回放）** 系统与 **Sequencer（序列器）** 打通。

UE 的 Replay 系统可以录制和回放网络化游戏的完整状态，但原生 API 只提供基本的播放/暂停/跳转。ReplayTracks 在 Sequencer 中添加了一种新的 Track 类型，让你可以用时间轴精确控制录像回放的时机——比如"在第 5 秒自动开始回放一段 10 秒的录像"、"配合摄像机动画同步回放"、"在回放期间进行 Scrub 和逐帧检查"。

核心架构基于 **Broker 模式**：`FMovieSceneReplayBroker` 提供了一个可扩展的接口，游戏可以注册自己的 Broker 实现来接管回放的启动、暂停、时间跳转等逻辑。插件自带一个默认 Broker，开箱可用。

## 使用场景

- 你在做一个竞技游戏（如 FPS/MOBA），需要用 Sequencer 编辑一段包含游戏录像回放的影片 → 用 ReplayTracks
- 你需要在 Sequencer 时间轴上精确控制录像回放的播放/暂停/Seek → 用 ReplayTracks
- 你需要将摄像机动画与录像回放同步（如赛后精彩回放 + 慢动作镜头）→ 用 ReplayTracks
- 你需要在编辑器中 Scrub 一段录像来精确截取画面 → 用 ReplayTracks

## 蓝图用法

本插件主要面向编辑器 Sequencer 工作流，**没有暴露 BlueprintCallable 函数**。所有操作通过 Sequencer UI 完成：

1. 在 Sequencer 中通过 **Add → Replay Track** 添加回放轨道
2. 在轨道上添加 Section，设置 `ReplayName` 属性为已录制的 Replay 名称
3. 启动 PIE，然后点击轨道上的 **"Start Replay"** 按钮来 Arm 并触发回放
4. Sequencer 的播放/暂停/Scrub 会自动同步到录像回放

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneReplayManager.h"
#include "Sections/MovieSceneReplaySection.h"
#include "Tracks/MovieSceneReplayTrack.h"
```

### 基本用法：通过 C++ 代码 Arm 和控制回放

```cpp
// 获取全局 Replay Manager
FMovieSceneReplayManager& Manager = FMovieSceneReplayManager::Get();

// Arm（预备）回放 — Sequencer 评估到 ReplaySection 时会自动启动
Manager.ArmReplay();

// 检查状态
bool bArmed = Manager.IsReplayArmed();
EMovieSceneReplayStatus Status = Manager.GetReplayStatus(); // Stopped / Loading / Playing

// Disarm（停止）回放
Manager.DisarmReplay();
```

> 来源：`Source/ReplayTracks/Private/MovieSceneReplayManager.cpp`

### 进阶用法：注册自定义 Replay Broker

默认 Broker 通过 `WorldSettings->SetTimeDilation` 控制回放速度。如果你的游戏需要自定义逻辑（如自定义 Spectator Pawn、特殊渲染设置），可以注册自己的 Broker：

```cpp
#include "MovieSceneReplayManager.h"

class FMyGameReplayBroker : public FMovieSceneReplayBroker
{
public:
    virtual bool SupportsWorld(const UWorld* InWorld) const override
    {
        // 只在游戏世界的 Replay 中生效
        return InWorld->WorldType == EWorldType::Game;
    }

    virtual bool CanStartReplay(const UWorld* InWorld) const override
    {
        // 自定义启动条件检查
        return InWorld->GetFirstPlayerController() != nullptr;
    }

    virtual void OnReplayStarted(UWorld* InWorld) override
    {
        // 回放已加载并准备就绪时的初始化逻辑
        UE_LOG(LogTemp, Log, TEXT("Replay started in world %s"), *InWorld->GetName());
    }

    virtual void OnReplayPlay(UWorld* InWorld) override
    {
        // Sequencer 从暂停恢复播放时
    }

    virtual void OnReplayPause(UWorld* InWorld) override
    {
        // Sequencer 暂停时
    }

    virtual void OnGoToTime(UWorld* InWorld, float TimeInSeconds) override
    {
        // 用户在 Sequencer 中 Scrub 到某个时间点时
        // TimeInSeconds 是相对于 Replay Section 起点的时间
    }

    virtual void OnReplayStopped(UWorld* InWorld) override
    {
        // 回放结束时的清理逻辑
    }
};

// 在你的模块 StartupModule 中注册
FMovieSceneReplayManager& Manager = FMovieSceneReplayManager::Get();
FMovieSceneReplayBrokerHandle Handle = Manager.RegisterBroker<FMyGameReplayBroker>();

// 在 ShutdownModule 中注销
Manager.UnregisterBroker(Handle);
```

> 来源：`Source/ReplayTracks/Public/MovieSceneReplayManager.h`、`Source/ReplayTracks/Private/MovieSceneReplayManager.cpp`

**注意**：Broker 查找采用**后注册优先**策略（从数组末尾向前搜索），因此后注册的 Broker 会覆盖默认 Broker。默认 Broker 始终在索引 0 位置。

## Demo 示例

以下是一个最小可运行的自定义 Broker + 手动 Arm 回放的示例：

### Build.cs

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "ReplayTracks",
    "MovieScene",
    "MovieSceneTracks"
});
```

### MyReplayBroker.h

```cpp
#pragma once
#include "MovieSceneReplayManager.h"

class FMyReplayBroker : public FMovieSceneReplayBroker
{
public:
    virtual bool SupportsWorld(const UWorld* InWorld) const override { return true; }
    virtual bool CanStartReplay(const UWorld* InWorld) const override;
    virtual void OnReplayStarted(UWorld* InWorld) override;
    virtual void OnReplayStopped(UWorld* InWorld) override;
};
```

### MyReplayBroker.cpp

```cpp
#include "MyReplayBroker.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpectatorPawn.h"

bool FMyReplayBroker::CanStartReplay(const UWorld* InWorld) const
{
    // 需要 PlayerController 和 SpectatorPawn 就绪
    if (APlayerController* PC = InWorld->GetFirstPlayerController())
    {
        return PC->GetSpectatorPawn() != nullptr;
    }
    return false;
}

void FMyReplayBroker::OnReplayStarted(UWorld* InWorld)
{
    UE_LOG(LogTemp, Log, TEXT("Custom broker: replay started"));
}

void FMyReplayBroker::OnReplayStopped(UWorld* InWorld)
{
    UE_LOG(LogTemp, Log, TEXT("Custom broker: replay stopped"));
}
```

## 模块依赖

### ReplayTracks（Runtime）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（DemoNetDriver、World 等） |
| `MovieScene` | Sequencer 实体系统框架 |
| `MovieSceneTracks` | Sequencer 基础 Track 类型 |
| `TimeManagement` | 时间管理（TimeDilation 等） |

### ReplayTracksEditor（Editor）

| 模块 | 用途 |
|---|---|
| `ReplayTracks` | 运行时模块 |
| `Sequencer` | Sequencer 编辑器框架 |
| `MovieSceneTools` | Sequencer 编辑器工具 |
| `UnrealEd` | 编辑器核心 |
| `Slate` / `SlateCore` | UI 框架 |
| `InputCore` | 输入核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-06-05 | `28030cd151c8` | Sequencer: remove uses of IMovieScenePlayer | Sequencer 框架级重构，清理旧 API。本插件跟随框架升级。 |
| 2024-02-21 | `33c4fac21034` | [Backout] - CL31676435 and 31676432 | 回退一个大型 Sequencer linker/runner 重构，说明该重构造成了问题。 |
| 2024-02-21 | `22575fdddad3` | [Backout] - CL31652683 Sequencer: linker/runner refactor | 同上，回退重构 CL。 |

### 维护评价

- **创建时间**：2021-04-08，已存在约 5 年
- **实验性状态**：始终标记为 `IsBetaVersion: true`，从未升级为正式版
- **更新频率**：2024 年的更新全部是跟随 Sequencer 框架重构的被动适配（包括一次回退），没有功能性增强
- **已有 1 年+ 无实质更新**：最后一次改动是 2024-06-05，距今约 23 个月，且仅是框架适配
- **无官方文档**：`.uplugin` 的 `DocsURL` 为空
- **无测试用例**：`Engine/Tests/` 下未找到相关测试

**综合评价**：这是一个**长期处于实验阶段的插件**，功能完整但从未被官方推进到正式状态。适合用于 Sequencer 与 Replay 集成的参考实现，但**不建议在生产环境依赖此插件**——其 API 随时可能变动或被废弃。如果你的项目确实需要 Sequencer 控制 Replay，建议 fork 此插件并自行维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/ReplayTracks)
- [官方文档](https://docs.unrealengine.com/)（此插件无专属文档页）
- UE Replay 系统文档：[Recording and Playing Back](https://docs.unrealengine.com/en-US/TestingAndOptimization/ReplaySystem/)
