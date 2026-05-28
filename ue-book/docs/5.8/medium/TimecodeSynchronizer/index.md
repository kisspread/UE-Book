# Timecode Synchronizer (Deprecated)

> This plugin has been deprecated and will be removed in a future engine version. Please update your project to use the features of the TimedDataMonitor plugin instead.
> An asset that will become the TimecodeProvider once all the inputs get synchronized to a timecode.

| 属性 | 值 |
|---|---|
| 中文名 | 时间码同步器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TimecodeSynchronizer` (Runtime), `TimecodeSynchronizerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-14 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TimecodeSynchronizer) | |

## 用途
**此插件已被官方废弃，将不再维护，并将在未来的引擎版本中移除。请勿在新项目中使用。**

该插件最初设计用于虚拟制作（Virtual Production）场景，旨在通过整合多个输入源（如音频、视频设备）的时间码，同步它们的时序，并最终提供一个统一的 `TimecodeProvider`。它的核心目的是确保虚拟制作中不同媒体流（如摄像机、录制设备、音频）的时间基准一致。根据官方建议，其功能已被新的 `TimedDataMonitor` 插件取代。

## 使用场景
鉴于插件已废弃，**不建议在任何新场景中使用**。如果必须在旧项目中维护：
- 你在维护一个基于旧版虚幻引擎的虚拟制作管线，并且该管线依赖此插件进行多设备时间码同步。
- 你需要理解其遗留代码以进行迁移或问题排查。

对于新项目，应直接使用 **TimedDataMonitor** 插件来实现媒体输入的时间码管理和同步。

## 蓝图用法
**注意：由于插件已废弃，以下API可能在未来版本中被移除。**

该插件主要提供 `UTimecodeSynchronizer` 资产，可在蓝图中创建和配置。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create` | 创建一个新的 `UTimecodeSynchronizer` 资产实例。 | `UTimecodeSynchronizer` |
| `Start` | 启动时间码同步过程，开始监听和同步配置的输入源。 | `UTimecodeSynchronizer` |
| `Stop` | 停止时间码同步。 | `UTimecodeSynchronizer` |
| `GetSynchronizedTimecode` | 获取当前已同步的时间码值。 | `UTimecodeSynchronizer` |

### 使用示例（蓝图描述）
1. 在蓝图中使用 `Create` 节点生成一个 `UTimecodeSynchronizer` 对象。
2. 通过其属性面板或 `Set` 节点，配置需要同步的输入源（如音频时间码、媒体播放器）。
3. 调用 `Start` 节点开始同步。
4. 在需要获取统一时间码的地方，调用 `GetSynchronizedTimecode` 节点。
5. 应用结束时调用 `Stop` 节点。

## C++ 用法
**重要警告：此插件已废弃，其API和类名可能在未来版本中更改或删除。以下代码仅用于理解遗留代码或紧急维护。**

### 头文件引入
```cpp
#include “TimecodeSynchronizer.h”
```

### 基本用法
以下代码片段展示了如何以编程方式创建和控制一个 `UTimecodeSynchronizer`。
```cpp
// 假设你已经有一个对象（例如 GameInstance）拥有一个成员变量
// UTimecodeSynchronizer* TimecodeSynchronizerAsset;

// 创建资产实例
TimecodeSynchronizerAsset = NewObject<UTimecodeSynchronizer>(GetTransientPackage());

// 配置输入源 (示例)
// TimecodeSynchronizerAsset->AddTimecodeProvider( SomeTimecodeProvider );

// 启动同步
TimecodeSynchronizerAsset->Start();

// 在游戏循环或需要的时候获取同步时间码
FTimecode SynchronizedTimecode = TimecodeSynchronizerAsset->GetSynchronizedTimecode();
if (SynchronizedTimecode.IsValid())
{
    UE_LOG(LogTemp, Log, TEXT(“Synchronized Timecode: %s”), *SynchronizedTimecode.ToString());
}

// 停止同步
TimecodeSynchronizerAsset->Stop();
```

## Demo 示例
一个最小的 C++ 示例，展示如何在 Actor 中使用（仅供理解）。
**TimecodeSyncActor.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once
#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “TimecodeSynchronizer.h”
#include “TimecodeSyncActor.generated.h”

UCLASS()
class ATimecodeSyncActor : public AActor
{
    GENERATED_BODY()

public:
    ATimecodeSyncActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    UTimecodeSynchronizer* TimecodeSync;

    void LogCurrentTimecode();
};
```
**TimecodeSyncActor.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include “TimecodeSyncActor.h”
#include “Engine/World.h”

ATimecodeSyncActor::ATimecodeSyncActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ATimecodeSyncActor::BeginPlay()
{
    Super::BeginPlay();
    TimecodeSync = NewObject<UTimecodeSynchronizer>(this);
    // 这里需要添加实际的 TimecodeProvider，否则无法工作
    // TimecodeSync->AddTimecodeProvider(...)
    TimecodeSync->Start();
}

void ATimecodeSyncActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (TimecodeSync)
    {
        TimecodeSync->Stop();
    }
    Super::EndPlay(EndPlayReason);
}

void ATimecodeSyncActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    LogCurrentTimecode();
}

void ATimecodeSyncActor::LogCurrentTimecode()
{
    if (TimecodeSync)
    {
        FTimecode CurrentTC = TimecodeSync->GetSynchronizedTimecode();
        if (CurrentTC.IsValid())
        {
            UE_LOG(LogTemp, Verbose, TEXT(“Current Synced Timecode: %s”), *CurrentTC.ToString());
        }
    }
}
```

## 模块依赖
从源码的 Build.cs 文件推断，此插件依赖以下模块：
| 模块 | 用途 |
|---|---|
| `Media` | 核心媒体框架，用于处理媒体播放器等。 |
| `MediaUtils` | 媒体工具函数。 |
| `MediaAssets` | 媒体资产（如媒体播放器）的核心定义。 |
| `TimeManagement` | 时间管理和时间码相关功能。 |
| `Slate`, `SlateCore` | 用于编辑器界面。 |
| `UMG` | 用于编辑器界面。 |
| `LevelSequence` | 用于与 Sequencer 的时间码进行交互。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志宏迁移到新的UE_LOGF格式。 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini. | 将配置文件命名从Base<Plugin>.ini重命名为Default<Plugin>.ini。 |
| 2025-06-13 | `b3edcb21` | Replace some usages of FORCEINLINE with inline in MovieScene modules. | 在MovieScene模块中将部分FORCEINLINE替换为inline。 |
| 2023-11-29 | `c98c8912` | Fix C4702 warnings. | 修复C4702编译器警告（不可达代码）。 |
| 2023-02-18 | `e599d19e` | Removing redundant Private includes. | 移除多余的私有头文件包含。 |

### 维护评价
**⚠️ 已废弃（Deprecated）**
- **创建时间**：2018年5月，插件历史较长。
- **维护状态**：自2023年起，所有提交均为**维护性、编译性修复**（如修正警告、迁移日志宏、重命名配置文件），**没有任何功能性更新**。这表明插件已处于“冻结”状态，仅确保能在新引擎版本中编译通过。
- **官方状态**：`.uplugin` 文件明确标记为已废弃 (`FriendlyName` 含 Deprecated)，并给出了明确的替代方案 `TimedDataMonitor`。
- **结论**：**强烈不推荐在任何新项目中使用此插件**。它仅为维护旧项目兼容性而存在。其核心功能已转移至 `TimedDataMonitor` 插件，应优先考虑使用后者。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TimecodeSynchronizer)
- 官方文档：无 (DocsURL 为空)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TimecodeSynchronizer/Tests) (如果存在)