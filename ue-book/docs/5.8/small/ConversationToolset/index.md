# Conversation Toolset

> Toolset for Conversation Systems

| 属性 | 值 |
|---|---|
| 中文名 | 对话工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具） |
| 模块 | `ConversationToolset` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-04-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ConversationToolset) | |

## 用途

这是一个为对话系统（`CommonConversation`）服务的编辑器扩展工具集。它的核心作用是为开发者（主要是设计师）提供在 Unreal Editor 内创建、编辑和预览对话资产的图形化界面和工具，从而简化复杂对话树的构建流程。它作为 `ToolsetRegistry` 插件的一部分被注册和管理。

## 使用场景

- 你正在开发一个包含复杂对话系统的 RPG 或叙事驱动型游戏，需要一个可视化的工具来设计对话分支和逻辑。
- 你的项目依赖 `CommonConversation` 插件来处理对话逻辑，并希望在编辑器中获得更好的内容创作支持。
- 你需要一个集中的地方来管理所有与对话相关的编辑器工具和资产创建向导。

## 蓝图用法

该插件主要提供编辑器工具（如资产创建、编辑器面板），而非运行时蓝图节点。其提供的工具通常通过编辑器菜单或资产右键菜单访问。

### 核心节点

*该插件未暴露任何 `BlueprintCallable` 函数。*

## C++ 用法

该插件是一个纯编辑器模块，其主要功能通过注册编辑器扩展（菜单、工具栏、资产编辑器）实现，不直接提供可供游戏代码调用的 C++ API。以下仅展示其模块加载代码。

### 头文件引入

```cpp
// 仅当开发编辑器扩展或工具集时才需要
#include "ConversationToolset.h"
```

### 基本用法

该模块的 `StartupModule` 和 `ShutdownModule` 通常负责注册和注销其提供的编辑器扩展。使用者通常不需要直接调用它。

```cpp
// 文件: Engine/Plugins/Experimental/Toolsets/ConversationToolset/Source/ConversationToolset/Private/ConversationToolset.cpp
// 这是模块的标准实现，用户插件无需直接交互
#include "ConversationToolset.h"
#include "Modules/ModuleManager.h"

DEFINE_LOG_CATEGORY(LogConversationToolset);

void FConversationToolsetModule::StartupModule()
{
    // 此处会注册编辑器工具、资产工厂、自定义资产编辑器等
    UE_LOG(LogConversationToolset, Log, TEXT("ConversationToolset Module Started"));
}

void FConversationToolsetModule::ShutdownModule()
{
    // 此处会注销在 StartupModule 中注册的所有内容
    UE_LOG(LogConversationToolset, Log, TEXT("ConversationToolset Module Shut Down"));
}

IMPLEMENT_MODULE(FConversationToolsetModule, ConversationToolset)
```

### 进阶用法

作为依赖 `CommonConversation` 的工具集，其进阶用法体现在如何利用它提供的工具来管理对话资产，并通过 `CommonConversation` 的运行时 API 驱动这些资产。具体取决于该工具集最终提供的功能（当前源码信息有限）。

## Demo 示例

由于该插件未提供独立的公共 API，其使用主要体现在编辑器内操作。一个最小的模块加载示例如下，它本身不实现功能，但展示了如何依赖和加载此模块。

```cpp
// MyEditorModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "ConversationToolset.h" // 包含工具集模块头文件

void FMyEditorModule::StartupModule()
{
    // ConversationToolset 模块在此处已被引擎加载，可以依赖其提供的服务
    // 但通常不会直接调用其内部函数，而是使用它创建的编辑器工具。
    UE_LOG(LogTemp, Log, TEXT("MyEditorModule started, ConversationToolset is available."));
}

void FMyEditorModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CommonConversation` | 核心对话运行时系统，此工具集为其提供编辑器支持。 |
| `ToolsetRegistry` | 工具集注册中心，用于发现和管理此工具集。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-03 | `7f02bd73` | [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r | 将所有工具集的加载阶段调整为引擎初始化后，以简化注册流程。 |
| 2026-04-01 | `4210d4c3` | [AI Toolsets]: Move ConversationToolset under the Toolsets directory | 将对话工具集移动至统一的工具集目录下。 |

### 维护评价

- **状态**：初始阶段 / 实验性
- **分析**：插件创建于 2026-04-01，最新提交在 2026-04-03，时间间隔极短，表明它正处于**早期开发或整合阶段**。目前只有两次提交，均为目录结构和加载配置的调整，**尚未包含实质性的功能代码**。作为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false` 的插件，它显然还不稳定。
- **建议**：可以关注其后续开发。由于是实验性插件且功能尚未完善，**不建议在生产项目中依赖它**。它是为未来 `CommonConversation` 生态工具链做准备的一部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ConversationToolset)
- [官方文档]() (无)
- [测试用例]() (当前源码中未发现)