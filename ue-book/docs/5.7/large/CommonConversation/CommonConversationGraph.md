# Common Conversation

> An *experimental* plugin for authoring graph-based conversation trees

| 属性 | 值 |
|---|---|
| 中文名 | 通用对话系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资源、图节点类） |
| 模块 | `CommonConversationRuntime` (Runtime), `CommonConversationGraph` (UncookedOnly), `CommonConversationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CommonConversation) | |

## 用途

**Common Conversation** 是一个实验性的插件，用于在 UE5 中创建基于节点图的对话树系统。它提供了一个可视化的编辑器，让设计师可以像编排行为树一样构建对话逻辑，包括：

- 使用 **任务（Task）**、**需求（Requirement）**、**效果（Side Effect）** 和 **分支（Choice）** 节点来定义对话流程。
- 通过 **编译器（FConversationCompiler）** 将图数据编译为运行时可使用的 `UConversationDatabase` 资产。
- 支持 **断点调试** 和 **运行时高亮**，便于测试对话内容。

该插件解决了传统对话系统难以维护、缺乏可视化编辑的问题，特别适合需要复杂分支、条件判断和事件触发的叙事游戏。

## 使用场景

- 开发一款 **角色扮演游戏（RPG）**，需要大量 NPC 对话，且对话分支依赖于玩家属性、任务进度或玩家选择。
- 制作 **视觉小说 / 冒险游戏**，需要精细控制对话流程，包括条件分支、随机选项和对话后触发事件。
- 在 **多人游戏** 中为客户端的对话实例提供网络同步支持（通过 `UConversationDatabase` 资产作为数据源）。

## 蓝图用法

> **注意**：`CommonConversationGraph` 模块主要提供编辑器和编译器功能，**不包含运行时蓝图可调用节点**（运行时蓝图 API 位于 `CommonConversationRuntime` 模块中，需参考其单独文档）。  
> 本模块的核心作用是在编辑器中创建和编译对话资产，以下为与蓝图交互的主要入口：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Rebuild Bank` | 强制重新编译指定的 `UConversationDatabase` 资产（从图节点更新运行时数据） | `FConversationCompiler`（静态方法，通过蓝图函数库调用） |
| `Get Graph from Bank` | 根据索引从 `UConversationDatabase` 获取对应的编辑器图 | `FConversationCompiler`（静态方法） |
| `Get Num Graphs` | 获取对话资产中的图数量 | `FConversationCompiler`（静态方法） |

### 使用示例（蓝图描述）

1. **创建对话资产**：在内容浏览器中右键 → 杂项 → 对话数据库（UConversationDatabase）。
2. **打开资产**：双击资产进入对话图编辑器，自动生成一个入口节点（Entry Point）。
3. **添加节点**：右键图面板，选择“添加任务”（Task）、“需求”（Requirement）、“效果”（Side Effect）或“分支”（Choice）。
4. **连接节点**：拖拽引脚连接节点，构成对话流程。
5. **编译**：在编辑器中点击“编译”按钮（或调用 **Rebuild Bank** 蓝图节点），将图数据写入资产。
6. **在运行时使用**：通过 `CommonConversationRuntime` 提供的节点启动对话（如 `Start Conversation`）。

## C++ 用法

### 头文件引入

```cpp
#include "ConversationCompiler.h"      // 编译器
#include "ConversationGraph.h"         // 图类型
#include "ConversationGraphNode.h"     // 图节点基类
#include "ConversationGraphSchema.h"   // 图形学
```

### 基本用法

以下示例展示了如何通过 C++ 代码创建 `UConversationDatabase` 资产并编译对话图：

```cpp
// 来源：CommonConversationGraph 模块的测试用例或内部代码（路径：Engine/Plugins/Experimental/CommonConversation/Source/CommonConversationGraph/...）

// 1. 创建一个对话数据库资产（通常在编辑器工具中创建）
UConversationDatabase* ConversationAsset = NewObject<UConversationDatabase>(GetTransientPackage(), NAME_None, RF_Transient);
// 注意：实际使用时应通过资产工厂或编辑器工具创建持久资产

// 2. 使用编译器添加新图
UConversationGraph* NewGraph = FConversationCompiler::AddNewGraph(ConversationAsset, TEXT("MainConversation"));

// 3. 在图中添加默认入口节点（由 Schema 自动创建）
NewGraph->GetSchema()->CreateDefaultNodesForGraph(*NewGraph);

// 4. 手动添加一个任务节点（示例：创建 UConversationGraphNode_Task）
UConversationGraphNode_Task* TaskNode = NewObject<UConversationGraphNode_Task>();
TaskNode->NodePosX = 200;
TaskNode->NodePosY = 100;
NewGraph->AddNode(TaskNode, true, true);

// 5. 编译资产（将图数据转换为运行时格式）
FConversationCompiler::RebuildBank(ConversationAsset);
```

### 进阶用法

**获取编译后的图并遍历节点**：

```cpp
// 从已存在的对话资产中获取图
int32 NumGraphs = FConversationCompiler::GetNumGraphs(ConversationAsset);
for (int32 i = 0; i < NumGraphs; ++i)
{
    UConversationGraph* Graph = FConversationCompiler::GetGraphFromBank(ConversationAsset, i);
    // 遍历图的所有节点
    for (UEdGraphNode* Node : Graph->Nodes)
    {
        if (UConversationGraphNode* ConvNode = Cast<UConversationGraphNode>(Node))
        {
            // 获取运行时节点实例
            UConversationNode* RuntimeNode = ConvNode->GetRuntimeNode<UConversationNode>();
            // 进一步处理...
        }
    }
}
```

**自定义连接规则**：继承 `UConversationGraphSchema` 并重写 `CanCreateConnection` 可以限制节点间的连接类型。

## Demo 示例

> 由于 `CommonConversationGraph` 主要作为编辑器模块，运行时代码在 `CommonConversationRuntime` 中，这里提供一个最小化的编辑器工具示例：编译已有的对话资产。

### ConversationCompileTool.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "ConversationCompiler.h"
#include "ConversationDatabase.h"

/**
 * 工具函数：强制编译所有加载的对话资产
 */
class FConversationCompileTool
{
public:
    static void CompileAllLoadedConversations()
    {
        // 获取所有加载的 UConversationDatabase 对象
        TArray<UObject*> ConversationAssets;
        GetObjectsOfClass(UConversationDatabase::StaticClass(), ConversationAssets, true, RF_NoFlags);
        
        for (UObject* Obj : ConversationAssets)
        {
            UConversationDatabase* Database = Cast<UConversationDatabase>(Obj);
            if (Database)
            {
                FConversationCompiler::RebuildBank(Database);
                UE_LOG(LogTemp, Log, TEXT("Compiled conversation: %s"), *Database->GetName());
            }
        }
    }
};
```

### ConversationCompileTool.cpp

```cpp
#include "ConversationCompileTool.h"

// 使用方式：在控制台命令或编辑器按钮中调用
// FConversationCompileTool::CompileAllLoadedConversations();
```

## 模块依赖

从 `CommonConversationGraph.Build.cs` 中提取的独特依赖（省略常见模块）：

| 模块 | 用途 |
|---|---|
| `AIGraph` | 对话图编辑器基类（`UAIGraph`, `UAIGraphNode`） |
| `CommonConversationRuntime` | 运行时节点类型（`UConversationNode`） |
| `GameFeatures` | 游戏特性系统集成（可选，.uplugin 中指定） |
| `GraphEditor` | 图编辑器基础 UI 和布局 |

## 维护状态

### 近期更新

- 2025-08-19 `589248b5` Extending Conversation system with QOL functions（扩展对话系统的生活质量函数）
- 2025-08-13 `53785040` Add option for GameFeatureSubsystem observers to not be updated for current state when added（游戏特性系统优化）
- 2025-07-11 `1bb7cec8` Remove null initializers when creating TSubclassOf<T>（代码清理）
- 2025-06-10 `1be7adc4` Replace FORCEINLINE with inline in GameplayFramework modules（编译优化）
- 2025-05-31 `52e3dac1` Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars（API 导出修复）

### 维护评价

- **创建时间**：2025年5月，非常年轻的插件（约 0.3 年）。
- **近期更新**：最近 3 个月内有功能性更新（QOL functions）和多项优化，表明仍在活跃开发。
- **实验性**：`.uplugin` 标记为 `IsExperimentalVersion=true`，且默认不启用，API 和功能可能随时变化，不建议用于正式项目。
- **已知问题**：作为实验性插件，部分功能（如断点调试、网络同步）可能不完善，依赖语法（AIGraph）也可能有隐含限制。
- **推荐度**：适合原型开发和内部工具使用，若投入生产需评估风险。建议关注未来官方更新或社区反馈。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CommonConversation)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（未提供专用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/CommonConversation/Tests/)（暂无单独测试目录）