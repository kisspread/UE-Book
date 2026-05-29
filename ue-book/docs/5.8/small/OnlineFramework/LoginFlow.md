# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Qos` (Runtime), `Party` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Hotfix` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

OnlineFramework 插件并非一个独立的在线子系统（Online Subsystem），而是一个**为各种在线子系统提供共享基础服务的框架**。它最初在 2016 年将引擎核心中的 `Hotfix`、`Lobby`、`Party`、`Qos` 等功能模块化并迁移至插件，后续又整合了 `LoginFlow`、`PlayTimeLimit`、`Rejoin` 等功能。

**它解决的核心问题是：** 避免每个 Online Subsystem（如 Steam, Xbox Live, PSN）重复实现玩家匹配、房间管理、质量检测、登录流程等通用且复杂的在线功能。这些功能被抽象为框架性的模块，供具体的在线子系统调用或依赖。

简单来说，它是 **UE 在线游戏功能的“公共基础设施”层**。

## 使用场景

- **你需要为你的游戏创建或加入一个游戏房间（Party/Session）**：使用 `Party` 和 `Lobby` 模块来管理玩家组队和匹配逻辑。
- **你的游戏需要跨区域联机，并希望选择延迟最低的服务器**：使用 `Qos` (Quality of Service) 模块来测量到不同服务器的网络质量并进行选择。
- **你的游戏支持通过 Facebook、Google 等第三方账号登录（尤其是 PC 平台）**：需要 `LoginFlow` 模块来创建和管理基于 Web 浏览器的授权登录窗口。
- **你需要实现家长控制或防沉迷系统中的游戏时长限制**：可以使用 `PlayTimeLimit` 模块。
- **你的游戏需要实现玩家掉线后的快速重新加入功能**：`Rejoin` 模块提供了相关支持。

## 蓝图用法

本插件主要提供的是底层 C++ 框架和接口，其功能更多是被其他在线子系统模块内部调用，而非直接暴露为蓝图节点。其核心模块（如 `LoginFlow`）的 API 主要设计为 C++ 接口。

部分模块（如 `Qos`）可能提供了蓝图友好的类，但需要查看具体子模块文档。在本插件（`OnlineFramework`）的层级，直接可供蓝图使用的公开节点较少。

**核心模式**：游戏逻辑通常通过 `OnlineSubsystem` 的蓝图接口（如 `Find Sessions`, `Create Session`）间接使用到本插件提供的底层服务。

## C++ 用法

本插件的使用主要在 C++ 层，通过引入相应模块的头文件来使用其接口。

### 头文件引入

```cpp
// 使用登录流功能
#include "ILoginFlowModule.h"

// 使用 Party 功能
#include "OnlineSubsystem.h"
// Party 模块的具体接口通常通过 OnlineSubsystem 获取
```

### 基本用法

以下示例展示了如何通过 `LoginFlow` 模块创建一个登录流程管理器，这是在 PC 平台实现第三方登录的关键步骤。

```cpp
// 假设在某个 GameInstance 或管理类中
#include "ILoginFlowModule.h"

class UMyLoginManager
{
public:
    void InitializeLoginFlow()
    {
        // 1. 检查 LoginFlow 模块是否可用
        if (ILoginFlowModule::IsAvailable())
        {
            // 2. 获取模块实例并创建登录流管理器
            ILoginFlowModule& LoginFlowModule = ILoginFlowModule::Get();
            TSharedPtr<ILoginFlowManager> LoginFlowManager = LoginFlowModule.CreateLoginFlowManager();

            if (LoginFlowManager.IsValid())
            {
                // 3. 为特定的 Online Subsystem (例如 Facebook) 注册登录流程
                //    这里需要绑定一个 FOnDisplayPopup 委托，用于在需要时显示浏览器窗口
                ILoginFlowManager::FOnDisplayPopup DisplayPopupDelegate;
                DisplayPopupDelegate.BindUObject(this, &UMyLoginManager::OnDisplayLoginPopup);

                FName OnlineSubsystemIdentifier = FName(TEXT("Facebook"));
                LoginFlowManager->AddLoginFlow(
                    OnlineSubsystemIdentifier,
                    DisplayPopupDelegate, // 登录流程的 UI 弹出委托
                    DisplayPopupDelegate, // 账户创建流程的 UI 弹出委托
                    true,  // 是否持久化 Cookies
                    false  // 是否消耗未处理的输入
                );

                // 保存管理器实例
                ActiveLoginFlowManager = LoginFlowManager;
            }
        }
    }

private:
    // 回调函数：当需要显示浏览器窗口时由 LoginFlowManager 调用
    ILoginFlowManager::FOnPopupDismissed OnDisplayLoginPopup(const TSharedRef<SWidget>& LoginWidget)
    {
        // 在这里将 LoginWidget 添加到你的 Slate UI 或 UMG 中进行显示
        // 例如：MyOverlay->AddChild(LoginWidget);

        // 返回一个委托，该委托在弹出窗口需要关闭时被调用
        return ILoginFlowManager::FOnPopupDismissed::CreateLambda([this]()
        {
            // 执行清理工作，例如从父控件中移除 LoginWidget
            // MyOverlay->RemoveChild(LoginWidget);
        });
    }

    TSharedPtr<ILoginFlowManager> ActiveLoginFlowManager;
};
```
*来源：基于 `Public/ILoginFlowManager.h` 和 `Public/ILoginFlowModule.h` 的分析。*

### 进阶用法

更高级的用法涉及直接创建登录流 Widget 以进行更精细的控制。

```cpp
// 创建一个独立的登录流小部件，并处理各种回调
#include "ILoginFlowModule.h"

void CreateLoginWidgetDirectly()
{
    if (!ILoginFlowModule::IsAvailable()) return;

    ILoginFlowModule& Module = ILoginFlowModule::Get();
    
    // 配置创建参数
    ILoginFlowModule::FCreateSettings Settings;
    Settings.Url = TEXT("https://example.com/auth/facebook");
    Settings.bConsumeInput = true;
    
    // 绑定各种回调
    Settings.CloseCallback.BindLambda([](const FString& CloseInfo) {
        UE_LOG(LogTemp, Log, TEXT("Login flow closed: %s"), *CloseInfo);
    });
    
    Settings.ErrorCallback.BindLambda([](ELoginFlowErrorResult ErrorType, const FString& ErrorInfo) {
        UE_LOG(LogTemp, Error, TEXT("Login flow error: %s"), *ErrorInfo);
    });
    
    Settings.RedirectCallback.BindLambda([](const FString& RedirectURL) -> bool {
        // 检查是否是目标回调 URL (例如你的游戏服务器返回的 token URL)
        if (RedirectURL.Contains(TEXT("mygame://auth/callback")))
        {
            // 处理认证码，完成登录
            HandleAuthCode(RedirectURL);
            return true; // 表示已处理
        }
        return false; // 让浏览器继续处理
    });
    
    // 创建 Widget
    TSharedRef<SWidget> LoginWidget = Module.CreateLoginFlowWidget(Settings);
    
    // 将 LoginWidget 添加到你的 Slate 层级中
    // ...
}

```
*来源：基于 `Public/ILoginFlowModule.h` 中 `FCreateSettings` 结构体的分析。*

## Demo 示例

一个完整的、可编译的最小示例，展示如何在 GameInstance 中初始化并管理登录流程。

**MyGameInstance.h**
```cpp
// MyGameInstance.h
#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "ILoginFlowManager.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;

    UFUNCTION(BlueprintCallable, Category = "Login")
    void StartFacebookLogin();

private:
    // 显示登录弹窗的回调
    ILoginFlowManager::FOnPopupDismissed OnShowLoginPopup(const TSharedRef<SWidget>& LoginWidget);

    // 清理当前登录流
    void CleanupLoginFlow();

    TSharedPtr<ILoginFlowManager> LoginFlowManager;
};
```

**MyGameInstance.cpp**
```cpp
// MyGameInstance.cpp
#include "MyGameInstance.h"
#include "ILoginFlowModule.h"
#include "Widgets/Layout/SBorder.h"
#include "Framework/Application/SlateApplication.h"

void UMyGameInstance::Init()
{
    Super::Init();
    // 模块通常在引擎早期加载，这里我们只是检查
    if (ILoginFlowModule::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("LoginFlow module is available."));
    }
}

void UMyGameInstance::StartFacebookLogin()
{
    if (LoginFlowManager.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("A login flow is already in progress."));
        return;
    }

    if (!ILoginFlowModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("LoginFlow module is not available!"));
        return;
    }

    // 1. 创建管理器
    ILoginFlowModule& LoginFlowModule = ILoginFlowModule::Get();
    LoginFlowManager = LoginFlowModule.CreateLoginFlowManager();

    if (!LoginFlowManager.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create LoginFlowManager."));
        return;
    }

    // 2. 设置委托：当需要弹窗时调用我们的函数
    ILoginFlowManager::FOnDisplayPopup PopupDelegate;
    PopupDelegate.BindUObject(this, &UMyGameInstance::OnShowLoginPopup);

    // 3. 为 “Facebook” 子系统注册登录流
    const FName FacebookIdentifier(TEXT("Facebook"));
    bool bSuccess = LoginFlowManager->AddLoginFlow(
        FacebookIdentifier,
        PopupDelegate,     // 登录弹窗
        PopupDelegate,     // 账户创建弹窗 (这里复用同一个)
        true,              // 保持 Cookie 登录状态
        false              // 不消耗全局输入
    );

    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to add login flow for %s."), *FacebookIdentifier.ToString());
        LoginFlowManager.Reset();
        return;
    }

    // 此时，逻辑上登录流已就绪。
    // 实际触发通常由 OnlineSubsystemIdentity 的 Login 方法内部发起，它会回调到我们的 PopupDelegate。
    // 为了演示，我们可以模拟触发：
    UE_LOG(LogTemp, Log, TEXT("LoginFlow registered for Facebook. Waiting for OnlineSubsystem to initiate login..."));
}

ILoginFlowManager::FOnPopupDismissed UMyGameInstance::OnShowLoginPopup(const TSharedRef<SWidget>& LoginWidget)
{
    UE_LOG(LogTemp, Log, TEXT("Displaying login flow popup."));

    // 在实际游戏中，你会将 LoginWidget 添加到一个 Slate 覆盖层或 UMG 面板中。
    // 这里我们简单地将其添加到桌面顶层进行演示。
    if (FSlateApplication::IsInitialized())
    {
        FSlateApplication::Get().AddWindow(
            SNew(SWindow)
            .ClientSize(FVector2D(800, 600))
            [
                SNew(SBorder)
                [
                    LoginWidget // 将登录浏览器 Widget 放入窗口
                ]
            ]
        );
    }

    // 返回一个委托，用于当登录流程完成或取消时清理我们的 UI。
    return ILoginFlowManager::FOnPopupDismissed::CreateLambda([this]()
    {
        UE_LOG(LogTemp, Log, TEXT("Login flow popup dismissed. Cleaning up."));
        CleanupLoginFlow();
    });
}

void UMyGameInstance::CleanupLoginFlow()
{
    if (LoginFlowManager.IsValid())
    {
        // 可选：主动取消任何进行中的流程
        LoginFlowManager->CancelLoginFlow();
        LoginFlowManager.Reset();
    }
}
```

## 模块依赖

本插件模块众多，但其依赖的模块大多是在线子系统的标准依赖。要使用本插件的特定模块（如 `LoginFlow`），你的模块可能需要在 `Build.cs` 中添加依赖。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 核心在线子系统接口，本插件的大部分模块服务于它 |
| `WebBrowserWidget` | `LoginFlow` 模块需要，用于创建嵌入式浏览器窗口 |
| `HTTP` | `Hotfix`、`PatchCheck` 等模块可能需要，用于下载热修复或补丁信息 |

*注意：具体依赖因使用的子模块而异。例如，`Party` 模块可能依赖 `OnlineSubsystemGDK`。请参考具体模块的 `.Build.cs` 文件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复“启动时热修复”功能在某些情况下无法应用内置修复的问题 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 当启用 Epic 派对镜像功能时，增加对邀请和加入派对等社交功能的保护 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为 `PartyPlatformSessionMonitor` 增加钩子，允许游戏派对向平台会话添加特殊键值 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复 `HotfixManager` 在启动时加载热修复的摘要日志输出 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在首次处理完更新后，再广播派对初始化完成的事件 |

### 维护评价

- **创建时间**：2016 年，已有近 9 年历史，是 Unreal Engine 在线生态的基石之一。
- **最近更新**：**非常活跃**。近 3 个月内有多次功能性更新和 Bug 修复，涉及 `Hotfix`、`Party`、`Rejoin` 等核心模块。
- **活跃维护**：是。Epic Games 显然仍在持续维护和改进此框架，以支持其自家游戏（如 Fortnite）和更广泛的开发者生态。
- **已知限制**：作为“框架”，其功能实现依赖于具体的 `OnlineSubsystem` 插件。`LoginFlow` 模块在主机平台可能不可用或行为不同（因 Web 浏览器限制）。
- **推荐使用**：如果你正在开发需要上述在线功能的多人游戏，并且目标平台包括 PC，**强烈建议了解和使用此插件提供的模块**，可以避免大量重复开发工作。但请注意，它需要手动在 `.uproject` 中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- [官方文档](https://docs.unrealengine.com) (Epic 官方未提供专门页面，相关文档分散在 OnlineSubsystem 和各自功能的文档中)