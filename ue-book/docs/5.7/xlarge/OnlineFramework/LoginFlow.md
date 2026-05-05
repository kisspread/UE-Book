# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Qos` (Runtime), `Party` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Hotfix` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework) | |

> ⚠️ **需要手动启用**：此插件 `EnabledByDefault=false`，需在项目设置中手动启用。

---

## 用途

OnlineFramework 是 Epic 为在线游戏服务提供的**共享基础设施插件**，将常见的在线功能抽象为独立模块，供各 OnlineSubsystem（如 EOS、Facebook、Google 等）复用。它不是一个完整的在线子系统，而是多个在线子系统共同依赖的"工具箱"。

核心解决的问题：

- **Web 登录流程**（LoginFlow）：为需要 OAuth 浏览器登录的平台（如 Windows 上的 Facebook/Google 登录）提供统一的 Web 弹窗登录 UI 框架
- **大厅与派对**（Lobby / Party）：提供跨平台的大厅匹配和玩家组队抽象
- **服务质量检测**（Qos）：测量和选择最优服务器/数据中心
- **热修复**（Hotfix）：支持服务端下发配置热更新，无需客户端发版
- **补丁检查**（PatchCheck）：启动时检查客户端版本是否需要更新
- **游玩时间限制**（PlayTimeLimit）：家长控制 / 防沉迷系统的游玩时长管理
- **重连**（Rejoin）：断线后重新加入游戏会话的基础设施

## 使用场景

- 你在 Windows 上集成 Facebook/Google 第三方登录 → 使用 **LoginFlow** 模块创建 Web 弹窗完成 OAuth
- 你需要跨平台的组队和大厅匹配 → 使用 **Party** 和 **Lobby** 模块
- 你需要自动选择延迟最低的服务器区域 → 使用 **Qos** 模块
- 你需要在不发版的情况下修复线上配置问题 → 使用 **Hotfix** 模块
- 你的游戏需要在启动时检查版本更新 → 使用 **PatchCheck** 模块
- 你的游戏需要遵守防沉迷法规限制游玩时长 → 使用 **PlayTimeLimit** 模块
- 你需要支持玩家断线后重新加入对局 → 使用 **Rejoin** 模块

## 蓝图用法

此插件主要面向 C++ 层，提供的是底层接口和管理器类，**没有暴露 BlueprintCallable 节点**。各模块通过 C++ 接口与 OnlineSubsystem 交互，上层游戏逻辑通常通过 OnlineSubsystem 的蓝图接口（如 `Login`、`CreateSession` 等）间接使用。

如果需要在蓝图中触发登录流程，应通过 OnlineSubsystem 的 `Login` 节点，LoginFlow 模块会在底层自动处理 Web 弹窗。

## C++ 用法

### 模块概览

本插件包含 8 个独立的 Runtime 模块，按需引用：

| 模块 | 职责 |
|---|---|
| `LoginFlow` | Web 弹窗式 OAuth 登录流程管理 |
| `Party` | 跨平台玩家组队系统 |
| `Lobby` | 大厅/房间匹配系统 |
| `Qos` | 服务质量检测（延迟、丢包） |
| `Hotfix` | 服务端热修复配置下发 |
| `PatchCheck` | 客户端版本/补丁检查 |
| `PlayTimeLimit` | 游玩时间限制（防沉迷） |
| `Rejoin` | 断线重连基础设施 |

---

### LoginFlow 模块详解

LoginFlow 是本插件中源码最清晰的模块，为需要浏览器弹窗完成 OAuth 登录的 OnlineSubsystem 提供统一框架。

#### 头文件引入

```cpp
#include "ILoginFlowModule.h"
#include "ILoginFlowManager.h"
#include "LoginFlowManager.h"
```

#### 核心概念

LoginFlow 的工作流程：

1. 游戏启动时，通过 `ILoginFlowManager::AddLoginFlow()` 注册需要 Web 登录的 OnlineSubsystem
2. 当 OnlineSubsystem 需要登录时，触发 `FOnDisplayPopup` 委托，传入一个包含 Web 浏览器的 Slate Widget
3. 应用程序将该 Widget 显示为弹窗（如模态对话框）
4. 用户在浏览器中完成 OAuth 授权
5. LoginFlow 捕获重定向 URL，完成登录流程
6. 弹窗关闭，清理资源

#### 基本用法 — 创建 LoginFlowManager

```cpp
// 来源: ILoginFlowModule.h

// 获取 LoginFlow 模块
if (ILoginFlowModule::IsAvailable())
{
    ILoginFlowModule& LoginFlowModule = ILoginFlowModule::Get();
    
    // 创建 LoginFlow 管理器
    TSharedPtr<ILoginFlowManager> LoginFlowManager = LoginFlowModule.CreateLoginFlowManager();
}
```

#### 注册 OnlineSubsystem 的登录流程

```cpp
// 来源: ILoginFlowManager.h

// 定义弹窗显示回调 — 当需要显示 Web 登录窗口时被调用
ILoginFlowManager::FOnDisplayPopup OnDisplayPopup;
OnDisplayPopup.BindLambda([](const TSharedRef<SWidget>& LoginWidget) -> ILoginFlowManager::FOnPopupDismissed
{
    // 将 LoginWidget 添加到你的 UI 层（例如模态对话框）
    // TSharedRef<SWidget> LoginWidget 是包含 Web 浏览器的控件
    
    // 返回一个委托，当弹窗需要关闭时调用
    ILoginFlowManager::FOnPopupDismissed OnDismissed;
    OnDismissed.BindLambda([]()
    {
        // 清理弹窗 UI
    });
    return OnDismissed;
});

// 注册 Facebook 登录流程
FName FacebookIdentifier(TEXT("Facebook"));
LoginFlowManager->AddLoginFlow(
    FacebookIdentifier,           // OnlineSubsystem 标识符
    OnDisplayPopup,               // 登录流程弹窗委托
    OnDisplayPopup,               // 账号创建流程弹窗委托（可复用同一回调）
    true,                         // bPersistCookies: 是否持久化 Cookie
    false                         // bConsumeInput: 是否消费未处理的输入
);
```

#### 检查和取消登录流程

```cpp
// 来源: ILoginFlowManager.h

// 检查某个 OnlineSubsystem 是否已注册登录流程
if (LoginFlowManager->HasLoginFlow(FName("Facebook")))
{
    // Facebook 登录流程已注册
}

// 取消当前正在进行的登录流程
LoginFlowManager->CancelLoginFlow();

// 取消当前正在进行的账号创建流程
LoginFlowManager->CancelAccountCreationFlow();

// 重置所有登录流程，断开与 OnlineSubsystem 的连接
LoginFlowManager->Reset();
```

#### 进阶用法 — 自定义登录 Widget 创建

```cpp
// 来源: ILoginFlowModule.h (FCreateSettings)

// 通过模块直接创建登录 Widget（更底层的控制）
ILoginFlowModule::FCreateSettings Settings;
Settings.Url = TEXT("https://www.facebook.com/v15.0/dialog/oauth?...");
Settings.StyleSet = nullptr;  // 使用默认样式，或传入自定义 ISlateStyle
Settings.bConsumeInput = false;

// 设置错误回调
Settings.ErrorCallback.BindLambda([](ELoginFlowErrorResult ErrorType, const FString& ErrorInfo)
{
    switch (ErrorType)
    {
    case ELoginFlowErrorResult::LoadFail:
        UE_LOG(LogLoginFlow, Error, TEXT("Web page failed to load: %s"), *ErrorInfo);
        break;
    case ELoginFlowErrorResult::Unknown:
    default:
        UE_LOG(LogLoginFlow, Error, TEXT("Unknown login flow error: %s"), *ErrorInfo);
        break;
    }
});

// 设置关闭回调
Settings.CloseCallback.BindLambda([](const FString& CloseInfo)
{
    UE_LOG(LogLoginFlow, Log, TEXT("Login flow closed: %s"), *CloseInfo);
});

// 设置重定向回调 — 用于拦截 OAuth 回调 URL
Settings.RedirectCallback.BindLambda([](const FString& RedirectURL) -> bool
{
    if (RedirectURL.StartsWith(TEXT("myapp://callback")))
    {
        // 解析 OAuth 回调参数
        // 返回 true 表示已处理，浏览器不会继续导航
        return true;
    }
    return false;  // 未处理，让浏览器继续
});
```

## Demo 示例

以下是一个完整的 LoginFlow 集成示例，展示如何在 Slate UI 中嵌入 Web 登录弹窗：

### MyLoginFlowWidget.h

```cpp
// MyLoginFlowWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "ILoginFlowManager.h"

class ILoginFlowManager;

class SMyLoginFlowWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyLoginFlowWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
    
    /** 启动指定 OnlineSubsystem 的登录流程 */
    void StartLogin(FName OnlineIdentifier);

private:
    /** LoginFlow 管理器实例 */
    TSharedPtr<ILoginFlowManager> LoginFlowManager;
    
    /** 当前显示的登录 Widget */
    TSharedPtr<SWidget> CurrentLoginWidget;
    
    /** 弹窗容器 */
    TSharedPtr<SBorder> PopupContainer;
    
    /** 弹窗关闭委托句柄 */
    ILoginFlowManager::FOnPopupDismissed OnPopupDismissed;
    
    /** 显示登录弹窗 */
    ILoginFlowManager::FOnPopupDismissed DisplayPopup(const TSharedRef<SWidget>& LoginWidget);
    
    /** 关闭登录弹窗 */
    void DismissPopup();
};
```

### MyLoginFlowWidget.cpp

```cpp
// MyLoginFlowWidget.cpp
#include "MyLoginFlowWidget.h"
#include "ILoginFlowModule.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"

void SMyLoginFlowWidget::Construct(const FArguments& InArgs)
{
    // 创建 LoginFlow 管理器
    if (ILoginFlowModule::IsAvailable())
    {
        ILoginFlowModule& LoginFlowModule = ILoginFlowModule::Get();
        LoginFlowManager = LoginFlowModule.CreateLoginFlowManager();
    }

    ChildSlot
    [
        SNew(SBorder)
        .Padding(10.0f)
        [
            SAssignNew(PopupContainer, SBox)
            .Visibility(EVisibility::Collapsed)  // 初始隐藏
        ]
    ];
}

ILoginFlowManager::FOnPopupDismissed SMyLoginFlowWidget::DisplayPopup(
    const TSharedRef<SWidget>& LoginWidget)
{
    // 显示登录 Widget
    CurrentLoginWidget = LoginWidget;
    PopupContainer->SetContent(LoginWidget);
    PopupContainer->SetVisibility(EVisibility::Visible);

    // 返回关闭回调
    ILoginFlowManager::FOnPopupDismissed DismissedDelegate;
    DismissedDelegate.BindSP(this, &SMyLoginFlowWidget::DismissPopup);
    return DismissedDelegate;
}

void SMyLoginFlowWidget::DismissPopup()
{
    // 隐藏并清理
    PopupContainer->SetContent(SNullWidget::NullWidget);
    PopupContainer->SetVisibility(EVisibility::Collapsed);
    CurrentLoginWidget.Reset();
}

void SMyLoginFlowWidget::StartLogin(FName OnlineIdentifier)
{
    if (!LoginFlowManager.IsValid())
    {
        return;
    }

    // 绑定弹窗显示委托
    ILoginFlowManager::FOnDisplayPopup OnDisplayPopup;
    OnDisplayPopup.BindSP(this, &SMyLoginFlowWidget::DisplayPopup);

    // 注册登录流程（如果尚未注册）
    if (!LoginFlowManager->HasLoginFlow(OnlineIdentifier))
    {
        LoginFlowManager->AddLoginFlow(
            OnlineIdentifier,
            OnDisplayPopup,   // 登录弹窗
            OnDisplayPopup,   // 账号创建弹窗（复用）
            true,             // 持久化 Cookie
            false             // 不消费输入
        );
    }
}
```

## 模块依赖

各模块的依赖关系（基于头文件分析）：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 所有模块的核心依赖，提供在线子系统抽象接口 |
| `WebBrowser` | LoginFlow 模块依赖，提供内嵌浏览器 Widget |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：使用本插件的任何模块时，你的 Build.cs 需要添加对对应模块的依赖。例如使用 LoginFlow：
> ```csharp
> PublicDependencyModuleNames.AddRange(new string[] { "LoginFlow" });
> ```

## 维护状态

### 近期更新

```
736bd5e2ed27 Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
66e9bb39ff7e Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base
d205101cc84a Removed unnecessary private include modules.
```

- `736bd5e2` — 构建系统改动：统一 DLL 导出标记（dllstorage），属于平台兼容性维护
- `66e9bb39` — 代码清理：移除 UE 5.2 时代的兼容性宏，属于版本升级维护
- `d205101c` — 代码清理：移除不必要的私有 include 模块引用

### 维护评价

**⚠️ 维护不活跃 — 仅接受构建系统修复**

- 创建于 2016 年，已有约 9 年历史
- 近期 3 次提交均为构建系统/代码清理，**无功能性更新**
- `EnabledByDefault=false` 表明 Epic 将此插件视为可选基础设施
- 8 个模块中，LoginFlow 的 Web 登录模式在现代 EOS（Epic Online Services）架构下使用频率降低
- Party、Lobby 等功能在 EOS SDK 中有更完整的实现

**建议**：
- 如果你使用 EOS SDK，优先使用 EOS 自带的 Party/Lobby/Connect 功能
- 如果你需要 Windows 上的 Facebook/Google Web 登录，LoginFlow 模块仍然可用
- Qos 模块在某些场景下仍有独立价值
- 此插件整体处于**维护模式**，不太可能有新功能添加

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework/Tests)（如果存在）