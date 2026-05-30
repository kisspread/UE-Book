# Spatialization

> Plugin featuring a variety of basic audio spatialization solutions.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音频空间化 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `Spatialization` (Runtime), `SpatializationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-01-25 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization) | |

## 用途

该插件提供了一套基础的音频空间化解决方案，核心是实现了简单的 **ITD (Interaural Time Difference，到达时间差)** 空间化算法。它通过为左右声道添加不同的延迟和增益差异，来模拟声音在人头部两侧到达耳朵的时间差和强度差，从而让玩家感知声音的方位。它解决的是在UE项目中快速实现基本3D音频定位的问题，适用于对空间化精度要求不高的场景。

## 使用场景

- 你的项目只需要简单的左右声道声像（Panning）定位，而不需要复杂的HRTF头部相关传输函数。
- 你正在开发一个性能受限（如移动端）的游戏，需要轻量级的音频空间化方案。
- 你需要快速原型化一个支持基本3D音频的游戏，而不需要依赖外部插件。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bEnableILD` | 是否启用基于声强差（Interaural Level Difference）的声像调节。 | `UITDSpatializationSourceSettings` |
| `PanningIntensityOverDistance` | 一条浮点曲线，用于根据声源距离（横轴）调整声像强度（纵轴，0.0-1.0）。 | `UITDSpatializationSourceSettings` |

### 使用示例（蓝图描述）

1.  在你的音频组件（Audio Component）或声音衰减（Sound Attenuation）设置中，找到“空间化插件”（Spatialization Plugin）选项。
2.  从下拉菜单中选择 **“Simple ITD”** 空间化插件。
3.  为了进一步配置该声源的空间化行为，可以创建一个 `UITDSpatializationSourceSettings` 资产。
4.  在该设置资产中，勾选 **“启用电平声像”（Enable Level Panning）** 来同时考虑响度差异。
5.  调整 **“随距离变化的声像强度”（PanningIntensityOverDistance）** 曲线，例如，你可以让声音在近距离时声像效果更明显，在远距离时效果减弱，模拟距离对声音方位感的影响。

## C++ 用法

### 头文件引入

```cpp
#include "SpatializationModule.h"
#include "ITDSpatializer.h"
```

### 基本用法

该插件主要通过UE的音频插件系统工作。通常在`IAudioSpatialization`接口的生命周期内使用。
```cpp
// 1. 初始化空间化插件实例（通常由音频设备管理，但展示了初始化流程）
FITDSpatialization Spatializer;
FAudioPluginInitializationParams InitParams; // 需要填充设备、采样率等信息
Spatializer.Initialize(InitParams);

// 2. 当音频源开始播放时，通知插件
uint32 SourceId = 123;
FName ComponentName = TEXT("MyAudioComponent");
Spatializer.OnInitSource(SourceId, ComponentName, nullptr); // Settings可传nullptr使用默认

// 3. 在音频渲染线程中处理音频数据
FAudioPluginSourceInputData InputData;
// ... 填充 InputData 的音频样本、位置等信息 ...
FAudioPluginSourceOutputData OutputData;
// ... 准备 OutputData 的缓冲区 ...
Spatializer.ProcessAudio(InputData, OutputData);
// 处理后的立体声数据在 OutputData 中。

// 4. 当音频源停止时释放
Spatializer.OnReleaseSource(SourceId);

// 5. 关闭插件
Spatializer.Shutdown();
```
*(基于 `FITDSpatialization` 类的接口实现推断)*

### 进阶用法

可以使用自定义的 `UITDSpatializationSourceSettings` 来为不同的声源配置独特的空间化行为。
```cpp
// 假设你有一个 UPROPERTY 指向设置对象
UPROPERTY(EditAnywhere, Category = "Audio")
UITDSpatializationSourceSettings* MySpatialSettings;

// 当初始化音频源时，将此设置传递给插件
Spatializer.OnInitSource(SourceId, ComponentName, MySpatialSettings);

// 也可以动态修改设置中的曲线，这会影响后续 ProcessAudio 的计算
FRuntimeFloatCurve NewCurve;
// ... 构建你自己的距离-声像强度曲线 ...
if (MySpatialSettings)
{
    MySpatialSettings->PanningIntensityOverDistance = NewCurve;
}
```
*(基于 `ITDSpatializationSourceSettings.h` 和 `OnInitSource` 接口推断)*

## Demo 示例

一个最小的演示如何创建并使用 `FITDSpatialization` 类的C++示例。
```cpp
// MinimalSpatializationDemo.h
#pragma once
#include "CoreMinimal.h"

class FMinimalSpatializationDemo
{
public:
    void Initialize();
    void ProcessSomeAudio(const float* InputSamples, int32 NumInputSamples, float* OutputLeft, float* OutputRight);
    void Shutdown();

private:
    // 我们使用的空间化插件实例
    TUniquePtr<class FITDSpatialization> SpatializationPlugin;
    uint32 DemoSourceId = 0;
};
```

```cpp
// MinimalSpatializationDemo.cpp
#include "MinimalSpatializationDemo.h"
#include "ITDSpatializer.h" // 包含FITDSpatialization定义

void FMinimalSpatializationDemo::Initialize()
{
    // 创建空间化实例
    SpatializationPlugin = MakeUnique<FITDSpatialization>();

    // 初始化参数 (在实际音频引擎中，这些参数由系统提供)
    FAudioPluginInitializationParams InitParams;
    InitParams.AudioDevicePtr = nullptr; // 实际需要一个有效的音频设备指针
    InitParams.SampleRate = 48000.0f;
    InitParams.NumSources = 1;
    InitParams.AudioMixerModuleName = TEXT("AudioMixer"); // 通常有固定值

    SpatializationPlugin->Initialize(InitParams);

    // 初始化一个虚拟音频源
    DemoSourceId = 1;
    SpatializationPlugin->OnInitSource(DemoSourceId, FName(TEXT("DemoComponent")), nullptr);
}

void FMinimalSpatializationDemo::ProcessSomeAudio(const float* InputSamples, int32 NumInputSamples, float* OutputLeft, float* OutputRight)
{
    if (!SpatializationPlugin) return;

    // 准备输入输出数据结构 (这是一个高度简化的示例)
    FAudioPluginSourceInputData InputData;
    InputData.SourceId = DemoSourceId;
    InputData.AudioData = InputSamples; // 单声道输入
    InputData.NumChannels = 1;
    InputData.NumFrames = NumInputSamples;
    // InputData.Position 需要设置声源的世界坐标

    FAudioPluginSourceOutputData OutputData;
    // 为立体声输出分配缓冲区
    TArray<float> OutputBuffer;
    OutputBuffer.SetNumUninitialized(NumInputSamples * 2); // 左+右
    OutputData.AudioData = OutputBuffer.GetData();
    OutputData.NumChannels = 2;
    OutputData.NumFrames = NumInputSamples;

    // 调用处理
    SpatializationPlugin->ProcessAudio(InputData, OutputData);

    // 将结果拷贝出来 (实际应用中，OutputData的缓冲区通常直接混音到主输出)
    FMemory::Memcpy(OutputLeft, OutputData.AudioData, sizeof(float) * NumInputSamples);
    FMemory::Memcpy(OutputRight, OutputData.AudioData + NumInputSamples, sizeof(float) * NumInputSamples);
}

void FMinimalSpatializationDemo::Shutdown()
{
    if (SpatializationPlugin)
    {
        SpatializationPlugin->OnReleaseSource(DemoSourceId);
        SpatializationPlugin->Shutdown();
        SpatializationPlugin.Reset();
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/AudioMixer 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器的“添加”菜单中音频相关菜单项更新，插件可能被关联。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie… | 为生成的代码文件添加内联宏，属于引擎底层代码现代化维护。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins… | 进行DLL导出符号规范化，属于引擎构建系统和代码规范维护。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录的常规提交，具体内容不明确。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件内链接至HTTPS协议，属于安全合规性维护。 |

### 维护评价

该插件创建于2019年，已有超过7年历史。从近期提交记录看，2025年仍有与引擎构建系统相关的底层维护更新，表明它作为引擎内置基础组件仍被纳入维护范围。然而，这些更新主要涉及代码规范和构建系统，而非插件功能本身。其核心空间化算法（ITD）自创建以来似乎没有重大功能更新或增强。鉴于它是引擎官方提供的基础解决方案，稳定性和兼容性有保障，但功能相对简单和古老。**推荐用于需要快速实现基本、轻量级空间化效果的项目**，但对于高质量的3D音频需求，建议评估更现代的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization/Tests) （如果存在）