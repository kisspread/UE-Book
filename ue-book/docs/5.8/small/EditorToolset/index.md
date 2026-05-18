# EditorToolset

> Toolsets for interacting with the Unreal Editor and core types (Blueprints, Actors, Properties, etc.) via the AI Toolset Registry.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `EditorToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/EditorToolset) | |

## 用途

EditorToolset 是一个专门为 **AI 代理 (AI Agent)** 设计的编辑器插件。它的核心目的是为 AI 提供一套标准化的、可编程的接口（Toolset），使其能够自动化地操控虚幻编辑器，而不仅仅是游戏运行时。

具体来说，它解决了以下问题：
1.  **AI 驱动的编辑器操作**：允许 AI 代理执行如“启动/停止 PIE 会话”、“查询和设置日志级别”、“获取编辑器视口截图并标注”等复杂操作。
2.  **标准化工具注册**：它依赖 `ToolsetRegistry` 插件，将自己的功能（如 `UEditorAppToolset`、`ULogsToolset`）注册到一个中央注册表中。这使得其他插件（尤其是 AI 框架）可以动态发现并调用这些工具。
3.  **环境状态捕获**：提供了生成带标注的编辑器视口图像的能力，帮助 AI 理解当前场景中的 Actor 位置和身份，这对于视觉反馈和调试至关重要。

简而言之，这个插件是构建能够理解并操控虚幻编辑器环境的智能 AI 代理的基础工具链的一部分。

## 使用场景

- **你正在开发一个 AI 代理**，该代理需要能够自动运行游戏场景测试 (`StartPIE`)，在测试失败时检查引擎日志 (`GetLogEntries`)，并理解错误发生时的场景状态（通过标注的视口截图）。
- **你需要一个 AI 能够调试或测试你的项目**，例如让 AI 自动化地在不同场景中运行，并收集性能数据或验证游戏逻辑。
- **你正在扩展 AI 的“技能”库**，希望为你的 AI 系统添加对虚幻编辑器的控制能力，EditorToolset 提供了实现这些技能所需的核心基础操作。

## 蓝图用法

**重要说明**：此插件的主要设计是为 **AI 工具集 (AI Toolset)** 服务，其核心函数使用 `UFUNCTION(meta=(AICallable))` 而非 `BlueprintCallable` 进行标记。这意味着这些函数主要意图是被注册的 AI 工具调用，而不是直接暴露在蓝图编辑器中。蓝图直接使用的场景较少。

### 核心节点

虽然主要面向 AI，但其定义的结构体（如 `FPIESessionOptions`）可能在蓝图中可见。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLogEntries` | 从当前会话日志文件中返回匹配条件的日志条目。 | `ULogsToolset` |
| `GetLogCategories` | 返回一个已注册的日志类别列表。 | `ULogsToolset` |
| `GetVerbosity` | 获取指定日志类别的当前冗余度级别。 | `ULogsToolset` |
| `SetVerbosity` | 设置指定日志类别的冗余度级别。 | `ULogsToolset` |

### 使用示例（蓝图描述）

由于主要面向 AI，蓝图中的典型使用可能是通过其他 AI 框架插件间接调用。一个概念性的蓝图使用流程可能是：
1.  获取 `ULogsToolset` 的类默认对象。
2.  调用 `GetLogEntries` 节点，传入类别 `"LogBlueprint"` 和模式 `""` (获取所有)，最多 100 条。
3.  将返回的字符串数组输出到屏幕或写入文件。

## C++ 用法

在 C++ 中，你通常不会直接实例化这些工具集，而是通过继承 `UToolsetDefinition` 来创建自己的自定义工具集，或者使用已有的工具集类。

### 头文件引入

```cpp
// 引入日志工具集
#include "LogsToolset.h"
// 如果需要操作编辑器会话
#include "EditorAppToolset.h"
// 如果需要创建位图注释
#include "BitmapAnnotation.h"
```

### 基本用法

以下示例展示如何创建一个继承自 `UToolsetDefinition` 的自定义工具集，并在其中添加一个 AI 可调用的函数。

```cpp
// MyCustomToolset.h
#pragma once

#include "CoreMinimal.h"
#include "ToolsetRegistry/ToolsetDefinition.h"
#include "MyCustomToolset.generated.h"

UCLASS()
class UMyCustomToolset : public UToolsetDefinition
{
    GENERATED_BODY()

public:
    // 声明一个 AI 可调用的函数
    UFUNCTION(meta=(AICallable), Category = "MyTools")
    static FString GetProjectName();
};

// MyCustomToolset.cpp
#include "MyCustomToolset.h"

FString UMyCustomToolset::GetProjectName()
{
    return FApp::GetProjectName();
}
```
*(概念性示例，展示了插件的扩展模式)*

### 进阶用法

结合 `EditorAppToolset` 和 `LogsToolset`，可以实现复杂的自动化测试流程。例如，在 C++ 中编写一个测试，使用工具集函数来启动 PIE、验证结果并清理环境。

## Demo 示例

下面是一个最小化的自定义工具集示例，它注册了两个简单的函数。

```cpp
// SimpleMathToolset.h
#pragma once

#include "CoreMinimal.h"
#include "ToolsetRegistry/ToolsetDefinition.h"
#include "SimpleMathToolset.generated.h"

UCLASS()
class USimpleMathToolset : public UToolsetDefinition
{
	GENERATED_BODY()

public:
	/** 将两个整数相加并返回结果。 */
	UFUNCTION(meta=(AICallable), Category = "SimpleMath")
	static int32 Add(int32 A, int32 B);

	/** 计算一个浮点数的平方。 */
	UFUNCTION(meta=(AICallable), Category = "SimpleMath")
	static float Square(float Value);
};
```

```cpp
// SimpleMathToolset.cpp
#include "SimpleMathToolset.h"

int32 USimpleMathToolset::Add(int32 A, int32 B)
{
	return A + B;
}

float USimpleMathToolset::Square(float Value)
{
	return Value * Value;
}
```

## 模块依赖

从 `Build.cs` 文件推断，使用此插件或构建类似功能的模块，需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供 AI 工具集注册和发现的核心框架。这是 EditorToolset 插件的基础，任何创建自定义 AI 工具集的模块都需要依赖它。 |

## 维护状态

### 近期更新

- 2026-05-14 `69dab60d` Move core toolsets, tests, and skills from ToolsetRegistry into EditorToolset. Also remove a few unn (核心功能迁移和重构)
- 2026-05-13 `c7baaf9c` Migrated EditorApp and Logs toolsets from ToolsetRegistry to new EditorToolset plugin. (插件创建及初始迁移)

### 维护评价

- **创建时间**：非常新（2026年5月）。
- **近期活动**：在创建后一天内就有一次重要的代码迁移提交，表明该项目正在积极初始化和整合中。
- **状态**：**活跃开发中**，但仍处于实验阶段 (`IsExperimentalVersion=true`)。其 API 和结构可能在未来发生较大变化。
- **建议**：此插件专为前沿的 AI 集成场景设计，适合早期采用者和希望探索 AI 驱动编辑器自动化的开发者。对于生产环境项目，需谨慎评估其稳定性，并准备应对其 API 可能的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/EditorToolset)
- [父级插件参考 - ToolsetRegistry](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ToolsetRegistry)