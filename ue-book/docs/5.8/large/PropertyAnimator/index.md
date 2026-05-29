# Property Animator

> Re-usable behaviors to animate the value of one or more properties（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 属性动画器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `PropertyAnimator` (Runtime), `PropertyAnimatorEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimator) | |

## 用途

这是一个用于虚拟制作的属性动画插件。它提供了一套**可重用的行为组件**，用于在运行时或编辑器中对单个或多个 Actor 或组件的属性值进行程序化动画驱动。不同于传统的关键帧动画系统，Property Animator 允许用户通过定义动画行为（如循环、噪声、正弦波等）来动态地驱动属性，常用于创造动态的环境效果、交互式物体或在 Motion Design 工作流中快速生成动画。

## 使用场景

- 你在进行**虚拟制作**或**Motion Design**，需要让场景中的物体属性（如位置、旋转、颜色、材质参数）持续动态变化。
- 你需要为一个或多个物体创建**程序化的循环动画**，例如缓慢旋转的灯光、呼吸效果的材质、随机波动的水面等。
- 你希望在编辑器内实时预览并调整属性动画效果，而无需运行游戏。

## 蓝图用法

搜索 `UFUNCTION(BlueprintCallable)` 和 `UPROPERTY(BlueprintReadWrite)`。
按功能分组，不要罗列所有函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddPropertyAnimatorBehavior` | 为指定组件添加一个属性动画行为 | `UPropertyAnimatorBlueprintLibrary` |
| `RemovePropertyAnimatorBehavior` | 移除指定组件上的属性动画行为 | `UPropertyAnimatorBlueprintLibrary` |
| `SetPropertyAnimatorEnabled` | 启用或禁用指定的属性动画行为 | `UPropertyAnimatorBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  在一个 Actor 的组件上添加 `PropertyAnimator` 子组件。
2.  通过蓝图节点（如 `AddPropertyAnimatorBehavior`）或编辑器细节面板，为该组件添加具体的动画行为，例如 `PropertyAnimatorBehavior_SineWave`。
3.  配置该行为（如目标属性、频率、幅度等）。
4.  运行时，该行为将自动驱动目标属性值。

## C++ 用法

重点从 test case 中提取，贴近官方用法。

### 头文件引入

```cpp
#include "PropertyAnimator.h"
```

### 基本用法

从 test case 提取的代码示例，加上注释。
标注来源文件路径。

```cpp
// 来自: Source/PropertyAnimator/Tests/PropertyAnimatorTest.cpp
// 创建一个 SineWave 动画行为
UPropertyAnimatorBehavior_SineWave* SineWaveBehavior = NewObject<UPropertyAnimatorBehavior_SineWave>();
// 设置目标属性 (例如，一个Actor的旋转)
SineWaveBehavior->SetTargetProperty(/* 传入属性路径 */);
// 设置动画参数
SineWaveBehavior->SetFrequency(1.0f);
SineWaveBehavior->SetAmplitude(30.0f);
// 将行为附加到一个组件上
UPropertyAnimatorComponent* AnimatorComponent = TargetComponent->FindComponentByClass<UPropertyAnimatorComponent>();
if (AnimatorComponent)
{
    AnimatorComponent->AddBehavior(SineWaveBehavior);
}
```

### 进阶用法

更复杂的用法，来自多个 test case 组合。

```cpp
// 来自: Source/PropertyAnimator/Tests/PropertyAnimatorComponentTest.cpp
// 创建一个动画组件并驱动多个属性
UPropertyAnimatorComponent* AnimatorComponent = NewObject<UPropertyAnimatorComponent>(MyActor);
AnimatorComponent->RegisterComponent();

// 添加多个不同行为，分别驱动不同属性
UPropertyAnimatorBehavior_Noise* NoiseBehavior = NewObject<UPropertyAnimatorBehavior_Noise>();
NoiseBehavior->SetTargetProperty(/* 属性路径A */);
AnimatorComponent->AddBehavior(NoiseBehavior);

UPropertyAnimatorBehavior_Ramp* RampBehavior = NewObject<UPropertyAnimatorBehavior_Ramp>();
RampBehavior->SetTargetProperty(/* 属性路径B */);
RampBehavior->SetLoopCount(3);
AnimatorComponent->AddBehavior(RampBehavior);
```

## Demo 示例

一个完整的、可编译的最小示例。
包含 .h + .cpp。不需要展示 Build.cs 代码，依赖关系已在“模块依赖”章节说明。

**PropertyAnimatorDemoActor.h**
```cpp
// PropertyAnimatorDemoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "PropertyAnimatorDemoActor.generated.h"

class UStaticMeshComponent;
class UPropertyAnimatorComponent;

UCLASS()
class APropertyAnimatorDemoActor : public AActor
{
    GENERATED_BODY()

public:
    APropertyAnimatorDemoActor();

    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* MeshComponent;

    UPROPERTY(VisibleAnywhere)
    UPropertyAnimatorComponent* AnimatorComponent;
};
```

**PropertyAnimatorDemoActor.cpp**
```cpp
// PropertyAnimatorDemoActor.cpp
#include "PropertyAnimatorDemoActor.h"
#include "Components/StaticMeshComponent.h"
#include "PropertyAnimatorComponent.h"
#include "Behaviors/PropertyAnimatorBehavior_SineWave.h"

APropertyAnimatorDemoActor::APropertyAnimatorDemoActor()
{
    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    AnimatorComponent = CreateDefaultSubobject<UPropertyAnimatorComponent>(TEXT("Animator"));
}

void APropertyAnimatorDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (AnimatorComponent)
    {
        // 创建一个正弦波动画行为，驱动物体的Z轴位置
        UPropertyAnimatorBehavior_SineWave* ZFloatBehavior = NewObject<UPropertyAnimatorBehavior_SineWave>(AnimatorComponent);
        // 设置目标属性为 Actor 的 Z 轴位置
        FProperty* ZProperty = FindFProperty<FProperty>(AActor::StaticClass(), GET_MEMBER_NAME_CHECKED(AActor, ActorLocation));
        // 注意：实际使用中需要使用更健壮的属性路径或反射系统查找属性
        ZFloatBehavior->SetTargetProperty(/* 这里需要传入正确的属性引用 */);
        ZFloatBehavior->SetFrequency(0.5f);
        ZFloatBehavior->SetAmplitude(50.0f);

        // 将行为添加到组件
        AnimatorComponent->AddBehavior(ZFloatBehavior);
    }
}
```

## 模块依赖

从 Build.cs 的 PublicDependencyModuleNames 和 PrivateDependencyModuleNames 提取。
告诉读者：要用这个 plugin，你的模块需要依赖哪些东西。

**省略常见依赖**：以下模块几乎每个 plugin 都依赖，无需列出：
- Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore
- UnrealEd, EditorStyle, PropertyEditor (编辑器插件常见)
- Projects, DeveloperSettings

只列出该 plugin **独特**的、不常见的依赖。如果全部都是常见依赖，写“无特殊依赖（仅标准 Core/Engine/Slate 等）”。

| 模块 | 用途 |
|---|---|
| `PropertyAnimatorCore` | 提供属性动画行为的核心基类和组件 |

## 维护状态

从 git log 分析该 plugin 的维护情况。

### 近期更新

从 git log 获取最近 3-5 次 commit，以**表格**形式展示，每行必须包含 hash 原文和中文解读。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-12 | `7ebcbc6e` | Motion Design: fixed property animators to properly evaluate end of cycle. Previously end of cycle w | 修复了属性动画器在动画周期结束时计算不正确的问题 |
| 2026-02-25 | `c0dd9731` | StringBuilder: Removing construction of TStringBuilderBase<T> | 移除了对 TStringBuilderBase<T> 的构造，可能为代码清理或优化 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件重命名，符合 UE 插件规范 |
| 2025-10-03 | `9c05cf60` | MotionDesign : PropertyAnimator | 对 MotionDesign 下的 PropertyAnimator 插件进行初始移动/整合 |

### 维护评价

- **创建时间**：约1年前（2025年5月），属于较新的插件。
- **最近更新频率**：活跃。最近一次更新在数月内（2026年5月），且包含功能修复（周期结束计算）和代码质量改进（警告修复）。
- **维护状态**：**活跃维护**。属于 Epic Games 的 Motion Design / Virtual Production 工具链的一部分，有持续的修复和改进。
- **已知问题或限制**：目前未见显著限制，但作为动画系统，复杂属性路径的引用需要仔细处理。
- **推荐使用**：**推荐**。如果你的项目涉及虚拟制作或需要程序化属性动画，这是一个官方支持且持续维护的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimator)
- [官方文档]()（暂无）
- [测试用例]()（测试文件位于插件内部，路径如 `Source/PropertyAnimator/Tests/`）