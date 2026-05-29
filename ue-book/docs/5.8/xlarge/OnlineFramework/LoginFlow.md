# LoginFlow

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 登录流程 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

本文档聚焦于 **LoginFlow** 模块。该模块为需要通过 Web 浏览器进行 OAuth 登录的在线子系统提供统一的登录流程管理框架。

具体来说，它解决以下问题：
- **Facebook / Google 等第三方登录**：在 Windows 平台上，OnlineSubsystemFacebook 和 OnlineSubsystemGoogle 需要弹出浏览器窗口让用户完成 OAuth 授权。LoginFlow 封装了整个浏览器交互流程（弹窗、URL 跳转监听、Cookie 管理、错误处理）。
- **账号创建流程**：除了登录，还支持通过浏览器完成新账号的注册/创建。
- **登录流程与 UI 解耦**：通过 `ILoginFlowManager` 接口和 `FOnDisplayPopup` 委托，将浏览器窗口的展示逻辑交给应用层实现，模块本身不关心 UI 样式。

整个 OnlineFramework 插件包含 8 个运行时模块（Hotfix、Lobby、LoginFlow、Party、PatchCheck、PlayTimeLimit、Qos、Rejoin），LoginFlow 是其中处理第三方 Web 认证的模块。

## 使用场景

- 你的游戏需要支持 **Facebook 登录**（Windows 平台）→ 使用 LoginFlow 模块注册登录流程
- 你的游戏需要支持 **Google 登录**（Windows 平台）→ 使用 LoginFlow 模块注册登录流程
- 你需要自定义登录弹窗的外观和行为 → 实现 `FOnDisplayPopup` 委托，返回自定义 Slate Widget
- 你需要在 Web 登录过程中监听 URL 重定向来判断授权是否成功 → 使用 `FOnLoginFlowRedirectURL` 回调

## 蓝图用法

该模块**没有暴露任何蓝图接口**。所有 API 均为 C++ 接口，需要在代码中使用。

## C++ 用法

### 头文件引入

```cpp
#include "LoginFlow.h"                // 模块入口头文件
#include "ILoginFlowModule.h"         // 模块接口
#include "ILoginFlowManager.h"        // 登录流程管理器接口
```

### 基本用法

以下代码展示如何创建并配置一个登录流程管理器：

```cpp
// 来源: Public/ILoginFlowModule.h, Public/ILoginFlowManager.h

#include "ILoginFlowModule.h"
#include "ILoginFlowManager.h"

// 1. 检查模块是否可用
if (ILoginFlowModule::IsAvailable())
{
    // 2. 获取模块实例并创建管理器
    ILoginFlowModule& LoginFlowModule = ILoginFlowModule::Get();
    TSharedPtr<ILoginFlowManager> LoginFlowManager = LoginFlowModule.CreateLoginFlowManager();

    // 3. 定义弹窗展示回调 —— 你的应用负责将浏览器 Widget 显示给用户
    ILoginFlowManager::FOnDisplayPopup OnDisplayPopup;
    OnDisplayPopup.BindLambda([](const TSharedRef<SWidget>& LoginWidget) -> ILoginFlowManager::FOnPopupDismissed
    {
        // 将 LoginWidget 添加到你的 Slate 面板中展示
        // 返回一个委托，当弹窗需要关闭时被调用
        ILoginFlowManager::FOnPopupDismissed OnDismissed;
        OnDismissed.BindLambda([]()
        {
            // 清理 UI（从面板中移除 widget 等）
        });
        return OnDismissed;
    });

    // 4. 注册 Facebook 子系统的登录流程
    FName OnlineIdentifier("Facebook");
    LoginFlowManager->AddLoginFlow(
        OnlineIdentifier,
        OnDisplayPopup,        // 登录弹窗回调
        OnDisplayPopup,        // 账号创建弹窗回调（可复用同一个）
        true,                  // bPersistCookies：持久化 Cookie
        false                  // bConsumeInput：不拦截未处理的输入
    );
}
```

### 进阶用法

创建独立的登录流程 Widget，手动控制浏览器窗口的生命周期：

```cpp
// 来源: Public/ILoginFlowModule.h (FCreateSettings)

#include "ILoginFlowModule.h"

ILoginFlowModule& LoginFlowModule = ILoginFlowModule::Get();

// 配置登录流程 Widget 的参数
ILoginFlowModule::FCreateSettings Settings;
Settings.Url = TEXT("https://www.facebook.com/v12.0/dialog/oauth?client_id=...&redirect_uri=...");
Settings.bConsumeInput = true;

// 监听 URL 重定向以判断登录是否成功
Settings.RedirectCallback.BindLambda([](const FString& RedirectURL) -> bool
{
    // 检查是否重定向到了你的回调地址
    if (RedirectURL.Contains(TEXT("your-redirect-uri")))
    {
        // 解析 URL 中的授权码
        // 返回 true 表示已处理，登录流程完成
        return true;
    }
    return false;
});

// 错误处理
Settings.ErrorCallback.BindLambda([](ELoginFlowErrorResult ErrorType, const FString& ErrorInfo)
{
    UE_LOG(LogLoginFlow, Error, TEXT("Login flow error: %s"), *ErrorInfo);
});

// 关闭回调
Settings.CloseCallback.BindLambda([](const FString& CloseInfo)
{
    UE_LOG(LogLoginFlow, Log, TEXT("Login flow closed: %s"), *CloseInfo);
});

// 创建浏览器 Widget
TSharedRef<SWidget> LoginWidget = LoginFlowModule.CreateLoginFlowWidget(Settings);

// 将 LoginWidget 添加到你的 Slate UI 面板中
```

## Demo 示例

一个完整的最小示例，展示如何集成 LoginFlow 模块实现 Facebook 登录：

**MyLoginFlowComponent.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ILoginFlowManager.h"
#include "MyLoginFlowComponent.generated.h"

UCLASS(ClassGroup=(Online), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyLoginFlowComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 发起 Facebook 登录 */
    void StartFacebookLogin();

    /** 取消当前登录流程 */
    void CancelLogin();

private:
    TSharedPtr<ILoginFlowManager> LoginFlowManager;
    ILoginFlowManager::FOnDisplayPopup OnDisplayPopup;

    void SetupDisplayPopupDelegate();
};
```

**MyLoginFlowComponent.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyLoginFlowComponent.h"
#include "ILoginFlowModule.h"
#include "Widgets/SWidget.h"

void UMyLoginFlowComponent::BeginPlay()
{
    Super::BeginPlay();

    if (ILoginFlowModule::IsAvailable())
    {
        ILoginFlowModule& Module = ILoginFlowModule::Get();
        LoginFlowManager = Module.CreateLoginFlowManager();

        SetupDisplayPopupDelegate();

        // 注册 Facebook 登录流程
        LoginFlowManager->AddLoginFlow(
            FName("Facebook"),
            OnDisplayPopup,
            OnDisplayPopup,   // 账号创建复用同一弹窗
            true,             // 持久化 Cookie
            false             // 不消费输入
        );
    }
}

void UMyLoginFlowComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (LoginFlowManager.IsValid())
    {
        LoginFlowManager->CancelLoginFlow();
        LoginFlowManager->Reset();
        LoginFlowManager.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

void UMyLoginFlowComponent::SetupDisplayPopupDelegate()
{
    OnDisplayPopup.BindLambda(
        [WeakThis = TWeakObjectPtr<UMyLoginFlowComponent>(this)](
            const TSharedRef<SWidget>& LoginWidget) -> ILoginFlowManager::FOnPopupDismissed
    {
        // 在这里将 LoginWidget 添加到你的游戏 UI 中
        // 例如添加到一个全屏覆盖层

        ILoginFlowManager::FOnPopupDismissed OnDismissed;
        OnDismissed.BindLambda([WeakThis]()
        {
            // 移除弹窗 UI
            if (WeakThis.IsValid())
            {
                UE_LOG(LogTemp, Log, TEXT("Login popup dismissed"));
            }
        });
        return OnDismissed;
    });
}

void UMyLoginFlowComponent::StartFacebookLogin()
{
    if (LoginFlowManager.IsValid())
    {
        LoginFlowManager->CancelLoginFlow(); // 取消之前的（如果有）
        // AddLoginFlow 后，在线子系统会自动触发登录流程
        // 浏览器弹窗通过 OnDisplayPopup 回调展示
    }
}

void UMyLoginFlowComponent::CancelLogin()
{
    if (LoginFlowManager.IsValid())
    {
        LoginFlowManager->CancelLoginFlow();
    }
}
```

## 模块依赖

LoginFlow 模块的独有依赖（Build.cs 中未直接提供，但根据头文件分析）：

| 模块 | 用途 |
|---|---|
| `WebBrowser` / `WebBrowserWidget` | 提供内嵌浏览器 Widget 能力，用于加载 OAuth 登录页面 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

OnlineFramework 插件整体仍在活跃维护，以下是最近的 commit（涵盖所有模块）：

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复烘焙热修复在无后端数据时未生效的问题 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 在 Epic 派对镜像启用时保护社交派对调用 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为 PartyPlatformSessionMonitor 添加钩子以支持平台会话特殊键 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复 Hotfix 加载时的摘要日志输出 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在首次更新处理完成后广播派对初始化事件 |

### 维护评价

- **创建时间**：2016 年 7 月，约 10 年历史
- **近期更新**：2026 年 5 月仍有活跃 commit，但主要集中在 **Hotfix** 和 **Party** 模块
- **LoginFlow 模块状态**：从近期 commit 记录看，LoginFlow 模块本身较长时间没有功能性更新，属于成熟稳定的模块
- **启用方式**：`EnabledByDefault = false`，需要在项目的 `.uproject` 或编辑器设置中手动启用
- **已知限制**：该模块主要面向 Windows 平台的 Web 登录场景；主机平台（PS/Xbox/Switch）通常使用各自的系统登录 API，不依赖此模块

⚠️ **建议**：LoginFlow 模块功能稳定，适合需要在 Windows 平台集成第三方 Web OAuth 登录的项目使用。如果你的目标平台仅为 Windows 且需要 Facebook/Google 登录，可以放心使用。如果需要更现代的浏览器集成（如 CEF），请确认项目的 WebBrowserWidget 模块配置正确。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- [OnlineFramework 源码根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework/Source/LoginFlow)