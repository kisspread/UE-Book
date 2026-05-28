# Adjust Analytics Provider

> Adjust Analytics Provider

| 属性 | 值 |
|---|---|
| 中文名 | Adjust分析提供者 |
| 分类 | Analytics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AdjustEditor` (Editor), `AndroidAdjust` (Runtime), `IOSAdjust` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/Adjust) | |

## 用途

此插件提供了一个 `IAnalyticsProvider` 的具体实现，用于将 Unreal Engine 项目中的分析数据发送到第三方移动分析平台 **Adjust**。它解决了在 UE 项目中集成 Adjust SDK 所需的平台特定初始化、会话管理和事件上报的封装问题，允许开发者通过 UE 统一的分析接口 (`FAnalytics`) 使用 Adjust 服务，主要用于移动应用（Android/iOS）的用户行为追踪、安装归因和广告效果分析。

## 使用场景

-   你正在开发面向移动平台（Android 或 iOS）的游戏或应用，并希望集成 Adjust 进行用户获取、归因和效果衡量。
-   你的项目需要使用 Unreal Engine 的分析系统 (`FAnalytics`) 来统一管理多个分析提供商，并希望将 Adjust 作为其中一个数据端点。
-   你需要跟踪应用安装、应用内事件、广告点击归因等数据。

## 蓝图用法

该插件主要通过 C++ 接口使用，没有直接暴露大量蓝图节点。其核心功能通过 UE 的分析系统 (`FAnalytics`) 间接调用。

### 核心节点

此插件不直接提供蓝图节点。其功能通过项目的 `Project Settings -> Analytics -> Providers` 配置后，由引擎自动调用。开发者通常通过 C++ 代码或在蓝图中使用通用的 `Record Event`（通过分析系统委托）来触发事件发送。

## C++ 用法

### 头文件引入

```cpp
#include "IOSAdjust.h" // 或对应平台的头文件
```

### 基本用法

获取已配置的 Adjust 分析提供者实例并记录事件。
*来源: 插件公共接口推断*

```cpp
// 获取分析提供者实例（通常在需要记录事件的地方）
TSharedPtr<IAnalyticsProvider> AdjustProvider = FAnalytics::Get().GetDefaultConfiguredProvider();
if (AdjustProvider.IsValid())
{
    // 记录一个简单的自定义事件
    TArray<FAnalyticsEventAttribute> Attributes;
    Attributes.Emplace(TEXT("Level"), 10);
    Attributes.Emplace(TEXT("Score"), 1500);
    AdjustProvider->RecordEvent(TEXT("LevelCompleted"), Attributes);
}
```

### 进阶用法

记录货币交易和设置用户ID。
*来源: FAnalyticsProviderAdjust 接口定义*

```cpp
TSharedPtr<IAnalyticsProvider> AdjustProvider = FAnalytics::Get().GetDefaultConfiguredProvider();
if (AdjustProvider.IsValid())
{
    // 设置用户ID
    AdjustProvider->SetUserID(TEXT("Player_12345"));

    // 记录货币购买事件
    AdjustProvider->RecordCurrencyPurchase(
        TEXT("Gold"),       // 游戏内货币类型
        500,                // 游戏内货币数量
        TEXT("USD"),        // 真实货币类型
        4.99f,              // 真实货币花费
        TEXT("GooglePlay")  // 支付提供商
    );

    // 记录物品购买事件
    AdjustProvider->RecordItemPurchase(
        TEXT("sword_epic"), // 物品ID
        TEXT("Gold"),       // 支付货币
        150,                // 单价
        1                   // 数量
    );
}
```

## Demo 示例

一个最小化的 C++ Actor 示例，用于在关卡开始时记录一个 Adjust 事件。
*注意：这要求项目已在 `Project Settings -> Analytics -> Providers` 中正确配置 Adjust 插件。*

**MyAnalyticsActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAnalyticsActor.generated.h"

UCLASS()
class AMyAnalyticsActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAnalyticsActor();

protected:
    virtual void BeginPlay() override;

private:
    // 用于测试记录的函数
    void LogSampleAdjustEvent();
};
```

**MyAnalyticsActor.cpp**
```cpp
#include "MyAnalyticsActor.h"
#include "Analytics.h"
#include "Interfaces/IAnalyticsProvider.h"

AMyAnalyticsActor::AMyAnalyticsActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyAnalyticsActor::BeginPlay()
{
    Super::BeginPlay();
    // 在游戏开始时记录一个测试事件
    LogSampleAdjustEvent();
}

void AMyAnalyticsActor::LogSampleAdjustEvent()
{
    // 获取默认配置的分析提供者（假设已在项目设置中配置为 Adjust）
    TSharedPtr<IAnalyticsProvider> AnalyticsProvider = FAnalytics::Get().GetDefaultConfiguredProvider();
    if (AnalyticsProvider.IsValid())
    {
        TArray<FAnalyticsEventAttribute> EventAttributes;
        EventAttributes.Emplace(TEXT("Context"), TEXT("DemoStart"));
        EventAttributes.Emplace(TEXT("Time"), FDateTime::Now().ToString());

        // 记录名为 “GameStarted” 的事件
        AnalyticsProvider->RecordEvent(TEXT("GameStarted"), EventAttributes);
        UE_LOG(LogTemp, Log, TEXT("Sample Adjust event logged."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No analytics provider found. Ensure Adjust plugin is configured in Project Settings."));
    }
}
```

## 模块依赖

要使用此插件，你的项目需要以下模块依赖（通常已包含在游戏项目中）：

| 模块 | 用途 |
|---|---|
| `Analytics` | UE 的核心分析框架，提供 `IAnalyticsProvider` 接口 |
| `AdjustSDK` (Android) | Adjust 提供的 Android 平台原生 SDK |
| `AdjustSDK` (iOS) | Adjust 提供的 iOS 平台原生 SDK |

*说明：实际的平台依赖由 `AndroidAdjust` 和 `IOSAdjust` 模块的 Build.cs 管理，使用者无需直接处理。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新格式。 |
| 2026-01-27 | `113268fe` | Fixed include casing mismatch when compiling ios with case sensitive on | 修复了iOS区分大小写编译时头文件大小写不匹配的问题。 |
| 2026-01-14 | `1a097717` | Fix IOS CIS Issues. | 修复iOS持续集成中的问题。 |
| 2025-04-04 | `dce44a87` | Proper fix for analytics check() being replaced with a log. Moved definition of the logging function | 修正了分析代码中检查断言被日志替换的问题，并移动了日志函数的定义。 |
| 2024-02-06 | `c02789b4` | [Backout] - CL31042395 | 回滚了某个提交。 |

### 维护评价

此插件**维护状态中等**。
-   **年龄**: 创建于2017年，属于“老古董”级别。
-   **近期活动**: 最近两年有多次维护性提交，主要是编译兼容性修复（如大小写问题、CIS修复）和日志系统适配，表明仍有人关注其基本运行状态。
-   **功能更新**: 没有发现实质性的新功能添加或 API 变更。它主要是一个平台适配层，依赖于底层 Adjust SDK 的更新。
-   **建议**: 对于新项目，集成此插件意味着你将使用一个久经考验但接口相对固定的适配层。如果需要最新 Adjust SDK 特性，可能需要自行检查或扩展此插件。**鉴于其长期未进行功能性更新，在使用前建议充分测试与当前 Adjust SDK 版本的兼容性。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/Adjust)
- [官方文档](https://docs.unrealengine.com/latest/INT/Gameplay/Analytics/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/Adjust) （注：未发现专用测试目录，测试可能集成在通用分析测试中）