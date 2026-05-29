# Actor Modifier

> Actual implementation of modifiers for actors based on ActorModifierCore plugin

| 属性 | 值 |
|---|---|
| 中文名 | Actor修饰器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（布局修饰器类） |
| 模块 | `ActorModifierLayout` (Runtime), `ActorModifierRendering` (Runtime), `ActorModifierEditor` (Runtime), `ActorModifier` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifier) | |

## 用途

此插件基于 `ActorModifierCore` 框架，提供了**一系列用于控制 Actor 空间布局和变换的修饰器（Modifier）**。它不是通用的变换工具，而是专注于解决虚拟制作和 Motion Design 工作流中，对 Actor 进行程序化、规则化空间排列和对齐的需求。

其核心价值在于：通过附加一个修饰器组件，即可自动、动态地将一组 Actor（通常是子 Actor）按照预设的规则（如网格、径向、对齐、沿样条线等）进行排列和变换，无需编写复杂的蓝图或 C++ 逻辑。这使得创建复杂的动态布局变得快速且易于维护。

## 使用场景

- **Motion Design 动态布局**：你需要创建一个环形菜单、径向仪表盘或沿样条线分布的按钮，使用 `RadialArrangeModifier` 或 `SplinePathModifier`。
- **UI 元素网格对齐**：你需要将一组 UI Actor 以网格形式精确对齐，使用 `GridArrangeModifier`。
- **规则化空间排列**：你需要让一组物体基于某个边界框进行水平/垂直对齐，使用 `JustifyModifier`。
- **动态跟随效果**：你需要让一个 Actor 始终跟随另一个 Actor 的边界移动，使用 `AutoFollowModifier`。
- **注视效果**：你需要让一个 Actor 始终“看向”另一个目标 Actor，使用 `LookAtModifier`。
- **平均位置对齐**：你需要让一个 Actor 位于多个其他 Actor 的平均位置，使用 `AlignBetweenModifier`。

## 蓝图用法

所有修饰器均派生自 `UActorModifierCoreBase`，并暴露了丰富的蓝图可调用属性和函数。使用它们的通用模式是：**向目标 Actor 添加对应的修饰器组件，然后配置其属性**。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRadialArrangeModifier` (示例) | 向 Actor 添加一个指定的修饰器组件 | `UActorModifierCoreBase` 子类 |
| `SetCount`, `SetRings`, `SetInnerRadius`... | 配置“径向排列”修饰器的各项参数 | `UActorModifierRadialArrangeModifier` |
| `SetHorizontalAlignment`, `SetVerticalAlignment`... | 配置“对齐”修饰器的对齐方式和锚点 | `UActorModifierJustifyModifier` |
| `SetSplineActor`, `SetSampleMode`, `SetProgress`... | 配置“样条路径”修饰器的路径和采样方式 | `UActorModifierSplinePathModifier` |
| `SetReferenceActor`, `SetFollowedAxis`, `SetProgress`... | 配置“自动跟随”修饰器的跟随目标和行为 | `UActorModifierAutoFollowModifier` |
| `SetReferenceActor`, `SetOrientationAxis`... | 配置“注视”修饰器的注视目标和朝向轴 | `UActorModifierLookAtModifier` |
| `SetCount`, `SetSpread`, `SetStartCorner`... | 配置“网格排列”修饰器的行列数和间距 | `UActorModifierGridArrangeModifier` |
| `AddReferenceActor`, `RemoveReferenceActor`, `SetReferenceActors` | 管理“居中对齐”修饰器的目标 Actor 列表 | `UActorModifierAlignBetweenModifier` |

### 使用示例（蓝图描述）

1.  **为 Actor 添加径向排列修饰器**：
    *   在 Actor 的组件面板中，选择 `Add Component`，搜索并添加 `RadialArrangeModifier`。
    *   在细节面板中配置 `Rings`（环数）、`InnerRadius`（内半径）等参数。
    *   确保该 Actor 下有足够的子 Actor，它们将被自动排列成环形。
2.  **让 Actor 沿样条线移动**：
    *   在场景中创建一个带有 `SplineComponent` 的 Actor（如路径线）。
    *   在另一个需要移动的 Actor 上，添加 `SplinePathModifier` 组件。
    *   在其 `Spline Actor` 属性中选择步骤1创建的样条线 Actor。
    *   通过调整 `Progress` 或 `Distance` 属性，或在运行时通过蓝图动态修改它们，即可驱动 Actor 沿样条线移动。
3.  **创建网格布局**：
    *   在一个父 Actor 下添加多个子 Actor。
    *   为父 Actor 添加 `GridArrangeModifier`。
    *   设置 `Count` 为 (3, 2) 创建一个 3 列 2 行的网格，并用 `Spread` 控制行列间距。

## C++ 用法

### 头文件引入

```cpp
#include "Modifiers/ActorModifierRadialArrangeModifier.h" // 以径向排列为例
#include "Modifiers/ActorModifierSplinePathModifier.h"
#include "ActorModifierCoreModule.h" // 核心模块
```

### 基本用法

从 API 结构推断的用法。核心是获取或创建修饰器实例并设置其属性。

```cpp
// 假设 MyActor 是一个 AActor*，并且有子 Actor
// 为 MyActor 添加一个径向排列修饰器
UActorModifierRadialArrangeModifier* RadialModifier = NewObject<UActorModifierRadialArrangeModifier>(MyActor);
// 将修饰器组件注册到 Actor
MyActor->AddOwnedComponent(RadialModifier);
RadialModifier->RegisterComponent();

// 配置修饰器属性
RadialModifier->SetRings(2);
RadialModifier->SetInnerRadius(100.0f);
RadialModifier->SetOuterRadius(300.0f);
RadialModifier->SetStartAngle(-90.0f);
RadialModifier->SetEndAngle(90.0f);
RadialModifier->SetOrient(true); // 让子元素朝向圆心
RadialModifier->SetOrientationAxis(EActorModifierAxis::X);

// 触发一次应用（通常属性设置会自动触发）
// RadialModifier->Apply(); // 如果需要手动触发
```

### 进阶用法

结合样条路径和运行时动态修改，创建一个动态沿路径移动的元素。

```cpp
// 假设 PathActor 是一个包含 SplineComponent 的 AActor*
// 在另一个 Actor (MoverActor) 上添加样条路径修饰器
UActorModifierSplinePathModifier* SplineModifier = NewObject<UActorModifierSplinePathModifier>(MoverActor);
MoverActor->AddOwnedComponent(SplineModifier);
SplineModifier->RegisterComponent();

// 设置样条线目标
SplineModifier->SetSplineActor(PathActor);
SplineModifier->SetSampleMode(EActorModifierLayoutSplinePathSampleMode::Percentage);
SplineModifier->SetOrient(true); // 沿路径方向旋转
SplineModifier->SetBaseOrientation(FRotator(0, 90, 0)); // 添加一个基础旋转偏移

// 在游戏逻辑中（如 Tick），动态更新进度
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (SplineModifier)
    {
        float NewProgress = FMath::Fmod(CurrentProgress + DeltaTime * 0.1f, 1.0f);
        SplineModifier->SetProgress(NewProgress);
    }
}
```

## Demo 示例

以下是一个在 C++ 中向 Actor 添加并配置径向排列修饰器的最小示例。

**MyActorWithRadialLayout.h**
```cpp
// MyActorWithRadialLayout.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActorWithRadialLayout.generated.h"

class UActorModifierRadialArrangeModifier;

UCLASS()
class MYPROJECT_API AMyActorWithRadialLayout : public AActor
{
    GENERATED_BODY()
    
public:
    AMyActorWithRadialLayout();

    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Layout")
    UActorModifierRadialArrangeModifier* RadialModifier;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Layout")
    float Radius = 200.0f;
};
```

**MyActorWithRadialLayout.cpp**
```cpp
// MyActorWithRadialLayout.cpp
#include "MyActorWithRadialLayout.h"
#include "Modifiers/ActorModifierRadialArrangeModifier.h"

AMyActorWithRadialLayout::AMyActorWithRadialLayout()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建根组件和径向排列修饰器
    USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);
    
    RadialModifier = CreateDefaultSubobject<UActorModifierRadialArrangeModifier>(TEXT("RadialLayout"));
    // 修饰器需要附加到根组件才能正确工作
    RadialModifier->SetupAttachment(Root);
}

void AMyActorWithRadialLayout::BeginPlay()
{
    Super::BeginPlay();

    // 在游戏开始时应用配置
    if (RadialModifier)
    {
        RadialModifier->SetRings(1);
        RadialModifier->SetInnerRadius(Radius);
        RadialModifier->SetStartAngle(-180.0f);
        RadialModifier->SetEndAngle(180.0f);
        RadialModifier->SetArrangement(EActorModifierRadialArrangeMode::Equal);
        RadialModifier->SetOrient(true);
        RadialModifier->SetOrientationAxis(EActorModifierAxis::X);
    }
    // 确保这个 Actor 下有子 Actor，它们将被自动排列
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ActorModifierCore` | 提供修饰器基类和框架 |
| `PropertyAnimation` | 提供属性动画和插值支持 (基于文件分析推断) |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-09 | `bdd66985` | Motion Design: made render state dirty reason optional + added some fixes to the text3d update causing some issues. | 为渲染状态更新原因增加可选性，并修复了导致文本3D更新问题的缺陷。 |
| 2026-04-08 | `5c28c1d0` | Motion Design: added render state dirty reason scope for the modifier system to have a better idea of when to update. | 为修饰器系统添加了渲染状态脏标记作用域，以优化更新时机判断。 |
| 2026-03-13 | `ab2df2c3` | Motion Design: moved usage of core ticker to custom ts ticker instance to better control timing. | 将核心定时器改为使用自定义时间步进实例，以更好地控制计时逻辑。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从 `Base` 命名规范改为 `Default` 命名规范。 |
| 2025-09-23 | `cabb6e4f` | MotionDesign : ActorModifier | ActorModifier 插件的初始功能提交或重大更新。 |

### 维护评价

该插件模块 **处于活跃维护状态**。
1.  **创建时间**：创建于 2025 年 5 月，是一个相对年轻的插件。
2.  **更新频率**：从提交历史看，在 2026 年 3 月至 4 月期间有多次功能性更新和优化（如修复问题、改进系统架构），显示开发仍在进行。
3.  **维护状态**：最近一次提交在 2026 年 4 月，距今（2025 年）不足一年，且内容涉及核心功能优化，表明**仍在积极维护和开发**。
4.  **使用建议**：作为 Virtual Production 工具链的一部分，该插件是 Epic 官方提供并维护的，**推荐用于 Motion Design 和虚拟制作工作流中**。它依赖于 `ActorModifierCore` 框架，设计上较为模块化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifier)
- [官方文档]() （暂无）
- [测试用例]() （暂未在提供的文件列表中明确列出，可能位于 `Engine/Tests` 或插件内部 `Tests` 目录）