# Common Conversation

> An *experimental* plugin for authoring graph-based conversation trees

| 属性 | 值 |
|---|---|
| 中文名 | 通用对话系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CommonConversationRuntime` (Runtime), `CommonConversationGraph` (UncookedOnly), `CommonConversationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation) | |

## 用途

Common Conversation 是一个用于创建和驱动基于图（Graph-Based）的对话系统的实验性框架。它解决了在 UE 中构建复杂、分支化对话流程时缺乏标准化工具和运行时的问题。与传统的基于状态机或数组的对话系统不同，它提供了一个专用的编辑器图界面，让策划和开发者能够直观地设计对话树、选项、分支和结果，并内置了运行时引擎来在游戏过程中驱动这些对话。

## 使用场景

- 你正在开发一款剧情驱动的 RPG 或互动叙事游戏，需要设计包含大量分支和条件选项的对话系统。
- 你需要一个对话系统，其行为能够与游戏任务、背包、好感度等其他游戏系统深度集成。
- 你希望将对话内容作为游戏功能（Game Feature）的一部分，实现模块化加载和卸载。
- 你的团队中有策划成员，希望他们能通过一个直观的图形界面独立编写和调整对话逻辑。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Conversation` | 为指定角色启动一个对话实例。 | `UConversationManager` |
| `Advance Conversation` | 在对话中前进，由玩家选择选项或由系统自动推进。 | `UConversationInstance` |
| `Get Available Choices` | 获取当前对话节点下可供玩家选择的选项列表。 | `UConversationInstance` |
| `Choose Option` | 玩家选择一个特定的对话选项。 | `UConversationInstance` |

### 使用示例（蓝图描述）

1.  在角色蓝图中，当需要触发对话时（如与NPC交互），调用 `Start Conversation` 节点，传入对话资产和参与者。
2.  对话开始后，UI蓝图监听 `On Conversation Updated` 等委托事件。
3.  在事件中，调用 `Get Available Choices` 获取当前选项，并将其显示为UI按钮。
4.  当玩家点击某个选项按钮时，调用 `Choose Option` 节点。
5.  系统根据选择执行后续逻辑（如播放动画、触发任务），并通过 `Advance Conversation` 推进到下一阶段。

## C++ 用法

### 头文件引入

```cpp
#include “CommonConversationRuntime.h” // 核心运行时
// 根据需要包含其他子模块头文件
```

### 基本用法

以下示例展示了如何用 C++ 启动一个基本的对话。

```cpp
// 在某个Actor（如NPC）或管理器中
void AMyNPC::StartInteraction(APlayerController* PlayerController)
{
    // 假设已持有对话资产引用 FConversationAssetHandle ConversationHandle
    if (UConversationSubsystem* ConvSubsystem = GetWorld()->GetSubsystem<UConversationSubsystem>())
    {
        // 创建一个对话实例
        UConversationInstance* ConvInstance = ConvSubsystem->StartConversation(
            ConversationHandle,
            { this, PlayerController->GetPawn() } // 参与者数组
        );

        if (ConvInstance)
        {
            // 绑定对话状态更新的回调
            ConvInstance->OnConversationUpdated.AddDynamic(this, &AMyNPC::HandleConversationUpdate);
        }
    }
}

void AMyNPC::HandleConversationUpdate(UConversationInstance* Instance)
{
    // 这里可以查询当前选项，或执行特定逻辑
    TArray<FConversationNodeHandle> Choices = Instance->GetAvailableChoices();
    // ... 将选项传递给UI
}
```
*（代码基于对 `UConversationSubsystem` 和 `UConversationInstance` 接口的推断）*

### 进阶用法

结合 Game Features 系统，可以将对话内容打包成独立模块，并在运行时动态启用/禁用。这通常通过 `UGameFeatureAction_AddConversation` 等动作来实现。

## Demo 示例

一个最小化的 C++ 示例，展示如何创建并启动一个简单的对话实例。

**MyDialogActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "CommonConversationTypes.h"
#include "MyDialogActor.generated.h"

class UConversationInstance;

UCLASS()
class AMyDialogActor : public AActor
{
    GENERATED_BODY()

public:
    void StartDialog(AActor* Participant);

private:
    UPROPERTY()
    FConversationAssetHandle DialogAsset;

    UPROPERTY()
    TObjectPtr<UConversationInstance> ActiveDialog;
};
```

**MyDialogActor.cpp**
```cpp
#include "MyDialogActor.h"
#include "ConversationSubsystem.h"
#include "ConversationInstance.h"

void AMyDialogActor::StartDialog(AActor* Participant)
{
    UWorld* World = GetWorld();
    if (!World) return;

    if (UConversationSubsystem* Subsystem = World->GetSubsystem<UConversationSubsystem>())
    {
        // 使用一个硬编码或数据资产中定义的对话句柄启动对话
        ActiveDialog = Subsystem->StartConversation(DialogAsset, { this, Participant });
        
        if (ActiveDialog)
        {
            UE_LOG(LogTemp, Log, TEXT(“对话已启动。”));
            // 这里可以继续绑定委托，驱动UI
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameFeatures` | 提供游戏功能插件化基础设施，本插件可作为游戏功能动态加载。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-17 | `5aabf92f` | Allowing conversation task nodes to choose branches in a specific order when advancing the conversat | 对话任务节点现在可以按特定顺序选择分支推进对话 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到新的UE_LOGF宏 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃了旧的带bool参数的函数，引入了新的枚举参数版本 |
| 2026-03-24 | `d413371b` | [AI][Conversation] Add ConversationToolset plugin | 添加了独立的 ConversationToolset 插件 |
| 2026-03-12 | `b7b7adad` | Add an option to stop and manually build the conversation registry dependencies graph when needed, i | 新增手动构建对话注册依赖图的选项 |

### 维护评价

- **状态**：**活跃维护中**。
- **年龄**：插件创建于 2021 年，已有约 4 年历史，但相对于 UE 核心系统仍较新。
- **更新频率**：最近 1 个月内有多次提交，且包含功能新增（如对话分支顺序控制、工具集插件）、API 优化（日志宏迁移）和底层改进（对象枚举函数）。这表明该插件仍在被积极开发和使用。
- **实验性**：插件仍标记为实验性（`IsExperimentalVersion=true`）且默认未启用。这意味着 API 可能发生破坏性更改，不建议在面向最终用户的生产项目中直接使用，除非准备好跟踪和更新。
- **推荐**：对于原型开发、内部工具或实验性项目，这是一个非常有价值和前瞻性的对话系统框架，值得投入时间学习和使用。对于正式生产项目，需谨慎评估其稳定性和长期支持策略。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation)
- 官方文档：暂无
- 测试用例：插件目录内未提供标准测试文件。