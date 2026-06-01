# WaveTable

> Default implementation of WaveTable support within the Unreal Audio Engine.

| 属性 | 值 |
|---|---|
| 中文名 | 波表 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `WaveTable` (Runtime), `WaveTableEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-15 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WaveTable) | |

## 用途

WaveTable 插件提供了 UE5 音频引擎中波表 (WaveTable) 的核心数据结构和运行时支持。波表是一种用于音频合成和调制的技术，它将波形存储在表格中，通过查表方式高效地生成或调制声音信号。此插件为音频设计师提供了基础的波表数据结构和相关工具，旨在被 MetaSound、音频调制等系统复用，以实现更灵活、高效的音频处理。

## 使用场景

- 你需要在 MetaSound 节点中使用自定义波形进行音频合成或调制。
- 你需要一个编辑器工具来直观地创建和编辑音频波表曲线。
- 你正在开发需要复杂音频调制效果（如 LFO、包络）的游戏或应用。

## 蓝图用法

由于插件处于 Beta 状态，其公开的蓝图 API 可能主要集中在编辑器和内部使用。具体的蓝图可调用函数和属性请参阅各子模块文档。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| *（待从具体模块文档补充）* | *（待从具体模块文档补充）* | *（待从具体模块文档补充）* |

### 使用示例（蓝图描述）

*（具体的蓝图节点使用示例需要参考各子模块文档，例如 `WaveTable` 和 `WaveTableEditor`。）*

## C++ 用法

此插件主要为其他音频系统提供底层支持，其 C++ API 的使用通常涉及与 MetaSound 或音频调制系统的集成。

### 头文件引入

```cpp
#include "WaveTable.h"
```

### 基本用法

*（基础的波表数据结构创建和使用示例需要参考 `WaveTable` 模块文档及源码。）*

### 进阶用法

*（进阶用法通常涉及与 MetaSound 节点或音频调制系统的结合，具体实现需查阅相关模块代码。）*

## Demo 示例

*（一个完整的最小可编译示例需要结合具体的使用场景，例如创建一个使用波表数据的简单 MetaSound。由于插件功能的集成性质，纯波表的独立运行示例较少，其核心价值在于被其他系统调用。）*

## 模块依赖

要使用此插件的功能，你的模块需要依赖以下独特的模块（除标准依赖外）：

| 模块 | 用途 |
|---|---|
| `WaveTable` | 提供波表数据结构、导入和采样等核心运行时功能。 |
| `WaveTableEditor` | 提供波表资产的编辑器 UI 和操作工具（仅编辑器环境需要）。 |

*注意：实际依赖关系请以模块 `Build.cs` 文件为准。此插件很可能还依赖 `AudioMixer`、`SignalProcessing` 等音频相关模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 为内容浏览器添加了新的音频资产添加菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件日志从 UE_LOG 迁移至 UE_LOGF 宏。 |
| 2026-02-02 | `9dc10c15` | Unclamp Modulation Patches | 解除了调制补丁的钳制限制，允许更大幅度的调制。 |
| 2025-07-12 | `b8bdcd83` | Run UnrealCodeFixup to fix dll storage | 运行代码修复工具，修正了 DLL 存储相关问题。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie... | 为包含对应 .gen.cpp 文件的源码添加了内联生成宏，优化了编译过程。 |

### 维护评价

- **活跃维护**：最近一次功能性更新（Unclamp Modulation Patches）发生在约 2 个月前，且近期仍有编译和工具链的维护性提交，表明该插件仍在积极维护中。
- **状态**：插件创建近 4 年，且被标记为 **Beta（实验性）** 并 **默认未启用**。这表明它可能尚未达到稳定生产的状态，API 和功能未来可能发生变化。
- **推荐**：适合在开发或原型阶段，尤其是与 MetaSound 音频系统深度集成时使用。用于生产环境需谨慎评估其 Beta 状态带来的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WaveTable)
- [官方文档]() (暂无)
- [测试用例]() (暂未明确，可尝试在 `Engine/Tests/` 目录下搜索相关测试)