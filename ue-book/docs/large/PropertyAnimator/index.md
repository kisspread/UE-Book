# Property Animator

> Re-usable behaviors to animate the value of one or more properties

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（曲线资产、预设） |
| 模块 | `PropertyAnimator` (Runtime), `PropertyAnimatorEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PropertyAnimator) | |

## 用途

PropertyAnimator 是 UE5 Motion Design（虚拟制片）工具链的一部分，用于对 Actor 的**任意属性**施加可复用的程序化动画行为。它解决的核心问题是：**在不编写蓝图/代码的情况下，让属性值随时间自动变化**（如位置抖动、缩放脉冲、旋转振荡、文字计数器等）。

与传统 Sequencer 动画不同，PropertyAnimator 是**运行时评估**的——动画行为绑定在组件上，无需 Sequencer 播放即可生效。它通过 PropertyAnimatorCore 插件提供的基础设施（属性链接、上下文、时间源、预设系统）实现了一个高度模块化的动画框架。

### 关键特性

- **多种内置动画器**：Curve（曲线）、Wiggle（抖动）、Time（线性时间）、SoundWave（音频驱动）、Counter（数字计数）、Clock（时钟显示）等
- **支持 Float / Vector / Rotator / String 属性**，每种类型有独立的 Context 处理振幅映射
- **预设系统**：内置 Location / Rotation / Scale / Visibility / Text 等预设，一键应用常见动画
- **Sequencer 集成**：通过自定义 Wave 和 Easing 双通道，可在 Sequencer 中直接使用 Wave/Easing 曲线
- **可扩展**：继承 `UPropertyAnimatorCoreBase` 即可创建自定义动画器

### 依赖插件

- **PropertyAnimatorCore** — 核心框架（属性链接、上下文、时间源、预设基础设施）
- **Text3D** — 文字属性动画支持
- **AudioSynesthesia** — SoundWave 动画器的音频分析

## 使用场景

- 你需要让场景中的灯光/物体持续做呼吸、脉冲、抖动动画 → 用 Curve / Wiggle / Pulse 动画器
- 你需要一个实时计数器显示在 3D 文字上（如倒计时、金额） → 用 Counter 动画器
- 你需要一个实时时钟显示在场景中 → 用 Clock 动画器
- 你需要让属性值跟随音频响度变化（如灯光随音乐跳动） → 用 SoundWave 动画器
- 你需要对 Location/Rotation/Scale 快速施加循环动画 → 用内置预设

## 内置动画器一览

### 数值动画器（继承 UPropertyAnimatorNumericBase）

| 动画器 | 说明 | 状态 |
|---|---|---|
| `UPropertyAnimatorCurve` | 基于曲线采样的波形动画，支持 EaseIn/Out | ✅ 推荐 |
| `UPropertyAnimatorWiggle` | 随机抖动，可调频率 | ✅ 推荐 |
| `UPropertyAnimatorTime` | 线性时间递增 | ✅ 可用 |
| `UPropertyAnimatorSoundWave` | 基于音频响度的动画 | ✅ 可用 |
| `UPropertyAnimatorOscillate` | 正弦/余弦/方波等振荡 | ⚠️ 已废弃（用 Curve 替代） |
| `UPropertyAnimatorBounce` | 弹跳效果 | ⚠️ 已废弃（用 Curve 替代） |
| `UPropertyAnimatorPulse` | 脉冲/缓动效果 | ⚠️ 已废弃（用 Curve 替代） |

### 文字动画器（继承 UPropertyAnimatorTextBase）

| 动画器 | 说明 |
|---|---|
| `UPropertyAnimatorCounter` | 数字计数器，支持自定义格式（千分位、精度、填充等） |
| `UPropertyAnimatorClock` | 实时时钟，支持本地时间/倒计时/秒表模式 |

### 属性上下文（Property Context）

| 上下文类 | 用途 |
|---|---|
| `UPropertyAnimatorFloatContext` | Float/Double 属性，定义 AmplitudeMin/Max 振幅映射 |
| `UPropertyAnimatorVectorContext` | FVector 属性，每轴独立振幅 |
| `UPropertyAnimatorRotatorContext` | FRotator 属性，每轴独立振幅 |

### 内置预设

| 预设 | 目标属性 |
|---|---|
| `UPropertyAnimatorPresetLocation` | SceneComponent RelativeLocation (X/Y/Z) |
| `UPropertyAnimatorPresetRotation` | SceneComponent RelativeRotation (Pitch/Yaw/Roll) |
| `UPropertyAnimatorPresetScale` | SceneComponent RelativeScale3D (X/Y/Z) |
| `UPropertyAnimatorPresetVisibility` | SceneComponent Visibility |
| `UPropertyAnimatorPresetText` | Text3D 文字总属性 |
| `UPropertyAnimatorPresetTextLocation` | Text3D 字符位置 |
| `UPropertyAnimatorPresetTextRotation` | Text3D 字符旋转 |
| `UPropertyAnimatorPresetTextScale` | Text3D 字符缩放 |
| `UPropertyAnimatorPresetTextVisibility` | Text3D 字符可见性 |

## 蓝图用法

PropertyAnimator 主要通过编辑器 Details 面板操作，而非蓝图节点。但动画器类暴露了 BlueprintReadWrite 属性，可以在蓝图中动态修改。

### 核心属性（UPropertyAnimatorNumericBase）

| 属性 | 类型 | 说明 |
|---|---|---|
| `Magnitude` | float | 动画幅度，默认 1.0 |
| `CycleMode` | EPropertyAnimatorCycleMode | 循环模式：DoOnce / Loop / PingPong |
| `CycleDuration` | float | 单次循环时长（秒） |
| `CycleGapDuration` | float | 循环间隔时长（秒） |
| `bRandomTimeOffset` | bool | 启用随机时间偏移 |
| `Seed` | int32 | 随机种子 |

### 核心枚举

**EPropertyAnimatorCycleMode**
- `DoOnce` — 只播放一次
- `Loop` — 循环播放
- `PingPong` — 来回往返

**EPropertyAnimatorOscillateFunction**（Oscillate 动画器）
- `Sine`, `Cosine`, `Square`, `InvertedSquare`, `Sawtooth`, `Triangle`

**EPropertyAnimatorWaveFunction**（Wave 曲线系统）
- `Sine`, `Cosine`, `Square`, `InvertedSquare`, `Sawtooth`, `Triangle`, `Bounce`, `Pulse`, `Perlin`

**EPropertyAnimatorEasingFunction**（缓动函数）
- `Linear`, `Sine`, `Quad`, `Cubic`, `Quart`, `Quint`, `Expo`, `Circ`, `Back`, `Elastic`, `Bounce`

## C++ 用法

### 头文件引入

```cpp
#include "Animators/PropertyAnimatorCurve.h"
#include "Animators/PropertyAnimatorWiggle.h"
#include "Animators/PropertyAnimatorCounter.h"
#include "PropertyAnimatorShared.h"
```

### 基本用法 — 数学函数

PropertyAnimator 内置了一套完整的 Easing 和 Wave 数学函数，可独立使用：

```cpp
#include "PropertyAnimatorShared.h"

// 缓动函数：输入 0-1 的进度，输出缓动后的值
float Result = UE::PropertyAnimator::Easing::Ease(
    0.5f,
    EPropertyAnimatorEasingFunction::Bounce,
    EPropertyAnimatorEasingType::InOut
);

// 波形函数：输入时间、振幅、频率、偏移
double WaveValue = UE::PropertyAnimator::Wave::Wave(
    CurrentTime,    // InTime
    1.0,            // InAmplitude
    2.0,            // InFrequency
    0.0,            // InOffset
    EPropertyAnimatorWaveFunction::Sine
);
```

来源：`Source/PropertyAnimator/Public/PropertyAnimatorShared.h`

### 进阶用法 — 自定义动画器

创建自定义动画器需要继承 `UPropertyAnimatorNumericBase` 并实现 `EvaluateProperty`：

```cpp
// MyCustomAnimator.h
#pragma once
#include "Animators/PropertyAnimatorNumericBase.h"
#include "MyCustomAnimator.generated.h"

UCLASS(MinimalAPI, AutoExpandCategories=("Animator"))
class UMyCustomAnimator : public UPropertyAnimatorNumericBase
{
    GENERATED_BODY()

protected:
    virtual void OnAnimatorRegistered(FPropertyAnimatorCoreMetadata& InMetadata) override
    {
        InMetadata.DisplayName = FText::FromString(TEXT("My Custom"));
        InMetadata.Category = FText::FromString(TEXT("Custom"));
    }

    virtual bool EvaluateProperty(
        const FPropertyAnimatorCoreData& InPropertyData,
        UPropertyAnimatorCoreContext* InContext,
        FInstancedPropertyBag& InParameters,
        FInstancedPropertyBag& OutEvaluationResult) const override
    {
        // 获取时间源提供的时间
        // 计算并输出属性值
        OutEvaluationResult.SetValueDouble(FName("Result"), FMath::Sin(GetWorld()->GetTimeSeconds()));
        return true;
    }
};
```

## Sequencer 集成

PropertyAnimator 在 Sequencer 中注册了两种自定义通道：

- **Wave 通道** (`FPropertyAnimatorWaveDoubleChannel`) — 使用波形函数（Sine/Cosine/Square 等）在 Sequencer 中生成程序化曲线
- **Easing 通道** (`FPropertyAnimatorEasingDoubleChannel`) — 使用缓动函数生成 In/Out/InOut 缓动曲线

这些通道通过 `FPropertyAnimatorEditorModule` 在编辑器启动时注册到 Sequencer 模块。

### MovieScene 工具

```cpp
#include "MovieScene/PropertyAnimatorMovieSceneUtils.h"

// 获取 Section 的基础时间
FFrameTime BaseTime = FPropertyAnimatorMovieSceneUtils::GetBaseTime(InSection, InMovieScene);
double BaseSeconds = FPropertyAnimatorMovieSceneUtils::GetBaseSeconds(InSection);
```

## 模块依赖

### PropertyAnimator (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础功能 |
| `MovieScene` | Sequencer 集成 |
| `PropertyAnimatorCore` | 核心框架（属性链接、上下文、时间源、预设） |
| `ApplicationCore` | 应用核心（私有） |
| `AudioSynesthesia` | 音频分析（SoundWave 动画器） |
| `CoreUObject` | UObject 系统 |
| `DeveloperSettings` | 设置系统（Counter 格式预设） |
| `Engine` | 引擎核心 |
| `Json` | 预设序列化 |
| `MovieSceneTracks` | Sequencer Track 支持 |
| `Text3D` | 3D 文字属性支持 |

### PropertyAnimatorEditor (Editor)

| 模块 | 用途 |
|---|---|
| `PropertyAnimator` | Runtime 模块 |
| `PropertyAnimatorCore` | 核心框架 |
| `PropertyAnimatorCoreEditor` | 核心编辑器支持 |
| `Sequencer` | Sequencer 编辑器集成 |
| `SequencerCore` | Sequencer 核心 |
| `MovieSceneTools` | MovieScene 编辑器工具 |
| `UnrealEd` | 编辑器框架 |
| `ToolMenus` | 菜单扩展 |
| `Slate` / `SlateCore` | UI 框架 |
| `Projects` | 项目设置 |

## Demo 示例

以下示例展示如何在 C++ 中以编程方式创建一个 Curve 动画器并应用到 Actor：

```cpp
// MyActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class UPropertyAnimatorCurve;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    UPROPERTY(VisibleAnywhere)
    USceneComponent* Root;

    UPROPERTY(VisibleAnywhere)
    UPropertyAnimatorCurve* CurveAnimator;
};

// MyActor.cpp
#include "MyActor.h"
#include "Animators/PropertyAnimatorCurve.h"
#include "Components/SceneComponent.h"

AMyActor::AMyActor()
{
    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    RootComponent = Root;

    // PropertyAnimator 通常由编辑器工具自动创建和管理
    // 以下为概念性示例，实际使用中通过 Details 面板操作
    CurveAnimator = CreateDefaultSubobject<UPropertyAnimatorCurve>(TEXT("CurveAnimator"));
}
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "PropertyAnimator",
    "PropertyAnimatorCore"
});
```

**实际使用流程**（编辑器操作）：
1. 选择 Actor → Details 面板 → 添加 `PropertyAnimator` 组件
2. 在组件上选择动画器类型（如 Curve）
3. 设置 Wave 曲线、CycleDuration、Magnitude 等参数
4. 通过 Link Property 按钮关联目标属性（如 RelativeLocation.Z）
5. 设置振幅范围（AmplitudeMin/Max）
6. 播放即可看到动画效果

## 维护状态

### 近期更新

| 日期 | Hash | 内容 | 解读 |
|---|---|---|---|
| 2025-10-03 | `bde2ffb7` | Fixed clock animator with missing format and padding | 修复 Clock 动画器格式和填充显示问题 |
| 2025-10-03 | `12579b17` | Deprecating legacy bounce, oscillate, pulse animator | 标记 Bounce/Oscillate/Pulse 为废弃，统一用 Curve 替代 |
| 2025-09-23 | `df329aa2` | Removed beta tag from motion design plugins | 正式脱离 Beta 状态 |

### 维护评价

- **创建时间**：2024-01-28（在 Experimental 目录），2025-05 迁移到 VirtualProduction
- **维护状态**：🟢 **活跃维护** — 持续有功能更新和 bug 修复，最近更新在 2025-10
- **发展趋势**：正在从多个独立动画器（Bounce/Oscillate/Pulse）收敛到统一的 Curve 系统，架构在持续优化
- **已知限制**：
  - Runtime 模块 TargetDenyList 包含 Server，不支持 Dedicated Server
  - SoundWave 动画器的音频分析只能在编辑器中执行，运行时使用缓存数据
  - Oscillate/Bounce/Pulse 已废弃，新项目应使用 Curve 动画器
- **推荐程度**：✅ 强烈推荐用于 Motion Design / Virtual Production 场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PropertyAnimator)
- [PropertyAnimatorCore 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PropertyAnimatorCore) — 核心框架
- 官方文档：无（.uplugin DocsURL 为空）
