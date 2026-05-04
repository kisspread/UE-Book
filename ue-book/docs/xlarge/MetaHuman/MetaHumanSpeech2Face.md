# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、配置、神经网络模型） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具链。它解决的核心问题是**将真实世界的表演（音频、视频）高效、高质量地转化为驱动 MetaHuman 数字角色面部动画的数据**。该插件提供了一套完整的端到端工作流，涵盖了从原始表演数据的采集、处理，到面部动画的求解、编辑和最终应用的整个流程。其存在是为了简化创建逼真数字人类动画的复杂过程，使开发者能够专注于创意而非底层技术实现。

## 使用场景

-   **语音驱动动画**：你有一段角色的语音录音（如播客、配音），需要快速生成与之匹配的口型和面部表情动画，用于游戏过场或虚拟主播。
-   **表演捕捉数据处理**：你使用 iPhone 或专业深度摄像头录制了演员的面部表演数据，需要将其处理并应用到 MetaHuman 角色上。
-   **批量处理动画**：你有大量的音频或视频文件需要转换为面部动画，希望自动化处理流程以提高效率。
-   **精细动画调整**：你已经生成了基础动画，但需要在 Sequencer 中对特定表情或口型进行微调。

## 蓝图用法

由于 MetaHuman Animator 的核心处理逻辑（如神经网络推理）主要在 C++ 层实现，且许多功能被标记为 `WITH_EDITOR`，其直接暴露给蓝图的节点相对有限。主要的蓝图交互集中在资产配置和数据结构上。

### 核心结构体

| 结构体/枚举 | 说明 | 所在头文件 |
|---|---|---|
| `FAudioDrivenAnimationModels` | 配置用于音频驱动动画的神经网络模型（音频编码器和动画解码器）的路径。 | `AudioDrivenAnimationConfig.h` |
| `FAudioDrivenAnimationSolveOverrides` | 覆盖音频驱动动画求解的参数，如情绪（Mood）和情绪强度。 | `AudioDrivenAnimationConfig.h` |
| `EAudioDrivenAnimationOutputControls` | 枚举，指定动画输出范围：全脸（FullFace）或仅嘴部（MouthOnly）。 | `AudioDrivenAnimationConfig.h` |
| `EAudioDrivenAnimationMood` | 枚举，定义可选的情绪类型（如快乐、悲伤、自动检测等）。 | `AudioDrivenAnimationMood.h` |

### 使用示例（蓝图描述）

1.  **配置模型**：在蓝图中创建一个 `FAudioDrivenAnimationModels` 结构体变量，并通过资产选择器为其 `AudioEncoder` 和 `AnimationDecoder` 属性指定正确的 NNE 模型资产路径。
2.  **设置求解参数**：创建一个 `FAudioDrivenAnimationSolveOverrides` 结构体变量，设置你想要的 `Mood`（例如 `EAudioDrivenAnimationMood::Happy`）和 `MoodIntensity`（0.0 到 1.0 之间）。
3.  **调用处理**：这些配置结构体通常作为参数传递给更高层的管理器或工具类（如 `MetaHumanToolkit` 模块中的类），由它们在后台调用 C++ 的 `FSpeech2Face` 等核心类来执行实际的动画生成。

## C++ 用法

核心的动画生成逻辑封装在 `FSpeech2Face` 类中，该类仅在编辑器环境下可用（`#if WITH_EDITOR`）。

### 头文件引入

```cpp
#include "Speech2Face.h"
#include "AudioDrivenAnimationConfig.h"
```

### 基本用法

以下示例展示了如何使用 `FSpeech2Face` 从音频生成面部动画数据。

```cpp
// 来源：基于 Speech2Face.h 中的 API 设计
#include "Speech2Face.h"
#include "Sound/SoundWave.h"

void GenerateAnimationFromAudio(const USoundWave* InSoundWave)
{
    // 1. 创建 FSpeech2Face 实例（加载神经网络模型）
    TUniquePtr<FSpeech2Face> Speech2FaceProcessor = FSpeech2Face::Create();
    if (!Speech2FaceProcessor)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create FSpeech2Face instance."));
        return;
    }

    // 2. (可选) 设置情绪参数
    Speech2FaceProcessor->SetMood(EAudioDrivenAnimationMood::Happy);
    Speech2FaceProcessor->SetMoodIntensity(0.8f);

    // 3. 准备音频参数
    FSpeech2Face::FAudioParams AudioParams(InSoundWave, 0.0f, true, 0);

    // 4. 生成动画
    TArray<FSpeech2Face::FAnimationFrame> FaceAnimation;
    TArray<FSpeech2Face::FAnimationFrame> HeadAnimation;
    float OutputFps = 30.0f;
    bool bGenerateBlinks = true;

    // 定义一个取消回调（可选）
    auto ShouldCancel = []() -> bool { return false; };

    bool bSuccess = Speech2FaceProcessor->GenerateFaceAnimation(
        AudioParams,
        OutputFps,
        bGenerateBlinks,
        ShouldCancel,
        FaceAnimation,
        HeadAnimation
    );

    if (bSuccess)
    {
        // 5. 使用生成的动画数据 (TArray<TMap<FString, float>>)
        // 每个 TMap 代表一帧，键是控制柄名称，值是控制柄数值。
        UE_LOG(LogTemp, Log, TEXT("Generated %d frames of face animation."), FaceAnimation.Num());
    }
}
```

### 进阶用法

使用自定义模型进行动画生成。

```cpp
// 来源：基于 AudioDrivenAnimationConfig.h 和 Speech2Face.h
#include "Speech2Face.h"
#include "AudioDrivenAnimationConfig.h"

void GenerateAnimationWithCustomModels(const USoundWave* InSoundWave)
{
    // 1. 配置自定义模型路径
    FAudioDrivenAnimationModels CustomModels;
    CustomModels.AudioEncoder = FSoftObjectPath("/Game/MLModels/MyAudioEncoder.MyAudioEncoder");
    CustomModels.AnimationDecoder = FSoftObjectPath("/Game/MLModels/MyAnimDecoder.MyAnimDecoder");

    // 2. 使用自定义模型创建实例
    TUniquePtr<FSpeech2Face> Speech2FaceProcessor = FSpeech2Face::Create(CustomModels);
    if (!Speech2FaceProcessor.IsValid())
    {
        return;
    }

    // 3. 配置求解覆盖参数
    FAudioDrivenAnimationSolveOverrides SolveOverrides;
    SolveOverrides.Mood = EAudioDrivenAnimationMood::AutoDetect;
    SolveOverrides.MoodIntensity = 1.0f;

    // 4. 后续生成流程与基本用法相同...
    // Speech2FaceProcessor->SetMood(SolveOverrides.Mood);
    // Speech2FaceProcessor->SetMoodIntensity(SolveOverrides.MoodIntensity);
    // ... 调用 GenerateFaceAnimation ...
}
```

## Demo 示例

一个最小化的控制台命令示例，用于从指定音频资产生成动画并输出帧数。

**MetaHumanSpeech2FaceDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMetaHumanSpeech2FaceDemo
{
public:
    static void RunDemo(const FString& SoundWavePath);
};
```

**MetaHumanSpeech2FaceDemo.cpp**
```cpp
#include "MetaHumanSpeech2FaceDemo.h"
#include "Speech2Face.h"
#include "Engine/World.h"
#include "Sound/SoundWave.h"
#include "AssetRegistry/AssetRegistryModule.h"

void FMetaHumanSpeech2FaceDemo::RunDemo(const FString& SoundWavePath)
{
#if WITH_EDITOR
    // 加载音频资产
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
    FAssetData AssetData = AssetRegistryModule.Get().GetAssetByObjectPath(*SoundWavePath);
    if (!AssetData.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("SoundWave asset not found: %s"), *SoundWavePath);
        return;
    }

    USoundWave* SoundWave = Cast<USoundWave>(AssetData.GetAsset());
    if (!SoundWave)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load SoundWave: %s"), *SoundWavePath);
        return;
    }

    // 创建处理器并生成动画
    TUniquePtr<FSpeech2Face> Processor = FSpeech2Face::Create();
    if (Processor.IsValid())
    {
        FSpeech2Face::FAudioParams Params(SoundWave);
        TArray<FSpeech2Face::FAnimationFrame> FaceAnim, HeadAnim;

        if (Processor->GenerateFaceAnimation(Params, 30.0f, true, [](){return false;}, FaceAnim, HeadAnim))
        {
            UE_LOG(LogTemp, Display, TEXT("Demo Success: Generated %d frames."), FaceAnim.Num());
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Demo Failed: Animation generation failed."));
        }
    }
#endif // WITH_EDITOR
}
```

## 模块依赖

`MetaHumanSpeech2Face` 模块依赖于插件内部的其他核心模块以及外部的神经网络推理框架。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供 MetaHuman 相关的核心类型、工具和基础功能。 |
| `NNE` | (Neural Network Engine) UE 的神经网络推理框架，用于加载和运行音频编码器与动画解码器模型。 |
| `MetaHumanPipeline` | 提供数据处理管道框架，`FSpeech2Face` 可能集成在此管道中。 |

## 维护状态

### 近期更新

```
- 9b414a8dd0d0 LiveLinkHub - Fix using wrong PropertyEditorModule method to unregister struct customizations
- fb15849136ed Audio solver mood refactoring
- 71c0fdfd700c [Backout] - CL46056783 [FYI] jon.cook #rnx Original CL Desc ----------------------------------------------------------------- Audio solver mood refactoring #rb jack.taylor
```

### 维护评价

MetaHuman Animator 是一个相对较新的插件（创建于 2024 年初），属于 Epic Games 的重点产品线。从近期提交记录看，它处于**活跃维护**状态。最近的提交涉及功能重构（音频求解器情绪系统）和编辑器集成修复（LiveLinkHub），表明团队正在持续改进其功能和稳定性。作为官方工具包，其长期支持和更新是有保障的。推荐在需要创建高质量 MetaHuman 面部动画的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/) (Unreal Engine 官方文档站)