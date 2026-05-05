# Property Animator Core

> Re-usable behaviors to control properties at runtime and in editor（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `PropertyAnimatorCore` (Runtime), `PropertyAnimatorCoreEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PropertyAnimatorCore) | |

## 用途

Property Animator Core 是一个用于在运行时和编辑器中驱动属性动画的框架系统。它解决的核心问题是：为虚拟制片（Virtual Production）场景提供一套可复用、可扩展的机制，以程序化方式控制 Actor 或 Component 上的任意属性（如位置、旋转、材质参数、灯光强度等）。

该插件并非一个具体的动画效果，而是一个底层框架。它定义了动画器（Animator）、属性处理器（Handler）、时间源（Time Source）、预设（Preset）等抽象基类和接口，允许开发者基于此框架创建自定义的属性动画行为。例如，可以创建一个“脉冲”动画器来周期性地改变灯光的强度，或者一个“随机抖动”动画器来扰动物体的位置。

## 使用场景

- **虚拟制片**：在 LED 虚拟影棚中，需要根据拍摄进度或导演指令，实时、程序化地调整场景中灯光、材质、后期处理等参数。
- **动态场景效果**：在游戏或实时应用中，需要基于游戏逻辑（如玩家接近、事件触发）或时间（如昼夜循环）来平滑地改变物体属性。
- **工具开发**：为编辑器开发自定义的属性动画工具，例如一个可以快速为选中物体添加“呼吸”效果的工具。
- **数据驱动动画**：通过预设（Preset）系统，将复杂的属性动画配置保存为资产，并在不同 Actor 或场景间快速复用。

## 蓝图用法

该插件主要通过 `UPropertyAnimatorCoreComponent` 和 `UPropertyAnimatorCoreBase` 的子类在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindOrAdd` | 查找或为指定 Actor 添加一个 PropertyAnimatorCoreComponent | `UPropertyAnimatorCoreComponent` |
| `Set Animators Enabled` | 启用或禁用该组件内所有动画器 | `UPropertyAnimatorCoreComponent` |
| `Set Animators Magnitude` | 设置该组件内所有动画器的整体强度 | `UPropertyAnimatorCoreComponent` |
| `Set Animator Enabled` | 启用或禁用单个动画器实例 | `UPropertyAnimatorCoreBase` |
| `Set Linked Properties` | 设置动画器要驱动的属性列表 | `UPropertyAnimatorCoreBase` |
| `Set Time Source Name` | 为动画器设置时间源（如 World, Sequencer, Manual） | `UPropertyAnimatorCoreBase` |

### 使用示例（蓝图描述）

1.  **为 Actor 添加动画能力**：
    - 在目标 Actor 的蓝图中，添加一个 `PropertyAnimatorCoreComponent` 组件。
    - 或者在运行时，使用 `UPropertyAnimatorCoreComponent::FindOrAdd(MyActor)` 节点动态添加。

2.  **配置一个具体的动画器**：
    - 在 `PropertyAnimatorCoreComponent` 的 `PropertyAnimators` 数组中，添加一个具体的动画器类实例（例如，一个自定义的 `UMyPulseAnimator`）。
    - 在该动画器实例的细节面板中，设置 `Linked Properties`，通过属性选择器指定要驱动的属性（例如，一个点光源的 `Intensity`）。
    - 设置 `Time Source Name` 为 `World` 以跟随游戏时间，或 `Manual` 以手动控制时间。
    - 勾选 `Animator Enabled` 以激活动画。

3.  **运行时控制**：
    - 通过 `Set Animators Enabled` 节点批量开关组件内所有动画。
    - 通过 `Set Animators Magnitude` 节点整体调整动画强度，实现淡入淡出效果。

## C++ 用法

### 头文件引入

```cpp
#include "PropertyAnimatorCoreComponent.h"
#include "Animators/PropertyAnimatorCoreBase.h"
// 其他需要的头文件，如具体的时间源、处理器等
```

### 基本用法

以下示例展示如何在 C++ 中为一个 Actor 添加动画组件并配置一个动画器。

```cpp
// 假设在某个 Actor 的 BeginPlay 或自定义函数中
void AMyActor::SetupPropertyAnimator()
{
    // 1. 查找或添加组件
    UPropertyAnimatorCoreComponent* AnimatorComp = UPropertyAnimatorCoreComponent::FindOrAdd(this);
    if (!AnimatorComp)
    {
        return;
    }

    // 2. 启用组件
    AnimatorComp->SetAnimatorsEnabled(true);

    // 3. 添加一个具体的动画器（例如，一个内置或自定义的动画器类）
    // 注意：这里假设你有一个名为 UMyCustomAnimator 的类，它继承自 UPropertyAnimatorCoreBase
    UPropertyAnimatorCoreBase* NewAnimator = AnimatorComp->AddAnimator<UMyCustomAnimator>();
    if (NewAnimator)
    {
        // 4. 配置动画器
        NewAnimator->SetAnimatorEnabled(true);
        NewAnimator->SetTimeSourceName(FName(TEXT("World"))); // 使用世界时间

        // 5. 链接要驱动的属性
        // 这是一个简化的示例，实际中需要构造 FPropertyAnimatorCoreData
        FPropertyAnimatorCoreData PropertyData(this, /* ... 属性信息 ... */);
        NewAnimator->LinkProperty(PropertyData);
    }
}
```
*来源：基于 `UPropertyAnimatorCoreComponent` 和 `UPropertyAnimatorCoreBase` 的公共接口推断。*

### 进阶用法

使用预设（Preset）系统来保存和加载动画配置。

```cpp
#include "Presets/PropertyAnimatorCoreAnimatorPreset.h"
#include "Subsystems/PropertyAnimatorCoreSubsystem.h"

void AMyActor::SaveAnimatorPreset()
{
    UPropertyAnimatorCoreComponent* AnimatorComp = FindComponentByClass<UPropertyAnimatorCoreComponent>();
    if (!AnimatorComp || AnimatorComp->GetAnimatorsCount() == 0)
    {
        return;
    }

    // 获取第一个动画器
    UPropertyAnimatorCoreBase* Animator = AnimatorComp->GetAnimators()[0];
    if (!Animator)
    {
        return;
    }

    // 获取子系统
    UPropertyAnimatorCoreSubsystem* Subsystem = UPropertyAnimatorCoreSubsystem::Get();
    if (!Subsystem)
    {
        return;
    }

    // 创建一个动画器预设
    UPropertyAnimatorCoreAnimatorPreset* Preset = NewObject<UPropertyAnimatorCoreAnimatorPreset>();
    Preset->CreatePreset(FName(TEXT("MySavedPreset")), {Animator});

    // 保存预设（具体实现取决于预设的存储机制，如保存到文件或资产）
    // Preset->SaveToAsset(...);
}

void AMyActor::LoadAnimatorPreset(UPropertyAnimatorCoreAnimatorPreset* InPreset)
{
    UPropertyAnimatorCoreComponent* AnimatorComp = UPropertyAnimatorCoreComponent::FindOrAdd(this);
    if (!AnimatorComp || !InPreset)
    {
        return;
    }

    // 检查预设是否支持当前 Actor
    if (InPreset->IsPresetSupported(this, nullptr))
    {
        // 应用预设，这可能会创建新的动画器或修改现有动画器
        InPreset->ApplyPreset(nullptr); // 传入 nullptr，让预设自行处理组件
    }
}
```
*来源：基于 `UPropertyAnimatorCoreAnimatorPreset` 和 `UPropertyAnimatorCoreSubsystem` 的接口。*

## Demo 示例

一个最小的自定义动画器示例，它使链接的属性值随时间正弦波动。

**MySineAnimator.h**
```cpp
#pragma once

#include "Animators/PropertyAnimatorCoreBase.h"
#include "MySineAnimator.generated.h"

UCLASS(BlueprintType, EditInlineNew, AutoExpandCategories=("Animator"))
class MYPROJECT_API UMySineAnimator : public UPropertyAnimatorCoreBase
{
    GENERATED_BODY()

public:
    UMySineAnimator();

    // 重写核心评估函数
    virtual bool EvaluateProperty(const FPropertyAnimatorCoreData& InProperty, const FInstancedPropertyBag& InAnimatorResult, FInstancedPropertyBag& OutEvaluatedValues) override;

protected:
    // 动画参数
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Animator")
    float Amplitude = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Animator")
    float Frequency = 1.0f;
};
```

**MySineAnimator.cpp**
```cpp
#include "MySineAnimator.h"
#include "Properties/PropertyAnimatorCoreContext.h"

UMySineAnimator::UMySineAnimator()
{
    // 设置动画器的元数据
    Metadata.Name = FName(TEXT("Sine"));
    Metadata.DisplayName = NSLOCTEXT("Animator", "SineAnimator", "Sine Wave");
    Metadata.Description = NSLOCTEXT("Animator", "SineAnimatorDesc", "Animates a property with a sine wave.");
    Metadata.Category = FName(TEXT("Math"));
}

bool UMySineAnimator::EvaluateProperty(const FPropertyAnimatorCoreData& InProperty, const FInstancedPropertyBag& InAnimatorResult, FInstancedPropertyBag& OutEvaluatedValues)
{
    // 从动画器结果中获取时间（由时间源提供）
    double TimeElapsed = 0.0;
    if (!InAnimatorResult.GetValueDouble(FName(TEXT("TimeElapsed")), TimeElapsed).IsValid())
    {
        return false;
    }

    // 计算正弦值
    float SineValue = FMath::Sin(TimeElapsed * Frequency * 2.0f * PI) * Amplitude;

    // 将计算出的值设置到输出属性包中
    // 注意：这里假设驱动的是单个浮点属性。实际中需要根据属性类型进行转换。
    OutEvaluatedValues.SetValueFloat(FName(TEXT("Value")), SineValue);

    return true;
}
```

## 模块依赖

### PropertyAnimatorCore (Runtime)
| 模块 | 用途 |
|---|---|
| `StructUtils` | 使用 `FInstancedPropertyBag` 和 `FPropertyBag` 进行通用属性值存储和操作。 |
| `PropertyEditor` | 用于属性细节面板自定义和属性选择。 |

### PropertyAnimatorCoreEditor (Editor)
| 模块 | 用途 |
|---|---|
| `PropertyAnimatorCore` | 运行时核心模块。 |
| `UnrealEd` | 编辑器基础功能。 |
| `PropertyEditor` | 编辑器属性自定义。 |

## 维护状态

### 近期更新

```
- 4dfd2b49a86d MotionDesign : - Various minimal fixes for ActorModifier, PropertyAnimator and Text3D
- 26e7710b27d0 MotionDesign : PropertyAnimator - Fixed SVGImporter actor moving pivot when entering PIE when animator is used
- 12579b17f580 MotionDesign : PropertyAnimator - Deprecating legacy bounce, oscillate, pulse animator (can't be added from menu) - Fixed allowing preset animator to be added from the advanced context menu of details panel
```

### 维护评价

- **活跃维护**：插件创建于2024年初，属于较新的模块。最近的提交（2025年）显示仍在积极修复问题和进行功能调整。
- **功能演进**：从提交记录看，插件正在整合进“MotionDesign”工作流，并对旧有动画器（如 bounce, oscillate, pulse）进行废弃处理，表明其架构和功能在持续优化。
- **推荐使用**：作为 Epic 官方维护的虚拟制片核心组件，且处于活跃开发中，**推荐在需要程序化属性动画的虚拟制片或高级游戏项目中使用**。但需注意其API可能随版本迭代而变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PropertyAnimatorCore)
- [官方文档]() (暂无)
- [测试用例]() (暂未在插件目录内发现标准测试文件)