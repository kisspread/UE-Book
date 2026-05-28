# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模型、配置资产） |
| 模块 | `MetaHumanSpeech2Face` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

`MetaHumanAnimator` 是 Epic Games 官方提供的 MetaHuman 角色动画工具包。`MetaHumanSpeech2Face` 模块是其核心子模块之一，专注于从音频（语音）驱动生成面部动画。它利用神经网络模型，分析输入的音频数据，自动预测并生成对应的面部控制器（Rig Controls）数值，从而实现音频驱动的面部动画（如口型同步、表情）。该模块的输出可直接驱动 MetaHuman 的面部绑定。

## 使用场景

- 你需要为一段录音或语音音频快速生成对应的面部口型动画。
- 你希望基于音频自动为 MetaHuman 角色添加眨眼、头部运动等细微表情。
- 你在进行动画捕捉后处理，希望使用 AI 算法优化或补充面部动画数据。
- 你需要批量处理大量语音资产，为每个音频生成对应的面部动画。

## 蓝图用法

`MetaHumanSpeech2Face` 模块本身主要提供 C++ 接口。其生成的动画数据以及配置结构体（如 `FAudioDrivenAnimationModels`, `FAudioDrivenAnimationSolveOverrides`）通常在其他更上层的模块或编辑器工具中通过蓝图暴露。以下为核心数据结构和枚举：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FAudioDrivenAnimationModels` | 配置用于音频驱动动画的神经网络模型（音频编码器和动画解码器）的资产路径。 | `USTRUCT` |
| `FAudioDrivenAnimationSolveOverrides` | 配置动画求解的覆盖参数，如情绪（Mood）和情绪强度。 | `USTRUCT` |
| `EAudioDrivenAnimationMood` | 枚举，定义动画输出的情绪类型（如中性、快乐等）。 | `UENUM` |
| `EAudioDrivenAnimationOutputControls` | 枚举，控制动画输出是影响全脸还是仅嘴巴区域。 | `UENUM` |

### 使用示例（蓝图描述）

1.  **配置模型**: 创建一个 `FAudioDrivenAnimationModels` 结构体变量。在其属性中，指定 `AudioEncoder` 和 `AnimationDecoder` 指向项目中的 NNE (Neural Network Engine) 模型资产。
2.  **配置情绪覆盖**: 创建一个 `FAudioDrivenAnimationSolveOverrides` 结构体变量。设置 `Mood` 属性为你想要的情绪（例如 `EAudioDrivenAnimationMood::Happy`），并调整 `MoodIntensity` 来控制强度。
3.  **驱动求解器**: 将上述配置传递给 MetaHuman Animator 工具链中的相应蓝图节点或 C++ 调用，即可使用指定的模型和情绪设置来处理音频并生成动画。

## C++ 用法

`FSpeech2Face` 类是该模块的核心 C++ 接口，用于执行实际的音频到动画转换。

### 头文件引入

```cpp
#include "Speech2Face.h"
#include "AudioDrivenAnimationConfig.h"
```

### 基本用法

创建一个 `FSpeech2Face` 实例，并使用它来生成面部动画。此过程主要在编辑器环境中（`WITH_EDITOR`）进行。

```cpp
// 来源: Public/Speech2Face.h

// 1. 创建 FSpeech2Face 实例
TUniquePtr<FSpeech2Face> Speech2FaceInstance = FSpeech2Face::Create();
if (!Speech2FaceInstance.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create FSpeech2Face instance."));
    return;
}

// 2. 准备音频参数 (需要一个 USoundWave 指针)
TWeakObjectPtr<const USoundWave> MySoundWave = /* ... */;
FSpeech2Face::FAudioParams AudioParams(MySoundWave);

// 3. 配置输出参数
float OutputFps = 24.0f; // 期望的输出动画帧率
bool bGenerateBlinks = true; // 是否生成眨眼动画
TArray<FSpeech2Face::FAnimationFrame> FaceAnimationData;
TArray<FSpeech2Face::FAnimationFrame> HeadAnimationData;

// 4. 生成动画 (包含一个用于取消的回调)
bool bSuccess = Speech2FaceInstance->GenerateFaceAnimation(
    AudioParams,
    OutputFps,
    bGenerateBlinks,
    []() { return false; }, // 取消回调，始终返回 false 表示不取消
    FaceAnimationData,
    HeadAnimationData
);

if (bSuccess)
{
    // FaceAnimationData 和 HeadAnimationData 现在包含了逐帧的控制器数值
    // 每个 FAnimationFrame 是一个 TMap<FString, float>，键为控制器名称，值为该帧的值。
}
```

### 进阶用法

你可以设置动画的情绪倾向，并使用自定义模型路径。

```cpp
// 来源: Public/Speech2Face.h, Public/AudioDrivenAnimationConfig.h

// 1. 使用自定义模型创建实例
FAudioDrivenAnimationModels CustomModels;
CustomModels.AudioEncoder = FSoftObjectPath("/Path/To/Your/CustomAudioEncoder.CustomAudioEncoder");
CustomModels.AnimationDecoder = FSoftObjectPath("/Path/To/Your/CustomAnimationDecoder.CustomAnimationDecoder");

TUniquePtr<FSpeech2Face> CustomSpeech2Face = FSpeech2Face::Create(CustomModels);

// 2. 设置情绪 (在生成动画之前调用)
CustomSpeech2Face->SetMood(EAudioDrivenAnimationMood::Sad);
CustomSpeech2Face->SetMoodIntensity(0.8f); // 强度 0-1

// 3. 之后再调用 GenerateFaceAnimation 即可获得带有情绪倾向的动画。
```

## Demo 示例

以下是一个完整的最小 C++ 示例，演示如何在编辑器工具或命令行插件中使用 `MetaHumanSpeech2Face` 模块生成动画。

**MySpeech2FaceTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class USoundWave;

class FMySpeech2FaceTool
{
public:
    void RunGenerationTest(USoundWave* InSoundWave);

private:
    void ProcessAnimationData(const TArray<TMap<FString, float>>& InFaceAnimation, const TArray<TMap<FString, float>>& InHeadAnimation);
};
```

**MySpeech2FaceTool.cpp**
```cpp
#include "MySpeech2FaceTool.h"
#include "Speech2Face.h"
#include "Sound/SoundWave.h"

void FMySpeech2FaceTool::RunGenerationTest(USoundWave* InSoundWave)
{
    if (!InSoundWave)
    {
        UE_LOG(LogTemp, Error, TEXT("Invalid SoundWave provided."));
        return;
    }

    // 创建实例
    TUniquePtr<FSpeech2Face> Animator = FSpeech2Face::Create();
    if (!Animator)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize FSpeech2Face."));
        return;
    }

    // 设置一些情绪
    Animator->SetMood(EAudioDrivenAnimationMood::Happy);
    Animator->SetMoodIntensity(0.6f);

    // 准备参数
    FSpeech2Face::FAudioParams Params(InSoundWave);
    TArray<FSpeech2Face::FAnimationFrame> OutFaceAnims;
    TArray<FSpeech2Face::FAnimationFrame> OutHeadAnims;

    // 生成动画
    const float TargetFps = 30.0f;
    const bool bDoBlinks = true;
    bool bSuccess = Animator->GenerateFaceAnimation(
        Params,
        TargetFps,
        bDoBlinks,
        []() -> bool { /* 这里可以加入你的取消逻辑，例如检查某个全局标志 */ return false; },
        OutFaceAnims,
        OutHeadAnims
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Generated %d frames of face animation."), OutFaceAnims.Num());
        ProcessAnimationData(OutFaceAnims, OutHeadAnims);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Face animation generation failed."));
    }
}

void FMySpeech2FaceTool::ProcessAnimationData(const TArray<TMap<FString, float>>& InFaceAnimation, const TArray<TMap<FString, float>>& InHeadAnimation)
{
    // 在这里处理生成的动画数据
    // 例如，将数据写入文件，或应用到骨骼网格体
    for (int32 FrameIndex = 0; FrameIndex < InFaceAnimation.Num(); ++FrameIndex)
    {
        const auto& FaceFrame = InFaceAnimation[FrameIndex];
        // 访问特定控制器的值，例如：
        // float BrowDownValue = FaceFrame.FindRef(TEXT("CTRL_L_brow_down.ty"));
    }
}
```

## 模块依赖

要使用 `MetaHumanSpeech2Face` 模块的功能，你的模块需要在 `Build.cs` 中添加以下特殊依赖项。

| 模块 | 用途 |
|---|---|
| `NNE` | UE 的神经网络引擎，用于加载和运行驱动动画生成的 AI 模型。 |
| `MetasoundFrontend` | 可能用于处理音频元数据和波形。 |
| `MetaHumanSpeech2Face` | 本模块，提供核心的 `FSpeech2Face` 类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 启用身体追踪时，过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHumanAnimator] 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**活跃维护**。`MetaHumanAnimator` 是 Epic Games 当前重点推进的 MetaHuman 生态系统的核心组成部分。从最近的 Git 提交记录来看（截至 2026 年 5 月），该插件仍在持续进行功能增强和问题修复，例如添加对身体追踪的支持、修复渲染问题、优化 Sequencer 集成等。虽然无法确定其确切创建时间，但鉴于其与 MetaHuman 技术栈的紧密关联以及最近的更新频率，可以判断它处于**活跃维护**状态，并且是生产可用的。

**推荐使用**。对于任何需要基于音频驱动 MetaHuman 面部动画的项目，这是一个官方且功能强大的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (无)
- [测试用例]() (位于 `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest/` 等目录，但具体文件未在此次分析中列出)