# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、预设、配置） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakesCore` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Takes 插件是 Unreal Engine 虚拟制作 (Virtual Production) 工作流的核心组件。它不仅仅是一个简单的录制工具，而是一个完整的**拍摄管理系统**。其核心功能是解决在虚拟制片（如 LED 墙拍摄）环境中，需要**同步录制、管理和回放来自多个异构数据源（如摄像机、演员动作捕捉、音频、灯光等）的复杂数据**的问题。

该插件通过 `UTakeRecorderSource` 的抽象基类，允许开发者扩展自定义的录制源。它管理整个录制生命周期，包括预录制准备、逐帧录制、停止录制以及后期处理。录制的数据被组织成带有丰富元数据（如 Slate、Take Number、时间码）的 `ULevelSequence` 资产，便于后期检索、审查和编辑。它解决了虚拟制片中数据同步、版本管理和工作流集成的核心挑战。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙前拍摄时，需要同步录制摄像机跟踪数据、演员表演、虚拟场景状态、音频等。
- **动作捕捉 (Motion Capture)**：录制来自专业动捕设备或 iPhone ARKit 的面部/身体动画数据。
- **多机位拍摄**：管理来自多个虚拟或物理摄像机的录制，并确保它们的时间码同步。
- **自动化测试与回放**：录制游戏内的特定场景或玩家输入，用于自动化测试或创建可重复的演示序列。
- **后期制作审查**：利用丰富的元数据（Slate、描述、时间码）对大量拍摄素材进行组织、筛选和审查。

## 蓝图用法

蓝图 API 主要集中在 `UTakesCoreBlueprintLibrary`、`UTakeRecorderSources` 和 `UTakeMetaData` 等类中，用于查询、管理和配置拍摄。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Compute Next Take Number` | 计算指定 Slate 下一个可用的 Take 编号。 | `UTakesCoreBlueprintLibrary` |
| `Find Takes` | 根据 Slate 和可选的 Take Number 查找所有已录制的拍摄资产。 | `UTakesCoreBlueprintLibrary` |
| `Add Source` | 向当前拍摄的录制源列表中添加一个新的录制源（如 Actor、音频等）。 | `UTakeRecorderSources` |
| `Remove Source` | 从录制源列表中移除一个指定的录制源。 | `UTakeRecorderSources` |
| `Get Sources (Copy)` | 获取当前所有录制源的副本（蓝图安全）。 | `UTakeRecorderSources` |
| `Is Locked` | 检查当前拍摄是否被锁定（防止意外修改）。 | `UTakeMetaData` |
| `Set On Take Recorder Slate Changed` | 设置一个委托，当 Slate 名称改变时触发。 | `UTakesCoreBlueprintLibrary` |
| `Set On Take Recorder Take Number Changed` | 设置一个委托，当 Take 编号改变时触发。 | `UTakesCoreBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **查询下一个 Take 编号**：
    - 创建一个 `Compute Next Take Number` 节点。
    - 将 Slate 字符串（例如 “MyScene_Shot01”）连接到其输入。
    - 输出引脚将返回一个整数，表示下一个可用的 Take 编号（例如 3）。

2.  **动态添加录制源**：
    - 在开始录制前，使用 `Add Source` 节点。
    - 通过 `InSourceType` 引脚指定要添加的源类型（例如 `ULevelSequenceRecordingSource`）。
    - 返回的 `UTakeRecorderSource` 对象可以进一步配置（如设置 `bEnabled`）。

3.  **监听 Slate 变化**：
    - 使用 `Set On Take Recorder Slate Changed` 节点。
    - 创建一个自定义事件（例如 `OnSlateChanged`），其参数为 `Slate (String)`。
    - 将该事件连接到委托输入。当 Take Recorder UI 中的 Slate 改变时，你的事件将被调用。

## C++ 用法

C++ 用法主要围绕配置和扩展录制源、访问元数据以及使用工具函数。

### 头文件引入

```cpp
// 核心蓝图库和工具
#include "TakesCoreBlueprintLibrary.h"
#include "TakesUtils.h"

// 录制源管理
#include "TakeRecorderSources.h"
#include "TakeRecorderSource.h"

// 元数据
#include "TakeMetaData.h"
#include "TakePreset.h"

// 命名令牌上下文（用于高级路径/名称生成）
#include "NamingTokens/TakeRecorderNamingTokensContext.h"
```

### 基本用法

**1. 计算下一个 Take 编号**
```cpp
// 来源: Engine/Plugins/VirtualProduction/Takes/Source/TakesCore/Public/TakesCoreBlueprintLibrary.h
FString CurrentSlate = TEXT("MyProject_Scene01");
int32 NextTake = UTakesCoreBlueprintLibrary::ComputeNextTakeNumber(CurrentSlate);
UE_LOG(LogTakesCore, Log, TEXT("Next available take for slate '%s' is: %d"), *CurrentSlate, NextTake);
```

**2. 查找已录制的拍摄资产**
```cpp
// 来源: Engine/Plugins/VirtualProduction/Takes/Source/TakesCore/Public/TakesCoreBlueprintLibrary.h
FString SlateToFind = TEXT("MyProject_Scene01");
TArray<FAssetData> FoundTakes = UTakesCoreBlueprintLibrary::FindTakes(SlateToFind, 0); // 0 表示查找所有 Take
for (const FAssetData& TakeAsset : FoundTakes)
{
    UE_LOG(LogTakesCore, Log, TEXT("Found take asset: %s"), *TakeAsset.AssetName.ToString());
}
```

**3. 以编程方式管理录制源**
```cpp
// 假设你有一个 UTakeRecorderSources* Sources 对象（通常从 UTakeMetaData 获取）
// 来源: Engine/Plugins/VirtualProduction/Takes/Source/TakesCore/Public/TakeRecorderSources.h
if (UTakeRecorderSources* Sources = /* ... */)
{
    // 添加一个 Actor 录制源
    UTakeRecorderSource* NewSource = Sources->AddSource(UActorRecordingSource::StaticClass());
    if (NewSource)
    {
        NewSource->bEnabled = true;
        // 配置源的具体属性...
    }

    // 获取所有源的列表
    TArrayView<UTakeRecorderSource* const> AllSources = Sources->GetSources();
    for (UTakeRecorderSource* Source : AllSources)
    {
        UE_LOG(LogTakesCore, Log, TEXT("Source: %s, Enabled: %s"), *Source->GetName(), Source->bEnabled ? TEXT("True") : TEXT("False"));
    }
}
```

### 进阶用法

**1. 创建和使用拍摄预设 (Take Preset)**
```cpp
// 来源: Engine/Plugins/VirtualProduction/Takes/Source/TakesCore/Public/TakePreset.h
// 创建一个临时的拍摄预设，用于本次录制会话
UTakePreset* TransientPreset = UTakePreset::AllocateTransientPreset(nullptr); // nullptr 表示不基于模板
if (TransientPreset)
{
    // 获取或创建预设中的关卡序列模板
    ULevelSequence* TemplateSequence = TransientPreset->GetOrCreateLevelSequence();
    // 可以对 TemplateSequence 进行预配置，例如添加默认轨道
    // ...
}
```

**2. 处理录制的时间码数据**
```cpp
// 来源: Engine/Plugins/VirtualProduction/Takes/Source/TakesCore/Public/TakeRecorderTimeProcessing.h
// 假设你有一系列录制的时间对 (记录帧, 对应的时间码)
UE::TakesCore::FArrayOfRecordedTimePairs RecordedTimes;
// ... 填充 RecordedTimes 数据 ...

// 将时间码数据处理并写入到拍摄序列的 Take Track 中
if (ULevelSequence* Sequence = /* ... */)
{
    UMovieSceneTakeTrack* TakeTrack = Sequence->GetMovieScene()->FindTrack<UMovieSceneTakeTrack>();
    if (TakeTrack)
    {
        UE::TakesCore::ProcessRecordedTimes(Sequence, TakeTrack, TRange<FFrameNumber>(), RecordedTimes);
    }
}
```

**3. 使用命名令牌上下文进行动态命名**
```cpp
// 来源: Engine/Plugins/VirtualProduction/Takes/Source/TakesCore/Public/NamingTokens/TakeRecorderNamingTokensContext.h
// 在录制源或相关逻辑中，创建上下文以供命名令牌系统使用
UTakeRecorderNamingTokensContext* NamingContext = NewObject<UTakeRecorderNamingTokensContext>();
NamingContext->TakeMetaData = CurrentTakeMetaData; // 关联当前拍摄的元数据
NamingContext->Actor = TargetActor; // 关联特定的 Actor
NamingContext->AudioInputDeviceChannel = 2; // 设置音频通道

// 这个上下文对象可以被传递给支持命名令牌的系统，用于动态生成资产路径或名称。
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何通过代码设置并启动一次拍摄录制。

**MyTakeRecorderActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTakeRecorderActor.generated.h"

class UTakeRecorderSources;
class UTakeMetaData;

UCLASS()
class AMyTakeRecorderActor : public AActor
{
    GENERATED_BODY()

public:
    AMyTakeRecorderActor();

    UFUNCTION(BlueprintCallable, Category = "Take Recorder")
    void StartRecording();

    UFUNCTION(BlueprintCallable, Category = "Take Recorder")
    void StopRecording();

private:
    UPROPERTY()
    TObjectPtr<UTakeRecorderSources> RecordingSources;

    UPROPERTY()
    TObjectPtr<UTakeMetaData> CurrentMetaData;

    bool bIsRecording = false;
};
```

**MyTakeRecorderActor.cpp**
```cpp
#include "MyTakeRecorderActor.h"
#include "TakeRecorderSources.h"
#include "TakeMetaData.h"
#include "TakesCoreBlueprintLibrary.h"
#include "TakeRecorderSource.h" // 用于 UTakeRecorderSource 基类

AMyTakeRecorderActor::AMyTakeRecorderActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTakeRecorderActor::StartRecording()
{
    if (bIsRecording) return;

    // 1. 创建录制源管理器
    RecordingSources = NewObject<UTakeRecorderSources>(GetTransientPackage());

    // 2. 添加一个录制源（示例：录制自身 Actor）
    // 注意：实际项目中可能需要使用更具体的源类型，如 UActorRecordingSource
    UTakeRecorderSource* ActorSource = RecordingSources->AddSource(UTakeRecorderSource::StaticClass());
    if (ActorSource)
    {
        ActorSource->bEnabled = true;
        // 这里可以进一步配置源，例如指定要录制的 Actor
    }

    // 3. 创建或获取拍摄元数据
    CurrentMetaData = UTakeMetaData::CreateFromDefaults(GetTransientPackage(), FName("MyRecording"));
    if (CurrentMetaData)
    {
        CurrentMetaData->SetSlate(TEXT("DemoSlate"));
        CurrentMetaData->SetTakeNumber(UTakesCoreBlueprintLibrary::ComputeNextTakeNumber(TEXT("DemoSlate")));
        CurrentMetaData->SetDescription(TEXT("Programmatic recording demo"));
    }

    // 4. 启动录制 (简化示意，实际需要调用 TakeRecorder 模块的接口)
    // ITakeRecorderModule::Get().StartRecording(RecordingSources, CurrentMetaData, ...);
    bIsRecording = true;
    UE_LOG(LogTemp, Log, TEXT("Take Recording Started. Slate: %s, Take: %d"),
        *CurrentMetaData->GetSlate(), CurrentMetaData->GetTakeNumber());
}

void AMyTakeRecorderActor::StopRecording()
{
    if (!bIsRecording) return;

    // 停止录制 (简化示意)
    // ITakeRecorderModule::Get().StopRecording();
    bIsRecording = false;

    // 保存录制结果（通常由 Take Recorder 自动处理）
    if (CurrentMetaData)
    {
        UE_LOG(LogTemp, Log, TEXT("Take Recording Stopped. Asset should be saved at: %s"),
            *CurrentMetaData->GetPackage()->GetName());
    }

    // 清理
    RecordingSources = nullptr;
    CurrentMetaData = nullptr;
}
```

## 模块依赖

从各模块的 `Build.cs` 分析，Takes 插件依赖于 UE 的序列器 (Sequencer) 和资产管理系统。以下是该插件**独特**的依赖项：

| 模块 | 用途 |
|---|---|
| `MovieScene` | 核心序列器框架，用于创建和操作电影场景轨道。 |
| `LevelSequence` | 关卡序列资产类型，是录制数据的主要载体。 |
| `Sequencer` | 编辑器中的序列器 UI 和交互逻辑。 |
| `TakeRecorder` | 插件自身的录制器运行时逻辑。 |
| `TakeMovieScene` | 处理与拍摄相关的电影场景扩展。 |
| `NamingTokens` | 提供动态命名令牌系统，用于生成资产路径和名称。 |

## 维护状态

### 近期更新

```
- dda1e95b930d [Backout] - CL46059773 [FYI] jason.walter #rnx Original CL Desc ----------------------------------------------------------------- Check for external references before save.
- d49215a6e55c Check for external references before save.
- 22d431123734 Turn on error reporting with save package.
```
*解读：最近的提交集中在改进资产保存的健壮性，特别是检查外部引用和错误报告。这表明插件仍在积极维护，以提升稳定性和用户体验。*

### 维护评价

- **创建时间**：2019年，是 UE4 时代为虚拟制作引入的重要插件。
- **最近更新**：2025年仍有实质性提交（资产保存改进），表明处于**活跃维护**状态。
- **功能状态**：作为 Epic 官方虚拟制作工具链的核心部分，功能稳定且持续迭代。
- **已知限制**：作为大型复杂系统，自定义扩展（如新的录制源）需要深入理解其架构。
- **推荐使用**：**强烈推荐**用于任何涉及虚拟制片、动作捕捉或多源数据同步录制的项目。它是 UE 虚拟制作工作流的基石。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/take-recorder-in-unreal-engine/) (通用文档链接，非 .uplugin 提供)