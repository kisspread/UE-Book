# Analytics Blueprint Library

> Blueprint Library for using an analytic event provider

| 属性 | 值 |
|---|---|
| 分类 | Analytics |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AnalyticsBlueprintLibrary (Runtime) |
| 创建时间 | 2014-08-28 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Analytics/AnalyticsBlueprintLibrary) | |

## 用途

AnalyticsBlueprintLibrary 是一个轻量级的蓝图函数库，它将 UE5 底层的 `IAnalyticsProvider` 接口包装为蓝图可调用的静态函数。这个 plugin 本身**不实现任何分析功能**——它只是一个桥接层，所有实际的事件发送工作都委托给项目中配置的 Analytics Provider（如 FileLogging、Adjust、AnalyticsMulticast 等）。

核心价值在于：**让不写 C++ 的设计师和策划也能在蓝图中直接发送分析事件**，无需了解底层 `IAnalyticsProvider` 接口和 `FAnalytics` 单例的运作方式。

需要注意的是，这个 plugin 默认是**禁用**的（`EnabledByDefault: false`），你必须在项目的 Plugin 设置中手动启用它，同时还需要配置至少一个 Analytics Provider 才能实际发送数据。

## 使用场景

- 你在做 F2P 手游，需要追踪玩家的内购行为（买了什么道具、花了什么货币）→ 用此 plugin 在蓝图中直接记录购买事件
- 你想在蓝图关卡中快速埋点，记录玩家到达了某个区域、完成了某个任务 → 用 `RecordEvent` / `RecordProgress` 节点
- 你需要在不修改 C++ 代码的情况下，让策划自行添加分析埋点 → 启用此 plugin，策划在蓝图中拖拽节点即可
- 你在做原型阶段，想快速验证某个分析方案是否可行 → 此 plugin 配合 FileLogging provider 可以零代码快速试验

## 蓝图用法

所有函数都是 `BlueprintCallable` 的静态函数，位于 `Analytics` 类别下，可直接在任何蓝图中调用。

### 核心节点

#### 会话管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartSession` | 启动一个分析会话（无自定义属性） | `UAnalyticsBlueprintLibrary` |
| `StartSessionWithAttributes` | 启动一个带自定义属性的分析会话 | `UAnalyticsBlueprintLibrary` |
| `EndSession` | 结束当前分析会话 | `UAnalyticsBlueprintLibrary` |
| `FlushEvents` | 立即发送所有缓存的事件 | `UAnalyticsBlueprintLibrary` |

#### 自定义事件记录

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecordEvent` | 记录一个命名事件（无属性，纯计数器） | `UAnalyticsBlueprintLibrary` |
| `RecordEventWithAttribute` | 记录带单个属性的事件 | `UAnalyticsBlueprintLibrary` |
| `RecordEventWithAttributes` | 记录带多个属性的事件 | `UAnalyticsBlueprintLibrary` |

#### 购买事件记录

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecordItemPurchase` | 记录道具购买（含货币类型、单价、数量） | `UAnalyticsBlueprintLibrary` |
| `RecordSimpleItemPurchase` | 记录简单道具购买（仅道具ID和数量） | `UAnalyticsBlueprintLibrary` |
| `RecordSimpleItemPurchaseWithAttributes` | 记录带自定义属性的道具购买 | `UAnalyticsBlueprintLibrary` |
| `RecordCurrencyPurchase` | 记录用真实货币购买游戏货币 | `UAnalyticsBlueprintLibrary` |
| `RecordSimpleCurrencyPurchase` | 记录简单货币购买（仅类型和数量） | `UAnalyticsBlueprintLibrary` |
| `RecordSimpleCurrencyPurchaseWithAttributes` | 记录带自定义属性的货币购买 | `UAnalyticsBlueprintLibrary` |
| `RecordCurrencyGiven` | 记录游戏内赠送的货币（非真实货币） | `UAnalyticsBlueprintLibrary` |
| `RecordCurrencyGivenWithAttributes` | 记录带自定义属性的赠送货币 | `UAnalyticsBlueprintLibrary` |

#### 错误与进度记录

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecordError` | 记录一个错误事件 | `UAnalyticsBlueprintLibrary` |
| `RecordErrorWithAttributes` | 记录带自定义属性的错误事件 | `UAnalyticsBlueprintLibrary` |
| `RecordProgress` | 记录玩家进度事件 | `UAnalyticsBlueprintLibrary` |
| `RecordProgressWithAttributes` | 记录带自定义属性的进度事件 | `UAnalyticsBlueprintLibrary` |
| `RecordProgressWithFullHierarchyAndAttributes` | 记录带完整层级和属性的进度事件 | `UAnalyticsBlueprintLibrary` |

#### 用户信息与辅助

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSessionId` | 获取当前会话 ID | `UAnalyticsBlueprintLibrary` |
| `SetSessionId` | 设置会话 ID（如果 provider 支持） | `UAnalyticsBlueprintLibrary` |
| `GetUserId` | 获取当前用户 ID | `UAnalyticsBlueprintLibrary` |
| `SetUserId` | 设置用户 ID | `UAnalyticsBlueprintLibrary` |
| `SetAge` | 设置用户年龄 | `UAnalyticsBlueprintLibrary` |
| `SetLocation` | 设置用户位置 | `UAnalyticsBlueprintLibrary` |
| `SetGender` | 设置用户性别 | `UAnalyticsBlueprintLibrary` |
| `SetBuildInfo` | 设置游戏构建信息 | `UAnalyticsBlueprintLibrary` |
| `MakeEventAttribute` | 创建一个 `FAnalyticsEventAttr` 结构体（BlueprintPure） | `UAnalyticsBlueprintLibrary` |

### 关键结构体

**`FAnalyticsEventAttr`** — 蓝图可读写的分析属性结构体：

| 属性 | 类型 | 说明 |
|---|---|---|
| `Name` | `FString` | 属性名称 |
| `Value` | `FString` | 属性值 |

### 使用示例（蓝图描述）

**示例 1：基本会话与事件记录**

1. 在 GameMode 的 `BeginPlay` 中，拖入 `StartSession` 节点
2. 连接一个 `Set Build Info` 节点，传入版本号字符串如 `"1.0.3-beta"`
3. 当玩家完成某个关卡时，调用 `Record Progress`，ProgressType 填 `"Level"`，ProgressName 填 `"Forest-01"`
4. 游戏退出时（`End Play`），调用 `End Session`

**示例 2：记录带多个属性的购买事件**

1. 创建一个 `Make Array` 节点，元素类型为 `FAnalyticsEventAttr`
2. 对每个元素使用 `Make Event Attribute` 节点创建属性，如：
   - `("ItemName", "FireSword")`
   - `("Rarity", "Legendary")`
   - `("Source", "Shop")`
3. 将数组传入 `Record Event With Attributes`，EventName 填 `"ItemPurchased"`

**示例 3：完整的内购记录**

1. 玩家在商店购买了 3 把铁剑，每把 100 金币
2. 调用 `Record Item Purchase`：
   - `ItemId`: `"IronSword"`
   - `Currency`: `"Gold"`
   - `PerItemCost`: `100`
   - `ItemQuantity`: `3`

## C++ 用法

### 头文件引入

```cpp
#include "AnalyticsBlueprintLibrary.h"
```

### 基本用法

本 plugin 的 C++ 用法意义不大——它的存在价值就是蓝图桥接。在 C++ 中你应该直接使用 `IAnalyticsProvider` 接口。但如果你确实需要在 C++ 中通过这个库调用：

```cpp
// 启动分析会话
bool bStarted = UAnalyticsBlueprintLibrary::StartSession();

// 设置用户 ID
UAnalyticsBlueprintLibrary::SetUserId(TEXT("Player_12345"));

// 记录一个简单事件
UAnalyticsBlueprintLibrary::RecordEvent(TEXT("LevelComplete"));

// 记录带属性的事件
TArray<FAnalyticsEventAttr> Attrs;
Attrs.Add(UAnalyticsBlueprintLibrary::MakeEventAttribute(TEXT("Level"), TEXT("Forest-01")));
Attrs.Add(UAnalyticsBlueprintLibrary::MakeEventAttribute(TEXT("Score"), TEXT("9500")));
UAnalyticsBlueprintLibrary::RecordEventWithAttributes(TEXT("LevelComplete"), Attrs);

// 结束会话
UAnalyticsBlueprintLibrary::EndSession();
```

来源：`Source/AnalyticsBlueprintLibrary/Private/AnalyticsBlueprintLibrary.cpp`

### 进阶用法：直接使用 IAnalyticsProvider

对于 C++ 项目，更推荐直接使用底层接口，避免蓝图序列化开销：

```cpp
#include "Analytics.h"
#include "Interfaces/IAnalyticsProvider.h"

// 获取默认配置的 provider
TSharedPtr<IAnalyticsProvider> Provider = FAnalytics::Get().GetDefaultConfiguredProvider();
if (Provider.IsValid())
{
    // 启动会话
    Provider->StartSession();
    
    // 设置用户信息
    Provider->SetUserID(TEXT("Player_12345"));
    Provider->SetBuildInfo(TEXT("v1.0.0"));
    
    // 记录事件（使用便捷的属性数组构造方式）
    Provider->RecordEvent(TEXT("ItemPurchased"), 
        MakeAnalyticsEventAttributeArray(
            TEXT("ItemId"), TEXT("FireSword"),
            TEXT("Currency"), TEXT("Gold"),
            TEXT("Amount"), TEXT("500")
        ));
    
    // 记录购买事件
    Provider->RecordItemPurchase(TEXT("FireSword"), TEXT("Gold"), 500, 1);
    
    // 记录进度事件
    Provider->RecordProgress(TEXT("Quest"), TEXT("MainQuest.Chapter1.BossDefeated"));
    
    // 立即发送缓存事件
    Provider->FlushEvents();
    
    // 结束会话
    Provider->EndSession();
}
```

来源：`Engine/Source/Runtime/Analytics/Analytics/Public/Interfaces/IAnalyticsProvider.h`

## Demo 示例

### 最小可运行示例：分析事件记录器

**MyAnalyticsActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AnalyticsBlueprintLibrary.h"
#include "MyAnalyticsActor.generated.h"

UCLASS()
class AMyAnalyticsActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 在蓝图中调用来记录自定义事件
    UFUNCTION(BlueprintCallable, Category = "Analytics")
    void TrackPlayerAction(const FString& ActionName, const FString& Detail);
};
```

**MyAnalyticsActor.cpp**

```cpp
#include "MyAnalyticsActor.h"
#include "AnalyticsBlueprintLibrary.h"

void AMyAnalyticsActor::BeginPlay()
{
    Super::BeginPlay();

    // 启动分析会话
    bool bStarted = UAnalyticsBlueprintLibrary::StartSession();
    if (bStarted)
    {
        // 设置构建信息
        UAnalyticsBlueprintLibrary::SetBuildInfo(
            FString::Printf(TEXT("%s-%s"), FApp::GetProjectName(), *FApp::GetBuildVersion()));
    }
}

void AMyAnalyticsActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 结束会话前先刷新
    UAnalyticsBlueprintLibrary::FlushEvents();
    UAnalyticsBlueprintLibrary::EndSession();

    Super::EndPlay(EndPlayReason);
}

void AMyAnalyticsActor::TrackPlayerAction(const FString& ActionName, const FString& Detail)
{
    UAnalyticsBlueprintLibrary::RecordEventWithAttribute(ActionName, TEXT("Detail"), Detail);
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "AnalyticsBlueprintLibrary"
});
```

> ⚠️ 注意：此示例仅演示如何调用 API。实际使用时，你必须在项目设置或 `DefaultEngine.ini` 中配置一个 Analytics Provider（如 `[Analytics]` 配置段），否则所有调用都会输出 warning 日志并静默失败。

## 模块依赖

从 `AnalyticsBlueprintLibrary.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库（基础类型、日志等） |
| `CoreUObject` | UObject 系统（UCLASS、USTRUCT 反射） |
| `Engine` | 引擎核心（UBlueprintFunctionLibrary 基类） |
| `Analytics` | 分析模块核心（`IAnalyticsProvider`、`FAnalytics` 单例，Private 依赖） |

**使用者需要在 Build.cs 中添加的模块**：`AnalyticsBlueprintLibrary`

> 注意：`Analytics` 模块是此 plugin 的私有依赖，使用者不需要直接引用它。所有功能通过 `UAnalyticsBlueprintLibrary` 的静态函数访问。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2024-11-09 | `66e9bb39ff7e` | 移除所有 `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2` 条件编译块 — 这是 UE5 全库范围的 IWYU 清理，非功能性改动 |
| 2023-01-13 | `3c9aacb1ad24` | 使用 IWYU 更新约 170 个 plugin 的公共头文件，移除不必要的 `#include` — 同样是全库级别的头文件清理 |
| 2023-01-12 | `2f78497e6753` | 使用 IWYU 更新所有 plugin 的私有文件 — 与上一条同批处理 |

### 维护评价

**评级：可能废弃 / 已固化**

这个 plugin 具有典型的"已固化"特征：

- **创建于 2014 年 8 月**，已超过 11 年，属于 Unreal Engine 的早期插件
- **最近 3 次提交全部是机械性的代码清理**（IWYU 头文件规范化、废弃宏移除），没有任何功能性更新
- **上一次实质性代码改动可能要追溯到 UE4 时代**
- 代码极其简单——`AnalyticsBlueprintLibrary.cpp` 仅 423 行，每个函数都是相同的模式：获取 provider → 调用方法 → 失败时打 warning
- 模块的 `StartupModule()` 和 `ShutdownModule()` 都是空实现，说明它纯粹是一个静态函数集合
- **没有测试用例**，在 Engine 的测试目录中也找不到相关测试
- `EnabledByDefault: false` 表明 Epic 自己也不认为这是默认需要的

**建议**：如果你需要在蓝图中使用分析功能，这个 plugin 仍然可用且功能完整。但由于它只是 `IAnalyticsProvider` 的简单包装，对于 C++ 项目来说直接使用底层接口更灵活。这个 plugin 不太可能被删除（向后兼容），但也不太可能获得新功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Analytics/AnalyticsBlueprintLibrary)
- [官方文档](https://docs.unrealengine.com/latest/INT/Gameplay/Analytics/Blueprints/index.html)
- [Analytics 核心模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/Analytics)
- [IAnalyticsProvider 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Analytics/Analytics/Public/Interfaces/IAnalyticsProvider.h)
