# Remote Control Components

> 

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制组件 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlComponents` (Runtime), `RemoteControlComponentsEditor` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2024-01-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteControlComponents) | |

## 用途

基于源码分析，`RemoteControlComponents` 并非一个独立的通用远程控制插件，而是 **Motion Design（运动设计）系统** 的一个核心子模块。它的主要功能是为 Motion Design 的 Remote Control (RC) 面板和后端引擎提供核心组件和逻辑，使得 RC 系统能够发现、连接并远程控制 Motion Design 图形（Motif）中的各种属性和材质实例。

该插件解决了在 Motion Design 的实时图形制作和控制工作流中，需要通过一个集中的面板（RC Panel）来远程编辑和预览图形元素（如材质参数、位置、缩放等）的需求。它填补了 Motion Design 核心功能与远程控制面板之间的连接逻辑。

## 使用场景

- 你正在使用 **Motion Design（运动设计）** 模块制作实时图形、运动控制图形或广播图形。
- 你需要通过 **Remote Control (RC) 面板** 来集中、直观地编辑和控制 Motion Design 图形中的各个元素（Motif）。
- 你开发了一个自定义的 Motion Design 组件，并希望将其属性暴露给 RC 面板进行远程控制。

## 蓝图用法

**重要提示**：根据提供的代码分析，此插件**没有暴露公开的蓝图API**。它主要作为内部实现，供 Motion Design 和 Remote Control 系统在 C++ 层面调用。其所有类和函数都基于 C++ 架构。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 该插件未提供公开的蓝图节点。 | N/A |

### 使用示例（蓝图描述）

不适用。该插件的功能通过 Motion Design 和 Remote Control 的现有蓝图界面集成，用户无需直接操作本插件的蓝图节点。

## C++ 用法

此插件为 C++ 模块，主要作为其他模块（如 MotionDesignComponents）的依赖项。

### 头文件引入

```cpp
// 通常不需要直接包含，因为其功能通过更高层级的模块暴露。
// 若需直接访问其内部类型（如样式），可以包含：
#include "Styles/RemoteControlComponentsEditorStyle.h"
```

### 基本用法

该插件的主要价值在于其构建的类层次结构和模块依赖关系，而非独立的API调用。一个典型的使用场景是，当你构建一个需要集成到 Motion Design RC 系统的自定义组件时，你可能会间接受益于或需要链接此模块。

```cpp
// 示例：在你的自定义 Motion Design 组件中，你可能需要链接 RemoteControlComponents 模块。
// 位于 MyCustomMotif.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    // ... 其他依赖 ...
    "RemoteControlComponents", // 如果你需要使用其提供的核心基类或接口
    "MotionDesignComponents"
});
```

（来源：推断自 `RemoteControlComponents` 模块的构建依赖关系）

### 进阶用法

更常见的用法是作为 `MotionDesignComponents` 模块的依赖而被间接使用。开发者更可能直接与 `MotionDesignComponents` 或 `RemoteControl` API 交互。

## Demo 示例

由于该插件是一个底层运行时组件，没有独立的可运行示例。其功能通过 Motion Design 模块的 Demo 项目（如官方示例）进行展示。

## 模块依赖

从 `Build.cs` 文件分析，此插件具有高度的内部依赖性，指向 Motion Design 生态系统。

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 核心远程控制逻辑和协议。 |
| `RemoteControlAPI` | 远程控制 API 层。 |
| `MotionDesignComponents` | **关键依赖**，Motion Design 的核心组件模块，本插件为其提供扩展功能。 |
| `MotionDesignCommon` | Motion Design 的通用类型和工具。 |
| `PropertyAccess` | 用于安全、动态地访问对象属性。 |
| `MaterialEditor` | 用于与材质编辑器交互（如预览材质）。 |
| `Engine` | Unreal 引擎核心（已省略）。 |
| `Slate`, `SlateCore` | UI 框架（已省略）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-02-14 | `c579ba10` | Motion Design: | 与 Motion Design 系统集成相关的提交。 |
| 2024-02-13 | `723c2005` | [Remote Control Components] Remove “invalid” tracked properties from Tracker | 移除跟踪器中的“无效”跟踪属性，优化属性追踪。 |
| 2024-02-12 | `10de4dbc` | Remote Control: | 远程控制相关改动。 |
| 2024-02-09 | `236f2d2f` | Remote Control Components: | 组件层面的修复或改进。 |
| 2024-02-07 | `1f30386d` | Motion Design RC: | Motion Design 与远程控制集成相关提交。 |

### 维护评价

- **创建时间**：2024年1月，是一个非常新的实验性插件。
- **活跃度**：在创建后的约2个月内（2024年2月）有密集的提交，主要用于功能开发和Bug修复。
- **当前状态**：自2024年2月14日后，在当前提供的git历史中没有新的更新记录，表明该插件可能进入了功能稳定期或等待上游依赖（如Motion Design）的更新。
- **风险提示**：作为实验性插件，其API和功能在未来版本中可能发生重大变化。最后更新距今已超过一年。
- **推荐使用**：仅推荐给正在使用或开发 **Motion Design** 相关功能的开发者。普通用户不应启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteControlComponents)
- [官方文档]：无（`.uplugin` 中 `DocsURL` 为空）
- [测试用例]：根据提供的文件列表，未发现独立的测试文件。其测试可能集成在 `MotionDesignComponents` 或 `RemoteControl` 的测试中。