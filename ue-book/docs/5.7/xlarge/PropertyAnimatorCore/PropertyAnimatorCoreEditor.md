# Property Animator Core

> Re-usable behaviors to control properties at runtime and in editor

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、预设） |
| 模块 | `PropertyAnimatorCore` (Runtime), `PropertyAnimatorCoreEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PropertyAnimatorCore) | |

## 用途

Property Animator Core 是一个为虚拟制作（Virtual Production）场景设计的属性动画框架。它提供了一套可复用的行为（Behaviors），用于在编辑器和运行时动态控制 Actor 或 Component 的各种属性（如位置、旋转、材质参数、灯光强度等）。

该插件的核心价值在于：
1.  **统一接口**：为不同类型的属性动画（如振荡、脉冲、弹跳等）提供统一的创建、管理和控制接口。
2.  **编辑器集成**：深度集成到 Unreal Editor 的细节面板（Details Panel）中，允许用户直接在属性行上添加、配置和预览动画效果。
3.  **预设系统**：支持将复杂的动画配置保存为预设资产（Preset Asset），方便复用和共享。
4.  **运行时控制**：不仅在编辑器中可用，其核心动画逻辑在打包后的运行时同样有效，适用于需要动态调整场景元素的虚拟制片流程。

它解决了在虚拟制作现场或后期调整中，需要快速、直观地为场景中的多个物体添加和同步复杂动画效果的需求。

## 使用场景

-   **虚拟制片灯光调整**：在 LED Volume 拍摄中，需要实时调整环境光或特定灯光的颜色、强度以匹配拍摄内容，可以使用 Property Animator 为灯光属性添加平滑的过渡或循环动画。
-   **动态场景元素**：为场景中的旗帜、水面、机械装置等添加持续的、基于物理或艺术指导的动画效果。
-   **材质参数动画**：动态控制材质的标量、向量参数（如金属度、粗糙度、自发光颜色），实现材质随时间或事件变化的效果。
-   **批量属性控制**：需要同时控制多个 Actor 上相同类型属性（例如，让一排灯同时闪烁）时，可以通过预设或链接功能快速实现。

## 蓝图用法

该插件的蓝图 API 主要通过编辑器子系统 `UPropertyAnimatorCoreEditorSubsystem` 暴露，用于在编辑器工具或蓝图编辑器工具中扩展功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` | 获取 PropertyAnimatorCoreEditorSubsystem 的单例实例。 | `UPropertyAnimatorCoreEditorSubsystem` |
| `FillAnimatorMenu` | 根据提供的上下文和选项，填充一个工具菜单（UToolMenu）用于添加、链接或管理动画器。 | `UPropertyAnimatorCoreEditorSubsystem` |
| `CreatePresetAsset` | 为一个或多个可预设化（Presetable）的对象创建一个新的预设资产。 | `UPropertyAnimatorCoreEditorSubsystem` |
| `RegisterAnimatorCategory` | 注册一个新的动画器类别，用于在菜单中组织不同类型的动画器。 | `UPropertyAnimatorCoreEditorSubsystem` |
| `FindAnimatorCategory` | 根据标识符查找一个已注册的动画器类别。 | `UPropertyAnimatorCoreEditorSubsystem` |

### 使用示例（蓝图描述）

1.  **在编辑器工具中创建自定义菜单**：
    *   获取 `UPropertyAnimatorCoreEditorSubsystem` 实例。
    *   创建一个 `FPropertyAnimatorCoreEditorMenuContext` 结构体，传入当前选中的 Actor 或属性数据。
    *   创建一个 `FPropertyAnimatorCoreEditorMenuOptions` 结构体，指定要生成的菜单类型（如 `NewAdvanced`）。
    *   调用 `FillAnimatorMenu` 节点，传入一个 `UToolMenu` 引用、上下文和选项，即可生成包含添加动画器、链接预设等选项的菜单。

2.  **创建并保存动画预设**：
    *   获取子系统实例。
    *   准备一个包含 `IPropertyAnimatorCorePresetable` 接口对象的数组（通常由动画器组件提供）。
    *   调用 `CreatePresetAsset` 节点，指定预设类（如 `UPropertyAnimatorCorePresetBase` 的子类）和可预设化对象数组。
    *   节点将返回创建的预设资产对象，可以将其保存到内容浏览器中。

## C++ 用法

### 头文件引入

```cpp
#include "Subsystems/PropertyAnimatorCoreEditorSubsystem.h"
#include "Menus/PropertyAnimatorCoreEditorMenuDefs.h"
```

### 基本用法

以下示例展示了如何在 C++ 编辑器模块中，为当前选中的 Actor 生成一个“添加动画器”的上下文菜单。

```cpp
// 来源：基于 PropertyAnimatorCoreEditorSubsystem.h 的 API 推断
void UMyEditorUtility::ShowAnimatorMenuForSelectedActors()
{
    // 1. 获取子系统实例
    UPropertyAnimatorCoreEditorSubsystem* Subsystem = UPropertyAnimatorCoreEditorSubsystem::Get();
    if (!Subsystem)
    {
        return;
    }

    // 2. 构建菜单上下文 (假设已有选中的 Actor 集合)
    TSet<UObject*> SelectedObjects = GetSelectedObjects(); // 你的获取选中对象逻辑
    TArray<FPropertyAnimatorCoreData> SelectedProperties; // 可选，如果需要针对特定属性
    FPropertyAnimatorCoreEditorMenuContext Context(SelectedObjects, SelectedProperties);

    // 3. 构建菜单选项
    FPropertyAnimatorCoreEditorMenuOptions Options;
    Options.MenuTypes = static_cast<uint8>(EPropertyAnimatorCoreEditorMenuType::NewAdvanced); // 使用高级菜单，包含子菜单
    Options.bUseTransact = true; // 启用撤销/重做
    Options.bCreateSubMenu = false; // 不创建子菜单容器

    // 4. 创建或获取一个 UToolMenu (通常由 Slate 菜单框架管理)
    UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("MyEditorUtility.ContextMenu");

    // 5. 填充菜单
    if (Subsystem->FillAnimatorMenu(Menu, Context, Options))
    {
        // 菜单填充成功，可以将其弹出显示
        FToolMenuContext MenuContext;
        FSlateApplication::Get().PushMenu(
            FSlateApplication::Get().GetActiveTopLevelWindow().ToSharedRef(),
            FWidgetPath(),
            Menu->GenerateWidget(MenuContext),
            FSlateApplication::Get().GetCursorPos(),
            FPopupTransitionEffect(FPopupTransitionEffect::ContextMenu)
        );
    }
}
```

### 进阶用法

注册自定义动画器类别，以便在插件的菜单系统中显示。

```cpp
// 来源：基于 PropertyAnimatorCoreEditorSubsystem.h 的 API 推断
void UMyAnimatorModule::StartupModule()
{
    // 在模块启动时注册类别
    UPropertyAnimatorCoreEditorSubsystem* Subsystem = UPropertyAnimatorCoreEditorSubsystem::Get();
    if (Subsystem)
    {
        FPropertyAnimatorCoreEditorCategoryMetadata MyCategoryMetadata;
        MyCategoryMetadata.Name = FName("MyCustomCategory");
        MyCategoryMetadata.DisplayName = NSLOCTEXT("MyAnimator", "CustomCategory", "My Custom Animators");
        
        Subsystem->RegisterAnimatorCategory(MyCategoryMetadata);
    }
}
```

## Demo 示例

一个最小化的自定义动画器行为示例，演示了如何继承核心基类。

```cpp
// MyOscillateAnimator.h
#pragma once

#include "Animators/PropertyAnimatorCoreBase.h"
#include "MyOscillateAnimator.generated.h"

UCLASS()
class UMyOscillateAnimator : public UPropertyAnimatorCoreBase
{
    GENERATED_BODY()

public:
    UMyOscillateAnimator();

    //~ Begin UPropertyAnimatorCoreBase Interface
    virtual void EvaluateProperties(FPropertyAnimatorCoreData& InPropertyData, const FPropertyAnimatorCoreEvaluationData& InEvaluationData) override;
    //~ End UPropertyAnimatorCoreBase Interface

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    float Amplitude = 50.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    float Frequency = 1.0f;
};
```

```cpp
// MyOscillateAnimator.cpp
#include "MyOscillateAnimator.h"
#include "Properties/PropertyAnimatorCoreData.h"

UMyOscillateAnimator::UMyOscillateAnimator()
{
    // 设置动画器的显示名称
    SetAnimatorDisplayName(NSLOCTEXT("MyAnimator", "Oscillate", "My Oscillate"));
}

void UMyOscillateAnimator::EvaluateProperties(FPropertyAnimatorCoreData& InPropertyData, const FPropertyAnimatorCoreEvaluationData& InEvaluationData)
{
    // 获取当前时间（由框架提供）
    const float CurrentTime = InEvaluationData.Time;

    // 计算基于正弦波的偏移量
    const float Offset = Amplitude * FMath::Sin(2.0f * PI * Frequency * CurrentTime);

    // 将偏移量应用到属性上
    // 注意：实际应用方式取决于属性类型（FVector, FRotator, float等），这里仅为示意
    if (InPropertyData.IsA<FVector>())
    {
        FVector CurrentValue = InPropertyData.GetValue<FVector>();
        CurrentValue.Z += Offset; // 假设我们只影响Z轴
        InPropertyData.SetValue(CurrentValue);
    }
    // ... 处理其他类型
}
```

## 模块依赖

该插件依赖于 `OperatorStack` 插件。对于使用该插件功能的项目模块，通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `PropertyAnimatorCore` | 运行时核心逻辑，包含动画器基类、属性数据、评估框架。 |
| `PropertyAnimatorCoreEditor` | 编辑器扩展，包含菜单系统、细节面板自定义、预设管理。 |
| `OperatorStack` | 提供操作栈（Operator Stack）框架，可能用于管理动画器的组合与执行顺序。 |

## 维护状态

### 近期更新

```
- 12579b17f580 MotionDesign : PropertyAnimator - Deprecating legacy bounce, oscillate, pulse animator (can't be added from menu) - Fixed allowing preset animator to be added from the advanced context menu of details panel
- 1a1d59465471 MotionDesign : PropertyAnimator - Fixed numeric animator would wait for all range elements to finish current animation cycle before entering new cycle creating a gap - Fixed animator negative offset on range property does not reverse order of animation
- fcc7551f3627 MotionDesign : PropertyAnimator - Added reset button to player controls that pauses and sets time to 0 for manual time source
```

**解读**：
1.  `12579b17f580`: 标记了旧版动画器（弹跳、振荡、脉冲）为废弃，并修复了从细节面板高级菜单添加预设动画器的问题。表明插件正在整合和清理旧功能。
2.  `1a1d59465471`: 修复了数值动画器在范围属性上的两个具体bug，涉及动画周期同步和负偏移顺序。这是对核心动画逻辑的稳定性修复。
3.  `fcc7551f3627`: 为播放器控件添加了重置按钮功能，增强了编辑器内的交互控制。

### 维护评价

**活跃维护**。
-   **创建时间**：插件于2024年初创建，非常年轻。
-   **更新频率**：近期提交（截至提供的信息）显示有持续的功能更新（添加新控件）和重要的bug修复。
-   **维护状态**：由 Epic Games 的 MotionDesign 团队维护，属于官方虚拟制作工具链的一部分，预计会持续更新以支持新的制作流程。
-   **已知限制**：从提交信息看，插件正在废弃一些旧的、独立的动画器实现，转向更统一的框架。使用者应注意使用推荐的新版动画器。
-   **推荐使用**：**推荐**。对于在 Unreal Engine 中进行虚拟制作，需要动态控制属性动画的项目，这是一个官方且活跃维护的解决方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PropertyAnimatorCore)
-   [官方文档]() (暂无)
-   [测试用例]() (路径未提供，通常位于 `Engine/Plugins/VirtualProduction/PropertyAnimatorCore/Tests/`)