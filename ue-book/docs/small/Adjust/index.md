# Adjust Analytics Provider

> Adjust Analytics Provider

| 属性 | 值 |
|---|---|
| 分类 | Analytics |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AdjustEditor (Editor), AndroidAdjust (Runtime), IOSAdjust (Runtime) |
| 创建时间 | 2017-06-08 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Analytics/Adjust) | |

## 用途

Adjust Plugin 是 [Adjust](https://www.adjust.com/) 移动归因与分析 SDK 的 Unreal Engine 集成层。它实现了 UE 的 `IAnalyticsProvider` 接口，将 UE 标准的 Analytics 事件（如会话开始、物品购买、货币购买等）桥接到 Adjust 的事件追踪系统中。

**解决的问题**：手游开发者需要追踪用户安装来源（归因）、分析用户行为、衡量广告投放效果。Adjust 是业界主流的移动归因平台之一，此 Plugin 让 UE 项目无需自行编写原生集成代码，直接通过 UE 的 Analytics 框架即可接入 Adjust。

**注意**：此 Plugin **仅支持 Android 和 iOS 移动平台**，不支持 Windows/Mac/Linux 等桌面平台。启用时需要在 Adjust 控制台获取 App Token 和事件 Token。

## 使用场景

- 你在做一款手游，需要追踪广告投放的安装归因（attribution）→ 用 Adjust
- 你需要统计玩家的内购行为并回报给广告平台做 ROAS 分析 → 用 Adjust
- 你的 UA 团队要求接入 Adjust SDK 来衡量 CPI 和 LTV → 用 Adjust
- 你只需要简单的游戏内行为统计，不涉及广告归因 → 不需要此 Plugin，用 UE 内置的 Analytics 或其他轻量方案即可

## 蓝图用法

此 Plugin **没有暴露任何蓝图节点**。所有功能通过 UE 的 Analytics 框架以 C++ API 调用，或者通过编辑器中的 **Project Settings → Analytics → Adjust** 面板进行配置。

### 编辑器配置

在 Project Settings 中找到 **Analytics → Adjust**，可配置以下选项：

| 配置项 | 说明 |
|---|---|
| **Sandbox mode for non-distribution** | 非发行包是否使用沙盒模式（默认 `true`） |
| **Sandbox mode for distribution** | 发行包是否使用沙盒模式（默认 `false`） |
| **Application token** | Adjust 控制台提供的 App Token（必填） |
| **Logging level** | 日志级别：VERBOSE / DEBUG / INFO / WARN / ERROR / ASSERT / SUPRESS |
| **Default tracker token** | 默认追踪器 Token（可选） |
| **Process name** | 覆盖进程名，留空则使用包名（可选） |
| **Enable event buffering** | 事件缓冲模式，批量每分钟发送而非立即发送 |
| **Send while in background** | 应用在后台时是否继续发送事件 |
| **Delay start (seconds)** | 首次事件发送前的延迟（最多 10 秒） |
| **Event Map** | 事件名到 Adjust 事件 Token 的映射列表 |

### 事件映射（Event Map）

这是此 Plugin 的核心配置机制。你需要在 Adjust 控制台创建事件，获得事件 Token，然后在此处将 UE 代码中的事件名映射到对应的 Token。

预定义的事件名（代码中硬编码查找）：

| 事件名 | 说明 |
|---|---|
| `SessionAttributes` | 会话开始时自动发送 |
| `Item Purchase` | 物品购买 |
| `Currency Purchase` | 真实货币购买游戏货币 |
| `Currency Given` | 赠送游戏货币 |
| `Error` | 错误事件 |
| `Progress` | 进度事件 |

你也可以通过 `RecordEvent()` 发送自定义事件名，只要在 Event Map 中配置了对应的 Token。

## C++ 用法

### 头文件引入

```cpp
#include "Analytics.h"
#include "Interfaces/IAnalyticsProvider.h"
```

### 基本用法

此 Plugin 通过 UE 的 `FAnalytics` 框架工作。你需要先获取 Analytics Provider，然后调用标准的 `IAnalyticsProvider` 接口方法。

**获取 Provider 并开始会话**：

```cpp
// 获取 Analytics Provider（Adjust 在 Android/iOS 上会被选为活跃的 provider）
TSharedPtr<IAnalyticsProvider> Analytics = FAnalytics::Get().GetDefaultConfiguredProvider();

if (Analytics.IsValid())
{
    // 开始会话，传入会话属性（会作为 session partner parameters 发送给 Adjust）
    TArray<FAnalyticsEventAttribute> SessionAttributes;
    SessionAttributes.Add(FAnalyticsEventAttribute(TEXT("PlayerLevel"), TEXT("5")));
    SessionAttributes.Add(FAnalyticsEventAttribute(TEXT("PlayerClass"), TEXT("Warrior")));
    Analytics->StartSession(SessionAttributes);
}
```

**记录自定义事件**：

```cpp
// 发送自定义事件（事件名必须在 AdjustSettings 的 EventMap 中有对应 Token）
TArray<FAnalyticsEventAttribute> EventAttrs;
EventAttrs.Add(FAnalyticsEventAttribute(TEXT("Level"), TEXT("Forest_01")));
EventAttrs.Add(FAnalyticsEventAttribute(TEXT("Score"), TEXT("1500")));
Analytics->RecordEvent(TEXT("LevelComplete"), EventAttrs);
```

**记录购买事件**：

```cpp
// 记录物品购买（使用内置的 "Item Purchase" 事件名）
// PerItemCost 单位是分（cents），Plugin 内部会除以 100 转换为元
Analytics->RecordItemPurchase(TEXT("sword_001"), TEXT("USD"), 999, 1);

// 记录货币购买
Analytics->RecordCurrencyPurchase(TEXT("Gold"), 500, TEXT("USD"), 4.99, TEXT("GooglePlay"));
```

**记录错误和进度**：

```cpp
// 记录错误
TArray<FAnalyticsEventAttribute> ErrorAttrs;
ErrorAttrs.Add(FAnalyticsEventAttribute(TEXT("ErrorCode"), TEXT("CONNECTION_TIMEOUT")));
Analytics->RecordError(TEXT("NetworkError"), ErrorAttrs);

// 记录进度
TArray<FAnalyticsEventAttribute> ProgressAttrs;
ProgressAttrs.Add(FAnalyticsEventAttribute(TEXT("Checkpoint"), TEXT("3")));
Analytics->RecordProgress(TEXT("Campaign"), TEXT("Chapter1.Boss3"), ProgressAttrs);
```

### 进阶用法

**设置默认事件属性**：

```cpp
// 设置默认属性，会附加到所有后续事件中
TArray<FAnalyticsEventAttribute> DefaultAttrs;
DefaultAttrs.Add(FAnalyticsEventAttribute(TEXT("BuildVersion"), TEXT("1.2.3")));
DefaultAttrs.Add(FAnalyticsEventAttribute(TEXT("Platform"), TEXT("Android")));
Analytics->SetDefaultEventAttributes(MoveTemp(DefaultAttrs));
```

**设置用户 ID**：

```cpp
Analytics->SetUserID(TEXT("player_12345"));
```

### Android 特有 JNI 函数

Android 模块通过 JNI 暴露了以下底层函数（源码中定义，非公开 API）：

| JNI 函数 | 说明 |
|---|---|
| `AndroidThunkCpp_Adjust_SetEnabled(bool)` | 启用/禁用追踪（跨会话记忆） |
| `AndroidThunkCpp_Adjust_SetOfflineMode(bool)` | 离线模式（保存到文件，恢复在线后发送） |
| `AndroidThunkCpp_Adjust_SetPushToken(const FString&)` | 设置推送 Token |
| `AndroidThunkCpp_Adjust_AddSessionPartnerParameter(...)` | 添加会话级 partner 参数 |
| `AndroidThunkCpp_Adjust_RemoveSessionPartnerParameter(...)` | 移除会话级 partner 参数 |
| `AndroidThunkCpp_Adjust_ResetSessionPartnerParameters()` | 重置所有会话级 partner 参数 |

这些函数不建议直接调用，应通过标准的 `IAnalyticsProvider` 接口操作。

## Demo 示例

### 最小集成示例

**MyGame.Build.cs**：

```csharp
using UnrealBuildTool;

public class MyGame : ModuleRules
{
    public MyGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine"
        });

        PrivateDependencyModuleNames.AddRange(new string[] {
            "Analytics"  // 需要依赖 Analytics 模块
        });
    }
}
```

**MyGameInstance.h**：

```cpp
#pragma once

#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;

    UFUNCTION(BlueprintCallable, Category = "Analytics")
    void TrackPurchase(const FString& ItemId, const FString& Currency, int32 PriceCents);
};
```

**MyGameInstance.cpp**：

```cpp
#include "MyGameInstance.h"
#include "Analytics.h"

void UMyGameInstance::Init()
{
    Super::Init();

    // 获取 Adjust provider 并开始会话
    TSharedPtr<IAnalyticsProvider> Analytics = FAnalytics::Get().GetDefaultConfiguredProvider();
    if (Analytics.IsValid())
    {
        TArray<FAnalyticsEventAttribute> Attrs;
        Attrs.Add(FAnalyticsEventAttribute(TEXT("AppVersion"), TEXT("1.0.0")));
        Analytics->StartSession(Attrs);
    }
}

void UMyGameInstance::TrackPurchase(const FString& ItemId, const FString& Currency, int32 PriceCents)
{
    TSharedPtr<IAnalyticsProvider> Analytics = FAnalytics::Get().GetDefaultConfiguredProvider();
    if (Analytics.IsValid())
    {
        Analytics->RecordItemPurchase(ItemId, Currency, PriceCents, 1);
    }
}
```

**DefaultEngine.ini**（也可通过编辑器 UI 配置）：

```ini
[Analytics]
AdjustAppToken=your_app_token_here
AdjustSandboxNondistribution=true
AdjustSandboxDistribution=false
AdjustLogLevel=INFO

[AdjustAnalyticsEventMapping]
+EventNames=SessionAttributes
+EventTokens=your_session_token
+EventNames=Item Purchase
+EventTokens=your_purchase_token
+EventNames=Currency Purchase
+EventTokens=your_currency_purchase_token
+EventNames=Currency Given
+EventTokens=your_currency_given_token
+EventNames=Error
+EventTokens=your_error_token
+EventNames=Progress
+EventTokens=your_progress_token
```

## 模块依赖

### AdjustEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `Analytics` | UE Analytics 框架，提供 `UAnalyticsSettingsBase` 基类 |
| `Core` | UE 核心模块 |

### AndroidAdjust（Runtime 模块，仅 Android）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块 |
| `Analytics` | UE Analytics 框架，提供 `IAnalyticsProvider` 接口 |
| `ApplicationCore` | Android JNI 支持 |

### IOSAdjust（Runtime 模块，仅 iOS）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块 |
| `Analytics` | UE Analytics 框架，提供 `IAnalyticsProvider` 接口 |

### 第三方依赖

| 平台 | SDK | 版本 |
|---|---|---|
| Android | `adjust-android-4.10.2.jar` | 4.10.2 |
| iOS | `AdjustSdk.embeddedframework` | 内嵌于 ThirdPartyFrameworks/ |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-04-03 | `dce44a87c81b` | Proper fix for analytics check() being replaced with a log. Moved definition of the logging function to its own source file and removed duplicated static definitions of the log category. | 修复了 Analytics 模块中 `check()` 被替换为日志调用的问题，属于编译兼容性修复 |
| 2024-02-06 | `c02789b46610` | [Backout] - Move the initial declaration of ::BlockUntilFlushed from IAnalyticsProviderET to its parent class IAnalyticsProvider | 回退了上一次的接口变更，说明此 Plugin 跟随父接口 `IAnalyticsProvider` 的变化 |
| 2024-01-31 | `6bfbcbac5bc7` | Move the initial declaration of ::BlockUntilFlushed from IAnalyticsProviderET to its parent class IAnalyticsProvider | 将 `BlockUntilFlushed` 从 ET provider 上移到父接口（后被回退） |

### 维护评价

- **创建时间**：2017 年 6 月，至今约 9 年，属于老古董级别
- **最近更新**：最近一次功能性更新停留在接口适配层面（跟随 `IAnalyticsProvider` 基类变化），无新功能添加
- **活跃度**：维护不活跃。最近 3 次 commit 都是接口兼容性修复，非功能性增强
- **已知问题/限制**：
  - Android 和 iOS 的 Provider 实现**完全独立**，共享相同类名 `FAnalyticsProviderAdjust`（通过平台条件编译隔离）
  - 代码中有多个 `@TODO: This is probably wrong..` 注释，说明收入事件的处理方式可能不正确
  - `GetSessionID()` 固定返回 `"unavailable"`，`SetSessionID()` 直接忽略调用
  - Android SDK 版本较旧（4.10.2），Adjust 已有更新的 SDK 版本
  - iOS 模块直接 `#import <AdjustSdk/Adjust.h>`，依赖嵌入式 framework，无版本管理
- **是否推荐使用**：⚠️ 如果你的项目需要接入 Adjust，建议**参考此 Plugin 的架构**但自行实现更新的 SDK 集成。此 Plugin 提供了一个良好的 `IAnalyticsProvider` 实现模板，但 Adjust SDK 版本过旧且长期未更新。如果你使用的是 UE 5.x，也可以考虑查看 Marketplace 上是否有更新的 Adjust 集成方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Analytics/Adjust)
- [官方文档](https://docs.unrealengine.com/latest/INT/Gameplay/Analytics/index.html)
- [Adjust 官方文档](https://help.adjust.com/)
- [Adjust SDK (Android)](https://github.com/adjust/android_sdk)
- [Adjust SDK (iOS)](https://github.com/adjust/ios_sdk)
