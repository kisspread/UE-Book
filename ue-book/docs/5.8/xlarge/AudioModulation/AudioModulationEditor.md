# Audio Modulation

> Default implementation of Audio Modulation in the Unreal Audio Engine.

| 属性 | 值 |
|---|---|
| 中文名 | 音频调制 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、样式资源） |
| 模块 | `AudioModulation` (Runtime), `AudioModulationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-08-23 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioModulation) | |

## 用途

AudioModulation 插件为 UE5 的音频引擎提供了一套完整的**参数化调制系统**。它的核心目标是让你能够通过"总线（Bus）"和"补丁（Patch）"机制，将任意音频源的属性（音量、音调、滤波器截止频率等）绑定到可动态变化的参数上。

与传统的蓝图驱动音量变化相比，AudioModulation 提供了以下关键能力：

- **控制总线（Control Bus）**：定义一个可被多个声音共享的参数通道，所有订阅该总线的声音会自动跟随参数值变化
- **控制总线混合（Control Bus Mix）**：将多条总线组合成一个混合预设，可以整体淡入淡出，适合场景切换时的音频环境管理
- **调制补丁（Modulation Patch）**：定义从输入参数到输出效果的映射曲线（支持自定义曲线），实现非线性的调制行为
- **调制生成器（Modulation Generator）**：自动生成调制信号（如 LFO），无需外部输入即可产生周期性变化
- **Sequencer 集成**：在 Sequencer 时间轴上直接编辑总线参数的关键帧动画

这个插件存在的原因是：游戏中的音频往往需要响应游戏状态动态变化（靠近敌人、进入室内、受伤等），AudioModulation 提供了一套架构化的方式来管理和驱动这些变化，而不是散落在各处的蓝图节点。

## 使用场景

- 你在做一个恐怖游戏，需要在不同房间自动切换混响效果 → 使用 Control Bus Mix 管理空间音频参数
- 你需要让背景音乐的音量随距离/危险等级平滑变化 → 使用 Control Bus + Modulation Patch 定义映射曲线
- 你想要一个周期性颤音效果 → 使用 Modulation Generator 生成 LFO 信号
- 你正在用 Sequencer 制作过场动画，需要精确控制音频参数随时间变化 → 使用 Sequencer 中的 Control Bus Track
- 你需要一个统一的地方管理所有音频参数，而不是在每个 Sound Cue 里单独处理 → 使用 AudioModulation 架构

## 蓝图用法

> 注意：本插件默认未启用（`EnabledByDefault: false`），需要在项目设置 → 插件中手动启用。

### 核心资产类型

| 资产类型 | 说明 | 创建路径 |
|---|---|---|
| Control Bus | 定义单个可调制参数通道 | Content Browser → Audio > Advanced > Audio Modulation |
| Control Bus Mix | 将多条 Control Bus 组合为混合预设 | Content Browser → Audio > Advanced > Audio Modulation |
| Modulation Patch | 定义输入到输出的映射曲线 | Content Browser → Audio > Advanced > Audio Modulation |
| Modulation Parameter | 定义调制参数的类型和范围 | Content Browser → Audio > Advanced > Audio Modulation |
| Modulation Generator | 自动生成调制信号（如 LFO） | Content Browser → Audio > Advanced > Audio Modulation |

### 使用示例（蓝图描述）

**基本调制流程：**

1. 创建一个 `SoundModulationParameter` 资产（例如 "MasterVolumeParam"，范围 0-1）
2. 创建一个 `SoundControlBus` 资产（例如 "MasterBus"），指定其参数类型为刚创建的 Parameter
3. 在声音资产的属性中，将音量/音调等映射到 "MasterBus"
4. 通过蓝图调用 Bus 的 Set Value 芃改变参数值，所有引用该 Bus 的声音都会自动响应

**场景混合控制：**

1. 创建多条 Control Bus（如 "ReverbBus"、"MusicVolumeBus"、"SFXVolumeBus"）
2. 创建一个 Control Bus Mix 资产，添加多个 Stage，每个 Stage 对应一条 Bus 并设定目标值
3. 在游戏蓝图中，根据场景切换（进入室内/室外）调用 Mix 的 Activate/Deactivate

## C++ 用法

### 编辑器扩展（Sequencer Track Editor）

编辑器模块提供了 Sequencer 集成，允许在时间轴上直接控制音频参数：

```cpp
// 引入头文件
#include "AudioControlBusBaseTrackEditor.h"
#include "AudioControlBusTrackEditor.h"
#include "AudioControlBusMixTrackEditor.h"
```

#### 自定义 Sequencer Track Editor

```cpp
// 来源: Source/AudioModulationEditor/Private/AudioControlBusTrackEditor.h
// Control Bus Track Editor - 在 Sequencer 中编辑单条 Control Bus 的参数曲线
class FAudioControlBusTrackEditor : public FAudioControlBusBaseTrackEditor
{
public:
    FAudioControlBusTrackEditor(TSharedRef<ISequencer> InSequencer);

    // 创建实例，由 Sequencer 回调
    static TSharedRef<ISequencerTrackEditor> CreateTrackEditor(TSharedRef<ISequencer> OwningSequencer);

    // 判断是否支持当前序列类型
    virtual bool SupportsSequence(UMovieSceneSequence* InSequence) const override;

    // 处理资产拖放到 Sequencer 的事件
    virtual bool HandleAssetAdded(UObject* Asset, const FGuid& TargetObjectGuid) override;
};

// 来源: Source/AudioModulationEditor/Private/AudioControlBusMixTrackEditor.h
// Control Bus Mix Track Editor - 在 Sequencer 中编辑 Bus Mix 的混合参数
class FAudioControlBusMixTrackEditor : public FAudioControlBusBaseTrackEditor
{
public:
    FAudioControlBusMixTrackEditor(TSharedRef<ISequencer> InSequencer);

    static TSharedRef<ISequencerTrackEditor> CreateTrackEditor(TSharedRef<ISequencer> OwningSequencer);

    virtual FText GetDisplayName() const override;
    virtual bool SupportsType(TSubclassOf<UMovieSceneTrack> Type) const override;
};
```

### 属性布局自定义

```cpp
// 来源: Source/AudioModulationEditor/Private/Layouts/SoundControlModulationPatchLayout.h
// 自定义 Modulation Patch 属性面板布局
class FSoundControlModulationPatchLayoutCustomization : public IPropertyTypeCustomization
{
public:
    static TSharedRef<IPropertyTypeCustomization> MakeInstance();

    // 自定义头部显示
    virtual void CustomizeHeader(TSharedRef<IPropertyHandle> StructPropertyHandle,
                                  FDetailWidgetRow& HeaderRow,
                                  IPropertyTypeCustomizationUtils& StructCustomizationUtils) override;

    // 自定义子属性显示（如 Inputs/Output 的可见性控制）
    virtual void CustomizeChildren(TSharedRef<IPropertyHandle> StructPropertyHandle,
                                    IDetailChildrenBuilder& ChildBuilder,
                                    IPropertyTypeCustomizationUtils& StructCustomizationUtils) override;
};
```

### 资产定义

```cpp
// 来源: Source/AudioModulationEditor/Private/AssetDefinition/AssetDefinition_SoundControlBus.h
// 定义 Control Bus 资产在 Content Browser 中的显示方式
UCLASS()
class UAssetDefinition_SoundControlBus : public UAssetDefinitionDefault_AudioDiffable
{
    virtual FText GetAssetDisplayName() const override;
    virtual FLinearColor GetAssetColor() const override;
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    virtual FText GetAssetDescription(const FAssetData& AssetData) const override;
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
};
```

### 工厂类（资产创建）

```cpp
// 来源: Source/AudioModulationEditor/Private/Factories/SoundControlBusFactory.h
UCLASS()
class USoundControlBusFactory : public UFactory
{
    virtual UObject* FactoryCreateNew(UClass* Class, UObject* InParent,
                                       FName Name, EObjectFlags Flags,
                                       UObject* Context, FFeedbackContext* Warn) override;
};

// 来源: Source/AudioModulationEditor/Private/Factories/SoundModulationPatchFactory.h
UCLASS()
class USoundModulationPatchFactory : public UFactory
{
    virtual UObject* FactoryCreateNew(UClass* Class, UObject* InParent,
                                       FName Name, EObjectFlags Flags,
                                       UObject* Context, FFeedbackContext* Warn) override;
};

// 来源: Source/AudioModulationEditor/Private/Factories/SoundControlBusMixFactory.h
UCLASS()
class USoundControlBusMixFactory : public UFactory
{
    virtual UObject* FactoryCreateNew(UClass* Class, UObject* InParent,
                                       FName Name, EObjectFlags Flags,
                                       UObject* Context, FFeedbackContext* Warn) override;
};

// 来源: Source/AudioModulationEditor/Private/Factories/SoundModulationGeneratorFactory.h
UCLASS()
class USoundModulationGeneratorFactory : public UFactory
{
    UPROPERTY()
    TSubclassOf<USoundModulationGenerator> GeneratorClass;

    virtual bool ConfigureProperties() override;
    virtual UObject* FactoryCreateNew(UClass* Class, UObject* InParent,
                                       FName Name, EObjectFlags Flags,
                                       UObject* Context, FFeedbackContext* Warn) override;
};

// 来源: Source/AudioModulationEditor/Private/Factories/SoundModulationParameterFactory.h
UCLASS()
class USoundModulationParameterFactory : public UFactory
{
    virtual bool ConfigureProperties() override;
    virtual UObject* FactoryCreateNew(UClass* Class, UObject* InParent,
                                       FName Name, EObjectFlags Flags,
                                       UObject* Context, FFeedbackContext* Warn) override;
};
```

## Demo 示例

以下示例展示如何在编辑器中注册一个自定义的 Sequencer Track Editor：

```cpp
// MyModulationTrackEditor.h
#pragma once

#include "AudioControlBusBaseTrackEditor.h"
#include "SequencerTrackEditor.h"

class FMyModulationTrackEditor : public FAudioControlBusBaseTrackEditor
{
public:
    FMyModulationTrackEditor(TSharedRef<ISequencer> InSequencer)
        : FAudioControlBusBaseTrackEditor(InSequencer)
    {
    }

    virtual ~FMyModulationTrackEditor() = default;

    static TSharedRef<ISequencerTrackEditor> CreateTrackEditor(TSharedRef<ISequencer> OwningSequencer)
    {
        return MakeShareable(new FMyModulationTrackEditor(OwningSequencer));
    }

    virtual FText GetDisplayName() const override;
    virtual void BuildAddTrackMenu(FMenuBuilder& MenuBuilder) override;
    virtual bool SupportsType(TSubclassOf<UMovieSceneTrack> Type) const override;
    virtual bool SupportsSequence(UMovieSceneSequence* InSequence) const override;
    virtual bool HandleAssetAdded(UObject* Asset, const FGuid& TargetObjectGuid) override;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaSound` | 调制系统与 MetaSound 音频图集成 |
| `WaveTable` | 调制补丁曲线编辑器复用 WaveTable 的曲线编辑 UI 框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `a438ef22` | Provide ownership mechanism to SoundControlBusMixes from CreateBusMixFromValue | 为 CreateBusMixFromValue 添加总线混合对象的所有权机制 |
| 2026-05-13 | `8e94bfef` | [Audio Modulation] [AudioModulationInsights] Added modulator activated/deactivated trace events so t | 添加调制器激活/停用追踪事件用于音频洞察分析 |
| 2026-04-28 | `784b2c19` | [Sequencer] - Fix for control bus track crashing when there is no parameter | 修复 Sequencer 中控制总线轨道在无参数时崩溃的问题 |
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 MetaSound 引脚类型注册及编辑器相关行为 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退导致 CIS 编译错误的变更 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2019 年 8 月，已有约 7 年历史
- **最近更新**：2026 年 5 月仍在持续更新，最近两个月内有 5 次提交
- **更新质量**：包括功能增强（所有权机制、追踪事件）、bug 修复（Sequencer 崩溃）和架构整合
- **模块成熟度**：已从实验性状态毕业（`IsExperimentalVersion: false`），但仍未默认启用
- **注意**：`EnabledByDefault: false`，使用前必须在项目设置中手动启用
- **推荐**：推荐使用。这是 Epic 官方的音频调制实现，与 MetaSound 深度集成，适合需要复杂音频参数管理的项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioModulation)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioModulation/Tests)