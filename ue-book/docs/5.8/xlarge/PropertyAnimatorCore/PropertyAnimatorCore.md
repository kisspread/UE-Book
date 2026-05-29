# Property Animator Core

> Re-usable behaviors to control properties at runtime and in editor

| 属性 | 值 |
|---|---|
| 中文名 | 属性动画核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PropertyAnimatorCore` (Runtime), `PropertyAnimatorCoreEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimatorCore) | |

## 用途

PropertyAnimatorCore 是一个**通用属性动画框架**，属于 Unreal Motion Design（虚拟制片）工具链的核心模块。它解决的核心问题是：**在运行时和编辑器中，以数据驱动的方式动态控制 Actor 上的任意属性**。

与传统 Timeline/Sequencer 动画不同，这个系统的设计思路是：

1. **将"哪个 Animator 驱动哪个属性"的绑定关系解耦**——Animator 不硬编码目标属性，而是在运行时链接到具体属性
2. **通过抽象的时间源（TimeSource）系统**统一时间驱动方式，支持世界时间、系统时钟、手动控制、Sequencer 轨道等多种时钟源
3. **通过预设（Preset）系统**实现动画配置的保存/加载/复用
4. **通过处理器（Handler）和转换器（Converter）系统**自动处理不同数据类型的读写与类型转换

它本质上是一个**属性驱动引擎**，让你可以创建自定义的 Animator 子类来实现各种效果（闪烁、脉动、摆动等），而无需关心目标属性是什么类型、如何读写。

## 使用场景

- 你在做虚拟制片/Motion Design → 用 PropertyAnimatorCore 让灯光/材质属性随时间变化
- 你需要批量控制大量 Actor 的属性 → 通过 AnimatorComponent 管理多个 Animator
- 你需要可复用的动画效果预设 → 通过 Preset 系统保存和分发动画配置
- 你需要 Sequencer 时间轴驱动属性 → 通过 Sequencer TimeSource 集成
- 你需要类型无关的属性控制 → 通过 Handler/Converter 抽象层自动处理 float→bool、float→int 等转换

## 蓝图用法

### 核心组件

`UPropertyAnimatorCoreComponent` 是挂载到 Actor 上的容器组件，管理一组 Animator 实例。

| 属性/函数 | 说明 | 所在类 |
|---|---|---|
| `SetAnimatorsEnabled` / `GetAnimatorsEnabled` | 全局开关，控制组件内所有 Animator 的启用状态 | `UPropertyAnimatorCoreComponent` |
| `SetAnimatorsMagnitude` / `GetAnimatorsMagnitude` | 全局强度（0-1），影响所有 Animator 的效果幅度 | `UPropertyAnimatorCoreComponent` |
| `SetAnimatorsTimeSourceName` / `GetAnimatorsTimeSourceName` | 全局时间源名称，可被单个 Animator 覆盖 | `UPropertyAnimatorCoreComponent` |
| `PropertyAnimators` (数组属性) | Animator 实例列表，蓝图可读写 | `UPropertyAnimatorCoreComponent` |
| `ForEachAnimator` | 遍历所有 Animator 并执行回调 | `UPropertyAnimatorCoreComponent` |

### Animator 控制

| 属性/函数 | 说明 | 所在类 |
|---|---|---|
| `SetAnimatorEnabled` / `GetAnimatorEnabled` | 单个 Animator 的开关 | `UPropertyAnimatorCoreBase` |
| `SetAnimatorDisplayName` | 设置 Animator 显示名称 | `UPropertyAnimatorCoreBase` |
| `SetOverrideTimeSource` / `GetOverrideTimeSource` | 是否覆盖全局时间源 | `UPropertyAnimatorCoreBase` |
| `SetTimeSourceName` | 指定使用的时间源 | `UPropertyAnimatorCoreBase` |
| `LinkProperty` | 将属性链接到此 Animator | `UPropertyAnimatorCoreBase` |
| `UnlinkProperty` | 取消属性链接 | `UPropertyAnimatorCoreBase` |
| `GetLinkedProperties` | 获取所有已链接的属性 | `UPropertyAnimatorCoreBase` |

### 属性上下文控制

| 属性/函数 | 说明 | 所在类 |
|---|---|---|
| `SetAnimated` / `IsAnimated` | 控制单个属性的动画开关 | `UPropertyAnimatorCoreContext` |
| `SetMagnitude` / `GetMagnitude` | 单个属性的效果强度（0-1） | `UPropertyAnimatorCoreContext` |
| `SetTimeOffset` / `GetTimeOffset` | 属性的时间偏移（秒） | `UPropertyAnimatorCoreContext` |
| `SetMode` / `GetMode` | Absolute（直接设值）或 Additive（叠加） | `UPropertyAnimatorCoreContext` |

### 使用示例（蓝图描述）

**基本用法**：在 Actor 上添加 PropertyAnimatorCoreComponent → 在 PropertyAnimators 数组中添加自定义 Animator 子类 → 通过编辑器面板链接目标属性 → Animator 自动在 Tick 中驱动属性。

**全局控制**：获取 Actor 上的 PropertyAnimatorCoreComponent → 调用 `SetAnimatorsEnabled(false)` 暂停所有动画效果。

**设置全局时间源**：在组件上设置 `AnimatorsTimeSourceName` 为 "System"（系统时钟）、"World"（世界时间）或 "Manual"（手动控制）。

## C++ 用法

### 头文件引入

```cpp
#include "Components/PropertyAnimatorCoreComponent.h"
#include "Animators/PropertyAnimatorCoreBase.h"
#include "Properties/PropertyAnimatorCoreData.h"
#include "Properties/PropertyAnimatorCoreContext.h"
#include "Subsystems/PropertyAnimatorCoreSubsystem.h"
#include "TimeSources/PropertyAnimatorCoreTimeSourceBase.h"
```

### 基本用法：获取子系统

```cpp
// 获取全局子系统，用于注册/查询 Animator 类、时间源、预设等
UPropertyAnimatorCoreSubsystem* Subsystem = UPropertyAnimatorCoreSubsystem::Get();

// 检查某个属性是否被任何 Animator 支持
FPropertyAnimatorCoreData PropertyData(Actor, PropertyChain);
bool bSupported = Subsystem->IsPropertySupported(PropertyData);

// 获取某个 Actor 上已存在的 Animator 实例
TSet<UPropertyAnimatorCoreBase*> ExistingAnimators = Subsystem->GetExistingAnimators(Actor);

// 通过子系统创建 Animator（推荐方式）
UPropertyAnimatorCoreBase* Animator = Subsystem->CreateAnimator(
    Actor,
    MyAnimatorClass,
    /*Preset=*/ nullptr,
    /*bTransact=*/ false  // 支持撤销
);
```

### 基本用法：操作组件

```cpp
// 查找或添加组件
UPropertyAnimatorCoreComponent* Component = UPropertyAnimatorCoreComponent::FindOrAdd(Actor);

// 全局开关
Component->SetAnimatorsEnabled(true);
Component->SetAnimatorsMagnitude(0.5f);
Component->SetAnimatorsTimeSourceName(FName("System"));

// 遍历所有 Animator
Component->ForEachAnimator([](UPropertyAnimatorCoreBase* Animator) -> bool
{
    // 返回 false 中断遍历
    UE_LOG(LogTemp, Log, TEXT("Animator: %s"), *Animator->GetAnimatorDisplayName().ToString());
    return true; // 继续
});
```

### 基本用法：链接属性

```cpp
// 构造属性数据 — 从 Actor 和属性链定位属性
FPropertyAnimatorCoreData PropertyData(Actor, MemberProperty, InnerProperty);

// 链接到 Animator（自动创建 Context）
UPropertyAnimatorCoreContext* Context = Animator->LinkProperty(PropertyData);

if (Context)
{
    // 设置属性动画参数
    Context->SetAnimated(true);
    Context->SetMagnitude(0.8f);
    Context->SetTimeOffset(1.0);  // 秒
    Context->SetMode(EPropertyAnimatorCoreMode::Additive);
}

// 检查属性是否已链接
bool bLinked = Animator->IsPropertyLinked(PropertyData);

// 取消链接
Animator->UnlinkProperty(PropertyData);
```

### 进阶用法：创建自定义 Animator 子类

```cpp
// MyBlinkAnimator.h
#pragma once
#include "Animators/PropertyAnimatorCoreBase.h"
#include "MyBlinkAnimator.generated.h"

UCLASS(MinimalAPI, BlueprintType, EditInlineNew, AutoExpandCategories=("Animator"))
class UMyBlinkAnimator : public UPropertyAnimatorCoreBase
{
    GENERATED_BODY()

public:
    UMyBlinkAnimator();

    // 声明 Animator 元数据
    virtual void OnAnimatorRegistered(FPropertyAnimatorCoreMetadata& InMetadata) override
    {
        InMetadata.Name = TEXT("Blink");
        InMetadata.DisplayName = NSLOCTEXT("MyAnim", "Blink", "Blink Effect");
        InMetadata.Description = NSLOCTEXT("MyAnim", "BlinkDesc", "Blinks linked properties on and off");
        InMetadata.Category = TEXT("Custom");
    }

    // 声明支持的属性类型
    virtual EPropertyAnimatorPropertySupport IsPropertySupported(
        const FPropertyAnimatorCoreData& InPropertyData) const override
    {
        // 支持 float、bool、int32 类型属性
        if (InPropertyData.IsA<FBoolProperty>() ||
            InPropertyData.IsA<FFloatProperty>() ||
            InPropertyData.IsA<FDoubleProperty>() ||
            InPropertyData.IsA<FIntProperty>())
        {
            return EPropertyAnimatorPropertySupport::Complete;
        }
        return EPropertyAnimatorPropertySupport::None;
    }

protected:
    // 核心评估函数 — 每 Tick 调用
    virtual void EvaluateProperties(FInstancedPropertyBag& InParameters) override
    {
        // 从参数包获取时间源提供的数据
        double TimeElapsed = 0.0;
        InParameters.GetValueDouble(TimeElapsedParameterName, TimeElapsed);

        float Magnitude = 1.f;
        InParameters.GetValueFloat(MagnitudeParameterName, Magnitude);

        float Frequency = 1.f;
        InParameters.GetValueFloat(FrequencyParameterName, Frequency);

        float Alpha = 1.f;
        InParameters.GetValueFloat(AlphaParameterName, Alpha);

        // 遍历并评估每个链接的属性
        EvaluateEachLinkedProperty(
            [&](UPropertyAnimatorCoreContext* InContext,
                const FPropertyAnimatorCoreData& InProperty,
                FInstancedPropertyBag& OutEvaluation,
                int32 InIndex, int32 InMax) -> bool
            {
                // 计算闪烁值：基于正弦波
                float BlinkValue = FMath::Sin(TimeElapsed * Frequency * 2.0 * PI) > 0.0f ? 1.0f : 0.0f;
                BlinkValue *= Magnitude * Alpha;

                // 根据属性类型设置评估结果
                if (InProperty.IsA<FBoolProperty>())
                {
                    OutEvaluation.SetValueBool(NAME_None, BlinkValue > 0.5f);
                }
                else
                {
                    OutEvaluation.SetValueFloat(NAME_None, BlinkValue);
                }

                return true; // 返回 true 表示应用此评估结果
            }
        );
    }

private:
    UPROPERTY(EditInstanceOnly, Category="Animator", meta=(ClampMin="0.1", ClampMax="20.0"))
    float Frequency = 2.0f;
};
```

```cpp
// MyBlinkAnimator.cpp
#include "MyBlinkAnimator.h"

UMyBlinkAnimator::UMyBlinkAnimator()
{
    // 基类构造函数已自动注册元数据
}
```

### 进阶用法：使用子系统批量操作

```cpp
UPropertyAnimatorCoreSubsystem* Subsystem = UPropertyAnimatorCoreSubsystem::Get();

// 批量创建 Animator
TSet<AActor*> Actors = { Actor1, Actor2, Actor3 };
TSet<UPropertyAnimatorCoreBase*> Animators = Subsystem->CreateAnimators(
    Actors, UMyBlinkAnimator::StaticClass(), /*Preset=*/ nullptr, /*bTransact=*/ true);

// 批量链接属性
FPropertyAnimatorCoreData PropData(Actor1, TargetProperty);
for (UPropertyAnimatorCoreBase* Anim : Animators)
{
    Subsystem->LinkAnimatorProperty(Anim, PropData, /*bTransact=*/ true);
}

// 批量启用/禁用
Subsystem->SetAnimatorsEnabled(Animators, true, /*bTransact=*/ true);

// 应用预设
TSet<UPropertyAnimatorCorePresetBase*> Presets = Subsystem->GetAvailablePresets(
    UPropertyAnimatorCoreAnimatorPreset::StaticClass());
for (UPropertyAnimatorCorePresetBase* Preset : Presets)
{
    Subsystem->ApplyAnimatorPreset(Animators[0], Preset, /*bTransact=*/ true);
}

// 清理
Subsystem->RemoveAnimators(Animators, /*bTransact=*/ true);
```

## Demo 示例

### 最小自定义 Animator

以下示例创建一个简单的"呼吸"Animator，使链接的 float 属性按正弦波平滑变化。

```cpp
// BreatheAnimator.h
#pragma once

#include "Animators/PropertyAnimatorCoreBase.h"
#include "BreatheAnimator.generated.h"

UCLASS(MinimalAPI, BlueprintType, EditInlineNew, AutoExpandCategories=("Animator"))
class UBreatheAnimator : public UPropertyAnimatorCoreBase
{
    GENERATED_BODY()

public:
    UBreatheAnimator();

    virtual EPropertyAnimatorPropertySupport IsPropertySupported(
        const FPropertyAnimatorCoreData& InPropertyData) const override;

protected:
    virtual void EvaluateProperties(FInstancedPropertyBag& InParameters) override;

    /** 呼吸速度（周期/秒） */
    UPROPERTY(EditInstanceOnly, Category="Breathe", meta=(ClampMin="0.01", ClampMax="10.0"))
    float BreathSpeed = 1.0f;

    /** 最小值 */
    UPROPERTY(EditInstanceOnly, Category="Breathe")
    float MinValue = 0.0f;

    /** 最大值 */
    UPROPERTY(EditInstanceOnly, Category="Breathe")
    float MaxValue = 1.0f;
};
```

```cpp
// BreatheAnimator.cpp
#include "BreatheAnimator.h"
#include "Properties/PropertyAnimatorCoreContext.h"
#include "Properties/PropertyAnimatorCoreData.h"

UBreatheAnimator::UBreatheAnimator()
{
}

EPropertyAnimatorPropertySupport UBreatheAnimator::IsPropertySupported(
    const FPropertyAnimatorCoreData& InPropertyData) const
{
    if (InPropertyData.IsA<FFloatProperty>() || InPropertyData.IsA<FDoubleProperty>())
    {
        return EPropertyAnimatorPropertySupport::Complete;
    }
    return EPropertyAnimatorPropertySupport::None;
}

void UBreatheAnimator::EvaluateProperties(FInstancedPropertyBag& InParameters)
{
    double TimeElapsed = 0.0;
    InParameters.GetValueDouble(TimeElapsedParameterName, TimeElapsed);

    float Magnitude = 1.f;
    InParameters.GetValueFloat(MagnitudeParameterName, Magnitude);

    EvaluateEachLinkedProperty(
        [this, TimeElapsed, Magnitude](
            UPropertyAnimatorCoreContext* /*InContext*/,
            const FPropertyAnimatorCoreData& /*InProperty*/,
            FInstancedPropertyBag& OutEval,
            int32 /*InIndex*/, int32 /*InMax*/) -> bool
        {
            // 正弦波映射到 [MinValue, MaxValue]
            const float Sine = (FMath::Sin(TimeElapsed * BreathSpeed * 2.0 * PI) + 1.0f) * 0.5f;
            const float Value = FMath::Lerp(MinValue, MaxValue, Sine) * Magnitude;

            OutEval.SetValueDouble(NAME_None, static_cast<double>(Value));
            return true;
        }
    );
}
```

## 模块依赖

从 Build.cs 分析，此插件依赖 OperatorStack 插件（已在 .uplugin 中声明）。

| 模块 | 用途 |
|---|---|
| `OperatorStack` | 操作栈框架，被列为必需插件依赖 |
| `PropertyBag` | 属性包系统（FInstancedPropertyBag），用于类型无关的属性值存储 |
| `MovieScene` / `MovieSceneTracks` | Sequencer 集成，用于时间轴驱动 Animator |

无特殊依赖（仅标准 Core/Engine/Slate 等 + PropertyBag）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中 scoped enum 导致的输出乱码 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏从 UE_LOG 到 UE_LOGF |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 弃用旧式 GetObjects*/ForEachObjectWithOuter 接口 |
| 2025-12-19 | `a01aeeaa` | check for UObjectInitialized && !IsEngineExitRequested() before running clean-up code that involves | 清理代码增加初始化和退出状态检查 |
| 2025-11-18 | `36825f29` | Motion Design: corrected log verbosity from Log to Verbose for logs that were constantly outputting | 修正频繁输出日志的级别为 Verbose |

### 维护评价

- **创建时间**：2025 年 5 月，是 Motion Design 工具链从 Experimental 迁移到 VirtualProduction 时创建的
- **维护状态**：**活跃维护中**。最近 6 个月内有多次功能性修复和 API 更新，且由 Epic Games 官方团队维护
- **最近更新**：主要集中在引擎级 API 迁移（UE_LOGF、ScopedEnum 修复等），说明该插件跟随引擎主分支持续更新
- **稳定性**：代码结构成熟，有完整的序列化/撤销/复制支持，但作为较新的框架，API 可能仍有变化
- **推荐**：✅ 如果你在做 Motion Design 或虚拟制片相关工作，这是官方推荐的属性动画框架。注意它默认未启用（`Installed: false`），需要在插件设置中手动启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimatorCore)
- 官方文档：无（.uplugin 中 DocsURL 为空）