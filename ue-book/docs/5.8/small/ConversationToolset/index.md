# ConversationToolset

> Toolset for Conversation Systems

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具） |
| 模块 | `ConversationToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ConversationToolset) | |

## 用途

该插件是 **CommonConversation** 对话系统在编辑器中的配套工具集。它本身不包含运行时对话逻辑，而是为对话内容的创建和编辑提供编辑器扩展和工具。其核心作用是作为 `CommonConversation` 插件的编辑器端补充，通过 `ToolsetRegistry` 插件进行注册，为设计师和开发者提供可视化的对话流程编辑能力。

## 使用场景

- 你正在使用 `CommonConversation` 插件构建游戏中的对话系统（如 RPG、冒险游戏），需要一个可视化的编辑器来创建和管理复杂的对话树、对话节点和对话选项。
- 你的项目需要一个统一的工具集注册机制（`ToolsetRegistry`）来管理各种编辑器工具，`ConversationToolset` 便是其中一个专注于对话系统的工具。

## 蓝图用法

该插件主要提供编辑器工具和扩展，而非运行时蓝图节点。其功能通过编辑器菜单、自定义资产编辑器或工具面板呈现。在蓝图中，你主要与 `CommonConversation` 插件提供的运行时对话组件和函数交互，而 `ConversationToolset` 提供的工具用于创建这些对话资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 该插件不暴露 `BlueprintCallable` 函数，其功能通过编辑器界面访问。 | - |

### 使用示例（蓝图描述）

1.  在编辑器中，通过 `ToolsetRegistry` 或特定的菜单路径（如“窗口” -> “对话工具”）打开 `ConversationToolset` 提供的对话编辑器。
2.  在对话编辑器中，创建新的对话资产（例如 `UConversationAsset`）。
3.  使用可视化节点编辑器设计对话流程，添加对话节点、分支选项和条件。
4.  保存对话资产后，在蓝图中，使用 `CommonConversation` 插件提供的组件（如 `UConversationComponent`）加载并运行该对话资产。

## C++ 用法

该插件的 C++ 代码主要负责模块的初始化和与 `ToolsetRegistry` 的注册，不提供面向游戏逻辑的公开 API。开发者通常通过编辑器扩展点来使用其功能。

### 头文件引入

```cpp
// 通常不需要直接引入此插件的头文件。
// 如果需要检查模块是否加载，可以包含：
#include "ConversationToolset.h"
```

### 基本用法

该插件的模块在 `StartupModule` 中向 `ToolsetRegistry` 注册其提供的工具集。使用者无需直接调用其 API，只需确保插件被启用，其工具便会自动集成到编辑器中。

```cpp
// 检查插件模块是否已加载（例如，在某个编辑器工具的初始化中）
if (FModuleManager::Get().IsModuleLoaded(TEXT("ConversationToolset")))
{
    UE_LOG(LogTemp, Log, TEXT("ConversationToolset module is loaded and available."));
}
```
*来源：基于 `ConversationToolset.h` 中的模块接口推断的典型用法。*

### 进阶用法

作为 `ToolsetRegistry` 的一部分，`ConversationToolset` 可能会注册自定义的资产编辑器、菜单扩展或工具面板。开发者如果想扩展或定制对话编辑器，需要研究 `ToolsetRegistry` 的注册机制和 `ConversationToolset` 的具体实现。

## Demo 示例

由于该插件是编辑器工具，没有独立的运行时示例。一个最小的“使用”示例是确保插件被正确启用和加载。

```cpp
// MyEditorUtility.h
#pragma once

#include "CoreMinimal.h"

class FMyEditorUtility
{
public:
    static void CheckConversationToolset()
    {
        // 检查依赖插件是否加载
        bool bCommonConversationLoaded = FModuleManager::Get().IsModuleLoaded(TEXT("CommonConversation"));
        bool bToolsetRegistryLoaded = FModuleManager::Get().IsModuleLoaded(TEXT("ToolsetRegistry"));
        bool bConversationToolsetLoaded = FModuleManager::Get().IsModuleLoaded(TEXT("ConversationToolset"));

        UE_LOG(LogTemp, Warning, TEXT("CommonConversation: %s, ToolsetRegistry: %s, ConversationToolset: %s"),
            bCommonConversationLoaded ? TEXT("Loaded") : TEXT("Not Loaded"),
            bToolsetRegistryLoaded ? TEXT("Loaded") : TEXT("Not Loaded"),
            bConversationToolsetLoaded ? TEXT("Loaded") : TEXT("Not Loaded"));
    }
};
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 字段可知，使用此插件前必须启用以下插件：

| 模块 | 用途 |
|---|---|
| `CommonConversation` | 提供核心的对话系统运行时框架和资产类型。 |
| `ToolsetRegistry` | 提供工具集注册和管理框架，`ConversationToolset` 通过它注册自身。 |

*注意：其自身的 `Build.cs` 仅依赖 `Core`，但其功能强依赖于上述两个插件。*

## 维护状态

### 近期更新

- `7f02bd73` 2026-04-03 — [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r
- `4210d4c3` 2026-04-01 — [AI Toolsets]: Move ConversationToolset under the Toolsets directory

### 维护评价

- **创建时间**：2026-04-01（基于提供的信息）。
- **最近更新**：最近两次提交均在 2026 年 4 月，内容涉及插件目录结构和加载阶段的优化，表明该插件正在被积极整合到“AI Toolsets”框架中。
- **活跃状态**：**活跃维护中**。作为实验性插件，它正处于开发和完善阶段。
- **已知限制**：作为实验性插件（`IsExperimentalVersion=true`），其 API 和功能可能在未来版本中发生变化。默认未启用（`EnabledByDefault=false`），需要用户手动在插件管理器中启用。
- **推荐使用**：如果你正在使用或计划使用 `CommonConversation` 插件来构建对话系统，并且需要一个编辑器工具来辅助内容创作，那么可以启用此插件。但需注意其“实验性”状态，不建议在追求稳定性的正式项目中作为核心依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ConversationToolset)
- 官方文档：无
- 测试用例：未在提供的路径中发现测试文件。