# Common UI Plugin

> A repository for game independent UI elements.

| 属性 | 值 |
|---|---|
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、样式模板、数据表） |
| 模块 | `CommonUI` (Runtime), `CommonUIEditor` (Editor), `CommonInput` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CommonUI) | |

## 用途

CommonUI 是 Epic 为跨平台游戏 UI 开发提供的**基础设施框架**。它解决的核心问题是：**在不同输入方式（手柄、键鼠、触摸）和不同平台之间，如何让同一套 UI 自适应地工作**。

具体来说，CommonUI 提供了：

1. **输入路由系统**：通过 `UCommonGameViewportClient` 拦截所有输入，优先分发给 UI 处理，再传递给游戏逻辑。这是手柄导航 UI 的基础。
2. **动作绑定系统**（Action Binding）：将 UI 按钮与输入动作绑定，自动根据当前输入方式显示正确的按键图标，并支持长按/短按等交互模式。
3. **硬件感知的可见性控制**：通过 `UCommonUIVisibilitySubsystem` 和 GameplayTag 查询，根据当前平台特征和输入方式自动显示/隐藏 UI 元素。
4. **可复用的 UI 组件库**：提供带样式系统的按钮、文本、边框、列表视图、轮播器、视频播放器等，所有组件都内置了手柄导航和触摸支持。
5. **Widget 生命周期管理**：`UCommonActivatableWidget` 提供激活/停用生命周期，配合动画切换器实现页面转场。

**为什么需要手动启用**：CommonUI 是一个框架级插件，启用后会改变输入处理流程（通过替换 GameViewportClient），因此默认关闭，需要项目主动集成。

## 使用场景

- 你正在开发一款**支持手柄和键鼠的跨平台游戏**，需要 UI 能自动响应输入方式切换 → 用 CommonUI 的输入路由和可见性系统
- 你需要 UI 按钮根据当前输入设备**自动显示正确的按键提示**（如 Xbox 的 A 键 vs PS 的 × 键）→ 用 `UCommonBoundActionBar` + `UCommonBoundActionButton`
- 你有**多个 UI 页面需要切换**，且希望有平滑的转场动画 → 用 `UCommonAnimatedSwitcher` + `UCommonActivatableWidget`
- 你需要**列表/网格视图在手柄上能正确导航**（焦点自动滚动到选中项）→ 用 `UCommonListView` / `UCommonTileView`
- 你需要根据平台（PC/主机/手机）**自动显示或隐藏特定 UI 元素** → 用 `UCommonHardwareVisibilityBorder`
- 你想要一套**统一的 UI 样式系统**，方便全局修改按钮、文本、边框的外观 → 用 `UCommonButtonStyle` / `UCommonTextStyle` / `UCommonBorderStyle`

## 蓝图用法

### 核心节点

#### 动作绑定栏（Action Bar）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Display Owning Player Actions Only` | 设置是否只显示当前玩家的动作按钮 | `UCommonBoundActionBar` |

#### 可见性切换器（Visibility Switcher）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Active Widget Index` | 设置当前显示的子控件索引 | `UCommonVisibilitySwitcher` |
| `Get Active Widget Index` | 获取当前显示的子控件索引 | `UCommonVisibilitySwitcher` |
| `Get Active Widget` | 获取当前显示的子控件 | `UCommonVisibilitySwitcher` |
| `Set Active Widget` | 设置当前显示的子控件（按引用） | `UCommonVisibilitySwitcher` |
| `Increment Active Widget Index` | 切换到下一个子控件 | `UCommonVisibilitySwitcher` |
| `Decrement Active Widget Index` | 切换到上一个子控件 | `UCommonVisibilitySwitcher` |
| `Activate Visible Slot` | 激活当前可见的 Slot | `UCommonVisibilitySwitcher` |
| `Deactivate Visible Slot` | 停用当前可见的 Slot | `UCommonVisibilitySwitcher` |

#### 动画切换器（Animated Switcher）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Activate Next Widget` | 切换到下一个控件（带动画） | `UCommonAnimatedSwitcher` |
| `Activate Previous Widget` | 切换到上一个控件（带动画） | `UCommonAnimatedSwitcher` |
| `Has Widgets` | 是否包含子控件 | `UCommonAnimatedSwitcher` |
| `Set Disable Transition Animation` | 禁用/启用转场动画 | `UCommonAnimatedSwitcher` |
| `Is Currently Switching` | 是否正在切换中 | `UCommonAnimatedSwitcher` |
| `Is Transition Playing` | 是否正在播放转场动画 | `UCommonAnimatedSwitcher` |

#### 旋转选择器（Rotator）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Populate Text Labels` | 设置可选的文本标签数组 | `UCommonRotator` |
| `Get Selected Text` | 获取当前选中的文本 | `UCommonRotator` |
| `Set Selected Item` | 设置当前选中项索引 | `UCommonRotator` |
| `Get Selected Index` | 获取当前选中索引 | `UCommonRotator` |
| `Shift Text Left` | 向左旋转 | `UCommonRotator` |
| `Shift Text Right` | 向右旋转 | `UCommonRotator` |

#### 视频播放器（Video Player）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Video` | 设置要播放的媒体源 | `UCommonVideoPlayer` |
| `Play` | 播放 | `UCommonVideoPlayer` |
| `Pause` | 暂停 | `UCommonVideoPlayer` |
| `Reverse` | 反向播放 | `UCommonVideoPlayer` |
| `Play From Start` | 从头播放 | `UCommonVideoPlayer` |
| `Seek` | 跳转到指定时间 | `UCommonVideoPlayer` |
| `Close` | 关闭视频 | `UCommonVideoPlayer` |
| `Set Looping` | 设置是否循环 | `UCommonVideoPlayer` |
| `Set Is Muted` | 设置是否静音 | `UCommonVideoPlayer` |
| `Get Video Duration` | 获取视频总时长 | `UCommonVideoPlayer` |
| `Get Playback Time` | 获取当前播放时间 | `UCommonVideoPlayer` |
| `Is Playing` | 是否正在播放 | `UCommonVideoPlayer` |
| `Is Paused` | 是否已暂停 | `UCommonVideoPlayer` |

#### 日期时间文本（DateTime Text）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set DateTime Value` | 设置日期时间值，可选择倒计时模式 | `UCommonDateTimeTextBlock` |
| `Set Timespan Value` | 设置时间跨度值 | `UCommonDateTimeTextBlock` |
| `Set Count Down Completion Text` | 设置倒计时结束时显示的文本 | `UCommonDateTimeTextBlock` |
| `Get DateTime` | 获取当前日期时间值 | `UCommonDateTimeTextBlock` |

#### 边框（Border）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Style` | 设置边框样式类 | `UCommonBorder` |

#### 工具函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Parent Widget Of Type` | 向上查找指定类型的父控件 | `UCommonUILibrary` |

#### 子系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Input Action Button Icon` | 获取指定动作在当前手柄上的按键图标 | `UCommonUISubsystemBase` |
| `Get Enhanced Input Action Button Icon` | 获取 Enhanced Input 动作的按键图标 | `UCommonUISubsystemBase` |

#### 轮播导航栏

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Linked Carousel` | 关联轮播控件 | `UCommonWidgetCarouselNavBar` |

#### 控件分组

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Widget` | 向分组添加控件 | `UCommonWidgetGroupBase` |
| `Add Widgets` | 批量添加控件 | `UCommonWidgetGroupBase` |
| `Remove Widget` | 从分组移除控件 | `UCommonWidgetGroupBase` |
| `Remove All` | 清空分组 | `UCommonWidgetGroupBase` |

### 使用示例（蓝图描述）

**场景：创建一个带手柄导航的设置菜单**

1. 创建一个 `UCommonActivatableWidget` 子类作为设置页面
2. 在其中放置 `UCommonVisibilitySwitcher`，添加多个子页面（如"音频"、"视频"、"控制"）
3. 在 Switcher 旁边放置 `UCommonRotator`，用 `PopulateTextLabels` 填充选项名称
4. 将 Rotator 的 `OnRotatedWithDirection` 事件连接到 Switcher 的 `SetActiveWidgetIndex`
5. 在页面底部放置 `UCommonBoundActionBar`，设置 `ActionButtonClass` 为你的 `UCommonBoundActionButton` 子类
6. ActionBar 会自动根据当前输入方式显示"返回"、"确认"等按键提示

**场景：创建一个倒计时活动页面**

1. 创建 `UCommonDateTimeTextBlock`，设置 `CustomTimespanFormat` 为 `"{Days}天 {Hours}时 {Minutes}分 {Seconds}秒"`
2. 调用 `SetDateTimeValue`，传入活动结束时间，`bShowAsCountdown = true`
3. 绑定 `OnTimeCountDownCompletion` 事件，在倒计时结束时显示活动已结束的 UI

## C++ 用法

### 头文件引入

```cpp
#include "CommonUI.h"                    // 模块主头文件
#include "CommonActivatableWidget.h"     // 可激活控件
#include "CommonButtonBase.h"            // 按钮基类
#include "CommonTextBlock.h"             // 文本块
#include "CommonBorder.h"                // 边框
#include "CommonListView.h"              // 列表视图
#include "CommonAnimatedSwitcher.h"      // 动画切换器
#include "CommonVisibilitySwitcher.h"    // 可见性切换器
#include "CommonBoundActionBar.h"        // 动作绑定栏
#include "CommonVideoPlayer.h"           // 视频播放器
#include "CommonDateTimeTextBlock.h"     // 日期时间文本
#include "CommonRotator.h"               // 旋转选择器
#include "CommonUILibrary.h"             // 工具函数库
#include "CommonUISubsystemBase.h"       // UI 子系统
#include "CommonUIVisibilitySubsystem.h" // 可见性子系统
#include "Input/UIActionBinding.h"       // 动作绑定
```

### 基本用法

**创建一个可激活的 Widget 子类**（来自 CommonActivatableWidget 的典型用法）：

```cpp
// MyMenuWidget.h
#pragma once

#include "CommonActivatableWidget.h"
#include "MyMenuWidget.generated.h"

UCLASS()
class UMyMenuWidget : public UCommonActivatableWidget
{
    GENERATED_BODY()

public:
    // 当 Widget 被激活时调用
    virtual void NativeOnActivated() override
    {
        Super::NativeOnActivated();
        // 播放打开动画、设置焦点等
        UE_LOG(LogTemp, Log, TEXT("Menu activated"));
    }

    // 当 Widget 被停用时调用
    virtual void NativeOnDeactivated() override
    {
        Super::NativeOnDeactivated();
        // 播放关闭动画、清理状态等
        UE_LOG(LogTemp, Log, TEXT("Menu deactivated"));
    }

protected:
    // 定义该 Widget 接受的输入方式
    virtual TOptional<FUIInputConfig> GetDesiredInputConfig() const override
    {
        // UI 模式：游戏暂停，输入全部给 UI
        return FUIInputConfig(ECommonInputMode::Menu, EMouseCaptureMode::NoCapture);
    }
};
```

**绑定 UI 动作**（来自 UIActionBinding.h）：

```cpp
// 在 Widget 中绑定一个"返回"动作
void UMyMenuWidget::NativeConstruct()
{
    Super::NativeConstruct();

    FBindUIActionArgs BindArgs;
    BindArgs.InputAction = BackAction;  // UInputAction* 或 FDataTableRowHandle
    BindArgs.OnExecuteAction = FSimpleDelegate::CreateUObject(this, &UMyMenuWidget::HandleBackAction);
    BindArgs.bDisplayInActionBar = true;
    BindArgs.ActionDisplayName = NSLOCTEXT("MyGame", "Back", "返回");

    FUIActionBindingHandle Handle = RegisterUIActionBinding(BindArgs);
}
```

**使用可见性子系统控制 Widget 显示**：

```cpp
// 根据当前输入方式控制 Widget 可见性
void UMyWidget::UpdateVisibilityBasedOnInput()
{
    UCommonUIVisibilitySubsystem* VisSystem = UCommonUIVisibilitySubsystem::Get(GetOwningLocalPlayer());
    if (VisSystem)
    {
        // 检查当前是否有 Gamepad 标签
        if (VisSystem->HasVisibilityTag(FGameplayTag::RequestGameplayTag(TEXT("Input.Gamepad"))))
        {
            SetVisibility(ESlateVisibility::Collapsed);
        }
        else
        {
            SetVisibility(ESlateVisibility::Visible);
        }
    }
}
```

### 进阶用法

**自定义 Widget 池化**（来自 CommonPoolableWidgetInterface.h）：

```cpp
// 实现池化接口，让 WidgetFactory 复用控件实例
UCLASS()
class UMyPoolableItem : public UUserWidget, public ICommonPoolableWidgetInterface
{
    GENERATED_BODY()

protected:
    // 从池中取出时调用
    virtual void OnAcquireFromPool_Implementation() override
    {
        SetVisibility(ESlateVisibility::SelfHitTestInvisible);
        // 重置状态，准备复用
    }

    // 归还到池中时调用
    virtual void OnReleaseToPool_Implementation() override
    {
        SetVisibility(ESlateVisibility::Collapsed);
        // 清理数据，释放资源
    }
};
```

**使用原生列表项**（来自 CommonNativeListItem.h）：

```cpp
// 定义自定义列表项（非 UObject）
class FMyListItem : public FCommonNativeListItem
{
    DERIVED_LIST_ITEM(FMyListItem, FCommonNativeListItem);

public:
    FText DisplayName;
    int32 ItemId;
};

class FMySpecialListItem : public FMyListItem
{
    DERIVED_LIST_ITEM(FMySpecialListItem, FMyListItem);

public:
    FText SpecialDescription;
};

// 使用时可以安全地进行类型判断
void ProcessItem(TSharedPtr<FCommonNativeListItem> Item)
{
    if (auto SpecialItem = Item->AsTypedItem<FMySpecialListItem>())
    {
        // 处理特殊项
    }
    else if (auto NormalItem = Item->AsTypedItem<FMyListItem>())
    {
        // 处理普通项
    }
}
```

**自定义输入动作数据表处理**（来自 CommonGenericInputActionDataTable.h）：

```cpp
// 创建自定义处理器，在 PostLoad 时修改输入动作数据表
UCLASS()
class UMyInputActionProcessor : public UCommonInputActionDataProcessor
{
    GENERATED_BODY()

public:
    virtual void ProcessInputActions(UCommonGenericInputActionDataTable* InputActionDataTable) override
    {
        Super::ProcessInputActions(InputActionDataTable);
        // 可以在这里根据平台修改数据表内容
        // 例如：为特定平台添加额外的按键映射
    }
};
```

## Demo 示例

**一个最小的 CommonUI 页面栈管理示例**：

```cpp
// MyUIManager.h
#pragma once

#include "CoreMinimal.h"
#include "CommonActivatableWidget.h"
#include "CommonActivatableWidgetContainerBase.h"
#include "MyUIManager.generated.h"

UCLASS()
class UMyActivatablePage : public UCommonActivatableWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonTextBlock> TitleText;

protected:
    virtual void NativeOnActivated() override
    {
        Super::NativeOnActivated();
        if (TitleText)
        {
            TitleText->SetText(FText::FromString(TEXT("Page Activated")));
        }
    }

    virtual TOptional<FUIInputConfig> GetDesiredInputConfig() const override
    {
        return FUIInputConfig(ECommonInputMode::Menu, EMouseCaptureMode::NoCapture);
    }
};
```

```cpp
// MyUIManager.cpp
#include "MyUIManager.h"
#include "CommonActivatableWidgetStack.h"
#include "CommonUISubsystemBase.h"

// 使用方式（在 GameMode 或 HUD 中）：
// 1. 在 UMG 中放置一个 UCommonActivatableWidgetStack
// 2. 通过 C++ 推入/弹出页面

void PushPage(UCommonActivatableWidgetStack* Stack, TSubclassOf<UCommonActivatableWidget> PageClass)
{
    if (Stack)
    {
        UCommonActivatableWidget* Page = Stack->AddWidget<UCommonActivatableWidget>(
            PageClass,
            [](UCommonActivatableWidget& Widget) {
                // Widget 创建后的回调
            }
        );
        // Page 会自动调用 NativeOnActivated()
    }
}

void PopPage(UCommonActivatableWidgetStack* Stack)
{
    if (Stack)
    {
        UCommonActivatableWidget* TopWidget = Stack->GetActiveWidget();
        if (TopWidget)
        {
            TopWidget->DeactivateWidget();
            // Widget 会自动从 Stack 中移除
        }
    }
}
```

## 模块依赖

CommonUI 的 Build.cs 依赖较多，以下是**不常见**的依赖模块：

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 可见性系统使用 GameplayTag 查询来判断平台/输入特征 |
| `EnhancedInput` | 支持 Enhanced Input 系统的动作绑定和按键图标获取 |
| `MediaAssets` | 视频播放器使用 UMediaPlayer / UMediaSource / UMediaTexture |
| `MediaUtils` | 媒体工具函数 |
| `CommonInput` | CommonUI 自带的输入模块，处理输入类型检测和按键图标映射 |
| `GameplayTagsEditor` | 编辑器中 GameplayTag 的选择器支持 |

> 注意：CommonUI 还依赖标准的 Core/CoreUObject/Engine/Slate/UMG 等模块，此处省略。

## 维护状态

### 近期更新

```
- 8976f0a455e0 CommonUI: close game window, crash issues.
- 22b03661e886 CommonButtonBase: avoid calling focus blueprint events during object loading #rb yohann.dossantos
- 0c917b035a90 CommonUI: Warn on duplicate tabs, do not ensure.
```

- 最近的更新集中在**崩溃修复**和**边界条件处理**（关闭窗口时的崩溃、加载期间的焦点事件、重复 Tab 的警告）。
- 这些都是稳定性修复，表明插件功能已基本成熟，当前处于维护阶段。

### 维护评价

- **创建时间**：2021 年 4 月，约 4 年历史
- **状态**：仍标记为 `IsBetaVersion = true`，但已在多个 Epic 官方项目中使用（如 Lyra、Fortnite）
- **活跃度**：持续有更新，但以 bug 修复为主，新功能开发已放缓
- **已知限制**：
  - 默认未启用，需要手动在项目设置中开启
  - 替换了默认的 GameViewportClient，可能与自定义输入系统冲突
  - 部分 API 仍在演进中（如 `FUIActionBinding` 的 UserIndex 参数在 5.6 中有废弃标记）
  - `UCommonVisibilityWidgetBase` 已标记为 Deprecated，应使用 `UCommonHardwareVisibilityBorder` 替代
- **推荐程度**：**强烈推荐**用于需要跨平台/多输入方式支持的项目。虽然是 Beta 标签，但已经是 Epic 内部多个大型项目的基础 UI 框架，稳定性和设计质量都很高。Lyra 示例项目就是基于 CommonUI 构建的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CommonUI)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/common-ui-plugin-in-unreal-engine/)（UE 官方文档站）
- [Lyra 示例项目](https://github.com/EpicGames/UnrealEngine/tree/5.7/Templates/LyraGame)（CommonUI 的最佳实践参考）