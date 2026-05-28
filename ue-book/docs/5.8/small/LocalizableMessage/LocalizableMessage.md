# Localizable Message

> Utility for a text message that can be replicated. It supports parameter resolution for the client.

| 属性 | 值 |
|---|---|
| 中文名 | 可本地化消息 |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LocalizableMessage` (Runtime), `LocalizableMessageBlueprint` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-05-08 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LocalizableMessage) | |

## 用途

LocalizableMessage 插件的核心目的是为多人游戏或网络应用中，需要从服务器复制到客户端的本地化文本消息提供一个统一的数据结构和处理框架。它解决了以下问题：

1.  **网络同步**：传统的 `FText` 在网络复制时可能丢失本地化信息或效率不高。`FLocalizableMessage` 结构体被设计为轻量级且可序列化的，其包含了用于本地化的 `Key` 和一个默认回退文本 `DefaultText`，适合在网络中高效传输。
2.  **客户端参数解析**：服务器在构建消息时，可能只知道参数的值（如一个数字、一个玩家名），但不知道客户端的语言环境。该插件通过 `FLocalizableMessageParameterEntry` 和 `FLocalizableMessageProcessor` 允许服务器传递参数的原始数据（通过 `FInstancedStruct`），客户端在收到消息后，根据其本地语言环境，调用注册的“本地化值函子”将参数解析为适合当前语言格式的 `FFormatArgumentValue`（例如，将整数 1000 格式化为 "1,000" 或 "1.000"），最终生成完整的 `FText`。
3.  **扩展性**：通过 `RegisterLocalizableType` 方法，开发者可以注册自定义的结构体类型，为其定义如何根据本地化上下文将其转换为格式化参数值，从而支持游戏中的特定数据类型（如物品、技能等）的本地化显示。

简单来说，它是 **专门为网络复制场景设计的、支持客户端延迟解析参数的本地化消息传递解决方案**。

## 使用场景

-   你在开发一个多人在线游戏，需要从服务器向所有客户端广播一条动态的系统公告（例如：“玩家 [玩家名] 击杀了 [Boss名]，获得了 [物品名]x[数量]”）。
-   你的游戏支持多语言，但服务器只知道事件发生的原始数据（ID、数量）。你需要一种方法，在客户端根据其语言设置，将这些数据转换并嵌入到正确的本地化字符串中。
-   你希望建立一个聊天或通知系统，消息本身需要被网络复制，并且支持富文本或特定格式的动态参数。

## 蓝图用法

从源码分析，`FLocalizableMessage` 是一个 `BlueprintType` 结构体，这意味着它可以在蓝图中被创建、传递和操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make LocalizableMessage` | 创建一个 `FLocalizableMessage` 结构体实例，设置其 `Key`、`DefaultText` 和 `Substitutions`。 | 蓝图自动生成 |
| `Break LocalizableMessage` | 分解一个 `FLocalizableMessage` 结构体，获取其内部字段。 | 蓝图自动生成 |
| `Key` (Get) | 获取消息的本地化键。 | `FLocalizableMessage` |
| `DefaultText` (Get) | 获取消息的默认回退文本。 | `FLocalizableMessage` |
| `Substitutions` (Get) | 获取消息的参数替换列表（`TArray<FLocalizableMessageParameterEntry>`）。 | `FLocalizableMessage` |
| `Reset` | 重置消息的所有字段。 | `FLocalizableMessage` |
| `IsEmpty` | 检查消息是否为空（Key 和 DefaultText 都为空）。 | `FLocalizableMessage` |

### 使用示例（蓝图描述）

1.  **创建一个可本地化消息变量**：在蓝图中使用 `Make LocalizableMessage` 节点。
2.  **设置消息键**：将 `Key` 输入引脚连接到一个字符串（如 `”Message.PlayerKilledBoss“`），该键对应本地化文本表中的条目。
3.  **设置默认文本**：将 `DefaultText` 输入引脚连接到一个包含占位符的字符串（如 `{PlayerName} killed {BossName}`），作为键失效时的回退。
4.  **添加参数**：对于 `Substitutions` 输入引脚，需要构建一个 `FLocalizableMessageParameterEntry` 数组。可以使用 `Make LocalizableMessageParameterEntry` 节点（假设存在）或通过构造数组的方式添加。每个条目需要提供一个 `Key`（如 `”PlayerName“`）和一个 `Value`（`FInstancedStruct`）。
    -   对于简单类型（如整数），蓝图可能需要一个将基础类型包装为 `FInstancedStruct` 的节点（例如，`Make InstancedStruct (Int)`）。
    -   对于自定义结构体，需要确保其类型已注册（见 C++ 用法）。
5.  **发送消息**：将构建好的 `FLocalizableMessage` 变量通过 RPC（远程过程调用）或其他网络复制机制发送给客户端。
6.  **客户端解析**：在客户端蓝图中，收到消息后，使用 C++ 层暴露的 `LocalizableMessageProcessor` 函数（或相应的蓝图节点）将 `FLocalizableMessage` 和当前本地化上下文转换为 `FText` 显示。

## C++ 用法

### 头文件引入

```cpp
#include "LocalizableMessage.h"
#include "LocalizableMessageProcessor.h"
#include "LocalizationContext.h"
```

### 基本用法

创建一个消息并进行本地化。
```cpp
// 创建一个本地化消息
FLocalizableMessage MyMessage;
MyMessage.Key = TEXT(“UI.Announcement.Damage”);
MyMessage.DefaultText = TEXT(“{Attacker} dealt {Damage} damage to {Target}.”);

// 添加参数
FLocalizableMessageParameterEntry AttackerParam;
AttackerParam.Key = TEXT(“Attacker”);
AttackerParam.Value.InitializeAs<FLocalizableMessageParameterString>();
AttackerParam.Value.GetMutable<FLocalizableMessageParameterString>().Value = TEXT(“Hero”);
MyMessage.Substitutions.Add(AttackerParam);

// ... 添加其他参数

// 在客户端进行本地化
ILocalizableMessageModule& Module = ILocalizableMessageModule::Get();
FLocalizableMessageProcessor& Processor = Module.GetLocalizableMessageProcessor();

// 创建本地化上下文（通常关联到一个 World 或 PlayerController）
FLocalizationContext LocContext(SomeWorldContextObject);

// 进行本地化，得到 FText
FText LocalizedText = Processor.Localize(MyMessage, LocContext);
UE_LOG(LogTemp, Log, TEXT(“Localized Message: %s”), *LocalizedText.ToString());
```

### 进阶用法

注册自定义结构体类型，使其能够作为消息参数被本地化。
```cpp
// 1. 定义你的结构体
USTRUCT()
struct FMyItemInfo
{
    GENERATED_BODY()

    UPROPERTY()
    FName ItemId;

    UPROPERTY()
    int32 Quantity;
};

// 2. 实现一个本地化值函子
FFormatArgumentValue LocalizeMyItemInfo(const FMyItemInfo& ItemInfo, const FLocalizationContext& Context)
{
    // 这里可以根据 Context 的语言环境，将 ItemInfo 格式化为 FText
    // 例如，查找物品表获取本地化名称
    FText ItemName = FText::FromName(ItemInfo.ItemId); // 简化示例
    FText Result = FText::Format( NSLOCTEXT(“MyGame”, “ItemInfo”, “{0} x{1}“), ItemName, ItemInfo.Quantity );
    // FFormatArgumentValue 可以从 FText 构造
    return FFormatArgumentValue(Result);
}

// 3. 在模块启动时注册（或在需要时）
{
    ILocalizableMessageModule& Module = ILocalizableMessageModule::Get();
    FLocalizableMessageProcessor& Processor = Module.GetLocalizableMessageProcessor();

    // 使用 ScopedRegistrations 进行 RAII 风格的注册/注销
    static FLocalizableMessageProcessor::FScopedRegistrations Registrations;

    Processor.RegisterLocalizableType<FMyItemInfo>(
        [](const FMyItemInfo& Info, const FLocalizationContext& Ctx) -> FFormatArgumentValue {
            return LocalizeMyItemInfo(Info, Ctx);
        },
        Registrations
    );
}

// 4. 现在可以将 FMyItemInfo 作为参数添加到 FLocalizableMessage 中
FLocalizableMessageParameterEntry ItemParam;
ItemParam.Key = TEXT(“Loot”);
ItemParam.Value.InitializeAs<FMyItemInfo>();
ItemParam.Value.GetMutable<FMyItemInfo>().ItemId = “Sword_01”;
ItemParam.Value.GetMutable<FMyItemInfo>().Quantity = 3;
MyMessage.Substitutions.Add(ItemParam);

// 当处理器处理这条消息时，会自动调用上面注册的函子来格式化 FMyItemInfo
```

## Demo 示例

一个最小的控制台应用示例，演示如何创建和本地化一条消息。

```cpp
// LocalizableMessageDemo.h
#pragma once

#include "CoreMinimal.h"

class FLocalizableMessageDemo
{
public:
    static void RunDemo();
};
```

```cpp
// LocalizableMessageDemo.cpp
#include "LocalizableMessageDemo.h"
#include "LocalizableMessage.h"
#include "LocalizableMessageProcessor.h"
#include "ILocalizableMessageModule.h"
#include "LocalizationContext.h"

void FLocalizableMessageDemo::RunDemo()
{
    // 确保模块已加载（在真实引擎环境中通常已自动加载）
    ILocalizableMessageModule& MessageModule = ILocalizableMessageModule::Get();
    FLocalizableMessageProcessor& Processor = MessageModule.GetLocalizableMessageProcessor();

    // 1. 构建消息
    FLocalizableMessage DamageMessage;
    DamageMessage.Key = TEXT(“Combat.DamageDealt”);
    DamageMessage.DefaultText = TEXT(“{Attacker} hit {Target} for {Damage} points.”);

    // 添加攻击者参数（字符串）
    {
        FLocalizableMessageParameterEntry Entry;
        Entry.Key = TEXT(“Attacker”);
        Entry.Value.InitializeAs<FLocalizableMessageParameterString>();
        Entry.Value.GetMutable<FLocalizableMessageParameterString>().Value = TEXT(“Warrior”);
        DamageMessage.Substitutions.Add(Entry);
    }

    // 添加目标参数（字符串）
    {
        FLocalizableMessageParameterEntry Entry;
        Entry.Key = TEXT(“Target”);
        Entry.Value.InitializeAs<FLocalizableMessageParameterString>();
        Entry.Value.GetMutable<FLocalizableMessageParameterString>().Value = TEXT(“Goblin”);
        DamageMessage.Substitutions.Add(Entry);
    }

    // 添加伤害参数（整数）
    {
        FLocalizableMessageParameterEntry Entry;
        Entry.Key = TEXT(“Damage”);
        Entry.Value.InitializeAs<FLocalizableMessageParameterInt>();
        Entry.Value.GetMutable<FLocalizableMessageParameterInt>().Value = 150;
        DamageMessage.Substitutions.Add(Entry);
    }

    // 2. 创建一个本地化上下文（这里不需要真实的 UObject）
    FLocalizationContext Context(nullptr); // 传入 null 意味着使用引擎默认的语言环境

    // 3. 进行本地化
    FText FinalText = Processor.Localize(DamageMessage, Context);

    // 4. 输出结果
    UE_LOG(LogTemp, Display, TEXT(“Original Key: %s“), *DamageMessage.Key);
    UE_LOG(LogTemp, Display, TEXT(“Default Text: %s“), *DamageMessage.DefaultText);
    UE_LOG(LogTemp, Display, TEXT(“Localized Text: %s“), *FinalText.ToString());
    // 可能的输出: “Localized Text: Warrior hit Goblin for 150 points.“ （取决于本地化数据和语言环境）
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库。 |
| `CoreUObject` | 用于 `USTRUCT`, `UCLASS` 等反射系统。 |
| `Engine` | 核心引擎功能，可能用于网络和世界上下文。 |
| `InstancedStruct` | 提供 `FInstancedStruct`，这是存储类型擦除参数的核心。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至新的 `UE_LOGF`。 |
| 2025-08-12 | `f3d05004` | Made it so that Hud messages could be compared in Blueprints. | 使 HUD 消息在蓝图中支持比较操作。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏，优化生成代码。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 为方法/静态变量添加 DLL 导出标记 (`dllexport`)，完善模块接口。 |
| 2024-12-06 | `3b9c9c2a` | Verse message: helper function to convert a verse::message into FText. | 添加了将 Verse 消息 (`verse::message`) 转换为 `FText` 的辅助函数，增强与 Verse 语言的集成。 |

### 维护评价

LocalizableMessage 插件创建于 2023 年，相对年轻。从 git 历史看，其维护状态**活跃**。最近一次更新（2026-04-14）是日志系统的迁移，属于框架适配性更新。在此之前的几次提交（2025年）分别增加了蓝图功能支持（消息比较）、代码优化（内联生成代码、DLL导出）以及与新兴脚本语言 Verse 的集成。这些更新表明该插件正在被持续使用和改进，以适应引擎和项目的发展。

**推荐使用**。该插件为解决多人游戏中本地化文本的网络复制和客户端解析提供了清晰、可扩展的方案，且处于积极维护中。对于有此类需求的新项目，它是一个值得考虑的基础设施选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LocalizableMessage)
- [官方文档]() （暂无）
- [测试用例]() （在提供的资料中未找到，可能位于 `Engine/Tests/` 目录下或内部测试项目中）