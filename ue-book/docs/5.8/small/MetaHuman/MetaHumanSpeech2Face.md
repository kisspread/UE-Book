# MetaHuman Speech2Face

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 语音驱动面部动画 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（神经网络模型资产） |
| 模块 | `MetaHumanSpeech2Face` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-01-01 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Speech2Face 是 MetaHuman Animator 工具套件中的语音驱动面部动画模块。它解决的核心问题是：**如何从一段语音录音自动生成面部动画数据**。

该模块内部使用两个神经网络模型（通过 UE 的 NNE 推理框架运行）：

1. **音频编码器（AudioEncoder）**：将原始音频特征化为模型可理解的向量表示，采样率 16kHz
2. **动画解码器（AnimationDecoder / RigLogicPredictor）**：将音频特征解码为 RigLogic 面部骨骼控制值

生成的动画数据覆盖完整的面部区域——眉毛、眼睛（含眨眼）、鼻子、嘴巴、下巴、舌头以及头部姿态。输出为 RigLogic rig 控制器名称到浮点值的映射，可直接驱动 MetaHuman 角色的面部动画。

## 使用场景

- 你有一段语音录制（SoundWave 资产），需要为 MetaHuman 角色自动生成口型同步和面部表情动画 → 使用 Speech2Face
- 你正在制作对话密集的过场动画，需要快速生成面部动画草稿 → 使用 Speech2Face 作为起点再手动调整
- 你需要从音频批量生成面部动画序列 → 使用 Speech2Face API 结合 Sequencer 导出
- 你需要不同的情绪风格（中性、高兴、悲伤、愤怒等）来影响生成的面部动画 → 使用 SetMood 配置情绪参数
- 你只需要口部动画，不需要眉毛和眼睛的变化 → 使用 `MouthOnly` 输出模式

## 蓝图用法

Speech2Face 核心类 `FSpeech2Face` 被 `#if WITH_EDITOR` 包裹，属于纯编辑器功能，不直接暴露为蓝图节点。但 `AudioDrivenAnimationConfig.h` 中定义的配置结构体是蓝图可见的：

### 核心结构体

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FAudioDrivenAnimationModels` | 指定音频编码器和动画解码器的 NNE 模型资产路径 | `USTRUCT(BlueprintType)` |
| `FAudioDrivenAnimationSolveOverrides` | 覆盖情绪类型和情绪强度参数 | `USTRUCT(BlueprintType)` |
| `EAudioDrivenAnimationMood` | 情绪枚举（Neutral、Happy、Sad、Angry 等） | `UENUM(BlueprintType)` |
| `EAudioDrivenAnimationOutputControls` | 输出控制模式：FullFace（全脸）或 MouthOnly（仅嘴部） | `UENUM(BlueprintType)` |

### 使用示例

在 MetaHuman Animator 编辑器工具中，你可以通过属性面板配置以下参数：

1. **模型配置**：指定 `FAudioDrivenAnimationModels` 中的 AudioEncoder 和 AnimationDecoder 模型资产（.uasset 文件）
2. **情绪覆盖**：在 `FAudioDrivenAnimationSolveOverrides` 中设置 Mood（如 AutoDetect 自动检测、Neutral 中性、Happy 高兴）和 MoodIntensity（0.0-1.0 情绪强度）
3. **输出范围**：选择 FullFace（完整面部 76+ 控制器）或 MouthOnly（仅嘴部相关控制器）

## C++ 用法

### 头文件引入

```cpp
#include "Speech2Face.h"
#include "AudioDrivenAnimationConfig.h"
```

### 基本用法

以下示例展示如何从语音生成面部动画（来源：`Public/Speech2Face.h`）：

```cpp
// 注意：所有 API 都在 #if WITH_EDITOR 内，仅编辑器可用

// 1. 创建 FSpeech2Face 实例（内部加载神经网络模型）
TUniquePtr<FSpeech2Face> Speech2Face = FSpeech2Face::Create();
if (!Speech2Face.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create Speech2Face instance"));
    return;
}

// 2. 配置音频参数
TObjectPtr<USoundWave> SoundWave = /* 从资产加载 */;
FSpeech2Face::FAudioParams AudioParams(
    SoundWave,      // 语音录音资产
    0.0f,           // 音频起始偏移（秒）
    true,           // 是否混合声道（降混）
    0               // 使用的声道索引
);

// 3. 生成面部动画
TArray<FSpeech2Face::FAnimationFrame> FaceAnimation;
TArray<FSpeech2Face::FAnimationFrame> HeadAnimation;

bool bSuccess = Speech2Face->GenerateFaceAnimation(
    AudioParams,
    24.0f,                                          // 输出动画帧率
    true,                                           // 是否生成眨眼
    []() { return false; },                         // 取消回调（不取消）
    FaceAnimation,                                  // 输出：面部动画
    HeadAnimation                                   // 输出：头部姿态动画
);

// 4. 遍历动画数据
for (int32 FrameIdx = 0; FrameIdx < FaceAnimation.Num(); ++FrameIdx)
{
    const auto& Frame = FaceAnimation[FrameIdx];
    // Frame 是 TMap<FString, float>，键为 rig 控制器名称，值为浮点值
    for (const auto& [ControlName, Value] : Frame)
    {
        // 例如: "CTRL_L_brow_down.ty" -> -0.5f
        // 例如: "CTRL_C_jaw.ty" -> 0.3f
    }
}
```

### 进阶用法

带情绪设置和自定义模型的高级用法：

```cpp
// 使用自定义 NNE 模型
FAudioDrivenAnimationModels CustomModels;
CustomModels.AudioEncoder = FSoftObjectPath("/Game/Models/CustomAudioEncoder.CustomAudioEncoder");
CustomModels.AnimationDecoder = FSoftObjectPath("/Game/Models/CustomAnimDecoder.CustomAnimDecoder");

TUniquePtr<FSpeech2Face> Speech2Face = FSpeech2Face::Create(CustomModels);

// 设置情绪参数
Speech2Face->SetMood(EAudioDrivenAnimationMood::Happy);
Speech2Face->SetMoodIntensity(0.7f);  // 70% 高兴强度

// 生成动画（带取消支持）
TArray<FSpeech2Face::FAnimationFrame> FaceAnim;
TArray<FSpeech2Face::FAnimationFrame> HeadAnim;

std::atomic<bool> bCancelRequested{false};

bool bSuccess = Speech2Face->GenerateFaceAnimation(
    FSpeech2Face::FAudioParams(MySoundWave, 0.5f, true, 0),  // 跳过前 0.5 秒
    30.0f,       // 30 FPS 输出
    false,       // 不生成眨眼
    [&bCancelRequested]() { return bCancelRequested.load(); },  // 可取消
    FaceAnim,
    HeadAnim
);

// 头部姿态动画通过以下辅助函数转换为 Transform
if (HeadAnim.Num() > 0)
{
    FTransform HeadPose = UE::MetaHuman::GetHeadPoseTransformFromRawControls(HeadAnim[0]);
    // HeadPose 包含平移 (tx, ty, tz) 和旋转 (rx, ry, rz)
}

// 将 GUI 控制器名称转换为原始控制器名称
for (auto& Frame : FaceAnim)
{
    UE::MetaHuman::ReplaceHeadGuiControlsWithRaw(Frame);
}

// 获取仅嘴部控制器集合（用于过滤非嘴部动画）
TSet<FString> MouthControls = UE::MetaHuman::GetMouthOnlyRawControls();
```

## Demo 示例

以下是一个完整的最小示例，展示如何在编辑器工具中使用 Speech2Face 从音频生成动画：

```cpp
// Speech2FaceDemo.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Speech2FaceDemo.generated.h"

class USoundWave;
class FSpeech2Face;

UCLASS(BlueprintType)
class USpeech2FaceDemo : public UObject
{
    GENERATED_BODY()

public:
    /** 从音频资产生成面部动画数据 */
    UFUNCTION(BlueprintCallable, Category = "Speech2FaceDemo")
    bool GenerateAnimationFromAudio(USoundWave* InSoundWave, float InFps = 24.0f);

private:
    // Speech2Face 实例可复用
    TUniquePtr<FSpeech2Face> Speech2FaceInstance;
};
```

```cpp
// Speech2FaceDemo.cpp
#include "Speech2FaceDemo.h"
#include "Speech2Face.h"
#include "AudioDrivenAnimationConfig.h"
#include "Sound/SoundWave.h"

bool USpeech2FaceDemo::GenerateAnimationFromAudio(USoundWave* InSoundWave, float InFps)
{
    if (!InSoundWave)
    {
        UE_LOG(LogTemp, Error, TEXT("Invalid SoundWave asset"));
        return false;
    }

    // 创建或复用实例
    if (!Speech2FaceInstance.IsValid())
    {
        Speech2FaceInstance = FSpeech2Face::Create();
    }
    if (!Speech2FaceInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize Speech2Face"));
        return false;
    }

    // 使用中性情绪
    Speech2FaceInstance->SetMood(EAudioDrivenAnimationMood::Neutral);
    Speech2FaceInstance->SetMoodIntensity(1.0f);

    // 构造音频参数
    FSpeech2Face::FAudioParams AudioParams(
        InSoundWave,
        0.0f,   // 无偏移
        true,   // 混合声道
        0       // 第 0 声道
    );

    // 生成动画
    TArray<FSpeech2Face::FAnimationFrame> FaceAnimation;
    TArray<FSpeech2Face::FAnimationFrame> HeadAnimation;

    bool bSuccess = Speech2FaceInstance->GenerateFaceAnimation(
        AudioParams,
        InFps,
        true,                                       // 生成眨眼
        []() { return false; },                     // 不取消
        FaceAnimation,
        HeadAnimation
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Generated %d frames of face animation"), FaceAnimation.Num());
        UE_LOG(LogTemp, Log, TEXT("Generated %d frames of head animation"), HeadAnimation.Num());
    }

    return bSuccess;
}
```

## 模块依赖

本模块（MetaHumanSpeech2Face）的 Build.cs 未在提供的信息中列出完整依赖。但根据源码分析，其独特依赖如下：

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络推理框架，用于加载和运行音频编码器/动画解码器模型 |
| `AudioMixer` / `AudioPlatform` | 音频采样和重采样处理（SoundWave PCM 数据提取） |
| `ControlRig` | RigLogic 控制器数据结构 |
| `MetaHumanCore` | MetaHuman 核心工具库 |
| `RigLogicModule` | RigLogic 面部骨骼驱动系统 |

其余依赖为标准 Core/Engine/Slate 等常见模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**活跃维护** ✅

MetaHumanAnimator 是 Epic Games 重点维护的旗舰插件，用于 MetaHuman 角色的完整动画制作流程。最近的更新集中在：

- **身体追踪集成**：近期多次提交涉及身体追踪功能的集成和修复
- **Sequencer 集成**：持续改进与 UE Sequencer 的协作，修复缓存和导出问题
- **渲染修复**：修复 MetaHuman 角色的渲染问题

该插件包含 29+ 个子模块和 544 个源文件，是 Epic 官方支持的大型专业工具套件。虽然 `IsBetaVersion=false`，但 Speech2Face 核心 API 全部在 `#if WITH_EDITOR` 内，意味着仅在编辑器环境中可用，不适合作为运行时语音驱动解决方案。

**推荐使用**：如果你的项目需要为 MetaHuman 角色生成语音驱动的面部动画，这是唯一官方支持的解决方案。注意需要配合 MetaHuman 模型资产和 NNE 模型资产使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator/)
- [MetaHuman Speech2Face 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanSpeech2Face)