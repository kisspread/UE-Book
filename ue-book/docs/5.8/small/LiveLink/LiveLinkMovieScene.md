# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（LiveLinkHub 程序支持） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

LiveLink 是 UE5 的实时动画数据流框架，解决了从外部应用程序（如 MotionBuilder、Maya、Vicon 等动作捕捉/动画软件）将动画数据实时传输到引擎中的问题。

它基于发布-订阅模式：外部程序作为**源（Source）**发布数据，引擎中的**客户端（Client）**订阅并消费这些数据。数据类型由**角色（Role）**定义，例如动画骨骼、摄像机变换、灯光参数等。每个数据流称为一个**主题（Subject）**。

**LiveLinkMovieScene** 模块是该插件与 Sequencer 的集成层，负责将 LiveLink 实时流数据**录制**为 Sequencer 关键帧轨道，并支持从 Sequencer **回放**这些录制数据到 LiveLink 管线中。

## 使用场景

- 你从 MotionBuilder 或 Maya 实时传输骨骼动画到引擎中的角色 → 用 LiveLink
- 你使用 Vicon/OptiTrack 等动捕系统实时驱动虚拟角色 → 用 LiveLink
- 你需要将 LiveLink 实时流录制为 Sequencer 关键帧以便后期编辑 → 用 LiveLinkMovieScene
- 你需要将录制好的 Sequencer 轨道重新回放到 LiveLink 管线 → 用 LiveLinkMovieScene
- 你在做虚拟制片，需要实时同步摄像机/灯光数据 → 用 LiveLink

## 蓝图用法

LiveLinkMovieScene 模块主要为 Sequencer 内部系统服务，不直接暴露大量蓝图 API。核心交互通过 Sequencer 编辑器 UI 和 C++ 接口完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetTrackRole` | 设置 LiveLink 轨道对应的角色类型 | `UMovieSceneLiveLinkTrack` |
| `GetTrackRole` | 获取当前轨道的角色类型 | `UMovieSceneLiveLinkTrack` |
| `SetSubjectName` | 设置 Section 关联的主题名称 | `UMovieSceneLiveLinkSection` |

> **说明**：该模块的蓝图暴露较少，主要通过 Sequencer 编辑器和 LiveLink 面板进行操作。LiveLink 的蓝图节点主要在 `LiveLinkComponents` 模块中。

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneLiveLinkSection.h"
#include "MovieSceneLiveLinkTrack.h"
#include "MovieSceneLiveLinkStructPropertyBindings.h"
#include "MovieSceneLiveLinkPropertyHandler.h"
#include "MovieSceneLiveLinkSubSection.h"
```

### 基本用法

以下示例展示如何通过 C++ 与 LiveLink Sequencer 系统交互：

```cpp
// 创建属性绑定，用于访问 LiveLink 帧数据中的特定属性
// 来源: Public/MovieScene/MovieSceneLiveLinkStructPropertyBindings.h
FLiveLinkStructPropertyBindings LocationBinding(FName("Location"), TEXT("Transform.Location"));

// 缓存绑定到特定 UStruct
const UScriptStruct& FrameStruct = *FLiveLinkAnimationFrameData::StaticStruct();
LocationBinding.CacheBinding(FrameStruct);

// 从帧数据中获取属性值
FVector Location = LocationBinding.GetCurrentValueAt<FVector>(0, FrameStruct, FrameDataPtr);

// 设置属性值（用于回放）
LocationBinding.SetCurrentValueAt<FVector>(0, FrameStruct, FrameDataPtr, NewLocation);
```

### 进阶用法

以下示例展示 LiveLink 数据录制到 Sequencer 的完整流程：

```cpp
// 1. 创建 LiveLink 轨道和 Section
// 来源: Public/MovieScene/MovieSceneLiveLinkTrack.h
UMovieSceneLiveLinkTrack* LiveLinkTrack = MovieScene->AddTrack<UMovieSceneLiveLinkTrack>(ObjectBindingID);

// 设置轨道角色（如动画角色）
TSubclassOf<ULiveLinkRole> AnimRole = ULiveLinkAnimationRole::StaticClass();
LiveLinkTrack->SetTrackRole(AnimRole);

// 创建 Section
UMovieSceneLiveLinkSection* Section = Cast<UMovieSceneLiveLinkSection>(LiveLinkTrack->CreateNewSection());

// 2. 初始化 Section（传入主题预设和静态数据）
// 来源: Public/MovieScene/MovieSceneLiveLinkSection.h
FLiveLinkSubjectPreset SubjectPreset;
SubjectPreset.Key.SubjectName = FName("MySubject");
Section->Initialize(SubjectPreset, StaticDataPtr);

// 3. 逐帧录制数据
// 来源: Public/MovieScene/MovieSceneLiveLinkSection.h
FFrameNumber FrameNum(100);
Section->RecordFrame(FrameNum, FrameData);

// 4. 完成录制，可选择优化关键帧
// 来源: Public/MovieScene/MovieSceneLiveLinkSection.h
FKeyDataOptimizationParams OptimizationParams;
Section->FinalizeSection(true /* bReduceKeys */, OptimizationParams);

// 5. 创建评估模板用于回放
// 来源: Public/MovieScene/MovieSceneLiveLinkSection.h
FMovieSceneEvalTemplatePtr Template = Section->CreateSectionTemplate(Track);
```

**属性处理器体系**（用于管理不同数据类型的录制与回放）：

```cpp
// 使用泛型属性处理器处理浮点/向量等类型
// 来源: Public/MovieScene/MovieSceneLiveLinkPropertyHandler.h
TSharedPtr<FMovieSceneLiveLinkPropertyHandler<FVector>> VectorHandler = 
    MakeShared<FMovieSceneLiveLinkPropertyHandler<FVector>>(Binding, PropertyStorage);

// 使用变换处理器处理 FTransform 类型
// 来源: Public/MovieScene/MovieSceneLiveLinkTransformHandler.h
TSharedPtr<FMovieSceneLiveLinkTransformHandler> TransformHandler = 
    MakeShared<FMovieSceneLiveLinkTransformHandler>(Binding, PropertyStorage);

// 使用枚举处理器处理枚举类型
// 来源: Public/MovieScene/MovieSceneLiveLinkEnumHandler.h
TSharedPtr<FMovieSceneLiveLinkEnumHandler> EnumHandler = 
    MakeShared<FMovieSceneLiveLinkEnumHandler>(Binding, PropertyStorage);
```

## Demo 示例

以下展示如何创建一个自定义的 LiveLink 子段来管理特定数据类型：

```cpp
// MyLiveLinkSubSection.h
#pragma once

#include "MovieSceneLiveLinkSubSection.h"
#include "MyLiveLinkSubSection.generated.h"

UCLASS()
class UMyLiveLinkSubSection : public UMovieSceneLiveLinkSubSection
{
    GENERATED_BODY()

public:
    UMyLiveLinkSubSection(const FObjectInitializer& ObjectInitializer);

    virtual void Initialize(TSubclassOf<ULiveLinkRole> InSubjectRole,
        const TSharedPtr<FLiveLinkStaticDataStruct>& InStaticData) override;

    virtual int32 CreateChannelProxy(int32 InChannelIndex,
        TArray<bool>& OutChannelMask,
        FMovieSceneChannelProxyData& OutChannelData) override;

    virtual void RecordFrame(FFrameNumber InFrameNumber,
        const FLiveLinkFrameDataStruct& InFrameData) override;

    virtual void FinalizeSection(bool bReduceKeys,
        const FKeyDataOptimizationParams& OptimizationParams) override;

    virtual bool IsRoleSupported(
        const TSubclassOf<ULiveLinkRole>& RoleToSupport) const override;

private:
    TSharedPtr<FMovieSceneLiveLinkTransformHandler> TransformHandler;
};
```

```cpp
// MyLiveLinkSubSection.cpp
#include "MyLiveLinkSubSection.h"
#include "MovieSceneLiveLinkTransformHandler.h"
#include "MovieSceneLiveLinkStructPropertyBindings.h"

UMyLiveLinkSubSection::UMyLiveLinkSubSection(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

void UMyLiveLinkSubSection::Initialize(TSubclassOf<ULiveLinkRole> InSubjectRole,
    const TSharedPtr<FLiveLinkStaticDataStruct>& InStaticData)
{
    Super::Initialize(InSubjectRole, InStaticData);

    // 创建 Transform 属性绑定
    FLiveLinkStructPropertyBindings Binding(FName("Transform"), TEXT("Transform"));
    FLiveLinkPropertyData* PropertyData = GetPropertyData(0);
    
    TransformHandler = MakeShared<FMovieSceneLiveLinkTransformHandler>(Binding, PropertyData);
    
    if (InStaticData.IsValid())
    {
        const int32 TransformCount = 1; // 根据实际骨骼数量设置
        TransformHandler->CreateChannels(InStaticData->GetStruct(), TransformCount);
    }
}

int32 UMyLiveLinkSubSection::CreateChannelProxy(int32 InChannelIndex,
    TArray<bool>& OutChannelMask,
    FMovieSceneChannelProxyData& OutChannelData)
{
    // 将内部通道注册到 Section 的通道代理
    int32 ChannelOffset = 0;
    // ... 注册浮点通道 (Location X/Y/Z, Rotation X/Y/Z, Scale X/Y/Z)
    return ChannelOffset;
}

void UMyLiveLinkSubSection::RecordFrame(FFrameNumber InFrameNumber,
    const FLiveLinkFrameDataStruct& InFrameData)
{
    if (TransformHandler.IsValid())
    {
        TransformHandler->RecordFrame(InFrameNumber,
            InFrameData.GetStruct(), InFrameData.GetBaseData());
    }
}

void UMyLiveLinkSubSection::FinalizeSection(bool bReduceKeys,
    const FKeyDataOptimizationParams& OptimizationParams)
{
    if (TransformHandler.IsValid())
    {
        TransformHandler->Finalize(bReduceKeys, OptimizationParams);
    }
}

bool UMyLiveLinkSubSection::IsRoleSupported(
    const TSubclassOf<ULiveLinkRole>& RoleToSupport) const
{
    // 支持动画角色
    return RoleToSupport == ULiveLinkAnimationRole::StaticClass();
}
```

## 模块依赖

基于 LiveLinkMovieScene 模块的实际功能，以下是关键依赖：

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心（轨道、区段、评估模板） |
| `MovieSceneTracks` | Sequencer 内置轨道类型（属性轨道基础） |
| `LiveLink` | LiveLink 核心框架（源、客户端、主题管理） |
| `LiveLinkInterface` | LiveLink 接口定义（角色、帧数据、静态数据） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is unavailable | 修复广播子系统不可用时的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode | 修复严格浮点模式下 double 到 float 的截断警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Python scripting changes properties | 修复 Python 脚本修改属性时 MemberProperty 为 null 导致的崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the new VP folder structure | 虚拟制片资产迁移到新的分类目录结构 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的垃圾输出 |

### 维护评价

- **创建时间**：2018 年 2 月（UE 4.19 版本时期），从 Experimental 文件夹迁移到 Animation 分类
- **更新频率**：近期保持活跃更新，最近一个月有多次提交，主要集中在 bug 修复和稳定性改进
- **维护状态**：**活跃维护中** — 作为 Epic Games 虚拟制片工具链的核心组件，持续获得更新
- **已知限制**：默认未启用（`EnabledByDefault=false`），需要手动在插件设置中启用；部分接口标记为 deprecated（如不带 Index 参数的 GetCurrentValue/SetCurrentValue 系列函数，4.24 起废弃）
- **推荐程度**：**强烈推荐** — 如果你需要实时外部数据流集成或 Sequencer 数据录制/回放功能，这是官方标准方案，文档和社区支持完善

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- [源码 - LiveLinkMovieScene](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink/Source/LiveLinkMovieScene)
- [官方文档](https://docs.unrealengine.com/en-US/animation/virtual-mocap/LiveLink/)