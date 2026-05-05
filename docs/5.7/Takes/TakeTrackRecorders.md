# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（虚拟制片资产） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakesCore` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Take Recorder 是 Unreal Engine 虚拟制片工作流的核心录制系统。它将编辑器视口中的实时数据（Actor 变换、骨骼动画、属性变化、粒子状态、可见性、附着关系、生成/销毁状态）捕获并写入 LevelSequence 轨道，供后续回放和编辑使用。

本插件采用**工厂模式**实现可扩展的录制架构：

- **`IMovieSceneTrackRecorderFactory`**：工厂接口，决定哪些对象/属性可以被录制，并创建对应的录制器实例。工厂以 `IModularFeature` 方式注册，支持运行时扩展。
- **`UMovieSceneTrackRecorder`**：录制器基类，定义了完整的录制生命周期（`CreateTrack` → `SetSectionStartTimecode` → `RecordSample` → `FinalizeTrack`）。
- **`IMovieSceneTrackPropertyRecorder`**：属性录制器接口，用于录制单个 UProperty 的值变化。

`TakeTrackRecorders` 模块提供了以下具体录制器实现：

| 录制器 | 录制内容 |
|---|---|
| `MovieScene3DTransformTrackRecorder` | Actor/组件的 3D 变换（位置、旋转、缩放） |
| `MovieSceneAnimationTrackRecorder` | 骨骼网格体动画（生成 AnimSequence 资产） |
| `MovieSceneVisibilityTrackRecorder` | Actor/组件的可见性状态 |
| `MovieSceneParticleTrackRecorder` | 粒子系统的激活/停用触发 |
| `MovieSceneSpawnTrackRecorder` | Actor 的生成/销毁状态 |
| `MovieScenePropertyTrackRecorder` | 任意 UProperty（通用属性录制） |
| `MovieScene3DAttachTrackRecorder` | Actor 之间的附着关系 |

这是基础设施代码——最终用户通过 Take Recorder 编辑器面板（由 `TakeRecorder` 模块提供）与之交互，而非直接调用这些录制器。

## 使用场景

- **虚拟制片**：在 nDisplay / LED 墙环境中录制摄像机和 Actor 的实时表演数据
- **动作捕捉**：录制动捕会话中的骨骼动画和变换数据到 Sequencer 轨道
- **实时预览录制**：在编辑器中预览动画时，将运行时数据录制为可编辑的关键帧序列
- **自定义录制管线**：通过实现 `IMovieSceneTrackRecorderFactory` 扩展录制系统，支持自定义数据类型的录制
- **批量属性录制**：使用 `MovieScenePropertyTrackRecorder` 录制任意 Actor 属性的变化历史

## 蓝图用法

Take Track Recorders 的核心录制逻辑是 C++ 驱动的，蓝图可交互的部分主要集中在**动画录制设置**。

### 动画录制设置（BlueprintReadWrite）

`UMovieSceneAnimationTrackRecorderSettings` 提供以下蓝图可配置属性：

| 属性 | 类型 | 说明 |
|---|---|---|
| `AnimationTrackName` | `FText` | 录制的动画轨道名称，支持 NamingTokens |
| `AnimationAssetName` | `FString` | 动画资产名称，支持 `{day}`, `{month}`, `{year}`, `{hour}`, `{minute}`, `{second}`, `{take}`, `{slate}`, `{actor}` 格式占位符 |
| `AnimationSubDirectory` | `FString` | 动画子目录，支持同上格式占位符 |
| `bRemoveRootAnimation` | `bool` | 是否将根骨骼动画移至变换轨道 |
| `TimecodeBoneMethod` | `FTimecodeBoneMethod` | 时间码写入骨骼的方法 |

### 轨道设置结构体

`FTakeRecorderTrackSettings` 用于配置哪些 Actor 类型自动创建哪些属性轨道：

| 属性 | 类型 | 说明 |
|---|---|---|
| `MatchingActorClass` | `FSoftClassPath` | 匹配的 Actor 类 |
| `DefaultPropertyTracks` | `TArray<FTakeRecorderPropertyTrackSettings>` | 自动创建的属性轨道列表 |
| `ExcludePropertyTracks` | `TArray<FTakeRecorderPropertyTrackSettings>` | 排除的属性轨道列表 |

### 使用示例（蓝图描述）

1. 在项目设置或 Take Recorder 面板中找到 **Animation Recorder Settings**
2. 设置 `AnimationAssetName` 为 `"{actor}_{take}"`，录制时会自动替换为 Actor 名称和 Take 编号
3. 设置 `AnimationSubDirectory` 为 `"Animations/{slate}"`，按 Slate 名称组织输出目录
4. 勾选 `bRemoveRootAnimation` 将根运动分离到独立的变换轨道

## C++ 用法

### 头文件引入

```cpp
// 录制器工厂接口
#include "TrackRecorders/IMovieSceneTrackRecorderFactory.h"

// 录制器基类
#include "TrackRecorders/MovieSceneTrackRecorder.h"

// 属性录制器接口
#include "TrackRecorders/MovieSceneTrackPropertyRecorder.h"

// 录制器宿主接口和设置
#include "TrackRecorders/IMovieSceneTrackRecorderHost.h"

// 具体录制器（按需引入）
#include "TrackRecorders/MovieScene3DTransformTrackRecorder.h"
#include "TrackRecorders/MovieSceneAnimationTrackRecorder.h"
#include "TrackRecorders/MovieScenePropertyTrackRecorder.h"
```

### 基本用法：注册自定义录制器工厂

录制器工厂通过 `IModularFeature` 系统注册，Take Recorder 会自动发现并使用它们。

```cpp
// MyCustomTrackRecorderFactory.h
#pragma once

#include "TrackRecorders/IMovieSceneTrackRecorderFactory.h"
#include "TrackRecorders/MovieSceneTrackRecorder.h"
#include "MyCustomTrackRecorderFactory.generated.h"

// 自定义录制器
UCLASS()
class UMyCustomTrackRecorder : public UMovieSceneTrackRecorder
{
    GENERATED_BODY()

protected:
    virtual void CreateTrackImpl() override;
    virtual void RecordSampleImpl(const FQualifiedFrameTime& CurrentTime) override;
    virtual void FinalizeTrackImpl() override;
};

// 自定义工厂
class FMyCustomTrackRecorderFactory : public IMovieSceneTrackRecorderFactory
{
public:
    // 判断对象是否可被此录制器录制
    virtual bool CanRecordObject(UObject* InObjectToRecord) const override;

    // 创建录制器实例
    virtual UMovieSceneTrackRecorder* CreateTrackRecorderForObject() const override;

    // 本工厂不录制特定属性
    virtual bool CanRecordProperty(UObject*, FProperty*) const override { return false; }
    virtual UMovieSceneTrackRecorder* CreateTrackRecorderForProperty(UObject*, const FName&) const override { return nullptr; }

    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MyCustom", "DisplayName", "Custom Track");
    }
};
```

```cpp
// MyCustomTrackRecorderFactory.cpp
#include "MyCustomTrackRecorderFactory.h"
#include "Features/IModularFeatures.h"

bool FMyCustomTrackRecorderFactory::CanRecordObject(UObject* InObjectToRecord) const
{
    // 只录制特定类型的对象
    return InObjectToRecord->IsA<UMyCustomComponent>();
}

UMovieSceneTrackRecorder* FMyCustomTrackRecorderFactory::CreateTrackRecorderForObject() const
{
    return NewObject<UMyCustomTrackRecorder>();
}

void UMyCustomTrackRecorder::CreateTrackImpl()
{
    // 创建 MovieScene 轨道和片段
    // ObjectToRecord 和 MovieScene 由基类在 CreateTrack() 中设置
}

void UMyCustomTrackRecorder::RecordSampleImpl(const FQualifiedFrameTime& CurrentTime)
{
    // 每帧调用，采集当前数据并写入片段
}

void UMyCustomTrackRecorder::FinalizeTrackImpl()
{
    // 录制结束后的清理和后处理
}

// 注册工厂（通常在模块 StartupModule 中调用）
void RegisterMyFactory()
{
    IModularFeatures::Get().RegisterModularFeature(
        IMovieSceneTrackRecorderFactory::GetModularFeatureName(),
        new FMyCustomTrackRecorderFactory()
    );
}
```

### 进阶用法：使用属性录制器模板

`FMovieSceneTrackPropertyRecorder<PropertyType>` 是一个模板类，可以录制任意类型的 UProperty。

```cpp
#include "TrackRecorders/MovieSceneTrackPropertyRecorder.h"

// 录制一个 float 属性
void RecordFloatProperty(UObject* InObject, UMovieScene* InMovieScene, const FGuid& InGuid)
{
    // 创建属性绑定
    FTrackInstancePropertyBindings Binding(
        FName("MyFloatProperty"),  // 属性名
        TEXT("MyFloatProperty")     // 属性路径
    );

    // 创建属性录制器
    auto PropertyRecorder = MakeShared<FMovieSceneTrackPropertyRecorder<float>>(Binding);

    // 初始化录制
    IMovieSceneTrackRecorderHost* Host = /* 获取宿主 */;
    PropertyRecorder->Create(Host, InObject, InMovieScene, InGuid, false);

    // 在每帧录制时调用
    FQualifiedFrameTime CurrentTime = /* 获取当前时间 */;
    PropertyRecorder->Record(InObject, CurrentTime);

    // 录制结束后调用
    PropertyRecorder->Finalize(InObject);
}
```

### 进阶用法：配置录制行为

通过 `FTrackRecorderSettings` 控制录制细节：

```cpp
#include "TrackRecorders/IMovieSceneTrackRecorderHost.h"

FTrackRecorderSettings Settings;
Settings.bRecordToPossessable = true;       // 录制到 Possessable 而非 Spawnable
Settings.bRemoveRedundantTracks = true;     // 移除无变化的冗余轨道
Settings.bReduceKeys = true;                // 减少关键帧数量
Settings.ReduceKeysTolerance = 0.001f;      // 关键帧精简容差
Settings.bSaveRecordedAssets = true;        // 保存录制生成的资产
Settings.TransformOrigin = FTransform::Identity; // 变换原点

// 配置默认属性轨道
FTakeRecorderTrackSettings TrackSettings;
TrackSettings.MatchingActorClass = AMyActor::StaticClass();

FTakeRecorderPropertyTrackSettings PropSetting;
PropSetting.PropertyPath = TEXT("Health");
TrackSettings.DefaultPropertyTracks.Add(PropSetting);

Settings.DefaultTracks.Add(TrackSettings);
```

## Demo 示例

一个完整的自定义轨道录制器，录制 Actor 的自定义浮点属性到 Sequencer 轨道。

### MyFloatPropertyTrackRecorder.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "TrackRecorders/MovieSceneTrackRecorder.h"
#include "TrackRecorders/IMovieSceneTrackRecorderFactory.h"
#include "Sections/MovieSceneFloatSection.h"
#include "Tracks/MovieSceneFloatTrack.h"
#include "MyFloatPropertyTrackRecorder.generated.h"

class FMyFloatPropertyTrackRecorderFactory : public IMovieSceneTrackRecorderFactory
{
public:
    virtual ~FMyFloatPropertyTrackRecorderFactory() {}

    virtual bool CanRecordObject(UObject* InObjectToRecord) const override;
    virtual UMovieSceneTrackRecorder* CreateTrackRecorderForObject() const override;
    virtual bool CanRecordProperty(UObject*, FProperty*) const override { return false; }
    virtual UMovieSceneTrackRecorder* CreateTrackRecorderForProperty(UObject*, const FName&) const override { return nullptr; }
    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MyFloatRecorder", "DisplayName", "Float Property Track");
    }
};

UCLASS()
class UMyFloatPropertyTrackRecorder : public UMovieSceneTrackRecorder
{
    GENERATED_BODY()

protected:
    virtual void CreateTrackImpl() override;
    virtual void RecordSampleImpl(const FQualifiedFrameTime& CurrentTime) override;
    virtual void FinalizeTrackImpl() override;
    virtual UMovieSceneSection* GetMovieSceneSection() const override { return Section.Get(); }

private:
    TWeakObjectPtr<UMovieSceneFloatSection> Section;
    TWeakObjectPtr<UMovieSceneFloatTrack> Track;
    float PreviousValue;
    bool bSetFirstKey;
};
```

### MyFloatPropertyTrackRecorder.cpp

```cpp
#include "MyFloatPropertyTrackRecorder.h"
#include "GameFramework/Actor.h"
#include "Features/IModularFeatures.h"

bool FMyFloatPropertyTrackRecorderFactory::CanRecordObject(UObject* InObjectToRecord) const
{
    // 示例：录制所有带 "CustomValue" 属性的 Actor
    if (AActor* Actor = Cast<AActor>(InObjectToRecord))
    {
        FProperty* Prop = Actor->GetClass()->FindPropertyByName(FName("CustomValue"));
        return Prop != nullptr && Prop->IsA<FFloatProperty>();
    }
    return false;
}

UMovieSceneTrackRecorder* FMyFloatPropertyTrackRecorderFactory::CreateTrackRecorderForObject() const
{
    return NewObject<UMyFloatPropertyTrackRecorder>();
}

void UMyFloatPropertyTrackRecorder::CreateTrackImpl()
{
    bSetFirstKey = true;
    PreviousValue = 0.0f;

    AActor* Actor = Cast<AActor>(ObjectToRecord.Get());
    if (!Actor || !MovieScene.Get())
    {
        return;
    }

    // 查找目标属性
    FProperty* Prop = Actor->GetClass()->FindPropertyByName(FName("CustomValue"));
    if (!Prop)
    {
        return;
    }

    // 创建 Float 轨道
    Track = MovieScene->FindTrack<UMovieSceneFloatTrack>(ObjectGuid);
    if (!Track.IsValid())
    {
        Track = MovieScene->AddTrack<UMovieSceneFloatTrack>(ObjectGuid);
    }

    // 创建 Float 片段
    Section = Cast<UMovieSceneFloatSection>(Track->FindSectionByPosition(FFrameNumber(0)));
    if (!Section.IsValid())
    {
        Section = Cast<UMovieSceneFloatSection>(Track->CreateNewSection());
        Track->AddSection(*Section);
        Section->SetRange(TRange<FFrameNumber>::All());
    }
}

void UMyFloatPropertyTrackRecorder::RecordSampleImpl(const FQualifiedFrameTime& CurrentTime)
{
    AActor* Actor = Cast<AActor>(ObjectToRecord.Get());
    if (!Actor || !Section.IsValid())
    {
        return;
    }

    // 读取当前属性值
    FProperty* Prop = Actor->GetClass()->FindPropertyByName(FName("CustomValue"));
    if (!Prop)
    {
        return;
    }

    float CurrentValue = 0.0f;
    void* ValuePtr = Prop->ContainerPtrToValuePtr<void>(Actor);
    Prop->CopySingleValue(&CurrentValue, ValuePtr);

    // 仅在值变化或首帧时添加关键帧
    if (bSetFirstKey || CurrentValue != PreviousValue)
    {
        FFrameNumber FrameNumber = CurrentTime.Time.GetFrame();
        Section->GetChannel().GetData().AddKey(FrameNumber, CurrentValue);
        PreviousValue = CurrentValue;
        bSetFirstKey = false;
    }
}

void UMyFloatPropertyTrackRecorder::FinalizeTrackImpl()
{
    // 如果没有录制到任何关键帧，移除轨道
    if (Section.IsValid() && Section->GetChannel().GetData().GetNumKeys() == 0)
    {
        if (Track.IsValid())
        {
            Track->RemoveSection(*Section);
        }
    }
}

// 在模块 StartupModule 中注册
void FMyModule::StartupModule()
{
    IModularFeatures::Get().RegisterModularFeature(
        IMovieSceneTrackRecorderFactory::GetModularFeatureName(),
        new FMyFloatPropertyTrackRecorderFactory()
    );
}

void FMyModule::ShutdownModule()
{
    IModularFeatures::Get().UnregisterModularFeature(
        IMovieSceneTrackRecorderFactory::GetModularFeatureName(),
        &MyFactory
    );
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 轨道、片段、通道等核心基础设施 |
| `LevelSequence` | 关卡序列资产支持 |
| `AnimationRecorder` | 骨骼动画录制引擎（`FAnimRecorderInstance`） |
| `TakesCore` | Take 录制核心日志和工具函数 |

## 维护状态

### 近期更新

- 462ec4ed8231 Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created and subsequently destroyed.
  > 代码质量修复，消除静态分析警告
- 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
  > 构建系统维护，修正 DLL 导出标记
- 9045d73aa2fc TakeRecorder: Change default of AnimationTrackName to {actor}_anim, solving an issue when loading into sequencer.
  > Bug 修复：将动画轨道名称默认值改为 `{actor}_anim`，解决加载到 Sequencer 时的问题

### 维护评价

- **创建时间**：2019 年 1 月，约 6 年历史
- **维护状态**：**维护中** — 作为 Epic 官方虚拟制片工具链的核心组件，持续接收 bug 修复和兼容性更新
- **近期更新内容**：以代码质量修复和构建系统维护为主，无重大功能变更，表明插件已进入**稳定期**
- **已知限制**：录制器工厂通过 `IModularFeature` 注册，需确保在 Take Recorder 启动前完成注册；动画录制依赖 `AnimationRecorder` 模块，该模块在打包构建中可能不可用
- **推荐程度**：**推荐使用** — 这是 Unreal Engine 虚拟制片工作流的标准录制方案，API 稳定，架构可扩展。如需自定义录制行为，通过实现 `IMovieSceneTrackRecorderFactory` 即可无缝集成

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes)
- [TakeTrackRecorders 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes/Source/TakeTrackRecorders)