# Analytics Blueprint Library

> Blueprint Library for using an analytic event provider

| 属性 | 值 |
|---|---|
| 中文名 | 分析蓝图库 |
| 分类 | Analytics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AnalyticsBlueprintLibrary` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-08-28 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/AnalyticsBlueprintLibrary) | |

## 用途

该插件为游戏内集成分析事件提供器（如 Google Analytics、Firebase 等）提供了一套标准化的蓝图接口。它不直接实现分析功能，而是充当一个抽象层，允许开发者在蓝图中调用通用的分析事件记录函数。其核心价值在于将分析事件的逻辑与具体的分析服务提供商解耦，使得更换分析服务时，游戏逻辑代码（蓝图）无需改动。

## 使用场景

-   **游戏内购分析**：当玩家购买虚拟物品或游戏货币时，记录详细的购买事件。
-   **玩家行为追踪**：记录玩家完成关卡、触发特定游戏事件或达到某个成就的“进度事件”。
-   **会话管理**：在玩家进入和退出游戏时，管理分析会话的生命周期。
-   **错误记录**：捕获并上报游戏运行时遇到的特定错误或异常。
-   **快速原型验证**：在项目早期，无需对接具体分析SDK，即可在蓝图中埋入分析逻辑，验证数据结构是否合理。

## 蓝图用法

所有功能均通过静态函数暴露在蓝图中，无需创建实例。核心类是 `UAnalyticsBlueprintLibrary`。

### 会话管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Session` | 启动一个不带自定义属性的分析会话 | `UAnalyticsBlueprintLibrary` |
| `Start Session With Attributes` | 启动一个带有自定义属性的分析会话 | `UAnalyticsBlueprintLibrary` |
| `End Session` | 结束当前的分析会话 | `UAnalyticsBlueprintLibrary` |
| `Flush Events` | 请求立即将所有缓存的事件发送出去 | `UAnalyticsBlueprintLibrary` |

### 通用事件记录

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Record Event` | 记录一个仅有名称的事件（事件计数器） | `UAnalyticsBlueprintLibrary` |
| `Record Event With Attribute` | 记录一个带有一个属性的事件 | `UAnalyticsBlueprintLibrary` |
| `Record Event With Attributes` | 记录一个带有多个属性的事件 | `UAnalyticsBlueprintLibrary` |
| `Make Event Attribute` | （纯函数）根据名称和值创建一个事件属性结构体 | `UAnalyticsBlueprintLibrary` |

### 购买与经济系统记录

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Record Item Purchase` | 记录一次使用指定游戏内货币的物品购买 | `UAnalyticsBlueprintLibrary` |
| `Record Simple Item Purchase` | 记录一次简单的物品购买（不含货币信息） | `UAnalyticsBlueprintLibrary` |
| `Record Currency Purchase` | 记录一次用真实货币购买游戏内货币的行为 | `UAnalyticsBlueprintLibrary` |
| `Record Currency Given` | 记录游戏内无偿授予玩家货币的行为 | `UAnalyticsBlueprintLibrary` |
| `Record Simple Currency Purchase` | 记录一次简单的货币购买（不含真实货币信息） | `UAnalyticsBlueprintLibrary` |

### 进度与用户信息记录

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Record Progress` | 记录用户进度事件 | `UAnalyticsBlueprintLibrary` |
| `Record Error` | 记录一个错误事件 | `UAnalyticsBlueprintLibrary` |
| `Set User ID` | 设置分析提供者的用户 ID | `UAnalyticsBlueprintLibrary` |
| `Get User ID` | 获取分析提供者的用户 ID | `UAnalyticsBlueprintLibrary` |
| `Set Session ID` | 设置分析提供者的会话 ID（如果支持） | `UAnalyticsBlueprintLibrary` |
| `Get Session ID` | 获取分析提供者的会话 ID | `UAnalyticsBlueprintLibrary` |
| `Set Age / Set Gender / Set Location` | 设置用户的年龄、性别、地理位置等信息 | `UAnalyticsBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **记录玩家击杀敌人**:
    -   在“杀死敌人”事件处，连接 `Record Event With Attribute` 节点。
    -   `Event Name` 输入 `“EnemyKilled”`。
    -   `Attribute Name` 输入 `“EnemyType”`。
    -   `Attribute Value` 输入当前被击败敌人的类型变量。

2.  **记录一次购买**:
    -   在玩家购买物品成功的回调中，连接 `Record Item Purchase` 节点。
    -   `Item ID` 输入已购买物品的唯一标识符。
    -   `Currency` 输入玩家支付的游戏货币类型（如 `“Gold”`）。
    -   `Per Item Cost` 和 `Item Quantity` 输入对应的数值。

3.  **创建复合事件属性**:
    -   使用 `Make Event Attribute` 节点创建多个 `FAnalyticsEventAttr` 结构体。
    -   将这些结构体放入一个数组中，然后输入到 `Record Event With Attributes` 节点的 `Attributes` 参数。

## C++ 用法

此插件主要为蓝图设计，但所有函数均为静态，也可在 C++ 中调用。

### 头文件引入

```cpp
#include "AnalyticsBlueprintLibrary.h"
```

### 基本用法

```cpp
// 启动一个分析会话
UAnalyticsBlueprintLibrary::StartSession();

// 记录一个自定义事件
UAnalyticsBlueprintLibrary::RecordEvent(TEXT("GameStarted"));

// 记录一个带属性的事件
FAnalyticsEventAttr Attr;
Attr.Name = TEXT("Level");
Attr.Value = TEXT("Forest");
TArray<FAnalyticsEventAttr> Attrs;
Attrs.Add(Attr);
UAnalyticsBlueprintLibrary::RecordEventWithAttributes(TEXT("CheckpointReached"), Attrs);

// 记录一次物品购买
UAnalyticsBlueprintLibrary::RecordItemPurchase(TEXT("Sword_01"), TEXT("Gold"), 100, 1);

// 在游戏退出时结束会话
UAnalyticsBlueprintLibrary::EndSession();
```

### 进阶用法

```cpp
// 1. 设置用户信息后再记录事件
UAnalyticsBlueprintLibrary::SetUserId(TEXT("Player12345"));
UAnalyticsBlueprintLibrary::SetBuildInfo(TEXT("v1.2.3-Release"));

// 2. 记录带有多个复杂属性的购买事件
FAnalyticsEventAttr CurrencyAttr, CostAttr, ItemAttr;
CurrencyAttr.Name = TEXT("CurrencyType");
CurrencyAttr.Value = TEXT("Gems");
CostAttr.Name = TEXT("TotalCost");
CostAttr.Value = TEXT("500");
ItemAttr.Name = TEXT("BundleID");
ItemAttr.Value = TEXT("StarterPack_01");

TArray<FAnalyticsEventAttr> PurchaseAttrs;
PurchaseAttrs.Add(CurrencyAttr);
PurchaseAttrs.Add(CostAttr);
PurchaseAttrs.Add(ItemAttr);

UAnalyticsBlueprintLibrary::RecordEventWithAttributes(TEXT("BundlePurchased"), PurchaseAttrs);

// 3. 在可能的情况下，立即发送事件（例如游戏存档前）
UAnalyticsBlueprintLibrary::FlushEvents();
```

## Demo 示例

```cpp
// AnalyticsDemoComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "AnalyticsDemoComponent.generated.h"

UCLASS(ClassGroup=(Analytics), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UAnalyticsDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UAnalyticsDemoComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable, Category = "Analytics Demo")
    void SimulatePlayerAction(const FString& ActionName, const FString& Detail);

    UFUNCTION(BlueprintCallable, Category = "Analytics Demo")
    void SimulatePurchase(const FString& ItemId, int32 Cost, const FString& Currency);
};
```

```cpp
// AnalyticsDemoComponent.cpp
#include "AnalyticsDemoComponent.h"
#include "AnalyticsBlueprintLibrary.h"

UAnalyticsDemoComponent::UAnalyticsDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UAnalyticsDemoComponent::BeginPlay()
{
    Super::BeginPlay();
    // 组件激活时，尝试启动一个分析会话
    if (UAnalyticsBlueprintLibrary::StartSession())
    {
        UE_LOG(LogTemp, Log, TEXT("Analytics session started successfully."));
    }
}

void UAnalyticsDemoComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 组件销毁前，确保结束分析会话
    UAnalyticsBlueprintLibrary::EndSession();
    Super::EndPlay(EndPlayReason);
}

void UAnalyticsDemoComponent::SimulatePlayerAction(const FString& ActionName, const FString& Detail)
{
    // 模拟记录一个玩家行为事件
    FAnalyticsEventAttr DetailAttr;
    DetailAttr.Name = TEXT("Detail");
    DetailAttr.Value = Detail;

    TArray<FAnalyticsEventAttr> Attrs;
    Attrs.Add(DetailAttr);

    UAnalyticsBlueprintLibrary::RecordEventWithAttributes(ActionName, Attrs);
    UE_LOG(LogTemp, Log, TEXT("Recorded analytics event: %s"), *ActionName);
}

void UAnalyticsDemoComponent::SimulatePurchase(const FString& ItemId, int32 Cost, const FString& Currency)
{
    // 模拟记录一次购买
    UAnalyticsBlueprintLibrary::RecordItemPurchase(ItemId, Currency, Cost, 1);
    UE_LOG(LogTemp, Log, TEXT("Recorded item purchase: %s for %d %s"), *ItemId, Cost, *Currency);
}
```

## 模块依赖

该插件的模块 `AnalyticsBlueprintLibrary` 主要依赖于引擎的 `Analytics` 模块来与实际的分析服务提供者交互。对于使用者（你的项目）而言，无需额外添加对 `Analytics` 模块的依赖，因为所有交互都通过本插件的蓝图/C++ 接口完成。

| 模块 | 用途 |
|---|---|
| `Analytics` | 提供核心的分析接口和数据结构，是本插件功能的底层支撑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，属于引擎范围的代码风格统一 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理过时的条件编译宏，适配新版引擎 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 引擎插件目录结构批量调整 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | 引擎插件目录结构批量调整 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内部链接为安全协议 |

### 维护评价

该插件创建于 **2014 年**，历史悠久。其**核心功能在创建后长期没有实质性更新**，最近几次提交均为引擎级的代码格式清理、宏迁移或目录结构调整，未涉及插件功能本身的增强或修复。插件默认**未启用** (`EnabledByDefault: false`)。

**结论**：该插件处于 **维护不活跃** 状态。它作为一个稳定的接口抽象层，功能简单且固定，可能已满足需求。但由于长期缺乏功能更新，且官方分析方案可能已有其他替代（如更直接的 SDK 集成），在新项目中使用它可能不是最优选择。它更适合已有集成基础或需要快速原型验证的旧项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/AnalyticsBlueprintLibrary)
- [官方文档](https://docs.unrealengine.com/latest/INT/Gameplay/Analytics/Blueprints/index.html)