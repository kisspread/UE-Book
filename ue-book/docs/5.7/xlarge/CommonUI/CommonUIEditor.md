# Common UI Plugin

> A repository for game independent UI elements.

| 属性 | 值 |
|---|---|
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据表、材质模板） |
| 模块 | `CommonUI` (Runtime), `CommonUIEditor` (Editor), `CommonInput` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CommonUI) | |

---

## 用途

CommonUI 是 Epic Games 提供的**跨平台 UI 框架**，旨在解决游戏 UI 开发中的核心痛点：

1. **输入设备无关性**：自动处理键鼠、手柄、触屏等多种输入方式的 UI 交互切换，无需手动管理焦点和输入映射
2. **平台适配**：统一的输入图标系统（CommonInput 模块），根据当前输入设备自动切换显示的按键提示图标
3. **可复用 UI 组件库**：提供游戏无关的通用 UI 控件（按钮、列表、切换器等），避免每个项目重复造轮子
4. **Activatable Widget 生命周期管理**：通过 `UCommonActivatableWidget` 提供标准化的 Widget 激活/停用状态管理，简化菜单栈（Menu Stack）的实现

**为什么存在**：UE5 内置的 UMG/Slate 功能强大但缺乏游戏 UI 的高层抽象。CommonUI 填补了这个空白，特别是对于需要同时支持手柄和键鼠的跨平台游戏（如 Fortnite、Rocket League 等 Epic 自家游戏）。

---

## 使用场景

- 你在开发一款**跨平台游戏**（PC + 主机 + 移动端），需要 UI 自动适配不同输入设备 → 用 CommonUI
- 你需要实现**菜单栈系统**（主菜单 → 设置 → 音频设置，支持返回）→ 用 CommonUI 的 ActivatableWidget + ActionRouter
- 你希望**按键提示图标**根据当前输入设备自动切换（如 Xbox 手柄显示 A/B/X/Y，键鼠显示 Space/Click）→ 用 CommonInput
- 你有多个项目需要**共享 UI 组件库**→ 用 CommonUI 的通用控件
- 你只需要简单的单平台 UI，不需要手柄支持 → **不需要** CommonUI，直接用 UMG 即可

---

## 模块架构

本插件包含 3 个模块，形成分层架构：

```
┌─────────────────────────────────────────────┐
│              CommonUIEditor (Editor)         │  ← 编辑器工具、资产工厂
├─────────────────────────────────────────────┤
│              CommonUI (Runtime)              │  ← 核心 UI 控件、Widget 基类
├─────────────────────────────────────────────┤
│              CommonInput (Runtime)           │  ← 输入设备管理、按键图标映射
└─────────────────────────────────────────────┘
```

### CommonInput（Runtime）

底层输入抽象层，负责：
- 输入设备类型检测与切换（键鼠/手柄/触屏）
- 按键到图标的映射（InputAction → 图标纹理）
- 输入数据表管理（`UCommonInputActionDataBase`）

### CommonUI（Runtime）

核心 UI 框架，提供：
- `UCommonActivatableWidget`：可激活的 Widget 基类，支持生命周期管理
- `UCommonActivatableWidgetContainerBase`：Widget 容器（栈、队列等）
- `UCommonButtonBase`：通用按钮基类
- `UCommonListView`：增强型列表视图
- `UCommonTabListWidgetBase`：标签页系统
- `UCommonActionWidget`：输入动作提示 Widget
- `FCommonInputActionDataBase`：输入动作数据资产

### CommonUIEditor（Editor）

编辑器扩展，提供：
- 自定义资产类型注册（AssetTypeActions）
- `UCommonGenericInputActionDataTableFactory`：通用输入动作数据表工厂

---

## 蓝图用法

### 核心节点

#### Widget 生命周期管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActivateWidget` | 激活 Widget，触发 OnActivated 事件 | `UCommonActivatableWidget` |
| `DeactivateWidget` | 停用 Widget，触发 OnDeactivated 事件 | `UCommonActivatableWidget` |
| `IsActivated` | 查询 Widget 是否处于激活状态 | `UCommonActivatableWidget` |
| `SetBindVisibilities` | 设置 Widget 在不同输入模式下的可见性 | `UCommonActivatableWidget` |

#### Widget 容器（菜单栈）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddWidget` | 向容器添加 Widget | `UCommonActivatableWidgetContainerBase` |
| `RemoveWidget` | 从容器移除 Widget | `UCommonActivatableWidgetContainerBase` |
| `ClearWidgets` | 清空容器中所有 Widget | `UCommonActivatableWidgetContainerBase` |
| `GetActiveWidget` | 获取当前激活的 Widget | `UCommonActivatableWidgetContainerBase` |

#### 通用按钮

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetButtonText` | 设置按钮显示文本 | `UCommonButtonBase` |
| `SetIsEnabled` | 启用/禁用按钮 | `UCommonButtonBase` |
| `SetIsSelectable` | 设置按钮是否可选中 | `UCommonButtonBase` |
| `SetIsSelected` | 设置按钮选中状态 | `UCommonButtonBase` |

#### 输入动作提示

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetInputAction` | 设置要显示的输入动作 | `UCommonActionWidget` |
| `GetIcon` | 获取当前输入动作对应的图标纹理 | `UCommonActionWidget` |

### 使用示例（蓝图描述）

**创建菜单栈系统**：

1. 在你的 HUD Widget 中放置一个 `CommonActivatableWidgetStack`（或 `CommonActivatableWidgetQueue`）
2. 当需要打开设置菜单时，调用 `AddWidget`，传入设置菜单的 Widget 类
3. 设置菜单 Widget 继承自 `UCommonActivatableWidget`，在 `OnActivated` 中初始化内容
4. 用户按下返回键时，调用 `DeactivateWidget`，容器自动弹出栈顶 Widget
5. 通过 `OnTransitioning` 事件实现菜单切换动画

**自动输入图标切换**：

1. 创建 `UCommonInputActionDataBase` 资产，配置各平台的按键图标
2. 在 Widget 中放置 `UCommonActionWidget`
3. 调用 `SetInputAction` 绑定到对应的输入动作
4. 当玩家切换输入设备时，图标自动更新（无需手动处理）

---

## C++ 用法

### 头文件引入

```cpp
// CommonUI 核心
#include "CommonActivatableWidget.h"
#include "CommonButtonBase.h"
#include "CommonActivatableWidgetContainerBase.h"

// CommonInput
#include "CommonInputSubsystem.h"
#include "CommonInputActionDataBase.h"
```

### 基本用法：创建自定义 Activatable Widget

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
    UMyMenuWidget(const FObjectInitializer& ObjectInitializer);

protected:
    // Widget 激活时调用（类似 OnBeginPlay）
    virtual void NativeOnActivated() override;
    
    // Widget 停用时调用
    virtual void NativeOnDeactivated() override;
    
    // 返回此 Widget 的输入配置
    virtual TOptional<FUIInputConfig> GetDesiredInputConfig() const override;

private:
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonButtonBase> StartButton;

    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonButtonBase> SettingsButton;
};
```

```cpp
// MyMenuWidget.cpp
#include "MyMenuWidget.h"
#include "CommonInputSubsystem.h"

UMyMenuWidget::UMyMenuWidget(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

void UMyMenuWidget::NativeOnActivated()
{
    Super::NativeOnActivated();
    
    // 绑定按钮点击事件
    if (StartButton)
    {
        StartButton->OnClicked().AddUObject(this, &UMyMenuWidget::OnStartClicked);
    }
}

void UMyMenuWidget::NativeOnDeactivated()
{
    Super::NativeOnDeactivated();
    // 清理逻辑
}

TOptional<FUIInputConfig> UMyMenuWidget::GetDesiredInputConfig() const
{
    // 指定此 Widget 使用 Game + Menu 输入模式
    // 允许手柄导航和鼠标点击同时生效
    return FUIInputConfig(ECommonInputMode::Menu, EMouseCaptureMode::NoCapture);
}
```

### 进阶用法：管理菜单栈

```cpp
// MyHUD.h
#pragma once

#include "CommonActivatableWidgetContainerBase.h"
#include "MyHUD.generated.h"

UCLASS()
class UMyHUD : public UUserWidget
{
    GENERATED_BODY()

protected:
    // 在蓝图中绑定的 Widget Stack
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonActivatableWidgetStack> MenuStack;

public:
    void OpenMainMenu();
    void OpenSettings();
    void CloseCurrentMenu();
};
```

```cpp
// MyHUD.cpp
#include "MyHUD.h"
#include "MyMainMenuWidget.h"
#include "MySettingsWidget.h"

void UMyHUD::OpenMainMenu()
{
    // Push 主菜单到栈顶
    MenuStack->AddWidget<UMyMainMenuWidget>(
        UMyMainMenuWidget::StaticClass(),
        [](UMyMainMenuWidget& Widget)
        {
            // 可在此处设置 Widget 初始参数
        }
    );
}

void UMyHUD::OpenSettings()
{
    // 在主菜单之上 Push 设置菜单
    MenuStack->AddWidget<UMySettingsWidget>(UMySettingsWidget::StaticClass());
}

void UMyHUD::CloseCurrentMenu()
{
    // 弹出栈顶 Widget
    if (UCommonActivatableWidget* ActiveWidget = MenuStack->GetActiveWidget())
    {
        ActiveWidget->DeactivateWidget();
    }
}
```

---

## Demo 示例

### 最小可运行示例：带输入提示的主菜单

```cpp
// SimpleMainMenu.h
#pragma once

#include "CommonActivatableWidget.h"
#include "CommonActionWidget.h"
#include "CommonButtonBase.h"
#include "SimpleMainMenu.generated.h"

UCLASS()
class USimpleMainMenu : public UCommonActivatableWidget
{
    GENERATED_BODY()

public:
    USimpleMainMenu(const FObjectInitializer& ObjectInitializer);

protected:
    virtual void NativeOnActivated() override;
    virtual void NativeConstruct() override;
    virtual TOptional<FUIInputConfig> GetDesiredInputConfig() const override;

    UFUNCTION()
    void OnPlayClicked();

    UFUNCTION()
    void OnQuitClicked();

private:
    // BindWidget: 必须在蓝图中放置同名控件
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonButtonBase> PlayButton;

    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonButtonBase> QuitButton;

    // 显示"确认"动作的输入提示
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonActionWidget> ConfirmAction;

    // 显示"返回"动作的输入提示
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UCommonActionWidget> BackAction;
};
```

```cpp
// SimpleMainMenu.cpp
#include "SimpleMainMenu.h"
#include "Kismet/GameplayStatics.h"

USimpleMainMenu::USimpleMainMenu(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

void USimpleMainMenu::NativeConstruct()
{
    Super::NativeConstruct();

    // 设置输入提示对应的动作
    if (ConfirmAction)
    {
        // CommonUI_Accept 是插件预定义的 GameplayTag
        ConfirmAction->SetInputAction(FDataTableRowHandle());
    }
    if (BackAction)
    {
        BackAction->SetInputAction(FDataTableRowHandle());
    }
}

void USimpleMainMenu::NativeOnActivated()
{
    Super::NativeOnActivated();

    // 绑定按钮事件
    if (PlayButton)
    {
        PlayButton->OnClicked().AddUObject(this, &USimpleMainMenu::OnPlayClicked);
    }
    if (QuitButton)
    {
        QuitButton->OnClicked().AddUObject(this, &USimpleMainMenu::OnQuitClicked);
    }

    // 默认选中第一个按钮（手柄支持）
    if (PlayButton)
    {
        PlayButton->SetFocus();
    }
}

TOptional<FUIInputConfig> USimpleMainMenu::GetDesiredInputConfig() const
{
    // Menu 模式：手柄可导航，鼠标可点击，不捕获鼠标
    return FUIInputConfig(ECommonInputMode::Menu, EMouseCaptureMode::NoCapture);
}

void USimpleMainMenu::OnPlayClicked()
{
    UGameplayStatics::OpenLevel(this, FName("GameLevel"));
}

void USimpleMainMenu::OnQuitClicked()
{
    UKismetSystemLibrary::QuitGame(
        this, 
        GetOwningPlayer(), 
        EQuitPreference::Quit, 
        false
    );
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 增强输入系统集成，用于输入动作映射 |
| `GameplayTags` | 使用 GameplayTag 标识输入动作和 UI 状态 |
| `GameplayTagsEditor` | 编辑器中 GameplayTag 的选择器支持 |
| `Slate` / `SlateCore` | 底层 UI 框架 |
| `UMG` | Widget 框架基础 |

> **注意**：CommonUI 通过 `.uplugin` 的 Plugins 字段声明了对 `EnhancedInput` 和 `GameplayTagsEditor` 的硬依赖。你的项目必须启用这两个插件。

---

## 维护状态

### 近期更新

```
- 66e9bb39ff7e Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base
- 48c2357147ba Remove unnecessary private include path to CommonUI
- 91c57d395e6b Removed redundant module includes.
```

以上三次提交均为**代码清理/编译修复**，不涉及功能更新。

### 维护评价

- **创建时间**：2021 年 4 月，约 4 年历史
- **实验性状态**：`IsBetaVersion=true`，`EnabledByDefault=false`，仍处于 Beta 阶段
- **更新频率**：近期更新以编译兼容性修复为主，无实质性功能迭代
- **实际使用**：尽管标记为 Beta，Epic 自家游戏（Fortnite 等）已在生产环境使用
- **已知限制**：
  - Beta 状态意味着 API 可能在版本间发生变化
  - 文档较少，主要依赖源码和示例项目学习
  - 与 EnhancedInput 强耦合，不支持旧版输入系统

**推荐使用**：✅ **推荐**。虽然标记为 Beta，但经过 Epic 大型项目的实战验证，是 UE5 跨平台游戏 UI 的事实标准方案。建议在新项目中采用，但需注意 API 变更风险。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CommonUI)
- [Lyra 示例项目](https://github.com/EpicGames/UnrealEngine/tree/5.7/Templates/LyraGame)（CommonUI 的官方最佳实践参考）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CommonUI/Tests)