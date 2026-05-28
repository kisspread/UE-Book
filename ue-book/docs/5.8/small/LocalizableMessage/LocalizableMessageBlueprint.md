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

这个插件的核心功能是解决网络游戏中文本消息的本地化（国际化）问题。它允许你在服务器（或权威端）定义一个带有文本键和参数的消息结构体 `FLocalizableMessage`，并将其复制到客户端。客户端收到这个结构体后，可以根据当前的语言环境，使用本地化系统查找对应的文本模板，并将参数填充进去，最终生成正确语言和格式的 `FText`。

**为什么需要它**：在传统的多人游戏逻辑中，如果直接复制 `FText`，会带来两个主要问题：
1.  **网络带宽浪费**：复制完整的、已解析的 `FText` 字符串比复制一个小的参数化结构体要占用更多带宽。
2.  **本地化时机问题**：服务器可能只有一种语言（如英语），复制过来的文本在客户端无法切换语言。

`LocalizableMessage` 通过只复制参数和键，将最终的本地化渲染延迟到客户端完成，完美解决了以上问题。

## 使用场景

-   **多人游戏系统消息**：服务器需要向所有玩家广播系统提示（例如，“玩家 [玩家名] 已加入游戏”、“回合结束，队伍 [队伍名] 获胜”）。
-   **任务/成就通知**：玩家在服务器上完成了一个成就，服务器需要向该玩家发送一条通知，该通知需要在客户端根据玩家的语言偏好进行显示。
-   **聊天系统**：发送结构化的聊天消息，例如，“[玩家A] 正在攻击 [目标B]”，其中 `[玩家A]` 和 `[目标B]` 是变量，消息文本模板由本地化表管理。

## 蓝图用法

插件的蓝图功能主要集中在 `ULocalizableMessageLibrary` 中，提供对 `FLocalizableMessage` 结构体的基本操作和转换。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Conv_LocalizableMessageToText` | 将本地化消息转换为可显示的 `FText`。这是在客户端将消息“渲染”为文本的最终步骤。 | `ULocalizableMessageLibrary` |
| `EqualEqual_LocalizableMessage` | 比较两个本地化消息是否相等。 | `ULocalizableMessageLibrary` |
| `IsEmpty_LocalizableMessage` | 检查消息是否为空。 | `ULocalizableMessageLibrary` |
| `Reset_LocalizableMessage` | 重置一个本地化消息。 | `ULocalizableMessageLibrary` |

### 使用示例（蓝图描述）

假设你有一个需要发送给玩家的系统消息蓝图逻辑：

1.  **在服务器或权威端**：你需要构建一个 `FLocalizableMessage` 变量。由于 `FLocalizableMessage` 本身在蓝图中通常不直接构造（更多在 C++ 中），你可能会通过一个标记为 `BlueprintCallable` 的 C++ 函数来创建它。
2.  **将消息复制到客户端**：通过 RepNotify 或 RPC 将包含 `FLocalizableMessage` 的属性发送到客户端。
3.  **在客户端**：在收到消息的事件图表中，将 `FLocalizableMessage` 变量连接到 `Conv_LocalizableMessageToText` 节点的输入。你需要提供一个 `WorldContextObject`（通常使用 `Self` 或拥有此蓝图的对象）。输出的 `FText` 节点就可以连接到 UI Text Block 的 `Set Text` 函数了。

## C++ 用法

### 头文件引入

```cpp
#include "LocalizableMessageTypes.h" // 核心消息结构 FLocalizableMessage
```

### 基本用法

创建和操作本地化消息的核心是 `FLocalizableMessage` 结构体。以下是一个典型的使用流程：

```cpp
// 来源: 插件核心结构 FLocalizableMessage 的推断用法

// 1. 创建一个本地化消息
FLocalizableMessage NewMessage;
// 通常通过一个专门的构造函数或工厂函数来设置，例如：
// NewMessage = FLocalizableMessage(LOCTABLE_ID(“GameStrings”, “PlayerJoined”), { FFormatNamedArgument(“PlayerName”, FText::FromString(“Tim”)) });
// 注意：实际创建方式取决于插件提供的具体API，以上为概念示例。

// 2. 通过网络复制
// 假设这是一个 AActor 的成员变量
UPROPERTY(Replicated)
FLocalizableMessage SystemMessage;

// 3. 在客户端处理（例如在 OnRep_SystemMessage 中）
if (HasAuthority() == false) // 确保只在客户端执行
{
    ULocalizableMessageLibrary* MessageLib = GetMutableDefault<ULocalizableMessageLibrary>();
    FText DisplayText = MessageLib->Conv_LocalizableMessageToText(this, SystemMessage);
    // 使用 DisplayText 更新 UI
}
```

### 进阶用法

结合 `FLocalizableMessage` 的设计，可以用于实现一个简单的消息分发系统：

```cpp
// 定义一个用于分发不同类型消息的组件
class UGameMessageComponent : public UActorComponent
{
    // ...
    UPROPERTY(ReplicatedUsing = OnRep_GameMessage)
    FLocalizableMessage CachedMessage;

    UFUNCTION()
    void OnRep_GameMessage();

    void BroadcastToAllPlayers(const FLocalizableMessage& Message);
};

// 客户端接收到消息后，根据消息的“键”（如“KillFeed”、“SystemAlert”）可能进行不同的处理
void UGameMessageComponent::OnRep_GameMessage()
{
    // 使用蓝图库进行基本转换
    FText Text = ULocalizableMessageLibrary::Conv_LocalizableMessageToText(this, CachedMessage);
    // 或者，你可以在 C++ 中更高效地解析 CachedMessage，根据其内部参数做更多自定义逻辑
}
```

## Demo 示例

以下示例展示了一个简化的、可复制的本地化消息属性及其在客户端的处理。

**MyActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LocalizableMessageTypes.h"
#include "MyActor.generated.h"

UCLASS()
class MYGAME_API AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    // 可复制的本地化消息属性
    UPROPERTY(ReplicatedUsing = OnRep_Announcement)
    FLocalizableMessage AnnouncementMessage;

    UFUNCTION(Server, Reliable)
    void Server_SetAnnouncement(const FLocalizableMessage& NewMessage);
    void Server_SetAnnouncement_Implementation(const FLocalizableMessage& NewMessage);

protected:
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

private:
    UFUNCTION()
    void OnRep_Announcement();
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "Net/UnrealNetwork.h"
#include "LocalizableMessageLibrary.h" // 为了使用蓝图库函数

AMyActor::AMyActor()
{
    // ...
    bReplicates = true;
}

void AMyActor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyActor, AnnouncementMessage);
}

void AMyActor::Server_SetAnnouncement_Implementation(const FLocalizableMessage& NewMessage)
{
    // 服务器接收并存储消息，自动复制到客户端
    AnnouncementMessage = NewMessage;
}

void AMyActor::OnRep_Announcement()
{
    // 客户端收到复制后的消息
    if (!HasAuthority())
    {
        // 使用 LocalizableMessageBlueprint 模块提供的库函数进行转换
        FText FinalText = ULocalizableMessageLibrary::Conv_LocalizableMessageToText(this, AnnouncementMessage);
        UE_LOG(LogTemp, Log, TEXT("Received Announcement: %s"), *FinalText.ToString());
        // 在这里更新你的 UI 或 HUD 来显示 FinalText
    }
}
```

## 模块依赖

从模块的 Build.cs 文件分析，使用者需要关注以下非通用依赖：

| 模块 | 用途 |
|---|---|
| `CommonUI` | `LocalizableMessage` 模块依赖于它，表明其本地化消息的解析或显示可能与通用的 UI 框架集成。 |
| `LocalizableMessage` | `LocalizableMessageBlueprint` 模块依赖于它，提供了核心的消息类型和逻辑。 |
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | `LocalizableMessageBlueprint` 模块本身无特殊依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF。 |
| 2025-08-12 | `f3d05004` | Made it so that Hud messages could be compared in Blueprints. | 使 HUD 消息在蓝图中可以进行比较。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied uniformly) | 为源文件添加了内联生成的宏。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 转换了符号导出格式。 |
| 2024-12-06 | `3b9c9c2a` | Verse message: helper function to convert a verse::message into FText. | 添加了辅助函数，用于将 Verse 语言的消息转换为 FText。 |

### 维护评价

-   **活跃维护**：插件创建于 2023 年，是相对较新的功能。从提交历史看，在 2025 年仍有实质性功能更新（如蓝图消息比较支持）和引擎基础架构适配，表明它处于活跃维护状态。
-   **功能完善**：最新的提交（`f3d05004`）增加了蓝图功能，说明 Epic 仍在根据内部项目需求（如 Fortnite）完善其 API。
-   **无已知严重问题**：目前没有看到关于此插件的废弃标记或严重问题报告。
-   **推荐使用**：对于需要高效、可本地化网络消息的多人游戏项目，这是一个**推荐使用**的官方工具插件。它解决了网络本地化的核心痛点，并且作为 Epic 官方维护的模块，质量和兼容性有保障。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LocalizableMessage)
-   [官方文档]() （暂无）
-   [测试用例]() （插件目录内未发现公开测试用例，其测试可能存在于引擎内部测试套件中）