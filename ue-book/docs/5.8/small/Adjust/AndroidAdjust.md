# Adjust Analytics Provider

> Adjust Analytics Provider

| 属性 | 值 |
|---|---|
| 中文名 | Adjust 分析 |
| 分类 | Analytics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AdjustEditor` (Editor), `AndroidAdjust` (Runtime), `IOSAdjust` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-08 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/Adjust) | |

## 用途

Adjust 是一个第三方**移动归因（Attribution）与分析平台**，主要用于追踪用户安装来源、应用内事件和广告转化效果。本插件将 Adjust SDK 集成到 UE5 的 `IAnalyticsProvider` 框架中，使得引擎的统一分析系统能够通过 Adjust 发送事件数据。

与 Firebase Analytics 等纯游戏分析工具不同，Adjust 的核心价值在于**用户获取归因**——即回答"这个用户是从哪个广告渠道安装的"这类营销问题。插件本身只是一个薄封装层，实际数据处理由各平台的原生 Adjust SDK 完成：

- **AndroidAdjust**：通过 JNI 调用 Adjust Android SDK
- **IOSAdjust**：通过 Objective-C++ 桥接 Adjust iOS SDK

插件默认不启用（`EnabledByDefault=false`），需要集成 Adjust 服务时手动开启。

## 使用场景

- 你在做一款移动游戏，需要追踪 Facebook/Google 广告投放的安装转化率 → 用 Adjust
- 你需要将游戏内购买事件关联到具体的广告投放渠道 → 用 Adjust
- 你的团队需要向 Adjust 仪表板发送自定义事件（如关卡完成、新手引导完成等）→ 用 Adjust
- 你只需要纯游戏内行为分析，不涉及广告归因 → 用 Firebase Analytics 或其他插件，不需要 Adjust

## 蓝图用法

本插件不提供额外的 BlueprintCallable 函数。所有交互通过 UE5 引擎统一的 **Analytics Provider** 系统进行：

### 核心节点

以下节点来自引擎内置的 Analytics 蓝图接口（非本插件独有，但通过本插件路由到 Adjust）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Session` | 启动分析会话，向 Adjust 报告 session 开始 | 引擎 Analytics 蓝图接口 |
| `End Session` | 结束分析会话 | 引擎 Analytics 蓝图接口 |
| `Record Event` | 发送自定义事件到 Adjust（需在 Adjust 仪表板配置事件 Token） | 引擎 Analytics 蓝图接口 |
| `Flush Events` | 立即发送缓冲区中的事件 | 引擎 Analytics 蓝图接口 |

### 使用示例（蓝图描述）

1. 在 **Project Settings → Analytics → Providers** 中启用 Adjust Provider
2. 配置 Adjust 的 **App Token**（从 Adjust 仪表板获取）
3. 在游戏逻辑中，通过引擎的 Analytics 蓝图节点调用 `Record Event`，传入事件名称和属性
4. 事件会通过 `FAnalyticsProviderAdjust::RecordEvent` 发送到 Adjust 服务器

## C++ 用法

### 头文件引入

```cpp
#include "IAnalyticsProvider.h"
```

### 基本用法

通过引擎的 Analytics 单例获取 Adjust Provider 并发送事件：

```cpp
// 来源: Public/AndroidAdjust.h, Private/AndroidAdjustProvider.h

#include "IAnalyticsProvider.h"
#include "AnalyticsEventAttribute.h"

// 获取当前激活的分析 Provider（即 Adjust，如果已配置）
TSharedPtr<IAnalyticsProvider> Analytics = FAnalytics::Get().GetDefaultConfiguredProvider();

if (Analytics.IsValid())
{
    // 启动会话
    Analytics->StartSession();

    // 发送自定义事件（事件名需对应 Adjust 仪表板中配置的事件 Token）
    TArray<FAnalyticsEventAttribute> Attributes;
    Attributes.Emplace(TEXT("level_name"), TEXT("Stage_01"));
    Attributes.Emplace(TEXT("difficulty"), TEXT("Hard"));
    Analytics->RecordEvent(TEXT("level_completed"), Attributes);

    // 设置用户 ID
    Analytics->SetUserID(TEXT("player_12345"));
}
```

### 进阶用法

使用 Adjust 特有的便捷方法记录货币购买和物品购买事件：

```cpp
// 来源: Private/AndroidAdjustProvider.h

TSharedPtr<IAnalyticsProvider> Analytics = FAnalytics::Get().GetDefaultConfiguredProvider();

if (Analytics.IsValid())
{
    // 记录游戏内货币购买（玩家用真金白银买了游戏币）
    Analytics->RecordCurrencyPurchase(
        TEXT("Gold"),           // 游戏货币类型
        1000,                   // 游戏货币数量
        TEXT("USD"),            // 真实货币类型
        4.99f,                  // 真实货币花费
        TEXT("GooglePlay")      // 支付提供商
    );

    // 记录物品购买（玩家用游戏币买了道具）
    Analytics->RecordItemPurchase(
        TEXT("sword_001"),      // 物品 ID
        TEXT("Gold"),           // 货币类型
        500,                    // 单价
        1                       // 数量
    );

    // 记录进度事件
    Analytics->RecordProgress(
        TEXT("Level"),          // 进度类型
        TEXT("World_01"),       // 进度层级
        {}                      // 额外属性
    );

    // 结束会话
    Analytics->EndSession();
}
```

## Demo 示例

一个完整的最小集成示例，在游戏模式中自动启动 Adjust 会话：

```cpp
// MyGameMode.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable)
    void TrackCustomEvent(const FString& EventName);
};
```

```cpp
// MyGameMode.cpp
#include "MyGameMode.h"
#include "IAnalyticsProvider.h"
#include "AnalyticsEventAttribute.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 获取 Adjust Provider 并启动会话
    TSharedPtr<IAnalyticsProvider> Analytics = FAnalytics::Get().GetDefaultConfiguredProvider();
    if (Analytics.IsValid())
    {
        Analytics->StartSession();
    }
}

void AMyGameMode::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    TSharedPtr<IAnalyticsProvider> Analytics = FAnalytics::Get().GetDefaultConfiguredProvider();
    if (Analytics.IsValid())
    {
        Analytics->EndSession();
    }

    Super::EndPlay(EndPlayReason);
}

void AMyGameMode::TrackCustomEvent(const FString& EventName)
{
    TSharedPtr<IAnalyticsProvider> Analytics = FAnalytics::Get().GetDefaultConfiguredProvider();
    if (Analytics.IsValid())
    {
        TArray<FAnalyticsEventAttribute> Attrs;
        Attrs.Emplace(TEXT("source"), TEXT("gameplay"));
        Analytics->RecordEvent(EventName, Attrs);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Analytics 等）。

插件的三个模块之间无相互依赖：
- **AdjustEditor**：编辑器工具，处理插件配置 UI
- **AndroidAdjust**：Android 平台原生桥接（依赖 Adjust Android SDK 的 JNI）
- **IOSAdjust**：iOS 平台原生桥接（依赖 Adjust iOS SDK 的 Objective-C++ 接口）

使用者只需依赖目标平台对应的 Runtime 模块（`AndroidAdjust` 或 `IOSAdjust`），加上标准的引擎分析模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 格式 |
| 2026-01-27 | `113268fe` | Fixed include casing mismatch when compiling ios with case sensitive on | 修复 iOS 大小写敏感编译时的头文件路径问题 |
| 2026-01-14 | `1a097717` | Fix IOS CIS Issues. | 修复 iOS 持续集成构建问题 |
| 2025-04-04 | `dce44a87` | Proper fix for analytics check() being replaced with a log. Moved definition of the logging function | 修复分析模块 check() 被替换为日志的问题 |
| 2024-02-06 | `c02789b4` | [Backout] - CL31042395 | 回退变更 CL31042395 |

### 维护评价

**维护状态：维护中，但无功能性更新**

- 插件已存在约 9 年（2017年创建），属于**老古董**级别
- 最近的 commit（2026-04-14）是全引擎范围的 `UE_LOG` 迁移，**不是插件专属的功能更新**
- 2024-2026 年的 commit 全部是编译修复和引擎升级适配，**无任何新功能或 API 变更**
- 插件本身结构极其简单（约 9 个源文件），作为第三方 SDK 薄封装，功能已稳定
- `EnabledByDefault=false` 表明这不是通用功能，仅在明确需要 Adjust 时才启用
- 仅支持 Android 和 iOS 两个移动平台，不支持桌面平台

**建议**：插件可用但功能受限于 Adjust SDK 的基础事件上报。如果需要更复杂的 Adjust 功能（如深度链接、受众细分等），可能需要自行扩展。由于 Adjust SDK 本身会定期更新，建议检查 UE5 内置的 Adjust SDK 版本是否为最新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/Adjust)
- [官方文档](https://docs.unrealengine.com/latest/INT/Gameplay/Analytics/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/Adjust)（未发现独立测试文件）