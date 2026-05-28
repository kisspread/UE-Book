# Common UI Plugin

> A repository for game independent UI elements.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 通用界面 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产、示例、子模块文档） |
| 模块 | `CommonUI` (Runtime), `CommonUIEditor` (Runtime), `CommonInput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-05-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CommonUI) | |

## 用途

CommonUI 是一个功能强大的跨平台UI框架，其核心目标是解决游戏开发中UI输入、管理和适配的共性问题。它不仅仅是提供基础UI控件，而是提供了一个完整的解决方案，用于：

1.  **统一管理输入切换**：自动处理键盘、鼠标、手柄等多种输入设备的焦点管理、导航和光标显示。
2.  **支持丰富的UI资产**：提供一套可重用、可本地化、支持不同输入设备显示的 UI 资产（如按钮、背景），并通过 `UCommonActivatableWidget` 管理 UI 的显示堆栈。
3.  **优化UI性能与流程**：通过 `UCommonActivatableWidget` 和 `UCommonActivatableWidgetContainerBase`（如栈、队列）简化复杂UI（如主菜单、暂停界面、弹窗）的创建和生命周期管理。
4.  **实现平台与输入感知的UI**：UI 能够根据当前平台和使用的输入设备（例如，切换到手柄时）自动调整外观和交互提示。

**简而言之**，它的存在是为了让开发者能够高效地构建一套能够自适应不同平台、输入设备和语言环境的复杂UI系统。

## 使用场景

-   你正在开发一款需要同时支持 PC、主机和移动端的多平台游戏。
-   你的游戏UI需要频繁地在键盘/鼠标与手柄之间无缝切换。
-   你需要构建一个具有复杂导航栈的UI系统（如：主菜单 -> 设置 -> 子设置，或者弹窗队列）。
-   你希望UI资产能够根据输入类型（例如，显示“A”键或“X”按钮）自动变化。
-   你追求一套统一的、可扩展的UI组件库，以保持整个项目UI风格的一致性。

## 蓝图用法

CommonUI 的蓝图节点主要围绕**输入子系统**和**可激活控件容器**展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Common Input Subsystem` | 获取通用输入子系统单例，用于查询和设置输入类型。 | `UCommonInputSubsystem` |
| `Set Input Type` | 切换当前的输入类型（鼠标键盘、手柄、触摸）。 | `UCommonInputSubsystem` |
| `Push Widget` | 将一个 `UCommonActivatableWidget` 压入一个容器（栈或队列）进行显示。 | `UCommonActivatableWidgetContainerBase` |
| `Pop Widget` | 从容器栈中弹出顶部的控件。 | `UCommonActivatableWidgetContainerBase` |
| `Clear Widgets` | 清空容器中的所有控件。 | `UCommonActivatableWidgetContainerBase` |
| `Find Widget Of Type` | 在容器中查找指定类型的活动控件。 | `UCommonActivatableWidgetContainerBase` |
| `Start Async Load Asset` | 异步加载一个 `UCommonUIInputActionData` 等资产。 | `UCommonUILoadAssetProxy` |

### 使用示例（蓝图描述）

1.  **创建通用导航栈**：在场景中放置一个 `UCommonActivatableWidgetContainer_Stack` 组件。通过其 `Push Widget` 函数，将你的主菜单（一个继承自 `UCommonActivatableWidget` 的蓝图类）压入栈中显示。
2.  **响应输入类型切换**：在你的UI控件（如自定义按钮）的 `Event Construct` 中，获取 `Common Input Subsystem`，并根据其当前的输入类型（`GetCurrentInputType`）来设置不同的图标或提示文本。
3.  **管理弹窗队列**：使用 `UCommonActivatableWidgetContainer_Queue`，调用 `Push Widget` 将多个弹窗蓝图实例加入队列。系统会按顺序依次显示它们，并在前一个关闭后自动显示下一个。

## C++ 用法

### 头文件引入

```cpp
#include "CommonActivatableWidget.h"
#include "CommonActivatableWidgetContainer.h"
#include "CommonInputSubsystem.h"
#include "CommonUIInputActionData.h"
```

### 基本用法

从核心子模块提取的典型用法。

```cpp
// 在某个 UI 管理器类中，使用栈容器管理一个设置界面
UPROPERTY()
TObjectPtr<UCommonActivatableWidgetContainer_Stack> SettingsStack;

// 创建并显示设置界面
void UMyGameUIManager::OpenSettings()
{
    UMySettingsWidget* SettingsWidget = CreateWidget<UMySettingsWidget>(GetWorld(), SettingsWidgetClass);
    SettingsStack->PushWidget(SettingsWidget);
}

// 关闭当前顶部的设置界面
void UMyGameUIManager::CloseSettings()
{
    SettingsStack->PopWidget();
}
```

*(代码灵感源自 `CommonUI` 模块中 Widget 容器的使用逻辑)*

### 进阶用法

结合输入子系统与资产加载，实现动态输入提示。

```cpp
// 异步加载一个描述“交互”操作的输入数据资产
void UMyInteractionPromptWidget::LoadInteractActionData()
{
    FSoftObjectPath ActionPath = TEXT("/Game/UI/InputActions/IA_Interact.IA_Interact");
    UCommonUIInputActionData* ActionData = Cast<UCommonUIInputActionData>(ActionPath.TryLoad());
    // 或者使用异步加载代理：UCommonUILoadAssetProxy
    if (ActionData)
    {
        // 根据 ActionData 和当前输入子系统，更新显示的按键图标和提示文本
        UpdatePromptForInputType(ActionData);
    }
}
```

*(代码结构参考了 `CommonInput` 模块中输入数据加载与应用的模式)*

## Demo 示例

一个最小的“设置界面压栈”示例。

```cpp
// MyUIManager.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "CommonActivatableWidgetContainer.h"
#include "MyUIManager.generated.h"

UCLASS()
class MYGAME_API UMyUIManager : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(Transient)
    TObjectPtr<UCommonActivatableWidgetContainer_Stack> MenuStack;

    UFUNCTION(BlueprintCallable, Category = "UI")
    void ShowSettingsPanel();

    UFUNCTION(BlueprintCallable, Category = "UI")
    void HideTopPanel();
};
```

```cpp
// MyUIManager.cpp
#include "MyUIManager.h"
#include "CommonActivatableWidget.h"
#include "MySettingsWidget.h" // 假设你的设置控件蓝图派生自此

void UMyUIManager::ShowSettingsPanel()
{
    if (!MenuStack) return;

    UCommonActivatableWidget* SettingsWidget = NewObject<UMySettingsWidget>(this, UMySettingsWidget::StaticClass());
    MenuStack->PushWidget(SettingsWidget);
}

void UMyUIManager::HideTopPanel()
{
    if (!MenuStack) return;

    MenuStack->PopWidget();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 集成增强输入系统，用于处理复杂的输入映射和操作数据。 |
| `GameplayTagsEditor` | 支持在编辑器中对 GamePlay Tag 进行编辑和配置（CommonUI 使用 Tag 来标识和管理输入操作）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ea0fcb96` | [UMG/Slate] Proximate Entry Navigation - ScrollIntoView Local Space & Intra-Entry List Interior Guar | 优化了UMG/Slate中近端条目的导航和列表内部的滚动保证逻辑。 |
| 2026-05-26 | `356fcc56` | [Virtual Pointer] Ignore the synthetic mouse-move event that UCommonInputSubsystem::SetCursorPositio | 虚拟指针模式下，忽略由SetCursorPosition生成的合成鼠标移动事件，避免干扰。 |
| 2026-05-25 | `a10370d0` | [Virtual Pointer] FCommonAnalogCursor::RefreshCursorVisibility: gate viewport cursor writes on actua | 虚拟指针模式下，仅在游戏手柄驱动时才更新视口光标可见性。 |
| 2026-05-22 | `e3f56aa5` | [Virtual Pointer] In VP mode, clamp the cursor to the viewport only when gamepad is driving it; mous | 在VP模式下，仅当游戏手柄控制时才将光标限制在视口内。 |
| 2026-05-20 | `4bcb727a` | CommonListView, SCommonTileView - Repair non-proximate pathway to not mutate focus when there is no | 修复了CommonListView和SCommonTileView在非近端路径下可能错误改变焦点的问题。 |

### 维护评价

**积极维护中**。CommonUI 插件创建时间约3年，正处于功能稳定和优化的阶段。从近期的 Git 记录可以看出，Epic Games 的团队正在**非常活跃地维护和改进**此插件，更新频率高（近一周内多次提交），并且工作重点集中在修复复杂的输入和导航问题（如虚拟指针、焦点管理），这表明它是一个被官方寄予厚望的核心UI框架，正在被持续打磨。

**强烈推荐使用**，特别是对于需要处理多平台输入和构建复杂UI流程的新项目。`EnabledByDefault: false` 意味着需要手动启用，这是为了控制在不适用项目中的体积，但其本身是稳定且受支持的。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CommonUI)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CommonUI/Tests) (如果存在，请验证具体路径)