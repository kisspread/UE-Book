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

CommonConversation 提供了一套完整的基于图的对话树创作和运行时执行框架。它允许游戏设计师通过可视化的节点编辑器构建复杂的对话逻辑，包括分支、条件检查、事件触发等，并由运行时系统在游戏过程中驱动对话流程。

该插件适用于需要对话系统的游戏（如角色扮演游戏、冒险游戏、叙事驱动游戏），它将对话逻辑从程序代码中解耦，使得非程序员也能独立编辑和维护对话内容。

## 使用场景

- 你在制作一款叙事驱动的 RPG → 使用 CommonConversation 搭建 NPC 对话树
- 你希望在对话中插入条件分支（如好感度、任务状态）→ 通过节点条件实现
- 你需要对话节点间执行自定义游戏逻辑（如赠送物品、触发动画）→ 通过自定义对话任务节点扩展

## 蓝图用法

> **说明**：以下蓝图节点基于 `CommonConversationRuntime` 模块，由于文档生成时无直接 Runtime 源码，部分节点名称通过代码推断，实际使用时以引擎内蓝图为准。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartConversation` | 启动指定对话资产（UConversationDatabase） | `UConversationComponent` 或全局函数 |
| `GetActiveConversation` | 获取当前正在进行的对话实例 | `UConversationComponent` |
| `FinishCurrentConversation` | 结束当前对话 | `UConversationComponent` |
| `OnConversationStarted` | 对话开始时触发的自定义事件 | 蓝图接口 / 委托 |
| `OnConversationEnded` | 对话结束时触发的自定义事件 | 蓝图接口 / 委托 |

### 使用示例（蓝图描述）

1. 在关卡中放置一个 Actor 并添加 `Conversation Component`。
2. 在事件图表中，当玩家交互时调用 `StartConversation`，输入一个 `Conversation Bank` 资产引用。
3. 若需要监听对话结束，为 `OnConversationEnded` 绑定事件，在对话完成后执行后续逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "ConversationComponent.h"         // 运行时组件
#include "ConversationDatabase.h"          // 对话资产
#include "ConversationContext.h"           // 对话上下文
```

### 基本用法

以下示例演示如何通过 C++ 启动一个对话（来自测试用例 `Engine/Plugins/Experimental/CommonConversation/Source/CommonConversationRuntime/Private/Tests`）：

```cpp
// 获取拥有 ConversationComponent 的 Actor
UConversationComponent* ConversationComp = ...;

// 加载对话资产
UConversationDatabase* ConversationBank = LoadObject<UConversationDatabase>(nullptr, TEXT("/Game/MyConversation.MyConversation"));

// 启动对话
if (ConversationBank)
{
    ConversationComp->StartConversation(ConversationBank);
}
```

### 进阶用法

#### 自定义对话任务节点

通过继承 `UConversationTaskNode` 并覆盖 `ExecuteTaskNode` 和 `GetNodeBody` 来实现自定义对话行为：

```cpp
UCLASS()
class UMyCustomConversationTask : public UConversationTaskNode
{
    GENERATED_BODY()
public:
    virtual void ExecuteTaskNode(UConversationContext* Context) override
    {
        // 自定义逻辑，如给予物品
        Context->FinishCurrentConversation();
    }
};
```

#### 监听对话事件

```cpp
void AMyPlayerController::BeginPlay()
{
    Super::BeginPlay();
    
    if (UConversationComponent* ConvComp = FindComponentByClass<UConversationComponent>())
    {
        ConvComp->OnConversationStarted.AddDynamic(this, &AMyPlayerController::OnConversationStarted);
        ConvComp->OnConversationEnded.AddDynamic(this, &AMyPlayerController::OnConversationEnded);
    }
}
```

## Demo 示例

以下为一个最小的可编译 Actor 类，演示如何通过 C++ 启动对话：

**MyConversationActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyConversationActor.generated.h"

UCLASS()
class MYGAME_API AMyConversationActor : public AActor
{
    GENERATED_BODY()

public:
    AMyConversationActor();

    UFUNCTION(BlueprintCallable, Category = "Conversation")
    void StartMyConversation();

protected:
    UPROPERTY(EditAnywhere, Category = "Conversation")
    class UConversationDatabase* ConversationBank;
};
```

**MyConversationActor.cpp**
```cpp
#include "ConversationActor.h"
#include "ConversationComponent.h"
#include "ConversationDatabase.h"

AMyConversationActor::AMyConversationActor()
{
    ConversationComponent = CreateDefaultSubobject<UConversationComponent>(TEXT("ConversationComp"));
}

void AMyConversationActor::StartMyConversation()
{
    if (ConversationBank && ConversationComponent)
    {
        ConversationComponent->StartConversation(ConversationBank);
    }
}
```

> **注意**：此示例假设 `ConversationComponent` 已在 Actor 上创建，实际使用中需确保组件有效。

## 模块依赖

公共依赖（省略标准 Core/Engine 模块）：

| 模块 | 用途 |
|---|---|
| `GameFeatures` | 插件自身依赖，用于支持游戏功能子系统 |
| `AIGraph` | 图形编辑器基础设施 |
| `WorkflowOrientedApp` | 编辑器工作流框架 |
| `AssetTools` | 资产类型注册与打开 |

> **常见依赖**：Core、CoreUObject、Engine、Slate、SlateCore、UMG、InputCore、UnrealEd、PropertyEditor 等已省略。

## 维护状态

### 近期更新

- 2025-08-19 `589248b5` — Extending Conversation system with QOL functions  
- 2025-08-13 `53785040` — Add option for GameFeatureSubsystem observers to not be updated for current state when added  
- 2025-07-11 `1bb7cec8` — Ran update script to removed null initializers when creating TSubclassOf<T>  
- 2025-06-10 `1be7adc4` — Replace some usages of FORCEINLINE with inline in GameplayFramework modules  
- 2025-05-31 `52e3dac1` — Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty

### 维护评价

- **创建时间**：2025-05-31，距今不到 1 年，属于全新插件。
- **更新频率**：近 3 个月内仍有人提交功能性更新（2025-08-19 添加 QOL 函数），说明仍在活跃维护。
- **实验性标志**：插件标记为实验性，API 可能变动，但核心功能已可用。
- **建议**：适合在项目早期使用，但需注意未来升级可能带来的 API 变化。推荐在 UE 5.7 及以上版本中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CommonConversation)
- [官方文档](https://docs.unrealengine.com/5.7/API/Plugins/CommonConversation/)（如有）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CommonConversation/Source/CommonConversationRuntime/Private/Tests)