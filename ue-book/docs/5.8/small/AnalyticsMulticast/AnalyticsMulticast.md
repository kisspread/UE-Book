# Multicast Analytics Provider

> Forwards analytics API calls to a list of analytics providers to log data to multiple services at once

| 属性 | 值 |
|---|---|
| 中文名 | 多播分析提供者 |
| 分类 | Analytics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AnalyticsMulticast` (Runtime), `AnalyticsMulticastEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2015-04-21 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/AnalyticsMulticast) | |

## 用途

当你的项目需要同时向多个分析服务（如自建后端 + 第三方平台）上报事件时，逐一调用各个 Provider 既繁琐又容易遗漏。AnalyticsMulticast 提供了一个**多播（Multicast）代理模式**：你只需调用一次 `RecordEvent`，它会自动将事件分发给所有已配置的子 Provider。

核心实现是一个 `FAnalyticsMulticast` 类，它本身实现了 `IAnalyticsProviderModule` 接口。启动时通过逗号分隔的 Provider 模块名列表加载各个子模块，然后为每个子模块创建独立的 `IAnalyticsProvider` 实例。后续所有 `IAnalyticsProvider` 接口方法调用都会被转发到全部子 Provider。

**注意**：该插件默认未启用（`EnabledByDefault=false`），需要在项目的 `.uproject` 或编辑器中手动开启。

## 使用场景

- 你的游戏需要同时将分析数据发送到 **自建分析后端** 和 **第三方服务**（如 GameAnalytics、Firebase 等）
- 你想在不修改业务代码的前提下，灵活增删分析上报目标
- 你需要一个统一的分析入口，避免业务层直接耦合多个 Provider

## 蓝图用法

该插件**不暴露任何蓝图节点**。`FAnalyticsMulticast` 的所有方法均为 C++ 级别的 `virtual` 函数，无 `UFUNCTION(BlueprintCallable)` 宏。如需在蓝图中使用分析功能，应使用 UE 内置的 `Record Event With Attributes` 等标准分析节点，配合引擎的 `FAnalyticsProviderET` 系统。

## C++ 用法

### 头文件引入

```cpp
#include "AnalyticsMulticast.h"
```

### 基本用法：通过配置创建多播 Provider

通过 `Config` 结构体指定需要多播的 Provider 模块列表，然后调用 `CreateAnalyticsProvider` 创建实例。

```cpp
// 来源: Engine/Plugins/Runtime/Analytics/AnalyticsMulticast/Source/AnalyticsMulticast/Public/AnalyticsMulticast.h

#include "AnalyticsMulticast.h"
#include "Interfaces/IAnalyticsProvider.h"

void UMyClass::InitAnalytics()
{
    // 获取 AnalyticsMulticast 模块实例
    FAnalyticsMulticast& MulticastModule = FAnalyticsMulticast::Get();

    // 配置：指定要多播到哪些 Provider 模块（逗号分隔）
    FAnalyticsMulticast::Config MulticastConfig;
    MulticastConfig.ProviderModuleNames = TEXT("MyCustomAnalytics,AnalyticsET");

    // 定义配置回调：每个子 Provider 会通过此委托获取自己的配置值
    FAnalyticsProviderConfigurationDelegate ConfigDelegate;
    ConfigDelegate.BindLambda([](const FString& Key, const FString& DefaultValue) -> FString
    {
        if (Key == TEXT("APIKey"))
        {
            return TEXT("my-api-key-12345");
        }
        return DefaultValue;
    });

    // 创建多播 Provider
    TSharedPtr<IAnalyticsProvider> Provider = MulticastModule.CreateAnalyticsProvider(MulticastConfig, ConfigDelegate);

    if (Provider.IsValid())
    {
        // 后续使用方式与普通 Provider 完全一致
        // 事件会自动多播到所有已配置的子 Provider
        Provider->StartSession();
        Provider->RecordEvent(TEXT("GameStart"), { {TEXT("Level"), TEXT("MainMenu")} });
    }
}
```

### 进阶用法：使用标准模块加载接口

`FAnalyticsMulticast` 也实现了 `IAnalyticsProviderModule` 接口，可以通过标准的模块加载方式创建 Provider。此时配置键名通过 `Config::GetKeyNameForProviderModuleNames()` 获取。

```cpp
// 来源: Engine/Plugins/Runtime/Analytics/AnalyticsMulticast/Source/AnalyticsMulticast/Public/AnalyticsMulticast.h

#include "AnalyticsMulticast.h"

void UMyClass::InitAnalyticsViaModule()
{
    // 通过模块接口创建（使用标准的 FAnalyticsProviderConfigurationDelegate）
    FAnalyticsProviderConfigurationDelegate ConfigDelegate;
    ConfigDelegate.BindLambda([](const FString& Key, const FString& DefaultValue) -> FString
    {
        // Multicast 模块自身只读取 ProviderModuleNames 键
        if (Key == FAnalyticsMulticast::Config::GetKeyNameForProviderModuleNames())
        {
            return TEXT("AnalyticsET,MyAnalyticsProvider");
        }
        // 其他键透传给各子 Provider
        if (Key == TEXT("APIKey"))
        {
            return TEXT("my-key");
        }
        return DefaultValue;
    });

    // 使用 IAnalyticsProviderModule 接口创建
    TSharedPtr<IAnalyticsProvider> Provider =
        FAnalyticsMulticast::Get().CreateAnalyticsProvider(ConfigDelegate);

    if (Provider.IsValid())
    {
        Provider->StartSession();
    }
}
```

## 模块依赖

该插件的核心依赖非常少。根据头文件中使用的 `IAnalyticsProviderModule` 和 `IAnalyticsProvider` 接口推断：

| 模块 | 用途 |
|---|---|
| `Analytics` | 提供 `IAnalyticsProvider` / `IAnalyticsProviderModule` 接口定义 |

无其他特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 日志宏迁移到新的 UE_LOGF 格式 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码编译错误 |
| 2024-02-06 | `c02789b4` | [Backout] - CL31042395 | 回退之前的变更 CL31042395 |
| 2024-01-31 | `6bfbcbac` | Move the initial declaration of ::BlockUntilFlushed from IAnalyticsProviderET to it's parent class IAnalyticsProvider | 将 BlockUntilFlushed 声明从子类移至父类接口 |
| 2023-12-08 | `ae0e1db1` | Pushed Set/GetDefaultAttributes into IAnalyticsProvider | 将 Set/GetDefaultAttributes 下推到 IAnalyticsProvider 基类接口 |

### 维护评价

AnalyticsMulticast 是一个**稳定但不活跃**的基础设施插件。

- **年龄**：已存在约 11 年，属于老资历插件
- **更新频率**：近几年的更新全部是**编译修复**和**接口重构跟随**（如 UE_LOG 迁移、父类接口变动），没有任何功能性新增
- **活跃度**：依赖母模块 `Analytics` 的接口变动被动维护，自身代码极少改动
- **功能成熟度**：功能非常简单（多播代理模式），已经完全成熟，不需要新功能
- **推荐度**：✅ **推荐使用**。如果你需要多 Provider 分发，这是官方推荐的方案。代码量极小（仅 5 个源文件），稳定可靠，几乎不会有 bug。唯一注意点是默认未启用，需要手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/AnalyticsMulticast)
- [官方文档](https://docs.unrealengine.com/latest/INT/Gameplay/Analytics/index.html)
- [公共头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Runtime/Analytics/AnalyticsMulticast/Source/AnalyticsMulticast/Public/AnalyticsMulticast.h)