# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、资产类型） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-10-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个大型综合性工具集插件，旨在为在 Unreal Engine 中创建、编辑和动画化逼真的数字人类（MetaHuman）提供完整的工作流支持。它不仅仅是一个单一功能的插件，而是一个包含多个紧密协作模块的平台，解决了从基础模型配置、身份管理、表演捕捉数据导入、面部动画生成（包括音频驱动和视频驱动）到最终在 Sequencer 中编辑和合成的全流程问题。

它存在的核心价值是：将创建电影级数字人类角色的复杂过程工具化和流程化，降低艺术家和技术美术的使用门槛，并确保在 UE 生态内高质量的集成。

## 使用场景

*   你正在开发一个需要高质量数字人类角色的项目（如电影、剧集、广告或高端游戏）。
*   你需要将演员的表演（通过音频、视频或动作捕捉设备）实时或离线地应用到 MetaHuman 角色上。
*   你希望基于语音自动生成匹配的口型和面部表情动画。
*   你需要在 UE 的 Sequencer 中对复杂的面部动画进行精细的编辑、分层和混合。
*   你的工作流涉及多个艺术家协同编辑同一个 MetaHuman 角色资产。

## 蓝图用法

本插件的核心功能多为编辑器工具和资产处理器，其公开的蓝图接口主要集中在配置和驱动层面。以下是从源码中提取的典型蓝图用法概述：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Mood` / `Set MoodIntensity` | 控制语音驱动动画的情绪倾向与强度 | `FSpeech2Face` (通过包装类) |
| `FAudioDrivenAnimationModels` | 配置用于音频动画生成的神经网络模型资产路径 | `USTRUCT` |
| `FAudioDrivenAnimationSolveOverrides` | 在编辑器中覆盖语音动画求解的参数（如情绪、强度） | `USTRUCT` |

### 使用示例（蓝图描述）

典型的蓝图工作流通常不直接操作 `FSpeech2Face` C++ 类，而是使用插件提供的编辑器工具或资产类型。一个简化的交互描述如下：
1.  在 Content Browser 中创建 `MetaHuman Identity` 资产，用于定义角色的拓扑和绑定。
2.  导入或捕获表演数据（如 `.wav` 音频文件），创建 `MetaHuman Capture Source`。
3.  使用 `MetaHuman Toolkit` 面板，选择目标角色和捕获源，选择“Audio Driven Animation”处理器。
4.  在处理器设置中，指定 `FAudioDrivenAnimationModels` 中的模型资产，并通过 `FAudioDrivenAnimationSolveOverrides` 调整情绪参数。
5.  执行处理，生成动画数据并应用到角色骨骼上。

## C++ 用法

以下示例重点展示如何通过 C++ 接口，使用 `MetaHumanSpeech2Face` 模块的核心功能生成语音驱动动画。

### 头文件引入

```cpp
#include "Speech2Face.h"
#include "AudioDrivenAnimationConfig.h"
```

### 基本用法

基本的语音驱动面部动画生成流程。
*来源文件: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanSpeech2Face/Public/Speech2Face.h`*

```cpp
// 假设已经有一个加载好的 USoundWave* 指针 MySpeechRecording
// 以及一个用于接收动画数据的数组
TArray<FSpeech2Face::FAnimationFrame> OutFaceAnimation;
TArray<FSpeech2Face::FAnimationFrame> OutHeadAnimation;

// 1. 创建 FSpeech2Face 实例（会加载必要的神经网络模型）
TUniquePtr<FSpeech2Face> Speech2FaceInstance = FSpeech2Face::Create();

if (Speech2FaceInstance.IsValid())
{
    // 2. 设置情绪参数（可选）
    Speech2FaceInstance->SetMood(EAudioDrivenAnimationMood::Happy);
    Speech2FaceInstance->SetMoodIntensity(0.8f);

    // 3. 配置音频参数
    FSpeech2Face::FAudioParams AudioParams(MySpeechRecording, 0.0f, true, 0);

    // 4. 定义取消回调（用于长时间生成时取消）
    auto ShouldCancel = []() -> bool { return false; /* 在实际使用中可检查外部状态 */ };

    // 5. 生成动画
    bool bSuccess = Speech2FaceInstance->GenerateFaceAnimation(
        AudioParams,
        24.0f, // 输出动画帧率，例如 24 FPS
        true,  // 是否生成眨眼动画
        ShouldCancel,
        OutFaceAnimation,
        OutHeadAnimation
    );

    if (bSuccess)
    {
        // 现在 OutFaceAnimation 和 OutHeadAnimation 中存储了按帧排列的控制值
        // 每一帧是一个 TMap<FString, float>，映射了骨骼控制名称到数值
        // 这些数据可以进一步应用到 ControlRig 或其他动画系统上
    }
}
```

### 进阶用法

展示如何使用自定义模型和获取辅助信息。
*来源文件: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanSpeech2Face/Public/Speech2Face.h` 及 `Private/Speech2FaceInternal.h`*

```cpp
#include "NNE.h" // 神经网络引擎模块

// 1. 使用自定义模型创建实例
FAudioDrivenAnimationModels CustomModels;
CustomModels.AudioEncoder = FSoftObjectPath("/Game/Path/To/MyAudioEncoderModel.MyAudioEncoderModel");
CustomModels.AnimationDecoder = FSoftObjectPath("/Game/Path/To/MyAnimDecoderModel.MyAnimDecoderModel");

TUniquePtr<FSpeech2Face> CustomSpeech2Face = FSpeech2Face::Create(CustomModels);

// 2. 使用命名空间中的辅助函数处理动画数据
if (OutFaceAnimation.Num() > 0)
{
    // 获取第一帧的数据
    TMap<FString, float>& FirstFrame = OutFaceAnimation[0];

    // 替换 GUI 控件名称为原始的 Rig 逻辑控件名称（用于直接驱动 ControlRig）
    UE::MetaHuman::ReplaceHeadGuiControlsWithRaw(FirstFrame);

    // 仅提取与嘴部相关的控件
    TSet<FString> MouthControls = UE::MetaHuman::GetMouthOnlyRawControls();
    // 可以基于此集合过滤 FirstFrame，实现仅嘴部动画的应用。

    // 从控件数据中提取头部姿态变换
    if (OutHeadAnimation.Num() > 0)
    {
        FTransform HeadPoseTransform = UE::MetaHuman::GetHeadPoseTransformFromRawControls(OutHeadAnimation[0]);
        // 可以将此变换应用到角色的头部骨骼上。
    }
}
```

## Demo 示例

以下是一个完整的、可编译的 C++ 类示例，演示如何封装 `FSpeech2Face` 以用于游戏或运行时场景（注意：`FSpeech2Face` 本身标记为 `#if WITH_EDITOR`，此示例假设在编辑器工具或特殊构建配置中使用）。

**MetaHumanSpeechGeneratorComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Speech2Face.h"
#include "MetaHumanSpeechGeneratorComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UMetaHumanSpeechGeneratorComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Speech2Face")
    TSoftObjectPtr<USoundWave> SpeechRecording;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Speech2Face")
    EAudioDrivenAnimationMood Mood = EAudioDrivenAnimationMood::Neutral;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Speech2Face")
    float MoodIntensity = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Speech2Face")
    float OutputAnimationFps = 30.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Speech2Face")
    bool bGenerateBlinks = true;

    UFUNCTION(BlueprintCallable, Category = "Speech2Face")
    void GenerateAnimationAsync();

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAnimationGenerated, const TArray<FSpeech2Face::FAnimationFrame>&, FaceAnimation, const TArray<FSpeech2Face::FAnimationFrame>&, HeadAnimation);

    UPROPERTY(BlueprintAssignable, Category = "Speech2Face")
    FOnAnimationGenerated OnAnimationGenerated;

private:
    TUniquePtr<FSpeech2Face> Speech2FaceInstance;
    FGraphEventRef GenerationTask;
};
```

**MetaHumanSpeechGeneratorComponent.cpp**
```cpp
#include "MetaHumanSpeechGeneratorComponent.h"
#include "Sound/SoundWave.h"
#include "Async/Async.h"

void UMetaHumanSpeechGeneratorComponent::GenerateAnimationAsync()
{
    if (!SpeechRecording.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("SpeechRecording is not valid."));
        return;
    }

    // 在游戏线程中初始化实例（加载模型）
    if (!Speech2FaceInstance.IsValid())
    {
        Speech2FaceInstance = FSpeech2Face::Create();
    }

    if (!Speech2FaceInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create FSpeech2Face instance."));
        return;
    }

    Speech2FaceInstance->SetMood(Mood);
    Speech2FaceInstance->SetMoodIntensity(MoodIntensity);

    USoundWave* SoundWave = SpeechRecording.Get();
    FSpeech2Face::FAudioParams AudioParams(SoundWave);

    // 将耗时的生成任务放到后台线程
    GenerationTask = Async(EAsyncExecution::Thread, [this, AudioParams]()
    {
        TArray<FSpeech2Face::FAnimationFrame> FaceAnim, HeadAnim;
        auto ShouldCancel = [](){ return false; };

        bool bSuccess = Speech2FaceInstance->GenerateFaceAnimation(
            AudioParams,
            OutputAnimationFps,
            bGenerateBlinks,
            ShouldCancel,
            FaceAnim,
            HeadAnim
        );

        // 回到游戏线程广播结果
        AsyncTask(ENamedThreads::GameThread, [this, bSuccess, FaceAnim = MoveTemp(FaceAnim), HeadAnim = MoveTemp(HeadAnim)]()
        {
            if (bSuccess)
            {
                OnAnimationGenerated.Broadcast(FaceAnim, HeadAnim);
            }
            else
            {
                UE_LOG(LogTemp, Warning, TEXT("Animation generation failed."));
            }
            GenerationTask = nullptr;
        });
    });
}
```

## 模块依赖

**核心外部依赖（汇总）：**
| 模块 | 用途 |
|---|---|
| `ControlRig` / `ControlRigDeveloper` | 面部动画的核心驱动和蓝图集成框架 |
| `SkeletalMeshUtilitiesCommon` | 处理骨骼网格体相关的通用工具 |
| `NNE` (Neural Network Engine) | 加载和运行用于音频/视觉处理的神经网络模型 |
| `MetaHumanSDKEditor` | 与 MetaHuman 核心 SDK 编辑器功能集成 |

*注：许多子模块依赖 UnrealEd，表明这是一个主要面向编辑器工具的插件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 在启用了身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 角色的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体添加了动画序列导出功能 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 的缓存问题 |

### 维护评价

**活跃维护**。
MetaHuman Animator 是 Epic Games 的旗舰技术之一，维护状态非常积极。从近期提交记录可以看出，团队仍在持续进行功能增强（如为现有网格导出动画）、性能优化和关键 bug 修复（渲染、缓存问题）。该插件与 MetaHuman 生态紧密相连，预计会长期得到官方支持和更新。作为创建高端数字人类角色的核心工具，**强烈推荐**在符合项目需求的场景下使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-in-unreal-engine/)