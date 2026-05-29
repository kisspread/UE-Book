# Spatialization

> Plugin featuring a variety of basic audio spatialization solutions.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 空间音频 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Spatialization` (Runtime), `SpatializationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-01-25 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization) | |

## 用途

此插件为虚幻引擎提供了一套基础的音频空间化解决方案。其核心功能是实现了一种基于**双耳时间差（Interaural Time Difference, ITD）** 和**双耳声级差（Interaural Level Difference, ILD）** 的简单立体声声像（Panning）算法。它通过为每个声源创建延迟线和增益调节器，模拟声音到达左右耳的时间和强度差异，从而在立体声输出中创造声音的方向感和距离感。插件主要面向需要基础空间音频效果，但无需复杂头部相关传输函数（HRTF）处理的项目。

## 使用场景

- 你的游戏项目需要基础的立体声空间音频效果来增强沉浸感，例如简单的左右声场定位。
- 你正在开发一个原型或小型项目，需要快速集成空间音频功能，而无需处理复杂的HRTF滤波或物理声学模拟。
- 你希望为游戏中的UI音效、环境音效或非关键战斗音效提供方向感，但对精确的3D空间化要求不高。
- 你的目标平台主要使用立体声输出（如耳机或双声道扬声器），而非多声道环绕声系统。

## 蓝图用法

此插件的大部分核心功能是通过C++接口和工厂模式暴露的，**没有设计为蓝图友好**。经过源码分析，未发现任何标记为 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 的函数或属性。空间化器的创建、配置和生命周期管理主要在C++层面进行。

唯一的蓝图可配置项来自 `UITDSpatializationSourceSettings` 类，它继承自 `USpatializationPluginSourceSettingsBase`，允许在编辑器中为特定音频组件调整空间化参数。

### 可配置属性（在音频组件上）

| 属性 | 说明 | 所在类 |
|---|---|---|
| `bEnableILD` | 是否启用基于声级差（ILD）的声像控制。 | `UITDSpatializationSourceSettings` |
| `PanningIntensityOverDistance` | 一个距离-强度曲线，控制声像效果随距离变化的强度（Y轴 0.0-1.0）。 | `UITDSpatializationSourceSettings` |

**配置说明**：这些属性通常需要在音频组件的 `Spatialization Settings` 或项目设置中进行调整。由于插件默认未启用，需要先通过代码或项目设置激活相关的空间化插件。

## C++ 用法

### 核心概念

插件通过两个关键接口工作：
1.  `IAudioSpatialization`: 空间化算法的具体实现（例如 `FITDSpatialization`）。
2.  `IAudioSpatializationFactory`: 用于创建空间化算法实例的工厂（例如 `FITDSpatializationPluginFactory`）。

引擎通过工厂查找并实例化合适的空间化器。

### 头文件引入

```cpp
#include "ITDSpatializer.h"
#include "ITDSpatializationSourceSettings.h"
#include "SpatializationModule.h"
```

### 基本用法：实现自定义空间化器

以下代码展示了如何创建一个基于该插件框架的自定义空间化器。核心是继承 `IAudioSpatialization` 接口并实现其方法。

**来源文件**: `Public/ITDSpatializer.h`

```cpp
// MyCustomSpatializer.h
#pragma once

#include "IAudioSpatialization.h"

class FMyCustomSpatializer : public IAudioSpatialization
{
public:
    FMyCustomSpatializer() = default;
    virtual ~FMyCustomSpatializer() = default;

    // IAudioSpatialization interface
    virtual void Initialize(const FAudioPluginInitializationParams InitializationParams) override
    {
        // 初始化你的资源，如采样率、缓冲区大小等
        UE_LOG(LogAudio, Log, TEXT("Custom Spatializer Initialized. Sample Rate: %f, Num Sources: %d"),
            InitializationParams.SampleRate, InitializationParams.NumSources);
    }

    virtual void Shutdown() override
    {
        // 清理资源
    }

    virtual void OnInitSource(const uint32 SourceId, const FName& AudioComponentUserId, USpatializationPluginSourceSettingsBase* InSettings) override
    {
        // 当一个音频源开始播放时调用，可以在这里为其初始化特定数据
    }

    virtual void OnReleaseSource(const uint32 SourceId) override
    {
        // 当一个音频源停止播放时调用，清理其特定数据
    }

    virtual void ProcessAudio(const FAudioPluginSourceInputData& InputData, FAudioPluginSourceOutputData& OutputData) override
    {
        // 核心处理函数，将单声道输入混合到立体声输出
        // InputData包含输入音频数据、声源位置、监听器位置等
        // OutputData包含输出缓冲区（通常是左声道和右声道）
        
        // 简单示例：直接将单声道输入复制到左右声道（无空间化）
        if (InputData.NumInputChannels == 1 && OutputData.NumOutputChannels == 2)
        {
            const float* InputAudio = InputData.AudioBuffer->GetData();
            float* LeftOutput = OutputData.AudioBuffer->GetData();
            float* RightOutput = LeftOutput + InputData.AudioBuffer->Num(); // 假设输出缓冲区是交错或连续排列的

            for (int32 i = 0; i < InputData.AudioBuffer->Num(); ++i)
            {
                LeftOutput[i] = InputAudio[i];  // 实际应加入空间化计算
                RightOutput[i] = InputAudio[i]; // 实际应加入空间化计算
            }
        }
    }
};
```

### 进阶用法：注册自定义空间化器工厂

要让引擎识别并使用你的自定义空间化器，你需要创建一个对应的工厂类，并通过模块的 `StartupModule` 函数注册它。

**来源文件**: `Public/SpatializationModule.h`, `Public/ITDSpatializer.h`

```cpp
// MyCustomSpatializerFactory.h
#pragma once

#include "IAudioSpatialization.h"

class FMyCustomSpatializerFactory : public IAudioSpatializationFactory
{
public:
    virtual FString GetDisplayName() override
    {
        return TEXT("My Custom Spatializer");
    }

    virtual bool SupportsPlatform(const FString& PlatformName) override
    {
        return true; // 或根据平台进行过滤
    }

    virtual TAudioSpatializationPtr CreateNewSpatializationPlugin(FAudioDevice* OwningDevice) override
    {
        return MakeShared<FMyCustomSpatializer, ESPMode::ThreadSafe>();
    }

    virtual int32 GetMaxSupportedChannels() override
    {
        return 2; // 支持立体声输出
    }
};

// 在你的游戏模块或音频模块的StartupModule中注册工厂
void FMyGameModule::StartupModule()
{
    // ... 其他初始化 ...
    
    if (FSpatializationModule* SpatializationModule = FModuleManager::GetModulePtr<FSpatializationModule>(“Spatialization”))
    {
        // SpatializationModule 可能提供了注册接口，或者你需要直接与音频设备交互
        // 具体注册方式取决于引擎版本和插件设计，通常需要获取音频设备并注册工厂。
        // 以下是伪代码逻辑：
        // if (GEngine && GEngine->GetMainAudioDevice())
        // {
        //     GEngine->GetMainAudioDevice()->RegisterSpatializationPluginFactory(MakeShared<FMyCustomSpatializerFactory>());
        // }
    }
}
```

## Demo 示例

一个最小化但完整的自定义空间化器实现示例。

**MySimpleSpatializer.h**
```cpp
#pragma once

#include "IAudioSpatialization.h"

class FMySimpleSpatializer : public IAudioSpatialization
{
public:
    virtual void Initialize(const FAudioPluginInitializationParams InitializationParams) override;
    virtual void Shutdown() override;
    virtual void OnInitSource(const uint32 SourceId, const FName& AudioComponentUserId, USpatializationPluginSourceSettingsBase* InSettings) override;
    virtual void OnReleaseSource(const uint32 SourceId) override;
    virtual void ProcessAudio(const FAudioPluginSourceInputData& InputData, FAudioPluginSourceOutputData& OutputData) override;
};
```

**MySimpleSpatializer.cpp**
```cpp
#include "MySimpleSpatializer.h"

void FMySimpleSpatializer::Initialize(const FAudioPluginInitializationParams InitializationParams)
{
    // 初始化
}

void FMySimpleSpatializer::Shutdown()
{
    // 清理
}

void FMySimpleSpatializer::OnInitSource(const uint32 SourceId, const FName& AudioComponentUserId, USpatializationPluginSourceSettingsBase* InSettings)
{
    // 初始化声源
}

void FMySimpleSpatializer::OnReleaseSource(const uint32 SourceId)
{
    // 释放声源
}

void FMySimpleSpatializer::ProcessAudio(const FAudioPluginSourceInputData& InputData, FAudioPluginSourceOutputData& OutputData)
{
    // 一个极其简单的声像控制示例：基于声源的X坐标计算左右声道增益
    if (InputData.NumInputChannels < 1 || OutputData.NumOutputChannels < 2 || !InputData.AudioBuffer || !OutputData.AudioBuffer)
    {
        return;
    }

    const FVector& SourcePosition = InputData.SpatializationParams.Position;
    // 归一化X坐标到[-1, 1]范围（假设声场宽度为200单位）
    const float Pan = FMath::Clamp(SourcePosition.X / 100.0f, -1.0f, 1.0f);

    // 计算左右声道增益（简单线性平移）
    const float LeftGain = FMath::Clamp(0.5f - Pan * 0.5f, 0.0f, 1.0f);
    const float RightGain = FMath::Clamp(0.5f + Pan * 0.5f, 0.0f, 1.0f);

    const float* InputDataPtr = InputData.AudioBuffer->GetData();
    float* OutputBufferPtr = OutputData.AudioBuffer->GetData();
    const int32 NumSamples = InputData.AudioBuffer->Num();

    // 假设输出缓冲区是交错存储的 [L0, R0, L1, R1, ...]
    for (int32 i = 0; i < NumSamples; ++i)
    {
        const float Sample = InputDataPtr[i];
        OutputBufferPtr[i * 2] = Sample * LeftGain;      // 左声道
        OutputBufferPtr[i * 2 + 1] = Sample * RightGain; // 右声道
    }
}
```

## 模块依赖

从 Build.cs 分析，依赖非常基础。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | `Spatialization` 模块仅依赖核心引擎模块。`SpatializationEditor` 模块额外依赖 `UnrealEd`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 本次改动涉及内容浏览器菜单，与本插件核心功能无关。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie... | 代码生成宏的现代化更新，属于引擎通用代码维护，未改变插件功能。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins... | 进行DLL导出符号标准化，属于底层构建和二进制兼容性维护，未改变功能。 |

### 维护评价

该插件**创建于2019年**，已有约6年历史。从最近的提交记录看，近期的更新（2025-2026年）均为引擎通用的代码维护和现代化工作（如宏更新、符号导出），**并未对插件自身的核心空间化功能进行实质性更新或改进**。最后一次有意义的功能性提交要追溯到更早之前。

**评价**：
- **维护状态**：**维护不活跃**。该插件的核心功能在近几年没有演进，似乎处于“无人管理”的状态。
- **推荐程度**：**谨慎使用**。它提供了一个可用且基础的立体声空间化方案，适合学习原理或用于对音频质量要求不高的简单原型项目。对于正式或商业项目，尤其是需要更高质量空间音频效果（如HRTF、遮挡、混响等）的项目，**强烈建议使用更新的、更活跃维护的音频空间化插件或解决方案**。
- **已知限制**：功能非常基础，仅支持双声道输出，算法简单，且缺乏现代空间音频特性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization)
- [官方文档]() (无)
- [测试用例]() (在提供的源码信息中未发现明确的测试文件)