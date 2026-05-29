# Common UI Plugin

> A repository for game independent UI elements.

| 属性 | 值 |
|---|---|
| 中文名 | 通用 UI 框架 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、输入配置） |
| 模块 | `CommonUI` (Runtime), `CommonUIEditor` (Editor), `CommonInput` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-05-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CommonUI) | |

## 用途

CommonUI 是 Epic 提供的**跨平台 UI 框架**，解决的核心问题是：在不同输入设备（键鼠、手柄、触屏）和不同平台之间，如何以统一的方式处理 UI 交互。

具体解决以下问题：

1. **输入设备自动切换检测**：自动识别当前使用的输入类型（键鼠/手柄/触屏），并通知 UI 层更新提示图标和交互模式
2. **统一的按钮提示图集**：为每个平台/手柄维护一套按键图标资产，自动根据当前输入类型显示正确的图标
3. **输入事件域管理**：通过 ActionDomain 系统控制 UI 层级间的事件传播和拦截，解决模态/非模态 UI 的输入焦点管理
4. **输入方法抖动防护**：防止用户在键鼠和手柄之间快速切换导致的 UI 状态混乱
5. **游戏手柄类型自动检测**：自动识别 Xbox/PS/Switch 等不同手柄，显示对应的按键图标

该插件**需要手动启用**（`EnabledByDefault: false`），建议配合 EnhancedInput 使用。

## 模块说明

该插件包含三个模块：

| 模块 | 类型 | 说明 |
|---|---|---|
| **CommonInput** | Runtime | 输入管理层：输入类型检测、子系统、输入域、按键图标映射 |
| **CommonUI** | Runtime | UI 组件层：可激活 Widget、通用按钮、ListView、拖拽、切换控件等 |
| **CommonUIEditor** | Editor | 编辑器扩展：资产类型定义、自定义编辑器工具 |

## 使用场景

- 你正在做一款需要同时支持键鼠、手柄、触屏的跨平台游戏 → 用 CommonUI 统一输入管理
- 你需要根据不同手柄（Xbox/PS/Switch）显示正确的按键图标 → 用 CommonInput 的控制器数据系统
- 你的 UI 需要处理模态对话框、暂停菜单等复杂的输入焦点问题 → 用 CommonUI 的 ActivatableWidget + ActionDomain
- 你想避免玩家快速切换输入设备导致 UI 图标闪烁 → 用 CommonInput 的 Thrashing 防护
- 你需要一个标准化的"通用按钮"组件，能自动响应不同输入方式 → 用 CommonUI 的 CommonButtonBase

---

# CommonInput 模块

CommonInput 是 CommonUI 的输入管理核心，负责输入设备检测、输入类型切换、按键图标映射等底层功能。

## 蓝图用法

### 核心节点

以下节点来自 `UCommonInputSubsystem`：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` | 获取当前本地玩家的 CommonInput 子系统实例 | `UCommonInputSubsystem` |
| `GetCurrentInputType` | 获取当前激活的输入类型（键鼠/手柄/触屏） | `UCommonInputSubsystem` |
| `GetDefaultInputType` | 获取当前平台的默认输入类型 | `UCommonInputSubsystem` |
| `SetCurrentInputType` | 手动设置当前输入类型 | `UCommonInputSubsystem` |
| `IsInputMethodActive` | 查询指定输入方法是否处于激活状态 | `UCommonInputSubsystem` |
| `IsUsingPointerInput` | 当前是否使用指针类输入（鼠标/触屏） | `UCommonInputSubsystem` |
| `GetCurrentGamepadName` | 获取当前识别的手柄名称（如 XboxGeneric、PS5） | `UCommonInputSubsystem` |
| `SetGamepadInputType` | 手动设置手柄类型 | `UCommonInputSubsystem` |
| `ShouldShowInputKeys` | 是否应显示输入按键提示（录制视频时可能需要隐藏） | `UCommonInputSubsystem` |
| `SetInputTypeFilter` | 按原因过滤/屏蔽某种输入类型 | `UCommonInputSubsystem` |
| `HadAnyChangeOfInputMethodInTheLastThrashingWindow` | 最近抖动窗口内是否发生过输入方法切换 | `UCommonInputSubsystem` |

### 使用示例（蓝图描述）

**获取当前输入类型并显示对应 UI**：
1. 从任意 LocalPlayer 对象调用 `CommonInput Subsystem` 节点获取子系统
2. 调用 `GetCurrentInputType` 返回 `ECommonInputType` 枚举
3. 通过 Switch 节点分支，为 Gamepad 显示手柄按键提示，为 MouseAndKeyboard 显示键位提示
4. 监听 `OnInputMethodChanged` 事件（BlueprintAssignable），实时响应输入切换

**锁定输入类型（防止误切换）**：
1. 调用 `SetInputTypeFilter`，传入 `InputType=Gamepad`、`Reason="UIFocusLock"`、`Filter=true` 屏蔽手柄输入
2. 操作完成后再次调用，`Filter=false` 解除屏蔽

---

## C++ 用法

### 头文件引入

```cpp
#include "CommonInputSubsystem.h"
#include "CommonInputBaseTypes.h"
#include "CommonInputSettings.h"
#include "ICommonInputModule.h"
```

### 基本用法

获取子系统并查询当前输入类型：

```cpp
// 获取 CommonInput 子系统
UCommonInputSubsystem* InputSubsystem = UCommonInputSubsystem::Get(GetLocalPlayer());
if (InputSubsystem)
{
    // 查询当前输入类型
    ECommonInputType CurrentType = InputSubsystem->GetCurrentInputType();
    
    switch (CurrentType)
    {
    case ECommonInputType::MouseAndKeyboard:
        // 显示键鼠提示
        break;
    case ECommonInputType::Gamepad:
        // 显示手柄提示
        break;
    case ECommonInputType::Touch:
        // 显示触屏提示
        break;
    }
    
    // 监听输入类型变化
    InputSubsystem->OnInputMethodChangedNative.AddUObject(this, &UMyClass::OnInputMethodChanged);
}
```

### 进阶用法

使用输入锁和过滤机制：

```cpp
void UMyUIScreen::OnActivate()
{
    UCommonInputSubsystem* InputSubsystem = UCommonInputSubsystem::Get(GetLocalPlayer());
    if (InputSubsystem)
    {
        // 锁定为游戏输入模式，防止 UI 层干扰
        InputSubsystem->AddOrRemoveInputTypeLock(FName("PauseMenu"), ECommonInputType::Gamepad, true);
        
        // 设置手柄类型（如果自动检测不可靠）
        InputSubsystem->SetGamepadInputType(FName("XboxOne"));
    }
}

void UMyUIScreen::OnDeactivate()
{
    UCommonInputSubsystem* InputSubsystem = UCommonInputSubsystem::Get(GetLocalPlayer());
    if (InputSubsystem)
    {
        // 解除输入锁
        InputSubsystem->AddOrRemoveInputTypeLock(FName("PauseMenu"), ECommonInputType::Gamepad, false);
    }
}
```

获取按键图标：

```cpp
// 通过平台设置获取手柄按键图标
UCommonInputPlatformSettings* PlatformSettings = UCommonInputPlatformSettings::Get();
if (PlatformSettings)
{
    FSlateBrush KeyBrush;
    FName GamepadName = InputSubsystem->GetCurrentGamepadName();
    
    if (PlatformSettings->TryGetInputBrush(KeyBrush, EKeys::Gamepad_FaceButton_Bottom, 
                                            ECommonInputType::Gamepad, GamepadName))
    {
        // KeyBrush 现在包含 Xbox 的 A 键或 PS 的 X 键的图标
        MyButton->SetBrush(KeyBrush);
    }
}
```

使用 ActionDomain 控制输入事件传播：

```cpp
// 创建 ActionDomain 表用于管理多个 UI 层的输入事件传播
UCommonInputActionDomainTable* DomainTable = InputSubsystem->GetActionDomainTable();
if (DomainTable)
{
    for (UCommonInputActionDomain* Domain : DomainTable->ActionDomains)
    {
        ECommonInputEventFlowBehavior Behavior = Domain->Behavior;
        ECommonInputEventFlowBehavior InnerBehavior = Domain->InnerBehavior;
        // 根据域行为决定输入事件如何在 UI 层之间传播
    }
}
```

---

## Demo 示例

一个最小的输入类型检测与响应示例：

```cpp
// MyInputWidget.h
#pragma once
#include "CommonActivatableWidget.h"
#include "MyInputWidget.generated.h"

UCLASS()
class UMyInputWidget : public UCommonActivatableWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;
    virtual void NativeDestruct() override;

protected:
    UFUNCTION()
    void OnInputMethodChanged(ECommonInputType NewInputType);
    
    void UpdateInputHints(ECommonInputType InputType);
};
```

```cpp
// MyInputWidget.cpp
#include "MyInputWidget.h"
#include "CommonInputSubsystem.h"

void UMyInputWidget::NativeConstruct()
{
    Super::NativeConstruct();
    
    UCommonInputSubsystem* InputSubsystem = UCommonInputSubsystem::Get(GetOwningLocalPlayer());
    if (InputSubsystem)
    {
        // 监听输入类型变化
        InputSubsystem->OnInputMethodChangedNative.AddUObject(
            this, &UMyInputWidget::OnInputMethodChanged);
        
        // 初始化时立即更新一次
        UpdateInputHints(InputSubsystem->GetCurrentInputType());
    }
}

void UMyInputWidget::NativeDestruct()
{
    UCommonInputSubsystem* InputSubsystem = UCommonInputSubsystem::Get(GetOwningLocalPlayer());
    if (InputSubsystem)
    {
        InputSubsystem->OnInputMethodChangedNative.RemoveAll(this);
    }
    
    Super::NativeDestruct();
}

void UMyInputWidget::OnInputMethodChanged(ECommonInputType NewInputType)
{
    UpdateInputHints(NewInputType);
}

void UMyInputWidget::UpdateInputHints(ECommonInputType InputType)
{
    // 根据输入类型更新 UI 提示图标
    switch (InputType)
    {
    case ECommonInputType::MouseAndKeyboard:
        UE_LOG(LogTemp, Log, TEXT("Switched to Mouse & Keyboard"));
        break;
    case ECommonInputType::Gamepad:
        UE_LOG(LogTemp, Log, TEXT("Switched to Gamepad: %s"), 
            *UCommonInputSubsystem::Get(GetOwningLocalPlayer())->GetCurrentGamepadName().ToString());
        break;
    case ECommonInputType::Touch:
        UE_LOG(LogTemp, Log, TEXT("Switched to Touch"));
        break;
    }
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 增强输入系统集成（可选，通过设置启用） |
| `GameplayTags` | 输入动作标签系统 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ea0fcb96` | [UMG/Slate] Proximate Entry Navigation - ScrollIntoView Local Space & Intra-Entry List Interior Guar | 修复 UMG/Slate 中 Proximate 入口导航的滚动和列表内部保护 |
| 2026-05-26 | `356fcc56` | [Virtual Pointer] Ignore the synthetic mouse-move event that UCommonInputSubsystem::SetCursorPositio | 虚拟指针模式下忽略 SetCursorPosition 产生的合成鼠标移动事件 |
| 2026-05-25 | `a10370d0` | [Virtual Pointer] FCommonAnalogCursor::RefreshCursorVisibility: gate viewport cursor writes on actua | 虚拟指针模式下光标可见性刷新改为仅在实际活跃时才写入视口 |
| 2026-05-22 | `e3f56aa5` | [Virtual Pointer] In VP mode, clamp the cursor to the viewport only when gamepad is driving it; mous | 虚拟指针模式下光标仅在手柄驱动时钳制到视口范围内 |
| 2026-05-20 | `4bcb727a` | CommonListView, SCommonTileView - Repair non-proximate pathway to not mutate focus when there is no | 修复 ListView/TileView 非近邻路径下无实际焦点变化时的焦点变更问题 |

### 维护评价

**活跃维护中** ⭐⭐⭐⭐

- **创建时间**：2023年5月，从 Experimental 迁移到正式版
- **更新频率**：非常活跃，最近一周内有多次实质性更新（虚拟指针改进、导航修复等）
- **维护质量**：由 Epic Games 官方团队维护，持续优化输入处理和导航系统
- **注意事项**：
  - 插件默认不启用（`EnabledByDefault: false`），需要手动在项目设置中启用
  - 标记为实验性（IsBetaVersion 虽然为 false，但创建信息显示从 Experimental 迁出）
  - 源码规模大（154 个文件），集成到项目时需理解其 Widget 层级体系
- **推荐使用**：✅ 强烈推荐。这是 Epic 为 Fortnite 等大型跨平台项目打造的官方 UI 框架，对于需要支持多种输入方式的项目来说是最成熟的解决方案。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CommonUI)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CommonUI/Tests)