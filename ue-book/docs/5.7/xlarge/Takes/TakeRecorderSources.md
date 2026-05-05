# Take Recorder Sources

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器设置） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakesCore` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes) | |

---

## 用途

Take Recorder Sources 是 Take Recorder 插件的核心子模块之一，负责**定义和管理所有可用的录制数据源（Source）**。在虚拟制片工作流中，你需要从各种来源采集数据——演员的动画、摄像机切换、麦克风音频、关卡可见性状态、世界设置，甚至是录制过程中动态生成的 Actor。这个模块提供了一个统一的 Source 抽象框架，让每种数据源以插件化方式注册到 Take Recorder 系统中。

核心价值：
- **统一的录制源接口**：所有数据源继承自 `UTakeRecorderSource`，实现标准化的录制生命周期（PreRecording → StartRecording → TickRecording → StopRecording → PostRecording）
- **动态 Actor 捕获**：支持录制过程中自动检测并捕获新生成的 Actor（如附近生成的特效、动态物体）
- **录制过滤机制**：通过 `ITakeRecorderSourcesModule` 提供委托系统，允许其他模块决定哪些对象应该被录制
- **辅助工具函数**：`TakeRecorderSourceHelpers` 提供批量添加/移除 Actor 源的便捷 API

## 使用场景

- 你在做虚拟制片，需要同时录制演员表演、摄像机运动和现场音频 → 使用 Actor Source + Camera Cut Source + Microphone Audio Source
- 你需要录制一个关卡序列的播放过程并将其嵌套到新序列中 → 使用 Level Sequence Source
- 你需要自动捕获录制过程中动态生成的特效 Actor → 使用 Nearby Spawned Actor Source
- 你需要录制关卡的可见性切换状态 → 使用 Level Visibility Source
- 你需要录制当前玩家控制的角色 → 使用 Player Source
- 你需要录制整个世界的状态（包括未显式指定的 Actor）→ 使用 World Source

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddActorSources` | 批量添加 Actor 到录制源列表 | `TakeRecorderSourceHelpers` |
| `RemoveActorSources` | 从录制源列表移除指定 Actor | `TakeRecorderSourceHelpers` |
| `RemoveAllActorSources` | 清空所有 Actor 录制源 | `TakeRecorderSourceHelpers` |
| `GetSourceActor` | 获取录制源对应的 Actor | `TakeRecorderSourceHelpers` |

### 录制源属性（蓝图可读写）

**UTakeRecorderActorSource**（最常用的录制源）：

| 属性 | 类型 | 说明 |
|---|---|---|
| `Target` | `TSoftObjectPtr<AActor>` | 要录制的目标 Actor |
| `RecordType` | `ETakeRecorderActorRecordType` | 录制类型：Possessable / Spawnable / 使用项目默认值 |
| `bRecordParentHierarchy` | `bool` | 是否同时录制父级层级 |
| `bReduceKeys` | `bool` | 是否执行关键帧精简 |
| `RecordedProperties` | `UActorRecorderPropertyMap*` | 要录制的属性和组件列表 |
| `IncludeAnimationNames` | `TArray<FString>` | 仅录制匹配的动画骨骼/曲线 |
| `ExcludeAnimationNames` | `TArray<FString>` | 排除匹配的动画骨骼/曲线 |

**UTakeRecorderMicrophoneAudioSource**：

| 属性 | 类型 | 说明 |
|---|---|---|
| `AudioGain` | `float` | 录制音频的增益（dB），范围 0-40 |
| `bReplaceRecordedAudio` | `bool` | 是否用新录制的音频替换已有音频 |

**UTakeRecorderNearbySpawnedActorSource**：

| 属性 | 类型 | 说明 |
|---|---|---|
| `Proximity` | `float` | 距摄像机的触发距离（厘米），0 表示不限距离 |
| `bFilterSpawnedActors` | `bool` | 是否启用类型过滤 |
| `FilterTypes` | `TArray<TSubclassOf<AActor>>` | 要过滤的 Actor 类型列表 |

**UTakeRecorderLevelSequenceSource**：

| 属性 | 类型 | 说明 |
|---|---|---|
| `LevelSequencesToTrigger` | `TArray<ULevelSequence*>` | 录制开始时要触发播放的关卡序列列表 |

### 使用示例（蓝图描述）

**添加 Actor 到录制源**：
1. 获取 Take Recorder Sources 对象引用
2. 创建一个 `AActor` 数组，填入要录制的 Actor
3. 调用 `TakeRecorderSourceHelpers::AddActorSources`，传入 Sources 对象和 Actor 数组
4. 可选：设置 `bReduceKeys` 和 `bShowProgress` 参数

**配置麦克风录制**：
1. 在项目设置中找到 Audio Input Device 设置（`UTakeRecorderMicrophoneAudioManager`）
2. 选择要使用的音频输入设备
3. 添加 `UTakeRecorderMicrophoneAudioSource` 到录制源
4. 设置 `AudioGain`、`AudioAssetName`（支持 `{take}`、`{slate}` 等格式化占位符）

## C++ 用法

### 头文件引入

```cpp
#include "TakeRecorderSourceHelpers.h"
#include "TakeRecorderActorSource.h"
#include "TakeRecorderMicrophoneAudioSource.h"
#include "TakeRecorderNearbySpawnedActorSource.h"
#include "ITakeRecorderSourcesModule.h"
```

### 基本用法

**批量添加 Actor 到录制源**（来自 `TakeRecorderSourceHelpers`）：

```cpp
// Engine/Plugins/VirtualProduction/Takes/Source/TakeRecorderSources/Public/TakeRecorderSourceHelpers.h

#include "TakeRecorderSourceHelpers.h"

// 假设已有 UTakeRecorderSources* TakeRecorderSources
TArray<AActor*> ActorsToRecord;
ActorsToRecord.Add(MyCharacter);
ActorsToRecord.Add(MyPropActor);

// 添加到录制源，启用关键帧精简，显示进度对话框
TakeRecorderSourceHelpers::AddActorSources(
    TakeRecorderSources,
    ActorsToRecord,
    /*bReduceKeys=*/ true,
    /*bShowProgress=*/ true
);
```

**移除录制源**：

```cpp
// 移除指定 Actor
TakeRecorderSourceHelpers::RemoveActorSources(TakeRecorderSources, ActorsToRemove);

// 清空所有 Actor 录制源
TakeRecorderSourceHelpers::RemoveAllActorSources(TakeRecorderSources);
```

### 进阶用法

**注册自定义录制过滤委托**（来自 `ITakeRecorderSourcesModule`）：

```cpp
// Engine/Plugins/VirtualProduction/Takes/Source/TakeRecorderSources/Public/ITakeRecorderSourcesModule.h

#include "ITakeRecorderSourcesModule.h"

using namespace UE::TakeRecorderSources;

// 注册一个过滤委托：只有特定类型的 Actor 才被录制
if (ITakeRecorderSourcesModule::IsAvailable())
{
    ITakeRecorderSourcesModule& SourcesModule = ITakeRecorderSourcesModule::Get();
    
    SourcesModule.RegisterCanRecordDelegate(
        FName("MyCustomFilter"),
        FCanRecordDelegate::CreateLambda([](const FCanRecordArgs& Args) -> bool
        {
            // 只允许 ACharacter 类型的对象被录制
            return Args.ObjectToRecord->IsA<ACharacter>();
        })
    );
}

// 取消注册
SourcesModule.UnregisterCanRecordDelegate(FName("MyCustomFilter"));
```

> **注意**：`RegisterCanRecordDelegate` 注册的委托是**合取关系（AND）**——所有已注册的委托都必须返回 `true`，对象才会被录制。任何一个委托返回 `false` 都会阻止录制。

**配置 Actor 录制类型**：

```cpp
#include "TakeRecorderActorSource.h"

UTakeRecorderActorSource* ActorSource = NewObject<UTakeRecorderActorSource>();

// 设置目标 Actor
ActorSource->Target = MyActor;

// 设置录制类型
ActorSource->RecordType = ETakeRecorderActorRecordType::Possessable;  // 作为 Possessable 录制
// ActorSource->RecordType = ETakeRecorderActorRecordType::Spawnable;  // 作为 Spawnable 录制

// 同时录制父级层级（确保变换数据正确）
ActorSource->bRecordParentHierarchy = true;

// 启用关键帧精简以减小序列文件大小
ActorSource->bReduceKeys = true;

// 配置动画录制过滤
ActorSource->IncludeAnimationNames.Add(TEXT("spine_01"));
ActorSource->IncludeAnimationNames.Add(TEXT("head"));
```

## Demo 示例

### 自定义录制源过滤器

```cpp
// MyRecordingFilter.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "ITakeRecorderSourcesModule.h"
#include "MyRecordingFilter.generated.h"

UCLASS()
class UMyRecordingFilterSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    static bool ShouldRecordObject(const UE::TakeRecorderSources::FCanRecordArgs& Args);
};
```

```cpp
// MyRecordingFilter.cpp
#include "MyRecordingFilter.h"
#include "ITakeRecorderSourcesModule.h"

void UMyRecordingFilterSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    if (UE::TakeRecorderSources::ITakeRecorderSourcesModule::IsAvailable())
    {
        auto& Module = UE::TakeRecorderSources::ITakeRecorderSourcesModule::Get();
        Module.RegisterCanRecordDelegate(
            FName("MyGameFilter"),
            UE::TakeRecorderSources::FCanRecordDelegate::CreateStatic(&UMyRecordingFilterSubsystem::ShouldRecordObject)
        );
    }
}

void UMyRecordingFilterSubsystem::Deinitialize()
{
    if (UE::TakeRecorderSources::ITakeRecorderSourcesModule::IsAvailable())
    {
        auto& Module = UE::TakeRecorderSources::ITakeRecorderSourcesModule::Get();
        Module.UnregisterCanRecordDelegate(FName("MyGameFilter"));
    }

    Super::Deinitialize();
}

bool UMyRecordingFilterSubsystem::ShouldRecordObject(const UE::TakeRecorderSources::FCanRecordArgs& Args)
{
    // 示例：排除所有标记为 "NoRecord" 的 Actor
    if (AActor* Actor = Cast<AActor>(Args.ObjectToRecord))
    {
        return !Actor->ActorHasTag(FName("NoRecord"));
    }
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TakesCore` | Take Recorder 核心数据类型和基础接口 |
| `TakeMovieScene` | MovieScene 扩展，处理 Take 相关的轨道和区段 |
| `TakeTrackRecorders` | 各种属性/组件的轨道录制器实现 |

## 维护状态

### 近期更新

```
- 40d1e23480b9 TakeRecorder: Make Take Recorder Source types public. Sources that weren't already exported now are. This is for consistency since all sources were previously exposed to blueprints.
- c2b5d90f4bbf Allow take recorder microphone sources to work in -game.
- 34cfb07a77a5 Take Recorder: Add a cvar TakeRecorder.AllowPossessablePIEObjects to bypass disallowing recording PIE objects as possessables. The default is to not allow this (no change in behavior)
```

- `40d1e23`：将所有 Source 类型的 API 标记为公开导出，确保蓝图和外部模块的一致性访问
- `c2b5d90`：修复麦克风录制源在 `-game` 模式（独立进程运行）下的兼容性
- `34cfb07`：新增 CVar 控制是否允许将 PIE（Play In Editor）对象录制为 Possessable，默认不允许

### 维护评价

Take Recorder Sources 作为虚拟制片核心工具链的一部分，由 Epic Games 持续维护。该模块创建于 2019 年，至今约 6 年历史，属于成熟稳定的功能模块。近期更新集中在 API 可见性规范化、运行时兼容性修复和录制行为控制等方面，表明该模块处于**活跃维护**状态。

作为 Virtual Production 工作流的基础设施，该模块在影视和虚拟制片领域被广泛使用，推荐在相关项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes/Source/TakeRecorderSources)
- [官方文档](https://docs.unrealengine.com/en-US/AnimatingObjects/Sequencer/RecordingAndPlayingBack/TakeRecorder/)