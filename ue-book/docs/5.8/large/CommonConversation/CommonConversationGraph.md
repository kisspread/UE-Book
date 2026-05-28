# Common Conversation

> An *experimental* plugin for authoring graph-based conversation trees（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 对话系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CommonConversationRuntime` (Runtime), `CommonConversationGraph` (UncookedOnly), `CommonConversationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation) | |

## 用途

CommonConversation 是一个用于构建基于图形的对话树的实验性插件。它解决的核心问题是为游戏提供一个可视化的、基于节点的对话编辑系统，让设计师能够直观地创建和管理复杂的对话流程，而无需编写大量代码。

这个插件的设计思路是将对话流程分解为不同类型的节点（如任务节点、选择节点、需求节点、副作用节点等），通过连接这些节点来构建对话的逻辑分支。它支持运行时对话的执行和编辑器内的可视化设计，特别适合需要复杂分支对话系统的游戏，如 RPG、冒险游戏或叙事驱动的游戏。

## 使用场景

- 你在制作一款 RPG 游戏，需要与 NPC 进行多分支、有条件的对话 → 使用 CommonConversation 创建对话树
- 你需要设计师和编剧能够独立设计对话流程，无需程序员介入 → 使用 CommonConversation 的可视化编辑器
- 对话系统需要根据游戏状态（如玩家等级、任务进度）动态改变对话选项 → 使用需求节点和条件系统
- 对话执行需要触发游戏内事件（如获得物品、触发任务） → 使用副作用节点

## 蓝图用法

**注意**：由于插件的实验性质和编辑器模块的焦点，大部分运行时 API 可能在 `CommonConversationRuntime` 模块中，但源码分析中未包含该模块的详细内容。以下是基于已有代码的推断。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 对话图编译 | 编译对话图数据，生成运行时对话数据库 | `FConversationCompiler` |
| 重建对话库 | 重新编译整个对话数据库 | `FConversationCompiler::RebuildBank` |
| 添加新图 | 在对话数据库中添加新的对话图 | `FConversationCompiler::AddNewGraph` |

### 使用示例（蓝图描述）

1. **创建对话资产**：在编辑器中右键 → Gameplay → Common Conversation → 创建对话资产。
2. **编辑对话图**：双击打开对话资产，进入图形编辑界面。从右键菜单添加节点：
   - **入口点 (Entry Point)**：对话的起始节点
   - **任务节点 (Task)**：包含对话文本或任务
   - **选择节点 (Choice)**：提供玩家选择分支
   - **需求节点 (Requirement)**：控制对话选项是否可用的条件
   - **副作用节点 (Side Effect)**：对话触发的事件
3. **连接节点**：拖拽节点间的引脚进行连接，构建对话流程。
4. **编译对话**：编辑完成后，系统会自动或手动编译对话图，生成运行时数据库。

## C++ 用法

### 头文件引入

```cpp
// 对话编译器
#include "ConversationCompiler.h"

// 对话图相关
#include "ConversationGraph.h"
#include "ConversationGraphNode.h"
```

### 基本用法

**对话图编译** - 来源: `Public/ConversationCompiler.h`

```cpp
// 获取对话数据库中的图数量
UConversationDatabase* ConversationAsset = /* 获取对话资产 */;
int32 NumGraphs = FConversationCompiler::GetNumGraphs(ConversationAsset);

// 获取指定索引的图
UConversationGraph* Graph = FConversationCompiler::GetGraphFromBank(ConversationAsset, 0);

// 重建整个对话库
FConversationCompiler::RebuildBank(ConversationAsset);

// 添加新图
UConversationGraph* NewGraph = FConversationCompiler::AddNewGraph(ConversationAsset, TEXT("NewDialogueBranch"));
```

**遍历连接的节点** - 来源: `Public/ConversationCompiler.h`

```cpp
// 遍历从某个引脚出发的所有对话节点（跳过连接点）
UEdGraphPin* SomePin = /* 获取引脚 */;
FConversationCompiler::ForeachConnectedOutgoingConversationNode(SomePin, 
    [](UConversationGraphNode* Node)
    {
        // 处理每个连接的节点
        UE_LOG(LogTemp, Log, TEXT("Found node: %s"), *Node->GetNodeTitle(ENodeTitleType::FullTitle).ToString());
    });

// 按左到右顺序遍历（深度优先遍历连接点）
FConversationCompiler::ForeachConnectedOutgoingConversationNodeSorted(SomePin,
    [](UConversationGraphNode* Node)
    {
        // 按可视化顺序处理节点
    });
```

### 进阶用法

**检查连接限制** - 来源: `Public/ConversationGraphNode.h` 和 `Public/ConversationGraphNode_Knot.h`

```cpp
// 检查两个节点之间是否可以连接
UConversationGraphNode* NodeA = /* 获取节点A */;
UConversationGraphNode* NodeB = /* 获取节点B */;
FText ErrorMessage;
bool bCanConnect = NodeA->IsOutBoundConnectionAllowed(NodeB, ErrorMessage);

if (!bCanConnect)
{
    UE_LOG(LogTemp, Warning, TEXT("Cannot connect: %s"), *ErrorMessage.ToString());
}

// 检查与连接点(Knot)的连接限制
UConversationGraphNode_Knot* KnotNode = /* 获取连接点 */;
bool bCanConnectToKnot = NodeA->IsOutBoundConnectionAllowed(KnotNode, ErrorMessage);
```

**获取连接点的收集节点** - 来源: `Public/ConversationGraphNode_Knot.h`

```cpp
// 从连接点收集所有入向的对话图节点
UConversationGraphNode_Knot* Knot = /* 获取连接点 */;
TArray<UConversationGraphNode*> InboundNodes;
Knot->GatherAllInBoundGraphNodes(InboundNodes);

// 收集所有出向的对话图节点
TArray<UConversationGraphNode*> OutboundNodes;
Knot->GatherAllOutBoundGraphNodes(OutboundNodes);
```

## Demo 示例

以下是一个最小示例，展示如何在 C++ 中访问和编译对话系统。

```cpp
// MyDialogueManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDialogueManager.generated.h"

class UConversationDatabase;

UCLASS()
class AMyDialogueManager : public AActor
{
    GENERATED_BODY()

public:
    AMyDialogueManager();

    // 对话数据库资产
    UPROPERTY(EditAnywhere, Category = "Dialogue")
    UConversationDatabase* DialogueAsset;

    // 编译对话库
    UFUNCTION(BlueprintCallable, Category = "Dialogue")
    void CompileDialogue();

    // 获取第一个对话图
    UFUNCTION(BlueprintCallable, Category = "Dialogue")
    UConversationGraph* GetFirstGraph();

protected:
    virtual void BeginPlay() override;
};

// MyDialogueManager.cpp
#include "MyDialogueManager.h"
#include "ConversationCompiler.h"
#include "ConversationGraph.h"
#include "ConversationDatabase.h" // 假设存在的对话数据库类

AMyDialogueManager::AMyDialogueManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDialogueManager::BeginPlay()
{
    Super::BeginPlay();
}

void AMyDialogueManager::CompileDialogue()
{
    if (DialogueAsset)
    {
        // 编译整个对话库
        FConversationCompiler::RebuildBank(DialogueAsset);
        
        UE_LOG(LogTemp, Log, TEXT("Dialogue asset compiled successfully"));
        
        // 打印图数量
        int32 NumGraphs = FConversationCompiler::GetNumGraphs(DialogueAsset);
        UE_LOG(LogTemp, Log, TEXT("Number of dialogue graphs: %d"), NumGraphs);
    }
}

UConversationGraph* AMyDialogueManager::GetFirstGraph()
{
    if (DialogueAsset && FConversationCompiler::GetNumGraphs(DialogueAsset) > 0)
    {
        // 获取第一个图
        return FConversationCompiler::GetGraphFromBank(DialogueAsset, 0);
    }
    return nullptr;
}
```

## 模块依赖

从 Build.cs 分析，以下是该插件的特殊依赖。由于插件是实验性的，依赖可能随版本变化。

| 模块 | 用途 |
|---|---|
| `GameFeatures` | 游戏功能插件框架，用于模块化游戏功能 |
| `AIGraph` | AI 图表基础框架，对话图继承自 AI 图表 |
| `GraphEditor` | 图形编辑器框架，用于对话图的可视化编辑 |

**注意**：由于插件是实验性的，依赖项可能不完整。实际使用时需要参考具体版本的 Build.cs 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-17 | `5aabf92f` | Allowing conversation task nodes to choose branches in a specific order when advancing the conversat | 允许对话任务节点在推进对话时按特定顺序选择分支 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF（格式化日志） |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃了使用 bool bIncludeNestedObjects 的 GetObjects* 和 ForEachObjectWithOuter 函数，引入新替代方案 |
| 2026-03-24 | `d413371b` | [AI][Conversation] Add ConversationToolset plugin | 【AI】【对话】添加 ConversationToolset 插件（新工具插件） |
| 2026-03-12 | `b7b7adad` | Add an option to stop and manually build the conversation registry dependencies graph when needed, i | 添加选项以在需要时停止并手动构建对话注册表依赖关系图 |

### 维护评价

**维护状态**：**活跃维护中**

**分析**：
1. **创建时间**：2021 年创建，已有约 5 年历史，但仍在持续更新。
2. **更新频率**：2026 年 3-4 月有密集的功能更新和重构（5 次提交），表明插件仍在积极开发中。
3. **实验性状态**：插件明确标记为实验性 (`IsExperimentalVersion: true`)，且默认未启用 (`EnabledByDefault: false`)，这表明 Epic 可能仍在测试和迭代该系统。
4. **功能发展**：最近的提交显示正在添加新功能（如分支顺序控制）、工具支持（ConversationToolset 插件）和底层优化（依赖图管理），说明插件正在走向成熟。
5. **代码健康**：有日志系统迁移、API 弃用和替换等维护工作，表明代码库正在规范化。

**建议**：
- 该插件适合在实验性项目中使用，但不建议在需要稳定性的商业项目中直接采用。
- 由于仍在积极开发，API 可能会有较大变化，需密切关注更新。
- 对于复杂对话系统需求，该插件提供了一个有前途的官方解决方案，但需要自行承担实验性 API 变化的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation)
- [官方文档]()（暂无）
- [测试用例]()（未在提供的信息中发现独立测试文件）