# Learning Agents

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 学习智能体 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningAgents) | |

## 用途

Learning Agents 插件旨在为游戏开发者提供一个集成的机器学习框架，用于训练和驱动游戏中的 AI 角色。其核心目的是简化将强化学习（Reinforcement Learning）和模仿学习（Imitation Learning）应用于游戏 AI 的复杂过程。开发者不再需要深入底层 ML 算法或编写复杂的 Python 脚本与引擎交互，而是可以通过蓝图或 C++ 在引擎内直接定义观察、动作、奖励，并录制演示数据或启动训练循环，从而让 AI 角色学会特定的行为。

## 使用场景

- **游戏角色AI行为学习**：你需要让一个非玩家角色（NPC）学会复杂的导航、战斗或任务执行策略，而不是手动编写状态机或行为树。
- **创建AI演示与调试**：你需要录制玩家或测试AI的操作过程，用于后期分析、作为模仿学习的训练数据，或生成游戏回放。
- **简化机器学习训练流程**：你希望利用机器学习训练角色，但希望避免搭建和维护复杂的外部训练环境，直接在编辑器或游戏进程中启动训练。

## 蓝图用法

### 核心节点

以下是从 `LearningAgentsReplay` 模块提取的核心蓝图节点，主要围绕重放（Replay）功能。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DoesPlatformSupportReplays` | 静态函数，检查当前平台是否支持重放功能。 | `ULearningAgentsReplaySubsystem` |
| `RecordClientReplay` | 开始为指定的玩家控制器录制客户端游戏过程。 | `ULearningAgentsReplaySubsystem` |
| `StopRecordingReplay` | 停止当前正在进行的录制。 | `ULearningAgentsReplaySubsystem` |
| `QueryLearningAgentsReplays` | 异步操作，查询已存储的重放列表。 | `UAsyncAction_LearningAgentsQueryReplays` |
| `PlayReplay` | 加载对应的地图并播放一个重放。 | `ULearningAgentsReplaySubsystem` |
| `SeekInActiveReplay` | 在正在播放的重放中前进或后退。 | `ULearningAgentsReplaySubsystem` |
| `GetReplayLengthInSeconds` | 获取当前重放的总时长（秒）。 | `ULearningAgentsReplaySubsystem` |
| `GetReplayCurrentTime` | 获取当前重放的播放时间点（秒）。 | `ULearningAgentsReplaySubsystem` |

#### `ULearningAgentsReplayListEntry` 属性查询节点
| 节点 | 说明 |
|---|---|
| `GetFriendlyName` | 获取重放的友好名称（UI显示用）。 |
| `GetTimestamp` | 获取重放的录制时间。 |
| `GetDuration` | 获取重放的时长。 |
| `GetNumViewers` | 获取正在观看此重放的观众数量。 |
| `GetIsLive` | 判断重放是否为实时直播中。 |

### 使用示例（蓝图描述）

1.  **录制游戏过程**：
    - 获取本地玩家控制器，调用 `RecordClientReplay` 节点开始录制。
    - 在需要停止录制的地方（如游戏结束时），调用 `StopRecordingReplay` 节点。

2.  **查询并播放重放**：
    - 使用 `QueryLearningAgentsReplays` 节点（异步），连接 `QueryComplete` 代理。
    - 在代理回调中，从返回的 `ULearningAgentsReplayList` 对象中获取 `Results` 数组。
    - 选择一个 `ULearningAgentsReplayListEntry`，调用 `PlayReplay` 节点开始回放。
    - 可使用 `GetReplayLengthInSeconds` 和 `GetReplayCurrentTime` 节点配合进度条UI。
    - 调用 `SeekInActiveReplay` 节点实现快进/倒带功能。

## C++ 用法

### 头文件引入

使用重放功能，主要包含 `LearningAgentsReplaySubsystem.h`。
```cpp
#include "LearningAgentsReplaySubsystem.h"
```

### 基本用法

以下代码展示了如何初始化重放子系统并开始录制游戏过程。
```cpp
// 假设在某个 Actor 或 GameMode 中
#include "LearningAgentsReplaySubsystem.h"

void AMyGameMode::StartRecordingDemo()
{
    UGameInstance* GameInstance = GetGameInstance();
    if (GameInstance)
    {
        // 获取重放子系统
        ULearningAgentsReplaySubsystem* ReplaySubsystem = GameInstance->GetSubsystem<ULearningAgentsReplaySubsystem>();
        if (ReplaySubsystem)
        {
            // 检查平台支持
            if (ULearningAgentsReplaySubsystem::DoesPlatformSupportReplays())
            {
                // 获取本地玩家控制器并开始录制
                APlayerController* PC = GetWorld()->GetFirstPlayerController();
                if (PC)
                {
                    ReplaySubsystem->RecordClientReplay(PC);
                }
            }
        }
    }
}
```

### 进阶用法

结合异步查询，列出并播放一个已有的重放。
```cpp
// 在某个 UI 类中
#include "LearningAgentsReplaySubsystem.h"
#include "AsyncAction_LearningAgentsQueryReplays.h"

void UMyReplayBrowserWidget::QueryAndPlayFirstReplay()
{
    APlayerController* PC = GetOwningPlayer();
    if (!PC) return;

    // 创建并激活异步查询操作
    UAsyncAction_LearningAgentsQueryReplays* QueryAction = UAsyncAction_LearningAgentsQueryReplays::QueryLearningAgentsReplays(PC);
    if (QueryAction)
    {
        // 绑定回调
        QueryAction->QueryComplete.AddDynamic(this, &UMyReplayBrowserWidget::OnQueryReplaysComplete);
        QueryAction->Activate();
    }
}

void UMyReplayBrowserWidget::OnQueryReplaysComplete(ULearningAgentsReplayList* ReplayList)
{
    if (ReplayList && ReplayList->Results.Num() > 0)
    {
        ULearningAgentsReplayListEntry* FirstReplay = ReplayList->Results[0];
        UGameInstance* GameInstance = GetGameInstance();
        if (GameInstance && FirstReplay)
        {
            ULearningAgentsReplaySubsystem* ReplaySubsystem = GameInstance->GetSubsystem<ULearningAgentsReplaySubsystem>();
            if (ReplaySubsystem)
            {
                // 播放第一个找到的重放
                ReplaySubsystem->PlayReplay(FirstReplay);
            }
        }
    }
}
```

## Demo 示例

一个最小的演示，展示如何在运行时开始和停止录制。
```cpp
// MyDemoRecorder.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDemoRecorder.generated.h"

class ULearningAgentsReplaySubsystem;

UCLASS()
class AMyDemoRecorder : public AActor
{
    GENERATED_BODY()
    
public:
    AMyDemoRecorder();

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void StartDemoRecording();

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void StopDemoRecording();

private:
    UPROPERTY()
    TObjectPtr<ULearningAgentsReplaySubsystem> CachedReplaySubsystem;
};
```

```cpp
// MyDemoRecorder.cpp
#include "MyDemoRecorder.h"
#include "LearningAgentsReplaySubsystem.h"
#include "Kismet/GameplayStatics.h"

AMyDemoRecorder::AMyDemoRecorder()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDemoRecorder::StartDemoRecording()
{
    UGameInstance* GameInstance = UGameplayStatics::GetGameInstance(this);
    if (GameInstance)
    {
        CachedReplaySubsystem = GameInstance->GetSubsystem<ULearningAgentsReplaySubsystem>();
        if (CachedReplaySubsystem && ULearningAgentsReplaySubsystem::DoesPlatformSupportReplays())
        {
            APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
            if (PC)
            {
                CachedReplaySubsystem->RecordClientReplay(PC);
                UE_LOG(LogTemp, Log, TEXT("Learning Agents Replay Recording Started."));
            }
        }
    }
}

void AMyDemoRecorder::StopDemoRecording()
{
    if (CachedReplaySubsystem)
    {
        CachedReplaySubsystem->StopRecordingReplay();
        UE_LOG(LogTemp, Log, TEXT("Learning Agents Replay Recording Stopped."));
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 分析，该插件主要用于运行时。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 仅 `LearningAgentsTrainingEditor` 模块依赖，用于编辑器内的训练集成。打包后运行时无需此依赖。 |
| **无其他特殊依赖** | `LearningAgents`, `LearningAgentsReplay`, `LearningAgentsTraining` 运行时模块主要依赖标准 Core/Engine 模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0b2b6629` | [LearningAgents] Fix interactor SetActionVector | 修复了交互器中设置动作向量的bug |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式说明符与参数位数不匹配的问题 |
| 2026-04-24 | `553c9043` | [LearningAgents] Pass NNECpuPath to python directly | 改进了NNE CPU路径传递方式，直接传给Python脚本 |
| 2026-04-20 | `305f49dd` | [LearningAgents] Improve reinitialize recording behavior to reset and add new schema (#14361) | 优化了重新初始化录制时的行为，支持重置和添加新schema |
| 2026-04-14 | `898b7c7c` | [LACombat] Replay Runtime Recording | 为战斗相关的学习智能体添加了运行时重放录制功能 |

### 维护评价

Learning Agents 插件处于**活跃维护**状态。尽管被放置在 `Experimental` 目录下且默认未启用，但其版本号（0.2）和近期的提交记录表明它仍在积极开发中。最近的更新集中在2026年4-5月，修复了多个运行时bug，并增加了新的功能特性（如战斗录制）。这表明 Epic 团队仍在投入资源完善该插件，是一个有潜力的、前沿的AI解决方案。

**推荐使用**：对于希望在UE项目中集成机器学习AI，特别是强化学习和模仿学习的开发者，此插件提供了一个官方的、与引擎深度集成的解决方案。虽然它可能仍存在一些API变动或不完善之处，但其活跃的维护状态意味着问题会被持续修复和功能会不断扩展。使用时应关注其文档和更新日志，以适应可能的API变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningAgents)
- [官方文档]()（暂无）
- [测试用例]()（暂未找到公开的测试用例路径）