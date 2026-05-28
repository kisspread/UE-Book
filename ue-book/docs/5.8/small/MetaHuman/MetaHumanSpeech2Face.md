# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师工具包 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（神经网络模型、动画资产、蓝图资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-05-06 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方推出的用于创建和驱动 MetaHuman 数字人角色的综合工具集。它不仅仅是一个简单的资产包，而是提供了一套完整的工作流，涵盖了从面部性能捕捉数据导入、面部动画生成（包括从音频和视频）、角色身份配置、到最终在引擎内驱动高保真 MetaHuman 角色的全部环节。其核心目的是降低创建逼真、高质量数字人角色动画的技术门槛，实现高效、批量化的制作流程。

## 使用场景

-   **数字人动画制作**：使用基于视频或音频的性能捕捉数据，自动驱动 MetaHuman 角色的面部表情和口型同步。
-   **游戏对话系统**：为大量游戏对话快速生成口型同步和基础表情动画，无需手动关键帧。
-   **虚拟主播与实时应用**：结合实时面捕方案，利用插件提供的低延迟动画解算器驱动 MetaHuman 进行实时直播或交互。
-   **影视与过场动画**：将专业演员的表演捕捉数据，精确转换为 MetaHuman 角色的面部动画。

## 蓝图用法

基于源码分析，`MetaHumanSpeech2Face` 模块主要提供 C++ 层的动画生成能力，但其配置结构体可用于蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Mood` | 设置生成的动画所表达的情绪。 | `FAudioDrivenAnimationSolveOverrides` |
| `Set Mood Intensity` | 设置情绪表达的强度。 | `FAudioDrivenAnimationSolveOverrides` |

### 使用示例（蓝图描述）

1.  创建一个 `FAudioDrivenAnimationSolveOverrides` 结构体变量。
2.  在蓝图中，通过该变量的引脚设置 `Mood` (如 `Happy`) 和 `MoodIntensity` (如 `0.8`)。
3.  将此结构体传递给能够执行音频驱动动画生成的节点（例如，在 `MetaHumanToolkit` 或 `MetaHumanPipeline` 模块中提供的封装节点）。

## C++ 用法

核心类 `FSpeech2Face` 用于从音频生成面部动画数据。它本身是编辑器专用（`WITH_EDITOR`）。

### 头文件引入

```cpp
#include "Speech2Face.h"
#include "AudioDrivenAnimationConfig.h"
```

### 基本用法

以下示例展示了如何使用 `FSpeech2Face` 从音频生成动画序列。

```cpp
// 来源: Public/Speech2Face.h
// 假设已加载音频资源 USoundWave* MySoundWave;
// 1. 创建FSpeech2Face实例
TUniquePtr<FSpeech2Face> Speech2Face = FSpeech2Face::Create();

if (Speech2Face)
{
    // 2. 配置参数
    FSpeech2Face::FAudioParams AudioParams(MySoundWave);
    float OutputFps = 30.0f;
    bool bGenerateBlinks = true;
    FAudioDrivenAnimationSolveOverrides SolveOverrides;
    SolveOverrides.Mood = EAudioDrivenAnimationMood::Happy;
    SolveOverrides.MoodIntensity = 0.7f;

    // 3. 设置情绪 (如果实例支持)
    // Speech2Face->SetMood(SolveOverrides.Mood);
    // Speech2Face->SetMoodIntensity(SolveOverrides.MoodIntensity);

    // 4. 生成动画
    TArray<FSpeech2Face::FAnimationFrame> FaceAnimation;
    TArray<FSpeech2Face::FAnimationFrame> HeadAnimation;

    bool bSuccess = Speech2Face->GenerateFaceAnimation(
        AudioParams,
        OutputFps,
        bGenerateBlinks,
        []() -> bool { return false; /* 取消回调，返回false表示继续 */ },
        FaceAnimation,
        HeadAnimation
    );

    if (bSuccess)
    {
        // 5. 使用生成的动画数据 (FaceAnimation, HeadAnimation)
        // 每个 FAnimationFrame 是一个 TMap<FString, float>，键为控制点名称，值为动画值。
        UE_LOG(LogTemp, Log, TEXT("Generated %d frames of face animation."), FaceAnimation.Num());
    }
}
```

### 进阶用法

在 `MetaHumanPipeline` 模块中，`FSpeech2Face` 通常作为一个处理节点，被集成到更复杂的数据处理流水线中，可以实现从原始素材（视频/音频）到最终 Skeletal Mesh 动画的全自动化流程。

## Demo 示例

一个最小化的、可运行的编辑器工具命令行示例，用于演示基本流程。

```cpp
// Speech2FaceDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Speech2Face.h"

class USoundWave;

class FSpeech2FaceDemo
{
public:
    static void GenerateDemoAnimation();
};
```

```cpp
// Speech2FaceDemo.cpp
#include "Speech2FaceDemo.h"
#include "AudioDrivenAnimationConfig.h"
#include "Sound/SoundWave.h"

void FSpeech2FaceDemo::GenerateDemoAnimation()
{
    // 注意：此为示意代码，实际音频资源加载逻辑需自行实现。
    USoundWave* DemoSoundWave = LoadObject<USoundWave>(nullptr, TEXT("/Game/Audio/DemoDialogue"));
    if (!DemoSoundWave)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to load demo sound wave."));
        return;
    }

    TUniquePtr<FSpeech2Face> Solver = FSpeech2Face::Create();
    if (!Solver)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create FSpeech2Face instance. Neural network models may be missing."));
        return;
    }

    FSpeech2Face::FAudioParams Params(DemoSoundWave, 0.0f, true, 0);
    float DesiredFps = 24.0f;
    bool bBlinks = true;

    TArray<FSpeech2Face::FAnimationFrame> FaceData;
    TArray<FSpeech2Face::FAnimationFrame> HeadData;

    // 生成动画
    bool bGenerated = Solver->GenerateFaceAnimation(
        Params,
        DesiredFps,
        bBlinks,
        []() { return false; }, // 不取消
        FaceData,
        HeadData
    );

    if (bGenerated)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully generated animation data with %d frames."), FaceData.Num());
        // 此处可以将 FaceData/HeadData 转换为 UE 的动画资产或进行下一步处理。
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Animation generation failed."));
    }
}
```

## 模块依赖

从 `MetaHumanSpeech2Face.Build.cs` 分析，使用者需要依赖以下核心模块。请注意，这是针对 `MetaHumanSpeech2Face` 子模块的依赖，整个插件的依赖更为复杂。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库，提供底层求解器支持。 |

**无特殊依赖（仅标准 Core/Engine/Slate 等）**：对于直接使用 `FSpeech2Face` API 的用法，除了 `MetaHumanCoreTechLib`，通常还需依赖 `NNE` 模块来加载神经网络模型。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 在启用身体追踪时禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**综合评价：活跃维护中**

- **年龄**：该插件于 2021 年左右随 MetaHuman 项目一同发布，作为核心工具链的一部分，已存在约 5 年。
- **更新频率与内容**：从提供的 git 历史看，更新非常频繁（最近几次更新集中在2天内），且都是**功能性更新和 Bug 修复**（如导出功能、渲染修复、缓存问题），表明 Epic Games 在持续投入开发。
- **活跃度**：作为 MetaHuman 生态系统的核心组件，预计会随着引擎版本持续更新。
- **已知限制**：`MetaHumanSpeech2Face` 模块明确标记为 `WITH_EDITOR`，意味着音频驱动动画生成功能**仅在编辑器环境可用**，不能用于打包后的运行时。
- **推荐使用**：对于任何涉及 MetaHuman 角色动画的项目，此插件是**官方推荐且必须使用**的工具包。对于非 MetaHuman 角色，其语音驱动动画生成的核心类 `FSpeech2Face` 具有参考价值，但集成复杂度较高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests)