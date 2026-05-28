# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | 实验性元音效 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

此插件是 MetaSound 音频系统的**功能试验场**。它用于开发和集成新的、尚未准备好用于正式发布版本的 MetaSound 节点和功能。具体来说，它提供了：
1.  **实验性运行时节点**：在 `MetasoundExperimentalRuntime` 模块中包含新的音频处理节点（如滤波器、乘法器）。
2.  **引擎集成功能**：`MetasoundExperimentalEngineRuntime` 模块提供了将实验性功能与 UE 引擎核心（如音频波形数据）集成的代码。
3.  **编辑器工具**：`MetasoundExperimentalEditor` 模块为这些实验性功能提供编辑器支持（如专门的节点类别）。
4.  **基础音频扩展**：`AudioExperimentalRuntime` 模块可能包含更底层的实验性音频处理原语。

开发者可以通过启用此插件，提前体验、测试并反馈尚未在标准 MetaSound 插件中提供的新功能。

## 使用场景

-   你是 MetaSound 的高级用户或开发者，希望**提前使用**新的音频处理节点（如通道无关类型 CAT 系列节点）。
-   你正在为项目开发定制的音频效果或合成器，并希望**利用最新的、未经验证的 MetaSound 底层功能**。
-   你参与 MetaSound 插件的开发或反馈，需要**测试正在开发中的新特性**。
-   你正在研究 UE 音频管线的内部实现，需要查看**实验性的引擎集成代码**。

## 模块用法

本插件包含四个模块，其用途概述如下，详细 API 请参考各子模块文档。

### 核心模块概述

| 模块 | 类型 | 主要用途 |
|---|---|---|
| `AudioExperimentalRuntime` | Runtime | 提供底层的、实验性的音频运行时工具和类型。 |
| `MetasoundExperimentalRuntime` | Runtime | **核心模块**，包含所有实验性 MetaSound 节点（如 CAT 类型的节点）的实现。 |
| `MetasoundExperimentalEngineRuntime` | Runtime | 处理实验性 MetaSound 功能与引擎其他系统（如波形数据）的集成。 |
| `MetasoundExperimentalEditor` | Editor | 为实验性节点和功能提供编辑器支持，如节点注册、外观和行为。 |

## Demo 示例

作为实验性插件，其功能通常作为现有 MetaSound 节点图的补充。一个典型的“使用示例”是**在 MetaSound 编辑器中，从“实验性”类别中拖出新节点**（例如 CAT Multiply, CAT Ladder Filter）并连接它们，以构建新的音频处理链路。

**在蓝图中使用（概念描述）**：
1.  确保 `MetasoundExperimental` 插件已在项目中启用。
2.  打开或创建一个 MetaSound 资产。
3.  在节点图编辑器中，搜索你感兴趣的实验性节点（如“Multiply (CAT)”）。
4.  将该节点添加到图表中，并将其输入/输出与其他 MetaSound 节点连接。

*注意：由于这是实验性 API，具体的节点名称和功能可能会随着开发快速变化。*

## 模块依赖

插件本身的 `.uplugin` 文件声明了对 `Metasound` 插件的依赖。

从各模块的 `Build.cs` 文件看，它们主要依赖 `CoreUObject`。

| 模块 | 用途 |
|---|---|
| `Metasound` | **核心依赖**。本插件是 MetaSound 的扩展，必须先启用 MetaSound 插件。 |

*注意：使用者无需在自己的 `Build.cs` 中直接依赖本插件的模块，只需启用插件即可在 MetaSound 资产中使用其提供的节点。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 新增实验性 CAT（通道无关类型）波形节点 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 `FSoundWaveData` API 废弃修复相关的合并冲突 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | 新增 CAT 乘法节点 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | 新增 CAT 梯形滤波器节点 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261': | 从待处理变更列表中取消搁置（合并代码） |

### 维护评价

-   **状态**：**活跃开发中**。
-   **分析**：该插件创建于 2025 年 4 月，非常年轻。从 git 历史看，在 **2026 年 5 月** 仍有密集的功能性提交，专注于 **CAT (Channel Agnostic Types)** 相关的新节点开发，表明它正在被积极用于原型新特性。
-   **建议**：由于 `IsExperimentalVersion: true` 且默认不启用，此插件 **不适合用于生产环境**。其 API 和功能不稳定，可能随时发生破坏性更改。它非常适合希望参与 MetaSound 未来功能探索、测试和反馈的开发者或技术艺术家。对于生产项目，应等待功能合并至主 `Metasound` 插件后再使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
-   [官方文档]( ) *(无)*
-   [测试用例]( ) *(无特定测试目录)*