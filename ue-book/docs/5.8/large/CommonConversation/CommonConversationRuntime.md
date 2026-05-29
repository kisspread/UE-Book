# Common Conversation

> An *experimental* plugin for authoring graph-based conversation trees

| 属性 | 值 |
|---|---|
| 中文名 | 对话系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CommonConversationRuntime` (Runtime), `CommonConversationGraph` (UncookedOnly), `CommonConversationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation) | |

## 用途

Common Conversation 插件提供了一个用于创建和运行基于图的对话系统的完整框架。它不仅仅是简单的对话树，而是一个强大的、支持网络同步的对话和行为系统。

其核心思想是将对话流程建模为一个**状态机和流程图的结合体**。对话由一系列**任务节点**构成，这些节点可以执行逻辑、检查条件、提供选择并推进对话。系统支持：

*   **多参与者对话**：支持两个或更多角色（如玩家和NPC）同时参与。
*   **客户端-服务器权威模型**：关键逻辑和选择验证在服务器端执行，确保安全，并将结果同步到客户端。客户端只处理显示和用户输入。
*   **动态内容与分支**：任务节点可以在运行时根据游戏状态动态生成对话选项和分支路径。
*   **对话记忆**：系统内置记忆机制，允许NPC或对话实例在对话过程中记住信息（例如玩家的选择、随机结果）。
*   **与游戏功能系统集成**：通过 `GameFeatures` 插件支持，对话资产可以作为游戏功能模块的一部分进行加载和管理。
*   **流式加载**：支持根据对话入口标签按需流式加载对话数据。

简而言之，这个插件存在是为了给开发者提供一个结构化、可扩展且网络同步的解决方案，用于构建超越简单对话菜单的复杂NPC交互。

## 使用场景

*   你在开发一款开放世界RPG，需要与NPC进行多分支、可重复、影响世界状态的深度对话 → 使用 **Common Conversation**。
*   你在开发一款多人在线游戏，需要确保所有玩家看到的对话选项和结果一致，并且选择经过服务器验证 → 使用 **Common Conversation** 的客户端-服务器模型。
*   你的对话需要集成任务系统、物品交易或动态信息查询等复杂逻辑，而非仅仅展示文本 → 将这些逻辑封装在 **对话任务节点** 中。
*   你需要多个NPC同时参与一场对话（例如圆桌会议、小组讨论）→ 利用系统的**多参与者**支持。
*   你希望以图形化（节点编辑器）的方式编辑对话，并且支持将对话资产打包到不同的游戏功能插件中 → 使用配套的 `CommonConversationEditor` 和 `CommonConversationGraph` 模块。

## 蓝图用法

系统在蓝图中主要通过 `UConversationLibrary`、`UConversationContextHelpers` 和 `UConversationParticipantComponent` 暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartConversation` | 在权威端启动一个新对话，指定入口点、发起者、目标和参与者标签。 | `UConversationLibrary` |
| `StartConversationFromGraph` | 同上，但可直接指定一个对话图资产，而非仅通过标签查找。 | `UConversationLibrary` |
| `AdvanceConversation` | 生成一个“推进对话”的任务结果，让对话自动选择下一个分支。 | `UConversationContextHelpers` |
| `PauseConversationAndSendClientChoices` | 暂停对话并向客户端发送包含选项的消息，等待玩家选择。 | `UConversationContextHelpers` |
| `ReturnToLastClientChoice` | 生成一个任务结果，使对话流返回到上一次等待玩家选择的点。 | `UConversationContextHelpers` |
| `AbortConversation` | 中止当前对话。 | `UConversationContextHelpers` |
| `MakeConversationParticipant` | 将一个Actor动态添加到当前对话上下文中。 | `UConversationContextHelpers` |
| `GetConversationParticipant` | 根据标签从对话上下文中获取参与者组件。 | `UConversationContextHelpers` |
| `RequestServerAdvanceConversation` | 客户端调用，向服务器发送请求，携带玩家选择的对话选项。 | `UConversationParticipantComponent` |

### 使用示例（蓝图描述）

1.  **启动一个简单对话**：
    *   一个NPC的蓝图，在某个事件（如与玩家交互）触发时，调用 `StartConversation` 节点。
    *   将 `ConversationEntryTag` 设置为你的对话图中定义的入口标签（如 `Dialogue.Greeting`）。
    *   将 `Instigator` 和 `InstigatorTag` 设置为玩家角色及其对应的参与者标签。
    *   将 `Target` 和 `TargetTag` 设置为NPC自身及其对应的参与者标签。
    *   （可选）指定 `ConversationInstanceClass` 以使用自定义的对话实例类。
    *   调用后，对话将开始。NPC上的 `UConversationParticipantComponent` 会收到 `ConversationStarted` 事件。

2.  **在对话任务节点中提供选择**：
    *   创建一个继承自 `UConversationTaskNode` 的蓝图类。
    *   重写 `ExecuteTaskNode` 函数。在此函数中，你可以执行任何服务器逻辑（如检查金钱、给予物品）。
    *   通过 `Context` 参数，你可以获取当前参与者信息。
    *   要向玩家提供选择，重写 `GatherDynamicChoices` 或 `GatherStaticChoices` 函数。
    *   在这些函数中，使用 `BranchBuilder.AddChoice` 来创建选项，并为每个选项设置 `ChoiceText` 和其他信息。
    *   你的节点需要返回 `FConversationTaskResult`，通常使用 `PauseConversationAndSendClientChoices` 来暂停并发送这些选择。

## C++ 用法

### 头文件引入

```cpp
#include “ConversationLibrary.h” // 用于启动对话
#include “ConversationContext.h” // 用于任务节点中处理上下文和结果
#include “ConversationInstance.h” // 用于操作对话实例
#include “ConversationParticipantComponent.h” // 用于参与者组件
#include “ConversationTaskNode.h” // 用于创建自定义任务节点
```

### 基本用法

**启动一个对话** (在服务器权威代码中)：
```cpp
// 来自 ConversationLibrary.h
if (UWorld* World = GetWorld())
{
    if (UConversationRegistry* ConvRegistry = UConversationRegistry::GetFromWorld(World))
    {
        FGameplayTag EntryPointTag = FGameplayTag::RequestGameplayTag(“Dialogue.MainQuest”);
        AActor* InstigatorActor = PlayerPawn;
        FGameplayTag InstigatorTag = FGameplayTag::RequestGameplayTag(“Conversation.Participant.Player”);
        AActor* TargetActor = SomeNPC;
        FGameplayTag TargetTag = FGameplayTag::RequestGameplayTag(“Conversation.Participant.NPC_Vendor”);

        // 使用默认的对话实例类
        UConversationInstance* ConvInst = UConversationLibrary::StartConversation(
            EntryPointTag, InstigatorActor, InstigatorTag, TargetActor, TargetTag);

        if (ConvInst)
        {
            // 对话已启动，可以进行额外操作
        }
    }
}
```

**创建自定义任务节点** (C++ 继承)：
```cpp
// MyTradeNode.h
UCLASS()
class UMyTradeNode : public UConversationTaskNode
{
    GENERATED_BODY()
public:
    // 执行节点的服务器逻辑
    virtual FConversationTaskResult ExecuteTaskNode_Implementation(const FConversationContext& Context) const override;

    // 收集动态生成的交易选项
    virtual void GatherDynamicChoices(FConversationBranchPointBuilder& BranchBuilder, const FConversationContext& Context) const override;
};

// MyTradeNode.cpp
FConversationTaskResult UMyTradeNode::ExecuteTaskNode_Implementation(const FConversationContext& Context) const
{
    // 示例：玩家选择交易后，在这里执行给予物品、扣除金钱等服务器逻辑
    UConversationParticipantComponent* PlayerComp = Context.GetParticipantComponent(FGameplayTag::RequestGameplayTag(“Conversation.Participant.Player”));
    if (PlayerComp)
    {
        AActor* PlayerActor = PlayerComp->GetOwner();
        // ... 执行交易逻辑
    }
    // 交易逻辑执行完毕后，推进对话到下一个节点（例如感谢语）
    return FConversationTaskResult::AdvanceConversation();
}

void UMyTradeNode::GatherDynamicChoices(FConversationBranchPointBuilder& BranchBuilder, const FConversationContext& Context) const
{
    // 假设我们根据游戏状态动态生成商品列表
    TArray<FString> ShopItems = GetShopItems(); // 你自己的函数
    for (const FString& Item : ShopItems)
    {
        FClientConversationOptionEntry Choice;
        Choice.ChoiceText = FText::FromString(FString::Printf(TEXT(“购买 %s”), *Item));
        Choice.ChoiceTags.AddTag(FGameplayTag::RequestGameplayTag(“Conversation.Choice.Buy”));
        Choice.ChoiceType = EConversationChoiceType::UserChoiceAvailable;

        // 将商品名称作为NodeParameter传递，以便在ExecuteTaskNode中识别具体是哪个商品
        FConversationNodeParameterPair Param(“ItemName”, Item);
        Choice.ChoiceReference.NodeParameters.Add(Param);

        // 将这个选择添加到分支构建器
        BranchBuilder.AddChoice(Context, MoveTemp(Choice));
    }
}
```

### 进阶用法

**处理对话记忆**：
```cpp
// 在任务节点中，可以为当前对话实例或参与者存储记忆
void UMyRecallNode::ExecuteTaskNode_Implementation(const FConversationContext& Context) const
{
    // 获取对话实例记忆（仅在本次对话有效）
    FConversationMemory& InstMemory = Context.GetActiveConversation()->GetInstanceMemory();
    FMyRecallData* RecallData = InstMemory.GetTaskMemory<FMyRecallData>(*this);
    if (!RecallData)
    {
        // 如果是第一次，初始化记忆
        RecallData = new FMyRecallData();
        RecallData->RecalledPhrase = “你好”;
    }

    // 获取NPC参与者记忆（长期记忆，需要NPC有对应的Memory组件）
    if (UConversationParticipantComponent* NPCComp = Context.GetParticipantComponent(FGameplayTag::RequestGameplayTag(“Conversation.Participant.NPC”)))
    {
        FConversationMemory& NPCMemory = NPCComp->GetParticipantMemory();
        FNPCLongTermMemory* NPCLongMem = NPCMemory.GetTaskMemory<FNPCLongTermMemory>(*this);
        // ... 操作NPC的长期记忆
    }
}
```

**链接其他对话（类似子程序调用）**：
使用 `UConversationLinkNode`。在对话图中，放置一个链接节点，设置其 `RemoteEntryTag` 为另一个对话图的入口标签。当对话流到达这个节点时，会跳转到目标对话的入口点继续执行，目标对话结束后会返回。

## Demo 示例

一个最小的 C++ 任务节点，它检查玩家是否拥有某个物品，并根据结果提供不同的选择。

**文件： SimpleItemCheckNode.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “ConversationTaskNode.h”
#include “SimpleItemCheckNode.generated.h”

UCLASS(Blueprintable)
class COMMONCONVERSATIONRUNTIME_API USimpleItemCheckNode : public UConversationTaskNode
{
    GENERATED_BODY()

public:
    // 需要检查的物品标签
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = “Check”)
    FGameplayTag RequiredItemTag;

protected:
    // 服务器端执行逻辑
    virtual FConversationTaskResult ExecuteTaskNode_Implementation(const FConversationContext& Context) const override;

    // 收集条件满足和不满足时的选项
    virtual void GatherStaticChoices(FConversationBranchPointBuilder& BranchBuilder, const FConversationContext& Context) const override;
};
```

**文件： SimpleItemCheckNode.cpp**
```cpp
#include “SimpleItemCheckNode.h”
#include “GameplayTagContainer.h”

FConversationTaskResult USimpleItemCheckNode::ExecuteTaskNode_Implementation(const FConversationContext& Context) const
{
    // 此节点主要提供选择，执行逻辑通常为空，或用于记录状态
    // 真正的检查逻辑在下面的 GatherStaticChoices 和需求检查中
    return FConversationTaskResult::AdvanceConversation();
}

void USimpleItemCheckNode::GatherStaticChoices(FConversationBranchPointBuilder& BranchBuilder, const FConversationContext& Context) const
{
    // 选项1：如果条件满足，提供继续的选项
    FClientConversationOptionEntry ChoiceOK;
    ChoiceOK.ChoiceText = NSLOCTEXT(“Dialog”, “ItemCheckOK”, “我带着你需要的东西。”);
    ChoiceOK.ChoiceType = EConversationChoiceType::UserChoiceAvailable;
    BranchBuilder.AddChoice(Context, MoveTemp(ChoiceOK));

    // 选项2：一个通用的“再见”选项
    FClientConversationOptionEntry ChoiceBye;
    ChoiceBye.ChoiceText = NSLOCTEXT(“Dialog”, “Goodbye”, “再见。”);
    ChoiceBye.ChoiceType = EConversationChoiceType::UserChoiceAvailable;
    BranchBuilder.AddChoice(Context, MoveTemp(ChoiceBye));
}

// 注意：还需要一个配套的需求节点（UConversationRequirementNode的子类）来检查玩家背包。
// 或者，你可以在此节点的 IsRequirementSatisfied 中实现检查，并设置 bIgnoreRequirementsWhileAdvancingConversations = true。
```

## 模块依赖

从模块的 Build.cs 分析，要使用此插件，你的项目模块通常需要依赖 `CommonConversationRuntime`。该插件本身对以下非标准模块有强依赖：

| 模块 | 用途 |
|---|---|
| `GameFeatures` | 用于支持游戏功能插件与对话系统的集成，实现对话资产的模块化加载和状态管理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-17 | `5aabf92f` | Allowing conversation task nodes to choose branches in a specific order when advancing the conversat | 为对话任务节点增加按特定顺序选择分支的能力。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的UE_LOG日志宏迁移到新的UE_LOGF格式。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃旧API，引入新API，并修复编译警告。 |
| 2026-03-24 | `d413371b` | [AI][Conversation] Add ConversationToolset plugin | 引入一个用于对话编辑的配套工具集插件。 |
| 2026-03-12 | `b7b7adad` | Add an option to stop and manually build the conversation registry dependencies graph when needed, i | 为对话注册表增加手动构建依赖图的选项，优化加载逻辑。 |

### 维护评价

**综合评价：活跃维护中的实验性核心系统**

*   **创建时间**：创建于 2021 年初，已有约 4 年历史，对于一个复杂系统来说正值壮年。
*   **维护频率**：**维护非常活跃**。从最近的提交记录看，在 2026 年 3-4 月间有多次功能性更新和优化，包括新增节点顺序控制、引入配套工具集插件、优化依赖图构建等。这表明 Epic 的 AI/对话团队仍在积极投入开发和改进此系统。
*   **已知限制**：
    1.  **实验性**：插件明确标记为 `IsExperimentalVersion=true` 且默认禁用（`EnabledByDefault=false`），意味着其 API 可能在未来版本中发生破坏性变更。
    2.  **文档缺失**：官方没有提供文档（DocsURL 为空），学习和使用主要依赖源码、注释和社区探索。
    3.  **网络同步复杂性**：系统基于客户端-服务器权威模型设计，对于纯单机游戏或不熟悉网络编程的开发者可能有较高的理解门槛。
*   **推荐使用**：
    *   **推荐**：如果你正在开发一个需要**复杂、网络同步对话系统**的项目，并且团队有能力承担一个实验性系统的集成和维护成本，那么这是一个非常强大且值得投入学习的基础框架。它是 UE5 官方对话系统的基石。
    *   **谨慎**：如果你的需求非常简单（例如单机、线性对话），或者项目周期紧张、无法接受未来 API 变更的风险，可以考虑更简单的第三方解决方案或自行实现。
    *   **建议**：建议在 **5.8 或更新版本**的 UE5 中使用此插件，以获取最新的功能和修复。始终关注其更新日志，及时适配 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation)
- [官方文档](https://docs.unrealengine.com/) (无直接文档链接，请参考引擎文档或社区资源)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation/Tests) (路径推测，可能存在)