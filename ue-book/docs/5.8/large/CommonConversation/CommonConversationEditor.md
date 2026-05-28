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
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation) | |

## 用途

CommonConversation 是一个基于图（Graph）的对话树编辑和运行时系统，用于在 UE5 中构建可执行的 NPC 对话流程。与 BehaviorTree 类似，它提供了一套完整的：

1. **运行时（Runtime）**：负责在游戏运行时执行对话逻辑，管理对话状态流转、黑板数据交互、对话参与者（Participant）通信等
2. **图定义（Graph）**：定义对话图的节点类型、连接方式和编辑器图结构（UncookedOnly 意味着仅在编辑器和未打包构建中可用）
3. **编辑器（Editor）**：提供可视化的对话树编辑器，支持图形化编辑、搜索、调试、差异对比（Diff）等功能

该插件解决的核心问题是：在 RPG、开放世界等需要大量对话内容的游戏中，提供一个**标准化、可扩展**的对话系统框架，让设计师可以像使用行为树一样，用可视化节点图来编排复杂的对话分支逻辑。它与 GameFeatures 插件集成，支持模块化扩展。

## 使用场景

- 你在做 RPG 游戏，需要大量分支对话 → 用 CommonConversation 的图编辑器编排对话树
- 你需要 NPC 对话系统支持条件判断、黑板数据查询 → 对话节点可访问 Blackboard
- 你需要多人共享和调试对话逻辑 → 编辑器内置调试器，支持断点、单步执行
- 你需要对不同版本的对话资产进行差异对比 → 编辑器内置 Diff 功能
- 你想通过 GameFeatures 插件模块化地扩展对话内容 → 插件原生支持 GameFeatures 集成

## 子模块概览

本插件包含 3 个模块（92 个源文件），属于 **large** 规模插件：

| 模块 | 类型 | 用途 |
|---|---|---|
| [CommonConversationRuntime](CommonConversationRuntime.md) | Runtime | 对话执行引擎、参与者管理、对话状态流转 |
| [CommonConversationGraph](CommonConversationGraph.md) | UncookedOnly | 对话图的节点定义、图结构、Schema |
| [CommonConversationEditor](CommonConversationEditor.md) | Editor | 可视化编辑器、调试器、搜索、Diff |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-17 | `5aabf92f` | Allowing conversation task nodes to choose branches in a specific order when advancing the conversat | 对话任务节点支持按指定顺序选择分支推进对话 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 宏到 UE_LOGF 格式 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. | 废弃旧版对象遍历 API，迁移新版接口 |
| 2026-03-24 | `d413371b` | [AI][Conversation] Add ConversationToolset plugin | 新增 ConversationToolset 辅助插件 |
| 2026-03-12 | `b7b7adad` | Add an option to stop and manually build the conversation registry dependencies graph when needed | 新增手动构建对话注册表依赖图的选项 |

### 维护评价

- **活跃维护中**：2026 年 3-4 月有多次功能性更新（分支选择顺序、新工具集插件、注册表依赖图构建）
- 虽然标注为实验性（`IsExperimentalVersion=true`），但从近期提交来看仍在持续开发和改进
- 需要注意：`EnabledByDefault=false`，需要手动在插件设置中启用
- 依赖 GameFeatures 插件，使用前需确保该插件已启用
- **推荐用于**：原型开发和实验性项目。生产环境使用需谨慎，因为 API 可能随版本变动

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation)
- 官方文档：无

---

# Common Conversation Editor

> 对话树编辑器模块——提供可视化对话图编辑、调试、搜索和差异对比功能

## 模块信息

| 属性 | 值 |
|---|---|
| 模块名 | CommonConversationEditor |
| 类型 | Editor |
| 加载阶段 | Default |
| 源文件数 | ~13 头文件 + 对应 cpp |

## 用途

该模块是 CommonConversation 插件的编辑器部分，为对话数据库（`UConversationDatabase`）资产提供完整的编辑体验，类似 BehaviorTreeEditor 之于 BehaviorTree。

## 核心类结构

```
FConversationEditor                    ← 主编辑器应用（WorkflowCentricApplication）
├── FConversationDebugger              ← 调试器（TickableGameObject）
├── FConversationEditorToolbar         ← 工具栏构建
├── SFindInConversation               ← 搜索面板
├── SConversationTreeEditor           ← 树形结构视图
├── SConversationDiff                 ← 差异对比视图
└── FAssetTypeActions_ConversationDatabase ← 资产类型注册
```

## 编辑器模式

编辑器支持两种视图模式（来自 `FConversationEditor`）：

| 模式 | 说明 |
|---|---|
| `GraphViewMode` | 图形化节点编辑视图（类似蓝图） |
| `TreeViewMode` | 树形结构浏览视图 |

## 资产类型

编辑器注册了 `ConversationDatabase` 资产类型（`FAssetTypeActions_ConversationDatabase`）：

- **资产名称**: Conversation Bank
- **类型颜色**: 紫色 (`FColor(149, 70, 255)`)
- **支持操作**: 打开编辑器、资产 Diff 对比

## 调试器功能（FConversationDebugger）

调试器提供完整的对话执行调试能力：

| 功能 | 说明 |
|---|---|
| 断点 | 支持在对话节点上添加/删除/启用/禁用断点 |
| 单步执行 | Step Forward Into/Over, Step Back Into/Over, Step Out |
| 状态查看 | 查看当前/保存的黑板值（`FindValueForKey`） |
| 时间戳 | 获取当前/保存的执行时间戳（`GetTimeStamp`） |
| PIE 集成 | 自动关联 PIE 会话中的对话实例 |
| AI 调试 | 支持从 AI 调试工具选择 Pawn 进行调试 |

## 搜索功能（SFindInConversation）

- 支持按关键字搜索对话图中的节点
- 结果以树形结构展示，支持父子层级
- 点击搜索结果自动跳转到对应节点
- 支持多 Token 匹配

## 差异对比（SConversationDiff）

- 双面板对比两个版本的 `UConversationDatabase` 资产
- 差异列表以列表视图展示
- 支持在默认 Diff 工具中查看
- 节点级别差异对比

## Tab 结构

编辑器由以下标签页组成：

| Tab ID | 说明 |
|---|---|
| `GraphDetailsID` | 属性/细节面板 |
| `SearchID` | 搜索面板 |
| `GraphEditorID` | 图编辑器（文档类型 Tab） |
| `TreeEditorID` | 树形结构编辑器 |

## 编辑器命令

### 通用命令（FConversationEditorCommonCommands）

| 命令 | 说明 |
|---|---|
| `SearchConversation` | 打开对话搜索 |

### 调试器命令（FConversationDebuggerCommands）

| 命令 | 说明 |
|---|---|
| `BackInto` / `BackOver` | 单步后退（进入/跳过） |
| `ForwardInto` / `ForwardOver` | 单步前进（进入/跳过） |
| `StepOut` | 步出 |
| `PausePlaySession` | 暂停运行 |
| `ResumePlaySession` | 恢复运行 |
| `StopPlaySession` | 停止运行 |
| `CurrentValues` / `SavedValues` | 切换当前/保存值视图 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation/Source/CommonConversationEditor)

---

# Common Conversation Runtime

> 对话执行引擎模块——管理对话的状态流转、参与者通信和运行时逻辑

## 模块信息

| 属性 | 值 |
|---|---|
| 模块名 | CommonConversationRuntime |
| 类型 | Runtime |
| 加载阶段 | PreDefault |

## 用途

该模块是 CommonConversation 插件的核心运行时，负责：

1. **对话实例管理**：创建、推进和终止对话实例
2. **参与者（Participant）系统**：管理对话中的多个参与者（如玩家、NPC），处理参与者之间的通信
3. **对话节点执行**：执行对话树中的各类节点（任务节点、选择节点等）
4. **黑板集成**：与 UE5 Blackboard 系统集成，支持条件判断和数据共享
5. **对话注册表**：维护对话资产的注册和依赖关系图

从近期提交可推断的关键功能：

- 对话任务节点支持按指定顺序选择分支推进（`5aabf92f`）
- 对话注册表依赖图的构建与管理（`b7b7adad`）
- 与 ConversationToolset 工具集插件协作（`d413371b`）

## C++ 用法

### 头文件引入

```cpp
#include "CommonConversationRuntimeModule.h"
```

### 基本用法

该模块作为 Runtime 模块，主要被对话图编辑器和游戏逻辑引用。典型的使用方式是通过 `UConversationDatabase` 资产驱动对话执行。

### 模块依赖

使用 CommonConversationRuntime 时，你的 Build.cs 需要添加依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "CommonConversationRuntime"
});
```

> 注意：该模块依赖 GameFeatures 插件（`.uplugin` 中声明），请确保项目中 GameFeatures 插件已启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation/Source/CommonConversationRuntime)

---

# Common Conversation Graph

> 对话图定义模块——定义对话树的节点类型、图结构和编辑器图 Schema

## 模块信息

| 属性 | 值 |
|---|---|
| 模块名 | CommonConversationGraph |
| 类型 | UncookedOnly |
| 加载阶段 | PreDefault |

## 用途

该模块是 CommonConversation 插件的图结构定义层，仅在编辑器和未打包构建中加载（`UncookedOnly`）。它负责：

1. **对话图节点定义**：定义对话树中所有可用的节点类型（如 `UConversationGraphNode`、`UConversationGraphNode_Root`、`UConversationGraphNode_CompositeDecorator` 等）
2. **图 Schema 定义**：定义节点之间的合法连接关系
3. **图资产编辑数据**：管理对话图在编辑器中的表示形式（`UEdGraph`）

从编辑器模块的代码可推断出的关键图节点类型：

| 节点类 | 说明 |
|---|---|
| `UConversationGraphNode` | 基础对话图节点 |
| `UConversationGraphNode_Root` | 对话树根节点 |
| `UConversationGraphNode_CompositeDecorator` | 复合装饰器节点（用于条件组合） |

## 为什么是 UncookedOnly？

`UncookedOnly` 意味着该模块：
- ✅ 在编辑器中可用
- ✅ 在未打包（Development/Debug）构建中可用
- ❌ 在打包（Shipping）构建中不可用

这是合理的，因为图结构定义（节点布局、连接方式等）仅在编辑时需要，运行时只需要序列化后的对话数据库资产。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CommonConversation/Source/CommonConversationGraph)