# Property Animator

> Re-usable behaviors to animate the value of one or more properties

| 属性 | 值 |
|---|---|
| 中文名 | 属性动画器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `PropertyAnimator` (Runtime), `PropertyAnimatorEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimator) | |

## 用途

Property Animator 是一个虚拟制片工具集，用于为各种属性提供可重用的动画行为。它允许用户通过定义参数化的行为（如正弦波、三角波等）来驱动属性值的变化，而不是直接关键帧动画。该插件与 Sequencer 深度集成，提供自定义的曲线通道接口，使得动画师可以在 Sequencer 时间线上直观地编辑和预览这些参数化动画。

该插件解决了在虚拟制片流程中创建和复用复杂属性动画的需求。传统关键帧动画在面对周期性、参数化动画时效率较低，而 Property Animator 通过行为化的方法，让用户可以快速创建和修改复杂的动画效果。

## 使用场景

- 你在制作虚拟制片项目，需要为灯光、摄像机或任何物体的属性创建周期性动画（如呼吸灯、旋转）。
- 你需要在 Sequencer 时间线上直观地编辑动画曲线参数（如振幅、频率、偏移）。
- 你希望为团队创建一套可重用的动画行为库，提高制作效率。

## 蓝图用法

该插件主要提供编辑器集成，没有直接暴露用于运行时蓝图交互的公开函数。动画行为通过编辑器界面进行配置和应用。

## C++ 用法

该插件的核心功能通过 C++ 扩展 Sequencer 来实现，不直接面向普通用户。主要提供以下扩展点：

### 头文件引入

```cpp
#include "PropertyAnimatorEditorModule.h"
```

### 基本用法

1. **注册自定义曲线通道接口**：为自定义的 `FMovieSceneChannel` 类型注册 Sequencer 接口，以在时间线上提供自定义的编辑和显示。

```cpp
// 在模块启动时，注册你的自定义曲线通道接口
void FPropertyAnimatorEditorModule::StartupModule()
{
    if (ISequencerModule* SequencerModule = FModuleManager::GetModulePtr<ISequencerModule>("Sequencer"))
    {
        // 注册一个自定义的曲线通道类型，MyCustomChannel
        RegisterCurveChannelInterface<FMyCustomCurveChannel>(*SequencerModule);
    }
}
```

2. **扩展曲线通道菜单**：通过继承 `FPropertyAnimatorEditorCurveSectionMenuExtension` 来为自定义通道添加 Sequencer 上下文菜单。

```cpp
// 创建一个针对特定通道类型的菜单扩展类
template<typename InChannelType>
class FMyCustomCurveSectionMenuExtension : public TPropertyAnimatorEditorCurveSectionMenuExtension<InChannelType>
{
public:
    // 构造函数
    FMyCustomCurveSectionMenuExtension(const TConstArrayView<FMovieSceneChannelHandle>& InChannelHandles, const TConstArrayView<TWeakObjectPtr<UMovieSceneSection>>& InWeakSections)
        : TPropertyAnimatorEditorCurveSectionMenuExtension<InChannelType>(InChannelHandles, InWeakSections)
    {
    }

    // 重写此函数以提供通道参数的结构体和数据指针，用于在属性面板中编辑
    virtual bool GetParameterStructData(FMovieSceneChannelHandle InChannelHandle, UStruct*& OutStruct, uint8*& OutData) const override
    {
        if (InChannelType* Channel = InChannelHandle.Cast<InChannelType>().Get())
        {
            OutStruct = FMyCustomChannelParameters::StaticStruct();
            OutData = reinterpret_cast<uint8*>(&Channel->Parameters);
            return true;
        }
        return false;
    }
};
```

### 进阶用法

实现自定义的曲线通道接口和可视化：

```cpp
// 继承模板基类，实现自定义的曲线通道 Sequencer 接口
template<typename InChannelType>
class FMyCustomCurveChannelInterface : public TPropertyAnimatorEditorCurveChannelInterface<InChannelType, FMyCustomCurveSectionMenuExtension<InChannelType>>
{
public:
    using Super = TPropertyAnimatorEditorCurveChannelInterface<InChannelType, FMyCustomCurveSectionMenuExtension<InChannelType>>;
    
    // 可以重写 DrawExtra_Raw 来实现自定义的曲线预览绘制
    virtual int32 DrawExtra_Raw(FMovieSceneChannel* InChannel, const UMovieSceneSection* InOwner, const FSequencerChannelPaintArgs& InPaintArgs, int32 InLayerId) const override
    {
        // ... 自定义绘制逻辑，例如绘制额外的辅助线或波形
        return Super::DrawExtra_Raw(InChannel, InOwner, InPaintArgs, InLayerId);
    }

    // 重写 CreateKeyEditor_Raw 来提供自定义的关键帧编辑器控件
    virtual TSharedRef<SWidget> CreateKeyEditor_Raw(const FMovieSceneChannelHandle& InChannel, const UE::Sequencer::FCreateKeyEditorParams& Params) const override
    {
        // ... 创建并返回自定义的关键帧编辑器控件
        return Super::CreateKeyEditor_Raw(InChannel, Params);
    }
};
```

## Demo 示例

```cpp
// MyPropertyAnimatorChannel.h
#pragma once
#include "Channels/MovieSceneDoubleChannel.h"
#include "MovieSceneChannelData.h"

USTRUCT()
struct FMyChannelParameters
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Animation")
    double Amplitude = 1.0;

    UPROPERTY(EditAnywhere, Category = "Animation")
    double Frequency = 1.0;

    UPROPERTY(EditAnywhere, Category = "Animation")
    double Offset = 0.0;
};

USTRUCT()
struct FMyCustomCurveChannel : public FMovieSceneDoubleChannel
{
    GENERATED_BODY()

    UPROPERTY()
    FMyChannelParameters Parameters;

    // 自定义求值函数
    double Evaluate(double BaseSeconds, double Seconds) const
    {
        // 实现一个简单的正弦波求值
        return Parameters.Amplitude * FMath::Sin((Seconds - BaseSeconds) * Parameters.Frequency * 2.0 * PI + Parameters.Offset);
    }
};

// MyPropertyAnimatorModule.h
#pragma once
#include "Modules/ModuleManager.h"
#include "PropertyAnimatorEditorModule.h"

class FMyPropertyAnimatorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MyPropertyAnimatorModule.cpp
#include "MyPropertyAnimatorModule.h"
#include "MyPropertyAnimatorChannel.h"
#include "SequencerChannelInterface.h"

#define LOCTEXT_NAMESPACE "FMyPropertyAnimatorModule"

void FMyPropertyAnimatorModule::StartupModule()
{
    if (ISequencerModule* SequencerModule = FModuleManager::GetModulePtr<ISequencerModule>("Sequencer"))
    {
        // 获取属性动画器模块并注册自定义通道接口
        FPropertyAnimatorEditorModule& PropertyAnimatorModule = FModuleManager::LoadModuleChecked<FPropertyAnimatorEditorModule>("PropertyAnimatorEditor");
        PropertyAnimatorModule.RegisterCurveChannelInterface<FMyCustomCurveChannel>(*SequencerModule);
    }
}

void FMyPropertyAnimatorModule::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyPropertyAnimatorModule, MyPropertyAnimator)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心框架，提供时间线、通道等基础功能 |
| `SequencerCore` | Sequencer 核心 UI 和交互 |
| `PropertyEditor` | 自定义属性编辑器细节面板 |
| `SlateCore` | UI 控件基础 |
| `UnrealEd` | 编辑器扩展 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数产生的警告 |
| 2026-05-12 | `7ebcbc6e` | Motion Design: fixed property animators to properly evaluate end of cycle. Previously end of cycle w... | 修复属性动画器在循环结束时评估不正确的问题 |
| 2026-02-25 | `c0dd9731` | StringBuilder: Removing construction of TStringBuilderBase<T> | 移除 TStringBuilderBase<T> 的构造函数 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从 Base<Plugin>.ini 重命名为 Default<Plugin>.ini |
| 2025-10-03 | `9c05cf60` | MotionDesign : PropertyAnimator | 属性动画器相关更新 |

### 维护评价

**活跃维护**。该插件自创建以来（约1年）保持了稳定的更新频率，最近一次更新在2026年5月，主要针对Bug修复和功能完善。从提交记录看，它作为 Motion Design 工具集的一部分被积极维护，最近修复了浮点精度和动画循环评估的问题。

该插件是虚拟制片流程中的重要工具，与Sequencer深度集成，适合需要创建参数化动画的项目。由于是实验性功能（`Installed: false`），建议在正式项目中谨慎使用并关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimator)
- [官方文档]()（暂无）