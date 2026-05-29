# GDK Virtual Keyboard

> Virtual Keyboard support for GDK. Used for Slate text input etc

| 属性 | 值 |
|---|---|
| 中文名 | GDK虚拟键盘 |
| 分类 | Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GDKVirtualKeyboard` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2026-02-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Microsoft/GDKVirtualKeyboard) | |

## 用途

该插件为 GDK (Game Development Kit，即 Xbox 开发环境) 平台提供虚拟键盘支持。它实现了 `IPlatformTextField` 接口，专门用于处理 Slate 文本输入控件（如 `SEditableText`）在 GDK 平台上的键盘弹出、输入和回调逻辑。其核心目的是在 Xbox 主机或使用 GDK 开发的 Windows 平台上，当玩家需要进行文本输入时，能够调用平台原生的虚拟键盘界面，并将输入结果安全地传递回游戏线程，从而避免阻塞和线程安全问题。

## 使用场景

- 你正在使用 GDK（Xbox 开发套件）进行游戏开发，需要支持玩家在游戏中进行文本输入。
- 你的游戏包含聊天框、用户名输入、搜索功能等需要文本输入的 Slate 控件，并且目标平台为 Xbox 或通过 GDK 构建的 Windows 版本。
- 你需要一个稳定的、线程安全的方案来调用和管理平台原生的虚拟键盘。

## 蓝图用法

此插件为底层平台抽象层，**不直接提供蓝图节点**。它的功能由引擎的文本输入系统（`IVirtualKeyboardEntry`）在幕后自动调用。开发者通常不需要直接与 `FGDKPlatformTextField` 交互，只需正常使用 Slate 文本输入控件即可。

**间接使用方式**：
在你的游戏 UI 中，放置一个标准的 `SEditableText` 或 `SMultiLineEditableText` 控件。当该控件获得焦点时，在 GDK 平台上，引擎会自动通过此插件的 `ShowVirtualKeyboard` 方法调出平台虚拟键盘。

## C++ 用法

此插件的主要用法是注册为平台文本字段实现，通常由引擎在初始化时自动完成。开发者主要需要关注其回调逻辑。

### 头文件引入

```cpp
#include "GDKPlatformTextField.h"
```

### 基本用法（源码分析）

`FGDKPlatformTextField` 是核心类，其生命周期由引擎管理。关键方法是 `ShowVirtualKeyboard`，它负责根据请求显示或隐藏虚拟键盘。

```cpp
// 来源: GDKPlatformTextField.h
// 虚拟键盘显示/隐藏的核心入口
virtual void ShowVirtualKeyboard(bool bShow, int32 UserIndex, TSharedPtr<IVirtualKeyboardEntry> TextEntryWidget) override;
```

**设计要点**：
1. **线程安全**：通过 `FCriticalSection` 和 `DebounceTime` 防止频繁、重复的键盘调用。
2. **异步回调**：使用 `VirtualKeyboardCallbackBackgroundThread` 和 `VirtualKeyboardCallbackGameThread` 处理来自平台的异步回调，确保在正确的线程上更新游戏状态。
3. **资源管理**：`KillExisitingDialog` 确保在显示新键盘前关闭旧的对话框。

### 进阶用法（自定义文本输入条目）

如果你需要创建自定义的文本输入控件，你需要实现 `IVirtualKeyboardEntry` 接口，并将其传递给引擎的虚拟键盘系统。此插件会与你实现的 `IVirtualKeyboardEntry` 进行交互。

```cpp
// 你的自定义文本输入条目需要实现此接口
class FMyCustomTextEntry : public IVirtualKeyboardEntry
{
    // ... 实现 GetTextValue, SetTextValue 等接口方法 ...
};

// 当需要显示键盘时（通常由 Slate 控件内部调用），引擎会调用：
// PlatformTextField->ShowVirtualKeyboard(true, UserIndex, MyTextEntryWidget);
```

## Demo 示例

由于此插件是平台层实现，且不直接对外暴露简单 API，以下示例展示了如何在你的 Slate UI 中创建一个文本框，使其在 GDK 平台上能自动唤起虚拟键盘。

**MyUserWidget.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "MyUserWidget.generated.h"

UCLASS()
class UMyUserWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(meta = (BindWidget))
    class UEditableTextBox* PlayerNameTextBox;

    virtual void NativeConstruct() override;

    UFUNCTION()
    void OnNameTextCommitted(const FText& Text, ETextCommit::Type CommitMethod);
};
```

**MyUserWidget.cpp**
```cpp
#include "MyUserWidget.h"
#include "Components/EditableTextBox.h"

void UMyUserWidget::NativeConstruct()
{
    Super::NativeConstruct();
    if (PlayerNameTextBox)
    {
        // 当文本提交时，可以获取到输入的内容
        PlayerNameTextBox->OnTextCommitted.AddDynamic(this, &UMyUserWidget::OnNameTextCommitted);
    }
}

void UMyUserWidget::OnNameTextCommitted(const FText& Text, ETextCommit::Type CommitMethod)
{
    if (CommitMethod == ETextCommit::OnEnter)
    {
        UE_LOG(LogTemp, Log, TEXT("Player entered name: %s"), *Text.ToString());
        // 处理输入结果，例如保存玩家名称
    }
}
```

**在 GDK 平台上运行此 Widget 时**：当 `PlayerNameTextBox` 获得焦点，引擎会自动通过 `GDKVirtualKeyboard` 插件调用系统虚拟键盘。玩家输入完毕确认后，结果会通过 `OnNameTextCommitted` 回调返回到游戏线程。

## 模块依赖

此插件为 GDK 平台专用，依赖关系较为特定。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemGDK` | GDK 平台的在线子系统，可能用于用户身份验证和权限，是调用平台 API 的基础 |
| `GDK` | GDK 核心平台模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-24 | `101f2bf3` | Enable GDK ARM64 support in plugins (requires April 2026 GDK & modern folder layout) | 为插件启用 GDK ARM64 架构支持（需要 2026 年 4 月 GDK 及新目录结构） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式 UE_LOG 日志宏迁移为新的 UE_LOGF 宏。 |
| 2026-03-09 | `5eb8fada` | [Backout] - CL51493025 | [回滚] - 回滚了 CL51493025 的更改。 |
| 2026-03-06 | `21bccda6` | Enable arm64 support in plugins | 为插件启用 ARM64 架构支持。 |
| 2026-02-17 | `5e0fa8dc` | Move GDK plugins to the public engine | 将 GDK 插件从私有仓库迁移至公开引擎代码库。 |

### 维护评价

- **活跃维护**：插件创建于 2026 年 2 月，距今非常新。最近一次更新在 2026 年 4 月 24 日，添加了重要的 ARM64 支持。
- **平台驱动**：维护活动紧跟 GDK 平台自身的更新（如 2026 年 4 月 GDK），表明它与 Xbox 开发工具链保持同步。
- **稳定性**：有一次代码回滚记录，说明团队在谨慎处理变更。
- **推荐使用**：如果你在为 Xbox 或使用 GDK 的 Windows 平台开发游戏并需要文本输入，**推荐使用**。它是 Epic 官方提供的标准解决方案，且处于积极维护中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Microsoft/GDKVirtualKeyboard)
- [官方文档](https://docs.unrealengine.com) (无特定文档，可参考 GDK 平台和 Slate 文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests) (插件目录下未发现专用测试文件，可能集成在更大的 GDK 测试中)