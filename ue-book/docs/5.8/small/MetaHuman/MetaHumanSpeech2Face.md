# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（神经网络模型资产、音频动画配置资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-05（估算） |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

---

## 用途

本文档聚焦 MetaHuman Animator 插件中的 **MetaHumanSpeech2Face** 模块。

**MetaHumanSpeech2Face** 模块的核心功能是：**从语音音频自动生成面部动画驱动数据**。它使用深度学习模型（神经网络），将 `USoundWave` 音频资产转换为一组面部骨骼控制值（RigLogic 面板控件），从而驱动 MetaHuman 角色的面部表情和嘴型同步。

这个模块解决的核心问题是：**自动化唇语同步和面部表情生成**。传统方法需要美术师手工 K 帧或使用昂贵的动作捕捉设备，而 Speech2Face 只需一段语音录音，就能自动生成高质量的面部动画，包括：
- 嘴唇、下巴、舌头的运动（唇语同步）
- 眼睛眨眼
- 眉毛运动
- 头部姿态（平移和旋转）
- 情绪状态（如高兴、悲伤、愤怒等）

## 使用场景

- 你有一个 MetaHuman 角色的对话音频，需要自动生成嘴型同步动画 → 用 MetaHumanSpeech2Face
- 你正在开发过场动画对话系统，需要快速生成大量对话的面部动画 → 用 MetaHumanSpeech2Face
- 你需要在批量处理流水线中自动化面部动画生成 → 结合 MetaHumanBatchProcessor 使用
- 你需要自定义情绪强度来调整生成动画的表达程度 → 用 SetMood / SetMoodIntensity

## 蓝图用法

MetaHumanSpeech2Face 的核心类 `FSpeech2Face` 是纯 C++ API（`#if WITH_EDITOR`），不直接暴露蓝图节点。蓝图可通过配置结构体 `FAudioDrivenAnimationModels` 和 `FAudioDrivenAnimationSolveOverrides` 来配置参数。

### 可用蓝图结构体

| 结构体 | 说明 |
|---|---|
| `FAudioDrivenAnimationModels` | 配置音频编码器和动画解码器的 NNE 模型资产路径 |
| `FAudioDrivenAnimationSolveOverrides` | 配置情绪类型（Mood）和情绪强度（MoodIntensity） |

### 蓝图枚举

| 枚举 | 值 | 说明 |
|---|---|---|
| `EAudioDrivenAnimationOutputControls` | `FullFace` | 驱动全脸控制 |
| `EAudioDrivenAnimationOutputControls` | `MouthOnly` | 仅驱动嘴部控制 |

### 配置示例（蓝图描述）

在蓝图中，你可以通过 `FAudioDrivenAnimationSolveOverrides` 结构体属性来配置：
1. 将 `Mood` 设置为 `AutoDetect`、`Neutral`、`Happy`、`Sad`、`Angry` 等情绪枚举值
2. 将 `MoodIntensity` 滑块调整到 0.0 - 1.0 之间，控制情绪表达的强烈程度

## C++ 用法

### 头文件引入

```cpp
#include "Speech2Face.h"
#include "AudioDrivenAnimationConfig.h"
```

### 基本用法

创建 `FSpeech2Face` 实例并生成面部动画：

```cpp
// 来源: Public/Speech2Face.h - FSpeech2Face::Create / GenerateFaceAnimation

#if WITH_EDITOR
#include "Speech2Face.h"
#include "AudioDrivenAnimationConfig.h"
#include "Sound/SoundWave.h"

void GenerateFaceAnimFromSpeech(const USoundWave* InSpeechWave)
{
    // 1. 创建 FSpeech2Face 实例（加载神经网络模型）
    TUniquePtr<FSpeech2Face> Speech2Face = FSpeech2Face::Create();
    if (!Speech2Face.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Speech2Face instance"));
        return;
    }

    // 2. 设置情绪参数（可选）
    Speech2Face->SetMood(EAudioDrivenAnimationMood::Neutral);
    Speech2Face->SetMoodIntensity(0.8f);

    // 3. 准备音频参数
    FSpeech2Face::FAudioParams AudioParams(
        InSpeechWave,    // USoundWave 资产
        0.0f,            // 音频起始偏移（秒）
        true,            // 是否混合声道（downmix）
        0                // 使用哪个声道
    );

    // 4. 生成动画
    TArray<FSpeech2Face::FAnimationFrame> FaceAnimation;
    TArray<FSpeech2Face::FAnimationFrame> HeadAnimation;

    bool bSuccess = Speech2Face->GenerateFaceAnimation(
        AudioParams,
        30.0f,           // 输出动画帧率
        true,            // 是否生成眨眼动画
        []() { return false; }, // 取消回调（返回 false 表示不取消）
        FaceAnimation,   // 输出：面部动画帧
        HeadAnimation    // 输出：头部动画帧
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Generated %d frames of face animation, %d frames of head animation"),
            FaceAnimation.Num(), HeadAnimation.Num());

        // FaceAnimation 每帧是一个 TMap<FString, float>
        // 键是控制名称（如 "CTRL_L_mouth_cornerPull.ty"），值是控制值
        for (const auto& Frame : FaceAnimation)
        {
            for (const auto& [ControlName, ControlValue] : Frame)
            {
                // 使用 ControlValue 驱动对应的 RigLogic 控件
            }
        }
    }
}
#endif
```

### 进阶用法

使用自定义模型并处理头部姿态：

```cpp
// 来源: Public/Speech2Face.h + Private/DataDefs.h

#if WITH_EDITOR
#include "Speech2Face.h"
#include "AudioDrivenAnimationConfig.h"

void AdvancedSpeech2FaceUsage(const USoundWave* InSpeechWave)
{
    // 1. 使用自定义 NNE 模型
    FAudioDrivenAnimationModels Models;
    Models.AudioEncoder = FSoftObjectPath("/Game/Models/MyAudioEncoder.MyAudioEncoder");
    Models.AnimationDecoder = FSoftObjectPath("/Game/Models/MyAnimDecoder.MyAnimDecoder");

    TUniquePtr<FSpeech2Face> Speech2Face = FSpeech2Face::Create(Models);
    if (!Speech2Face.IsValid())
    {
        return;
    }

    // 2. 设置情绪为"高兴"，强度为 0.6
    Speech2Face->SetMood(EAudioDrivenAnimationMood::Happy);
    Speech2Face->SetMoodIntensity(0.6f);

    // 3. 从音频的第 2 秒开始，使用第 2 个声道
    FSpeech2Face::FAudioParams AudioParams(InSpeechWave, 2.0f, false, 1);

    // 4. 生成 24fps 动画，包含眨眼
    TArray<FSpeech2Face::FAnimationFrame> FaceAnimation;
    TArray<FSpeech2Face::FAnimationFrame> HeadAnimation;

    Speech2Face->GenerateFaceAnimation(
        AudioParams, 24.0f, true,
        []() { return false; },
        FaceAnimation, HeadAnimation
    );

    // 5. 提取头部姿态变换
    for (const auto& HeadFrame : HeadAnimation)
    {
        FTransform HeadTransform = UE::MetaHuman::GetHeadPoseTransformFromRawControls(HeadFrame);
        // HeadTransform 包含头部的位置和旋转
        FVector HeadTranslation = HeadTransform.GetTranslation();
        FRotator HeadRotation = HeadTransform.Rotator();
    }

    // 6. 转换 GUI 控件名为原始控件名
    for (auto& Frame : FaceAnimation)
    {
        UE::MetaHuman::ReplaceHeadGuiControlsWithRaw(Frame);
    }

    // 7. 获取仅嘴部控件集合（用于过滤）
    TSet<FString> MouthOnlyControls = UE::MetaHuman::GetMouthOnlyRawControls();
}
#endif
```

## Demo 示例

### 完整最小示例

```cpp
// Speech2FaceDemo.h
#pragma once

#include "CoreMinimal.h"

class USoundWave;

class FSpeech2FaceDemo
{
public:
    /** 从音频资产生成面部动画数据并打印摘要 */
    static void RunDemo(const USoundWave* InSoundWave);
};
```

```cpp
// Speech2FaceDemo.cpp
#include "Speech2FaceDemo.h"
#include "Speech2Face.h"
#include "AudioDrivenAnimationConfig.h"
#include "Sound/SoundWave.h"

#if WITH_EDITOR

void FSpeech2FaceDemo::RunDemo(const USoundWave* InSoundWave)
{
    if (!InSoundWave)
    {
        UE_LOG(LogTemp, Warning, TEXT("Speech2FaceDemo: No sound wave provided"));
        return;
    }

    // 创建实例
    TUniquePtr<FSpeech2Face> Solver = FSpeech2Face::Create();
    if (!Solver.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Speech2FaceDemo: Failed to create solver"));
        return;
    }

    // 配置情绪
    Solver->SetMood(EAudioDrivenAnimationMood::Neutral);
    Solver->SetMoodIntensity(1.0f);

    // 设置音频参数（使用全部声道，从头开始）
    FSpeech2Face::FAudioParams Audio(InSoundWave, 0.0f, true, 0);

    // 生成动画
    TArray<FSpeech2Face::FAnimationFrame> FaceAnim;
    TArray<FSpeech2Face::FAnimationFrame> HeadAnim;

    bool bOK = Solver->GenerateFaceAnimation(
        Audio, 30.0f, true,
        []() -> bool { return false; },
        FaceAnim, HeadAnim
    );

    if (bOK && FaceAnim.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Speech2FaceDemo: Generated %d frames"), FaceAnim.Num());

        // 输出第一帧的所有控制值
        const auto& FirstFrame = FaceAnim[0];
        for (const auto& [Name, Value] : FirstFrame)
        {
            UE_LOG(LogTemp, Verbose, TEXT("  %s = %.4f"), *Name, Value);
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Speech2FaceDemo: Animation generation failed"));
    }
}

#else

void FSpeech2FaceDemo::RunDemo(const USoundWave* InSoundWave)
{
    UE_LOG(LogTemp, Warning, TEXT("Speech2FaceDemo: Only available in editor builds"));
}

#endif
```

## 模块依赖

MetaHumanSpeech2Face 模块的 Build.cs 中列出了以下关键依赖（省略 Core/Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎，用于加载和运行音频编码器和动画解码器模型 |
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供 RigLogic 相关基础设施 |
| `AudioPlatformConfiguration` | 音频平台配置，用于音频采样率和格式处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

MetaHumanSpeech2Face 是 MetaHuman Animator 的核心子模块之一，属于 Epic Games 官方维护的产品级功能。

**积极方面**：
- 作为 MetaHuman 生态的核心组件，由 Epic Games 团队持续维护
- 最近更新频繁（2026 年 5 月有多次提交），表明项目处于**活跃维护**状态
- 使用 NNE（Neural Network Engine）作为推理后端，架构现代化
- API 设计清晰，支持自定义模型替换

**注意事项**：
- 核心生成逻辑（`FSpeech2Face`）仅在 `WITH_EDITOR` 环境下可用，运行时需要通过 Sequencer 或动画导出使用
- 音频处理上限为 30 秒（`RigLogicPredictorMaxAudioSamples`），超长音频需要分段处理
- 生成的原始动画为 50 FPS（`AudioEncoderOutputFps`），输出帧率通过最近邻算法重采样
- 需要有效的 NNE 模型资产（`FAudioDrivenAnimationModels`）才能工作
- 该模块是更大 MetaHuman 插件生态的一部分，单独使用功能有限，通常需配合 MetaHuman 角色和 RigLogic 系统

**推荐**：✅ 推荐使用。对于使用 MetaHuman 角色的项目，这是生成对话面部动画的首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanSpeech2Face)
- [MetaHuman 官方文档](https://docs.unrealengine.com/en-US/metahuman-in-unreal-engine/)
- [NNE 模块文档](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE)