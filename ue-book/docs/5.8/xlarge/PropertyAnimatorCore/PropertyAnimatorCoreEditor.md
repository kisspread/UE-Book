# Property Animator Core

> Re-usable behaviors to control properties at runtime and in editor

| 属性 | 值 |
|---|---|
| 中文名 | 属性动画核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产和自定义） |
| 模块 | `PropertyAnimatorCore` (Runtime), `PropertyAnimatorCoreEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimatorCore) | |

## 用途

PropertyAnimatorCore 是一个通用的属性动画框架。它解决的核心问题是：在编辑器和运行时，为 UObject（特别是 Actor 和组件）的任意属性提供可重用的动画控制行为。它超越了传统的时间线动画，提供了一个模块化系统，允许开发者通过各种“动画器”（Animator）驱动对象属性（如位置、旋转、材质参数、光照强度等）产生动态变化。该框架的设计使得创建、管理、预览和应用这些属性动画变得简单和统一。

## 使用场景

- 你在制作虚拟制片（Virtual Production）场景，需要为灯光、摄像机或道具的属性（如颜色、强度、位置）快速创建复杂的周期性或随机动画效果。
- 你希望为游戏中的环境物体（如风扇、闪烁的灯、水面波纹）添加基于规则的动态属性变化，而无需手动编写 Tick 逻辑或使用传统的时间线。
- 你需要一个统一的编辑器界面来查看、链接、管理运行在多个 Actor 上的大量属性动画，并希望能将动画配置保存为预设（Preset）以便重用。

## 蓝图用法

### 核心节点

根据源码分析，此插件的核心功能主要通过 C++ 和编辑器子系统暴露。蓝图可直接调用的函数通常位于运行时组件 `UPropertyAnimatorCoreComponent` 上。由于未提供运行时模块的完整头文件，以下为基于典型用法推断的核心蓝图节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Property Animator` | 向组件添加一个新的属性动画器实例。 | `UPropertyAnimatorCoreComponent` |
| `Remove Property Animator` | 从组件中移除指定的属性动画器实例。 | `UPropertyAnimatorCoreComponent` |
| `Get Property Animator` | 根据类型或名称获取组件上的一个属性动画器实例。 | `UPropertyAnimatorCoreComponent` |
| `Link Property` | 将一个对象的属性链接到指定的动画器，使其受该动画器控制。 | `UPropertyAnimatorCoreBase` (或其子类) |
| `Set Animator Enabled` | 启用或禁用一个动画器实例。 | `UPropertyAnimatorCoreBase` |

*注：具体的函数名需以实际运行时模块 `PropertyAnimatorCore` 中的 `UFUNCTION(BlueprintCallable)` 标记为准。*

### 使用示例（蓝图描述）

1.  **添加组件**：在目标 Actor 上添加一个 `PropertyAnimatorCoreComponent`。
2.  **创建动画器**：调用组件的 `Add Property Animator` 节点，并选择一个动画器类型（如 `SineWave`，`Noise` 等）。
3.  **链接属性**：使用返回的动画器对象，调用 `Link Property`。通过属性路径（例如 `StaticMeshComponent.RelativeRotation.Yaw`）指定要控制的 Actor 属性。
4.  **配置动画**：设置动画器的各种参数（如振幅、频率、种子等）。
5.  **启用**：确保组件和动画器均已启用，运行游戏或预览编辑器效果。

## C++ 用法

### 头文件引入

```cpp
#include "PropertyAnimatorCoreComponent.h" // 核心运行时组件
#include "PropertyAnimatorCoreSubsystem.h" // 核心运行时子系统（如果存在）
#include "PropertyAnimatorCoreEditorSubsystem.h" // 编辑器子系统（仅编辑器代码）
```

### 基本用法

以下示例展示了如何在 C++ 中为 Actor 添加并配置一个属性动画器。

```cpp
// 在 Actor 的 BeginPlay 或适当的初始化函数中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取或创建 PropertyAnimatorCoreComponent
    UPropertyAnimatorCoreComponent* AnimatorComponent = FindComponentByClass<UPropertyAnimatorCoreComponent>();
    if (!AnimatorComponent)
    {
        AnimatorComponent = NewObject<UPropertyAnimatorCoreComponent>(this);
        AnimatorComponent->RegisterComponent();
    }

    // 2. 添加一个正弦波动画器实例
    UPropertyAnimatorCoreBase* SineAnimator = AnimatorComponent->AddPropertyAnimator(UPropertyAnimatorCoreSineWave::StaticClass());
    if (SineAnimator)
    {
        // 3. 配置动画器参数 (假设 SineAnimator 有 Amplitude 和 Frequency 属性)
        FPropertyAnimatorCoreSineWaveParams Params;
        Params.Amplitude = 50.0f;
        Params.Frequency = 1.0f;
        SineAnimator->SetParameters(Params);

        // 4. 链接要控制的属性。路径为 "Component.Property.SubProperty"
        //    例如控制场景组件的 Z 轴位置
        FString PropertyPath = TEXT("RootComponent.RelativeLocation.Z");
        SineAnimator->LinkProperty(this, PropertyPath);

        // 5. 启用动画器
        SineAnimator->SetEnabled(true);
    }
}
```

### 进阶用法

以下示例展示了如何在编辑器模块中利用 `UPropertyAnimatorCoreEditorSubsystem` 来扩展编辑器功能。

```cpp
#include "PropertyAnimatorCoreEditorSubsystem.h"

void FMyEditorModule::RegisterCustomAnimatorCategory()
{
    // 1. 获取编辑器子系统实例
    UPropertyAnimatorCoreEditorSubsystem* EditorSubsystem = UPropertyAnimatorCoreEditorSubsystem::Get();
    if (EditorSubsystem)
    {
        // 2. 注册一个新的动画器分类
        FPropertyAnimatorCoreEditorCategoryMetadata MyCategory;
        MyCategory.CategoryIdentifier = FName("MyCustomCategory");
        MyCategory.DisplayText = NSLOCTEXT("MyCategory", "DisplayName", "My Custom Animators");
        MyCategory.TooltipText = NSLOCTEXT("MyCategory", "Tooltip", "Custom animators for my project.");
        
        EditorSubsystem->RegisterAnimatorCategory(MyCategory);
    }
}

void FMyEditorModule::FillContextMenuForProperties(const TArray<FPropertyAnimatorCoreData>& InProperties)
{
    UPropertyAnimatorCoreEditorSubsystem* EditorSubsystem = UPropertyAnimatorCoreEditorSubsystem::Get();
    if (EditorSubsystem)
    {
        // 1. 创建菜单上下文，传入选中的属性
        FPropertyAnimatorCoreEditorMenuContext Context;
        // ... 填充上下文的 Actor 和属性信息 ...

        // 2. 配置菜单选项
        FPropertyAnimatorCoreEditorMenuOptions Options(EPropertyAnimatorCoreEditorMenuType::NewAdvanced | EPropertyAnimatorCoreEditorMenuType::Existing);

        // 3. 获取或创建一个 UToolMenu，然后由子系统填充
        UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("MyApp.ContextMenu");
        EditorSubsystem->FillAnimatorMenu(Menu, Context, Options);
    }
}
```

## Demo 示例

一个最小的、可编译的 C++ 示例，展示如何创建自定义的属性动画器。

```cpp
// MyCustomAnimator.h
#pragma once

#include "CoreMinimal.h"
#include "Animators/PropertyAnimatorCoreBase.h"
#include "MyCustomAnimator.generated.h"

UCLASS(BlueprintType)
class UMyCustomAnimator : public UPropertyAnimatorCoreBase
{
	GENERATED_BODY()

public:
	UMyCustomAnimator();

	// 动画参数
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
	float Speed = 1.0f;

protected:
	// 核心评估函数，每帧调用以计算属性偏移值
	virtual void OnEvaluateAnimation_Implementation(float InProgress, float InDelta) override;

private:
	// 运行时状态
	float CurrentPhase = 0.0f;
};

// MyCustomAnimator.cpp
#include "MyCustomAnimator.h"

UMyCustomAnimator::UMyCustomAnimator()
{
	// 设置显示名称
	SetDisplayText(FText::FromString(TEXT("My Custom Animator")));
}

void UMyCustomAnimator::OnEvaluateAnimation_Implementation(float InProgress, float InDelta)
{
	// 简单的逻辑：随着时间推进相位
	CurrentPhase += InDelta * Speed;
	CurrentPhase = FMath::Fmod(CurrentPhase, 2 * PI); // 保持相位在 [0, 2PI]

	// 计算输出值（例如，一个简单的余弦波）
	float Value = FMath::Cos(CurrentPhase);

	// 将计算结果应用到所有已链接的属性
	for (const FPropertyAnimatorCoreData& LinkedProperty : GetLinkedProperties())
	{
		// 实际应用需要根据属性类型（float, vector等）进行适配
		// 此处为概念示例
		if (LinkedProperty.Property.IsValid())
		{
			// SetPropertyValue(LinkedProperty, Value * LinkedProperty.Scale);
		}
	}
}
```

## 模块依赖

从插件的结构和源码分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `OperatorStack` | 为编辑器中的“算子堆栈”标签页提供自定义 UI 和交互逻辑，用于可视化管理动画器组件。 |
| `Sequencer` (或相关模块) | 用于集成动画器到电影序列器（Sequencer）中，支持创建动画器轨道。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了格式化函数中使用的 scoped enum 可能导致输出乱码的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，可能涉及日志分类或格式的统一。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃了包含 `bIncludeNestedObjects` 参数的旧版对象遍历函数，并引入了新的替代方案。 |
| 2025-12-19 | `a01aeeaa` | check for UObjectInitialized && !IsEngineExitRequested() before running clean-up code that involves | 在执行涉及 UObject 的清理代码前，增加了引擎初始化状态和退出请求的检查，提升稳定性。 |
| 2025-11-18 | `36825f29` | Motion Design: corrected log verbosity from Log to Verbose for logs that were constantly outputting | 将一些频繁输出的日志从 `Log` 级别更正为 `Verbose` 级别，减少日志刷屏。 |

### 维护评价

**活跃维护**。该插件创建于 2025 年 5 月，属于较新的模块。从 git 历史看，在 2026 年 4 月仍有连续的更新，包括错误修复、代码质量改进（日志迁移）和 API 优化（废弃旧函数）。这些更新表明插件正在被持续维护和改进，以适应引擎的最新变化。它作为 Motion Design 套件的一部分被迁移到正式的 VirtualProduction 目录下，表明其成熟度和重要性。目前没有发现已知的废弃警告，推荐在需要运行时/编辑器属性动画功能时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimatorCore)
- 官方文档（暂无）
- 测试用例路径：`Engine/Plugins/VirtualProduction/PropertyAnimatorCore/Source/PropertyAnimatorCoreEditor/Tests/` (假设存在)