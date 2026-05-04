# Common UI Plugin

> A repository for game independent UI elements.

| 属性 | 值 |
|---|---|
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产、输入配置、平台设置） |
| 模块 | `CommonInput` (Runtime), `CommonUI` (Runtime), `CommonUIEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CommonUI) | |

## 用途

CommonUI 是一个**跨平台 UI 框架与输入管理系统**，解决以下核心问题：

1. **输入类型自动检测**：自动识别玩家当前使用的是键鼠、手柄还是触屏，并在切换时通知 UI 系统更新提示图标和交互方式。
2. **统一的输入处理域（Action Domain）**：为复杂的 UI 层级（菜单叠加、弹窗、HUD）提供可控的输入事件传播机制，避免多个 UI 面板同时响应输入。
3. **平台无关的 UI 组件库**：提供一套不绑定具体游戏的通用 UI 控件（按钮、列表、切换器等），支持根据当前输入设备自动切换显示的按键图标。
4. **输入防抖保护**：防止玩家在短时间内频繁切换输入设备（如误触手柄摇杆）导致 UI 图标疯狂闪烁。

该插件默认不启用（`EnabledByDefault: false`），且标记为 Beta，说明 Epic 仍在迭代中，但已被《Fortnite》等大型项目验证。

## 使用场景

- 你在做一款**支持手柄和键鼠双端操作**的 PC/主机游戏 → 用 CommonInput 自动检测输入类型并切换 UI 提示
- 你的游戏有**多层叠加 UI**（主菜单 → 设置 → 确认弹窗）需要精确控制输入事件传播 → 用 Action Domain 管理事件流
- 你需要一套**跨平台通用 UI 组件**，避免为每个平台重写菜单 → 用 CommonUI 的 Widget 集合
- 你的游戏需要**根据输入设备动态切换按键图标**（如 Xbox 手柄显示 A/B 键，PS 手柄显示 ×/○） → 用 CommonInput 的 Key Brush 配置系统
- 你使用了 **Enhanced Input** 系统，需要 UI 层面的输入集成 → CommonUI 原生支持 Enhanced Input

## 子模块概览

| 模块 | 类型 | 职责 |
|---|---|---|
| [CommonInput](CommonInput.md) | Runtime | 输入类型检测、输入模式管理、Action Domain、输入防抖 |
| CommonUI | Runtime | 通用 UI Widget 库（按钮、列表、切换器、Activatable Widget 等） |
| CommonUIEditor | Editor | 编辑器工具、自定义资产编辑器、属性面板扩展 |

> 本文档当前仅包含 **CommonInput** 子模块的详细文档。CommonUI 和 CommonUIEditor 待补充。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 集成 UE5 新输入系统，支持 InputAction 映射 |
| `GameplayTags` | Action Domain 和 UI 组件使用 GameplayTag 进行标识和过滤 |

## 维护状态

### 近期更新

```
- b8d4c3667f7d Fix common input settings regression (no longer editable in the project settings): - Platfom inialization is necessary also for the CDO, reactivated it. - Reenable defered loading on editor only, and keep sync loading in CreateSettingsObjectForPlatform otherwise.
- 0d2723e5a1f5 -Fix synchronous load done at a bad time because UCommonInputPlatformSettings was expecting its PostLoad method to be called to force the load, but it was never happening (take 2). Now PostLoad will be called for all UPlatformSettings. -Prevent some common ui CDOs to try to load the settings too early, which could fail if occurring to soon, especially now that the UCommonInputPlatformSettings are no longer lazy loaded.
- 055d68c017c6 Extract a new public method called "HadAnyChangeOfInputMethodInTheLastThrashingWindow" from CommonInputSubsystem to expose it to public API.
```

近期更新集中在**设置加载时序修复**和**API 完善**，说明 Epic 在持续维护并修复生产环境问题。

### 维护评价

- **活跃维护**：作为 Fortnite 等旗舰项目的核心 UI 框架，Epic 持续投入维护
- **Beta 状态**：`IsBetaVersion=true`，API 可能在未来版本发生变化
- **默认不启用**：需要手动在项目设置中启用，说明 Epic 认为它还不适合所有项目
- **推荐使用**：如果你的项目需要跨平台 UI 支持，这是 Epic 官方推荐的方案；但需注意 API 可能变动

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CommonUI)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/common-ui-plugin-in-unreal-engine/)（UE 官方文档站）

---

# CommonInput 子模块

> CommonInput 是 CommonUI 插件的输入管理核心，负责跨平台输入类型检测、输入模式切换、Action Domain 事件流控制和输入防抖保护。

## 用途

CommonInput 解决的核心问题是：**在支持多种输入方式的游戏中，如何让 UI 自动感知玩家当前使用的输入设备，并据此调整交互行为和视觉提示。**

具体职责：
1. **输入类型检测**：通过 `FCommonInputPreprocessor` 在 Slate 层面拦截所有输入事件，判断当前是键鼠、手柄还是触屏
2. **输入模式管理**：区分 Menu（仅 UI 接收输入）、Game（仅游戏接收输入）、All（两者都接收）三种模式
3. **Action Domain 系统**：定义输入事件在多个 UI 层级间的传播规则（阻断、透传等）
4. **输入防抖**：防止快速切换输入设备导致 UI 图标闪烁
5. **手柄类型识别**：自动检测连接的手柄品牌（Xbox、PlayStation 等），用于显示对应的按键图标

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCurrentInputType` | 获取当前输入类型（键鼠/手柄/触屏） | `UCommonInputSubsystem` |
| `GetDefaultInputType` | 获取当前平台的默认输入类型 | `UCommonInputSubsystem` |
| `SetCurrentInputType` | 手动设置当前输入类型 | `UCommonInputSubsystem` |
| `IsInputMethodActive` | 检查指定输入方式是否激活 | `UCommonInputSubsystem` |
| `GetCurrentGamepadName` | 获取当前手柄的名称标识 | `UCommonInputSubsystem` |
| `SetGamepadInputType` | 设置手柄输入类型（如 Xbox/PS） | `UCommonInputSubsystem` |
| `IsUsingPointerInput` | 当前是否使用指针类输入（鼠标/触屏） | `UCommonInputSubsystem` |
| `ShouldShowInputKeys` | 是否应该在屏幕上显示按键提示 | `UCommonInputSubsystem` |

### 使用示例（蓝图描述）

**场景 1：根据输入类型切换 UI 提示图标**

1. 获取 `UCommonInputSubsystem`（通过 `Get Common Input Subsystem` 节点，传入 Local Player）
2. 调用 `GetCurrentInputType` 获取当前输入类型
3. 用 `Switch on ECommonInputType` 分支：
   - `MouseAndKeyboard` → 显示键盘按键图标
   - `Gamepad` → 调用 `GetCurrentGamepadName` 获取手柄名称，显示对应手柄按键图标
   - `Touch` → 显示触屏手势提示
4. 监听 `OnInputMethodChanged` 委托，在输入类型变化时重新执行上述逻辑

**场景 2：在菜单打开时锁定输入模式**

1. 打开菜单时，调用 `SetCurrentInputType` 或通过 Action Domain 配置将输入模式设为 `Menu`
2. 此时游戏逻辑不再接收输入，只有 UI 响应
3. 关闭菜单时恢复为 `Game` 或 `All` 模式

## C++ 用法

### 头文件引入

```cpp
#include "CommonInputSubsystem.h"
#include "CommonInputBaseTypes.h"
#include "CommonInputTypeEnum.h"
#include "CommonInputModeTypes.h"
```

### 基本用法：获取输入子系统并查询当前输入类型

```cpp
// 获取本地玩家的 CommonInput 子系统
ULocalPlayer* LocalPlayer = GetWorld()->GetFirstLocalPlayerFromController();
UCommonInputSubsystem* InputSubsystem = UCommonInputSubsystem::Get(LocalPlayer);

if (InputSubsystem)
{
    // 查询当前输入类型
    ECommonInputType CurrentType = InputSubsystem->GetCurrentInputType();
    
    switch (CurrentType)
    {
    case ECommonInputType::MouseAndKeyboard:
        UE_LOG(LogTemp, Log, TEXT("当前使用键鼠"));
        break;
    case ECommonInputType::Gamepad:
        UE_LOG(LogTemp, Log, TEXT("当前使用手柄: %s"), *InputSubsystem->GetCurrentGamepadName().ToString());
        break;
    case ECommonInputType::Touch:
        UE_LOG(LogTemp, Log, TEXT("当前使用触屏"));
        break;
    }
}
```

### 基本用法：监听输入类型变化

```cpp
// 绑定输入类型变化回调
UCommonInputSubsystem* InputSubsystem = UCommonInputSubsystem::Get(LocalPlayer);

// 原生 C++ 委托
InputSubsystem->OnInputMethodChangedNative.AddUObject(this, &UMyClass::OnInputMethodChanged);

// 蓝图委托（用于 UFUNCTION）
InputSubsystem->OnInputMethodChanged.AddDynamic(this, &UMyClass::OnInputMethodChangedBP);

// 回调函数
void UMyClass::OnInputMethodChanged(ECommonInputType NewInputType)
{
    // 更新 UI 显示
    UpdateInputIcons(NewInputType);
}
```

### 进阶用法：输入类型过滤与锁定

```cpp
// 锁定输入类型，防止在特定场景下切换（如过场动画期间）
UCommonInputSubsystem* InputSubsystem = UCommonInputSubsystem::Get(LocalPlayer);

// 添加锁定，阻止切换到手柄输入
InputSubsystem->AddOrRemoveInputTypeLock(
    FName("CutscenePlaying"),    // 锁定原因（用于调试和管理）
    ECommonInputType::Gamepad,   // 要锁定的输入类型
    true                         // true = 添加锁定
);

// 过场结束后移除锁定
InputSubsystem->AddOrRemoveInputTypeLock(
    FName("CutscenePlaying"),
    ECommonInputType::Gamepad,
    false  // false = 移除锁定
);
```

### 进阶用法：配置 Action Domain 控制输入事件流

```cpp
// Action Domain 定义了输入事件在 UI 层级间的传播规则
// 通过 UCommonInputActionDomain 配置：

// 在编辑器中创建 UCommonInputActionDomain 数据资产，设置：
// - Behavior: BlockIfActive / BlockIfHandled / NeverBlock
//   控制事件在不同 Domain 之间的传播
// - InnerBehavior: BlockIfActive / BlockIfHandled / NeverBlock
//   控制事件在同一个 Domain 内部的传播
// - bUseActionDomainDesiredInputConfig: 是否强制使用该 Domain 的输入配置
// - InputMode: Menu / Game / All
// - MouseCaptureMode: 鼠标捕获模式

// 在运行时设置 Action Domain Table
InputSubsystem->SetActionDomainTable(MyActionDomainTable);
```

## Demo 示例

### 自动切换输入提示图标

```cpp
// MyInputIconManager.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CommonInputTypeEnum.h"
#include "MyInputIconManager.generated.h"

class UCommonInputSubsystem;
class UImage;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyInputIconManager : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "Input Icons")
    UTexture2D* KeyboardIcon;

    UPROPERTY(EditAnywhere, Category = "Input Icons")
    UTexture2D* XboxIcon;

    UPROPERTY(EditAnywhere, Category = "Input Icons")
    UTexture2D* PlayStationIcon;

    UPROPERTY(EditAnywhere, Category = "Input Icons")
    UTexture2D* TouchIcon;

    UPROPERTY(EditAnywhere, Category = "Input Icons")
    UImage* TargetImage;

private:
    UFUNCTION()
    void OnInputMethodChanged(ECommonInputType NewInputType);

    void UpdateIcon(ECommonInputType InputType);

    FDelegateHandle InputMethodChangedHandle;
};
```

```cpp
// MyInputIconManager.cpp
#include "MyInputIconManager.h"
#include "CommonInputSubsystem.h"
#include "Components/Image.h"
#include "Engine/Texture2D.h"

void UMyInputIconManager::BeginPlay()
{
    Super::BeginPlay();

    ULocalPlayer* LocalPlayer = GetWorld()->GetFirstLocalPlayerFromController();
    UCommonInputSubsystem* InputSubsystem = UCommonInputSubsystem::Get(LocalPlayer);

    if (InputSubsystem)
    {
        // 监听输入类型变化（原生委托）
        InputMethodChangedHandle = InputSubsystem->OnInputMethodChangedNative.AddUObject(
            this, &UMyInputIconManager::OnInputMethodChanged
        );

        // 初始化当前图标
        UpdateIcon(InputSubsystem->GetCurrentInputType());
    }
}

void UMyInputIconManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    ULocalPlayer* LocalPlayer = GetWorld()->GetFirstLocalPlayerFromController();
    UCommonInputSubsystem* InputSubsystem = UCommonInputSubsystem::Get(LocalPlayer);

    if (InputSubsystem)
    {
        InputSubsystem->OnInputMethodChangedNative.Remove(InputMethodChangedHandle);
    }

    Super::EndPlay(EndPlayReason);
}

void UMyInputIconManager::OnInputMethodChanged(ECommonInputType NewInputType)
{
    UpdateIcon(NewInputType);
}

void UMyInputIconManager::UpdateIcon(ECommonInputType InputType)
{
    if (!TargetImage) return;

    UTexture2D* NewIcon = nullptr;

    switch (InputType)
    {
    case ECommonInputType::MouseAndKeyboard:
        NewIcon = KeyboardIcon;
        break;
    case ECommonInputType::Gamepad:
        {
            ULocalPlayer* LocalPlayer = GetWorld()->GetFirstLocalPlayerFromController();
            UCommonInputSubsystem* InputSubsystem = UCommonInputSubsystem::Get(LocalPlayer);
            FName GamepadName = InputSubsystem ? InputSubsystem->GetCurrentGamepadName() : NAME_None;

            // 根据手柄类型选择图标
            if (GamepadName == FName("PS5") || GamepadName == FName("PS4"))
            {
                NewIcon = PlayStationIcon;
            }
            else
            {
                NewIcon = XboxIcon; // 默认使用 Xbox 图标
            }
        }
        break;
    case ECommonInputType::Touch:
        NewIcon = TouchIcon;
        break;
    }

    if (NewIcon)
    {
        TargetImage->SetBrushFromTexture(NewIcon);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 集成 UE5 Enhanced Input 系统，支持 InputAction 映射到 UI 操作 |
| `GameplayTags` | Action Domain 和 UI 组件使用 GameplayTag 进行标识 |

> 其余依赖为标准 Core/Engine/Slate 等，无需额外声明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CommonUI/Source/CommonInput)
- [CommonInputSubsystem 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/CommonUI/Source/CommonInput/Public/CommonInputSubsystem.h)
- [CommonInputSettings 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/CommonUI/Source/CommonInput/Public/CommonInputSettings.h)
- [CommonInputActionDomain 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/CommonUI/Source/CommonInput/Public/CommonInputActionDomain.h)