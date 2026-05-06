# Common Conversation

> An *experimental* plugin for authoring graph-based conversation trees

| 属性 | 值 |
|---|---|
| 中文名 | 通用对话 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CommonConversationRuntime` (Runtime), `CommonConversationGraph` (UncookedOnly), `CommonConversationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CommonConversation) | |

## 用途

Common Conversation 提供了一个可扩展的、基于图表的对话系统，用于在游戏中创建复杂的 NPC 交互。不同于传统的线性对话树，它使用节点图来定义对话流程，支持分支、条件、副作用和动态选择。插件设计为与 Game Features 系统集成，允许将对话内容作为 Game Feature 的一部分进行分发和流式加载。

核心运行时模块 `CommonConversationRuntime` 负责对话的实例化、执行、参与者管理、内存管理和网络复制（面向服务端权威）。`CommonConversationGraph` 提供编辑器中的图编辑器节点，`CommonConversationEditor` 包含资产编辑器和属性面板。

## 使用场景

- **需要复杂的多分支对话**：NPC 拥有多个对话选项，每个选项受条件控制（如任务状态、玩家等级）。
- **对话中需要触发游戏逻辑**：在对话节点执行任务（如给予物品、改变 NPC 状态、播放动画），而不是简单文本展示。
- **对话需要动态反馈**：根据上下文生成动态选择项（如购买菜单、随机选项）。
- **多人游戏对话**：对话状态在服务器端管理，通过 RPC 同步到客户端。
- **将对话内容拆分为功能模块**：利用 Game Features 实现 DLC 或条件性内容加载。

## 蓝图用法

Common Conversation 提供了一系列可复写的节点（蓝图 NativeEvent）和可直接调用的静态函数。以下是主要蓝图 API。

### 启动和推进对话

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartConversation` | 在服务端启动一个对话，根据 entry tag 查找并实例化对话 | `UConversationLibrary` |
| `StartConversationFromGraph` | 启动一个指向特定图的对话（可指定 entry point 标识符） | `UConversationLibrary` |
| `RequestServerAdvanceConversation` | 客户端向服务器发送前进对话请求（包含选择的选择） | `UConversationParticipantComponent` |
| `ServerAdvanceConversation`（RPC） | 服务端实际推进对话的逻辑节点（内部使用） | `UConversationParticipantComponent` |

### 参与者查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsInActiveConversation` | 检查此参与者当前是否处于活跃对话中 | `UConversationParticipantComponent` |
| `GetParticipantDisplayName` | 获取参与者的显示名称（可复写） | `UConversationParticipantComponent` |
| `GetParticipantActor` | 根据 tag 获取指定参与者的 Actor | `UConversationParticipantComponent` |
| `GetOtherParticipantActors` | 获取对话中除自己外的所有参与者 | `UConversationParticipantComponent` |
| `GetParticipant`（蓝图不可直接调用） | 通过 tag 获取参与者条目（可用于 C++） | `UConversationInstance` |

### 可覆盖的节点逻辑（NativeEvent）

这些函数通常用于创建自定义对话节点蓝图子类。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsRequirementSatisfied` | 判断是否可以显示此节点（返回 Passed/FailedButVisible/FailedAndHidden） | `UConversationRequirementNode` |
| `FillChoice` | 当节点作为选择项时，填充显示文本和附加数据 | `UConversationChoiceNode` |
| `ExecuteTaskNode` | 执行任务的主要逻辑，返回 `FConversationTaskResult` 控制流程 | `UConversationTaskNode` |
| `ExecuteClientEffects` | 在客户端执行视觉效果或副作用（BlueprintCosmetic） | `UConversationTaskNode` |
| `IsRequirementSatisfied`（任务节点） | 任务自身的需求判断（高级用法） | `UConversationTaskNode` |
| `GetNodeBodyColor` | 返回编辑器节点的背景颜色 | `UConversationTaskNode` |
| `ServerCauseSideEffect` | 服务端副作用逻辑 | `UConversationSideEffectNode` |
| `ClientCauseSideEffect` | 客户端副作用逻辑（BlueprintCosmetic） | `UConversationSideEffectNode` |
| `GatherChoiceInfo` | 收集静态选择信息（用于分支） | `UConversationTaskNode` |
| `GatherStaticChoices` | 返回静态选择项数组 | `UConversationTaskNode` |
| `GatherDynamicChoices` | 返回动态选择项数组 | `UConversationTaskNode` |

### 常用结构体与枚举

- `EConversationTaskResultType`：控制对话流程（AdvanceConversation、PauseConversationAndSendClientChoices 等）。
- `FConversationTaskResult`：任务执行结果，包含类型和可选消息。
- `FClientConversationMessage`：发送给客户端的对话消息（文本、参与者、选择项）。
- `FClientConversationOptionEntry`：单个选择项（显示文本、标签、辅助数据）。
- `FConversationBranchPointBuilder`：用于在任务节点中构建分支选择。

## C++ 用法

### 头文件引入

```cpp
#include "ConversationLibrary.h"
#include "ConversationParticipantComponent.h"
#include "ConversationInstance.h"
```

### 基本用法

**启动对话（服务端）**

```cpp
// 使用通用 entry point tag 启动对话
UConversationLibrary::StartConversation(
    EntryPointTag,          // FGameplayTag 标识对话入口
    InstigatorActor,        // 发起对话的 Actor（如玩家角色）
    InstigatorTag,          // 发起者的 Participant Tag（如 "Player"）
    TargetActor,            // 目标 Actor（如 NPC）
    TargetTag,              // 目标的 Participant Tag（如 "NPC"）
    ConversationInstanceClass // 可选的 UConversationInstance 子类
);
```

**从指定 Graph 启动**

```cpp
UConversationLibrary::StartConversationFromGraph(
    EntryPointTag,
    InstigatorActor,
    InstigatorTag,
    TargetActor,
    TargetTag,
    ConversationDatabaseAsset  // 指向 UConversationDatabase 资产
);
```

**客户端请求推进对话**

```cpp
// 在参与者组件上调用
UConversationParticipantComponent* Comp = GetComponentByClass<UConversationParticipantComponent>();
FAdvanceConversationRequest Request;
Request.Choice.ChoiceText = FText::FromString("Take the sword");
// 可选：指定选择项对应的节点 GUID
Request.Choice.ChoiceNodeGUID = SomeGUID;
Comp->RequestServerAdvanceConversation(Request);
```

**获取对话实例并执行服务器操作**

```cpp
// 在 ConversationInstance 子类中（服务端）
void UMyConversationInstance::ExecuteSomeAction()
{
    ServerAdvanceConversation(FAdvanceConversationRequest());
    // 或 ServerRefreshConversationChoices()
}
```

**注册参与者和启动对话（C++ 高级）**

```cpp
// 创建对话实例并手动赋值参与者
UConversationInstance* Convo = NewObject<UConversationInstance>(this);
Convo->ServerAssignParticipant(FGameplayTag::RequestGameplayTag("Player"), PlayerActor);
Convo->ServerAssignParticipant(FGameplayTag::RequestGameplayTag("NPC"), NPCActor);
Convo->ServerStartConversation(EntryPointTag);
```

**从 ConversationRegistry 获取运行时节点**

```cpp
UConversationRegistry* Registry = UConversationRegistry::GetFromWorld(GetWorld());
// 根据 GUID 获取节点
UConversationNode* Node = Registry->GetRuntimeNodeFromGUID(NodeGUID);
// 获取 entry point guid 列表
TArray<FGuid> Guids = Registry->GetEntryPointGUIDs(EntryPointTag);
```

### 进阶用法

**创建自定义对话任务节点（C++）**

```cpp
// MyTaskNode.h
UCLASS()
class UMyTaskNode : public UConversationTaskNode
{
    GENERATED_BODY()
public:
    virtual FConversationTaskResult ExecuteTaskNode_Implementation(const FConversationContext& Context) const override
    {
        // 向玩家发送消息并暂停显示选择
        FClientConversationMessage Message;
        Message.NodeParameters.Emplace("Greeting", "Hello!");
        return FConversationTaskResult::PauseConversationAndSendClientChoices(Message);
    }
};
```

**使用内存系统存储任务数据**

```cpp
// 定义内存结构
USTRUCT()
struct FMyTaskMemory
{
    GENERATED_BODY()
    int32 TimesVisited;
};

// 在任务节点中获取/设置
void UMyTaskNode::ExecuteTaskNode_Implementation(const FConversationContext& Context) const
{
    FMyTaskMemory* Memory = Context.GetConversationMemory().GetTaskMemory<FMyTaskMemory>(*this);
    if (Memory)
    {
        Memory->TimesVisited++;
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何从指定对话数据库启动对话。

**MyConversationStarter.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyConversationStarter.generated.h"

UCLASS()
class AMyConversationStarter : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Conversation")
    class UConversationDatabase* ConversationDatabase;

    UPROPERTY(EditAnywhere, Category = "Conversation")
    FGameplayTag EntryPointTag;
};
```

**MyConversationStarter.cpp**

```cpp
#include "MyConversationStarter.h"
#include "ConversationLibrary.h"
#include "ConversationParticipantComponent.h"
#include "ConversationInstance.h"

void AMyConversationStarter::BeginPlay()
{
    Super::BeginPlay();

    if (!HasAuthority()) return;

    // 找到参与者
    AActor* Instigator = GetWorld()->GetFirstPlayerController()->GetPawn();
    AActor* Target = this;

    // 确保参与者组件存在
    UConversationParticipantComponent* InstigatorComp = Instigator->FindComponentByClass<UConversationParticipantComponent>();
    if (!InstigatorComp)
    {
        InstigatorComp = NewObject<UConversationParticipantComponent>(Instigator);
        Instigator->AddOwnedComponent(InstigatorComp);
        InstigatorComp->RegisterComponent();
    }
    UConversationParticipantComponent* TargetComp = Target->FindComponentByClass<UConversationParticipantComponent>();
    if (!TargetComp)
    {
        TargetComp = NewObject<UConversationParticipantComponent>(Target);
        Target->AddOwnedComponent(TargetComp);
        TargetComp->RegisterComponent();
    }

    // 启动对话
    UConversationInstance* Conversation = UConversationLibrary::StartConversationFromGraph(
        EntryPointTag,
        Instigator,
        FGameplayTag::RequestGameplayTag("Player"),
        Target,
        FGameplayTag::RequestGameplayTag("NPC"),
        ConversationDatabase
    );
}
```

## 模块依赖

CommonConversationRuntime 依赖以下核心模块（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `GameFeatures` | 与 Game Features 系统集成，支持对话内容的条件性加载和分发 |
| `GameplayTags` | 对话入口点、参与者标识、选择标签等相关功能 |
| `DeveloperSettings` | 对话配置（如默认对话实例类） |

此外，`CommonConversationGraph` 和 `CommonConversationEditor` 额外依赖 `UnrealEd`、`Kismet`、`BlueprintGraph` 等编辑器模块。

## 维护状态

### 近期更新

- 2025-08-19 `589248b5` — Extending Conversation system with QOL functions（扩展对话系统，增加生活质量功能）
- 2025-08-13 `53785040` — Add option for GameFeatureSubsystem observers to not be updated for current state when added（更新 GameFeature 观察者选项）
- 2025-07-11 `1bb7cec8` — Ran update script to removed null initializers when creating TSubclassOf<T>（更新脚本，移除 TSubclassOf 的空初始化器）
- 2025-06-10 `1be7adc4` — Replace some usages of FORCEINLINE with inline in GameplayFramework modules（替换 FORCEINLINE 为 inline）
- 2025-05-31 `52e3dac1` — Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars（修复 DLL 存储声明）

### 维护评价

Common Conversation 是一个**实验性**插件，创建于 2025 年 5 月，至今约三个月。近期（2025 年 8 月）仍有实质性功能更新（QOL 功能扩展），表明团队在积极改进。代码基础较新，API 设计现代，与 Game Features 集成良好，适合需要高度模块化对话系统的项目。作为实验性插件，其 API 可能在未来版本中发生不兼容改动；建议在采用前关注后续引擎更新。总体推荐在新项目中使用，但需做好跟踪更新的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CommonConversation)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CommonConversation/Tests)（推测位置，实际路径可能不存在）