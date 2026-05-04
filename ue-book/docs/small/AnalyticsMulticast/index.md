# Multicast Analytics Provider

> Forwards analytics API calls to a list of analytics providers to log data to multiple services at once

| 属性 | 值 |
|---|---|
| 分类 | Analytics |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AnalyticsMulticastEditor (Editor), AnalyticsMulticast (Runtime) |
| 创建时间 | 2015-04-21 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Analytics/AnalyticsMulticast) | |

## 用途

AnalyticsMulticast 是 UE5 Analytics 系统中的**多路广播（Multicast）代理**。它本身不采集或存储任何分析数据，而是充当一个**代理层**：将所有 Analytics API 调用透明地转发给多个底层 Analytics Provider。

核心价值在于：你只需要对接一个 Analytics Provider（Multicast），就能同时把数据发送到多个后端服务（如 Epic 的 Studio Telemetry、FileLogging、Adjust 等）。这避免了在游戏代码中重复写多套 Analytics 调用的逻辑。

内部实现是 `FAnalyticsProviderMulticast`，它持有 `TArray<TSharedPtr<IAnalyticsProvider>> Providers` 列表，每个方法（`RecordEvent`、`StartSession`、`EndSession` 等）都遍历所有子 Provider 并逐一调用。

## 使用场景

- 你需要同时把玩家行为数据发送到**多个**分析后端（例如 Studio Telemetry + 自建日志系统）→ 用 AnalyticsMulticast 作为统一入口
- 你在 A/B 测试不同 Analytics 服务，想并行发送数据进行对比 → 配置 Multicast 同时包含两个 Provider
- 你想把 `RecordEvent`、`RecordItemPurchase` 等调用只写一遍，但需要多端接收 → Multicast 帮你做分发

## 蓝图用法

AnalyticsMulticast 没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 接口。它是一个纯 C++ Runtime 模块，通过 UE 的 Analytics 框架在底层工作。蓝图中无法直接调用 Multicast 的方法。

如果需要在蓝图中使用 Analytics 功能，请使用 `AnalyticsBlueprintLibrary` 插件。

## C++ 用法

### 头文件引入

```cpp
#include "AnalyticsMulticast.h"
```

### 基本用法

AnalyticsMulticast 通过 UE 的 Analytics Provider 配置机制工作。在 `DefaultEngine.ini` 中配置使用：

```ini
[Analytics]
ProviderModuleNames=AnalyticsMulticast

[AnalyticsMulticast]
ProviderModuleNames=FileLogging,AnalyticsLog
```

第一行将 Multicast 设为默认 Analytics Provider，第二行告诉 Multicast 把事件转发给哪些子 Provider。

也可以通过代码创建：

```cpp
#include "AnalyticsMulticast.h"
#include "Analytics.h"

// 获取 Multicast 模块
FAnalyticsMulticast& MulticastModule = FAnalyticsMulticast::Get();

// 通过配置委托创建 Provider
FAnalyticsProviderConfigurationDelegate ConfigDelegate;
ConfigDelegate.BindLambda([](const FString& Key, const FString& DefaultValue) -> FString
{
    if (Key == TEXT("ProviderModuleNames"))
    {
        return TEXT("FileLogging,AnalyticsLog");
    }
    return DefaultValue;
});

TSharedPtr<IAnalyticsProvider> Provider = MulticastModule.CreateAnalyticsProvider(ConfigDelegate);
```

### 进阶用法

#### 直接通过 Config 结构创建

```cpp
#include "AnalyticsMulticast.h"

FAnalyticsMulticast::Config MulticastConfig;
MulticastConfig.ProviderModuleNames = TEXT("FileLogging,AnalyticsLog");

FAnalyticsProviderConfigurationDelegate ConfigDelegate;
// ... 绑定配置委托 ...

FAnalyticsMulticast& Module = FAnalyticsMulticast::Get();
TSharedPtr<IAnalyticsProvider> Provider = Module.CreateAnalyticsProvider(MulticastConfig, ConfigDelegate);
```

#### Session ID 格式

Multicast Provider 的 `GetSessionID()` 返回一个特殊格式的复合字符串，编码了所有子 Provider 的 Session ID：

```
ModuleName1@@SessionID1##ModuleName2@@SessionID2
```

- `@@` 分隔模块名和 Session ID
- `##` 分隔不同 Provider 的记录

`SetSessionID()` 能解析这个格式并将各 Session ID 分发到对应的子 Provider。

#### 通过编辑器 Settings 配置

Editor 模块提供了 `UAnalyticsMulticastSettings`，可以在 **Project Settings → Analytics → Multicast** 中配置不同构建类型的 Provider 列表：

- **Release Providers** — 发布版本使用的 Provider 列表
- **Debug Providers** — 调试版本使用的 Provider 列表
- **Test Providers** — 测试版本使用的 Provider 列表
- **Development Providers** — 开发版本使用的 Provider 列表

如果某个构建类型未配置，会回退到 Release 配置的值。

## Demo 示例

### 最小可编译示例

**MyAnalyticsSubsystem.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Interfaces/IAnalyticsProvider.h"
#include "MyAnalyticsSubsystem.generated.h"

UCLASS()
class UMyAnalyticsSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    void TrackPlayerAction(const FString& ActionName);

private:
    TSharedPtr<IAnalyticsProvider> AnalyticsProvider;
};
```

**MyAnalyticsSubsystem.cpp**

```cpp
#include "MyAnalyticsSubsystem.h"
#include "Analytics.h"
#include "AnalyticsMulticast.h"

void UMyAnalyticsSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 获取当前全局 Analytics Provider（如果是 Multicast，会自动广播）
    AnalyticsProvider = FAnalytics::Get().GetDefaultConfiguredProvider();
    if (AnalyticsProvider.IsValid())
    {
        AnalyticsProvider->StartSession();
    }
}

void UMyAnalyticsSubsystem::Deinitialize()
{
    if (AnalyticsProvider.IsValid())
    {
        AnalyticsProvider->EndSession();
        AnalyticsProvider.Reset();
    }
    Super::Deinitialize();
}

void UMyAnalyticsSubsystem::TrackPlayerAction(const FString& ActionName)
{
    if (AnalyticsProvider.IsValid())
    {
        // 这条事件会被 Multicast 自动转发到所有配置的子 Provider
        AnalyticsProvider->RecordEvent(ActionName, {});
    }
}
```

**Build.cs 依赖**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "Analytics"
});
```

> 注意：你的项目模块不需要直接依赖 `AnalyticsMulticast` 模块。它通过 UE 的模块动态加载机制和 `IAnalyticsProviderModule` 接口工作。只需在 ini 中配置即可。

## 模块依赖

### AnalyticsMulticast（Runtime）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、内存管理 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Analytics` | Analytics Provider 接口定义 |

### AnalyticsMulticastEditor（Editor）

| 模块 | 用途 |
|---|---|
| `Analytics` | Analytics 配置框架 |
| `AnalyticsVisualEditing` | Analytics 设置 UI |
| `UnrealEd` | 编辑器框架 |
| `PropertyEditor` | 属性面板（Project Settings 中的配置界面） |
| `DeveloperSettings` | 开发者设置基类 |
| `Slate` / `SlateCore` | UI 框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-12-08 | `ae0e1db` | Pushed Set/GetDefaultAttributes into IAnalyticsProvider; added Dynamic Analytics Provider Module Loading | 重大更新：实现了 `SetDefaultEventAttributes` 接口，并支持动态加载 Analytics Provider 模块 |
| 2023-05-16 | `381f77a` | Optimized include module name dependencies | IWYU 编译优化，减少头文件依赖 |
| 2023-01-16 | `bbc37aa` | Another batch iwyu updates | IWYU 批量更新 |

### 维护评价

- **创建时间**：2015 年 4 月，已有 11 年历史
- **最近更新**：最后一次实质性更新在 2023 年 12 月（`SetDefaultEventAttributes` 支持），之后无新功能提交
- **维护状态**：**维护不活跃** — 代码非常稳定但已超过 1 年没有更新
- **已知限制**：
  - 没有蓝图接口，纯 C++ 使用
  - 没有测试用例（在 plugin 目录和 Engine/Tests 下均未找到）
  - Editor 模块目录名有拼写错误（`AnaltyicsMulticastEditor` 而非 `AnalyticsMulticastEditor`），但模块名本身正确
  - Singleton 模式：`FAnalyticsProviderMulticast` 只维护一个全局实例，不支持同时存在多个 Multicast Provider
- **是否推荐**：如果需要多路广播 Analytics 事件，这是 UE 官方提供的唯一方案，功能完整且稳定。但需注意它不适合需要多个独立 Multicast 实例的场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Analytics/AnalyticsMulticast)
- [官方文档](https://docs.unrealengine.com/latest/INT/Gameplay/Analytics/index.html)
- 测试用例：无（plugin 内及 Engine/Tests 下均未找到相关测试）
