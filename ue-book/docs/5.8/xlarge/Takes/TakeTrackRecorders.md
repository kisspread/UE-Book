# Take Track Recorders

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 中文名 | 轨道录制器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、命名令牌） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderEditor` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime), `TakesCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Take Track Recorders 是 Take Recorder 系统的核心录制引擎模块。它为虚拟制片环境中的"Take（拍摄条次）"录制提供了统一的轨道录制框架。该模块包含一组针对不同数据类型的专用录制器（Track Recorder），能够在运行时将场景中的 Actor 变换、动画、属性变化、粒子触发、可见性状态、附件关系等信息录制到 Sequencer 的轨道中。

**核心解决的问题：** 在虚拟制片中，导演需要反复拍摄同一场景的多个版本（take），然后从中挑选最佳版本。手动记录这些 take 的动画和状态数据极其繁琐。本模块通过工厂模式和模板化的属性录制器，自动化了整个录制过程，将实时场景数据直接写入 Sequencer 关键帧，支持后续在编辑器中回放、对比和编辑。

## 使用场景

- **虚拟制片中录制 Actor 动画** → 使用 `UMovieSceneAnimationTrackRecorder` 捕获骨骼网格体动画并保存为 `UAnimSequence` 资产
- **录制场景中物体的位置/旋转/缩放变化** → 使用 `UMovieScene3DTransformTrackRecorder` 将变换关键帧写入 Sequencer
- **录制任意 UObject 属性变化** → 使用 `FMovieSceneTrackPropertyRecorder<T>` 模板或 `UMovieScenePropertyTrackRecorder`
- **录制 Actor 生成/销毁事件** → 使用 `UMovieSceneSpawnTrackRecorder`
- **录制粒子系统触发事件** → 使用 `UMovieSceneParticleTrackRecorder`
- **录制物体可见性切换** → 使用 `UMovieSceneVisibilityTrackRecorder`
- **录制 Actor 之间的附件关系变化** → 使用 `UMovieScene3DAttachTrackRecorder`
- **录制 Actor 引用属性** → 使用 `UMovieSceneActorReferenceTrackRecorder`
- **需要自定义录制器扩展** → 实现 `IMovieSceneTrackRecorderFactory` 接口并注册为模块特性

## 蓝图用法

本模块主要面向 C++ 层，大部分核心类（`UMovieSceneTrackRecorder`、`IMovieSceneTrackRecorderFactory` 等）标记为 `BlueprintType` 但主要是为了反射系统支持。真正的蓝图交互由上层 `TakeRecorder` 和 `TakeRecorderEditor` 模块提供。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateTrack` | 初始化录制轨道，创建 Sequencer Section | `UMovieSceneTrackRecorder` |
| `RecordSample` | 录制一帧采样数据 | `UMovieSceneTrackRecorder` |
| `StopRecording` | 停止录制 | `UMovieSceneTrackRecorder` |
| `FinalizeTrack` | 完成录制后后处理（精简关键帧、移除冗余轨道） | `UMovieSceneTrackRecorder` |
| `CancelTrack` | 取消录制并清理 | `UMovieSceneTrackRecorder` |
| `SetSavedRecordingDirectory` | 设置录制数据保存目录 | `UMovieSceneTrackRecorder` |
| `LoadRecordedFile` | 加载已录制的文件并创建 Sequencer Section | `UMovieSceneTrackRecorder` |
| `ShouldContinueRecording` | 判断是否应继续录制 | `UMovieSceneTrackRecorder` |

## C++ 用法

### 头文件引入

```cpp
#include "TrackRecorders/MovieSceneTrackRecorder.h"
#include "TrackRecorders/MovieScene3DTransformTrackRecorder.h"
#include "TrackRecorders/MovieSceneAnimationTrackRecorder.h"
#include "TrackRecorders/MovieSceneTrackPropertyRecorder.h"
#include "TrackRecorders/IMovieSceneTrackRecorderFactory.h"
#include "TrackRecorders/IMovieSceneTrackRecorderHost.h"
```

### 基本用法

**创建并使用轨道录制器：**

```cpp
// 来源: Public/TrackRecorders/MovieSceneTrackRecorder.h
// UMovieSceneTrackRecorder 的标准生命周期

// 1. 通过工厂创建录制器实例
UMovieSceneTrackRecorder* Recorder = Factory->CreateTrackRecorderForObject();

// 2. 在 PreRecording 阶段初始化轨道和 Section
Recorder->CreateTrack(
    RecorderHost,      // IMovieSceneTrackRecorderHost* - 宿主接口
    ObjectToRecord,    // UObject* - 要录制的对象（如 AActor*）
    MovieScene,        // UMovieScene* - 目标 Sequencer
    SettingsObject,    // UMovieSceneTrackRecorderSettings* - 设置
    ObjectGuid         // FGuid - 对象在 Level Sequence 中的绑定 GUID
);

// 3. 设置 Section 起始时间码
Recorder->SetSectionStartTimecode(
    StartTimecode,     // FTimecode - 外部时间码
    FirstFrame         // FFrameNumber - Section 首帧
);

// 4. 每帧采样录制（在录制循环中调用）
Recorder->RecordSample(CurrentFrameTime);

// 5. 停止录制
Recorder->StopRecording();

// 6. 完成录制，进行后处理
Recorder->FinalizeTrack();
```

### 进阶用法

**创建自定义轨道录制器工厂：**

```cpp
// 来源: Public/TrackRecorders/IMovieSceneTrackRecorderFactory.h
// 实现 IMovieSceneTrackRecorderFactory 接口，注册为模块特性

class FMyCustomTrackRecorderFactory : public IMovieSceneTrackRecorderFactory
{
public:
    // 检查对象是否可被此工厂录制
    virtual bool CanRecordObject(UObject* InObjectToRecord) const override
    {
        // 例如：只录制特定类型的组件
        return InObjectToRecord->IsA<UMyCustomComponent>();
    }

    // 创建对象录制器
    virtual UMovieSceneTrackRecorder* CreateTrackRecorderForObject() const override
    {
        return NewObject<UMyCustomTrackRecorder>();
    }

    // 检查特定属性是否可被录制
    virtual bool CanRecordProperty(UObject* InObjectToRecord, FProperty* InPropertyToRecord) const override
    {
        return InPropertyToRecord->GetFName() == GET_MEMBER_NAME_CHECKED(UMyCustomComponent, MyFloatParam);
    }

    // 创建属性录制器
    virtual UMovieSceneTrackRecorder* CreateTrackRecorderForProperty(
        UObject* InObjectToRecord, const FName& InPropertyToRecord) const override
    {
        return NewObject<UMyCustomPropertyTrackRecorder>();
    }

    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MyRecorder", "DisplayName", "My Custom Recorder");
    }

    // 设置是否可序列化
    virtual bool IsSerializable() const override { return true; }
    virtual FName GetSerializedType() const override { return FName("MyCustomRecorder"); }
};
```

**使用泛型属性录制器模板：**

```cpp
// 来源: Public/TrackRecorders/MovieSceneTrackPropertyRecorder.h
// FMovieSceneTrackPropertyRecorder<T> 是一个模板类，支持任意属性类型

// 录制一个 float 属性
FTrackInstancePropertyBindings Binding("MyFloatProperty", "MyFloatProperty");
FMovieSceneTrackPropertyRecorder<float> FloatRecorder(Binding);

// 录制一个 FVector 属性
FTrackInstancePropertyBindings VectorBinding("ActorLocation", "ActorLocation");
FMovieSceneTrackPropertyRecorder<FVector> VectorRecorder(VectorBinding);

// 标准录制流程
FloatRecorder.Create(Host, Object, MovieScene, Guid);
FloatRecorder.SetSectionStartTimecode(Timecode, FirstFrame);
FloatRecorder.Record(Object, CurrentTime);
FloatRecorder.Finalize(Object);
```

**实现 IMovieSceneTrackRecorderHost 接口（宿主）：**

```cpp
// 来源: Public/TrackRecorders/IMovieSceneTrackRecorderHost.h
// 宿主需要提供跨录制器的上下文信息

class FMyRecorderHost : public IMovieSceneTrackRecorderHost
{
public:
    // 查询其他 Actor 是否也在被录制（用于附件录制）
    virtual bool IsOtherActorBeingRecorded(AActor* OtherActor) const override
    {
        return RecordedActors.Contains(OtherActor);
    }

    // 获取被录制 Actor 的对象绑定 GUID
    virtual FGuid GetRecordedActorGuid(AActor* OtherActor) const override
    {
        if (const FGuid* Guid = ActorToGuidMap.Find(OtherActor))
            return *Guid;
        return FGuid();
    }

    // 获取通用录制设置
    virtual FTrackRecorderSettings GetTrackRecorderSettings() const override
    {
        return TrackSettings;
    }

    // 获取根 Level Sequence
    virtual ULevelSequence* GetRootLevelSequence() const override { return RootSequence; }

    // 获取 Sequence ID
    virtual FMovieSceneSequenceID GetSequenceID() const override { return SequenceID; }

    // 获取被录制 Actor 动画的初始根变换
    virtual FTransform GetRecordedActorAnimationInitialRootTransform(AActor* OtherActor) const override
    {
        return FTransform::Identity;
    }
};
```

## Demo 示例

以下演示如何创建一个简单的属性录制器来录制 Actor 的某个 float 属性：

```cpp
// MyPropertyRecorder.h
#pragma once

#include "TrackRecorders/MovieSceneTrackRecorder.h"
#include "TrackRecorders/MovieSceneTrackPropertyRecorder.h"
#include "TrackRecorders/IMovieSceneTrackRecorderHost.h"

UCLASS()
class UMyFloatPropertyRecorder : public UMovieSceneTrackRecorder
{
    GENERATED_BODY()

public:
    // 要录制的属性名
    UPROPERTY()
    FName PropertyName;

protected:
    virtual void CreateTrackImpl() override;
    virtual void RecordSampleImpl(const FQualifiedFrameTime& CurrentTime) override;
    virtual void FinalizeTrackImpl() override;
    virtual UMovieSceneSection* GetMovieSceneSection() const override;
    virtual void SetSavedRecordingDirectory(const FString& InDirectory) override;

private:
    TSharedPtr<FMovieSceneTrackPropertyRecorder<float>> PropertyRecorder;
};
```

```cpp
// MyPropertyRecorder.cpp
#include "MyPropertyRecorder.h"
#include "Tracks/MovieSceneFloatTrack.h"
#include "Sections/MovieSceneFloatSection.h"

void UMyFloatPropertyRecorder::CreateTrackImpl()
{
    if (!ObjectToRecord.IsValid())
    {
        return;
    }

    FTrackInstancePropertyBindings Binding(PropertyName, PropertyName.ToString());
    PropertyRecorder = MakeShared<FMovieSceneTrackPropertyRecorder<float>>(Binding);

    bool bOpenSerializer = OwningTakeRecorderSource->GetTrackRecorderSettings().bSaveRecordedAssets;
    PropertyRecorder->Create(
        OwningTakeRecorderSource,
        ObjectToRecord.Get(),
        MovieScene.Get(),
        ObjectGuid,
        bOpenSerializer
    );
}

void UMyFloatPropertyRecorder::RecordSampleImpl(const FQualifiedFrameTime& CurrentTime)
{
    if (!ObjectToRecord.IsValid() || !PropertyRecorder.IsValid())
    {
        return;
    }

    PropertyRecorder->Record(ObjectToRecord.Get(), CurrentTime);
}

void UMyFloatPropertyRecorder::FinalizeTrackImpl()
{
    if (!ObjectToRecord.IsValid() || !PropertyRecorder.IsValid())
    {
        return;
    }

    PropertyRecorder->Finalize(ObjectToRecord.Get());
}

UMovieSceneSection* UMyFloatPropertyRecorder::GetMovieSceneSection() const
{
    // 属性录制器内部管理 Section，这里返回 nullptr
    return nullptr;
}

void UMyFloatPropertyRecorder::SetSavedRecordingDirectory(const FString& InDirectory)
{
    if (PropertyRecorder.IsValid())
    {
        PropertyRecorder->SetSavedRecordingDirectory(InDirectory);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TakesCore` | 核心录制框架，提供序列化、时间码处理等基础设施 |
| `TakeMovieScene` | Sequencer 相关的自定义轨道和 Section 定义 |
| `MovieScene` | Sequencer 核心框架 |
| `AnimationRecording` | 骨骼动画录制接口 |
| `Animation` | 动画资产和骨骼网格体支持 |
| `Niagara` | Niagara 粒子系统支持（可选） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee6722f8` | Take Recorder: Correcting regression where the Attach Track Recorder does not correctly record attachment | 修复附件录制器未正确录制附件关系的回归问题 |
| 2026-05-14 | `d17111f0` | Take Recorder: Protecting against crashing on a null sub section sequence. | 防止子 Section 序列为空时导致崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-13 | `0c5ab24a` | Take Recorder: Adding missing WITH_EDITOR guard on log. | 补充缺失的 WITH_EDITOR 日志宏保护 |
| 2026-05-13 | `6aee158b` | Take Recorder: Fixing possible crash where a weak pointer could trigger an assertion due to a CastCh | 修复弱指针 CastChecked 触发断言导致的潜在崩溃 |

### 维护评价

**活跃维护。** 虽然该插件创建于 2019 年（约 7 年前），但作为虚拟制片工作流的核心组件，Epic 持续维护。近期（2026 年 5 月）有多次实质性修复，包括回归问题修复和崩溃防护，说明该模块在 UE5.8 中仍处于活跃开发状态。

**注意事项：**
- 属性表中模块均为 Runtime 类型，表明录制功能可在运行时使用，不依赖编辑器
- `IMovieSceneTrackRecorderFactory` 采用模块化特性（Modular Feature）模式，支持第三方扩展自定义录制器
- 模板化的 `FMovieSceneTrackPropertyRecorder<T>` 通过模板特化支持不同属性类型（float、bool、FVector、FQuat 等），新类型需要添加对应的模板特化
- 内置的录制器工厂覆盖了虚拟制片中最常见的录制需求：变换、动画、粒子、可见性、附件、Spawn、Actor 引用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes/Source/TakeTrackRecorders)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/take-recorder-in-unreal-engine/)