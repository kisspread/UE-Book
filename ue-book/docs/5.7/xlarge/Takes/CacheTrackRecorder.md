# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板等） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakesCore` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Takes 插件是 Unreal Engine 虚拟制作工作流的核心组件，提供了一套完整的“拍摄”（Take）管理解决方案。它不仅仅是一个录制工具，更是一个围绕“Take”概念构建的生态系统，用于在虚拟制片（Virtual Production）环境中捕获、组织、审查和回放各种数据。

其核心解决的问题是：在复杂的虚拟制片现场（如使用LED墙、动作捕捉、实时渲染），需要精确同步并记录来自多个来源（摄像机、演员、灯光、特效、Live Link数据等）的实时数据，以便后期进行回放、审查和合成。该插件通过与 Sequencer 深度集成，将录制的数据以标准化的 Sequencer 轨道形式存储，便于后续编辑和复用。

## 使用场景

- **虚拟制片现场录制**：在LED墙前拍摄时，同步录制摄像机运动、演员表演、实时渲染画面及所有相关参数，生成一个完整的“Take”。
- **实时数据缓存与回放**：需要精确帧数据的场景（如Niagara粒子系统、复杂材质动画），使用 `CacheTrackRecorder` 模块进行高精度录制，确保回放时数据完全一致。
- **多源数据同步录制**：同时录制来自Live Link（动作捕捉、面部捕捉）、多个虚拟摄像机、音频等不同来源的数据，并将它们对齐到同一个时间线上。
- **拍摄管理与审查**：通过Take Recorder面板管理大量的拍摄记录（Slate、Take编号），快速切换、比较和审查不同的拍摄版本。
- **自动化测试与数据生成**：在编辑器中录制游戏过程或特定序列，用于生成测试数据或创建预渲染的过场动画。

## 蓝图用法

Takes 插件主要通过编辑器UI（Take Recorder面板）和C++ API进行交互，其蓝图暴露的接口相对有限，主要集中在状态查询和基础控制上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Take Recorder State` | 获取当前Take Recorder的录制状态（空闲、录制中、准备中等）。 | `UTakeRecorderBlueprintLibrary` |
| `Start Recording` | 通过蓝图启动一次Take录制。 | `UTakeRecorderBlueprintLibrary` |
| `Stop Recording` | 通过蓝图停止当前正在进行的Take录制。 | `UTakeRecorderBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **查询状态**：在蓝图中，可以使用 `Get Take Recorder State` 节点来检查当前是否正在录制，从而决定是否触发其他逻辑（例如，在录制开始时显示一个UI提示）。
2.  **触发录制**：虽然通常通过UI按钮触发，但也可以通过蓝图调用 `Start Recording` 节点来程序化地开始一次录制。这可以用于自动化流程，例如在特定游戏事件发生时自动开始录制。

## C++ 用法

Takes 插件的真正强大功能通过其 C++ API 暴露，允许开发者深度定制录制行为、添加自定义录制源和轨道。

### 头文件引入

```cpp
#include "TakesCore.h"
#include "TakeRecorder.h"
#include "CacheTrackRecorder.h"
```

### 基本用法

以下示例展示了如何配置并启动一次基于缓存的录制，适用于需要高精度帧数据的场景。

```cpp
// 来源: Engine/Plugins/VirtualProduction/Takes/Source/CacheTrackRecorder/Public/Recorder/CacheTrackRecorder.h
// 配置缓存录制器参数
FCacheRecorderParameters RecorderParams;
RecorderParams.User.bMaximizeViewport = true; // 录制时最大化视口
RecorderParams.User.EngineTimeDilation = 1.0f; // 正常时间流速
RecorderParams.Project.DefaultSlate = TEXT(“MySequence”); // 设置默认Slate名称
RecorderParams.Project.bCacheTrackRecorderControlsClockTime = true; // 让录制器控制时钟，确保帧精度
RecorderParams.Project.bStartAtCurrentTimecode = false; // 从0开始，而非当前时间码
RecorderParams.Project.bRecordTimecode = true; // 在轨道中记录时间码

// 获取缓存录制器单例并开始录制
if (ICacheTrackRecorderModule* CacheRecorderModule = FModuleManager::GetModulePtr<ICacheTrackRecorderModule>(“CacheTrackRecorder”))
{
    CacheRecorderModule->StartRecording(RecorderParams);
}
```

### 进阶用法

结合 `TakesCore` 模块，可以监听录制事件并做出响应。

```cpp
// 来源: Engine/Plugins/VirtualProduction/Takes/Source/TakesCore/
#include “TakesCoreDelegates.h”

// 绑定到录制开始和结束的委托
FTakesCoreDelegates::OnTakeRecordingStarted.AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT(“Take recording has started!”));
    // 在这里可以开始记录自定义数据或准备UI
});

FTakesCoreDelegates::OnTakeRecordingStopped.AddLambda([](bool bWasCancelled)
{
    if (!bWasCancelled)
    {
        UE_LOG(LogTemp, Log, TEXT(“Take recording completed successfully.”));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT(“Take recording was cancelled.”));
    }
});
```

## Demo 示例

一个最小的自定义录制器模块示例，演示如何创建一个简单的录制器来记录Actor的位置。

**MySimpleRecorder.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “MovieSceneTrackRecorder.h”
#include “MySimpleRecorder.generated.h”

UCLASS()
class UMySimpleRecorder : public UMovieSceneTrackRecorder
{
    GENERATED_BODY()

public:
    // 初始化录制器，绑定到特定的Actor
    virtual void CreateTrack UObject* InObjectToRecord, UMovieScene* InMovieScene, const FGuid& InGuid) override;

    // 每一帧记录数据
    virtual void RecordSampleImpl(const FQualifiedFrameTime& CurrentTime) override;

    // 停止录制并清理
    virtual void FinalizeTrack() override;

private:
    UPROPERTY()
    TWeakObjectPtr<AActor> TargetActor;

    UPROPERTY()
    UMovieScene3DTransformTrack* TransformTrack;
};
```

**MySimpleRecorder.cpp**
```cpp
#include “MySimpleRecorder.h”
#include “MovieScene.h”
#include “Sections/MovieScene3DTransformSection.h”
#include “Tracks/MovieScene3DTransformTrack.h”

void UMySimpleRecorder::CreateTrack UObject* InObjectToRecord, UMovieScene* InMovieScene, const FGuid& InGuid)
{
    Super::CreateTrack(InObjectToRecord, InMovieScene, InGuid);

    TargetActor = Cast<AActor>(InObjectToRecord);
    if (TargetActor.IsValid() && InMovieScene)
    {
        // 为这个Actor创建或找到3D变换轨道
        TransformTrack = InMovieScene->FindTrack<UMovieScene3DTransformTrack>(InGuid);
        if (!TransformTrack)
        {
            TransformTrack = InMovieScene->AddTrack<UMovieScene3DTransformTrack>(InGuid);
        }
    }
}

void UMySimpleRecorder::RecordSampleImpl(const FQualifiedFrameTime& CurrentTime)
{
    if (TargetActor.IsValid() && TransformTrack)
    {
        FTransform ActorTransform = TargetActor->GetActorTransform();
        // 将当前变换数据添加到轨道的区段中
        // (具体实现涉及操作UMovieScene3DTransformSection，此处为示意)
    }
}

void UMySimpleRecorder::FinalizeTrack()
{
    // 清理工作，例如确保所有区段都已正确闭合
    TargetActor.Reset();
    TransformTrack = nullptr;
}
```

## 模块依赖

要使用 `CacheTrackRecorder` 模块，你的模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer的核心模块，提供轨道、区段等基础类。 |
| `SequencerCore` | Sequencer的核心功能，如评估器、时钟。 |
| `TakesCore` | Takes插件的核心模块，提供录制器接口和基础功能。 |
| `LevelSequence` | 用于操作关卡序列资产。 |

## 维护状态

### 近期更新

- 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
  *解读：代码维护性更新，确保API导出符号正确，属于基础设施改进。*
- 936a68f6753c Fixed a bug where recording a cache didn't work when the editor window lost focus
  *解读：修复了一个重要Bug，即编辑器窗口失焦时缓存录制失败的问题。*
- 43ca5776e963 Reset sequencer speed when recording a cache and it’s in reverse mode
  *解读：修复了在反向播放模式下录制缓存时，序列器速度未重置的问题。*

### 维护评价

Takes 插件是 Unreal Engine 虚拟制作功能的核心支柱之一，自2019年创建以来持续得到维护和更新。从近期的提交记录看，它仍在**活跃维护**中，最近的更新集中在修复影响工作流的关键Bug和进行代码质量改进。作为虚拟制作管线中不可或缺的一环，Epic Games 有强烈的动机保持其稳定性和功能性。

**推荐使用**。对于任何涉及虚拟制片、实时渲染数据录制或需要复杂拍摄管理的项目，Takes 插件都是首选方案。尽管它是一个“老古董”级别的插件，但其持续的维护和在行业中的广泛应用证明了其价值和可靠性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/take-recorder-in-unreal-engine/) (UE5 官方文档链接，.uplugin中未提供)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes/Tests) (如果存在)