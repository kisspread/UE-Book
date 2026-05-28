# Common UI Plugin

> A repository for game independent UI elements.

| 属性 | 值 |
|---|---|
| 中文名 | 通用 UI 框架 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、样式模板） |
| 模块 | `CommonUI` (Runtime), `CommonUIEditor` (Editor), `CommonInput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-05-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CommonUI) | |

## 用途

CommonUI 是 UE5 官方提供的**游戏无关的 UI 框架**，解决的核心问题：

1. **跨平台输入适配**：自动处理键鼠、手柄、触屏等不同输入方式，在 UI 中显示对应的平台图标（如 Xbox A 键 vs PS × 键）
2. **统一的 UI 交互模型**：提供 `ActivatableWidget` 模式，支持栈/队列式的页面导航、焦点恢复、返回（Back）操作
3. **输入路由系统**：通过 `ActionRouter` 管理 UI 输入优先级，确保激活的 UI 面板能正确接收和分发输入
4. **按钮/文本/列表等通用组件**：提供带样式系统、动画切换器、加载守卫等生产级 UI 组件

> ⚠️ **需要手动启用**：`EnabledByDefault=false`，需在项目的 `.uproject` 或编辑器插件设置中手动启用。

## 使用场景

- 你在做一个**多平台游戏**，需要 UI 同时支持手柄和键鼠 → 用 CommonUI 管理输入映射和图标显示
- 你需要一个**页面栈/导航系统**（如主菜单 → 设置 → 音频），支持返回操作 → 用 `UCommonActivatableWidgetStack`
- 你想要**统一的按钮样式系统**，在不同状态下（正常/悬停/按下/选中/禁用）自动切换外观 → 用 `UCommonButtonBase` + `UCommonButtonStyle`
- 你需要异步加载内容时**显示加载指示器** → 用 `UCommonLoadGuard`
- 你需要**可滚动的文本**或**数字动画显示** → 用 `UCommonTextBlock` 或 `UCommonNumericTextBlock`
- 你需要**标签页切换**（如商城的角色/武器/皮肤页签） → 用 `UCommonTabListWidgetBase`

## 蓝图用法

### 核心节点

#### 按钮系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIsSelected` | 手动设置按钮选中状态，可选择是否播放反馈 | `UCommonButtonBase` |
| `SetIsLocked` | 锁定按钮（可聚焦/悬停但不触发点击事件） | `UCommonButtonBase` |
| `DisableButtonWithReason` | 禁用按钮并附带禁用原因文本 | `UCommonButtonBase` |
| `SetStyle` | 动态设置按钮样式（重建内部样式） | `UCommonButtonBase` |
| `SetTriggeringInputAction` | 设置按钮关联的输入动作（DataTable） | `UCommonButtonBase` |
| `SetTriggeringEnhancedInputAction` | 设置按钮关联的增强输入动作 | `UCommonButtonBase` |
| `SetIsToggleable` | 设为可切换模式（点击已选中时取消选中） | `UCommonButtonBase` |
| `SetRequiresHold` | 强制按钮使用长按行为 | `UCommonButtonBase` |
| `SetPressedSoundOverride` | 覆盖按下音效 | `UCommonButtonBase` |
| `SetClickedSoundOverride` | 覆盖点击音效 | `UCommonButtonBase` |
| `SetHoveredSoundOverride` | 覆盖悬停音效 | `UCommonButtonBase` |

#### 可激活控件系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActivateWidget` | 激活控件，触发 OnActivated 事件 | `UCommonActivatableWidget` |
| `DeactivateWidget` | 停用控件，触发 OnDeactivated 事件 | `UCommonActivatableWidget` |
| `IsActivated` | 查询控件是否处于激活状态 | `UCommonActivatableWidget` |
| `GetDesiredFocusTarget` | 获取激活时应获得焦点的目标控件 | `UCommonActivatableWidget` |
| `BindVisibilityToActivation` | 将自身可见性绑定到另一控件的激活状态 | `UCommonActivatableWidget` |
| `RequestRefreshFocus` | 请求刷新焦点（仅当自身是最叶节点时生效） | `UCommonActivatableWidget` |
| `ClearFocusRestorationTarget` | 清除缓存的焦点恢复目标 | `UCommonActivatableWidget` |

#### 容器系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Push Widget` (BP_AddWidget) | 向栈/队列容器添加并显示一个可激活控件 | `UCommonActivatableWidgetContainerBase` |
| `GetActiveWidget` | 获取容器中当前显示的控件 | `UCommonActivatableWidgetContainerBase` |
| `RemoveWidget` | 从容器移除指定控件 | `UCommonActivatableWidgetContainerBase` |
| `ClearWidgets` | 清空容器中的所有控件 | `UCommonActivatableWidgetContainerBase` |
| `SetTransitionDuration` | 设置控件切换的过渡动画时长 | `UCommonActivatableWidgetContainerBase` |

#### 标签页系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterTab` | 注册一个新标签页（TabID + 按钮类型 + 内容控件） | `UCommonTabListWidgetBase` |
| `SelectTabByID` | 通过 TabID 选择指定标签页 | `UCommonTabListWidgetBase` |
| `GetActiveTab` | 获取当前活跃的标签页 ID | `UCommonTabListWidgetBase` |
| `SetLinkedSwitcher` | 关联动画切换器，标签切换时自动切换内容 | `UCommonTabListWidgetBase` |
| `SetTabEnabled` | 启用/禁用指定标签页 | `UCommonTabListWidgetBase` |
| `RemoveTab` | 移除指定标签页 | `UCommonTabListWidgetBase` |

#### 按钮组系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SelectNextButton` | 选择组内下一个按钮（可循环） | `UCommonButtonGroupBase` |
| `SelectPreviousButton` | 选择组内上一个按钮（可循环） | `UCommonButtonGroupBase` |
| `SelectButtonAtIndex` | 按索引选择组内按钮 | `UCommonButtonGroupBase` |
| `DeselectAll` | 取消组内所有按钮选中 | `UCommonButtonGroupBase` |
| `SetSelectionRequired` | 设为必须始终有一个按钮被选中 | `UCommonButtonGroupBase` |

#### 输入动作与图标

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetInputAction` | 设置动作控件显示的输入动作（DataTable） | `UCommonActionWidget` |
| `SetEnhancedInputAction` | 设置动作控件显示的增强输入动作 | `UCommonActionWidget` |
| `GetIcon` | 获取当前平台对应的输入图标 | `UCommonActionWidget` |
| `GetDisplayText` | 获取当前动作的显示文本 | `UCommonActionWidget` |
| `RegisterUIAction` | 注册 UI 输入动作（增强输入） | `UCommonUserWidget` |

#### 加载与延迟

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GuardAndLoadAsset` | 在资产加载期间显示加载状态 | `UCommonLoadGuard` |
| `SetIsLoading` | 手动设置加载状态 | `UCommonLoadGuard` |
| `SetLazyContent` | 异步加载并显示 Widget | `UCommonLazyWidget` |
| `SetBrushFromLazyTexture` | 异步加载纹理并设置为图片画刷 | `UCommonLazyImage` |

#### 文本与数值

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStyle` | 设置文本样式类 | `UCommonTextBlock` |
| `SetWrapTextWidth` | 设置自动换行宽度 | `UCommonTextBlock` |
| `InterpolateToValue` | 将数值文本从当前值平滑插值到目标值 | `UCommonNumericTextBlock` |
| `SetCurrentValue` | 直接设置当前数值（取消插值） | `UCommonNumericTextBlock` |

### 使用示例（蓝图描述）

**创建一个带有返回功能的菜单栈**：
1. 在 Widget Blueprint 中放置 `UCommonActivatableWidgetStack`
2. 创建多个继承自 `UCommonActivatableWidget` 的菜单页面 Widget
3. 设置各页面的 `bIsBackHandler = true`
4. 在主菜单 Widget 中，调用 `Push Widget` 将设置页面添加到栈中
5. 用户按下返回键时，栈顶页面自动弹出并显示下层页面

**创建标签页导航**：
1. 放置 `UCommonTabListWidgetBase` 和 `UCommonAnimatedSwitcher`
2. 调用 `SetLinkedSwitcher` 将标签列表关联到切换器
3. 为每个标签调用 `RegisterTab`，传入 TabID、按钮类、内容 Widget
4. 调用 `SelectTabByID` 切换到指定标签，切换器自动播放过渡动画

## C++ 用法

### 头文件引入

```cpp
#include "CommonActivatableWidget.h"
#include "CommonButtonBase.h"
#include "CommonTabListWidgetBase.h"
#include "CommonButtonGroupBase.h"
#include "CommonActionWidget.h"
#include "CommonLoadGuard.h"
#include "CommonTextBlock.h"
#include "CommonNumericTextBlock.h"
#include "CommonActivatableWidgetContainer.h"
#include "CommonListView.h"
#include "CommonLazyImage.h"
#include "CommonLazyWidget.h"
#include "CommonWidgetCarousel.h"
#include "CommonUILibrary.h"
#include "UITag.h"
```

### 基本用法

**创建一个可激活的 UI 面板**：

```cpp
// MySettingsPanel.h
#pragma once
#include "CommonActivatableWidget.h"
#include "MySettingsPanel.generated.h"

UCLASS()
class UMySettingsPanel : public UCommonActivatableWidget
{
    GENERATED_BODY()

protected:
    // 当控件激活时调用
    virtual void NativeOnActivated() override
    {
        Super::NativeOnActivated();
        // 自定义激活逻辑，如播放动画
    }

    // 当控件停用时调用
    virtual void NativeOnDeactivated() override
    {
        Super::NativeOnDeactivated();
        // 自定义停用逻辑
    }

    // 提供激活时应获得焦点的目标控件
    virtual UWidget* NativeGetDesiredFocusTarget() const override
    {
        // 返回你希望聚焦的按钮/输入框
        return FirstButton;
    }

    // 可选：定义输入配置（激活时自动应用）
    virtual TOptional<FUIInputConfig> GetDesiredInputConfig() const override
    {
        // Menu 模式：仅 UI 输入，不捕获鼠标
        return FUIInputConfig(ECommonInputMode::Menu, EMouseCaptureMode::NoCapture);
    }

protected:
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonButtonBase> FirstButton;
};
```

### 进阶用法

**创建带样式系统的自定义按钮**：

```cpp
// MyCustomButton.h
#pragma once
#include "CommonButtonBase.h"
#include "MyCustomButton.generated.h"

UCLASS(BlueprintType)
class UMyCustomButton : public UCommonButtonBase
{
    GENERATED_BODY()

protected:
    virtual void NativeConstruct() override
    {
        Super::NativeConstruct();
        
        // 设置按钮样式
        SetStyle(MyButtonStyleClass);
        
        // 绑定增强输入动作
        SetTriggeringEnhancedInputAction(ConfirmAction);
        
        // 设置为可选中
        SetIsSelectable(true);
        
        // 监听选中状态变化
        OnIsSelectedChanged().AddUObject(this, &UMyCustomButton::HandleSelectionChanged);
    }

    UFUNCTION()
    void HandleSelectionChanged(UCommonButtonBase* Button, bool bSelected)
    {
        // 根据选中状态更新视觉效果
    }

protected:
    UPROPERTY(EditAnywhere, Category = "Style")
    TSubclassOf<UCommonButtonStyle> MyButtonStyleClass;

    UPROPERTY(EditAnywhere, Category = "Input")
    TObjectPtr<UInputAction> ConfirmAction;
};
```

**在运行时向容器添加页面**：

```cpp
// 假设 WidgetStack 是一个 UCommonActivatableWidgetStack*
UCommonActivatableWidget* NewPanel = WidgetStack->AddWidget<UMySettingsPanel>(
    UMySettingsPanel::StaticClass(),
    [](UMySettingsPanel& Panel) {
        // 初始化回调：在添加到容器后、激活前调用
        Panel.SetSomeData(MyData);
    }
);
// 返回的 NewPanel 会自动激活并显示
```

**注册 UI 输入动作**：

```cpp
// 在 UCommonUserWidget 子类中
void UMyWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    
    // 方式1：通过 FUIActionTag 注册（推荐，使用项目设置中的映射）
    FBindUIActionArgs Args(FGlobalUITags::Get().UIAction_Cancel, true, 
        FSimpleDelegate::CreateUObject(this, &UMyWidget::HandleCancel));
    Args.InputMode = ECommonInputMode::Menu;
    Args.bConsumeInput = true;
    RegisterUIActionBinding(Args);
    
    // 方式2：通过增强输入注册
    RegisterUIAction(MyInputAction, true);
    
    // 方式3：从输入映射上下文批量注册
    RegisterUIActionsFromMappingContext(MyMappingContext, true);
}
```

## Demo 示例

### 可激活的设置面板

```cpp
// MySettingsPanel.h
#pragma once
#include "CommonActivatableWidget.h"
#include "CommonButtonBase.h"
#include "CommonTextBlock.h"
#include "MySettingsPanel.generated.h"

UCLASS()
class UMySettingsPanel : public UCommonActivatableWidget
{
    GENERATED_BODY()

protected:
    virtual void NativeOnInitialized() override;

    virtual void NativeOnActivated() override;
    virtual void NativeOnDeactivated() override;
    virtual UWidget* NativeGetDesiredFocusTarget() const override;

    virtual TOptional<FUIInputConfig> GetDesiredInputConfig() const override;

    UFUNCTION()
    void HandleApplyClicked();

    UFUNCTION()
    void HandleBackAction();

protected:
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonTextBlock> TitleText;

    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonButtonBase> ApplyButton;

    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonButtonBase> CancelButton;
};
```

```cpp
// MySettingsPanel.cpp
#include "MySettingsPanel.h"
#include "CommonUILibrary.h"
#include "UITag.h"

void UMySettingsPanel::NativeOnInitialized()
{
    Super::NativeOnInitialized();

    // 设置面板标题
    TitleText->SetText(FText::FromString(TEXT("Settings")));

    // 绑定按钮事件
    ApplyButton->OnClicked().AddUObject(this, &UMySettingsPanel::HandleApplyClicked);
    CancelButton->OnClicked().AddUObject(this, &UMySettingsPanel::HandleBackAction);

    // 注册取消输入动作（返回键）
    FBindUIActionArgs CancelArgs(
        FGlobalUITags::Get().UIAction_Cancel,
        true,
        FSimpleDelegate::CreateUObject(this, &UMySettingsPanel::HandleBackAction));
    CancelArgs.InputMode = ECommonInputMode::Menu;
    RegisterUIActionBinding(CancelArgs);
}

void UMySettingsPanel::NativeOnActivated()
{
    Super::NativeOnActivated();
    // 播放入场动画、刷新数据等
}

void UMySettingsPanel::NativeOnDeactivated()
{
    Super::NativeOnDeactivated();
    // 清理临时状态
}

UWidget* UMySettingsPanel::NativeGetDesiredFocusTarget() const
{
    return ApplyButton;
}

TOptional<FUIInputConfig> UMySettingsPanel::GetDesiredInputConfig() const
{
    return FUIInputConfig(ECommonInputMode::Menu, EMouseCaptureMode::NoCapture);
}

void UMySettingsPanel::HandleApplyClicked()
{
    // 保存设置...
    
    // 自动停用（如果 bIsBackHandler=true，DeactivateWidget 会从栈中弹出）
    DeactivateWidget();
}

void UMySettingsPanel::HandleBackAction()
{
    DeactivateWidget();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 增强输入系统集成，支持 InputAction/InputMappingContext 绑定 |
| `GameplayTags` | UITag/UIActionTag 标签系统（底层依赖，通过 GameplayTagsEditor 间接引用） |
| `CommonInput` | CommonUI 自带的输入子模块，管理输入方式切换和平台图标 |

无特殊依赖（仅标准 Core/Engine/Slate/UMG 等 + 上述模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ea0fcb96` | [UMG/Slate] Proximate Entry Navigation - ScrollIntoView Local Space & Intra-Entry List Interior Guar | 修复 TileView 近似焦点导航的局部空间滚动和列表内部导航 |
| 2026-05-26 | `356fcc56` | [Virtual Pointer] Ignore the synthetic mouse-move event that UCommonInputSubsystem::SetCursorPositio | 虚拟指针：忽略设置光标位置后的合成鼠标移动事件 |
| 2026-05-25 | `a10370d0` | [Virtual Pointer] FCommonAnalogCursor::RefreshCursorVisibility: gate viewport cursor writes on actua | 虚拟指针：仅在实际变更时更新视口光标，避免冗余写入 |
| 2026-05-22 | `e3f56aa5` | [Virtual Pointer] In VP mode, clamp the cursor to the viewport only when gamepad is driving it; mous | 虚拟指针：仅手柄驱动时限制光标到视口，鼠标输入不受限 |
| 2026-05-20 | `4bcb727a` | CommonListView, SCommonTileView - Repair non-proximate pathway to not mutate focus when there is no | 修复 ListView/TileView 在无选中项时的焦点处理路径 |

### 维护评价

- **活跃维护**：2026年5月仍有密集的功能更新，主要集中在虚拟指针（Virtual Pointer）和近似焦点导航（Proximate Entry Navigation）的完善
- **持续进化**：从 2023 年移出实验阶段以来持续迭代，代码量从最初的模块扩展到 154 个源文件
- **官方支持**：由 Epic Games 维护，是 Lyra Starter Game 的核心 UI 框架
- **已知限制**：`EnabledByDefault=false`，需要手动启用；部分旧 API（如 `ICommonActionHandlerInterface`）标记为 deprecated 预计在 5.3 后移除
- **推荐使用**：✅ 强烈推荐。它是 UE5 生态中最完整的跨平台 UI 框架，适合需要手柄/触屏支持的项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CommonUI)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/common-ui-plugin-for-advanced-user-interfaces-in-unreal-engine/)