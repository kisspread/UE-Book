# Property Animator

> Re-usable behaviors to animate the value of one or more properties（可复用的行为，用于为一个或多个属性值创建动画）

| 属性 | 值 |
|---|---|
| 中文名 | 属性动画器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（动画器预设、曲线资产、项目设置） |
| 模块 | `PropertyAnimator` (Runtime), `PropertyAnimatorEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimator) | |

## 用途

`PropertyAnimator` 是 Unreal Motion Design (UMG) 工具套件的一部分，它提供了一套可复用、可配置的行为（称为“动画器”），用于程序化地驱动场景中对象的属性值。它解决的核心问题是：在虚拟制片和实时渲染场景中，需要为场景元素（如灯光、几何体、文字）添加动态、可重复的运动或变化效果，而无需手动打关键帧。

该插件设计用于与 `PropertyAnimatorCore` 协同工作，提供了具体的动画行为实现（如波动、脉冲、抖动、时钟、计数器等），并能够通过解析器（Resolver）将单个属性的动画效果应用到多个子属性上（例如，将一个 `float` 动画应用到一个 `FVector` 的每个分量上）。它极大地简化了为场景添加程序化动画的工作流程。

## 使用场景

- **虚拟制片 / Motion Graphics**：你需要为灯光、3D 文本或道具添加循环的发光、缩放、旋转或位移效果。
- **实时数据可视化**：你需要将一个数值（如音频响度、时间、用户输入）映射到一个可视属性（如位置、颜色、透明度）上。
- **音频可视化**：你需要让一个物体的运动或形态随着音频波形或音量而变化。
- **创建动态UI或文字效果**：你需要为文字组件创建计数器、时钟或逐字显示的动画效果。
- **快速原型制作**：你需要快速为场景中的物体添加一些“生命感”，而无需深入动画蓝图或 Sequencer。

## 蓝图用法

`PropertyAnimator` 中的动画器通常通过其基类 `UPropertyAnimatorCoreBase` 在编辑器中配置，但其许多属性和方法也暴露给了蓝图。以下是一些核心的可配置节点：

### 核心节点 (UPropertyAnimatorNumericBase 及其子类)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMagnitude` | 设置动画对属性影响的幅度或强度。 | `UPropertyAnimatorNumericBase` |
| `SetCycleMode` | 设置动画循环模式（单次、循环、往返）。 | `UPropertyAnimatorNumericBase` |
| `SetCycleDuration` | 设置一个完整动画循环的周期（以秒为单位）。 | `UPropertyAnimatorNumericBase` |
| `SetCycleGapDuration` | 设置两个动画循环之间的暂停时间。 | `UPropertyAnimatorNumericBase` |
| `SetRandomTimeOffset` | 是否为每个属性应用一个随机的时间偏移，以增加变化。 | `UPropertyAnimatorNumericBase` |
| `SetSeed` | 设置用于生成随机偏移的种子值。 | `UPropertyAnimatorNumericBase` |
| `SetFrequency` | (用于 `UPropertyAnimatorWiggle`) 设置抖动的频率，值越高变化越快。 | `UPropertyAnimatorWiggle` |
| `SetDisplayFormat` | (用于 `UPropertyAnimatorClock`) 设置时间显示的格式字符串（如 `%H:%M:%S`）。 | `UPropertyAnimatorClock` |
| `SetPresetFormatName` | (用于 `UPropertyAnimatorCounter`) 选择一个预设的数字格式（如带千分符的格式）。 | `UPropertyAnimatorCounter` |
| `SetSampledSoundWave` | (用于 `UPropertyAnimatorSoundWave`) 设置用于分析的音波资源。 | `UPropertyAnimatorSoundWave` |

### 使用示例（蓝图描述）

要在蓝图中配置一个动画器：
1.  获取目标 Actor 或组件的引用。
2.  使用 `Add Component` 节点添加一个 `PropertyAnimatorCoreComponent`。
3.  通过该组件的 `Add Animator` 节点，选择并实例化一个具体的动画器类（如 `PropertyAnimatorCurve`）。
4.  对返回的动画器对象实例，调用如 `SetMagnitude`、`SetCycleMode`、`SetCycleDuration` 等 setter 函数来配置其行为。
5.  使用组件的 `Link Property` 或 `Apply Preset` 函数，将动画器绑定到具体的属性上（例如，Actor 的 `Actor3D->K2_SetActorLocation`）。

## C++ 用法

`PropertyAnimator` 主要作为数据驱动的运行时系统，其 C++ 用法侧重于扩展和自定义动画行为。

### 头文件引入

```cpp
#include "PropertyAnimator.h"
// 如果需要使用特定的动画器子类
#include "Animators/PropertyAnimatorCurve.h"
#include "Animators/PropertyAnimatorWiggle.h"
// 如果需要使用属性上下文
#include "Properties/PropertyAnimatorFloatContext.h"
```

### 基本用法：创建自定义动画器

一个自定义动画器通常继承自 `UPropertyAnimatorNumericBase` 或 `UPropertyAnimatorTextBase`，并重写 `EvaluateProperty` 函数来实现具体的动画逻辑。

```cpp
// MyPropertyAnimator.h
#pragma once

#include "CoreMinimal.h"
#include "Animators/PropertyAnimatorNumericBase.h"
#include "MyPropertyAnimator.generated.h"

UCLASS(MinimalAPI, AutoExpandCategories = ("Animator"))
class UMyPropertyAnimator : public UPropertyAnimatorNumericBase
{
    GENERATED_BODY()

public:
    UMyPropertyAnimator();

protected:
    // 重写核心评估函数，定义动画行为
    virtual bool EvaluateProperty(
        const FPropertyAnimatorCoreData& InPropertyData,
        UPropertyAnimatorCoreContext* InContext,
        FInstancedPropertyBag& InParameters,
        FInstancedPropertyBag& OutEvaluationResult) const override;

    // 当动画器被注册到系统时调用，用于设置元数据
    virtual void OnAnimatorRegistered(FPropertyAnimatorCoreMetadata& InMetadata) override;

private:
    // 自定义属性（例如，一个额外的“扭曲”参数）
    UPROPERTY(EditInstanceOnly, Setter, Getter, Category = "Animator|Custom")
    float TwistAmount = 0.5f;

    // 对应的 setter/getter
    void SetTwistAmount(float InAmount);
    float GetTwistAmount() const { return TwistAmount; }
};
```

```cpp
// MyPropertyAnimator.cpp
#include "MyPropertyAnimator.h"

UMyPropertyAnimator::UMyPropertyAnimator()
{
    // 可以在此设置默认值
}

void UMyPropertyAnimator::SetTwistAmount(float InAmount)
{
    TwistAmount = FMath::Max(0.0f, InAmount);
}

void UMyPropertyAnimator::OnAnimatorRegistered(FPropertyAnimatorCoreMetadata& InMetadata)
{
    Super::OnAnimatorRegistered(InMetadata);
    // 设置动画器在编辑器中的友好名称
    InMetadata.Name = TEXT("MyCustomAnimator");
    InMetadata.Category = TEXT("Custom");
}

bool UMyPropertyAnimator::EvaluateProperty(
    const FPropertyAnimatorCoreData& InPropertyData,
    UPropertyAnimatorCoreContext* InContext,
    FInstancedPropertyBag& InParameters,
    FInstancedPropertyBag& OutEvaluationResult) const
{
    // 从参数中获取时间（通常由时间源提供）
    const double Time = InParameters.GetValueDouble(FPropertyAnimatorCoreParams::Time);

    // 获取当前链接的属性上下文（包含振幅等信息）
    UPropertyAnimatorFloatContext* FloatContext = Cast<UPropertyAnimatorFloatContext>(InContext);
    if (!FloatContext)
    {
        return false;
    }

    // 应用基础的周期、幅度等逻辑 (Magnitude, CycleMode, CycleDuration 等)
    // 此处省略基础计算，假设得到 `EvaluatedValue`
    const double BaseValue = /* ... 复杂的基础计算 ... */;

    // 应用自定义的“扭曲”逻辑
    const double TwistedValue = BaseValue + FMath::Sin(Time * 2.0 * PI) * TwistAmount;

    // 将结果限制在上下文定义的振幅范围内
    const double ClampedValue = FMath::Clamp(TwistedValue,
        FloatContext->GetAmplitudeMin(), FloatContext->GetAmplitudeMax());

    // 将最终评估结果存入输出参数袋
    OutEvaluationResult.SetValueDouble(FPropertyAnimatorCoreParams::EvaluatedValue, ClampedValue);

    return true;
}
```

### 进阶用法：应用预设

`PropertyAnimator` 包含多个预设（Preset），可以快速将动画应用到一组标准属性上。

```cpp
#include "PropertyAnimatorCoreComponent.h"
#include "Presets/PropertyAnimatorPresetLocation.h"

// 假设 `AnimatorComponent` 是一个指向 UPropertyAnimatorCoreComponent 的指针
if (AnimatorComponent)
{
    // 实例化一个位置动画器
    UPropertyAnimatorCurve* CurveAnimator = NewObject<UPropertyAnimatorCurve>(AnimatorComponent);
    // 应用“Location”预设，它会自动将动画器链接到目标 Actor 的位置 X, Y, Z 属性
    if (UPropertyAnimatorPresetLocation* LocationPreset = NewObject<UPropertyAnimatorPresetLocation>(AnimatorComponent))
    {
        LocationPreset->ApplyPreset(AnimatorComponent->GetOwner(), CurveAnimator);
    }
    // 添加动画器并启动
    AnimatorComponent->AddAnimator(CurveAnimator);
}
```

## Demo 示例

一个最小的自定义抖动（Wiggle）动画器实现。

```cpp
// SimpleWiggleAnimator.h
#pragma once

#include "CoreMinimal.h"
#include "Animators/PropertyAnimatorNumericBase.h"
#include "SimpleWiggleAnimator.generated.h"

UCLASS(MinimalAPI, AutoExpandCategories = ("Animator"))
class USimpleWiggleAnimator : public UPropertyAnimatorNumericBase
{
    GENERATED_BODY()

public:
    USimpleWiggleAnimator();

protected:
    virtual bool EvaluateProperty(
        const FPropertyAnimatorCoreData& InPropertyData,
        UPropertyAnimatorCoreContext* InContext,
        FInstancedPropertyBag& InParameters,
        FInstancedPropertyBag& OutEvaluationResult) const override;

    virtual void OnAnimatorRegistered(FPropertyAnimatorCoreMetadata& InMetadata) override;

    // 使用 Perlin 噪声生成抖动
    UPROPERTY(EditInstanceOnly, Setter, Getter, Category = "Animator", meta = (ClampMin = "0.01"))
    float NoiseScale = 1.0f;

    void SetNoiseScale(float InScale);
    float GetNoiseScale() const { return NoiseScale; }
};
```

```cpp
// SimpleWiggleAnimator.cpp
#include "SimpleWiggleAnimator.h"
#include "Math/UnrealMathUtility.h"

USimpleWiggleAnimator::USimpleWiggleAnimator()
{
}

void USimpleWiggleAnimator::SetNoiseScale(float InScale)
{
    NoiseScale = FMath::Max(0.01f, InScale);
}

void USimpleWiggleAnimator::OnAnimatorRegistered(FPropertyAnimatorCoreMetadata& InMetadata)
{
    Super::OnAnimatorRegistered(InMetadata);
    InMetadata.Name = TEXT("Simple Wiggle");
}

bool USimpleWiggleAnimator::EvaluateProperty(
    const FPropertyAnimatorCoreData& InPropertyData,
    UPropertyAnimatorCoreContext* InContext,
    FInstancedPropertyBag& InParameters,
    FInstancedPropertyBag& OutEvaluationResult) const
{
    const double Time = InParameters.GetValueDouble(FPropertyAnimatorCoreParams::Time);

    // 使用 Perlin 噪声函数生成 [-1, 1] 范围内的抖动值，并根据幅度和噪声缩放进行调整
    const double NoiseValue = FMath::PerlinNoise1D(Time * NoiseScale);
    const double WiggleValue = NoiseValue * GetMagnitude();

    OutEvaluationResult.SetValueDouble(FPropertyAnimatorCoreParams::EvaluatedValue, WiggleValue);
    return true;
}
```

## 模块依赖

从 `PropertyAnimator.Build.cs` 分析，使用此插件需要以下关键依赖：

| 模块 | 用途 |
|---|---|
| `PropertyAnimatorCore` | 核心框架模块，提供动画器基类、上下文、解析器等基础架构。 |
| `LoudnessNRT` | 用于音频响度分析，是 `PropertyAnimatorSoundWave` 动画器的依赖。 |
| `MovieScene` | 用于与 Sequencer 集成，提供自定义的缓动和波形通道。 |

*注意：该插件还隐式依赖于 `Core`, `CoreUObject`, `Engine` 等标准模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量隐式转换为浮点数产生的编译警告。 |
| 2026-05-12 | `7ebcbc6e` | Motion Design: fixed property animators to properly evaluate end of cycle. Previously end of cycle w | 修复了属性动画器在循环结束时评估不正确的问题。 |
| 2026-02-25 | `c0dd9731` | StringBuilder: Removing construction of TStringBuilderBase<T> | 内部代码优化，移除了对 TStringBuilderBase 的构造。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件从 `Base<Plugin>.ini` 重命名为 `Default<Plugin>.ini`，符合新的引擎规范。 |
| 2025-10-03 | `9c05cf60` | MotionDesign : PropertyAnimator | 插件首次从实验性目录迁移至正式的虚拟制作目录。 |

### 维护评价

- **创建时间**：2025年5月创建，是较新的插件。
- **近期更新**：最近一次提交在2026年5月，修复了编译警告和评估逻辑，表明**仍在活跃维护**。
- **活跃度**：作为 Motion Design 工具链的核心组件，预计会持续更新和优化。
- **已知限制**：源码中发现 `PropertyAnimatorPulse`、`PropertyAnimatorOscillate`、`PropertyAnimatorBounce` 等类被标记为 `Deprecated`，建议使用基于曲线 (`PropertyAnimatorCurve`) 的预设替代。这是正常的架构演进。
- **推荐使用**：✅ **推荐**。这是一个功能完整、设计现代且维护活跃的插件，非常适合在虚拟制片和 Motion Graphics 项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimator)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimator/Tests) (位于插件目录内，可能为自测)