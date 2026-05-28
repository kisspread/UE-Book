# Localizable Message

> Utility for a text message that can be replicated. It supports parameter resolution for the client.（照抄，不翻译）

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

该插件的核心功能是实现一个支持**网络复制**并能在**客户端进行本地化参数解析**的消息数据结构。它解决了在多人游戏中，服务器向客户端发送包含动态参数的本地化文本消息的需求。例如，服务器需要通知所有客户端 “玩家A击杀了玩家B”，但击杀者的名称和武器是动态的，且需要根据客户端的语言设置进行翻译。插件提供了一个结构化的方式来构造、复制和在客户端解析这类消息。

## 使用场景

- 你正在开发一款多人在线游戏，需要从服务器向所有客户端广播游戏事件通知（如“XX玩家加入了游戏”、“XX玩家获得了成就”）。
- 你需要发送的消息中包含动态数据（如玩家名、分数、物品名），且这些消息的文本需要根据客户端的语言环境进行本地化翻译。
- 你希望将消息逻辑与本地化资源（如文本表）解耦，通过消息标识符和参数来动态构建最终显示的文本。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `LocalizableMessage` | Runtime | 核心模块，定义了 `FLocalizableMessage` 等数据结构，实现了消息的创建、序列化、复制和客户端解析逻辑。 |
| `LocalizableMessageBlueprint` | Runtime | 蓝图支持模块，将核心功能暴露给蓝图，提供了在蓝图中创建、操作和比较可本地化消息的节点。 |

## 蓝图用法

蓝图功能主要由 `LocalizableMessageBlueprint` 模块提供。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Localizable Message` | 创建一个 `FLocalizableMessage` 结构体实例。 | `ULocalizableMessageBlueprintLibrary` |
| `Set Message Text` / `Set Message String` | 为消息设置主体文本或标识符字符串。 | `ULocalizableMessageBlueprintLibrary` |
| `Add Message Argument` | 向消息添加一个键值对参数（如 `{PlayerName}` -> “Tim”）。 | `ULocalizableMessageBlueprintLibrary` |
| `To Text` | 将 `FLocalizableMessage` 转换为可直接显示的 `FText`。这是最终输出的步骤。 | `ULocalizableMessageBlueprintLibrary` |
| `Equal` / `Not Equal` | 比较两个 `FLocalizableMessage` 是否相等。 | `ULocalizableMessageBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **构造消息**：使用 `Create Localizable Message` 节点创建新消息。用 `Set Message Text` 设置一个本地化键（如 `NSLOCTEXT(“Game”, “KillMessage”, “{Killer} 杀死了 {Victim}”)`）。
2.  **填充参数**：使用 `Add Message Argument` 节点多次，分别添加键（如 `“Killer”`, `“Victim”`）和对应的值（如玩家名的字符串或文本）。
3.  **发送或存储**：将构造好的 `FLocalizableMessage` 结构体作为 RPC 参数发送，或存储在需要复制的变量中。
4.  **客户端显示**：在客户端收到消息后，调用 `To Text` 节点将其转换为 `FText`，然后用于 UI 显示。此时，文本会根据客户端的语言设置和提供的参数进行最终解析。

## C++ 用法

### 头文件引入

```cpp
#include "LocalizableMessageTypes.h"
```

### 基本用法

以下示例展示了如何在 C++ 中构造一个本地化消息并转换为 FText。

```cpp
// 引用自模块设计：LocalizableMessageTypes.h
#include "LocalizableMessageTypes.h"

// 假设在服务器或逻辑中构造消息
FLocalizableMessage NewMessage;
NewMessage.Text = FText::FromString(“{PlayerA} picked up a {Item}.”);

// 添加参数
NewMessage.Arguments.Add(TEXT(“PlayerA”), FText::FromString(“Tim”));
NewMessage.Arguments.Add(TEXT(“Item”), FText::FromString(“Super Rifle”));

// 在客户端（例如，RPC 回调或属性复制后）解析为 FText
FText DisplayText = NewMessage.ToText();
// DisplayText 的内容将是 “Tim picked up a Super Rifle.” (根据客户端语言可能被翻译)
```

### 进阶用法

将消息用于网络复制的 `UPROPERTY`。

```cpp
// 在某个复制的 Actor 或 Component 类中
UPROPERTY(ReplicatedUsing = OnRep_GameMessage)
FLocalizableMessage GameMessage;

UFUNCTION()
void OnRep_GameMessage()
{
    // 当 GameMessage 在客户端更新时，调用解析并更新 UI
    FText TextToDisplay = GameMessage.ToText();
    UpdateNotificationWidget(TextToDisplay);
}
```

## Demo 示例

以下是一个最小化示例，展示如何在 Actor 中定义和使用一个复制的本地化消息。

```cpp
// MyActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "LocalizableMessageTypes.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    AMyActor();

    // 需要复制的消息
    UPROPERTY(ReplicatedUsing=OnRep_ServerMessage)
    FLocalizableMessage ServerMessage;

    UFUNCTION()
    void OnRep_ServerMessage();

    // 服务器端调用的函数，用于设置消息
    UFUNCTION(BlueprintCallable)
    void ServerBroadcastMessage(const FText& PlayerName, const FText& ItemName);

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "Net/UnrealNetwork.h"

AMyActor::AMyActor()
{
    bReplicates = true;
}

void AMyActor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyActor, ServerMessage);
}

void AMyActor::ServerBroadcastMessage(const FText& PlayerName, const FText& ItemName)
{
    if (HasAuthority())
    {
        // 构造消息
        ServerMessage.Text = NSLOCTEXT(“GameEvents”, “Pickup”, “{Player} picked up a {Item}.”);
        ServerMessage.Arguments.Add(TEXT(“Player”), PlayerName);
        ServerMessage.Arguments.Add(TEXT(“Item”), ItemName);

        // 标记需要复制
        ForceNetUpdate();
    }
}

void AMyActor::OnRep_ServerMessage()
{
    // 在客户端，将消息转换为本地化文本并使用
    FText FinalText = ServerMessage.ToText();
    UE_LOG(LogTemp, Display, TEXT(“Received localized message: %s”), *FinalText.ToString());
    // 此处可以更新UI，播放音效等
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新的 UE_LOGF 格式。 |
| 2025-08-12 | `f3d05004` | Made it so that Hud messages could be compared in Blueprints. | 为 HUD 消息添加了蓝图中的比较运算符支持。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie... | 为源文件添加内联生成宏，优化编译。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i... | 调整代码导出符号以兼容特定构建目标。 |
| 2024-12-06 | `3b9c9c2a` | Verse message: helper function to convert a verse::message into FText. | 添加了将 Verse 消息转换为 FText 的辅助函数。 |

### 维护评价

该插件创建于约2年前，从实验性目录中诞生，且默认启用。根据近期的 Git 历史记录，其维护状态为 **维护中**。
-   **活跃度**：最近一年内有多次实质性更新，包括功能增强（如蓝图比较支持）、编译兼容性修复和对新语言（Verse）的适配。
-   **稳定性**：功能相对聚焦，近期更新多为改进和优化，未见重大重构或废弃标记。
-   **推荐使用**：推荐。它解决了多人游戏中本地化消息复制的一个具体痛点，且仍在持续维护，功能在不断完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LocalizableMessage)
- [官方文档]() (无)
- [测试用例]() (未在提供的信息中找到明确路径，可查阅插件 `Tests` 目录)