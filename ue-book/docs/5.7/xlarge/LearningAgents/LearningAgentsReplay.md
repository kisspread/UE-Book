# Learning Agents

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 学习智能体 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、训练配置模板） |
| 模块 | `Learning` (Runtime), `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime), `LearningTraining` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents) | |

---

## 用途

Learning Agents 插件为虚幻引擎提供了完整的强化学习与模仿学习工作流，使开发者能够通过简单易用的蓝图接口训练 AI 角色。其核心模块 `Learning` 和 `LearningAgents` 实现了神经网络模型、观察/动作编码、训练循环等底层逻辑；而 `LearningAgentsReplay` 模块（本文档重点）负责录制和回放游戏过程，作为训练数据的采集与回放工具。

**LearningAgentsReplay 模块** 专门解决机器学习中数据来源的问题：  
- 录制玩家或 AI 控制的游戏过程，生成 replay 文件  
- 通过蓝图查询已有 replay 列表  
- 回放 replay 并支持时间跳转、速率控制  
- 为训练模块提供真实环境中的示范数据（模仿学习）或用于验证训练后的策略

---

## 使用场景

- **强化学习数据采集**：你想让智能体学习在特定环境中行动，需要大量交互数据。用 `RecordClientReplay` 录制多次尝试过程，再使用训练模块从 replay 中提取经验。
- **模仿学习示范**：由人类玩家演示正确玩法，录制 replay，然后让智能体通过模仿学习复现场景。
- **调试与回放**：训练过程中发现了意外的行为，录制 replay 后可以暂停、慢放、跳转，分析问题。
- **多人回放系统**：基于 `ULearningAgentsReplaySubsystem` 快速搭建自定义回放 UI，支持查询、播放、停止等功能。

---

## 蓝图用法

### 核心节点（LearningAgentsReplay 模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DoesPlatformSupportReplays` | 检查当前平台是否支持回放 | `ULearningAgentsReplaySubsystem` |
| `QueryLearningAgentsReplays` | 异步查询所有可用的 replay，完成时触发 `QueryComplete` 委托，返回 `ULearningAgentsReplayList` | `UAsyncAction_LearningAgentsQueryReplays` |
| `PlayReplay` | 加载 replay 对应的地图并开始播放 | `ULearningAgentsReplaySubsystem` |
| `StopRecordingReplay` | 停止当前正在录制的 replay | `ULearningAgentsReplaySubsystem` |
| `RecordClientReplay` | 开始录制客户端 replay，提供 `APlayerController` 作为录制视角 | `ULearningAgentsReplaySubsystem` |
| `SeekInActiveReplay` | 在当前播放的 replay 中跳转到指定时间（秒） | `ULearningAgentsReplaySubsystem` |
| `GetReplayLengthInSeconds` | 获取当前 replay 的总时长 | `ULearningAgentsReplaySubsystem` |
| `GetReplayCurrentTime` | 获取当前 replay 的播放进度时间 | `ULearningAgentsReplaySubsystem` |

### 数据访问节点（通过 ULearningAgentsReplayListEntry）

| 节点 | 说明 |
|---|---|
| `GetFriendlyName` | 返回 replay 的友好名称 |
| `GetTimestamp` | 返回录制时间 |
| `GetDuration` | 返回持续时间（FTimespan） |
| `GetNumViewers` | 返回当前观看人数（仅直播） |
| `GetIsLive` | 判断是否为直播中的 replay |

### 使用示例（蓝图）

**录制 replay**：  
1. 获取 `GameInstance` → 获取 `LearningAgentsReplaySubsystem`  
2. 调用 `RecordClientReplay(PlayerController)`  
3. 游戏过程中自动录制，结束时调用 `StopRecordingReplay`  

**查询 replay 列表**：  
1. 调用 `QueryLearningAgentsReplays(PlayerController)`  
2. 节点执行时会显示 `QueryComplete` 执行引脚  
3. 连接 `QueryComplete` 事件，获取 `ULearningAgentsReplayList`  
4. 遍历 `Results` 数组，使用 `GetFriendlyName` 等节点展示信息  

**播放 replay**：  
1. 从查询结果中选择一个 `ULearningAgentsReplayListEntry`  
2. 调用 `PlayReplay(Entry)`，引擎自动加载地图并开始播放  
3. 可通过 `GetReplayCurrentTime` 更新 UI，用 `SeekInActiveReplay` 跳转  

---

## C++ 用法

### 头文件引入

```cpp
#include "LearningAgentsReplaySubsystem.h"
#include "AsyncAction_LearningAgentsQueryReplays.h"
```

### 基本用法

```cpp
// 获取 Replay Subsystem（来自 GameInstance）
ULearningAgentsReplaySubsystem* ReplaySubsystem = 
    GetWorld()->GetGameInstance()->GetSubsystem<ULearningAgentsReplaySubsystem>();

// 检查平台支持
if (ULearningAgentsReplaySubsystem::DoesPlatformSupportReplays())
{
    // 开始录制
    ReplaySubsystem->RecordClientReplay(PlayerController);
    
    // 停止录制
    ReplaySubsystem->StopRecordingReplay();
    
    // 播放指定 replay
    ULearningAgentsReplayListEntry* Entry = ...; // 从查询结果获取
    ReplaySubsystem->PlayReplay(Entry);
    
    // 跳转到第 30 秒
    ReplaySubsystem->SeekInActiveReplay(30.0f);
    
    // 获取当前进度
    float CurrentTime = ReplaySubsystem->GetReplayCurrentTime();
    float TotalLength = ReplaySubsystem->GetReplayLengthInSeconds();
}
```

### 异步查询 Replay 列表

```cpp
// 发起异步查询
UAsyncAction_LearningAgentsQueryReplays* QueryAction = 
    UAsyncAction_LearningAgentsQueryReplays::QueryLearningAgentsReplays(PlayerController);
QueryAction->QueryComplete.AddDynamic(this, &UMyClass::OnReplaysQueried);
QueryAction->Activate();

// 回调处理
void UMyClass::OnReplaysQueried(ULearningAgentsReplayList* Results)
{
    for (ULearningAgentsReplayListEntry* Entry : Results->Results)
    {
        FString Name = Entry->GetFriendlyName();
        FDateTime Timestamp = Entry->GetTimestamp();
        // ...
    }
}
```

---

## Demo 示例

以下是一个完整的最小示例，演示在游戏启动时自动查询 replay 并播放第一个。

**MyReplayDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyReplayDemo.generated.h"

UCLASS()
class UMyReplayDemo : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UFUNCTION()
    void OnReplaysQueried(ULearningAgentsReplayList* Results);
};
```

**MyReplayDemo.cpp**
```cpp
#include "MyReplayDemo.h"
#include "LearningAgentsReplaySubsystem.h"
#include "AsyncAction_LearningAgentsQueryReplays.h"

void UMyReplayDemo::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 自动发起查询
    if (APlayerController* PC = GetWorld()->GetFirstPlayerController())
    {
        UAsyncAction_LearningAgentsQueryReplays* QueryAction =
            UAsyncAction_LearningAgentsQueryReplays::QueryLearningAgentsReplays(PC);
        QueryAction->QueryComplete.AddDynamic(this, &UMyReplayDemo::OnReplaysQueried);
        QueryAction->Activate();
    }
}

void UMyReplayDemo::OnReplaysQueried(ULearningAgentsReplayList* Results)
{
    if (Results && Results->Results.Num() > 0)
    {
        ULearningAgentsReplayListEntry* FirstEntry = Results->Results[0];
        if (ULearningAgentsReplaySubsystem* ReplaySub =
            GetWorld()->GetGameInstance()->GetSubsystem<ULearningAgentsReplaySubsystem>())
        {
            ReplaySub->PlayReplay(FirstEntry);
        }
    }
}
```

---

## 模块依赖

由于 `LearningAgentsReplay` 是 Learning Agents 插件的一部分，使用该模块需要依赖其底层模块。

| 模块 | 用途 |
|---|---|
| `Learning` | 核心神经网络与训练基础算法 |
| `LearningAgents` | 智能体抽象、观察/动作编码、训练桥接 |
| `LearningAgentsTraining` | 训练循环的编辑器集成 |

注意：`LearningAgentsReplay` 内部使用了 Unreal 的 `NetworkReplayStreaming` 系统，但该依赖已隐式包含（不单独列出）。

---

## 维护状态

### 近期更新

- 2025-09-23 `e6f9d5f` — [LearningAgents] LearningAgentsRecording（添加录制功能）
- 2025-09-23 `dcf8187` — [LearningAgents] bug fix to conv1d conv2d serialization
- 2025-09-23 `86de7c7` — [LearningAgents] Missing types in ComputeObservationSchemaSubsetIndices and bugfix
- 2025-09-23 `1571e33` — LearningAgents: Ensure instead of check during GetAgent
- 2025-09-16 `f485ef5` — [LearningAgents] - schema subset bug fix

### 维护评价

该插件创建于 2025 年 9 月，属于非常新的插件。从提交记录看，功能尚在快速迭代中（添加录制功能、修复各种 bug），维护活跃。当前版本为 0.2，标记为实验性（位于 Experimental 目录，默认不启用），但 `.uplugin` 中 `IsBetaVersion=false`，表明它尚未正式发布。功能可能仍有不稳定或 API 变动，适合在开发阶段使用；对于正式项目需评估风险。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/learning-agents-in-unreal-engine/)（非官方链接，仅供参考）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents/Tests)