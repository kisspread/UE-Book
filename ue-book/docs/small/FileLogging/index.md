# File Logging Analytics Provider

> Writes analytic API calls to local disk for debugging or local use

| 属性 | 值 |
|---|---|
| 分类 | Analytics |
| 默认启用 | ❌ 否 |
| 包含内容 | 否 |
| 模块 | FileLogging (Runtime, LoadingPhase=PreDefault) |
| 创建时间 | 2014-09-12 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Analytics/FileLogging) | |

## 用途

FileLogging 是 UE Analytics 系统的一个**本地文件 Provider**。它实现了 `IAnalyticsProvider` 接口，将所有分析事件写入本地磁盘的 JSON 文件，而非发送到远程服务器。

这个 plugin 解决的核心问题是：**在开发和调试阶段，你需要一个零配置、零网络依赖的方式来查看和验证游戏的分析事件数据**。你不需要注册任何第三方分析服务（如 Firebase、Mixpanel），只需启用这个 plugin，所有 `RecordEvent` 调用就会自动落盘为 JSON 文件。

与远程分析服务 Provider 的对比：

| 特性 | FileLogging | 远程 Provider（如 Adjust） |
|---|---|---|
| 网络依赖 | 无 | 需要 |
| 配置复杂度 | 几乎为零 | 需要 API Key 等 |
| 适用场景 | 开发/调试 | 生产环境 |
| 数据格式 | 本地 JSON 文件 | 远程平台 |

## 使用场景

- 你在开发阶段想验证 Analytics 事件是否正确触发 → 启用 FileLogging，运行游戏后检查 `Saved/Analytics/` 目录
- 你在做自动化测试，需要检查分析事件数据 → FileLogging 的 JSON 输出可以直接被脚本解析
- 你在教学或演示 Analytics 系统，不想配置真实后端 → FileLogging 是最简单的 Provider
- 你用 AnalyticsMulticast 同时向多个 Provider 发送事件，想保留一份本地备份 → FileLogging 作为其中一个

## 蓝图用法

此 plugin 本身**不包含任何蓝图节点**。它是一个底层 Provider 实现，通过 UE 的 Analytics 系统间接使用。

如果你需要在蓝图中调用分析事件，需要同时启用 **AnalyticsBlueprintLibrary** plugin，然后通过 `Start Session` / `Record Event` 等节点操作。当 FileLogging 被配置为默认 Provider 时，这些蓝图节点的事件会自动写入本地文件。

### 蓝图使用示例

在蓝图中使用 Analytics Blueprint Library（需额外启用 AnalyticsBlueprintLibrary 插件）：

1. **BeginPlay** → 调用 `Start Session`（使用 Analytics Provider 引用）
2. 在游戏逻辑中 → 调用 `Record Event with Attributes`，传入事件名和属性数组
3. **EndPlay** → 调用 `End Session`

这些调用的数据会被 FileLogging Provider 写入磁盘。

## C++ 用法

### 头文件引入

```cpp
#include "Analytics.h"
#include "Interfaces/IAnalyticsProvider.h"
#include "AnalyticsEventAttribute.h"
```

### 基本用法

FileLogging 作为 Analytics Provider，通过 `FAnalytics` 模块的工厂方法创建。最简单的方式是使用默认配置：

```cpp
// 获取默认配置的 Provider（会读取 Engine.ini 中的 [Analytics] 配置）
TSharedPtr<IAnalyticsProvider> AnalyticsProvider = FAnalytics::Get().GetDefaultConfiguredProvider();

if (AnalyticsProvider.IsValid())
{
    // 开始分析会话
    AnalyticsProvider->StartSession();

    // 记录一个事件，带自定义属性
    AnalyticsProvider->RecordEvent(TEXT("PlayerLogin"),
        MakeAnalyticsEventAttributeArray(
            TEXT("Platform"), TEXT("Windows"),
            TEXT("BuildVersion"), TEXT("1.0.3")
        ));

    // 结束会话（会关闭文件）
    AnalyticsProvider->EndSession();
}
```

> 来源: `Engine/Source/Runtime/Analytics/Analytics/Public/Analytics.h`

### 指定 Provider 模块名

你也可以显式指定使用 FileLogging Provider，而不依赖 INI 配置：

```cpp
// 显式创建 FileLogging Provider
TSharedPtr<IAnalyticsProvider> Provider = FAnalytics::Get().CreateAnalyticsProvider(
    FName(TEXT("FileLogging")),
    FAnalyticsProviderConfigurationDelegate()
);

if (Provider.IsValid())
{
    Provider->StartSession();

    Provider->RecordEvent(TEXT("LevelCompleted"),
        MakeAnalyticsEventAttributeArray(
            TEXT("LevelName"), TEXT("Forest_01"),
            TEXT("TimeSeconds"), TEXT("120.5"),
            TEXT("Score"), TEXT("9500")
        ));

    Provider->EndSession();
}
```

> 来源: `Engine/Source/Runtime/Analytics/Analytics/Private/Analytics.cpp`

### 记录特定类型的事件

除了通用的 `RecordEvent`，Provider 还支持特定业务场景的事件记录方法：

```cpp
// 记录物品购买
Provider->RecordItemPurchase(TEXT("Sword_001"), TEXT("Gold"), 500, 1);

// 记录货币购买（真实货币→游戏货币）
Provider->RecordCurrencyPurchase(TEXT("Gem"), 100, TEXT("USD"), 4.99f, TEXT("Steam"));

// 记录货币发放
Provider->RecordCurrencyGiven(TEXT("Coin"), 1000);

// 记录错误
Provider->RecordError(TEXT("ConnectionTimeout"),
    MakeAnalyticsEventAttributeArray(TEXT("RetryCount"), TEXT("3")));

// 记录进度
Provider->RecordProgress(TEXT("Achievement"), TEXT("FirstBlood"),
    MakeAnalyticsEventAttributeArray(TEXT("EnemyType"), TEXT("Goblin")));
```

> 来源: `Engine/Plugins/Runtime/Analytics/FileLogging/Source/FileLogging/Private/FileLoggingProvider.h`

### 设置用户和会话信息

```cpp
// 在 StartSession 之前设置用户 ID（会话开始后不可修改）
Provider->SetUserID(TEXT("Player_42"));

// 设置人口统计信息
Provider->SetAge(25);
Provider->SetGender(TEXT("Male"));
Provider->SetLocation(TEXT("Tokyo, JP"));
Provider->SetBuildInfo(TEXT("v1.2.3-Release"));
```

> 来源: `Engine/Plugins/Runtime/Analytics/FileLogging/Source/FileLogging/Private/FileLogging.cpp`

### 默认事件属性

你可以设置默认属性，这些属性会自动附加到每个事件中：

```cpp
TArray<FAnalyticsEventAttribute> DefaultAttrs;
DefaultAttrs.Add(FAnalyticsEventAttribute(TEXT("GameVersion"), TEXT("1.0")));
DefaultAttrs.Add(FAnalyticsEventAttribute(TEXT("Environment"), TEXT("Staging")));
Provider->SetDefaultEventAttributes(MoveTemp(DefaultAttrs));

// 之后记录的事件会自动包含上面的默认属性
Provider->RecordEvent(TEXT("CustomEvent"),
    MakeAnalyticsEventAttributeArray(TEXT("ExtraKey"), TEXT("ExtraValue")));
```

## 输出文件格式

FileLogging 将事件写入 `{项目目录}/Saved/Analytics/{sessionId}.analytics` 文件。

文件名格式：`{UserId}-{时间戳}.analytics`

输出内容为 JSON 格式：

```json
{
	"sessionId" : "User123-2024.01.15-14.30.22",
	"userId" : "User123",
	"buildInfo" : "v1.0.0",
	"age" : 25,
	"gender" : "Male",
	"events" : [
		{
			"eventName" : "PlayerLogin",
			"attributes" : [
				{ "name" : "Platform", "value" : "Windows" },
				{ "name" : "BuildVersion", "value" : "1.0.3" }
			]
		},
		{
			"eventType" : "ItemPurchase",
			"itemId" : "Sword_001",
			"itemQuantity" : 1,
			"attributes" : [
				{ "name" : "currency", "value" : "Gold" },
				{ "name" : "perItemCost", "value" : "500" }
			]
		}
	]
}
```

> 来源: `Engine/Plugins/Runtime/Analytics/FileLogging/Source/FileLogging/Private/FileLogging.cpp` — `StartSession` 和 `RecordEvent` 方法

## INI 配置

要将 FileLogging 设为默认 Analytics Provider，在项目的 `Engine.ini`（或 `DefaultEngine.ini`）中添加：

```ini
[Analytics]
ProviderModuleName=FileLogging
```

不同构建类型使用不同的 INI Section：

| 构建类型 | INI Section |
|---|---|
| Development | `[AnalyticsDevelopment]` |
| Debug | `[AnalyticsDebug]` |
| Test | `[AnalyticsTest]` |
| Release | `[Analytics]` |

> 来源: `Engine/Source/Runtime/Analytics/Analytics/Public/Analytics.h` — `ConfigFromIni::SetSectionNameByBuildType`

## Demo 示例

一个最小的 C++ 示例，在 GameInstance 中使用 FileLogging 记录分析事件：

### MyGame.Build.cs

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "Analytics"  // 需要依赖 Analytics 模块
});
```

### MyGameInstance.h

```cpp
#pragma once

#include "Engine/GameInstance.h"
#include "Interfaces/IAnalyticsProvider.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
    virtual void Shutdown() override;

private:
    TSharedPtr<IAnalyticsProvider> AnalyticsProvider;
};
```

### MyGameInstance.cpp

```cpp
#include "MyGameInstance.h"
#include "Analytics.h"
#include "AnalyticsEventAttribute.h"

void UMyGameInstance::Init()
{
    Super::Init();

    // 创建 FileLogging Provider
    AnalyticsProvider = FAnalytics::Get().CreateAnalyticsProvider(
        FName(TEXT("FileLogging")),
        FAnalyticsProviderConfigurationDelegate()
    );

    if (AnalyticsProvider.IsValid())
    {
        AnalyticsProvider->StartSession();
        AnalyticsProvider->RecordEvent(TEXT("GameStarted"),
            MakeAnalyticsEventAttributeArray(
                TEXT("MapName"), TEXT("MainMenu")
            ));
    }
}

void UMyGameInstance::Shutdown()
{
    if (AnalyticsProvider.IsValid())
    {
        AnalyticsProvider->RecordEvent(TEXT("GameShutdown"));
        AnalyticsProvider->EndSession();
        AnalyticsProvider.Reset();
    }

    Super::Shutdown();
}
```

运行后检查 `{项目目录}/Saved/Analytics/` 目录，会看到一个 `.analytics` JSON 文件。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础库（FString, FArchive 等） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Analytics` | Analytics 系统接口（IAnalyticsProvider, IAnalyticsProviderModule）— *私有依赖* |

使用者需要在自己的 Build.cs 中依赖 `Analytics` 模块才能调用 `FAnalytics::Get()` 工厂方法。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-12-08 | `ae0e1db` | Pushed Set/GetDefaultAttributes into IAnalyticsProvider, fixed up FileLogging, AnalyticsSwrve and AnalyticsMulticast | 为 FileLogging 添加了 `SetDefaultEventAttributes` / `GetDefaultEventAttributesSafe` 等方法，跟随 IAnalyticsProvider 接口变更 |
| 2023-04-11 | `e109a24` | GitHub #9388: FileLogging analytic nested json support | 添加了 `IsJsonFragment()` 支持，允许属性值输出为原始 JSON（非字符串） |
| 2023-01-16 | `bbc37aa` | Another batch IWYU updates to reduce number of includes | 编译头文件清理，无功能变更 |

### 维护评价

- **年龄**: 2014 年创建，已超过 11 年，属于 UE Analytics 系统最早期的组件之一
- **活跃度**: 最近一次功能性更新在 2023 年 12 月，距今约 2.4 年。更新频率极低，大约每年 1 次
- **代码质量**: 实现非常简洁（~600 行），功能单一明确，几乎不存在 bug 需要修复的空间
- **稳定性**: 作为开发调试工具，功能足够完善，不太需要频繁更新
- **已知限制**:
  - 不支持并发写入（单线程 FArchive）
  - JSON 输出是手动拼接的，不是严格标准 JSON（缺少转义处理）
  - 会话期间不能更换 UserID 或 SessionID
  - 不支持事件缓存和批量发送（每次 RecordEvent 直接写盘）
- **推荐度**: ✅ 适合开发调试使用，不建议用于生产环境的数据收集

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Analytics/FileLogging)
- [Analytics 系统源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/Analytics)
- [IAnalyticsProvider 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Analytics/Analytics/Public/Interfaces/IAnalyticsProvider.h)
- [AnalyticsBlueprintLibrary](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Analytics/AnalyticsBlueprintLibrary) — 蓝图中使用 Analytics 的插件
