# Slate Screen Reader

> A screen reader that provides vision accessibility services for Slate.

| 属性 | 值 |
|---|---|
| 中文名 | Slate 屏幕阅读器 |
| 分类 | Accessibility |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateScreenReader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-06-09 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateScreenReader) | |

## 用途

该插件为基于 Slate 构建的 UI 框架提供屏幕阅读器（Screen Reader）功能，属于无障碍（Accessibility）服务的一部分。它允许应用程序通过文本转语音（TTS）向用户（特别是视障用户）播报 UI 控件的状态、内容和用户交互信息。其核心作用是将 Slate 界面元素的可访问性信息转换为语音反馈。

**与 `ScreenReader` 插件的关系**：本插件依赖并基于 `ScreenReader` 插件提供的基础框架和接口。`SlateScreenReader` 插件提供了针对 Slate 引擎的具体实现（如 `FSlateScreenReader` 类），将 `ScreenReader` 的抽象概念与 Slate 的控件系统（`SWidget`）连接起来，从而实现真正的屏幕阅读功能。

## 使用场景

- 你正在开发需要符合无障碍标准（如 WCAG）的 UI 密集型应用程序或游戏。
- 你的应用程序基于 Slate 构建，并希望为视障用户提供音频反馈，使他们能够理解界面内容和操作结果。
- 你需要为游戏或工具中的特定控件（如菜单、按钮、文本）添加语音描述，以增强可访问性。

## 蓝图用法

所有核心功能都封装在 `USlateScreenReaderEngineSubsystem` 引擎子系统中，通过蓝图可访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Activate Screen Reader` | 激活屏幕阅读器系统，使其准备就绪并允许用户注册。 | `USlateScreenReaderEngineSubsystem` |
| `Deactivate Screen Reader` | 停用屏幕阅读器，停止所有语音服务，但不清除已注册的用户。 | `USlateScreenReaderEngineSubsystem` |
| `Is Screen Reader Active` | 检查屏幕阅读器当前是否处于激活状态。 | `USlateScreenReaderEngineSubsystem` |
| `Register User` | 向屏幕阅读器框架注册一个用户（对应一个输入设备，如键盘或控制器）。 | `USlateScreenReaderEngineSubsystem` |
| `Activate User` | 激活一个已注册的屏幕阅读器用户，使其开始接收无障碍反馈。 | `USlateScreenReaderEngineSubsystem` |
| `Deactivate User` | 停用一个屏幕阅读器用户，使其停止接收反馈。 | `USlateScreenReaderEngineSubsystem` |
| `Request Speak` | 请求向指定的屏幕阅读器用户播报一条自定义文本消息。 | `USlateScreenReaderEngineSubsystem` |
| `Request Speak Focused Widget` | 请求朗读指定用户当前焦点所在的控件的无障碍信息。 | `USlateScreenReaderEngineSubsystem` |
| `Stop Speaking` | 立即停止指定用户正在接收的任何语音播报。 | `USlateScreenReaderEngineSubsystem` |
| `Is Speaking` | 检查指定用户当前是否有语音在播放。 | `USlateScreenReaderEngineSubsystem` |
| `Set Speech Volume` | 设置指定用户的文本转语音音量（0.0 到 1.0）。 | `USlateScreenReaderEngineSubsystem` |
| `Set Speech Rate` | 设置指定用户的文本转语音语速（0.0 到 1.0）。 | `USlateScreenReaderEngineSubsystem` |
| `Mute Speech` | 静音指定用户的文本转语音。 | `USlateScreenReaderEngineSubsystem` |
| `Unmute Speech` | 取消静音指定用户的文本转语音。 | `USlateScreenReaderEngineSubsystem` |

### 使用示例（蓝图描述）

一个典型的使用流程如下：

1.  **初始化**：在游戏开始时（例如在 `BeginPlay` 中），获取 `SlateScreenReaderEngineSubsystem` 并调用 `ActivateScreenReader`。
2.  **注册用户**：调用 `RegisterUser`，通常传入用户 ID `0` 来表示主要输入设备。
3.  **激活用户**：调用 `ActivateUser`，传入相同的用户 ID，使该用户开始接收语音反馈。
4.  **播放语音**：
    - 当需要播报自定义信息时，使用 `RequestSpeak` 并传入一个 `FScreenReaderAnnouncement` 结构体。
    - 当希望系统自动朗读当前焦点控件时，调用 `RequestSpeakFocusedWidget`。
5.  **控制**：根据需要使用 `StopSpeaking`、`SetSpeechVolume` 等节点来控制语音播放。

## C++ 用法

### 头文件引入

```cpp
#include "SlateScreenReaderEngineSubsystem.h"
```

### 基本用法

以下是一个完整的 C++ 使用示例，展示了如何初始化屏幕阅读器、注册并激活用户，然后请求语音播报。

```cpp
// MyAccessibilityManager.cpp
#include "SlateScreenReaderEngineSubsystem.h"
#include "Internationalization/Text.h"

void UMyAccessibilityManager::InitializeScreenReader()
{
    // 1. 获取屏幕阅读器子系统单例
    USlateScreenReaderEngineSubsystem& ScreenReaderSubsystem = USlateScreenReaderEngineSubsystem::Get();
    
    // 2. 激活整个屏幕阅读器框架
    ScreenReaderSubsystem.ActivateScreenReader();
    
    // 3. 注册用户 ID 0（通常对应键盘/鼠标或第一个控制器）
    FScreenReaderReply RegisterReply = ScreenReaderSubsystem.RegisterUser(0);
    if (RegisterReply.IsHandled())
    {
        UE_LOG(LogTemp, Log, TEXT("Screen reader user 0 registered."));
        
        // 4. 激活用户，使其开始接收事件
        FScreenReaderReply ActivateReply = ScreenReaderSubsystem.ActivateUser(0);
        if (ActivateReply.IsHandled())
        {
            UE_LOG(LogTemp, Log, TEXT("Screen reader user 0 activated."));
            
            // 5. 向用户播报一条欢迎消息
            static const FText WelcomeText = LOCTEXT("WelcomeMessage", "Welcome to the game. Use the arrow keys to navigate.");
            FScreenReaderAnnouncement WelcomeAnnouncement(WelcomeText.ToString(), FScreenReaderInfo::Important());
            ScreenReaderSubsystem.RequestSpeak(0, WelcomeAnnouncement);
        }
    }
}

// 在子系统生命周期结束或不再需要时，进行清理
void UMyAccessibilityManager::DeinitializeScreenReader()
{
    USlateScreenReaderEngineSubsystem& ScreenReaderSubsystem = USlateScreenReaderEngineSubsystem::Get();
    // 可以选择先注销用户，再停用整个阅读器
    ScreenReaderSubsystem.UnregisterUser(0);
    ScreenReaderSubsystem.DeactivateScreenReader();
}
```

### 进阶用法

可以通过 `ISlateScreenReaderModule` 接口自定义屏幕阅读器的构建逻辑。

```cpp
#include "SlateScreenReaderModule.h"
#include "ScreenReaderBuilder.h"

// 自定义一个构建器，可能用于返回一个带有特定配置的屏幕阅读器实例
class FMyCustomScreenReaderBuilder : public IScreenReaderBuilder
{
public:
    virtual TSharedRef<FScreenReaderBase> Create(const IScreenReaderBuilder::FArgs& InArgs) override
    {
        // 可以在此创建并返回一个自定义的 FScreenReaderBase 子类实例
        // 例如，使用不同的 TTS 引擎配置
        return MakeShared<FSlateScreenReader>(InArgs.PlatformApplication);
    }
};

void RegisterCustomBuilder()
{
    ISlateScreenReaderModule& SlateScreenReaderModule = ISlateScreenReaderModule::Get();
    TSharedRef<FMyCustomScreenReaderBuilder> CustomBuilder = MakeShared<FMyCustomScreenReaderBuilder>();
    SlateScreenReaderModule.SetCustomScreenReaderBuilder(CustomBuilder);
}
```

## Demo 示例

以下是一个最小化的 Actor 类示例，用于在关卡开始时激活屏幕阅读器并播报一段文字。

```cpp
// AccessibilityDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AccessibilityDemoActor.generated.h"

UCLASS()
class AAccessibilityDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    AAccessibilityDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;
};
```

```cpp
// AccessibilityDemoActor.cpp
#include "AccessibilityDemoActor.h"
#include "SlateScreenReaderEngineSubsystem.h"

AAccessibilityDemoActor::AAccessibilityDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AAccessibilityDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取并激活屏幕阅读器
    USlateScreenReaderEngineSubsystem& SRSubsystem = USlateScreenReaderEngineSubsystem::Get();
    SRSubsystem.ActivateScreenReader();
    
    // 注册并激活用户
    const int32 UserId = 0;
    SRSubsystem.RegisterUser(UserId);
    SRSubsystem.ActivateUser(UserId);
    
    // 播报演示信息
    static const FText DemoText = NSLOCTEXT("AccessibilityDemo", "DemoAnnouncement", "Screen reader activated. This is a demo announcement.");
    FScreenReaderAnnouncement Announcement(DemoText.ToString(), FScreenReaderInfo::Default());
    SRSubsystem.RequestSpeak(UserId, Announcement);
}

void AAccessibilityDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 此处可以添加逻辑来根据游戏状态动态请求播报
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ScreenReader` | 提供屏幕阅读器的基础框架、接口（`IScreenReaderBuilder`、`FScreenReaderBase`）和核心数据结构。是本插件运行的必需依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 `UE_LOG` 迁移至新的格式化版本 `UE_LOGF`，属于引擎代码规范更新。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件目录结构的整理或调整，无实质性功能变更。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件元数据中的链接为安全协议（HTTPS），属于维护性更新。 |
| 2022-06-14 | `28609e6f` | Removal of TEXT used in static_asserts (redundant in ANSI/wide modes, broken in UTF-8 mode). | 移除 `static_assert` 中多余的 `TEXT` 宏，修复 UTF-8 模式下的编译问题。 |
| 2021-12-10 | `d9792b10` | Speculative fix for compilation errors in DevBuild relating to screen reader.. | 修复开发构建中与屏幕阅读器相关的编译错误。 |

### 维护评价

`SlateScreenReader` 插件自 2021 年创建以来，功能层面**未见实质性更新或增强**。近期的提交（2022年及之后）均为引擎范围的维护性改动（如日志迁移、链接更新、编译修复），并未添加新功能或改进其无障碍服务。

考虑到以下几点：
1.  它位于 `Experimental` 目录下，且 `.uplugin` 中明确标记 `IsExperimental: true`、`EnabledByDefault: false`。
2.  它严重依赖另一个同样处于实验性的 `ScreenReader` 基础插件。
3.  近 4 年没有功能性更新。

**结论**：该插件是一个**实验性、功能完整但处于维护非活跃状态**的模块。它提供了一个可行的、针对 Slate 的屏幕阅读器原型，但可能未达到生产就绪状态，且未来方向不确定。仅建议在探索无障碍功能或进行相关研究时使用，不推荐作为核心生产功能依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateScreenReader)
- [官方文档](https://docs.unrealengine.com/) (该插件无专门文档页，请查阅引擎通用无障碍文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateScreenReader) (该插件目录下未发现独立测试文件)