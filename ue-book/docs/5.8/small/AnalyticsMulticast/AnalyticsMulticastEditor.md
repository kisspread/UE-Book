# Multicast Analytics Provider

> Forwards analytics API calls to a list of analytics providers to log data to multiple services at once

| 属性 | 值 |
|---|---|
| 中文名 | 多路分析提供商 |
| 分类 | Analytics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AnalyticsMulticast` (Runtime), `AnalyticsMulticastEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2015-04-21 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/AnalyticsMulticast) | |

## 用途

AnalyticsMulticast 插件的核心功能是**聚合与分发**。它作为一个“调度中心”，允许开发者将引擎的分析事件（如用户行为、性能数据）同时发送给多个不同的分析服务提供商（例如 Firebase、自研平台、第三方分析SDK等）。

**解决的问题**：在没有此插件的情况下，如果一个项目需要将数据上报到多个分析平台，开发者可能需要为每个平台单独集成其 SDK 并编写调用代码，导致代码重复、配置复杂且难以维护。此插件通过一个统一的配置入口和转发机制，简化了这一过程。开发者只需配置一个“多路提供商”，并在其中列出所有希望接收数据的真实提供商名称，引擎便会自动将分析调用转发给它们。

## 使用场景

- **多平台数据上报**：你的游戏同时需要向 Epic 的分析服务和内部 BI 平台发送数据，使用此插件可以避免在游戏代码中嵌入两套调用逻辑。
- **开发与测试环境分离**：你可以在 `Development` 配置中将数据发送到调试用的分析服务，而在 `Release` 配置中发送到正式的生产分析服务，通过配置轻松切换。
- **集成多个第三方 SDK**：项目集成了多个用于不同目的（如用户行为追踪、崩溃日志、广告效果）的分析 SDK，通过此插件进行统一管理。

## 蓝图用法

此插件主要通过编辑器设置进行配置，而非提供运行时蓝图节点。其配置界面在项目设置中。

### 核心配置

配置位于 **项目设置 (Project Settings) -> 插件 (Plugins) -> Multicast Analytics** 下的 `UAnalyticsMulticastSettings` 类。

| 属性 | 说明 |
|---|---|
| `Release Providers` | 用于“发行版”构建配置的分析提供商列表。 |
| `Debug Providers` | 用于“调试”构建配置的分析提供商列表。 |
| `Test Providers` | 用于“测试”构建配置的分析提供商列表。 |
| `Development Providers` | 用于“开发”构建配置的分析提供商列表。 |

**配置示例**：
1.  打开项目设置，导航到上述位置。
2.  在对应的构建配置（例如 `Development Providers`）的文本框中，输入你希望转发数据的分析提供商名称，用逗号分隔。
    例如：`MyAnalyticsProvider, FirebaseProvider`
3.  保存设置。游戏在对应构建配置下运行时，分析事件将自动转发给列表中的所有提供商。

## C++ 用法

此插件的使用更多体现在配置层面，其内部转发机制在引擎分析系统中自动完成。C++ 中主要涉及对其设置类 `UAnalyticsMulticastSettings` 的操作或查询。

### 头文件引入

```cpp
// 引入分析多路配置类
#include "AnalyticsMulticastSettings.h"
```

### 基本用法

通常，开发者不需要直接在游戏逻辑中调用此插件的 API。它的主要作用是通过配置来扩展引擎的分析系统。

以下示例展示了如何以编程方式访问当前的多路分析设置（尽管通常更推荐通过编辑器 UI 配置）：

```cpp
// 示例：获取多路分析设置并读取开发环境下的提供商列表
// 注意：这通常用于编辑器工具或调试，运行时调用可能无意义
#include "AnalyticsMulticastSettings.h"
#include "Analytics.h"

void ExampleAccessSettings()
{
    // 获取项目设置对象
    const UAnalyticsMulticastSettings* Settings = GetDefault<UAnalyticsMulticastSettings>();
    if (Settings)
    {
        UE_LOG(LogTemp, Log, TEXT("当前配置的开发环境分析提供商数量: %d"), Settings->DevelopmentMulticastProviders.Num());
        for (const FString& ProviderName : Settings->DevelopmentMulticastProviders)
        {
            UE_LOG(LogTemp, Log, TEXT(" - 提供商: %s"), *ProviderName);
        }
    }
}
```

**说明**：`GetDefault<UAnalyticsMulticastSettings>()` 用于获取该 UClass 的默认对象（CDO），从而读取其当前配置的属性值。

### 进阶用法

在引擎层面，当调用 `FAnalytics::Get().GetDefaultConfiguredProvider()` 或类似的接口获取分析提供商时，如果项目启用了 AnalyticsMulticast 插件，引擎会返回一个多路转发的提供商实例。该实例内部根据当前的构建配置（Development, Shipping 等），从对应的列表中找到所有已注册的提供商名称，并将后续的 `RecordEvent`, `FlushEvents` 等调用转发给它们。

## Demo 示例

以下是一个最小化的示例，展示如何在自己的分析事件记录代码中，确保它能被多路系统所捕获。实际的分析事件记录使用标准的引擎分析接口。

**MyGameAnalytics.h**
```cpp
#pragma once

class FMyGameAnalytics
{
public:
    // 初始化分析系统
    static void Initialize();

    // 记录一个自定义游戏事件
    static void RecordGameEvent(const FString& EventName, const TMap<FString, FString>& Attributes);
};
```

**MyGameAnalytics.cpp**
```cpp
#include "MyGameAnalytics.h"
#include "AnalyticsEventAttribute.h"
#include "Interfaces/IAnalyticsProvider.h"
#include "Analytics.h"

void FMyGameAnalytics::Initialize()
{
    // 标准的分析初始化。如果配置了AnalyticsMulticast，此处获取的将是多路提供商。
    IAnalyticsProviderPtr AnalyticsProvider = FAnalytics::Get().GetDefaultConfiguredProvider();
    if (AnalyticsProvider.IsValid())
    {
        AnalyticsProvider->StartSession();
        UE_LOG(LogTemp, Log, TEXT("分析会话已启动 (可能已由多路提供商分发)。"));
    }
}

void FMyGameAnalytics::RecordGameEvent(const FString& EventName, const TMap<FString, FString>& Attributes)
{
    IAnalyticsProviderPtr AnalyticsProvider = FAnalytics::Get().GetDefaultConfiguredProvider();
    if (AnalyticsProvider.IsValid())
    {
        // 将 TMap 转换为 FAnalyticsEventAttribute 数组
        TArray<FAnalyticsEventAttribute> EventAttributes;
        for (const auto& Attr : Attributes)
        {
            EventAttributes.Add(FAnalyticsEventAttribute(Attr.Key, Attr.Value));
        }
        // 此调用会被多路提供商透明地转发给所有配置的后端服务
        AnalyticsProvider->RecordEvent(EventName, EventAttributes);
    }
}
```

## 模块依赖

AnalyticsMulticast 插件的运行依赖于引擎的分析框架。使用者（即游戏模块）通常不需要直接依赖此插件模块，但需要确保正确配置并启用了此插件。

| 模块 | 用途 |
|---|---|
| `Analytics` | 引擎核心分析接口和框架，是此插件工作的基础。 |
| `AnalyticsMulticastEditor` | 提供编辑器内的设置UI (`UAnalyticsMulticastSettings`)。运行时不需要。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 `UE_LOG` 迁移至新式 `UE_LOGF` 宏。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复代码中存在的不可达代码错误。 |
| 2024-02-06 | `c02789b4` | [Backout] - CL31042395 | 回滚了 CL31042395 提交的更改。 |
| 2024-01-31 | `6bfbcbac` | Move the initial declaration of ::BlockUntilFlushed from IAnalyticsProviderET to it's parent class I | 将 `BlockUntilFlushed` 函数的初始声明从子接口移到父接口。 |
| 2023-12-08 | `ae0e1db1` | Pushed Set/GetDefaultAttributes into IAnalyticsProvider | 将 `SetDefaultAttributes` 和 `GetDefaultAttributes` 函数提升到 `IAnalyticsProvider` 父接口中。 |

### 维护评价

**维护状态：不活跃**

该插件创建于 **2015 年**，是一个相当古老的插件。从 Git 历史来看，近年来的提交主要是**维护性更新**（如修复编译错误、日志宏迁移、代码结构重构以适应父类接口变化），而非新功能开发或重大改进。

**优点**：
1.  **功能稳定**：核心的“多路转发”逻辑简单且成熟，能够长期稳定工作。
2.  **架构清晰**：作为分析系统的一个透明中间层，与引擎集成良好。

**风险与限制**：
1.  **默认未启用**：`EnabledByDefault=false` 表明 Epic 可能不认为这是绝大多数项目的必需组件。
2.  **维护投入低**：实质性功能更新停留在 2023 年或更早。未来的引擎版本若对分析接口进行重大重构，此插件可能无法及时跟进。
3.  **功能相对单一**：仅提供配置级别的分发，不包含高级路由、过滤或数据转换功能。

**推荐使用场景**：
如果你有明确的、需要同时向多个分析后端发送原始数据的需求，并且这些后端都已注册为引擎的 `IAnalyticsProvider`，那么此插件是**值得使用且可靠的**。它能有效减少样板代码。

**不推荐场景**：
如果需求复杂，需要在发送前对事件进行过滤、合并或富化处理，那么可能需要更复杂的自定义解决方案或第三方中间件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/AnalyticsMulticast)
- [官方文档](https://docs.unrealengine.com/latest/INT/Gameplay/Analytics/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/AnalyticsMulticast/Tests) (如果存在)